---
name: bld-orchestrator-fable
description: Boss mode over Claude subagents — turn a brain-dump into a plan → execute → judge loop. Claude scopes, specs, fans out bld-executor workers in parallel, judges their reports as a skeptic, and re-specs until the work meets the bar. Use when the user says /bld-orchestrator-fable, drops a messy multi-item to-do list, or wants several independent pieces built at once. Claude never writes the code.
model: fable
---

# bld-orchestrator-fable — Claude is the head, the executors are the hands

The user's brain-dump comes after `/bld-orchestrator-fable`. **Claude never writes the
code.** Claude gathers context, writes the specs, fans out workers, and judges what
comes back. An edit to a source file means a workstream escaped — stop and hand it to
an executor.

The reasoning is a thin slice of the work; the grinding is the thick slice. This skill
keeps the reasoning in one seat and pushes the grinding out to workers running at once.

**Do not rely on `model: fable` to put this loop in the top seat.** Verified
2026-08-26: reaching this skill through the Skill tool mid-turn does not change the
model at all — the turn finishes on whatever the session was already running.
Whether a user-typed `/bld-orchestrator-fable` *starts* its turn on Fable has not been
tested, and even at best that covers one turn of a loop spanning several. The
reliable path is the user running `/model fable` before starting. Treat the
frontmatter as a hint, never a guarantee.

## The executor pool

| Executor | Call | Good for |
|---|---|---|
| `bld-executor` @ sonnet | `Agent(subagent_type: 'bld-executor')` | the default — build work that needs real verification |
| `bld-executor` @ opus | same, plus `model: 'opus'` | boss's explicit call only — the one stream where a weak first pass costs a full re-spec |
| `bld-executor` @ haiku | same, plus `model: 'haiku'` | mechanical, judgeable from the diff alone |
| Codex | `codex exec` — locked, see Step 4 | bulky, repetitive, low-judgment, long generation |
| Gemini | fallback only, 20 req/day | Codex down |

`bld-executor` lives in `.claude/agents/bld-executor.md`. It already carries the handoff
format and the workspace hard stops — don't restate either in a spec.

## Step 1 — Scope

Restate the brain-dump in **one or two lines** so a misread costs one sentence instead
of four workers. Split it into **independent workstreams**: one concern, fewest files,
finishable by one worker and judgeable on its own.

Batch every question into **ONE upfront round** with `AskUserQuestion` (2–4 questions),
then move. Ask only what changes the plan — never what the repo already answers. If the
plan holds a bulky low-judgment stream and external executors are locked, the unlock
question belongs in this same round (Step 4).

## Step 2 — Gather context, in parallel

Spawn one `Explore` agent per area **in a single message** so they run at once. Each
returns a tight report: relevant files, conventions already in use, gotchas. Doing the
broad reading directly is what rots the boss context, and clean context is the whole
instrument for judging later.

Skip this step only for workstreams whose files are already read this session.

## Step 3 — Spec each workstream

One spec per workstream, using the template in `bld-runtime-agents/SKILL.md`
(under `~/.claude/skills/` on a global install, `<project>/.claude/skills/` if scoped)
(Step 3) — same headings, same discipline. A spec that survives judging:

- names the **exact files** the worker may touch, and forbids every other file,
- states "done" as a checklist gradeable without asking a follow-up question,
- names **how to verify** — the real command, the real output to observe,
- stays narrow. No refactors, no renames, no "while I'm here".

Specs longer than a screen go to a scratchpad file; hand the worker the path.

⚠️ **Two workstreams touching the same file run one at a time.** Parallel edits to one
file produce a collision the boss has to unpick by hand, which costs more than the
serial run saved.

## Step 4 — Route, then execute

Route by what the workstream actually demands, not by its size:

| The workstream is | Send it to |
|---|---|
| a judgment call, security-touching, or something the boss would re-derive to review | keep it — tighten the spec or escalate |
| the single hardest build stream, where a weak first pass costs a full re-spec | `bld-executor` @ opus — explicit `model: 'opus'`, at most one per plan |
| ordinary build work — a screen, a hook, a route, a fix | `bld-executor` @ sonnet |
| mechanical and diff-checkable — a rename across files, deleting dead files, moving a util | `bld-executor` @ haiku |
| bulky, repetitive, low-judgment, long generation — fixtures, boilerplate, per-file conversions, long copy | Codex, once unlocked |

Architecture and design decisions, the YAGNI call on whether code should exist at all,
and security-sensitive code never leave Claude at any size — they are the reason the
boss seat exists.

⚠️ **Every worker token draws down the same subscription window the boss runs on.**
The fan-out spends more total tokens than building inline — it buys speed, clean boss
context, and judged quality, never savings. So weigh each stream and pick the lightest
executor that can still pass Step 5; a stream haiku can pass never goes to sonnet.
Codex is the one true saving: it spends the user's ChatGPT Plus quota
(`<your-chatgpt-account>`, weekly window), not the Claude window, which makes it the
cheapest seat for any stream it fits — and the reason the unlock question belongs in
the Step 1 round whenever the plan has eligible streams. It is not free, though:
each `codex exec` carries a ~15k input-token floor, so give it whole streams rather
than a scatter of small ones.

**Spawn every independent Claude executor in a single message** so they run in parallel,
each with its full spec. Serialize only on real dependencies.

### Unlocking Codex / Gemini

External executors are off by default, because their review path needs a clean `git
diff` that parallel Claude workers destroy. They turn on when either holds:

- `/bld-runtime-agents` has been invoked this session (its instructions are in context), or
- the user names Codex or Gemini in the brain-dump or in the Step 1 question round.

Once unlocked, the CLI flags and delegation rules live in the `agent-delegation` block
in `~/.claude/CLAUDE.md` and in `bld-agents` — follow them, don't restate them. Three
rules apply only to running Codex *inside this loop*:

```bash
git -C <app> status --short           # must be clean, or the review diff is unreadable
cat <spec>.md | codex exec -s workspace-write -C <app>
# PowerShell: Get-Content <spec>.md -Raw | codex exec -s workspace-write -C <app>
git -C <app> diff --stat              # any file outside the spec list = instant reject
```

1. ⚠️ **A Codex stream runs alone — drain the Claude workers first.** Reviewing Codex
   means reading `git diff` against a clean tree, and every in-flight Claude executor is
   writing into that same tree. Never `git stash` to force it clean while workers are
   out: the stash swallows their unfinished edits and they report success on work that
   no longer exists. Accept the Claude streams, then run Codex streams one at a time.
2. ⚠️ **`codex exec` is not on the permission allowlist** — it prompts. Before the first
   run, tell the user in plain language what it does and that `-s workspace-write`
   confines its edits to that folder.
3. **Not a git repo?** Codex refuses to start. Say so and offer `git init` before
   planning any Codex stream at all.

## Step 5 — Judge (this is the job)

Read every report as a skeptic, not to rubber-stamp it.

- **Weight "How I verified" hardest.** A report claiming "should work", or showing no
  real command output, is an automatic revise — the diff doesn't need reading yet.
- **A file outside the spec's list is an instant reject**, however good the change is.
- Walk the "done means" checklist literally, item by item.
- Act on the worker's own flags. A worker surfacing a problem is the loop working.
- Re-run the cheap real check directly: `npx tsc --noEmit`, the app's own test.
- **The boss owns the browser.** Workers can't touch the preview pane — there is one
  pane and several of them. For a UI stream, verify it in the preview after accepting
  the code. That is judging, not building.

Verdict per workstream: **accept** (met the spec, verified for real), **revise**
(re-spawn with a corrected spec naming exactly what fell short — never "make it
better"), or **escalate** (the spec was wrong, not the work — stop and ask the user).

Loop Steps 4–5 until every workstream is accepted or escalated.

⚠️ **Ceiling: 2 revise loops per workstream.** After the second, either fix it directly
— the one sanctioned exception to never implementing — or escalate, and say out loud
which. A third re-spec costs more than the edit and usually means the plan is wrong.

## Step 6 — Synthesize

Terse, no victory lap: what shipped and the observation that verified it, what was
rejected and why, what is escalated, and anything a worker flagged that Claude chose to
leave alone. If nothing was actually verified, say that plainly.

## Hard rules

- **Claude never implements**, except the 2-strike exception above, declared out loud.
- **Parallel by default.** Independent context agents in one message, independent Claude
  executors in one message. Serialize on real dependencies and on every Codex stream.
- **Judge honestly.** A real problem surfaced beats a clean report that buries one.
- **Escalate, never silently redesign.** Under-specified or wrong → stop and ask.

## Notes

- Workspace deploy discipline holds: this loop is **local only**. No commit, no push, no
  Vercel unless the user says ship — then `/bld-util-deploy`.
- Keep the dev server up for the session and end the final response with the localhost
  link. Never open a browser for the user.
- Past ~6 genuinely independent workstreams, one message of parallel agents stops being
  the right harness — the `Workflow` tool is, and it keeps the same judging bar.
- On Opus, `/bld-orchestrator-opus` runs this same loop with Opus in the boss seat;
  the executor pool is unchanged.
