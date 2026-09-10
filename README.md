# BLD

**A lightweight agent skillset for every step of the building process.**

Ask Claude Code to build something and it will. Ask it twice and you get two
different processes.

BLD gives the process a shape: 23 slash commands, one per step, each carrying the
checklist and the gotchas for that step. Decide what is worth building with
`/bld-sprint-planning`. Build it with `/bld-sprint-init`. Measure it with
`/bld-optimize-app`. Ship it with `/bld-util-deploy`.

You pick the step. The skill brings everything else.

---

## Contents

- [Install](#install)
- [How it stays light](#how-it-stays-light)
- [How commands are named](#how-commands-are-named)
- [What BLD will not do](#what-bld-will-not-do)
- [Repo layout](#repo-layout)
- [The commands](#the-commands)
  - [sprint](#sprint) · [optimize](#optimize) · [find](#find) · [runtime](#runtime)
  - [orchestrator](#orchestrator) · [util](#util) · [settings](#settings) · [special](#special)
- [License](#license)
- [Credits](#credits)

---

## Install

Assuming you already have [Claude Code](https://claude.com/claude-code), plus `npm`
and `git`:

**1. Clone it.**

```bash
git clone https://github.com/mnguyenht/bld-package.git
```

**2. Open Claude in that folder,** or open it in the native Claude app.

```bash
cd bld-package
claude
```

**3. Run the setup command.**

```bash
/bld-setup
```

That is the whole install. Claude reads the file, checks your machine, shows you
what it could install, and puts on only what you pick.

**Why you ask instead of typing a slash command.** `/bld-setup` is a slash
command, and slash commands come from skills that are already installed. A fresh
clone has not installed anything yet, so the command does not exist until BLD
does. Pointing Claude at the file skips that chicken and egg, and it means
nothing reaches your machine before you have seen the list.

### What it does

| Step | What happens |
|---|---|
| **Preflight** | Checks what you already have. Read-only. Stops with install links if something required is missing. |
| **The manifest** | Prints every tool it could install, with a source link and a column saying whether it runs code on your machine. |
| **Deploy accounts** | Asks whether you want `/bld-util-deploy`, since GitHub and Vercel need logins only you can do. |
| **You choose** | Nothing is installed until you pick. |
| **Install** | Cheap and safe first, slow last. |
| **Restart** | Skills register at startup, so Claude Code has to restart before anything works. |

`/bld-setup` records what you chose and what you skipped, so an interrupted setup
resumes where it stopped, and running it again later shows you what you passed on
rather than repeating the whole flow.

Nothing is installed silently, and nothing is installed that was not on the
printed list.

> **Want the real slash command instead?** Copy the one skill in first and
> restart Claude Code, then `/bld-setup` exists:
>
> ```bash
> mkdir -p ~/.claude/skills && cp -r skills/bld-setup ~/.claude/skills/
> ```
>
> Same flow either way. The trade is that this puts one file on your machine
> before you have read the manifest.

> **On macOS or Linux?** `/bld-setup` has been executed and verified on Windows
> and Linux, but never on macOS. If you would rather not be the first,
> [MANUAL-INSTALL.md](MANUAL-INSTALL.md) is the same install written out linearly
> with macOS and Linux spellings. Same end state either way.

---

## How it stays light

Every skillset claims to be lightweight. Here is what BLD does to earn it.

**Nothing runs in the background.** No `.mcp.json` is created unless you ask for
one. Code search servers get spawned for one batch of queries and killed. No
third-party process sits idle with a view of your codebase.

**You can read the whole thing.** BLD is instructions, not a framework. Five small
helper scripts do real work; the rest is markdown you could get through in an
afternoon and disagree with in specific places.

**It ships less than it could.** BLD bundles
[gstack](https://github.com/garrytan/gstack) at 6 skills instead of 54. The other
48 were iOS, paid-provider and team-process skills that duplicated what BLD
already did, and every one cost context on every session.

**Skills call skills.** `/bld-sprint-init` drives the design engine, the
scaffolder and the deploy skill rather than reimplementing any of them.

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

Once you know the set, leading with the type buries the word you are reaching
for. `/bld-professional-settings on` moves the type to the end, so typing the
first few letters lands on the command instead of the category. `off` puts it
back. Both orders keep all three parts, and the switch rewrites folders,
frontmatter and every cross-reference together, so nothing is left pointing at a
command that no longer exists.

Four commands never rename themselves. `/bld-setup` and `/bld-quiz` are what you
reach for when you are confused about your own setup, and a command that renames
itself is the worst thing to need at that moment. The two settings commands stay
fixed for a sharper reason: a switch named after its own state is a trap.

---

## What BLD will not do

These are the opinions. They live in the CLAUDE.md templates, so they apply to
every app you build with it.

- **It will not push your code.** Finishing a change is not a reason to ship one.
- **It will not fix what you did not mention.** Not the padding next to the thing
  you asked about, not the easing curve it read on the way past. If it spots a
  real problem, it tells you and leaves it alone.
- **It will not take over your scrolling.** Wheel and trackpad motion stays
  exactly what your OS would do. Click a nav link and it can glide, because you
  asked to go somewhere.
- **It will not invent a number.** No made-up prices, testimonials, or proof.
  Gaps get marked and handed back, because a plausible fake price ends up quoted
  to a real customer.
- **It will not trust a scanner.** Every audit in here returns a tempting list of
  things nobody asked for. BLD reads the code before believing any of it.

---

## Repo layout

```
bld-package/
├── README.md
├── MANUAL-INSTALL.md               the install written out by hand
├── skills/                         23 commands, one folder each
│   ├── bld-setup/
│   │   ├── SKILL.md
│   │   ├── references/manifest.md  every tool, with source links
│   │   ├── scripts/preflight.py    what is installed, what is missing
│   │   └── scripts/scenarios.py    regression tests for preflight
│   ├── bld-sprint-*/               planning · init · refine
│   ├── bld-optimize-*/             app · react · security · seo-indexing
│   ├── bld-find-*/                 21st · spline
│   ├── bld-runtime-*/              agents · tokens · activate-mcps
│   ├── bld-orchestrator-*/         fable · opus
│   ├── bld-util-*/                 deploy · handoff · documentation · customize-component · copywriting
│   ├── bld-quiz/
│   └── bld-professional-settings/
│       └── scripts/switch-mode.py  renames every command between modes
├── agents/
│   └── bld-executor.md             the worker the orchestrators fan out to
└── templates/
    ├── CLAUDE.global.md            machine-wide rules
    └── CLAUDE.workspace.md         workspace rules
```

A skill is a folder with a `SKILL.md`. The `name:` in its frontmatter is the
command you type. Add `references/` for detail that should not cost context on
every invocation, and `scripts/` for work that has to be deterministic.

---

## The commands

### sprint

*You give Claude a goal and it builds toward it.*

| Command | What it does |
|---|---|
| `/bld-sprint-planning` | Decides what should exist before anything gets built. Plan mode answers *how to build*. This answers *whether to*. |
| `/bld-sprint-init` | Idea to a working, deployed base in one sprint. Asks your time budget and design direction, then scaffolds and ships. |
| `/bld-sprint-refine` | Base to feels-alive. The craft passes init skipped. Run it per screen, once a screen is basically done. |

### optimize

*Improves an app that already exists.*

| Command | What it does |
|---|---|
| `/bld-optimize-app` | Lighthouse against the shipped app, three runs and a median, because one run is a sample and not a measurement. |
| `/bld-optimize-react` | Static scan of your source with react-doctor and your own eslint. Findings are hypotheses, so it triages before it fixes. |
| `/bld-optimize-security` | A static security pass, 13 layers deep. Free, local, and it reports rather than auto-fixing. |
| `/bld-optimize-seo-indexing` | Gets an app found on Google. Audits the live site with curl instead of trusting the source. |

### find

*Locates a ready-made asset.*

| Command | What it does |
|---|---|
| `/bld-find-21st` | Browses [21st.dev](https://21st.dev) for shadcn components. Coming back empty-handed is a valid outcome. |
| `/bld-find-spline` | Same idea for 3D scenes from [Spline](https://spline.design). Heavy, so it only suggests one that earns its weight. |

### runtime

*Applies to how the session runs, not to what gets built.*

| Command | What it does |
|---|---|
| `/bld-runtime-agents` | Boss mode over an external coding agent. Claude specs and reviews, the agent writes. Needs a Codex or Gemini account. |
| `/bld-runtime-tokens` | How much of your Claude window is left, and what to do about it. |
| `/bld-runtime-activate-mcps` | Spawns a code-search server, fires one batch of queries, kills it. |

### orchestrator

*Claude bosses other agents instead of writing code.*

| Command | What it does |
|---|---|
| `/bld-orchestrator-fable` | Plan, execute in parallel, judge each report as a skeptic, re-spec until it passes. |
| `/bld-orchestrator-opus` | The same loop with Opus in the boss seat. |

### util

*Everything in between.*

| Command | What it does |
|---|---|
| `/bld-util-deploy` | Private GitHub repo plus Vercel, auto-deploy on push. After the first run, shipping is a commit and a push. |
| `/bld-util-handoff` | Snapshots the session so you can `/clear` and pick up in fresh context before it rots. |
| `/bld-util-documentation` | Writes a `/docs` page inside your app, in Simplified Technical English. Half-built features go under Known limits. |
| `/bld-util-customize-component` | Builds real sliders in the browser, bound to the real component. You drag, the values get committed, the panel gets deleted. |
| `/bld-util-copywriting` | App copy, with workspace rules for pre-launch proof, litotes, irony, and phrasing that reads as machine-written. |

### settings

*A package setting you turn on and off.*

| Command | What it does |
|---|---|
| `/bld-mcp-settings` | Switches BLD's MCP servers between on-demand and always-on, without touching an entry it did not write. |
| `/bld-professional-settings` | Switches the naming scheme between the two conventions. |

### special

*Acts on BLD itself.*

| Command | What it does |
|---|---|
| `/bld-setup` | Sets BLD up, or adds more of it later. Remembers where it got to. |
| `/bld-quiz` | A learning checkpoint after a sprint, at matching depth. Small changes get a walkthrough instead. |

---

---

## License

MIT. Use it, fork it, ship things with it.

The security checklists in `skills/bld-optimize-security/references/ecc/` are
vendored from [affaan-m/ECC](https://github.com/affaan-m/ECC) and stay under
ECC's own MIT license, included in full beside them.

---

## Credits

BLD is mostly glue. The people below wrote the parts that do the hard work, and
every one is worth a look on its own terms. This is the same table `/bld-setup`
shows you before it installs anything.

### Claude Code plugins

| Tool | What it does | Source |
|---|---|---|
| ponytail | Anti-over-engineering mode. Forces the laziest solution that works. | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| ui-ux-pro-max | The design engine behind `/bld-sprint-init`. Styles, palettes, font pairings, UX rules. | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| claude-code-setup | Anthropic's official setup advisor. | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |

### Skills

| Tool | What it does | Source |
|---|---|---|
| emil-design-eng | Emil Kowalski on UI polish, component feel, animation. | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| animation-vocabulary | Names a motion effect so you can ask for it by its real term. | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| review-animations | Strict animation craft gate. | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
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
| ECC checklists | Security checklists behind `/bld-optimize-security`. Vendored into the skill rather than installed separately, under MIT, with the source commit pinned in `references/ecc/SOURCES.md`. | [affaan-m/ECC](https://github.com/affaan-m/ECC) |

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

On-demand by default: spawned, queried, killed, with no `.mcp.json` involved.
`/bld-mcp-settings` switches any of them to always-on if you want that, per server
and reversibly.

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
