# BLD

**A lightweight agent skillset for every step of the building process.**

21 skills for [Claude Code](https://claude.com/claude-code) that carry an idea from
"I think I want to build this" to a deployed, audited, documented app. Type a slash
command, get the part of the process you asked for. That's the whole interface.

```bash
git clone https://github.com/<you>/bld-package.git
# then, in Claude Code:
/bld-setup
```

`/bld-setup` prints a full table of every tool it would install, with a GitHub link
for each one, and installs nothing until you say yes.

---

## What "lightweight" means here

Every skillset calls itself lightweight. Here is what it actually buys you:

**No always-on MCP servers.** There is deliberately no `.mcp.json`. Servers get
spawned for one batch of queries and killed. Nothing third-party sits in the
background with a view of your codebase.

**Markdown first.** Most of BLD is instructions, not code. Three python and node
helpers do real work; everything else is text a person can read in an afternoon.

**Pruned, not piled on.** BLD bundles [gstack](https://github.com/garrytan/gstack)
at 6 skills instead of 54. The other 48 were iOS, paid-provider and team-process
skills that duplicated what BLD already did, and they cost context on every
session. Trimming them took the load from roughly 1.5k tokens to 160.

**One hook.** It blocks AI image generation. BLD finds existing assets instead.

**Skills that call skills.** `/bld-sprint-init` orchestrates the design engine, the
scaffolder and the deploy skill rather than reimplementing any of them. Less to
maintain, less to go wrong.

---

## How commands are named

Every command reads **`bld` - type - skill**. The middle segment tells you what
kind of thing it is before you have learned the set:

    /bld-sprint-init
     ^    ^      ^
     |    |      what it does
     |    which kind of skill it is
     the prefix

Once you know the set, the type segment is just confirmation you are paying for
in keystrokes. `/bld-mode pro` drops it, so every command becomes prefix plus
skill. `/bld-mode friendly` puts it back. Same skills either way.

Three commands never change name, because they are the ones you reach for when
you are confused about your own setup: `/bld-setup`, `/bld-quiz`, `/bld-mode`.

## The skills

### sprint - you give Claude a goal and it builds toward it

| Command | What it does |
|---|---|
| **`/bld-sprint-planning`** | Decides what should exist before anything gets built. Interviews the idea, pressure-tests the assumption it rests on, cuts it to a shippable v1, and leaves three durable files behind. Plan mode answers *how to build*. This answers *whether to*. |
| **`/bld-sprint-init`** | Idea to a good-looking, working, deployed base in one sprint. Asks your time budget and design direction first, generates a design system, scaffolds, builds the core screens, ships. |
| **`/bld-sprint-refine`** | Base to feels-alive. The craft passes init skipped: micro-interactions, motion review, a design audit. Run it per screen, once a screen is basically done. |

### optimize - improves an app that already exists

| Command | What it does |
|---|---|
| **`/bld-optimize-app`** | Runs Google Lighthouse against the shipped app, then triages. Three runs and a median, because one run is a sample and not a measurement. Knows the difference between a real regression and a cold edge cache. |
| **`/bld-optimize-react`** | Static scan of the source with react-doctor plus your own eslint. Findings are hypotheses, so it triages before it fixes. |
| **`/bld-optimize-security`** | The static security pass, 13 layers deep. Combines Claude's built-in review, the gstack security skills and vendored checklists. Free, local, and it reports rather than auto-fixing. |
| **`/bld-optimize-seo-indexing`** | Gets an app found on Google. Audits the live site with curl instead of trusting the source, adds the crawl plumbing, then hands you the account steps only a human can do. |

### find - locates a ready-made asset on an external surface

| Command | What it does |
|---|---|
| **`/bld-find-21st`** | Browses [21st.dev](https://21st.dev) for ready-made shadcn components, shortlists them, installs the one you pick. Coming back empty-handed is a valid outcome. |
| **`/bld-find-spline`** | Same idea for 3D scenes from [Spline](https://spline.design). Heavy, so it only suggests one when it genuinely earns its weight. |

### runtime - applies to how the session runs, not to what gets built

| Command | What it does |
|---|---|
| **`/bld-runtime-agents`** | Boss mode over an external coding agent. Claude specs and reviews, the agent writes the code. For work that is bulky, repetitive, or a long generation. |
| **`/bld-runtime-tokens`** | One-shot check of how much of your window is left, and what to do about it: keep going, batch, delegate, or hand off. |
| **`/bld-runtime-activate-mcps`** | Spawns a code-search MCP server, fires one batch of queries, kills it. For big sprints where you would otherwise read twenty files. |

### orchestrator - Claude bosses other agents instead of writing code

| Command | What it does |
|---|---|
| **`/bld-orchestrator-fable`** | Plan, execute in parallel, judge each report as a skeptic, re-spec until it passes. Claude never writes the code itself. |
| **`/bld-orchestrator-opus`** | The same loop with Opus in the boss seat. |

### util - everything in between. Not building, not optimizing

| Command | What it does |
|---|---|
| **`/bld-util-deploy`** | Private GitHub repo plus Vercel, auto-deploy on push. First run is full setup; after that, shipping is a commit and a push. |
| **`/bld-util-handoff`** | Snapshots the session to `handoff.md` so you can `/clear` and pick up in a fresh context before it rots. |
| **`/bld-util-documentation`** | Surveys the whole app and writes a `/docs` page inside it, in Simplified Technical English. Documents what the code actually does. Half-built features go under Known limits. |
| **`/bld-util-customize-component`** | When tweaking an effect by prompt has failed twice, this builds you real sliders in the browser, bound to the real component. You drag, the values get committed, the panel gets deleted. |

### special - acts on BLD itself rather than on your app

These keep the same name in both modes.

| Command | What it does |
|---|---|
| **`/bld-setup`** | Turns a fresh Claude Code install into this one. Prints every tool, plugin, CLI and MCP server it would install with a GitHub link for each, gets consent, then installs only what is missing and writes the CLAUDE.md rule layers. Idempotent. |
| **`/bld-quiz`** | A learning checkpoint after a sprint. Sizes what was built, then quizzes you on it at matching depth. Small changes get a walkthrough instead. |
| **`/bld-mode`** | Switches the naming scheme above. Renames the folders, the frontmatter and every cross-reference together, so nothing ends up pointing at a command that no longer exists. |

## House rules BLD builds in

These are the opinions. They are in the CLAUDE.md templates, so they apply to every
app you build with it.

- **Local first.** Never commit and push just because a change is done. Shipping is
  something you ask for.
- **Stay in scope.** Change only what was asked for, including the neighbouring
  values nobody named. Something else looks wrong? Report it, do not fix it.
- **Never hijack scrolling.** Wheel and trackpad motion stays exactly what the OS
  would do. Clicking a nav link is consent to travel, so that can glide.
- **Never fabricate.** No invented prices, testimonials, or proof, anywhere.
  Unknowns get marked and handed back to a human.
- **Findings are hypotheses.** Every scanner in here hands you a tempting list of
  things nobody asked you to touch. Read the code before believing any of it.

---

## Credits

BLD is mostly glue. The heavy lifting belongs to the people below, and every one of
these is worth a look on its own. This is the same table `/bld-setup` prints before
it installs anything.

### Claude Code plugins

| Tool | What it does | Source |
|---|---|---|
| **ponytail** | Anti-over-engineering mode. Forces the laziest solution that works. | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| **ui-ux-pro-max** | The design engine behind `/bld-sprint-init`. Styles, palettes, font pairings, UX rules. | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| **claude-code-setup** | Anthropic's official setup advisor. | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |

### Skills

| Tool | What it does | Source |
|---|---|---|
| **emil-design-eng** | Emil Kowalski on UI polish, component feel, animation. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| **animation-vocabulary** | Names a motion effect so you can ask for it by its real term. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| **review-animations** | Strict animation craft gate. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| **impeccable** | Design craft and audit, 23 sub-commands. | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| **gstack** | Garry Tan's engineering framework. BLD keeps 6 of its 54 skills. | [garrytan/gstack](https://github.com/garrytan/gstack) |
| **karpathy-guidelines** | Anti-slop rules: ask before coding, surgical changes. | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) |
| **find-skills** | Discovers skills on skills.sh. | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| **copywriting** | Headlines, CTAs, value props, landing page copy. | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) |
| **a11y-audit** | WCAG 2.2 A and AA scan, fix, verify. | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| **framer-motion** | Disney's 12 animation principles in Framer Motion. | [dylantarre/animation-principles](https://github.com/dylantarre/animation-principles) |
| **webapp-testing** | Drives a local app with Playwright. | [anthropics/skills](https://github.com/anthropics/skills) |
| **terms-of-service** | Drafts and reviews SaaS terms. | [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) |
| **privacy-policy** | Drafts and reviews privacy policies. | [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) |

### Command-line tools

| Tool | What it does | Source |
|---|---|---|
| **lighthouse** | Google's page auditor. The engine behind `/bld-optimize-app`. | [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse) |
| **react-doctor** | Static React scanner. The engine behind `/bld-optimize-react`. | [millionco/react-doctor](https://github.com/millionco/react-doctor) |
| **react-scan** | Runtime re-render overlay. | [aidenybai/react-scan](https://github.com/aidenybai/react-scan) |
| **claude-monitor** | Local Claude Code usage monitor. Powers `/bld-runtime-tokens`. | [Maciek-roboblog/Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) |
| **vercel** | Deploy target. | [vercel/vercel](https://github.com/vercel/vercel) |
| **gh** | GitHub CLI. Creates the private repo in `/bld-util-deploy`. | [cli/cli](https://github.com/cli/cli) |

### MCP servers

On-demand only. Spawned, queried, killed. Never in a `.mcp.json`.

| Server | What it does | Source |
|---|---|---|
| **jcodemunch** | Token-cheap code search. Read-only. | [jgravelle/jcodemunch-mcp](https://github.com/jgravelle/jcodemunch-mcp) |
| **context-mode** | Heavier code context. Its `ctx_execute` runs real shell commands, so BLD treats it as high trust weight. | [mksglu/context-mode](https://github.com/mksglu/context-mode) |
| **shadcn** | Real registry data so components are not guessed. | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) |

### Optional, not installed by default

| Tool | Why it's separate | Source |
|---|---|---|
| **codex** | Delegation executor for `/bld-runtime-agents`. Needs a ChatGPT Plus login. | [openai/codex](https://github.com/openai/codex) |
| **gemini-cli** | Delegation fallback. Free tier is 20 requests a day. | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |

---

## Repo layout

```
skills/       21 bld-* skills
agents/       bld-executor, the worker the orchestrators fan out to
hooks/        block-image-skills.py
templates/    the CLAUDE.md rule layers, sanitised
```

> Keep this credits section and `skills/bld-setup/references/manifest.md` in sync.
> The manifest is the operational copy and carries a trust column; this one is for
> people deciding whether to install.
