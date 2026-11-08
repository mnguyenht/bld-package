---
name: bld-optimize-security
description: 'os: Full security audit of an app across 13 layers. Reads code and config, plus two probes of the app on localhost; never attacks a live site. Use for "secure this app", "full security audit", "harden this", or before shipping something serious.'
---

# bld-optimize-security — the final-boss security pass

One skill that runs every *static* security tool we have against one app and
returns a single triaged report. It **orchestrates** — it invokes other skills and
checklists rather than re-deriving them. Detail lives in `references/`; this file
is the conductor. Everything here is free and local. Dynamic runtime pentesting
(actually attacking a live target) is deliberately **out of scope** — the tooling
for it costs money, and BLD is free. The one runtime step is Phase 4b: two
probes that need nothing but `curl`, sent only to the app running on
localhost, because reading code can miss a route that asking the app cannot.

## What it combines

| Source | Role | Cost |
|--------|------|------|
| Built-in `/security-review` skill | Fast first-pass vuln scan of the diff/code | free |
| `gstack-cso` | Chief-Security-Officer deep review | free |
| `gstack-review` | Pre-landing code review (security lens on the diff) | free |
| `gstack-careful` | Guardrails around any destructive command this skill runs | free |
| `gstack-investigate` | Root-cause a confirmed critical before fixing | free |
| ECC `security-review.md` + `cloud-infrastructure-security.md` | Layered checklists (app + infra) | free (vendored markdown) |
| ECC `production-audit.md` | "What breaks in prod" readiness (infra layers) | free (vendored) |
| ECC `security-bounty-hunter.md` | Adversarial hunt for *remotely reachable* exploits | free (vendored) |
| ECC `agent-architecture-audit.md` | **Only if the app has an LLM/agent** | free (vendored) |
| `agentshield-checklist.md` | Audits our own `.claude/` harness config | free (markdown-only) |
| `curl` against localhost | Phase 4b: logged-out sweep + single-quote probe | free (built in) |

All vendored ECC content is MIT, copied verbatim (except AgentShield, stripped to
checklist-only). See `references/ecc/SOURCES.md`. Dynamic pentesting is **not**
here: apart from Phase 4b's localhost probes, this pass reads code and config,
and it never sends traffic at a live target.

## Before you start — scope & safety

1. **Only our own apps.** This runs adversarial tooling. Confirm the target is an
   app in this workspace (or our deployment). Never point it at anything we don't own.
2. **Read the whole flow first** (ponytail: comprehension is not the lazy part).
   Trace the app's real request paths before checking boxes.
3. **Fully local, no exfiltration.** This audit reads code and config — it does
   not upload the repo anywhere or make external calls. The only traffic it sends
   is Phase 4b's, to `localhost`, never to a deployed URL.
4. **Any destructive command → run it past the `gstack-careful` mindset first**
   (resetting state, deleting generated files). Confirm before, not after.

## Phase 0 — Scope the target

Establish, and write down in the report header:

- **App folder** + stack (Vite/React vs Next.js; Tailwind/shadcn; etc.).
- **Backend surface:** Supabase? Stripe? serverless/edge functions? external APIs?
- **Deployed?** local only, or a `<app>.vercel.app` URL exists?
- **Has an AI/agent feature?** (LLM calls, tool use, autonomous loops) → decides
  whether Phase 4's `agent-architecture-audit` runs.
- **Layer applicability:** walk `references/13-layers.md` and mark each of the 13
  layers **applies / N/A** for this app. You audit only the ones that apply, and
  you name any you skip.

## Phase 1 — Harness config scan (Layer 0)

Audit **our own** Claude Code config using `references/ecc/agentshield-checklist.md`.
Read `CLAUDE.md` (all layers), `.claude/settings*.json`, hooks, agents/skills, and
confirm `.mcp.json` is absent. A poisoned harness compromises every app, so this
goes first. Record findings; they're config findings, separate from app layers.

## Phase 2 — Static security review (the core pass)

**`/security-review` and `gstack-review` are diff/PR tools, not whole-repo scanners
— they compare the working tree against `origin/HEAD`.** If they find uncommitted
changes with no diff to point at, some implementations paper over that by
committing (and in the worst case pushing) the working tree themselves just to
have something to review. That is a real incident this skill caused once already
(2026-08-03): an uncommitted-changes tree got auto-committed and pushed
to `main` mid-audit, triggering an unrequested Vercel deploy. **Never let a tool
you invoke take that decision.**

Before invoking either diff-based tool, check the git state yourself:
`git status --short` and `git diff --stat origin/HEAD` (fix `origin/HEAD` first
with `git remote set-head origin main` if that errors — safe, local-only).

- **Uncommitted changes exist:** **review them.** This is the highest-value diff
  in the whole pass, not a reason to skip one. Uncommitted work is the newest
  code, the least reviewed, and the most likely to be seconds away from shipping.
  `/security-review` describes itself as reviewing the *pending* changes on the
  current branch, and pending includes the working tree, so there is a real diff
  here and nothing has to be manufactured to get it.

  **Never commit merely to give a tool something to read.** If a tool genuinely
  refuses a working-tree diff, capture it (`git diff`) and hand it over as
  content, then note in the report which tool could not take it and why. Falling
  back to the whole-repo checklist is the last resort, not the first move, and if
  you do fall back, say plainly that the newest code got the weaker treatment.
- **Clean tree, real diff against origin/HEAD exists** (unpushed commits): safe to
  run both — there's an actual diff for them to review, nothing to manufacture.
- **Clean tree, no diff at all** (already in sync with origin): the diff tools have
  nothing to do. Skip them, note *"no diff to review, already in sync with
  origin/HEAD"*, and move straight on. This is a pass, not a blocker — don't stall
  the audit waiting for a diff that doesn't exist.

Run these over the app and reconcile their findings:

1. Invoke the built-in **`/security-review`** skill (via the Skill tool) for a fast
   vuln sweep — **only per the git-state check above.**
2. Invoke **`gstack-cso`** (via the Skill tool) for the deep security review. This
   one is whole-repo, not diff-based — always safe to run regardless of git state.
3. Walk **`references/ecc/security-review.md`** and
   **`references/ecc/cloud-infrastructure-security.md`** checklists, mapping each
   check to the applicable layer per `references/13-layers.md`. Cover every
   *applies* layer 1–13; skip N/A ones explicitly. Always run this one — it's the
   whole-repo pass that doesn't depend on there being a diff.
   **Then walk the "Pre-launch must-checks (20)" table** in `13-layers.md` item by
   item, and give each one a pass / finding / N/A line in the report.

## Phase 3 — Code review of the diff

Invoke **`gstack-review`** (via the Skill tool) on the current branch/diff so any
*recent* change gets a security-focused review before landing — **subject to the
same git-state check as Phase 2.** If there's no real diff to review (clean tree,
in sync with origin), say so and move on instead of invoking it.

## Phase 4 — Deep & adversarial

1. **`references/ecc/security-bounty-hunter.md`** — hunt for remotely reachable,
   genuinely exploitable issues (SSRF, auth bypass, injection, path traversal,
   auto-XSS). Discard local-only noise. This is the "would this actually get
   popped?" lens.
2. **`references/ecc/production-audit.md`** — production-readiness across the infra
   layers (5, 6, 11, 12, 13): idempotent webhooks, rollback paths, health checks,
   secrets hygiene, migration safety. Produces a ship/block score.
3. **AI apps only** — if Phase 0 found an LLM/agent feature, run
   **`references/ecc/agent-architecture-audit.md`** (prompt-injection surface, tool
   discipline, memory pollution, hidden repair loops). Skip entirely otherwise.

## Phase 4b — Localhost probes (two, free)

Reading code tells you what the app *should* do. These two ask the running app
what it *does*, and they catch the two bugs behind most "vibe-coded app leaked
everyone's data" stories. Skip the phase for an app with no backend surface (a
static page has nothing to probe) and say so in the report.

**Rules, all four, every time:**
- **`localhost` only.** Never the deployed URL, never someone else's app. If the
  dev server isn't running, start it the way the app's `CLAUDE.md` says.
- **Check the database first.** Read `.env`: if the dev server talks to the
  *production* database, skip probe B (it writes) and say why in the report.
- **Probe A only reads** (GET). Probe B may submit forms, so only against a local
  or dev database, logged in as a test account, and remove what it created.
- **One request at a time.** These are checks, not load tests.

Run them from the Bash tool. On Windows PowerShell the command is `curl.exe`,
because bare `curl` there is a different program (`Invoke-WebRequest`).

### Probe A — everything, logged out

1. **List every API route and data endpoint from the code**: the router,
   `app/api/` or `pages/api/`, serverless functions in `api/`, anything the
   front end `fetch`es. For a Vite single-page app, every *page* URL returns
   the same HTML shell with status 200, which isn't a leak. The data comes
   from the API calls, so those are what get probed.
2. **Request each one with no cookie and no `Authorization` header:**
   ```bash
   BASE=http://localhost:<port>
   for route in /api/<route-1> /api/<route-2>; do
     curl -s -o /dev/null -w "%{http_code}  $route\n" "$BASE$route"
   done
   ```
   `401`, `403`, or a redirect to the login page = pass. A `200` on a route
   that should need a login = open that one route's body
   (`curl -s "$BASE<route>" | head -c 300`): if it holds another user's data,
   that's a **Critical** at layers 2 and 4.
3. **Supabase apps: ask the user first**, because this one reads from the
   live Supabase project rather than localhost. It sends only what any
   visitor's browser can already send: the public anon key, one row.
   ```bash
   curl -s -o /dev/null -w "%{http_code}  %{size_download} bytes  <table>\n" \
     "$SUPABASE_URL/rest/v1/<table>?select=*&limit=1" -H "apikey: $SUPABASE_ANON_KEY"
   ```
   `2 bytes` (an empty `[]`) or a `401` = pass: row-level security hid the rows.
   More than 2 bytes means an anonymous visitor can read that table, a
   **Critical** at layer 8. The byte count is the point; never print the rows.

### Probe B — a single quote in every input

Any input that reaches the server (form field, search box, URL parameter)
gets a value containing `'`:

```bash
curl -s -G --data-urlencode "q='" -w "  <- %{http_code}\n" "$BASE/api/<route>"
```

For forms, send the same through the endpoint the form posts to, or type it
in the browser preview. A `500`, a database error in the response
(`syntax error`, `unterminated quoted string`, `unrecognized token`), or a
broken page = the input is pasted into a query instead of passed as a
parameter: a **Critical** at layer 2 (SQL injection). Pass = the quote comes
back as ordinary text, or a validation message. Supabase and Prisma queries
parameterize for you, so a finding there usually points at a hand-written
`sql` string or an `rpc` call.

Each finding goes into Phase 5 like any other, tagged `(localhost probe)` so
the report shows it was observed, not inferred.

## Phase 5 — Triage, root-cause & report

1. **Consolidate & dedupe** every finding from Phases 1–4 into one list. The same
   issue found by three tools is one finding.
2. **Severity-rank** (Critical / High / Medium / Low / Info). A finding is Critical
   only if it's reachable and exploitable — apply the bounty-hunter's reachability
   test, don't inflate theoretical issues.
3. For each **confirmed Critical**, invoke **`gstack-investigate`** (via the Skill
   tool) to root-cause it before proposing a fix (ponytail: fix the root, one guard
   where all callers route through — not per-symptom patches).
4. **Write `security-report.md`** into the app folder (format below). Propose fixes;
   **do not auto-apply** them unless the user says so — this skill audits, the user
   decides what lands.

### `security-report.md` format

```markdown
# Security audit — <app> — <date>

**Verdict:** <SHIP / SHIP WITH CAVEATS / BLOCK> — <one sentence>
**Production-audit score:** <n>/100 (from ECC production-audit)

## Scope
- Stack: ...
- Layers audited: <list applies> · N/A: <list>
- AI-agent audit: <ran / N/A>
- Localhost probes (4b): <ran on localhost:<port> / probe B skipped: <why> / N/A: no backend>
- Pentest of the deployed site: not part of this pass

## Findings by severity
### Critical
- [Layer N] <title> — <file:line> — <impact> — <root cause (from investigate)> — <fix>
### High
...
### Medium / Low / Info
...

## Harness (Layer 0) findings
- <.claude config issues, if any>

## Coverage by layer (1–13)
| Layer | Status | Notes |
| ... | clean / findings / N/A | ... |

## Fix plan (ordered)
1. <highest-impact fix first>
...

## Evidence checked / missing
- Checked: <files, tools, URL>
- Missing: <what would raise confidence>
```

## Notes

- **Entirely free.** Every phase here runs on free/local tooling, which is why
  full runtime pentesting of a deployed site is not part of BLD — the tools for
  it need a paid API key. Phase 4b is the free slice of it. If you run a paid
  one yourself against a target you own, fold its findings back into this
  report rather than keeping two.
- **Phase 4b's source:** @itsthatlady.dev's reel on the "wall of shame for
  vibe-coded apps" (instagram.com/reel/DXhN739m2NM): "try to access every page
  and every endpoint without being logged in" and "put a single quote in every
  input field". Checked 2026-11-08, verified on a throwaway local server with
  one open endpoint and one injectable search: probe A flagged the open route
  (200) and passed the protected one (401); probe B got a 500 with the database
  error from the injectable search and plain text from the parameterized one.
  The Supabase step is docs-based (row-level security returns an empty list to
  the anon key), not run.
- **Stay in scope.** This skill *reports*; it doesn't refactor. Proposing fixes is
  in scope; applying them (or retuning unrelated values) is not, unless asked.
- **Refresh vendored checklists** from the commit pinned in `references/ecc/SOURCES.md`.
