---
name: bld-sprint-init
description: Initial app-building sprint — take an app idea to a good-looking, working, deployed BASE. Orchestrates design direction (ui-ux-pro-max), scaffolding (Vite + React + shadcn/Tailwind), building the core screens, and shipping (deploy skill). Use when the user says /bld-sprint-init, "start a new app", "build me an app", "spin up a new project". Produces a strong base, NOT final polish — that's /bld-sprint-refine.
---

# bld-sprint-init — idea → good-looking, deployed base

One sprint from an app idea to a live, decent-looking base. This skill
**orchestrates skills we already have** — don't reimplement them, invoke them.
Scope is a strong BASE: real structure, on-brand look, deployed. Deep polish,
animation, and craft passes belong to `/bld-sprint-refine`.

Default stack: **Vite + React + TypeScript + Tailwind + shadcn/ui** (user's
preference). Keep it beginner-friendly — explain approval-required commands first.

Goal: make it look **as good as it can in the time budget the user picks** — not a
deliberately bare base. The budget sets how far to push, not whether to care.

## Phase 0 — Ask the time budget (FIRST)

Before anything, ask how much time/depth they want, and scale every phase to it.
Use AskUserQuestion with these tiers:

| Tier | Rough time | What it means |
|------|-----------|---------------|
| ⚡ **Quick** | ~10–15 min | Scaffold + MASTER.md + ONE polished core screen + deploy. Clean and on-brand, minimal scope. |
| 🎯 **Standard** | ~30–45 min | All core screens, responsive, on-brand, light polish (hover/focus/transitions), deploy. Default. |
| 🏗️ **Thorough** | ~60+ min | Standard + a first real polish pass (Emil-style micro-interactions, an impeccable audit), more screens/states. |

Push quality to the ceiling of the chosen tier — a Quick app should still look
genuinely good, just smaller in scope. The strict, exhaustive craft passes
(full impeccable critique, review-animations gate) still live in `/bld-sprint-refine`
regardless of tier.

## Phase 1 — Understand + design direction (DO NOT SKIP THE ASK)

1. **Understand the app:** what it is, who uses it, its one core job. Ask if unclear.
2. **Ask the user for design direction FIRST** — do not guess it (this is the step
   that's easy to skip and shouldn't be): vibe/mood (playful · serious · minimal ·
   bold), light/dark/both, any brand colors or reference apps, audience.
3. **Then run the engine with those answers** and persist a source of truth:
   ```bash
   cd <app-folder>
   python3 <ui-ux-pro-max skill>/scripts/search.py "<product type> <the user's vibe words>" \
     --design-system --persist -p "App Name"
   ```
   Use whichever of `python3` / `python` / `py` actually exists on this machine.
   macOS and most Linux distros ship no bare `python` at all, so hardcoding it
   fails the design step before a single screen gets built.

   This writes `design-system/MASTER.md` — the palette/type/style/rules every screen
   follows. Everything downstream reads this instead of re-running the engine.

## Phase 2 — Scaffold

4. If greenfield: create the Vite React+TS app. Then initialize Tailwind and shadcn:
   `npx shadcn@latest init`. Confirm it runs (`npm run dev` / preview).
5. Apply the MASTER.md tokens (colors, fonts, spacing) to the base CSS/theme so the
   whole app starts on-brand, not default-shadcn.
6. Create `<app>/CLAUDE.md` from the per-app template in the workspace CLAUDE.md
   (purpose, users/monetization angle, stack, design pointer, status). Update its
   Status line at the end of the sprint.

## Phase 3 — Build the base

7. Build the core screens/layout from `design-system/MASTER.md` + the `ui-styling`
   skill (shadcn + Tailwind components). One primary CTA per screen; real content.
8. Pull real shadcn component data on demand via the **`bld-optimize`** skill
   (`run.py shadcn`) instead of guessing component APIs. As the codebase grows, use
   `bld-optimize` (`jcodemunch`) for cheap code search.
9. Verify in the browser preview: it renders, no console errors, responsive at 375 /
   768 / 1024. Fix before shipping.

## Phase 4 — Ship

10. Invoke the **`deploy`** skill → private GitHub repo + Vercel share link, auto-deploy
   on push. Hand the user the live URL.

## Guardrails

- Make it as good as the chosen time budget allows — never a deliberately bare
  base. But respect the budget: don't silently balloon a Quick job into an hour.
  The exhaustive strict craft passes still belong to `/bld-sprint-refine`.
- Never invoke image-generation skills (`design`, `banner-design`) — blocked.
- MCP tools stay on-demand via `bld-optimize`; never add servers to `.mcp.json`.
- Explain approval-required commands in beginner terms before running them.
