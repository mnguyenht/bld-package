<!--
  BLD workspace rules template  →  install to  <your-workspace>/CLAUDE.md

  Sanitised: app names, GitHub handles and personal context replaced with
  <FILL IN>. This is the middle layer. ~/.claude/CLAUDE.md sits above it and
  always applies; per-app CLAUDE.md files sit below and win on conflict.
-->

# <FILL IN: workspace name> — workspace guide

A **container for multiple small web apps**. Not a single project: each app lives
in its own subfolder. Machine-wide rules (explanation level, security drill, skill
installs, platform quirks) live in `~/.claude/CLAUDE.md` and always apply; this
file holds only what's specific to this workspace.

## What we're doing & why

- **Situation:** <FILL IN — who is building here and in what context.>
- **Goal:** <FILL IN — e.g. "ship multiple small web apps, each potentially able to
  make money. Monetization is TBD per app; when an app gets serious, proactively
  raise payments rather than waiting.">
- **Pace:** <FILL IN — e.g. "no schedule; build when inspiration hits. Many sessions
  start with a brand-new idea, so helping find a small, shippable, monetizable idea
  IS the task.">

## Where knowledge lives (link, don't copy)

| Layer | Holds |
|---|---|
| `~/.claude/CLAUDE.md` | machine-wide rules: who I am, security drill, installs, dev loop |
| this file | workspace mission, routing, toolkit, guardrails, deploy conventions |
| `<app>/CLAUDE.md` | per-app purpose, stack, status (template below) |
| `<app>/PRODUCT.md` | per-app register, users, brand, anti-references (`/bld-sprint-planning`) |
| `<app>/planning.md` | per-app vision + **required "Working backlog"** section |
| `<app>/progress.md` | per-app current state: what just landed, what's next, what's blocked |
| `<app>/design-system/MASTER.md` | per-app design truth (ui-ux-pro-max `--persist`) |
| `.claude/skills/*/SKILL.md` | how each procedure actually runs — details live there |
| auto-memory | cross-session facts Claude saves itself |
| `handoff.md` | ephemeral session snapshot (gitignored, overwritten) |

## Routing — pick the next move fast

| Situation | Do |
|---|---|
| Brand-new machine, or nothing installed yet | `/bld-setup` — prints the full tool manifest first, installs nothing without a yes |
| An idea with no shape, or no idea yet | `/bld-sprint-planning` — interview, pressure-test, cut to v1, write PRODUCT/planning/progress |
| Plan approved, time to build | `/bld-sprint-init` (asks time budget ⚡🎯🏗️, then design direction) |
| A screen is basically done | `/bld-sprint-refine` on that screen — never on half-built UI |
| Tweaking an effect by prompt isn't landing (2+ tries) | `/bld-util-customize-component` — build sliders, user tunes by hand, commit the values |
| Need a base shadcn component | `/bld-runtime-activate-mcps` → `shadcn` server |
| Need a rich premade component | `/bld-find-21st` (quality bar: only if it genuinely improves the app) |
| Want 3D flair | `/bld-find-spline` (heroes/landing only; heavy — lazy-load + fallback) |
| Codebase grew, reads getting expensive | `/bld-runtime-activate-mcps` → `jcodemunch` |
| Screen done, or "what's wrong with this app?" | `/bld-optimize-react` — react-doctor scan → triage → fix errors first |
| "Why is my site slow?" / pre-ship perf check | `/bld-optimize-app` — Lighthouse against the **shipped** app, 3 runs, median, then triage |
| App is live but invisible on Google | `/bld-optimize-seo-indexing` — audit the LIVE site with curl, add the crawl plumbing, hand over the account steps |
| Securing an app before shipping something serious | `/bld-optimize-security` — final-boss STATIC pass over all 13 layers. Free + local |
| App needs a user guide / docs / help page | `/bld-util-documentation` — survey the app → write a `/docs` subpage in Simplified Technical English |
| Bulky / repetitive / long generation | `/bld-runtime-agents` — Claude specs + reviews, an external agent writes the code |
| A brain-dump of several independent pieces at once | `/bld-orchestrator-fable` — Claude plans + judges, `bld-executor` workers build in parallel |
| Same loop but on Opus | `/bld-orchestrator-opus` |
| Sprint wrapped, user wants to understand what was built | `/bld-quiz` — learning checkpoint scaled to sprint size |
| Long sprint ahead, or "how many tokens left?" | `/bld-runtime-tokens` — one-shot check → one line + what to do |
| Long session, context rotting | `/bld-util-handoff` → `/clear` → "read handoff.md and continue" |
| Session starts and `handoff.md` exists | offer to resume from it |
| Want the MCP servers connected all session instead of per-query | `/bld-mcp-settings on <server>` — writes them into `.mcp.json`. `off` removes them. Enable `context-mode` only on its own, never in a bundle |
| These command names are too long to type | `/bld-professional-settings on` — pro mode drops the type segment from all 21 names, so each becomes noticeably shorter. `off` returns to the long ones |
| Change done & user explicitly says ship it | `/bld-util-deploy` (established app = just commit + push) — NOT after every edit |
| App about to **charge users** | install a Stripe skill |
| App needs **accounts/DB/backend** | install a Supabase skill |

## Skills at our disposal

The `bld-*` set is documented in the package README. Everything else BLD leans on
is listed in `skills/bld-setup/references/manifest.md`, with GitHub links.

Two that carry non-obvious operating rules worth repeating here:

**gstack** — installed solo: **no hooks in `settings.json`**, telemetry off, no team
mode. **Pruned to 6 skills** (`spec`, `investigate`, `cso`, `review`, `careful`,
`upgrade`) from 54.
- ⚠️ **`setup` un-prunes.** On Windows the wrappers are file copies, not symlinks, so
  `setup` must be re-run after every `git pull` / `/gstack-upgrade` — and it
  regenerates all 54. Immediately follow it with the prune script (idempotent). The
  prune only deletes generated wrappers in `~/.claude/skills/`; the repo and its
  binaries are never touched, so it's fully reversible.
- 🌐 gstack's README asks you to ban Claude's built-in browser tools in favour of its
  own browser skill. **We did not do that** — `mcp__Claude_Browser__*` stays default.
- 📉 Context cost after prune: ~160 tokens, down from ~1.5k. Note the *invoke* cost is
  what's really heavy: `gstack-spec`'s body is ~32k tokens, so reach for it
  deliberately, not reflexively.

**ui-ux-pro-max** — the design **engine**. `--design-system` generates palette/type/
style/UX rules; persist once per app to `design-system/MASTER.md`, then reference it
(don't re-run per screen). Sub-skills: `ui-styling` (shadcn build), `design-system`
(tokens), `slides`, `brand`. (`design` / `banner-design` = **blocked**, image gen.)

## MCP servers — ON-DEMAND ONLY

**On-demand is the default.** Servers run via `/bld-runtime-activate-mcps`
(spawn → query → kill), so no `.mcp.json` is needed and none of them ambiently
sees the codebase. They're unofficial third-party tools and that default is
deliberate.

**Always-on is opt-in, through `/bld-mcp-settings on`.** It writes them into
`.mcp.json` so they connect at startup and stay for the session. More convenient,
and a real change in what a third-party tool observes. Never hand-edit
`.mcp.json` to achieve this: the skill refuses to remove entries it did not
write, and editing around it loses that protection.

- `jcodemunch` (pip) — code search. **Blind to CSS**; use `search_text` or read CSS directly.
- `context-mode` (npx) — heavier; its `ctx_execute` runs shell with logged-in CLIs.
- `shadcn` (`npx shadcn@latest mcp`) — real shadcn registry data.

## Workspace guardrails

- ✋ **Change only what was asked for — including the *values* named.** Full rule in
  `~/.claude/CLAUDE.md` ("Stay in scope"). The repeat offence is retuning a
  neighbouring value while doing the real ask (a duration, an easing, a padding, a
  prop nobody mentioned), or deleting a rule that a change happened to orphan.
  Adjacent ≠ in scope. If the ask truly can't work without a second change, **say so
  first and wait**. Spot something else wrong? Report it, don't fix it.
- 🚫 **No AI image generation** — `design` / `banner-design` are blocked by the
  PreToolUse hook at `~/.claude/hooks/block-image-skills.py` (loads at startup).
  `/bld-setup` copies it there deliberately, out of the cloned package, so deleting
  the clone cannot silently disable it.
- 🔒 **MCP defaults to on-demand.** Always-on is a deliberate choice made through
  `/bld-mcp-settings`, never by hand-editing `.mcp.json`. **`context-mode` gets
  enabled on its own or not at all** — its `ctx_execute` runs shell commands with
  logged-in CLIs, so always-on hands that to the whole session.
- ✅ **Asset lookups have a quality bar** (21st/Spline): only surface what genuinely
  improves the app; **empty-handed is a valid outcome**.
- 🎨 Every app builds from its `design-system/MASTER.md` — no ad-hoc restyling.
- 📝 **Never fabricate** prices, proof, testimonials, or market facts. Unknowns get
  marked `[NEEDS INPUT]` and handed back to a human.
- 🚀 **Deploy discipline — do NOT deploy after every change.** `/bld-sprint-init` deploys once
  as part of its flow; after that, **develop and verify locally** and only commit +
  push (= redeploy) **when the user explicitly says to ship**. Don't run
  `/bld-util-deploy` unprompted.

## Per-app CLAUDE.md (the third layer)

Every app gets its own `CLAUDE.md` at scaffold time (`/bld-sprint-init` creates it).
Keep it under ~30 lines; it loads on top of this file when working in that app:

```markdown
# <app> — <one-line purpose>
- **Users & monetization angle:** (or "none yet")
- **Stack:** <stack> (+ notable deps)
- **Design:** follow design-system/MASTER.md — no ad-hoc restyling
- **App-specific rules:** (overrides/additions to workspace rules)
- **Status:** what works / what's next — update when it changes
```

## The three planning files

Written by `/bld-sprint-planning`, kept current by whoever touches the app. They are not
interchangeable:

- **`PRODUCT.md`** — what this is, who for, brand, anti-references. Durable.
- **`planning.md`** — vision, dated decisions, open questions, and the **required
  `## Working backlog`**. This is the single home for the to-do list; no separate
  `todo.md`. Durable.
- **`progress.md`** — where the work stands *right now* and what's next. Volatile,
  rewritten as work moves. `planning.md` answers *what is the plan*; `progress.md`
  answers *what is the state*.

## Deploy — use the `/bld-util-deploy` skill

**Only when the user asks to ship.** For an app already deployed once, "deploy" =
**commit + `git push`** (auto-redeploys in ~30s). Settled decisions:

- **GitHub:** account **`<FILL IN>`**, always **private**, named **`<appname>`**.
- **Never a free-plan org** — Vercel's Hobby plan refuses private org repos.
- **Vercel:** each app = its own project; after first deploy, every `git push`
  auto-redeploys → `https://<appname>.vercel.app`. Remind: push = redeploy.
  ⚠️ **`*.vercel.app` is a GLOBAL namespace**, so the obvious short name is often
  taken by a stranger. Check **before** naming the project:
  `curl -s -o /dev/null -w "%{http_code}" https://<name>.vercel.app`
  (404 = free; a 200 you don't recognise means pick another).

## Maintenance — keep this file true

- Toolkit changed (skill/hook/server added, removed, renamed)? **Update this file in
  the same session.** Stale rules are worse than missing ones.
- New gotcha learned? Procedure detail goes in the relevant SKILL.md; add a line here
  only if *every* session needs it. Each fact lives in exactly one place.

## Key files & conventions

- `.mcp.json` — **absent by default** (on-demand MCP). `/bld-mcp-settings` writes
  it if you opt into always-on, and is the only thing that should.
- `.claude/agents/` — subagent definitions. Holds `bld-executor`, the worker the two
  orchestrator skills fan out. Project-level beats `~/.claude/agents/` on a name clash.
- `.gitignore` — ignores `.code-index/` (jcodemunch cache) and `handoff.md`.
- One subfolder per app; each app gets its own git repo.
- New skills/hooks register at **startup** — restart Claude Code to load them.
