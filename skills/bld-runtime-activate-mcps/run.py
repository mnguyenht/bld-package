#!/usr/bin/env python3
"""Spawn an MCP server over stdio, run a batch of tool calls, print compact
results, then kill it. Nothing persists — the server lives only for these calls.

Usage:
    echo '[{"name":"search_text","arguments":{"repo":"<repo>","query":"var("}}]' \
        | python run.py jcodemunch

argv[1] = server key: "jcodemunch" | "context-mode"
stdin   = JSON array of tool calls: [{"name":..., "arguments":{...}}, ...]
"""
import atexit, json, os, signal, subprocess, sys, threading, time, queue, shutil

_NPX = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
SERVERS = {
    "jcodemunch": ["jcodemunch-mcp", "serve"],
    # npx on Windows is npx.cmd; resolve at runtime
    "context-mode": [_NPX, "-y", "context-mode"],
    "shadcn": [_NPX, "-y", "shadcn@latest", "mcp"],
}


def _popen_kwargs():
    """Extra Popen options that make the server killable as a whole tree.

    npx is a wrapper: it starts, then starts node, and node is the real server.
    Signalling only the wrapper leaves node running. On POSIX the fix is to give
    the child its own process group so one signal reaches the whole family; on
    Windows there is no equivalent flag, so shutdown() uses taskkill /T instead.
    """
    return {} if sys.platform == "win32" else {"start_new_session": True}


def shutdown(proc):
    """Kill the server AND anything it spawned. Safe to call more than once.

    Order matters, and getting it wrong is why this leaked for months. The old
    version called terminate() first and only reached the tree kill if the
    following wait TIMED OUT. But terminating the npx wrapper works fine, so the
    wait almost always succeeded, the tree kill never ran, and node survived
    every single clean shutdown. The tree has to be killed while the parent is
    still alive to anchor it.

    Nothing here needs a graceful stop. jcodemunch is the only server with an
    on-disk cache and it runs directly, with no wrapper and no child; the two
    that do have a child (context-mode, shadcn) are read-only query servers, and
    by shutdown time we already have every answer we asked for.
    """
    if proc.poll() is not None:
        return
    if sys.platform == "win32":
        # /T takes the children too, /F because a console server has no window
        # to close politely.
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            proc.terminate()
    try:
        proc.wait(timeout=5)
        return
    except Exception:
        pass
    try:                                    # still there: stop asking nicely
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (OSError, AttributeError):
        proc.kill()
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def _pid_alive(pid):
    if sys.platform == "win32":
        out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid],
                             capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def selftest():
    """Prove the CHILD dies too, not just the process we launched.

    Stands in for npx without needing npx: a parent that spawns a child, prints
    the child's PID, and then sleeps. Under the old shutdown order the parent
    died and the child was still running a second later, which is exactly what
    node did behind npx on every clean exit. Exits non-zero if that comes back.
    """
    parent_src = ("import subprocess, sys, time;"
                  "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']);"
                  "print(p.pid, flush=True);"
                  "time.sleep(120)")
    proc = subprocess.Popen([sys.executable, "-c", parent_src],
                            stdout=subprocess.PIPE, text=True, **_popen_kwargs())
    kid = int(proc.stdout.readline().strip())
    shutdown(proc)
    time.sleep(1.0)
    leaked = _pid_alive(kid)
    print("selftest: parent %s, child %s"
          % ("dead" if proc.poll() is not None else "ALIVE",
             "LEAKED" if leaked else "dead"))
    if leaked:
        subprocess.run(["taskkill", "/F", "/PID", str(kid)], capture_output=True) \
            if sys.platform == "win32" else os.kill(kid, signal.SIGKILL)
        sys.exit("FAIL: the child outlived the batch. That is the whole bug.")
    print("selftest ok: nothing outlived the batch")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) < 2 or sys.argv[1] not in SERVERS:
        sys.exit(f"usage: python run.py <{'|'.join(SERVERS)}>  (calls JSON on stdin)\n"
                 f"       python run.py --selftest   (proves the tree kill works)")
    cmd = SERVERS[sys.argv[1]]
    calls = json.load(sys.stdin)
    if not isinstance(calls, list):
        sys.exit("stdin must be a JSON array of {name, arguments}")

    try:
        # errors="replace" is not optional on Windows. These servers log through
        # a console that is cp1252 by default, so a single byte like 0xb7 (a
        # middot in a progress line) is invalid UTF-8 and raises inside the
        # reader thread. Observed for real: it killed the stderr reader outright.
        # On stdout the same byte would kill the only thread reading replies and
        # turn a working server into a 120-second timeout with no explanation.
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True,
                                encoding="utf-8", errors="replace", bufsize=1,
                                **_popen_kwargs())
    except FileNotFoundError:
        sys.exit("cannot start %s: %r is not installed or not on PATH.\n"
                 "jcodemunch installs with pip; the others run through npx."
                 % (sys.argv[1], cmd[0]))

    # The whole promise of this skill is that nothing outlives the batch, and a
    # bare kill at the end of main() only holds when main() reaches the end. Any
    # error path left the server running. atexit covers all of them: normal
    # return, sys.exit from die(), and an unhandled exception.
    atexit.register(lambda: shutdown(proc))

    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in proc.stdout], daemon=True).start()

    # Keep stderr instead of discarding it. A server that starts and then dies
    # (missing dependency, bad version, no index yet) says why on stderr and
    # nothing on stdout, so throwing it away turned every startup failure into
    # an unexplained 120-second timeout.
    errs = []
    threading.Thread(target=lambda: [errs.append(l) for l in proc.stderr],
                     daemon=True).start()

    def die(why):
        # Give the reader thread a moment to drain. Without this, the common
        # case (server dies, we notice instantly on a broken pipe) reports
        # "nothing on stderr" while the explanation is still in flight, which
        # is the exact failure this function exists to prevent.
        proc.poll()
        for _ in range(20):
            if errs:
                break
            time.sleep(0.05)
        tail = "".join(errs[-15:]).strip()
        sys.exit("%s\nserver stderr:\n%s" % (why, tail or "(nothing on stderr)"))

    _id = 0
    def rpc(method, params=None, notify=False, timeout=120):
        nonlocal _id
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            _id += 1
            msg["id"] = _id
        try:
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            # The server exited. Without this the user gets a BrokenPipeError
            # traceback instead of the reason, which is sitting in stderr.
            die("%s died before answering %r." % (sys.argv[1], method))
        if notify:
            return None
        want = _id
        while True:
            try:
                line = q.get(timeout=timeout)
            except queue.Empty:
                return {"error": "timeout"}
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("id") == want:
                return obj

    init = rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                              "clientInfo": {"name": "bld-runtime-activate-mcps", "version": "0"}})
    if not init or init.get("error"):
        die("%s never completed the MCP handshake." % sys.argv[1])
    rpc("notifications/initialized", {}, notify=True)

    total = 0
    for c in calls:
        r = rpc("tools/call", {"name": c["name"], "arguments": c.get("arguments", {})})
        if not r or "result" not in r:
            print(f"=== {c['name']} === ERROR: {json.dumps(r)[:300]}\n")
            continue
        text = "".join(x.get("text", "") for x in r["result"].get("content", [])
                        if x.get("type") == "text")
        total += len(text)
        print(f"=== {c['name']} ({len(text)} chars, ~{len(text)//4} tok) ===")
        print(text or "(empty)")
        print()
    print(f"--- TOTAL: {total} chars  ~{total//4} tokens ---")

if __name__ == "__main__":
    main()
