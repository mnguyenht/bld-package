---
name: bld-util-customize-component
description: Build a temporary live control panel — real sliders in the browser — for tuning an effect, animation, or component by hand instead of by prompt. Use when the user says /bld-util-customize-component, "let me tune this", "give me sliders", "control panel", "I want to adjust this myself", or when a motion/visual tweak has gone more than two prompt round-trips without landing. Parametric design: pick the axes, design the ranges, hand over the knobs, commit the values, delete the panel.
---

# bld-util-customize-component — put the knobs in the user's hands

## Why this exists

Prompting is a lossy channel for anything felt rather than specified. "A bit
bouncier" costs a full round-trip and lands somewhere adjacent. Six round-trips
later the thing is worse and nobody can say why.

The fix is not better prompting. It's **changing the interface**: stop describing
the value, expose the value. Claude's job moves from *guessing the number* to
*designing the space the number lives in* — which parameters matter, what their
useful range is, and what the defaults should be. Then the user drags a slider for
ten seconds and it's exactly right, because taste is faster to apply than to
articulate.

**The parameter selection IS the design work.** A panel with 40 knobs is a
capitulation — it hands the user a CSS inspector and calls it a tool. A panel with
4 well-chosen knobs and honestly-bounded ranges is a designed space. Left end and
right end should both be things someone might plausibly ship. If half the slider's
travel is garbage, the range is wrong — fix the range, don't make the user avoid it.

## Step 0 — name the effect

Before touching parameters, know what the thing is called. Vague noun → vague
parameters. Use the **`animation-vocabulary`** skill to turn "the bouncy thing when
it opens" into "Pop in", because the name tells you which knobs exist: a Pop in has
overshoot, a fade doesn't.

Then read the actual component. You cannot parameterize code you haven't traced.

## Step 1 — choose the axes (the taste step)

Pick **3–6 knobs**. More than 6 and the user is doing your job. Two tiers:

**Macro sliders — one or two, taste-level.** These are the ones worth naming after
a feeling, and each drives several primitives through a formula you write:

| Macro | Typically drives |
|---|---|
| **Energy** | duration ↓, overshoot ↑, stagger ↓ |
| **Weight** | duration ↑, easing → more decelerated, travel ↑, scale delta ↓ |
| **Chaos** | per-instance jitter in delay / rotation / offset ↑ |
| **Presence** | opacity floor ↑, blur ↓, scale delta ↑ |

**Micro sliders — the primitives**, for hand-tuning after the macro gets close.

Common primitives by domain:

- **Motion** — duration (ms), delay, stagger-per-item, easing (curve), travel
  distance, scale delta, overshoot, spring stiffness/damping/mass
- **Visual** — blur, opacity, border radius, shadow y/blur/opacity, gradient angle,
  grain amount
- **Shader / three.js** — any uniform: speed, amplitude, frequency, noise scale,
  color mix, distortion
- **Behavior** — trigger threshold, hover intent delay, repeat vs. once

### Ranges are the rails — design them, don't default them

A duration slider spanning 0–5000ms is not a tool, it's a shrug. The honest range
for a UI transition is roughly **120–600ms**, and that bound is a design decision
carrying real information. Same for everything else: pick min/max so both extremes
are defensible, set the step fine enough to feel continuous but coarse enough to
land on committable numbers (`10` for ms, `0.05` for unit scalars).

### Chaos needs a seed

Any randomness knob **must** pair with a seed input, and the seed gets committed
alongside the values. Unseeded `Math.random()` means the arrangement the user fell
in love with can never be reproduced — they tune it, approve it, reload, and it's
gone. Use a tiny seeded PRNG (mulberry32 is ~4 lines) rather than a dependency.

## Step 2 — make the component parametric

**Bind to the real component. Never build a copy to tune.** A mock diverges from
the real thing in exactly the details you're tuning, and the values won't transfer.

Three binding mechanisms, cheapest first:

**1. CSS custom properties — default choice for CSS/Tailwind animation.**
Rewrite the component's hardcoded values as `var(--x, fallback)`. The panel sets
the vars on a wrapper element; the browser updates live with **zero React
re-render**, so the animation doesn't restart on every slider drag — which matters
enormously, because a re-render mid-drag makes the panel feel broken.

```css
transition-duration: var(--tune-dur, 260ms);
transition-timing-function: var(--tune-ease, cubic-bezier(.2,.8,.2,1));
transform: translateY(var(--tune-travel, 12px));
```

The fallbacks are the current shipped values — so the component behaves identically
when the panel isn't mounted. That's what makes this safe to leave in.

**2. React props** — when the value drives JS logic, not just style. Give each a
default equal to the current behavior.

**3. three.js uniforms** — for shader work (relevant on shader-heavy pages). The panel
writes `material.uniforms.uX.value` directly in a `useFrame` or an effect; no
re-render, no remount. Never remount the canvas on a slider change.

⚠️ **Adding the `var()` indirection is a real edit to a real file.** Say so before
doing it, and keep the fallback exactly equal to the current value so nothing
changes until a slider moves.

## Step 3 — build the panel

Location:

| Stack | Path | Guard |
|---|---|---|
| Next App Router | `app/tune/page.tsx` | `if (process.env.NODE_ENV === 'production') notFound()` |
| Vite | `src/tune/Panel.tsx`, mounted in `main.tsx` when `import.meta.env.DEV && location.search.includes('tune')` | `import.meta.env.DEV` is the guard; the query param only keeps it out of the way |

⚠️ **The query param is not a guard.** `location.search.includes('tune')` is a
runtime check, so the panel still ships in the production bundle and anyone who
adds `?tune` to the live URL gets your tuning controls. `import.meta.env.DEV` is
a build-time constant that Vite replaces with `false` in a production build, so
the whole panel tree-shakes out and never reaches users at all. Keep both: the
first decides whether it exists, the second whether it is showing.

Next.js note: don't use `app/_tune/` — an underscore prefix is a *private folder*
and opts the route out of routing entirely, so the page would 404.

**Use native `<input type="range">`.** No shadcn Slider, no dependency. This panel
is scaffolding that gets deleted; styling it is wasted work. A `<label>`, a range
input, and a live number readout per knob.

The panel must have:

- **The real component**, rendered against a background that matches its actual
  context — a dark effect tuned on white gets committed wrong.
- **Live numeric readout** next to every slider. A knob whose value you can't read
  can't be committed.
- **A replay button** for enter/exit animations. Without it the user tunes a
  transition they can only see once, then reloads the page forty times.
- **A paste-ready output block** — the current values as the exact code that goes
  into the source, one click to copy. This is the handoff format; don't make the
  user transcribe numbers.
- **A/B compare** if the tuning is subtle: store snapshot A, keep tuning, toggle.
  The eye judges differences far better than absolutes.
- **A reset-to-current button** so the user can always get back to what ships today.

Panel chrome obeys the workspace rules like anything else: **no native scrollbars**,
and **no scroll-jacking** — if the panel scrolls, it scrolls natively.

## Step 4 — hand it over

Start the dev server, then **end the response with the localhost link**. Read the
port the dev server actually printed and build the URL for the stack you used —
they differ, and handing over a link that 404s wastes the handover:

| Stack | Typical URL |
|---|---|
| Next | `http://localhost:3000/tune` |
| Vite | `http://localhost:5173/?tune` |

Never paste a remembered port. Vite moves to 5174 and up when 5173 is taken, and
the panel is only reachable on the one it actually bound. Do not open a browser;
it steals window focus.
Claude's preview pane is for Claude's verification only and never counts as showing
the user anything.

Then stop and wait. The user drags. This step is theirs.

## Step 5 — commit the values, remove the panel

When the user hands back values (or says "it's good"):

1. Write the numbers into the component as the **new defaults** — either replacing
   the hardcoded values or becoming the `var()` fallbacks. The tuned state must be
   what ships with no panel present.
2. Check `prefers-reduced-motion`. A value tuned for delight still needs the
   reduced-motion path to be honest — durations to ~0 or the animation skipped.
   This is accessibility, not polish; it does not get simplified away.
3. **Ask before deleting the panel.** Users often want it around for the next pass.
   If keeping it: it's dev-guarded already, and it's dead weight in the repo — say
   so once and let them decide.
4. Report exactly which files changed and which values moved, old → new.

## Guardrails

- **Only the parameters the user asked to tune go in the panel.** Building a knob
  for a value nobody mentioned is the stay-in-scope violation in its native
  habitat — a control panel is an infinitely tempting place to add "while I'm here"
  sliders. Notice something else that wants tuning? **Say it, don't build it.**
- **Committing tuned values changes only those values.** Not the neighbouring
  padding, not the easing you didn't touch, not the "now-unused" keyframe the change
  orphaned.
- The panel is **scaffolding, not a feature**. It doesn't get polished, doesn't get
  a design system, doesn't get committed to `main` without the user saying so.
- If two round-trips of prompting would genuinely be faster than building a panel,
  **say that and skip the panel**. This skill is for spaces worth exploring — a
  single duration change is not one.
