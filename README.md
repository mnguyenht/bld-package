# BLD

**A lightweight agent skillset for every step of the building process.**

Ask Claude Code to build something and it will. Ask it twice and you get two
different processes. BLD gives the process a shape: 21 slash commands, one per
step, each carrying the checklist and the gotchas for that step.

Decide what is worth building with `/bld-sprint-planning`. Build it with
`/bld-sprint-init`. Measure it with `/bld-optimize-app`. Ship it with
`/bld-util-deploy`. You pick the step. The skill brings everything else.

---

## Contents

- [Setup](#setup)
- [What "lightweight" actually means](#what-lightweight-actually-means)
- [How commands are named](#how-commands-are-named)
- [The commands](#the-commands)
- [What BLD will not do](#what-bld-will-not-do)
- [Repo layout](#repo-layout)
- [License](#license)
- [Credits](#credits)

---

## Setup

**You need:** [Claude Code](https://claude.com/claude-code), plus `node`, `npm`
and `git`. Everything else is optional, and BLD tells you what each optional
piece unlocks before you decide.

```bash
git clone https://github.com/<you>/bld-package.git
cd bld-package
```

Then, inside Claude Code:

```
/bld-setup
```

### What that does

| Step | What happens |
|---|---|
| **1. Preflight** | Checks what you already have. Read-only. Stops with install links if a prerequisite is missing. |
| **2. The manifest** | Prints every tool, plugin, CLI and MCP server it could install, with a source link for each and a column saying whether it runs code on your machine. |
| **3. Deploy accounts** | Asks whether you want `/bld-util-deploy`. If yes, GitHub and Vercel get set up first, since those need logins only you can do. |
| **4. You choose** | Multi-select, with an "everything recommended" option. Nothing is installed until you pick. |
| **5. Install** | Cheap and safe first, slow last. |
| **6. Restart** | Skills register at startup, so Claude Code has to restart before anything works. |

`/bld-setup` records what you chose and what you skipped. That means:

- **An interrupted setup resumes** where it stopped instead of starting over.
- **Running it again later** does not repeat the whole flow. It shows you what
  you skipped last time and what is new.

Nothing is installed silently, and nothing is installed that was not on the
printed list.

---

## What "lightweight" actually means

Every skillset claims to be lightweight. Here is what BLD does to earn it.

**Nothing runs in the background.** There is deliberately no `.mcp.json`. Code
search servers get spawned for one batch of queries and killed. No third-party
process sits idle with a view of your codebase.

**You can read the whole thing.** BLD is instructions, not a framework. Four
small helper scripts do real work; the rest is markdown you could get through in
an afternoon and disagree with in specific places.

**It ships less than it could.** BLD bundles
[gstack](https://github.com/garrytan/gstack) at 6 skills instead of 54. The other
48 were iOS, paid-provider and team-process skills that duplicated what BLD
already did, and every one cost context on every session. Cutting them took the
load from roughly 1.5k tokens to 160.

**One hook, and you can read it too.** It blocks AI image generation, because BLD
finds existing assets instead of inventing them.

**Skills call skills.** `/bld-sprint-init` drives the design engine, the
scaffolder and the deploy skill rather than reimplementing any of them. Less to
maintain, and fewer places for the three to disagree.

---

## How commands are named

Every command reads **`bld` · type · skill**. The middle segment tells you what
kind of thing it is before you have learned the set.

```
/bld-sprint-init
 │    │      └── what it does
 │    └───────── which kind of skill it is
 └────────────── the prefix
```

Once you know the set, that middle segment is confirmation you are paying for in
keystrokes. `/bld-professional-mode on` drops it, so commands become prefix plus
skill. `off` puts it back. Same skills either way, and the switch rewrites the
folders, the frontmatter and every cross-reference together so nothing is left
pointing at a command that no longer exists.

Three commands never change name, because they are what you reach for when you
are confused about your own setup: `/bld-setup`, `/bld-quiz`, and
`/bld-professional-mode` itself.

---

## The commands

### sprint

You give Claude a goal and it builds toward it.

| Command | What it does |
|---|---|
| `/bld-sprint-planning` | Decides what should exist before anything gets built. Interviews the idea, pressure-tests the assumption it rests on, cuts it to a shippable v1, and leaves three durable files behind. Plan mode answers *how to build*. This answers *whether to*. |
| `/bld-sprint-init` | Idea to a good-looking, working, deployed base in one sprint. Asks your time budget and design direction first, generates a design system, scaffolds, builds the core screens, ships. |
| `/bld-sprint-refine` | Base to feels-alive. The craft passes init skipped: micro-interactions, motion review, a design audit. Run it per screen, once a screen is basically done. |

### optimize

Improves an app that already exists.

| Command | What it does |
|---|---|
| `/bld-optimize-app` | Runs Google Lighthouse against the shipped app, then triages. Three runs and a median, because one run is a sample and not a measurement. Knows the difference between a real regression and a cold edge cache. |
| `/bld-optimize-react` | Static scan of the source with react-doctor plus your own eslint. Findings are hypotheses, so it triages before it fixes. |
| `/bld-optimize-security` | A static security pass, 13 layers deep. Combines Claude's built-in review, the gstack security skills and vendored checklists. Free, local, and it reports rather than auto-fixing. |
| `/bld-optimize-seo-indexing` | Gets an app found on Google. Audits the live site with curl instead of trusting the source, adds the crawl plumbing, then hands you the account steps only a human can do. |

### find

Locates a ready-made asset on an external surface.

| Command | What it does |
|---|---|
| `/bld-find-21st` | Browses [21st.dev](https://21st.dev) for ready-made shadcn components, shortlists them, installs the one you pick. Coming back empty-handed is a valid outcome. |
| `/bld-find-spline` | Same idea for 3D scenes from [Spline](https://spline.design). Heavy, so it only suggests one when it genuinely earns its weight. |

### runtime

Applies to how the session runs, not to what gets built.

| Command | What it does |
|---|---|
| `/bld-runtime-agents` | Boss mode over an external coding agent. Claude specs and reviews, the agent writes the code. For work that is bulky, repetitive, or a long generation. Needs a Codex or Gemini account. |
| `/bld-runtime-tokens` | One-shot check of how much of your Claude window is left, and what to do about it: keep going, batch, delegate, or hand off. |
| `/bld-runtime-activate-mcps` | Spawns a code-search MCP server, fires one batch of queries, kills it. For big sprints where you would otherwise read twenty files. |

### orchestrator

Claude bosses other agents instead of writing code.

| Command | What it does |
|---|---|
| `/bld-orchestrator-fable` | Plan, execute in parallel, judge each report as a skeptic, re-spec until it passes. Claude never writes the code itself. |
| `/bld-orchestrator-opus` | The same loop with Opus in the boss seat. |

### util

Everything in between. Not building, not optimizing.

| Command | What it does |
|---|---|
| `/bld-util-deploy` | Private GitHub repo plus Vercel, auto-deploy on push. First run is full setup; after that, shipping is a commit and a push. |
| `/bld-util-handoff` | Snapshots the session to `handoff.md` so you can `/clear` and pick up in a fresh context before it rots. |
| `/bld-util-documentation` | Surveys the whole app and writes a `/docs` page inside it, in Simplified Technical English. Documents what the code actually does. Half-built features go under Known limits. |
| `/bld-util-customize-component` | When tweaking an effect by prompt has failed twice, this builds real sliders in the browser, bound to the real component. You drag, the values get committed, the panel gets deleted. |

### special

Acts on BLD itself. These keep the same name in both naming modes.

| Command | What it does |
|---|---|
| `/bld-setup` | Sets BLD up, or adds more of it later. Remembers where it got to. |
| `/bld-quiz` | A learning checkpoint after a sprint. Sizes what was built, then quizzes you on it at matching depth. Small changes get a walkthrough instead. |
| `/bld-professional-mode` | Switches the naming scheme. `on` for short commands, `off` for the type-prefixed ones. |

---

## What BLD will not do

These are the opinions. They live in the CLAUDE.md templates, so they apply to
every app you build with it.

- **It will not push your code.** Finishing a change is not a reason to ship one.
  Deploying happens when you ask, and not before.
- **It will not fix what you did not mention.** Not the padding next to the thing
  you asked about, not the easing curve it read on the way past. Spots a real
  problem? It tells you and leaves it alone.
- **It will not take over your scrolling.** Wheel and trackpad motion stays
  exactly what your OS would do. Click a nav link and it can glide, because you
  asked to go somewhere.
- **It will not invent a number.** No made-up prices, testimonials, or proof.
  Gaps get marked and handed back to you, because a plausible fake price ends up
  quoted to a real customer.
- **It will not trust a scanner.** Every audit in here returns a tempting list of
  things nobody asked for. BLD reads the code before believing any of it.

---

## Repo layout

```
bld-package/
├── README.md
├── skills/                         21 commands, one folder each
│   ├── bld-setup/
│   │   ├── SKILL.md
│   │   ├── references/manifest.md  every tool, with source links
│   │   └── scripts/preflight.py    what is installed, what is missing
│   ├── bld-sprint-*/               planning · init · refine
│   ├── bld-optimize-*/             app · react · security · seo-indexing
│   ├── bld-find-*/                 21st · spline
│   ├── bld-runtime-*/              agents · tokens · activate-mcps
│   ├── bld-orchestrator-*/         fable · opus
│   ├── bld-util-*/                 deploy · handoff · documentation · customize-component
│   ├── bld-quiz/
│   └── bld-professional-mode/
│       └── scripts/switch-mode.py  renames every command between modes
├── agents/
│   └── bld-executor.md             the worker the orchestrators fan out to
├── hooks/
│   └── block-image-skills.py       blocks AI image generation
└── templates/
    ├── CLAUDE.global.md            machine-wide rules
    └── CLAUDE.workspace.md         workspace rules
```

A skill is a folder with a `SKILL.md`. The `name:` in its frontmatter is the
command you type. Add `references/` for detail that should not cost context on
every invocation, and `scripts/` for work that has to be deterministic.

---

## License

MIT. Use it, fork it, ship things with it.

The security checklists in `skills/bld-optimize-security/references/ecc/` are
vendored from [affaan-m/ECC](https://github.com/affaan-m/ECC) and stay under
ECC's own MIT license, included in full beside them.

---

## Credits

BLD is mostly glue. The people below wrote the parts that do the hard work, and
every one of these is worth a look on its own terms. This is the same table
`/bld-setup` shows you before it installs anything.

### Claude Code plugins

| Tool | What it does | Source |
|---|---|---|
| ponytail | Anti-over-engineering mode. Forces the laziest solution that works. | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| ui-ux-pro-max | The design engine behind `/bld-sprint-init`. Styles, palettes, font pairings, UX rules. | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| claude-code-setup | Anthropic's official setup advisor. | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |

### Skills

| Tool | What it does | Source |
|---|---|---|
| emil-design-eng | Emil Kowalski on UI polish, component feel, animation. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| animation-vocabulary | Names a motion effect so you can ask for it by its real term. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| review-animations | Strict animation craft gate. | [emilkowalski/skill](https://github.com/emilkowalski/skill) |
| impeccable | Design craft and audit, 23 sub-commands. | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| gstack | Garry Tan's engineering framework. BLD keeps 6 of its 54 skills. | [garrytan/gstack](https://github.com/garrytan/gstack) |
| karpathy-guidelines | Anti-slop rules: ask before coding, surgical changes. | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) |
| find-skills | Discovers skills on skills.sh. | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| copywriting | Headlines, CTAs, value props, landing page copy. | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) |
| a11y-audit | WCAG 2.2 A and AA scan, fix, verify. | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| framer-motion | Disney's 12 animation principles in Framer Motion. | [dylantarre/animation-principles](https://github.com/dylantarre/animation-principles) |
| webapp-testing | Drives a local app with Playwright. | [anthropics/skills](https://github.com/anthropics/skills) |
| terms-of-service | Drafts and reviews SaaS terms. | [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) |
| privacy-policy | Drafts and reviews privacy policies. | [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) |

Security checklists used by `/bld-optimize-security` are vendored from
[affaan-m/ECC](https://github.com/affaan-m/ECC) under MIT, with the source commit
pinned in `references/ecc/SOURCES.md`.

### Command-line tools

| Tool | What it does | Source |
|---|---|---|
| lighthouse | Google's page auditor. The engine behind `/bld-optimize-app`. | [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse) |
| react-doctor | Static React scanner. The engine behind `/bld-optimize-react`. | [millionco/react-doctor](https://github.com/millionco/react-doctor) |
| react-scan | Runtime re-render overlay. | [aidenybai/react-scan](https://github.com/aidenybai/react-scan) |
| claude-monitor | Local Claude Code usage monitor. Powers `/bld-runtime-tokens`. | [Maciek-roboblog/Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) |
| vercel | Deploy target. | [vercel/vercel](https://github.com/vercel/vercel) |
| gh | GitHub CLI. Creates the private repo in `/bld-util-deploy`. | [cli/cli](https://github.com/cli/cli) |

### MCP servers

On-demand only. Spawned, queried, killed. Never in a `.mcp.json`.

| Server | What it does | Source |
|---|---|---|
| jcodemunch | Token-cheap code search. Read-only. | [jgravelle/jcodemunch-mcp](https://github.com/jgravelle/jcodemunch-mcp) |
| context-mode | Heavier code context. Its `ctx_execute` runs real shell commands, so BLD treats it as the highest-trust item it offers. | [mksglu/context-mode](https://github.com/mksglu/context-mode) |
| shadcn | Real registry data so components are not guessed. | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) |

### Optional, not installed by default

Needed only for `/bld-runtime-agents`. `/bld-setup` offers to walk you through
either one, and you do the login yourself.

| Tool | Why it is separate | Source |
|---|---|---|
| codex | Delegation executor. Needs a paid ChatGPT plan. | [openai/codex](https://github.com/openai/codex) |
| gemini-cli | Delegation fallback. Has a free tier. | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
