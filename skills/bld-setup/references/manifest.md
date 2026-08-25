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
| **emil-design-eng** | Emil Kowalski's philosophy on UI polish, component feel, animation. | md | https://github.com/emilkowalski/skill |
| **animation-vocabulary** | Reverse-lookup glossary: "the bouncy thing when a popover opens" → *Pop in*. Names an effect so you can prompt for it. | md | https://github.com/emilkowalski/skill |
| **review-animations** | Strict animation craft gate. Manual-only, run late and per-component. | md | https://github.com/emilkowalski/skill |
| **karpathy-guidelines** | Anti-LLM-slop rules: ask before coding, surgical changes, verifiable success criteria. | md | https://github.com/multica-ai/andrej-karpathy-skills |
| **find-skills** | Discovers skills on skills.sh. Use it to find, then vet before installing. | md | https://github.com/vercel-labs/skills |
| **copywriting** | Marketing copy: headlines, CTAs, value props, landing page text. | md | https://github.com/coreyhaines31/marketingskills |
| **a11y-audit** | WCAG 2.2 A/AA scan-fix-verify across React, Next, Vue, Svelte, plain HTML. | code (scripts) | https://github.com/alirezarezvani/claude-skills |
| **framer-motion** | Disney's 12 animation principles applied to Framer Motion in React. | md | https://github.com/dylantarre/animation-principles |
| **webapp-testing** | Drives a local web app with Playwright: click, type, screenshot, read console. | code (scripts) | https://github.com/anthropics/skills |
| **terms-of-service** | Drafts and reviews SaaS terms of service. | md | https://github.com/shawnpang/startup-founder-skills |
| **privacy-policy** | Drafts and reviews privacy policies across jurisdictions. | md | https://github.com/shawnpang/startup-founder-skills |

---

## 3. Skills with their own installer

Both are large. Both want to wire hooks. BLD installs them **skill-only**.

| Tool | What it does | Runs code? | Verify at |
|---|---|---|---|
| **gstack** | Garry Tan's engineering framework. 54 skills upstream; BLD keeps **6** (`spec`, `investigate`, `cso`, `review`, `careful`, `upgrade`) and prunes the rest. | code (binaries, hooks, telemetry) | https://github.com/garrytan/gstack |
| **impeccable** | Design craft + audit, 23 sub-commands (`craft`, `audit`, `polish`, `harden`…). | code (node scripts) | https://github.com/pbakaus/impeccable |

> 🚩 **Never run `/impeccable live`.** It forwards `ANTHROPIC_API_KEY` /
> `CLAUDE_CODE_OAUTH_TOKEN` to a third-party backend. Every other impeccable
> command is fine. Never run `npx impeccable install` or `update` either, both
> wire hooks into your settings.
>
> 🚩 **gstack's `setup` regenerates all 54 skill wrappers.** Re-run the prune
> immediately after every `setup` or `/gstack-upgrade`, or the pruned 48 come
> back. gstack's own README asks you to ban Claude's built-in browser tools in
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

## 5. MCP servers — on-demand only, never in `.mcp.json`

These are unofficial third-party servers. BLD spawns them over stdio, fires one
batch of queries, and kills the process. **There is deliberately no `.mcp.json`**,
so none of them ever ambiently sees your codebase.

| Server | What it does | Trust weight | Verify at |
|---|---|---|---|
| **jcodemunch** | Token-cheap code search via tree-sitter. Read-only. Blind to CSS. | low, read-only | https://github.com/jgravelle/jcodemunch-mcp |
| **context-mode** | Heavier code context server. Its `ctx_execute` **runs real shell commands** with your logged-in `gh` / `aws` / `vercel`. | **high** | https://github.com/mksglu/context-mode |
| **shadcn** | Real shadcn/ui registry data so components aren't guessed from memory. Official. | low | https://github.com/shadcn-ui/ui |

---

## 6. What BLD adds itself

| Piece | What it does | Runs code? |
|---|---|---|
| **21 `bld-*` skills** | The workflow set: init → refine → deploy, plus review, security, SEO, docs, planning, delegation. All free. | md, except two python helpers |
| **`bld-executor` agent** | The worker the orchestrator skills fan out to. | md |
| **`block-image-skills.py` hook** | PreToolUse hook that **blocks** `design` and `banner-design`. BLD never generates images with AI; it finds existing assets. | code (yours, ~30 lines, read it) |
| **`CLAUDE.md` templates** | The global + workspace rule layers. Sanitised, no personal data. | md |

---

## 7. NOT installed — opt-in, and most cost money

Listed so you know they exist and know BLD did not put them on your machine.
`/bld-setup` Phase 7 offers to walk you through Codex or Gemini if you want
`/bld-runtime-agents`. The user does every login themselves.

| Tool | Why it's separate | Verify at |
|---|---|---|
| **codex** (OpenAI CLI) | The delegation executor for `/bld-runtime-agents`. Needs a ChatGPT Plus login. Only worth it if you already pay for one. | https://github.com/openai/codex |
| **gemini-cli** | Delegation fallback. Free tier is 20 requests/day. | https://github.com/google-gemini/gemini-cli |

---

## Sources

Every row above was resolved from install metadata on a machine already running
BLD, not from memory:

- `~/.agents/.skill-lock.json` — §2 repos
- `~/.claude/plugins/known_marketplaces.json` — §1 repos
- `npm view <pkg> repository.url`, `pip show`, PyPI JSON API — §4, §5
- `git remote -v` in the installed skill folder — gstack
