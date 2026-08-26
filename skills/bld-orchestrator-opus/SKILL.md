---
name: bld-orchestrator-opus
description: The bld-orchestrator-fable plan → execute → judge loop with Opus in the boss seat. Use when the user says /bld-orchestrator-opus, or wants the orchestrator loop run on Opus rather than Fable. Claude never writes the code.
model: opus
---

# bld-orchestrator-opus — the same loop, Opus in the boss seat

**Read `skills/bld-orchestrator-fable/SKILL.md` and run it exactly**, from wherever BLD
is installed: `~/.claude/skills/` on a default global install, or
`<project>/.claude/skills/` if it was scoped to one project. Every
step, every table, every hard rule applies unchanged. The executor pool already
defaults to sonnet, so the workers sit below the boss without any re-tiering.
Nothing here overrides a rule there.

**Do not rely on `model: opus` to put this loop in the top seat.** Verified
2026-08-26: reaching this skill through the Skill tool mid-turn does not change the
model at all — the turn finishes on whatever the session was already running.
Whether a user-typed `/bld-orchestrator-opus` *starts* its turn on Opus has not been
tested, and even at best that covers one turn of a loop spanning several. The
reliable path is the user running `/model opus` before starting. Treat the
frontmatter as a hint, never a guarantee.
Ultracode is a session toggle the user sets, not something a skill can turn on.

The one judgment shift: `bld-executor` @ opus puts a worker in the same seat as the
boss, so the "hardest stream" escalation buys no tier gap here — only a clean, fresh
context. Reserve it for a stream that genuinely needs boss-grade reasoning on a
clean slate; everything else stays sonnet or below.
