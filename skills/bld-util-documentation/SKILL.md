---
name: bld-util-documentation
description: Survey the whole app, then write it up as a documentation subpage inside the app itself, in ASD-STE100 Simplified Technical English. Use when the user says /bld-util-documentation, "write the docs", "add a docs page", "document this app", "user guide", or "help page". Documents only what the code actually does, in controlled English a non-native reader can follow.
---

# bld-documentation — the app, explained in Simplified Technical English

Two halves, and both matter:

1. **Survey** the app that is actually in front of you — its stack, screens,
   flows, data, and limits. Document reality, never intent.
2. **Write** it in **ASD-STE100 Simplified Technical English** and ship it as a
   real subpage of the app (`/docs`), not a Markdown file nobody opens.

The rules live in `references/ste-rules.md`. **Read that file before writing a
single sentence of the page.** STE is a controlled language with hard limits —
sentence length, verb forms, one-word-one-meaning — and it is not something to
approximate from memory.

## Step 0 — Two questions, then go

Ask only what changes the work:

1. **Who reads it?** End users (default), or developers who will run the code?
   One audience per page. If both are needed, write the user page first.
2. **Where does it live?** `/docs` inside the app is the default. Accept any
   route the user names instead.

Everything else is a judgment call — make it and say what you assumed.

## Step 1 — Survey the app

Cheapest useful order. Stop as soon as you can describe every screen and every
user action without guessing.

1. `<app>/CLAUDE.md`, `<app>/planning.md`, `README.md` — purpose, status, backlog.
2. `package.json` — stack, scripts, real dependencies.
3. `design-system/MASTER.md` — the tokens and components the docs page must use.
4. Routes and screens — `app/**/page.tsx` (Next.js) or `src/App.tsx` plus
   `src/components/` (Vite).
5. State, data, and API — stores, `lib/`, `api/`, env vars, database calls.
6. Auth, payments, and anything with a limit or a cost.

Big app, and reading it is getting expensive? Run `/bld-runtime-activate-mcps` → `jcodemunch`
for the search pass, then read only the files it points at.

**The reality rule:** every sentence on the page must trace to a file you read.
A feature you cannot find in the code does not go on the page. A feature that is
half-built goes in a **Known limits** section, described honestly.

Note the exact strings as you go — button labels, route paths, error messages,
env var names. They get copied verbatim later, never paraphrased.

## Step 2 — Outline before prose

Draft the section list and show it to the user. Default shape for an end-user page:

- **What this app does** — three or four sentences, no marketing.
- **Before you start** — accounts, permissions, browser, cost.
- **Screens** — one short section per screen: what it shows, what you can do.
- **Procedures** — numbered steps for each real task the user performs.
- **Data and privacy** — what is stored, where, and for how long.
- **Known limits** — what does not work yet, and what to do instead.
- **Problems and fixes** — real failure states from the code, each with a fix.

For a developer page, swap Screens/Procedures for **Install**, **Run locally**,
**Project layout**, **Environment variables**, **Deploy**.

Cut any section with nothing true to say. An empty section is worse than a
missing one.

## Step 3 — Write it in STE

Open `references/ste-rules.md` and follow it. The five that break most drafts:

- Instructions are imperative and start with the verb. **20 words maximum.**
- Descriptive sentences: **25 words maximum**. Paragraphs: **6 sentences maximum**.
- **No `-ing` verbs** unless the word is a quoted UI string or a technical name.
- **`must` / `can` / `do not`** only. Never `shall`, `should`, `may`.
- One name per thing, for the whole page. No synonyms for variety.

STE text reads flat and repetitive. That is the standard working, not a draft
problem. Do not polish it back toward normal marketing prose.

## Step 4 — Build the page

Follow the app's existing routing. **Add no new dependency** — no MDX, no docs
framework, no router the app does not already have.

- **Next.js app router:** `app/docs/page.tsx`. If the app has `app/[locale]/`,
  it goes in `app/[locale]/docs/page.tsx` and the copy goes through the same
  locale files as every other string.
- **Vite + React with a router:** add the route the way the existing routes are added.
- **Vite + React with no router:** do not install one. Render the docs as a view
  the existing nav can reach, using whatever state the app already uses for
  view switching. If that is genuinely awkward, stop and ask.

Style it from `design-system/MASTER.md` and the components already in the app.
The page is long-form reading, so: one column, roughly 65 to 75 characters per
line, real heading hierarchy (`h1` → `h2` → `h3`), and generous space between
sections. Anchor links on headings, since people arrive from a search.

Add the link to the app's existing nav or footer. A docs page nothing links to
does not exist.

## Step 5 — Verify

1. Start the dev server through the preview tool (never Bash) and open the route.
2. Read the rendered page and check it against the compliance checklist at the
   end of `references/ste-rules.md`. Fix what fails.
3. Check every quoted label, route, and identifier against the real code again.
4. Check it at mobile width, and in dark mode if the app has one.

## Step 6 — Report and keep the workspace true

Tell the user:

- the route, and where the link to it lives,
- which sections you wrote, and which you cut for having nothing true to say,
- **every claim you could not verify in code** — this is the important line,
- the STE rules you bent, and why. Software has no approved-word list, so
  interface verbs (`click`, `sign in`, `download`) are used as technical terms.

Then add a **Documentation** line to the app's `planning.md` backlog for whatever
is still undocumented, and update **Status** in the app's `CLAUDE.md`.

Docs go stale faster than code. When a later sprint changes a documented
behavior, say so and offer to update the page — do not silently let it rot.

## Guardrails

- Do not deploy. This skill ends locally, like every other sprint. The user
  says ship, then `/bld-util-deploy` ships.
- Do not change app code to match the docs. Wrong behavior gets reported, not
  fixed here.
- Do not paste the ASD-STE100 dictionary or spec into this repo. Paraphrased
  rules only — that is what `references/ste-rules.md` is.
