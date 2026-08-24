---
name: bld-find-spline
description: Find ready-made 3D scenes on Spline (spline.design) for use in an app, present a shortlist to pick from, then wire the chosen scene's embed into the code. Use when the user says /bld-find-spline, "find a 3D scene", "add a Spline", "get me a 3D hero/model", or wants a premade 3D asset instead of building one. No MCP, no API key — web browsing + npm. 3D is heavy: only surface a scene if it genuinely elevates the app and the performance cost is acceptable.
---

# bld-find-spline — shop Spline for a 3D scene, then wire the embed

Sibling of `bld-find-21st`, but for **3D scenes on Spline**. Same spirit
(find → present → user picks → wire it in), with two big differences baked in
below: Spline gates its assets, and 3D is expensive.

No MCP server, no API key. Pure WebSearch/WebFetch + npm.

## Hard realities of Spline (read before promising anything)

1. **The community catalog is mostly unreadable.** `community.spline.design`
   listing/tag pages are login-gated JS shells — WebFetch gets an empty shell.
   What IS readable: **`spline.design/examples`** (official template gallery,
   ~18 scenes with `app.spline.design/file/<id>` links) and whatever individual
   scene URLs a web search surfaces. Discover from those, not the community app.
2. **The user must export the asset themselves.** To actually use a scene, the
   user logs into Spline, opens/duplicates it, and exports — either a public
   **scene URL** (`https://prod.spline.design/<id>/scene.splinecode`) or a
   downloaded **`.splinecode`** file. Free tier = 3 exports/month. You CANNOT do
   this step; hand it to the user with clear instructions.
3. **3D is heavy.** Scenes are large (often MBs), GPU-hungry, and rough on mobile
   and battery. This raises the quality bar — see Guardrails.

## Workflow

1. **Pin the need.** What's the 3D for (hero background, product model, icon,
   playful accent), which app, and the vibe. 3D usually earns its weight only on
   heroes / landing pages, rarely on dense app UI.

2. **Find candidates:**
   - WebFetch `https://spline.design/examples` for the official gallery.
   - WebSearch `site:spline.design <thing>` and `site:community.spline.design <thing>`
     to surface indexed scene URLs.
   - Individual `spline.design/...` marketing pages are sometimes readable; the
     community app pages usually are not — don't rely on them.

3. **Present a shortlist** (3–4 max), one block each: name, vibe/what it is, link,
   and a one-line note on likely weight (simple icon vs. full animated room).
   Let the user pick. Don't wire anything yet.

4. **User exports the pick.** Give them the steps:
   > Open the scene in Spline (log in) → duplicate to your workspace →
   > Export → Code / Viewer → copy the **scene URL** (`prod.spline.design/....splinecode`)
   > or download the `.splinecode` file.

5. **Wire the embed** once they give you the URL/file. Two options:
   - **React (their stack):** `npm i @splinetool/react-spline @splinetool/runtime`
     then `import Spline from '@splinetool/react-spline'` and
     `<Spline scene="<url>" />`.
   - **Web component (framework-agnostic):** `<spline-viewer url="<url>">` via the
     `@splinetool/viewer` script — good for a quick drop-in.
   Add a loading state, lazy-load below the fold, and self-host the `.splinecode`
   if CORS blocks the hosted URL.

## Guardrails

- **Only use a Spline scene if it genuinely elevates the app AND the perf cost is
  acceptable.** Same quality bar as `bld-find-21st`, stricter because 3D is
  expensive. If nothing fits, or the app can't afford the weight (mobile-first,
  perf-sensitive, content-dense), say so and stop — a good CSS/SVG treatment often
  beats a heavy 3D scene. Returning empty-handed is a valid outcome.
- Always **lazy-load** the scene, gate it behind `prefers-reduced-motion`, and
  provide a lightweight fallback (poster image / gradient) for mobile and slow
  networks. Never ship a multi-MB 3D scene as a blocking hero.
- Never generate 3D via AI or any image/model generation — find existing scenes
  the user picks. Present, then let the user choose.
