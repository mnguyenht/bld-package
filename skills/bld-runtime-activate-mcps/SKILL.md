---
name: bld-runtime-activate-mcps
description: Run the third-party code-optimizer MCP servers (jcodemunch, context-mode) on-demand for a single burst of code search, then shut them down — no persistent connection. Use when the user says /bld-runtime-activate-mcps, "hard optimize", "token-optimize this search", or is about to do a big code sprint across many files and wants compact, cheap code exploration.
---

# bld-runtime-activate-mcps — burst-use the optimizer MCPs, then dip

These are **unofficial third-party MCP servers** installed from GitHub
(`jcodemunch-mcp` via pip, `context-mode` via npx). By default they stay **out of
`.mcp.json`**, so they never auto-load and never ambiently route the codebase. This skill spins one up over stdio, fires the exact queries needed,
prints compact results, and kills the process — seconds, not a session.

Use it for a **big sprint** where you'd otherwise read many large files: pull the
compact search results once, then work from them.

## Ground rules

- **Do not hand-edit `.mcp.json` to make these permanent.** Always-on is a real
  option, but it belongs to `/bld-mcp-settings`, which refuses to delete entries
  it did not write. Editing the file directly loses that protection, and this
  skill keeps working either way.
- Prefer **jcodemunch** — it's read-only code search. Reach for **context-mode**
  only if the task genuinely needs its shell/cross-tool features (its `ctx_execute`
  runs real commands with your logged-in `gh`/`aws`/`kubectl` — heavier trust).
- **jcodemunch is blind to CSS** (`missing_extractors: css`) — its symbol/semantic
  tools return nothing for stylesheets. For CSS use `search_text`, or just read the
  file. Its strength is JS/TS/Python symbols.

## How to run it

> **`python` is the Windows spelling.** macOS and most Linux distros ship the
> interpreter as `python3` and have no bare `python` at all, so every command
> below fails with `command not found` until you swap the name. Check once with
> `python3 --version || python --version || py --version` and use whichever
> answered.


> **`<BLD>` is wherever BLD is installed.** `/bld-setup` recommends global, which
> is `~/.claude/skills/`; a project-scoped install is `<project>/.claude/skills/`.
> Resolve it once before running anything below. A hardcoded `.claude/skills/...`
> is the project-scoped path, and it does not exist on a default install.

The runner spawns the server, runs a batch of tool calls, prints results with
token counts, then terminates. Feed it a JSON array of calls on stdin:

```bash
cd <project-root>
python <BLD>/bld-runtime-activate-mcps/run.py jcodemunch <<'EOF'
[
  {"name": "list_repos", "arguments": {}},
  {"name": "search_text", "arguments": {"repo": "REPO", "query": "var("}}
]
EOF
```

Replace `REPO` with the repo name from `list_repos` (for this workspace it is
the git-root folder name).

### Typical sprint flow

1. **First time / stale code** — index, then get the repo name:
   ```
   [{"name":"index_folder","arguments":{"path":"<ABSOLUTE PROJECT PATH>"}},
    {"name":"list_repos","arguments":{}}]
   ```
2. **Explore** — one batch of the searches you need (each returns trimmed
   matching lines, not whole files):
   ```
   [{"name":"search_symbols","arguments":{"repo":"REPO","query":"handleSubmit"}},
    {"name":"find_references","arguments":{"repo":"REPO","symbol":"handleSubmit"}},
    {"name":"get_file_outline","arguments":{"repo":"REPO","path":"src/App.tsx"}}]
   ```
3. Work from the printed results. The server is already dead — nothing lingers.

Useful jcodemunch tools: `search_text`, `search_symbols`, `get_file_outline`,
`get_repo_outline`, `find_references`, `find_importers`, `get_symbol_source`,
`get_context_bundle`. (Run `list_repos` / `get_file_tree` to orient.)

For context-mode, pass `context-mode` as the server arg; its tools are
`ctx_search`, `ctx_index`, `ctx_execute`, etc. — check `tools/list` output if unsure.

### shadcn/ui component lookup (on-demand)

The shadcn MCP server is also wired in on-demand. Use it
when building/adding shadcn components so you pull real registry data instead of
guessing. Pass `shadcn` as the server arg:

```bash
python <BLD>/bld-runtime-activate-mcps/run.py shadcn <<'EOF'
[{"name":"search_items_in_registries","arguments":{"registries":["@shadcn"],"query":"dialog"}},
 {"name":"get_item_examples_from_registries","arguments":{"registries":["@shadcn"],"query":"dialog"}}]
EOF
```

Its tools: `search_items_in_registries`, `list_items_in_registries`,
`view_items_in_registries`, `get_item_examples_from_registries`,
`get_add_command_for_items`, `get_audit_checklist`, `get_project_registries`.
Pairs naturally with the `ui-styling` skill.

## Why this is safe-ish

Nothing is persistent: no live MCP connection, no background watcher, no auto-hook.
The server only ever sees the specific queries in the batch you hand it, and it's
gone the moment the batch finishes.
