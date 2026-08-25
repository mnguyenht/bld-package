---
name: bld-orchestrator-opus
description: The bld-orchestrator-fable plan → execute → judge loop with Opus in the boss seat. Use when the user says /bld-orchestrator-opus, or wants the orchestrator loop run on Opus rather than Fable. Claude never writes the code.
model: opus
---

# bld-orchestrator-opus — the same loop, Opus in the boss seat

**Read `.claude/skills/bld-orchestrator-fable/SKILL.md` and run it exactly.** Every
step, every table, every hard rule applies unchanged. The executor pool already
defaults to sonnet, so the workers sit below the boss without any re-tiering.
Nothing here overrides a rule there.

`model: opus` pins the boss seat for the invoking turn only — the session model
resumes on the next prompt, and this loop spans several turns. For a loop that stays
on Opus the whole way, the user runs `/model opus` before starting. Ultracode is a
session toggle the user sets, not something a skill can turn on.

The one judgment shift: `bld-executor` @ opus puts a worker in the same seat as the
boss, so the "hardest stream" escalation buys no tier gap here — only a clean, fresh
context. Reserve it for a stream that genuinely needs boss-grade reasoning on a
clean slate; everything else stays sonnet or below.
