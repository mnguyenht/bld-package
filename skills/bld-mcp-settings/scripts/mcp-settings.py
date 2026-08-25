#!/usr/bin/env python3
"""Toggle BLD's MCP servers between on-demand and always-on.

    python mcp-settings.py status
    python mcp-settings.py on  jcodemunch shadcn
    python mcp-settings.py off jcodemunch
    python mcp-settings.py off --all

ON  writes the named servers into .mcp.json, so Claude Code starts them at
    launch and keeps them running for the whole session.
OFF removes them again. The servers still work on demand through
    /bld-runtime-activate-mcps, which needs no .mcp.json at all.

It NEVER touches an entry it did not write. See `owned()` for how that is
decided, and why it matters.

ASCII output only: Windows consoles default to cp1252, and a stray symbol in
the one command that reports your config would crash it.
"""

import sys

if sys.version_info[:2] < (3, 7):
    sys.stderr.write(
        "BLD needs Python 3.7 or newer. This is %d.%d.\n"
        "On macOS and Linux try `python3` instead of `python`.\n"
        % (sys.version_info[0], sys.version_info[1])
    )
    sys.exit(1)

import io
import json
import os

# Exactly what BLD writes for each server. These mirror the SERVERS table in
# bld-runtime-activate-mcps/run.py; if that changes, change this too.
#
# `npx` is spelled plainly here, not npx.cmd. Claude Code resolves it itself,
# unlike Python's subprocess, which is why run.py has to be fussier.
SERVERS = {
    "jcodemunch":   {"command": "jcodemunch-mcp", "args": ["serve"]},
    "context-mode": {"command": "npx", "args": ["-y", "context-mode"]},
    "shadcn":       {"command": "npx", "args": ["-y", "shadcn@latest", "mcp"]},
}

# Trust notes printed before enabling. context-mode is not like the other two.
TRUST = {
    "jcodemunch":   "read-only code search. Lowest risk of the three.",
    "context-mode": "HIGH TRUST. Its ctx_execute runs real shell commands with "
                    "your logged-in gh / aws / vercel. Always-on means that is "
                    "available for the whole session, not just one batch.",
    "shadcn":       "official shadcn registry data. Read-only.",
}


def config_path(root):
    return os.path.join(root, ".mcp.json")


def load(path):
    """Return (data, existed). A broken file is never silently overwritten."""
    if os.path.isdir(path):
        sys.exit("%s is a directory, not a file. Nothing was changed." % path)
    if not os.path.isfile(path):
        return {"mcpServers": {}}, False
    try:
        raw = io.open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        sys.exit("cannot read %s (%s). Nothing was changed." % (path, e))
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError as e:
        sys.exit(
            ".mcp.json exists but is not valid JSON (%s).\n"
            "Refusing to touch it, because rewriting it would destroy whatever\n"
            "is in there. Fix the file by hand, then run this again." % e
        )
    # Valid JSON of the wrong shape is still someone's file. Refuse it for the
    # same reason as malformed JSON rather than "fixing" it into the expected
    # shape, which would silently discard whatever was actually in there.
    if not isinstance(data, dict):
        sys.exit(
            ".mcp.json contains valid JSON, but the top level is %s rather than\n"
            "an object. That is not a config this tool wrote or understands, so\n"
            "it has been left exactly as it is." % type(data).__name__
        )
    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        sys.exit(
            ".mcp.json has an \"mcpServers\" key that is %s rather than an object.\n"
            "Left untouched. Fix it by hand, then run this again."
            % type(servers).__name__
        )
    return data, True


def owned(name, entry):
    """True only if this entry is byte-for-byte what BLD would have written.

    A name match is NOT enough. Someone may run their own jcodemunch with
    different args, or have edited ours after we wrote it. Removing that on
    `off` would delete a config BLD never created and cannot restore, so a
    modified entry is left alone and reported instead.
    """
    return name in SERVERS and entry == SERVERS[name]


def show(path, data, existed):
    print("  file : %s%s" % (path, "" if existed else "  (does not exist yet)"))
    servers = data.get("mcpServers", {})
    if not servers:
        print("  state: OFF - no servers run automatically.")
        print("         BLD's servers still work on demand via")
        print("         /bld-runtime-activate-mcps (spawn, query, kill).")
        return
    print("  state: ON for %d server(s)" % len(servers))
    for name in sorted(servers):
        if owned(name, servers[name]):
            tag = "BLD"
        elif name in SERVERS:
            tag = "BLD name, EDITED - off will not remove it"
        else:
            tag = "yours, untouched"
        print("    - %-14s [%s]" % (name, tag))


def write(path, data):
    # Drop the key entirely when empty rather than leaving {"mcpServers": {}}.
    # An empty file is indistinguishable from "off" to Claude Code, but it is
    # confusing to a human reading their own repo.
    if not data.get("mcpServers"):
        data.pop("mcpServers", None)
    if not data:
        if os.path.isfile(path):
            os.remove(path)
            print("  removed %s (nothing left in it)" % path)
        return
    data.setdefault("mcpServers", {})
    # Write to a sibling temp file and rename over the original. Opening the
    # real path with "w" truncates it before a single byte is written, so a
    # failure mid-write (disk full, permissions, a killed process) leaves the
    # user with an empty or half-written .mcp.json. This tool's whole promise is
    # that it never damages your config, and that promise cannot survive a
    # truncating write. os.replace is atomic on both Windows and POSIX.
    tmp = path + ".bld-tmp"
    try:
        io.open(tmp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(data, indent=2) + "\n")
        os.replace(tmp, path)
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        sys.exit("could not write %s (%s).\nYour original file is untouched." % (path, e))
    print("  wrote %s" % path)


def main():
    args = [a for a in sys.argv[1:]]
    root = os.getcwd()
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            sys.exit("--root needs a directory after it.")
        root = args[i + 1]
        del args[i:i + 2]
        if not os.path.isdir(root):
            sys.exit("--root %r is not a directory. Nothing was changed." % root)

    action = args[0].lower() if args else "status"
    names = [a for a in args[1:] if not a.startswith("-")]
    every = "--all" in args

    if action not in ("status", "on", "off"):
        sys.exit("usage: mcp-settings.py status | on <server...> | off <server...|--all>\n"
                 "       servers: " + ", ".join(sorted(SERVERS)))

    path = config_path(root)
    data, existed = load(path)

    if action == "status":
        show(path, data, existed)
        return

    if every:
        names = sorted(SERVERS) if action == "on" else sorted(data["mcpServers"])
    if not names:
        sys.exit("name at least one server, or pass --all. Available: "
                 + ", ".join(sorted(SERVERS)))

    unknown = [n for n in names if n not in SERVERS]
    if unknown and action == "on":
        sys.exit("BLD does not ship these servers: %s\nAvailable: %s"
                 % (", ".join(unknown), ", ".join(sorted(SERVERS))))

    changed, skipped = [], []
    for name in names:
        if action == "on":
            if name in data["mcpServers"] and not owned(name, data["mcpServers"][name]):
                skipped.append("%s: you already have your own entry, left as is" % name)
                continue
            if owned(name, data["mcpServers"].get(name)):
                skipped.append("%s: already on" % name)
                continue
            data["mcpServers"][name] = dict(SERVERS[name])
            changed.append(name)
        else:
            entry = data["mcpServers"].get(name)
            if entry is None:
                skipped.append("%s: not in the file" % name)
            elif name not in SERVERS:
                skipped.append("%s: not a BLD server. Left alone." % name)
            elif not owned(name, entry):
                skipped.append("%s: present but edited, so this is not the entry "
                               "BLD wrote. Left alone; remove it by hand if you "
                               "meant to." % name)
            else:
                del data["mcpServers"][name]
                changed.append(name)

    if changed:
        write(path, data)
        print("  %s: %s" % ("enabled" if action == "on" else "disabled",
                            ", ".join(changed)))
    for s in skipped:
        print("  skipped %s" % s)

    if action == "on" and changed:
        print("")
        for name in changed:
            print("  %-14s %s" % (name, TRUST[name]))
        print("")
        print("  >> RESTART Claude Code. MCP servers connect at startup, so")
        print("     nothing enabled here is live until you do.")
    elif action == "off" and changed:
        print("")
        print("  >> RESTART Claude Code to actually stop them. They keep running")
        print("     in the current session until it ends.")


if __name__ == "__main__":
    main()
