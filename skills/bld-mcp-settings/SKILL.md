---
name: bld-mcp-settings
description: Toggle BLD's MCP servers between on-demand and always-on. On writes them into .mcp.json so Claude Code starts them at launch; off removes them again and they stay available through /bld-runtime-activate-mcps. Use when the user says /bld-mcp-settings, "keep my MCPs running", "always-on MCP", "turn the MCP servers on", "stop spawning MCPs every time", or asks why an MCP server is not connected. Never removes an MCP entry BLD did not write.
---

# bld-mcp-settings — on-demand or always-on

BLD ships three MCP servers and runs them **on demand** by default: spawn, fire
one batch of queries, kill. This skill switches them to **always-on** instead, by
writing them into `.mcp.json` so Claude Code connects them at startup and keeps
them for the whole session.

Two settings, one file. Nothing else changes.

| Setting | What it means | How the servers run |
|---|---|---|
| **off** (default) | No `.mcp.json`, or none of BLD's servers in it | `/bld-runtime-activate-mcps` spawns one, queries it, kills it |
| **on** | Named servers written into `.mcp.json` | Claude Code starts them at launch and holds them open |

## Say this before turning anything on

The default is off **on purpose**, and the user should hear why once before
changing it. Not as discouragement, as information:

> **Always-on means the server sees your session, not just your query.** On
> demand, a server is alive for the few seconds of one batch and only ever
> receives the specific calls sent to it. Always-on, it is connected the whole
> time you work. That is genuinely more convenient, and it is a real change in
> what a third-party tool can observe.

Then let them decide. **Do not refuse, and do not repeat the warning.**

## The one that is not like the others

`jcodemunch` and `shadcn` are read-only lookups. **`context-mode` is not.** Its
`ctx_execute` runs real shell commands using whatever CLIs are already logged in
(`gh`, `aws`, `vercel`). On demand, that capability exists for one batch.
Always-on, it is available for the entire session.

**Never enable `context-mode` as part of a bundle.** If the user says "turn them
all on", enable the other two, name this one separately, and ask about it on its
own. `--all` exists for the user to type deliberately, not for you to reach for
because it is shorter.

## How to run it

> **`python` is the Windows spelling.** macOS and most Linux distros ship the
> interpreter as `python3` only. Check with
> `python3 --version || python --version || py --version` and use what answered.

**Two different directories are involved, and confusing them is the easy mistake
here.** The *script* lives wherever BLD is installed: `~/.claude/skills/` on a
default global install, `<project>/.claude/skills/` if it was scoped. The *file it
edits* is `.mcp.json` in the project being configured. Resolve the script to an
absolute path, and name the project with `--root`:

```bash
PY=~/.claude/skills/bld-mcp-settings/scripts/mcp-settings.py   # or the scoped path

python "$PY" status                          --root "<project>"
python "$PY" on  jcodemunch shadcn           --root "<project>"
python "$PY" off jcodemunch                  --root "<project>"
python "$PY" off --all                       --root "<project>"
```

`--root` defaults to the current directory, so it can be omitted when you are
already in the project. Omitting it while sitting somewhere else writes
`.mcp.json` into the wrong repo, which is why it is spelled out above.

`status` is read-only and changes nothing. **Run it first, every time**, and show
the user the output. It is the only way to know whether a `.mcp.json` already
exists and what is in it.

Servers: `jcodemunch`, `context-mode`, `shadcn`.

Add `--root "<path>"` to target a project other than the current directory.
`.mcp.json` is per-project, so the working directory decides which project you
are configuring. Getting that wrong writes config into the wrong repo.

## What it will not do

**It never removes an entry it did not write.** A name match is not enough: an
entry is only BLD's if it is byte-for-byte what BLD would have written. So

- a server the user added themselves is reported as `yours, untouched` and
  survives `off --all`,
- one of BLD's servers that the user has since edited is reported as `EDITED`
  and is also left alone, because the edit is theirs and cannot be restored once
  deleted.

If the user genuinely wants one of those gone, say that it needs removing by
hand and why. **Do not remove it for them by editing the JSON directly** — that
is the exact behaviour the guard exists to prevent.

**It refuses to touch a `.mcp.json` that is not valid JSON**, rather than
overwriting it. A malformed file usually means someone was editing it, and their
work is worth more than the convenience of this command succeeding.

## After either direction: restart

MCP servers connect **at startup**. Nothing turned on here is live, and nothing
turned off here has actually stopped, until Claude Code restarts. Say this
plainly. It is the first thing people get confused about.

## Committing `.mcp.json`

Ask before assuming. It is a project file, so committing it turns a personal
preference into a team default, and everyone who clones the repo starts those
servers. For a solo project that is usually fine. For anything shared, it is a
decision, and `context-mode` in a committed `.mcp.json` hands shell execution to
every future contributor's session.

## Notes

- Server definitions here mirror the `SERVERS` table in
  `skills/bld-runtime-activate-mcps/run.py`. **Change one, change both**, or `off` stops
  recognising entries `on` wrote and silently refuses to remove them.
- `npx` is spelled plainly in `.mcp.json`. Claude Code resolves it, unlike
  Python's `subprocess`, which is why `run.py` has to look for `npx.cmd`.
- Turning servers on does **not** replace `/bld-runtime-activate-mcps`. That skill
  still works, and is still the cheaper option for a single burst of queries.
