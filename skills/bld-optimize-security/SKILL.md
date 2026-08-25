---
name: bld-optimize-security
description: The final-boss STATIC security pass for an app in this workspace. Runs a full audit across 13 layers (front-end → APIs → DB → auth → hosting → cloud → CI/CD → RLS → rate limiting → caching/CDN → scaling → logging → recovery) by combining the built-in /security-review, the gstack security skills (cso, review, careful, investigate), vendored ECC checklists (security-review, cloud-infra, production-audit, bounty-hunter, and — for AI apps — agent-architecture-audit), and an AgentShield config checklist. Use when the user says /bld-optimize-security, "secure this app", "full security audit", "harden this", or "final security pass" before shipping something serious. Static only: it reads code and config and never attacks a running target.
---

# bld-security — the final-boss security pass

One skill that runs every *static* security tool we have against one app and
returns a single triaged report. It **orchestrates** — it invokes other skills and
checklists rather than re-deriving them. Detail lives in `references/`; this file
is the conductor. Everything here is free and local. Dynamic runtime pentesting
(actually attacking a live target) is deliberately **out of scope** — the tooling
for it costs money, and BLD is free.

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

All vendored ECC content is MIT, copied verbatim (except AgentShield, stripped to
checklist-only). See `references/ecc/SOURCES.md`. Dynamic pentesting is **not**
here: this pass reads code and config, it never sends traffic at a live target.

## Before you start — scope & safety

1. **Only our own apps.** This runs adversarial tooling. Confirm the target is an
   app in this workspace (or our deployment). Never point it at anything we don't own.
2. **Read the whole flow first** (ponytail: comprehension is not the lazy part).
   Trace the app's real request paths before checking boxes.
3. **Fully local, no exfiltration.** This audit reads code and config only — it does
   not upload the repo anywhere or make external calls. (Nothing here sends traffic at a
   running target.)
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

- **Uncommitted changes exist:** do not invoke `/security-review` or
  `gstack-review` — they have nothing legitimate to diff and may try to force one.
  Skip that finding source for this pass, note in the report *"diff-review skipped:
  uncommitted changes present"*, and rely on the whole-repo checklist pass (step 3
  below) plus `gstack-cso` instead. Recent-but-uncommitted code still gets covered,
  just by the non-diff tools.
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
- Dynamic pentest: not part of this pass (static review only)

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
  dynamic runtime pentesting is not part of BLD — the tools for it need a paid
  API key. If you run one yourself against a target you own, fold its findings
  back into this report rather than keeping two.
- **Stay in scope.** This skill *reports*; it doesn't refactor. Proposing fixes is
  in scope; applying them (or retuning unrelated values) is not, unless asked.
- **Refresh vendored checklists** from the commit pinned in `references/ecc/SOURCES.md`.
