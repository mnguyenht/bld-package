---
name: bld-refine
description: Refinement sprint — take a working app base and bring it to life with craft, polish, and (optionally) 3D/premade assets. Orchestrates the ui-ux-pro-max steps that /bld-init skipped, plus emil-design-eng, impeccable, and review-animations, then asks about Spline 3D and 21st.dev. Use when the user says /bld-refine, "polish this app", "make it feel great", "bring it to life", after a base exists. Runs per-screen once a screen is basically done.
---

# bld-refine — working base → feels alive

Takes a base (from `/bld-init` or existing) and layers on craft. This skill
**orchestrates other skills** — you must actually INVOKE each one (via the Skill tool /
its script), not just read about it. The last time this was skipped, the app stayed
plain. Don't repeat that.

## ⛔ MANDATORY PROTOCOL — read before doing anything

1. **Every sub-skill below must be actually invoked**, in order, for the screen you're
   refining. "Invoke" = call the Skill tool for that skill (or run its script), load its
   guidance, and **apply the changes it produces**. Mentioning it is not invoking it.
2. **Vibe first.** If there's no agreed design direction / design guide for this app yet,
   STOP and pin it down with the user before any polish (ask: mood, references, what
   "great" looks like). Craft passes on an undefined vibe just thrash.
3. **One screen at a time, fully.** Take a single screen all the way through Phases 1→4
   before starting the next. Don't half-apply across many screens.
4. **You are NOT done until the Completion Checklist at the bottom is filled with real
   evidence** (which skill ran + what it changed) for this screen. If you skipped one,
   say so explicitly — an incomplete refine must be reported as incomplete, never as done.

Announce the screen you're refining, then work the phases.

## Phase 1 — ui-ux-pro-max (the deeper steps bld-init skipped)

**Invoke `ui-ux-pro-max`** against `design-system/MASTER.md` as baseline:
1. **UX validation pass:** `search.py "animation accessibility loading z-index" --domain ux`
   — check the screen against best practices + anti-patterns; apply fixes.
2. **Stack guidelines:** `search.py "<need>" --stack shadcn` for implementation specifics.
3. **Design dials:** re-run `--design-system --motion <n> --density <n>` to tune
   motion/spacing for the app type (dashboard = dense, landing = spacious).
4. **Page overrides:** if the screen deviates, persist `design-system/pages/<page>.md`.
5. Run the **pre-delivery checklist** (contrast, touch targets, reduced-motion, 375px).

## Phase 2 — emil-design-eng (make it FEEL right)

6. **Invoke `emil-design-eng`** and apply it — component details, sensible defaults,
   easing curves, micro-interactions, the invisible things that make software feel great.
   Use **`animation-vocabulary`** when you need the name for an effect.

## Phase 3 — impeccable (craft + audit)

7. **Invoke `impeccable`** and run its craft/polish passes on the screen
   (`polish`, `audit`, `critique`). Apply the findings — don't just collect them.
   🚩 **NEVER `impeccable live`** — it forwards your API keys to their server.

## Phase 4 — review-animations (strict gate, last)

8. Once animations exist and the component is done, **invoke `review-animations`**
   (manual-only) as a strict craft gate. Approval is earned; fix everything it flags,
   then re-run until it passes.

## Phase 5 — Enrichment (ASK the user)

9. Ask whether to bring in richer assets — only where they genuinely elevate the app:
   - **3D scenes** → offer **`bld-find-spline`** (Spline). Heavy; heroes/landing only.
   - **Premade components** → offer **`bld-find-21st`** (21st.dev shadcn parts).
   Present the option; let the user decide. Don't force either in.

## Completion Checklist — REQUIRED output before declaring the screen done

Fill this in for the screen, with a concrete one-liner of what each pass changed
(or an explicit "skipped because …"). Do not claim the refine is complete with blanks.

```
Screen: <name>
- [ ] ui-ux-pro-max   — <what the UX/stack/dials pass changed>
- [ ] emil-design-eng — <micro-interactions / feel changes applied>
- [ ] impeccable      — <audit/critique findings applied>
- [ ] review-animations — <passed? what was fixed to pass>
- [ ] enrichment asked (spline/21st) — <user's decision>
```

If any box is unchecked, the screen is NOT refined — report that to the user rather
than moving on silently.

## Guardrails

- Per-screen, post-done. Never run strict critique/animation review on a half-built app.
- Never image-generation skills (`design`, `banner-design`) — blocked.
- Never `impeccable live`. MCP tools stay on-demand via `bld-optimize`.
- Enrichment (Spline/21st) only if it makes the app better; empty-handed is fine.
- Heavy pass: this is token-intensive by nature. That's expected — don't shortcut the
  invocations to save tokens; if scope is too big, refine fewer screens, not fewer passes.
