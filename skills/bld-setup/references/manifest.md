# BLD install manifest

Everything `/bld-setup` can put on a machine. Nothing here is installed silently.

**Phase 3 prints the rows of "At a glance" that the chosen commands need**,
verbatim, before installing anything. It names every tool, what runs code, where
it comes from, and which BLD commands stop working without it. Phase 2 comes
first and picks the commands, from `skills.md`. Sections 1-7 below are the full
reference: install commands, every warning, every source. Print any of them when
the user asks.

## At a glance

| Group | What you get | Runs code? | Skip it and you lose | Source |
|---|---|---|---|---|
| **BLD** | The `/bld-*` commands chosen in Phase 2, and the `bld-executor` agent | 5 short helper scripts | every `/bld-*` command | this package |
| **Plugins** | ponytail, ui-ux-pro-max, claude-code-setup | 2 of 3 | the design step of `/bld-sprint-init`, and the first phase of `/bld-sprint-refine` | [ponytail](https://github.com/DietrichGebert/ponytail) · [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) · [claude-code-setup](https://github.com/anthropics/claude-plugins-official) |
| **Core skills** | 11 skills: design feel, animation, copywriting, accessibility audits, legal drafts | 2 of 11 | the copywriting skill `/bld-util-copywriting` builds on, and two phases of `/bld-sprint-refine` | [emilkowalski](https://github.com/emilkowalski/skills) · [karpathy](https://github.com/multica-ai/andrej-karpathy-skills) · [vercel-labs](https://github.com/vercel-labs/skills) · [marketingskills](https://github.com/coreyhaines31/marketingskills) · [claude-skills](https://github.com/alirezarezvani/claude-skills) · [animation-principles](https://github.com/dylantarre/animation-principles) · [anthropics](https://github.com/anthropics/skills) · [startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) |
| **React tools** | react-doctor, react-scan | yes | `/bld-optimize-react` | [react-doctor](https://github.com/millionco/react-doctor) · [react-scan](https://github.com/aidenybai/react-scan) |
| **Token monitor** | claude-monitor | yes | `/bld-runtime-tokens` | [claude-monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) |
| **Code search** | jcodemunch. context-mode and shadcn download themselves when used | yes | jcodemunch inside `/bld-runtime-activate-mcps` | [jcodemunch](https://github.com/jgravelle/jcodemunch-mcp) · [context-mode](https://github.com/mksglu/context-mode) · [shadcn](https://github.com/shadcn-ui/ui) |
| **gstack** | 5 of its skills: spec, investigate, cso, review, careful | yes | the gstack passes in `/bld-optimize-security`, and the spec option in `/bld-sprint-planning` | [gstack](https://github.com/garrytan/gstack) |
| **impeccable** | Design craft and audit | yes | the audit phase of `/bld-sprint-refine` | [impeccable](https://github.com/pbakaus/impeccable) |
| **Deploy** | gh and vercel, plus two logins you do yourself | yes | `/bld-util-deploy` | [gh](https://github.com/cli/cli) · [vercel](https://github.com/vercel/vercel) |
| *Not installed:* Codex or Gemini | Offered in Phase 7. You sign in yourself | not installed | `/bld-runtime-agents` | [codex](https://github.com/openai/codex) · [gemini-cli](https://github.com/google-gemini/gemini-cli) |

**Four warnings.** The full text is in the sections below.

- ui-ux-pro-max ships two image-generation skills. BLD blocks them by default with a hook; `/bld-settings-block-image-generation off` allows them.
- Never run `/impeccable live`. It sends your Claude credentials to a third-party server.
- react-doctor reports usage by default. BLD passes `--no-telemetry` on every run.
- context-mode runs shell commands with your logged-in CLIs, which makes it the
  highest-trust item on this list.

---

Four different kinds of thing live in this manifest, and they get confused:

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
> `banner-design`). **BLD blocks them by default**, with the hook installed
> alongside its own skills, and `/bld-settings-block-image-generation off` is the
> one switch that allows them again. BLD's own convention is to find existing assets
> rather than generate them, but that is a convention in the rule files, not
> something enforced here. The plugin is worth installing for everything else it
> does.

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

Both are large. Both have installers that wire hooks. BLD runs neither installer
and copies **only the skill files it uses**.

| Tool | What it does | Runs code? | Verify at |
|---|---|---|---|
| **gstack** | Garry Tan's engineering framework. BLD turns on **5** of its 54 skills (`spec`, `investigate`, `cso`, `review`, `careful`) by copying them out of the repo, and **never runs gstack's own `setup`**. The repo is still cloned, because those five call helper scripts in its `bin/` folder. | code (bash helper scripts). Telemetry is off unless you opt in when a gstack skill first asks | https://github.com/garrytan/gstack |
| **impeccable** | Design craft + audit, 23 sub-commands (`craft`, `audit`, `polish`, `harden`…). | code (node scripts) | https://github.com/pbakaus/impeccable |

> 🚩 **Never run `/impeccable live`.** It forwards `ANTHROPIC_API_KEY` /
> `CLAUDE_CODE_OAUTH_TOKEN` to a third-party backend. Every other impeccable
> command is fine. Never run `npx impeccable install` or `update` either, both
> wire hooks into your settings.
>
> 🚩 **Never run gstack's `setup`, and never accept its upgrade offer.** Both
> install the whole suite: all 54 skills, about **700 MB** of Playwright
> Chromium (`%LOCALAPPDATA%\ms-playwright` on Windows, `~/.cache/ms-playwright`
> on macOS/Linux), and a `Stop` hook named `gstack-timeline-stop` in
> `settings.json`. BLD switches gstack's update check off so the offer never
> appears, and does not install `gstack-upgrade`. To update gstack, re-run
> `/bld-setup`. An install made by an older BLD did run `setup`; to remove its
> hook, run `gstack-settings-hook remove-source --source gstack-timeline-stop`.
> gstack's own README also asks you to ban Claude's built-in browser tools in
> favour of its browser skill. BLD does **not** do that.

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

`/bld-settings-mcp on` switches any of them to always-on if you want that. It is
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
| **24 `bld-*` skills** | The workflow set: init → refine → deploy, plus review, security, SEO, docs, planning, delegation. Free, with one exception: /bld-runtime-agents drives an external coding agent and needs either a paid ChatGPT subscription for Codex or Gemini's free tier. Every other command costs nothing beyond your own Claude usage. | md, except **six helper scripts**: `bld-setup/scripts/preflight.py` (reads your machine, installs nothing), `bld-settings-professional/scripts/switch-mode.py` (renames BLD's own files), `bld-settings-mcp/scripts/mcp-settings.py` (edits your `.mcp.json`, and refuses to remove entries it did not write), `skills/bld-runtime-activate-mcps/run.py` (spawns an MCP server, then kills it), `skills/bld-optimize-app/scripts/lh-report.mjs` (node, reads a Lighthouse JSON report), and `bld-settings-block-image-generation/scripts/block-image-generation.py` (a PreToolUse hook that refuses image generation, installed and registered with BLD itself, and turned off through that command). All six are ours and short enough to read. A sixth file, `bld-setup/scripts/scenarios.py`, is copied with the rest but is the test harness for `preflight.py` and never runs during setup or during any command. |
| **`bld-executor` agent** | The worker the orchestrator skills fan out to. | md |
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
