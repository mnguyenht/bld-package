---
name: bld-quiz
description: Post-sprint learning checkpoint — size the sprint Claude just built, then quiz the student on it at matching depth; for one-line changes, skip the quiz and show the exact line and how to tweak it. Use when the user says /bld-quiz, "quiz me", "test me on that", or a sprint has just wrapped and the user wants to actually understand what was built. Covers only this sprint's changes, never pre-existing code.
---

# bld-quiz — turn the sprint just built into a learning checkpoint

The user is learning by building, and Claude just wrote code they now need to
actually understand. **Do not assume how much they already know.** Read it off
the conversation: what they have asked, what they corrected, what they clearly
already use without explanation. If the sprint touched something where the right
depth is genuinely unclear, ask once, in one line, and then stay at that level.
A quiz pitched at the wrong level teaches nobody: too low is patronising, too
high just produces wrong answers and no learning. Turn this sprint's diff into a
checkpoint sized to what changed. **Quiz only what Claude changed this sprint**
— never pre-existing code, unrelated files, or another session's work.

Keep it cheap: the diff is already in context from the sprint itself. Don't
re-read the whole app, don't spawn agents, don't re-run `git log` archaeology.

## Step 1 — Size the sprint

Judge by complexity and learning value, not raw line count:

- meaningful lines changed — excluding lockfiles, generated files, and
  formatting-only churn,
- relevant files touched,
- conceptual difficulty, and how many concepts are genuinely new to the user,
- whether architecture, data flow, state management, APIs, or the database moved.

| Tier | Looks like | Checkpoint |
|---|---|---|
| Micro | one-line fix, copy change, CSS value, rename, config value | no quiz — walkthrough below |
| Quick fix | one simple bug, ~2–10 meaningful lines, one concept | 1–2 questions |
| Small | one contained behavior, ~10–50 lines, ≤3 files | 3 questions |
| Medium | multi-file feature, ~50–200 lines, connected concepts | 4–6 questions |
| Large | major feature, architecture/API/DB change, 200+ lines | 7–10 questions, rounds of ≤3 |

## Micro changes — walkthrough, not quiz

A formal quiz on a one-liner is overhead. Instead give:

- what changed, in plain language,
- the exact `file:line`,
- a short before/after snippet when it helps,
- what that line controls,
- one safe value or small edit the user could try themselves,
- how to undo the experiment.

The point is teaching the user to manipulate the app in mini chunks — hand them
the knob, not a test about the knob.

## Step 2 — Sprint map (quiz tiers only)

Before the first question, a concise map:

- what was built or fixed,
- the important files changed,
- how information or control flows through the changed code,
- the two or three concepts most worth understanding.

## Step 3 — Ask, one at a time

- One question per message. **Wait for the answer — never reveal it first.**
- Grade each reply as **Correct / Partially correct / Not quite yet**, then
  explain in simple language and cite the relevant `file:line`.
- Wrong answer → one useful hint first, then let them retry. Give the answer
  only when asked.
- The user can always reply `skip`, `hint`, or `show me` — honor all three.
- Large sprints run in rounds of ≤3 questions with a one-line recap between
  rounds, so ten questions never lands as a wall.

## Step 4 — Wrap up

- what the user now understands,
- one concept worth revisiting,
- one small customization challenge they can attempt themselves.

## Question design

Base every question on code that actually exists in the sprint, testing
understanding over memorization. The shapes that work:

- what role does this function or component play?
- trace what happens when the user performs this action,
- why is this state, condition, or data transformation necessary?
- what would happen if this line were removed or changed?
- where would you modify the app to change a particular behavior?
- how would you diagnose a realistic failure in this code?

Mix code tracing, prediction, debugging, and customization across the set.

Never:

- generic CS trivia, or anything about Claude's hidden reasoning,
- syntax questions — unless that syntax teaches a reusable concept,
- shaming, or calling a question "easy" or "obvious".

Assume second-year college knowledge. Define framework-specific terms the first
time they appear (the global define-jargon rule applies here doubly). Keep
explanations concise, then offer a deeper pass if the user asks.
