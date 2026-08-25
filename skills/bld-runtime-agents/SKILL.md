---
name: bld-runtime-agents
description: Run a task as BOSS over an external coding agent — interview to scope, plan it into small specced pieces, hand each piece to the Codex CLI (Gemini as fallback), review the result against the spec, re-run until it passes. Use when the user says /bld-runtime-agents, "delegate this", "boss mode", "have Codex build X", or hands over work that is bulky/repetitive/long-generation. Claude plans and reviews only; the executor writes the code.
---

# bld-agents — Claude is the boss, Codex is the executor

The user's request comes after `/bld-runtime-agents`. **Once this skill is invoked, Codex
writes the code — all of it.** Claude is the manager: it holds the taste, the
context, the design, and the requirements, and spends its window on those. Every
token Claude spends typing implementation is a token wasted twice — once on the
typing, once on the context it displaces.

## ⛔ "Agents" here means OTHER companies' agents — never Claude subagents

This skill exists to spend **someone else's quota**. Codex bills ChatGPT Plus;
Gemini bills its own free tier. **That asymmetry is the entire point.**

**Spawning Claude subagents is NOT delegation** — it spends the same budget the
main window does, except each subagent carries its own full context, so it costs
*more*, not less. If this skill is invoked and the work goes to `Agent`/`Workflow`
instead of the `codex` CLI, the skill has been misused.

Hard rules (full rationale + the 939k-token incident that produced them is in the
`~/.claude/CLAUDE.md` subagent-cap section):

- **Max 2–3 Claude subagents at a time, only when genuinely necessary.**
- **Never tell a subagent to invoke a heavy skill** (`impeccable`,
  `ui-ux-pro-max`, `emil-design-eng`, `gstack-spec`) — that multiplies a large
  document across every agent's context.
- **Never fan out one verifier agent per finding.** Review the list yourself
  against the files; it costs a fraction.
- Order of preference when work needs handing off: **main window → Codex →
  Gemini → (last resort) 2–3 Claude subagents.**

**Executor: Codex first.** The user's Codex is signed in as `<your-chatgpt-account>`
on a **ChatGPT Plus** plan (since 2026-07-29) — it is the default for everything.
There is no credit balance to draw down; Plus bills against a weekly window.
**Gemini is the fallback** — only when Codex is unavailable or errors out (see
Fallback below). If Codex starts refusing on quota, read the actual remaining
allowance (command in `~/.claude/CLAUDE.md`) before assuming the spec was bad.

CLI flags, model ids, and the delegation rules live in the `agent-delegation` block
in `~/.claude/CLAUDE.md` — that file is always loaded. Don't restate it; follow it.

## Step 0 — The split

The default is **Codex writes it.** Not just the bulky or repetitive work — the
technical work too: algorithms, state, data fetching, API routes, types and schemas,
hooks, handlers, components, the CSS that implements Claude's design call, tests,
fixtures, config, refactors, conversions. If the output is program code, it is
Codex's to type.

**Claude holds what a manager holds** — the things that don't survive being
compressed into a spec:

- **Requirements** — what to build, and what "done" means concretely
- **Taste and design** — the look, the feel, `design-system/MASTER.md` adherence.
  Claude decides it; Codex implements it.
- **Context** — how this fits the app, what already exists, what to reuse instead
  of rebuilding. This is the expensive thing Claude has and Codex can't be handed.
- **Architecture, data model, and the YAGNI call** on whether a piece exists at all
- **Diagnosis** — Claude root-causes the bug (that needs live context); **Codex
  writes the fix**. Don't keep the fix just because Claude found the cause.
- **Review and verification** of everything Codex produced
- **Security-sensitive code stays with Claude and is written by Claude** — auth,
  sessions, tokens, permissions, payment paths, anything handling secrets or user
  input at a trust boundary. This is the one carve-out the "Codex writes it"
  default does not override; it's a standing rule in `~/.claude/CLAUDE.md`.

Two escape hatches, both narrow — they are not general permission to take the work
back:

1. **The change is a genuine one-to-few-liner** and the sentence describing it would
   be longer than the edit. Type it, say so, move on.
2. **Two failed re-runs on the same piece** (the Step 4 ceiling).

If Claude is writing implementation for any other reason, that's drift — the split
above is the point of the skill.

### Context economy — the actual credit saving

Both budgets are spent by the same mistake: loading the same code into two heads.

- **Don't read what Codex will read.** The spec names paths; Codex opens them. Claude
  reading a file *and* pointing Codex at it pays for that file twice. Read only what's
  needed to write the spec and judge the diff.
- **Batch — every `codex exec` has a ~15k input-token floor** (measured 2026-07-29: a
  one-word reply cost 15,250 input tokens; that's system prompt + repo context, paid
  before your spec is even read). Seven micro-handoffs burn ~105k tokens of pure
  overhead. Group work that shares a spec and a mental model into **one** run, and keep
  the pieces separately checkable via the Done means checklist instead.
- **Review from `git diff`, never from whole files.**
- On failure, **append the correction to the same spec file and re-run it** rather than
  writing a fresh one.

## Step 1 — Interview (2–3 questions, then stop)

Use **AskUserQuestion** with 2–3 questions max. Ask only what changes the plan:
scope boundary, target files/app, and the one real constraint (stack, look, data
shape, "must not touch X"). Never ask what the repo can answer — look first.

Then state the scope back in **one line** and move on. No confirmation round trip.

Interview for **requirements and taste**, not implementation. How it should look,
behave, and what counts as done are Claude's to pin down, because those are what
the spec has to carry. Never ask a question whose answer is a technical choice
Codex should just make.

## Step 2 — Plan into small pieces

Break the work into ordered pieces where each one is:

- **one concern**, touching the **fewest files** possible (ideally 1–3),
- independently reviewable — Claude can tell pass/fail from the diff alone,
- ordered so each piece compiles/runs on top of the last.

**Then batch them back up before handing off.** Pieces are a *review* unit, not a
*run* unit — because of the ~15k floor, adjacent pieces sharing files and context
ship as one `codex exec` carrying one spec with several Done means checklists.
Split into separate runs only when a piece must be verified before the next can be
written, or when one is risky enough to want its own clean `git diff`.

Load the task tools once (`ToolSearch` → `select:TaskCreate,TaskUpdate,TaskList`)
and put every piece on the list. Mark `in_progress` when handed off, `completed`
only after review passes. The list is the running status the user asked for.

If a piece is small enough that specifying it costs more than writing it,
**do it yourself and say so** — delegation has overhead, don't pay it for one line.

## Step 3 — Spec each piece

Write the spec to a file in the scratchpad (not inline) — it dodges PowerShell
quote hell and becomes the artifact reviewed against later.

```markdown
# Piece <n>: <title>

## Goal
One sentence. What is true when this is done.

## Inputs
Files to read for context (exact paths). Existing patterns/utils to reuse.

## Output
Exactly what to produce — file paths, exported names, signatures, routes.

## Constraints
- Stack/style rules that apply (design-system/MASTER.md, shadcn+Tailwind, etc.)
- Reuse <helper> — do not reimplement it.
- Keep the diff minimal. No refactors, no renames, no "while I'm here" cleanups.

## Files you may touch
- path/a.tsx  (modify)
- path/b.ts   (create)
DO NOT create, modify, or delete any other file.

## Done means
A checklist Claude can verify from `git diff`. Be literal.
```

**Commit or stash first** so the next `git diff` is only the agent's work. Codex
enforces this for you — it refuses to run outside a git repo. Then hand off:

```bash
cat spec.md | codex exec -s workspace-write -C <app-folder>
# PowerShell: Get-Content spec.md -Raw | codex exec -s workspace-write -C <app-folder>
```

`-s workspace-write` lets it edit inside the workspace and nothing else.
🚩 **Never `--dangerously-bypass-approvals-and-sandbox`** — that is Codex's YOLO
switch; it drops the sandbox entirely.

Piping the spec on stdin is deliberate: Codex appends piped stdin to the prompt as
a `<stdin>` block, so the spec arrives verbatim with no shell-escaping damage.

## Step 4 — Review (this is the job)

1. `git diff --stat` — **any file outside "Files you may touch" is an instant reject.**
2. `git diff` on the changed files. Read the diff, not whole files — cheaper.
3. Walk the **Done means** checklist literally, item by item.
4. Run the real check: `tsc --noEmit`, the dev server, or the app's own test.
   The agent claiming it works is not evidence.

**Fail → concrete fixes, re-run.** Name the file, the line, and the exact change
required. Append the correction to the spec file and re-run the same command;
never send "make it better".

**Ceiling: 2 failed re-runs.** After the second, fix it yourself, note it in the
status line, and tighten the next spec. Endless re-runs cost more than the edit.

**Never accept unreviewed code.** The executor's output is Claude's output.

## Step 5 — One-line status after every loop

Exactly one line, then straight into the next piece:

```
[3/7] Auth form — Codex ✓ 1st pass · 2 files, +48/-6 · tsc clean · next: session hook
```

Include: piece number/total · name · executor · passes needed · diff size · what
verified it · next.

## Step 6 — Continue until done

Loop steps 3–5 without asking permission between pieces. Stop early only if a
piece contradicts the plan, a decision is genuinely the user's, or the same piece
fails twice for different reasons (the plan is wrong, not the executor).

When the list is clear: one short summary — what shipped, what the agent wrote vs
what Claude fixed, and anything deliberately left out.

## Fallback — when Codex can't run

Switch to Gemini for the affected piece, say so in the status line, and carry on:

```bash
cat spec.md | gemini -m gemini-3.6-flash --approval-mode auto_edit --skip-trust -p "Implement the spec provided on stdin exactly."
# PowerShell: swap `cat` for `Get-Content spec.md -Raw`
```

⚠️ Gemini's free tier is **20 requests/day** on `gemini-api-key` auth — it ran dry
after a single handoff on 2026-07-26. If Gemini also fails, **build it yourself**
rather than stalling, and tell the user which pieces Claude wrote instead.

## Notes

- Not a git repo yet? Say so and offer `git init` — Codex requires one, and the
  review step needs `git diff` anyway. `--skip-git-repo-check` exists but defeats
  the point.
- Workspace deploy discipline still applies: **local only, no push** unless the
  user says ship.
- What Claude keeps vs what Codex writes is **Step 0**. Don't re-derive it per piece
  — if it's program code and it isn't security-sensitive, it goes to Codex.
