# The 24 BLD commands, and what each one needs

**Phase 2 prints this table verbatim before asking which skills to install.**
Nobody can choose from a list they have not seen, and "do you want react-doctor?"
is unanswerable if you do not know which command uses it.

**Needs** is the only column that drives the next question. A command with a dash
there works the moment BLD is copied. Everything else is named in `manifest.md`,
with its source and whether it runs code.

**A dash with a tool in italics after it is an optional enhancement**, not a
requirement: the command runs without it and does more with it. Phase 3 offers
those separately, after the required tools, and never to someone who took the
self-contained bundle - that bundle's whole promise is that nothing else
installs.

## sprint — take an idea to a built thing

| Command | What it does | Needs |
|---|---|---|
| `/bld-sprint-planning` | Decides what should exist before anything gets built. Interviews the idea, cuts it to a shippable v1, writes the planning files. | — *(a deeper spec option with **gstack**)* |
| `/bld-sprint-init` | Idea to a working, deployed base in one sprint: design direction, scaffold, core screens. | **Plugins** (the design engine picks your palette and type) |
| `/bld-sprint-refine` | Base to feels-alive. The craft passes init skipped, run per screen. | **Plugins**, **Core skills**, **impeccable** |

## optimize — improve something that exists

| Command | What it does | Needs |
|---|---|---|
| `/bld-optimize-app` | Lighthouse over the live app, three runs and a median, then triage. | — (Lighthouse runs through `npx`) |
| `/bld-optimize-react` | Static scan of your source for real defects: bugs, hooks, re-renders, a11y. | **React tools** |
| `/bld-optimize-security` | A static security pass, 13 layers deep. Reports, never auto-fixes. | — *(4 more passes with **gstack**)* |
| `/bld-optimize-seo-indexing` | Gets an app found on Google. Audits the live site rather than the source. | — |

## find — locate a ready-made asset

| Command | What it does | Needs |
|---|---|---|
| `/bld-find-21st` | Browses 21st.dev for shadcn components. Empty-handed is a valid answer. | — |
| `/bld-find-spline` | The same for 3D scenes from Spline. Only suggests one that earns its weight. | — |

## runtime — how the session runs

| Command | What it does | Needs |
|---|---|---|
| `/bld-runtime-activate-mcps` | Spawns a code-search server, fires one batch of queries, kills it. | **Code search** (only for jcodemunch; the other two fetch themselves) |
| `/bld-runtime-agents` | Boss mode over an external coding agent. Claude specs and reviews, the agent types. | **Codex or Gemini** (Phase 7) |
| `/bld-runtime-tokens` | How much of your Claude window is left, and what to do about it. | **Token monitor** |

## orchestrator — Claude bosses other agents

| Command | What it does | Needs |
|---|---|---|
| `/bld-orchestrator-fable` | Plan, execute in parallel, judge each report as a skeptic, re-spec until it passes. | — |
| `/bld-orchestrator-opus` | The same loop with Opus in the boss seat. | — |

## util — everything in between

| Command | What it does | Needs |
|---|---|---|
| `/bld-util-deploy` | Private GitHub repo plus Vercel, auto-deploy on push. | **gh + vercel**, and two logins only you can do (Phase 7) |
| `/bld-util-copywriting` | Hero, CTAs, empty states, pricing. No invented proof, no AI tells. | **Core skills** (it builds on the copywriting skill) |
| `/bld-util-documentation` | Writes a docs page inside the app, in Simplified Technical English. | — |
| `/bld-util-customize-component` | Real sliders in the browser so you tune an effect by hand, then commit the values. | — |
| `/bld-util-handoff` | Snapshots the session so a fresh one can continue it. | — |

## settings and special

| Command | What it does | Needs |
|---|---|---|
| `/bld-mcp-settings` | Switches BLD's MCP servers between on-demand and always-on. | — |
| `/bld-professional-settings` | Switches command naming between friendly and pro mode. | — |
| `/bld-settings-block-image-generation` | The one switch for the image-generation block, which is on from install. `off` allows it again. | — |
| `/bld-quiz` | Quizzes you on what the last sprint actually built. | — |
| `/bld-setup` | This. Installs BLD, or adds more of it later. | — |

## The two bundles Phase 2 offers

- **All 24.** Every command above.
- **Only the self-contained ones (16).** Every row whose Needs column is a dash:
  `/bld-sprint-planning`, `/bld-optimize-app`, `/bld-optimize-security`,
  `/bld-optimize-seo-indexing`, `/bld-find-21st`, `/bld-find-spline`,
  `/bld-orchestrator-fable`, `/bld-orchestrator-opus`,
  `/bld-util-documentation`, `/bld-util-customize-component`,
  `/bld-util-handoff`, `/bld-mcp-settings`, `/bld-professional-settings`,
  `/bld-quiz`, `/bld-settings-block-image-generation` and `/bld-setup`. Nothing
  else to install, nothing half-working.

The other eight each need one thing, named in their row: `/bld-sprint-init` and
`/bld-sprint-refine`, `/bld-optimize-react`, `/bld-util-copywriting`,
`/bld-util-deploy`, `/bld-runtime-agents`, `/bld-runtime-tokens` and
`/bld-runtime-activate-mcps`.

`/bld-optimize-security` is in that sixteen on purpose: it runs its whole pass
without gstack, using the built-in review and BLD's own vendored checklists.
gstack adds four more passes to it.

**Every installed skill costs context in every session.** Claude Code loads each
skill's one-line description at startup, and that listing is capped at about 1%
of the model's context window, shared with every other skill on the machine. All
24 of BLD's descriptions together run about 5,200 characters. That is the honest
argument for taking fewer: it is not disk space, it is the budget the listing
competes for.
