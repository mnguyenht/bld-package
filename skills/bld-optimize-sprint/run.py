#!/usr/bin/env python3
"""Spawn an MCP server over stdio, run a batch of tool calls, print compact
results, then kill it. Nothing persists — the server lives only for these calls.

Usage:
    echo '[{"name":"search_text","arguments":{"repo":"<repo>","query":"var("}}]' \
        | python run.py jcodemunch

argv[1] = server key: "jcodemunch" | "context-mode"
stdin   = JSON array of tool calls: [{"name":..., "arguments":{...}}, ...]
"""
import json, subprocess, sys, threading, queue, shutil

_NPX = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
SERVERS = {
    "jcodemunch": ["jcodemunch-mcp", "serve"],
    # npx on Windows is npx.cmd; resolve at runtime
    "context-mode": [_NPX, "-y", "context-mode"],
    "shadcn": [_NPX, "-y", "shadcn@latest", "mcp"],
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SERVERS:
        sys.exit(f"usage: python run.py <{'|'.join(SERVERS)}>  (calls JSON on stdin)")
    cmd = SERVERS[sys.argv[1]]
    calls = json.load(sys.stdin)
    if not isinstance(calls, list):
        sys.exit("stdin must be a JSON array of {name, arguments}")

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True,
                            encoding="utf-8", bufsize=1)
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in proc.stdout], daemon=True).start()

    _id = 0
    def rpc(method, params=None, notify=False, timeout=120):
        nonlocal _id
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            _id += 1
            msg["id"] = _id
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
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

    rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "bld-optimize", "version": "0"}})
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
    proc.terminate()

if __name__ == "__main__":
    main()
