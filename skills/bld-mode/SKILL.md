---
name: bld-mode
description: Switch BLD's command naming between friendly mode (bld-<type>-<skill>, e.g. /bld-sprint-init) and pro mode (bld-<skill>, e.g. /bld-init). Use when the user says /bld-mode, "pro mode", "activate pro mode", "shorter commands", "turn off pro mode", "go back to the long names", or asks which naming mode they are in. Renames the skill folders, the frontmatter, and every cross-reference, then tells the user to restart.
---

# bld-mode — friendly names or short names

BLD ships every command in one of two naming schemes. Same skills, same
behaviour, different thing to type.

| Mode | Shape | Example | For |
|---|---|---|---|
| **friendly** (default) | `bld-<type>-<skill>` | `/bld-sprint-init` | Learning the set. Typing `/bld-` groups everything by type, so the list teaches you the taxonomy. |
| **pro** | `bld-<skill>` | `/bld-init` | Knowing the set. The type is confirmation you no longer need, so it just costs keystrokes. |

Neither is better. Friendly is the default because a first-timer facing 21
unfamiliar commands benefits from the grouping, and a pro can switch in one
command.

## The one thing that actually matters

**The folder name is cosmetic. The `name:` in the frontmatter is what you type.**

Renaming a folder alone changes nothing about the command, and this is the single
easiest way to leave the package in a state where the docs and the commands
disagree. The script handles both together, which is why this skill runs a script
instead of doing it by hand.

## How to run it

```bash
python skills/bld-mode/scripts/switch-mode.py status     # read-only, changes nothing
python skills/bld-mode/scripts/switch-mode.py pro
python skills/bld-mode/scripts/switch-mode.py friendly
```

Run it from the BLD root (the folder holding `skills/`). If BLD is installed
globally, that root is `~/.claude/`; if it is project-scoped, it is
`<project>/.claude/`.

`status` first, always. It prints the current mode and the full table, costs
nothing, and tells you whether there is anything to do.

The script is **idempotent** — switching to the mode you are already in is a
no-op, so a re-run after an interrupted switch is safe and is the right recovery.

## What it changes

Three things, together, because changing any one alone breaks the other two:

1. **Folder names** — `skills/bld-sprint-init/` ⇄ `skills/bld-init/`. Uses
   `git mv` when the tree is a repo, so history follows the file instead of
   showing a delete plus an add.
2. **The `name:` frontmatter** — this is the command. Nothing else is touched in
   the file.
3. **Every `/bld-*` reference in every `.md`** — skills that mention each other,
   the README, the routing table in the CLAUDE.md templates. Roughly 130 of them.
   Matching is longest-first so `/bld-sprint-init` is never mangled into
   `/bld-sprint-` plus a stale `/bld-init`.

## After switching: restart

**Skills register at startup.** Until Claude Code restarts, the old command names
are still live and the new ones do not exist. Say this every time — a user who
switches and immediately types the new command will get nothing and reasonably
conclude the skill is broken.

Then verify rather than assume: type `/bld-` and confirm the list looks like the
mode you asked for.

## Reading the table

`scripts/switch-mode.py` holds the canonical mapping in `SKILLS`. That table is
the source of truth for the whole taxonomy, not just this skill.

| Type | What it means |
|---|---|
| **sprint** | You give Claude a goal and it builds toward it |
| **optimize** | Improves an app that already exists |
| **find** | Locates a ready-made asset on an external surface |
| **runtime** | Applies to how the session runs, not to what gets built |
| **orchestrator** | Claude bosses other agents rather than writing code |
| **util** | Everything in between: not building, not optimizing |
| *(special)* | Acts on BLD itself. **Identical in both modes** — `bld-setup`, `bld-quiz`, `bld-mode` |

Specials keep one name on purpose. They are the commands you reach for when you
are confused about your setup, and a command that changes name between modes is
the worst possible thing to need at that moment.

## Adding a skill later

Add one row to `SKILLS` in the script, giving its type, friendly name and pro
name. The script picks it up on the next run. It also carries a `LEGACY` dict
mapping retired names to their row, so an older install migrates cleanly instead
of leaving orphans — add to it rather than editing `SKILLS` in place when a
command gets renamed.

If a folder is not in the table, the script says so and leaves it alone. It never
guesses, and it refuses to overwrite an existing folder rather than clobbering it.

## Pitfalls

- **Renaming folders by hand and stopping there.** The commands do not change.
  This is the failure the script exists to prevent.
- **Claiming the switch worked before a restart.** It has not, yet.
- **Running it from the wrong directory.** It resolves paths from its own
  location, but a half-copied install will still confuse it. Run `status` first.
- **Editing `name:` in one skill to "just fix this one".** That puts the repo in
  mixed mode, which `status` will report but which nothing else will warn you
  about.
- **Assuming pro mode is the better one.** It is shorter, not better. Pro's
  `/bld-app` and `/bld-react` say noticeably less than friendly's
  `/bld-optimize-app` and `/bld-optimize-react`.
