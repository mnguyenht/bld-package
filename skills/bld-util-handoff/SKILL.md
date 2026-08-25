---
name: bld-util-handoff
description: Write a handoff.md snapshot of the current session (goal, state, active files, changes, failed attempts, next steps) so work can continue in a fresh session before context rot sets in. Use when the user says /bld-util-handoff, "hand off", "write a handoff", "save state and start fresh", or wants to switch sessions without losing context.
---

# handoff — snapshot the session for a clean restart

The user switches to a new session before the current context gets long and
degraded ("context rot"). This skill captures everything the next session needs
into `handoff.md`, so a cold-start Claude can pick up exactly where this one left off.

## Step 1 — Write `handoff.md` at the project root

Fill all six sections from the ACTUAL session — real file paths, real decisions,
no placeholders. Be concrete and specific; the next session has zero memory of
this conversation and can only see this file.

```markdown
# Handoff — <short task name> (<today's date>)

## 1. Goal
What we're ultimately trying to accomplish. The end state that means "done."

## 2. Current state
Where things stand right now. What works, what's half-done, what's blocked.

## 3. Active files
Files being worked on, with absolute or repo-relative paths and a one-line note
on each ("src/App.tsx — added the nav, still needs mobile breakpoint").

## 4. Changes made
Concrete edits/commands already done this session, so they aren't redone.

## 5. Failed attempts
Dead ends and what went wrong — so the next session does NOT repeat them.
This section is the whole point; be honest and specific.

## 6. Next steps
The concrete next actions, ordered. First line = the very next thing to do.
```

Keep it tight but complete — enough that someone with no memory of this chat
could continue. Prefer specifics (function names, error messages, exact commands)
over vague summaries.

## Step 2 — Hand the user the restart steps

After writing the file, tell the user (do NOT try to run these yourself — you can't):

1. Run **`/clear`** to wipe context.
2. In the fresh session, paste: **`read handoff.md and continue where we left off`**

That's it — the new session reads the file and resumes.

## Notes

- `handoff.md` is ephemeral session scratch. If the repo is tracked, add it to
  `.gitignore` (don't commit it) unless the user says otherwise.
- Overwrite any existing `handoff.md` — it's a live snapshot, not a log.
- When a session STARTS by being told to read `handoff.md`: read it, briefly
  confirm the goal and next step back to the user, then continue the work.
