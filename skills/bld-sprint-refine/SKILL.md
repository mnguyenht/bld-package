---
name: bld-sprint-refine
description: 'sr: Polish a working app base screen by screen. Design craft, motion, optional 3D and premade components. Use for "polish this app", "make it feel great", "bring it to life", once a screen is basically done.'
---

# bld-sprint-refine — working base → feels alive

Takes a base (from `/bld-sprint-init` or existing) and layers on craft. This skill
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

## The bar: bold, not plain (user's standing feedback, 2026-10-18)

"Everything looks way too plain" was the verdict on a pass that ran every phase below. Running the
phases is necessary, not sufficient. On every screen:

- **Emphasize and de-emphasize by context.** Pick the one thing the screen is about and make it
  unmistakable (weight 700, size, the brand color). Everything secondary becomes its own quieter
  entity, not just smaller text: fade it (60–75% opacity), set it in italic, soften its color, or
  give it a pill. Example: a big bold time with the day under it in faded italic; a date picker
  where the chosen date is bold and the month/year is small and muted.
- **Vary the composition.** Don't stack every element left-aligned in identical rows. Mix
  alignments (a right-aligned status pill, a two-tile row, a centered quiet action), group related
  controls, and give the screen one focal block.
- **Color is a signal, not decoration.** The accent marks the one main action. A ring, a fill or a
  tint must mean something the user could name; if it can't, remove it. Prefer semantic color
  (green = live/online) over brand color for states.
- **Cut text.** Hints and captions that repeat the title go. If a setting needs a paragraph, the
  setting is designed wrong.
- **Motion is part of the build, not a garnish.** Every screen gets purposeful motion: list
  entrances, state changes, press feedback, one moment of delight where it's rare. The
  review-animations gate in Phase 4 still decides what stays.
- **Voice:** clear and casual for the audience. Slang that tries too hard reads worse than plain.

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

   **6b. Only if the screen has gesture-driven UI or glass surfaces** (drag, swipe,
   sheets and drawers, carousels, flick-to-dismiss, translucent toolbars): **invoke
   `apple-design`** and apply it. It covers what emil-design-eng doesn't: velocity
   handoff, momentum projection, rubber-banding, translucent materials. A static screen
   skips it and the checklist says so. Three guards, every time:
   - **Ask it a concrete question** about the element ("how should this bottom sheet track
     the drag and settle?"). Invoked bare, it only replies with a greeting and waits.
   - **`design-system/MASTER.md` wins.** Ignore its system-font default and translucent
     chrome unless MASTER.md already chose them.
   - **Never on page scroll.** Springs, momentum and rubber-banding go on elements the
     user drags, never on the page's own scrolling, which stays exactly native.

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
- [ ] apple-design    — <gesture/material changes, or "skipped: no gestures or glass">
- [ ] impeccable      — <audit/critique findings applied>
- [ ] review-animations — <passed? what was fixed to pass>
- [ ] bold bar      — <what was emphasized, what was quieted, what color/ring was removed>
- [ ] enrichment asked (spline/21st) — <user's decision>
```

If any box is unchecked, the screen is NOT refined — report that to the user rather
than moving on silently.

## Guardrails

- Per-screen, post-done. Never run strict critique/animation review on a half-built app.
- Never `impeccable live`. MCP tools default to on-demand via
  `/bld-runtime-activate-mcps`; always-on is opt-in through `/bld-settings-mcp`.
- Enrichment (Spline/21st) only if it makes the app better; empty-handed is fine.
- Heavy pass: this is token-intensive by nature. That's expected — don't shortcut the
  invocations to save tokens; if scope is too big, refine fewer screens, not fewer passes.
