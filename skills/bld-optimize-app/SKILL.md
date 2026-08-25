---
name: bld-optimize-app
description: Audit a whole web app with Google Lighthouse — performance, accessibility, best practices, SEO — then triage the findings and fix the ones that are real. Use when the user says /bld-optimize-app, "run Lighthouse", "check my PageSpeed", "why is my site slow", "audit the live site", "get my scores up", or before shipping something that strangers will load on mobile. Measures the shipped app end to end; /bld-optimize-react reads the source instead.
---

# bld-optimize-app — measure the shipped app, then fix what the numbers point at

`/bld-optimize-react` reads your **source** and tells you what looks wrong.
This skill loads your **shipped app in a real browser** and tells you what *is*
wrong for someone on a mid-range phone. Different instrument, different failures,
neither replaces the other.

| | Reads | Catches | Misses |
|---|---|---|---|
| `/bld-optimize-react` | source files | hooks bugs, dead code, unsafe patterns | anything that only appears once bundled and served |
| **`/bld-optimize-app`** | the running page | LCP, layout shift, blocking JS, contrast, crawlability | logic errors, anything below the fold, anything behind a login |

Run this one **after** the app is deployed or at least built for production, and
after `/bld-optimize-react` has cleared the obvious source-level defects.

## The rule that makes every number meaningful or worthless

> **Never audit a dev server.**

`npm run dev` serves unminified bundles, no tree-shaking, a HMR client, and
source maps. It scores 30 points below the same code built for production. A
Lighthouse run against `next dev` is not a pessimistic measurement, it is a
measurement of something you are never going to ship.

Three valid targets, best first:

| Target | Command | What the number means |
|---|---|---|
| **Live production URL** | already up | The real thing, including your CDN and edge cache. This is the number that counts. |
| **Local production build** | `npm run build && npm run preview` (Vite) or `npm run start` (Next). **Read `package.json` first** — running the wrong one either fails or silently serves the dev build, which is the one measurement this skill says never to take. | Honest about your code, silent about your hosting. Best for before/after on a fix. |
| ~~Dev server~~ | — | **Nothing.** Do not do it. |

## Phase 0 — settle the target before you measure anything

Ask, or derive, three things:

1. **Which URL.** Not the domain, the URL. If the site redirects (`example.com` →
   `example.com/vi`), Lighthouse audits the destination and reports it in
   `finalDisplayedUrl`. Read that field back to the user so nobody argues about
   which page got scored.
2. **Mobile or desktop.** Default **mobile** — it is the harsher run, it is
   Google's default, and it is where the points are lost. Desktop is a second run,
   not a substitute.
3. **Just before a deploy?** Then measure the **local production build**, not the
   live site. A live site that was deployed 60 seconds ago has a cold edge cache
   and will lie to you. See Phase 6.

Also confirm the page is publicly reachable. Lighthouse cannot log in, so an
app behind auth needs the local-build route with a seeded session, or it needs
its public shell audited and the rest declared out of scope. Say which.

## Phase 1 — get an engine running

Two engines run the identical Lighthouse audit. Try them in this order.

### 1a. Local Lighthouse via npx — the one that actually works

```bash
cd "<scratchpad>"
export CHROME_PATH="/c/Program Files/Google/Chrome/Application/chrome.exe"   # Windows
npx -y lighthouse@latest "https://example.com/" \
  --output=json --output-path=./lh-1.json \
  --chrome-flags="--headless=new --no-sandbox --disable-gpu" --quiet
```

Every part of that line is load-bearing, and each one is a lesson from a run that
failed without it:

- **`CHROME_PATH`** — Lighthouse's Chrome launcher does not reliably find Chrome
  on Windows. Without it you get `Unable to connect to Chrome` and waste ten
  minutes on the wrong theory. Probe for it rather than hardcoding:
  ```bash
  for p in "/c/Program Files/Google/Chrome/Application/chrome.exe" \
           "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
           "$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"; do
    [ -f "$p" ] && export CHROME_PATH="$p" && break
  done; echo "CHROME_PATH=$CHROME_PATH"
  ```
- **`--headless=new`**, not bare `--headless`. The old value fails on current
  Chrome. This exact flag string is the one that works.
- **`--no-sandbox --disable-gpu`** — headless Chrome in a tool-driven shell.
- **`--output-path` into the scratchpad**, never the project. A Lighthouse JSON
  report is ~1 MB and has no business in a git repo.
- **`--quiet`** — the progress spinner is thousands of useless output lines.
- Add **`--preset=desktop`** for the desktop run. Nothing else changes.
- Add **`--only-categories=performance`** when re-measuring one fix; it is ~3×
  faster and you already know the other three scores.

**If npx dies with `ECOMPROMISED`** — that is an npm cache-lock heartbeat bug on
Windows, not a Lighthouse problem. The download was fine. Bypass npx entirely:

```bash
mkdir -p lh && cd lh && npm init -y >/dev/null
npm install lighthouse --no-audit --no-fund
node node_modules/lighthouse/cli/index.js "<url>" --output=json --output-path=./lh-1.json \
  --chrome-flags="--headless=new --no-sandbox --disable-gpu" --quiet
```

### 1b. PageSpeed Insights API — usually blocked, try it second

```bash
curl -s --max-time 180 \
  "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<urlencoded>&strategy=mobile&category=PERFORMANCE&category=ACCESSIBILITY&category=BEST_PRACTICES&category=SEO" \
  -o psi-mobile.json
```

Same engine, run on Google's hardware instead of the user's laptop, and it can
also return **CrUX field data** — real measurements from real Chrome users, which
local Lighthouse can never produce.

**Expect it to fail.** Keyless access has returned `quota_limit_value: "0"` and
plain `429 daily quota exhausted` on separate attempts. Anonymous use is
effectively dead; it now wants a free API key from Google Cloud. If it 429s,
say so in one line and go straight to 1a rather than retrying.

### 1c. What does not work: driving pagespeed.web.dev in the browser pane

Do not try. The pane is not displayed, so Chrome never composites frames and
PSI's result poller never fires — the page sits at "Running analysis" forever.
Google *does* accept the job; you just can never read the answer. Spoofing
`document.visibilityState` does not help, the throttle is below the JS layer.
This is the same root cause as animations appearing frozen in the pane.

## Phase 2 — three runs, always

**Lighthouse is noisy.** Performance can swing 10+ points between back-to-back
runs against an unchanged site. A single run is a sample, not a measurement, and
treating one as a measurement is how you end up confidently reporting a
regression that does not exist.

```bash
for n in 1 2 3; do
  npx -y lighthouse@latest "<url>" --output=json --output-path=./lh-r$n.json \
    --chrome-flags="--headless=new --no-sandbox --disable-gpu" --quiet
done
```

Run it with `run_in_background` — three runs is 2–4 minutes and foreground
`sleep` is blocked anyway. Accessibility, best-practices and SEO are
deterministic; only performance needs the repeats.

## Phase 3 — read the report properly

```bash
node <skill>/scripts/lh-report.mjs lh-r1.json lh-r2.json lh-r3.json
```

That prints medians for everything, plus the four things that matter:

**1. Which metric is costing the points.** The performance score is five weighted
metrics, and the weights are lopsided — TBT and LCP together are usually well
over half. A 100-point CLS next to a 40-point LCP is not "mostly fine", it is one
problem. The script reads the weights out of the report rather than from memory,
because they change between Lighthouse majors.

**2. Why LCP is slow, not just that it is.** LCP splits into TTFB → load delay →
load time → render delay. These have nothing to do with each other:

| Dominant phase | What it means | What does NOT fix it |
|---|---|---|
| TTFB | server or edge is slow | image compression |
| Load delay | the browser found out about the element late | anything about the element itself |
| Load time | the asset really is too big | anything else |
| **Render delay** | bytes arrived, nothing painted | **compressing the image** |

Render delay is the one that gets misdiagnosed. On one real audit the LCP element
was a logo that finished downloading in 230 ms and then was not painted for
another **six seconds** — 88% of a 7.2 s LCP. Nothing about that is an image
problem, and every minute spent optimising the logo would have been wasted.

**3. The opportunities list, as hypotheses.** Lighthouse's "estimated savings" is
a model, not a promise. Rank by it; believe it only after you look at the code.

**4. The payload fingerprint** — total bytes, request count, JS transferred. Take
it now, before you change anything. Phase 6 needs it.

## Phase 4 — triage before touching a line

Same discipline as `/bld-optimize-react`: **findings are hypotheses.**

- **Read the actual code before believing any finding.** "Reduce unused
  JavaScript, 57 KB" names a symptom; the cause could be one eager import.
- **Sort by points recoverable, not by how bad the row looks.** A red row worth 2
  points loses to an orange row worth 25.
- **Accessibility failures outrank performance.** They are deterministic, cheap,
  and they affect people rather than a number.
- **Separate config flips from behaviour changes.** Adding `loading="lazy"`,
  setting explicit `width`/`height`, preloading a font: do them. Refactoring an
  animation library to a lazy-loaded variant to reclaim 57 KB: that changes how
  the app behaves, so **report it and let the user decide.** Workspace
  stay-in-scope rules apply hardest here, because a scanner hands you a very
  tempting list of things nobody asked for.
- **Never chase 100.** The last few points on mobile performance often cost more
  than everything before them. State what a realistic ceiling is.

## Phase 5 — fix, one lever at a time

One change per measurement. Batch five fixes and the re-run tells you the sum
moved, not which one did it, and one of them may have been a regression the
others hid.

The usual real levers, in rough order of value per effort:

| Symptom | Lever |
|---|---|
| High TBT | ship less JS: lazy-load below-fold components, drop an eager import |
| LCP render delay | remove what blocks the main thread before first paint |
| LCP load time | modern format (WebP/AVIF), correct `sizes`, `fetchpriority="high"` on the hero |
| CLS > 0 | explicit `width`/`height` on images, reserve space for late content |
| Slow font paint | self-host, subset, `font-display: swap`, preload the one face above the fold |
| SEO < 100 | usually meta or crawlability → that is `/bld-optimize-seo-indexing`, not this skill |

## Phase 6 — re-measure, and prove it rather than asserting it

Three runs again, median again, **and compare the payload fingerprint.**

This is the step that separates a real result from a story. A real case: after a
fix, mobile performance read 82 → 71. That looks like a serious regression. It
was not, and here is how that was settled rather than argued:

- The delivered payload was **byte-identical** before and after — 797 KB, 30
  requests, 161 KB of JS, same two hero images in the initial HTML. Nothing
  different was downloaded or parsed, so the change **could not** have moved FCP
  or LCP. There is no mechanism.
- The 71 was measured moments after a deploy, against a **cold edge cache**.
- The one metric the change *could* affect moved the right way and stayed there:
  **TBT 310 ms → 110–160 ms**, across all four runs.
- Warm runs settled at 79–80 against a single pre-change sample of 82 — so the
  honest conclusion was "no regression", not "a 2-point improvement", because
  there was only ever one before-sample.

Rules that fall out of it, and they are the most valuable thing in this file:

- **A score swing with an identical payload is noise.** Say so, and show the
  fingerprint.
- **Never measure the live site immediately after deploying.** Wait, or measure
  twice, or measure the local build instead.
- **Reason about mechanism, not just numbers.** "Could this change physically
  have moved this metric?" kills more false regressions than any amount of
  re-running.
- **Do not claim a small improvement from a single before-sample.** If you only
  measured once before, you cannot tell 2 points from noise. Say that.

## Reporting

Give the user, in this order:

1. **The four scores, mobile and desktop, in one table.** Medians, with the range
   if the spread was wide.
2. **The single sentence version.** "Desktop is perfect; mobile's 82 is almost
   entirely LCP at 3.7 s." Most audits genuinely reduce to one sentence.
3. **What you fixed**, with `file:line`, and what it moved.
4. **What you deliberately did not fix**, and why — the behaviour-changing
   refactors, with the cost/benefit, as the user's call.
5. **Lab vs field**, once, plainly: local Lighthouse is your laptop simulating a
   phone. It is directional and great for before/after. It is not what Google
   holds against your site — that is CrUX field data from real users, which needs
   PSI or Search Console.

## Pitfalls

- **Auditing the dev server.** The single most common way to produce a
  meaningless report.
- **One run.** Covered above; it is the second most common.
- **Measuring a just-deployed site** and reporting the cold-cache number.
- **Compressing an image to fix a render-delay LCP.** Read the phase breakdown.
- **Chasing SEO points here.** A low SEO score means missing meta or blocked
  crawling. That is `/bld-optimize-seo-indexing`, and it also will not make Google index
  you faster.
- **Reporting a raw score with no target named.** `finalDisplayedUrl` may not be
  the URL that was asked for.
- **Writing 1 MB reports into the project.** Scratchpad only.
- **Retrying the PSI API after a 429.** The quota is daily. Move on.
- **Mass-applying every opportunity Lighthouse lists.** It is a hypothesis list,
  not a to-do list, and some of its suggestions are wrong for your app.
