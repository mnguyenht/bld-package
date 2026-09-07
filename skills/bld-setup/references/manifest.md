# BLD install manifest

Everything `/bld-setup` can put on a machine. **Print this table verbatim before
installing anything.** Nothing here is installed silently.

Three different kinds of thing live in this table, and they get confused:

| Kind | What it is | Where |
|---|---|---|
| **Plugin** | A Claude Code extension, loaded at startup | S1 |
| **Skill** | Markdown instructions Claude reads | S2, S3, S6 |
| **CLI** | An ordinary command-line program | S4 |
| **MCP server** | A data source Claude queries | S5 |

**There is no GitHub plugin and no Vercel plugin.** `gh` and `vercel` are
plain CLIs in S4 that `/bld-util-deploy` shells out to.

**Runs code?** is the column that matters most for trust. `md` = pure markdown, it
can only ever suggest text. `code` = ships scripts or binaries that execute on your
machine. Read the source of anything marked `code` before you accept it.

---

## 1. Claude Code plugins

Installed by adding a marketplace + enabling the plugin. Registered at startup.

| Tool | What it does | Runs code? | Verify at |
|---|---|---|---|
| **ponytail** | Anti-over-engineering mode. Forces the laziest solution that works (YAGNI → stdlib → native → one line). Also `/ponytail-review`, `-audit`, `-debt`. | code (hooks + statusline) | https://github.com/DietrichGebert/ponytail |
| **ui-ux-pro-max** | The design engine. 50+ styles, 161 palettes, 57 font pairings, UX rules. `--design-system` generates the per-app design truth. | code (python scripts) | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| **claude-code-setup** | Anthropic's official setup advisor. Analyses a repo and recommends hooks/agents/skills. | md | https://github.com/anthropics/claude-plugins-official |

> ⚠️ **ui-ux-pro-max ships two image-generation sub-skills** (`design`,
> `banner-design`). BLD blocks both with a hook — see §6. The plugin is worth
> installing for everything else it does.

---

## 2. Global skills — `npx skills add`

Pure markdown unless noted. These are the cheapest, safest things on the list.

| Tool | What it does | Runs code? | Verify at |
|---|---|---|---|
| **emil-design-eng** | Emil Kowalski's philosophy on UI polish, component feel, animation. | md | https://github.com/emilkowalski/skills |
| **animation-vocabulary** | Reverse-lookup glossary: "the bouncy thing when a popover opens" → *Pop in*. Names an effect so you can prompt for it. | md | https://github.com/emilkowalski/skills |
| **review-animations** | Strict animation craft gate. Manual-only, run late and per-component. | md | https://github.com/emilkowalski/skills |
| **karpathy-guidelines** | Anti-LLM-slop rules: ask before coding, surgical changes, verifiable success criteria. | md | https://github.com/multica-ai/andrej-karpathy-skills |
| **find-skills** | Discovers skills on skills.sh. Use it to find, then vet before installing. | md | https://github.com/vercel-labs/skills |
| **copywriting** | Marketing copy: headlines, CTAs, value props, landing page text. | md | https://github.com/coreyhaines31/marketingskills |
| **a11y-audit** | WCAG 2.2 A/AA scan-fix-verify across React, Next, Vue, Svelte, plain HTML. | code (scripts) | https://github.com/alirezarezvani/claude-skills |
| **framer-motion** | Disney's 12 animation principles applied to Framer Motion in React. | md | https://github.com/dylantarre/animation-principles |
| **webapp-testing** | Drives a local web app with Playwright: click, type, screenshot, read console. | code (scripts) | https://github.com/anthropics/skills |
| **terms-of-service** | Drafts and reviews SaaS terms of service. | md | https://github.com/shawnpang/startup-founder-skills |
| **privacy-policy** | Drafts and reviews privacy policies across jurisdictions. | md | https://github.com/shawnpang/startup-founder-skills |

---

## 2b. Rule files (offered at the end, never automatic)

Two markdown files of opinionated defaults. **Phase 8 asks before installing
either, and "neither" is a supported answer** - every `/bld-*` command works
without them. An existing file at the same path is renamed to `CLAUDE.old.md`,
never overwritten or merged.

| File | What it holds | Runs code? | Installed to |
|---|---|---|---|
| `CLAUDE.global.md` | How you like to be worked with, security defaults, the dev loop | md | `~/.claude/CLAUDE.md` |
| `CLAUDE.workspace.md` | Workspace mission, routing table, guardrails, deploy conventions | md | `<workspace>/CLAUDE.md` |

Both carry `<FILL IN>` blanks you complete during setup, and both say in their own
text that they are living documents Claude should revise as it learns how you work.

## 3. Skills with their own installer

Both are large. Both want to wire hooks. BLD installs them **skill-only**.

| Tool | What it does | Runs code? | Verify at |
|---|---|---|---|
| **gstack** | Garry Tan's engineering framework. 54 skills upstream; BLD keeps **6** (`spec`, `investigate`, `cso`, `review`, `careful`, `upgrade`) and prunes the rest. **Needs `bun`** (`npm install -g bun`, official package) - its installer is a bun script, so without it the clone succeeds and `setup` then fails. | code (binaries, hooks, telemetry) | https://github.com/garrytan/gstack |
| **impeccable** | Design craft + audit, 23 sub-commands (`craft`, `audit`, `polish`, `harden`…). | code (node scripts) | https://github.com/pbakaus/impeccable |

> 🚩 **Never run `/impeccable live`.** It forwards `ANTHROPIC_API_KEY` /
> `CLAUDE_CODE_OAUTH_TOKEN` to a third-party backend. Every other impeccable
> command is fine. Never run `npx impeccable install` or `update` either, both
> wire hooks into your settings.
>
> 🚩 **gstack's `setup` regenerates all 54 skill wrappers.** Re-run the prune
> immediately after every `setup` or `/gstack-upgrade`, or the pruned 48 come
> back. gstack's own README asks you to ban Claude's built-in browser tools in
> favour of its browser skill. BLD does **not** do that. `setup` also downloads
> about **700 MB** of Playwright Chromium outside `~/.claude/` to
> `%LOCALAPPDATA%\ms-playwright` on Windows or `~/.cache/ms-playwright` on
> macOS/Linux. It registers a `Stop` hook named `gstack-timeline-stop` in
> `settings.json` and leaves `settings.json.bak.<timestamp>` beside it. Run
> `gstack-settings-hook remove-source --source gstack-timeline-stop` to remove
> that hook.

---

## 4. Command-line tools

| Tool | What it does | Install | Verify at |
|---|---|---|---|
| **react-doctor** | Static React/Next scanner: bugs, hooks rules, perf, a11y, security, dead code. The engine behind `/bld-optimize-react`. | `npm i -g react-doctor` | https://github.com/millionco/react-doctor |
| **react-scan** | Runtime re-render overlay. Shows what re-renders while you use the app. | `npm i -g react-scan` | https://github.com/aidenybai/react-scan |
| **lighthouse** | Google's page auditor: performance, a11y, best practices, SEO. The engine behind `/bld-optimize-app`. Run via `npx`, never installed. | `npx -y lighthouse@latest` | https://github.com/GoogleChrome/lighthouse |
| **claude-monitor** | Reads your local Claude Code usage and reports what's left in the window. Powers `/bld-runtime-tokens`. Privacy-first: local files only. | `uv tool install claude-monitor` | https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor |
| **vercel** | Deploy target for every BLD app. | `npm i -g vercel` | https://github.com/vercel/vercel |
| **gh** | GitHub CLI. Creates the private repo in `/bld-util-deploy`. | winget / installer | https://github.com/cli/cli |

> ⚠️ **`react-doctor` phones home by default.** It bundles `@sentry/node` and posts
> to a score API. BLD passes `--no-telemetry` on **every** run. If you use the tool
> outside BLD, pass it yourself.

---

## 5. MCP servers — on-demand by default

These are unofficial third-party servers. By default BLD spawns them over stdio,
fires one batch of queries, and kills the process, so **nothing is written to
`.mcp.json` and none of them ever ambiently sees your codebase**.

`/bld-mcp-settings on` switches any of them to always-on if you want that. It is
opt-in, per-server, and reversible. Read the trust column first: always-on means
the server is connected for your whole session rather than for one batch.

| Server | What it does | Trust weight | Install | Verify at |
|---|---|---|---|---|
| **jcodemunch** | Token-cheap code search via tree-sitter. Read-only. Blind to CSS. | low, read-only | `pip install jcodemunch-mcp`, or `pipx` / `uv tool` where pip is externally managed | https://github.com/jgravelle/jcodemunch-mcp |
| **context-mode** | Heavier code context server. Its `ctx_execute` **runs real shell commands** with your logged-in `gh` / `aws` / `vercel`. | **high** | `npx -y context-mode`, never installed | https://github.com/mksglu/context-mode |
| **shadcn** | Real shadcn/ui registry data so components aren't guessed from memory. Official. | low | `npx -y shadcn@latest mcp`, never installed | https://github.com/shadcn-ui/ui |

**Only jcodemunch puts anything on disk.** The other two are fetched by `npx` at
query time and leave nothing behind but an npm cache entry.

---

## 6. What BLD adds itself

| Piece | What it does | Runs code? |
|---|---|---|
| **23 `bld-*` skills** | The workflow set: init → refine → deploy, plus review, security, SEO, docs, planning, delegation. Free, with one exception: /bld-runtime-agents drives an external coding agent and needs either a paid ChatGPT subscription for Codex or Gemini's free tier. Every other command costs nothing beyond your own Claude usage. | md, except **five helper scripts**: `bld-setup/scripts/preflight.py` (reads your machine, installs nothing), `bld-professional-settings/scripts/switch-mode.py` (renames BLD's own files), `bld-mcp-settings/scripts/mcp-settings.py` (edits your `.mcp.json`, and refuses to remove entries it did not write), `skills/bld-runtime-activate-mcps/run.py` (spawns an MCP server, then kills it), and `skills/bld-optimize-app/scripts/lh-report.mjs` (node, reads a Lighthouse JSON report). All five are ours and short enough to read. A sixth file, `bld-setup/scripts/scenarios.py`, is copied with the rest but is the test harness for `preflight.py` and never runs during setup or during any command. |
| **`bld-executor` agent** | The worker the orchestrator skills fan out to. | md |
| **`block-image-skills.py` hook** | PreToolUse hook that **blocks** `ui-ux-pro-max:design` and `banner-design`. BLD never generates images with AI; it finds existing assets. Claude Code's own top-level `design` skill is not blocked: it lays out HTML artboards and generates nothing. It matches the `Skill` tool only, so it is a guardrail on skill invocation rather than a sandbox. | code (yours, under 80 lines, read it) |
| **`CLAUDE.md` templates** | The global + workspace rule layers. Sanitised, no personal data. | md |
| **6 vendored ECC checklists** | Security checklists inside `/bld-optimize-security`, copied from a third party rather than written here. Markdown only, they execute nothing. Source and full MIT license ship beside them in `references/ecc/`. | md, third-party ([affaan-m/ECC](https://github.com/affaan-m/ECC)) |

---

## 7. NOT installed — opt-in, and both are capped rather than paid

Listed so you know they exist and know BLD did not put them on your machine.
`/bld-setup` Phase 7 offers to walk you through Codex or Gemini if you want
`/bld-runtime-agents`. The user does every login themselves.

| Tool | Why it's separate | Verify at |
|---|---|---|
| **codex** (OpenAI CLI) | The delegation executor for `/bld-runtime-agents`. Runs on a ChatGPT account. The free tier works but is capped; a paid plan raises the ceiling rather than unlocking it. | https://github.com/openai/codex |
| **gemini-cli** | Delegation fallback. Free tier, small enough to exhaust in a single handoff. Check the current quota for your auth method rather than trusting a number here. | https://github.com/google-gemini/gemini-cli |

---

## Sources

Every row above was resolved from install metadata on a machine already running
BLD, not from memory:

- `~/.agents/.skill-lock.json` — §2 repos
- `~/.claude/plugins/known_marketplaces.json` — §1 repos
- `npm view <pkg> repository.url`, `pip show`, PyPI JSON API — §4, §5
- `git remote -v` in the installed skill folder — gstack
