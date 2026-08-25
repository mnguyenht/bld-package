---
name: bld-find-21st
description: Browse the 21st.dev marketplace for ready-made shadcn/Tailwind UI components, present a shortlist for the user to pick from, then install the chosen one. Use when the user says /bld-find-21st, "find a component", "find UI on 21st", "get me a <navbar/hero/card/form/etc>", or wants a premade UI asset instead of building one from scratch. No MCP server, no API key, no AI generation — pure web browsing.
---

# bld-find-21st — shop the 21st.dev marketplace

Find existing, human-made UI components on 21st.dev and let the user pick. This
does NOT use an MCP server, an API key, or AI generation — just web search + fetch.
Nothing of the user's leaves the machine beyond normal web requests.

The user's default stack is **shadcn/ui + Tailwind** (see their preferences), which
is exactly what 21st.dev ships — so components drop in cleanly.

## Workflow

1. **Pin the need.** Get the component type (hero, navbar, pricing card, login
   form, testimonial, etc.), which app it's for, and any style cue (dark, playful,
   minimal). Ask only if it's unclear — don't over-interrogate.

2. **Search the marketplace** with WebSearch:
   ```
   site:21st.dev <component type> <optional style>
   ```
   Category pages (`21st.dev/s/...`, `21st.dev/community/components/s/...`) are
   JS-rendered and NOT readable by WebFetch — use them only to discover URLs.
   Individual component pages (`21st.dev/<author>/<component>`) ARE readable.

3. **Read 3–4 specific component pages** with WebFetch. Pull: name, author,
   what it looks like, key features, dependencies, and the install command.

4. **Present a shortlist** (3–4 options), one compact block each:
   - **Name** by @author — one-line look/feel
   - Features + dependencies (flag heavy deps like `framer-motion`)
   - Link to the page
   - Install: `npx @21st-dev/cli add <author>/<component>`

   Let the user pick. Don't install anything yet.

5. **Install the pick.** Run `npx @21st-dev/cli add <author>/<component>` in the
   target app, or fetch the component's registry code and adapt it by hand. Then
   wire it into their app and install any missing deps.

## Prerequisites to flag

- 21st components need **shadcn + Tailwind**. The mock apps are plain Vite React —
  if shadcn isn't initialized, run `npx shadcn@latest init` in that app first.
- Some components pull `framer-motion`, `lucide-react`, etc. Call these out before
  installing so the user isn't surprised by new dependencies.
- For a quick shadcn primitive (button, dialog, table) the user may not need
  21st.dev at all — the on-demand shadcn MCP (`/bld-runtime-activate-mcps` → `shadcn`) covers
  the base registry. Use 21st.dev for richer, styled, opinionated components.

## Guardrails

- **Only surface a component if it genuinely fits the app and makes it BETTER.**
  This is a quality bar, not a fetch quota. If the search turns up nothing that's
  a real improvement over what's there (or over a quick hand-built version), say so
  plainly — "nothing on 21st.dev beats what you'd get building this directly" — and
  stop. Returning empty-handed is a valid, expected outcome. Never pad the shortlist
  with mediocre matches just to have something to show.
- Never invoke the 21st.dev **Magic MCP** or any AI image/component generation —
  the user wants existing assets they pick, not generated ones.
- Present, then let the user choose. Don't auto-pick and install without a pick.
