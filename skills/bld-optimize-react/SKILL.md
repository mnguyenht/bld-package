---
name: bld-optimize-react
description: Scan a React/Next app for real defects — bugs, hooks misuse, perf, a11y, security — using the globally-installed react-doctor CLI, the app's own eslint, and (opt-in) react-scan's runtime re-render overlay. Triage findings before fixing. Use when the user says /bld-optimize-react, "scan this app", "what's wrong with my React code", "check for re-renders", "audit this app", or before shipping a screen.
---

# bld-react-optimize — find what's actually broken, then triage

Three tools, **two of which overlap**. Read this before running anything.

| Tool | Type | Installed as | What it uniquely catches |
|---|---|---|---|
| **react-doctor** | static CLI | **global** (`react-doctor`) | bugs, hooks rules, perf, a11y, security, dead code, supply chain |
| **app's own eslint** | static | per-app devDep | Next-specific rules react-doctor lacks (`no-img-element`, `no-html-link-for-pages`) |
| **react-scan** | **runtime** overlay | global CLI (`init` only) | re-renders you can only see by *using* the app |
| **`/code-review`** | model review of the **diff** | built-in | logic errors no rule encodes — run *after* fixing |

## The redundancy — do NOT run eslint-plugin-react-hooks separately

`react-doctor` **bundles `eslint-plugin-react-hooks` as a dependency** and runs its
rules under its own names:

- `eslint-plugin-react-hooks/rules-of-hooks` → `react-doctor/rules-of-hooks` (error)
- `eslint-plugin-react-hooks/exhaustive-deps` → `react-doctor/exhaustive-deps` (warn)

Running the plugin standalone re-reports the same findings. **Phase 1 already covers
hooks.** Phase 2 exists only for the Next-specific rules, which is a genuinely
different set.

## Phase 1 — react-doctor (always; this is 90% of the value)

```bash
react-doctor <app-path> --no-telemetry
```

**`--no-telemetry` is mandatory, every run.** react-doctor ships `@sentry/node` and
posts to a score API by default. The flag kills both.

Exit code 1 means "found an error-severity issue" — that is a *result*, not a
crash. Don't report it as a failure.

Useful narrowing (all composable):

| Need | Flag |
|---|---|
| every finding, not just top 3 | `--verbose` |
| only what changed vs. a branch | `--scope changed --base master` |
| one category | `--category Security` (or Bugs, Performance, Accessibility, Maintainability) |
| machine-readable | `--json --json-out report.json` |
| offline / no network | `--no-supply-chain` |
| runaway guard | `--max-duration 180` |
| why did this fire? | `react-doctor why <file>:<line>` |

### Speed rules (this tool is slow if you aim it wrong)

- **Never run it at the workspace root.** Always pass a single app path — the root
  has 4 app folders and it will scan all of them.
- **Never `npx react-doctor@latest`.** That re-downloads 251 packages *per run* and
  is what made the first attempt feel endless. It is installed globally; call
  `react-doctor` directly.
- Correctly scoped, a run is **~10 seconds**. If it takes minutes, the path is wrong.

## Phase 2 — the app's own eslint (only if it has one)

```bash
npm --prefix <app-path> run lint
```

Check for `eslint.config.mjs` + a `lint` script first; skip silently if absent.
Report **only** rules react-doctor didn't already flag — mostly `@next/next/*`.
Exit code is non-zero on warnings; judge by output, not the code.

⚠️ **Expect this to add little.** On a real project (2026-07-29) it returned a strict
*subset* of phase 1 — react-doctor `--verbose` already had all 5 `no-img-element`
sites plus a 6th. It looked like it found unique issues only because a non-verbose
react-doctor run hides everything below its top 3 rules. It costs seconds, so still
run it, but don't present its output as new until you've diffed it against phase 1.

## Phase 3 — react-scan (opt-in, runtime, needs a human)

⚠️ **Ask before doing this. It requires editing the app.**

react-scan is not a scanner you point at a folder — it's an **overlay that renders
in the browser** and highlights components as they re-render. It only produces
findings while someone *uses* the app.

The global `react-scan` CLI (v0.5.7) exposes **only `init`**, which permanently
edits the project. Three ways in, cheapest first:

1. **Browser extension** — zero code changes, works on any running dev server.
   Best option. Link: `github.com/aidenybai/react-scan` → browser extension guide.
2. **Temporary script tag** — add to `app/layout.tsx` `<head>`, run, then **revert**:
   ```tsx
   <Script src="//unpkg.com/react-scan/dist/auto.global.js"
           crossOrigin="anonymous" strategy="beforeInteractive" />
   ```
   Say up front that it will be reverted, and actually revert it.
3. `react-scan init` — permanent. Only if the user explicitly wants it committed.

Then: dev server up → **hand the user the localhost link** and let them drive.
Claude's preview pane doesn't count as showing them anything.

## Phase 4 — `/code-review` on the fixes (after fixing, before shipping)

Phases 1–2 are **rule matchers**: they find patterns someone wrote a rule for, on
every file, forever. `/code-review` is a **reader**: it reasons about the actual
diff and catches logic errors no rule encodes. Opposite failure modes, so run both.

Run it **after** applying fixes, on the resulting diff — not on the untouched
codebase, where phase 1 already has better coverage.

```bash
/code-review
```

**Why this step exists** (real case, 2026-07-29): a fix for
`no-async-event-handler-without-reentry-guard` was written as
`if (status === "sending") return;` — which does nothing, because `status` is React
state and inside the handler's closure it still holds the previous render's value.
It *looked* correct. Re-running phase 1 caught it because that rule happened to
exist; a reviewer would have caught it by reasoning. **Don't assume a fix worked
because it compiles — re-run phase 1 and read the diff.**

Two constraints:

- **`/code-review ultra`** (multi-agent cloud review) is **user-triggered and
  billed**. Claude cannot launch it — never try via Bash or otherwise. Mention it
  as an option for a big change; the user runs it.
- Plain `/code-review` reviews **changed code**. It is not a whole-repo audit, so
  it complements phase 1 rather than replacing it.

## Triage — findings are hypotheses, not a to-do list

react-doctor says this itself, and it's right:

- **Read the actual file before believing any finding.** Mark each true positive,
  false positive, or needs-review, with high/medium/low confidence.
- **Fix root cause, not the rule.** Never silence a rule or edit `doctor.config.ts`
  to make a finding go away unless the user asks.
- **Ignore** pure style nits and theoretical issues with no real impact.
- **One rule spanning dozens of files = a migration.** Fix one representative case,
  confirm the recipe, *then ask* before touching the rest. Never mass-fix unreviewed.
- Errors before warnings. Bugs and Security before Maintainability.

## Reporting back

Give the user: total count by severity → the errors in full with file:line → a
one-line summary of the warning families → a recommendation of what's worth fixing
now. **Do not start fixing without saying what you're about to change** — the
workspace stay-in-scope rule applies here more than anywhere, because a scanner
hands you a tempting list of 24 things nobody asked you to touch.

## Config (per-app, optional)

`doctor.config.ts` in the app root tunes rules; `react-doctor rules list` /
`rules set <rule> <severity>` / `rules disable <rule>` manage them. Only reach for
this when a rule is genuinely wrong for the project, never to hide a real finding.
