---
name: bld-orchestrator-fable
description: 'of: Boss mode over Claude subagents. Plan a brain-dump, fan out bld-executor workers in parallel, judge their work. Use for a messy multi-item to-do list or several independent pieces to build at once.'
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

Every Claude row also takes an `effort` (low → max) and every Codex run a model and a
reasoning effort. The ladder in Step 4 sets both per workstream.

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

One spec per workstream, using the template in `skills/bld-runtime-agents/SKILL.md`
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

Route by what the workstream actually demands, not by its size. **The boss is the
router:** for every workstream it picks a rung, an effort and a verify depth, and writes
all three at the top of that spec. Rules, not an extra model call: the boss has already
read the stream, so a separate routing call costs more than it saves.

### The ladder — cheapest rung that can pass, effort before model

One ladder per quota. Climb **effort before model**: a cheaper model thinking longer
often passes where the bigger model would have been bought, and the bigger model is the
expensive step.

| Rung | Claude window — `bld-executor` | ChatGPT quota — Codex, once unlocked |
|---|---|---|
| 1 | `model: 'haiku'`, `effort: 'low'` | cheapest listed model, `low` |
| 2 | `model: 'sonnet'`, `effort: 'medium'` | middle model, `medium` |
| 3 | `model: 'sonnet'`, `effort: 'high'` | middle model, `xhigh` |
| 4 | `model: 'opus'`, `effort: 'high'` — at most one per plan | top model, `high` |

**This skill explicitly asks for a per-spawn effort:** pass `effort` on every executor
spawn, from the rung. Codex takes both per run:
`codex exec -m <model> -c model_reasoning_effort=<level> ...`. Codex model ids change
with every release, so read them instead of hard-coding them: the entries marked
`"visibility": "list"` in `~/.codex/models_cache.json` are what the installed CLI
accepts, and OpenAI's pricing page orders them. A model missing from that file needs a
CLI upgrade first.

### Pick the starting rung and the verify depth

| The workstream is | Starts at |
|---|---|
| a judgment call, security-touching, or something the boss would re-derive to review | off the ladder — keep it, tighten the spec or escalate |
| mechanical and diff-checkable — a rename across files, deleting dead files, moving a util | rung 1 |
| ordinary build work — a screen, a hook, a route, a fix | rung 2 |
| the single hardest build stream, where a weak first pass costs a full re-spec | rung 3, or rung 4 on the boss's explicit call |
| bulky, repetitive, low-judgment, long generation — fixtures, boilerplate, per-file conversions, long copy | Codex ladder, rung 1 or 2 |

A tight spec is what lets a stream start low: every question the worker has to guess at
is effort it burns, or a rung it climbs.

**Verify depth scales with risk:**

- **light** — the diff stays inside the spec's file list, and the spec's verify command
  passes when the boss re-runs it. For rung-1 mechanical streams.
- **full** — all of Step 5. Mandatory for anything a user sees, logic touching money,
  auth or stored data, a file another stream also needs, and any stream on its second
  attempt.

Why a ladder: on a simulated six-task coding workload, routing model and effort per task
and verifying by risk cost 36× less per solved task than sending everything to the top
model at max effort. The hard task never reached the top model; the middle one thinking
longer passed it. (Creator's figures, "AI Levels" reel by @donimas, Oct 2026; a
simulation, not a benchmark. The price ratios behind it match OpenAI's pricing page,
checked 2026-10-18.) On a subscription the saving is quota: every rung not climbed is
window left.

### The advisor — optional, beside the ladder, not on it

Claude Code's advisor lets an agent consult a stronger model at decision points: before
committing to an approach, when an error keeps recurring, before declaring done. The
advisor reads the agent's whole transcript and returns guidance; it never edits.
Subagents inherit the session's advisor. An advisor that ranks below the main model is
not attached to the main model, but subagents it outranks may still use it — so with a
Fable boss, turning on an Opus advisor gives every Sonnet and Haiku worker Opus at its
decision points while the boss runs without one. With an Opus boss, the boss gets it
too: Opus reviewing Opus, at Opus cost. Turn it on per orchestrator session, not as a
global default, since a saved default reaches every session.

- **It is not a rung.** Claude decides when to call it and nothing forces a call, so a
  failed check still climbs the ladder.
- **When it is on, every spec says:** "if the same failure happens twice, consult the
  advisor before a third attempt." Asking in instructions is the only lever there is.
- **It costs per call:** each call re-reads the worker's full transcript at the
  advisor's rate, uncached, against the same plan limits.
- **It can be off without saying so.** It needs the Anthropic API directly (or a gateway
  that forwards requests intact) and feature-flag fetching, which telemetry-disabling
  variables turn off. If no `Advising` line ever shows up, check those two first.

(Advisor behaviour checked 2026-10-18 against code.claude.com/docs/en/advisor.)

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

Judge at the depth the spec's header names: light or full (Step 4).

Verdict per workstream: **accept** (met the spec, verified for real), **revise**
(re-spawn with a corrected spec naming exactly what fell short — never "make it
better"), or **escalate** (the spec was wrong, not the work — stop and ask the user).

**A revise goes one rung up the ladder** — effort first, then model. The exception is a
report showing the spec itself was unclear: fix the spec and stay on the rung, since a
bigger model on a muddy spec only fails at a higher price. Crossing ladders is allowed:
a Codex stream that fails twice can go to `bld-executor` at rung 3.

Loop Steps 4–5 until every workstream is accepted or escalated.

⚠️ **Ceiling: 2 revise loops per workstream.** After the second, either fix it directly
— the one sanctioned exception to never implementing — or escalate, and say out loud
which. A third re-spec costs more than the edit and usually means the plan is wrong.

## Step 6 — Synthesize

Terse, no victory lap: what shipped and the observation that verified it, what was
rejected and why, what is escalated, and anything a worker flagged that Claude chose to
leave alone. If nothing was actually verified, say that plainly.

End with one routing line per workstream: `kind · started at · passed at · revises`
(`ordinary build · sonnet/medium · sonnet/high · 1`), plus `· advisor` when the worker
consulted one. That log is the router's memory:
a later stream of the same kind **in this session** starts at the rung that passed, not
the one that failed. Nothing carries across sessions yet.

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
