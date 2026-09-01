# Testing bld-setup

`/bld-setup` is the first thing a new user touches and the hardest thing to test,
because the only honest test is a machine that does not have BLD on it yet.

Simulated first-runs are the substitute. **Three of them found nine real bugs**,
including a security control that registered and then failed silently on every
non-Windows machine. None of the nine were found by reading the skill. Reading
finds typos; walking a scenario finds the steps that cannot happen.

This file is the method. It generalises to any skill, but `/bld-setup` is where
it earns its keep.

---

## Two modes

### Quiet audit — the default

Walk a scenario against the skill in your head and **report only what you found.**
No transcript, no role-play, no "> user says yes". A short findings list and a
recommendation.

This is what to do when nobody asked for a show. It is most of the value at a
fraction of the output.

### Narrated simulation — only when asked

Role-play the whole session as a transcript: what Claude says, what the machine
prints, what the user answers. Slower and much longer, but it exposes things a
quiet audit cannot:

- **Tone and pacing.** Whether the skill's voice rules actually produce readable
  output, or a lecture.
- **Ordering.** Whether a question arrives before the information needed to
  answer it.
- **How much the user has to hold in their head** at any one point.

Run this mode when the user says *simulate*, *run a simulation*, *act like a new
user*, *walk me through it*, or *let's test the setup*. Otherwise stay quiet.

---

## How to run one

1. **Pick a machine** from the matrix below. Make it awkward in **one specific
   way**, not five. One variable per run keeps the finding attributable.
2. **Read the skill top to bottom as if executing it**, in order, no skipping.
3. At every **command**, ask: *would this actually run on this machine?* Wrong
   interpreter name, missing binary, wrong shell, wrong path separator.
4. At every **instruction to Claude**, ask: *can Claude actually do this?* Check
   tool limits, and check for things Claude must never do (enter credentials,
   run an interactive login, launch a terminal-dialog slash command).
5. **Stop as soon as you have findings.** Running to completion for its own sake
   burns output and finds nothing extra. Two of the three runs stopped early.

---

## The rule that makes this work

> **Be an honest adversary, not a helpful assistant.**

The failure mode is *rescuing the skill*. In simulation 3 the skill only
documented `winget install GitHub.cli`, and the in-character Claude wrote
`brew install gh` because it was obvious on macOS. That smoothed over a real gap
and nearly buried it.

**When you improvise past something the skill did not cover, the improvisation
IS the finding.** Write it down. If you had to be clever, a weaker session will
not be, and the user gets the failure.

Two more habits that matter:

- **Let failures fail.** If a command would error, print the error. Do not narrate
  around it.
- **Do not grade on intent.** "The skill obviously means python3 here" is exactly
  the bug. Follow it literally.

---

## The scenario matrix

Vary one axis per run.

| Axis | Values worth testing |
|---|---|
| **OS** | Windows, macOS, Linux |
| **Python** | absent · `python3` only (macOS default) · `py` launcher only |
| **git** | present · absent (they downloaded a ZIP) |
| **Node** | present (Claude Code implies it) · very old version |
| **Prior state** | first run · interrupted mid-install · completed · corrupt or half-written state file |
| **Install scope** | global · project-scoped · both at once |
| **Deploy** | wanted · declined · installed but **not** signed in |
| **Their choice** | everything recommended · essentials · let-me-choose · everything + extras |
| **Interruption point** | at a question · between groups · mid-group · after install, before restart |
| **Shell** | Git Bash · PowerShell · zsh |

Pairs that have historically hidden bugs: **macOS + hooks**, **ZIP download +
git-gated features**, **crash mid-group + resume**, **project scope + preflight**.

---

## Already run (pick new ground)

| # | Machine | Found |
|---|---|---|
| 1 | Fresh Windows, nothing installed | No prerequisite check at all · `gh` needs a login the skill never mentions · "global or project?" is unanswerable for someone with no project · `uv` appeared in the survey but nowhere in the install steps |
| 2 | Windows, no Python, no git, ZIP download | **Prerequisite checker written in Python** could not report that Python was missing · `git` hard-blocked everything when it only gates three features · **picker specified 8 options into a 4-option tool** · `<BLD>` placeholder shown to a user who cannot substitute it · `cp -r` breaks in PowerShell |
| 3 | macOS (`python3` only), git present, crash mid-install | **Hook registration hardcodes `python`, so the image-gen block registers and fails silently on every fire** · `gh` install instructions were Windows-only · other skills hardcode `python` too · resume trusted the state file without checking disk |

Untested as of writing: Linux, `py` launcher, corrupt state file, project-scoped
install, declined-deploy path, "let me choose" branch, interruption at a question.

---

## What counts as a finding

Ranked by whether it would hurt a real person:

1. **Strands the user.** A step that cannot complete, with no path forward.
2. **Silently wrong.** Something registers or reports success while not working.
   The macOS hook bug is the archetype: a security control that is not running
   and never says so.
3. **Impossible instruction.** The skill tells Claude to do something the tools
   do not allow. Check limits rather than assuming.
4. **Platform-locked.** Works only on the OS the author happened to use.
5. **Voice.** Lecturing, unexplained jargon, a question asked before the
   information needed to answer it.

**Not findings:** style preferences, things you would word differently, or
hypotheticals you did not actually walk into.

---

## After the test

1. **Fix**, smallest change that removes the cause.
2. **Re-verify mechanically** (below).
3. **Re-audit the fixes.** A later round found **seven defects introduced by that
   same round's own fixes.** Changed code is the most suspect code in the repo.
4. **Add the scenario to the table above** so the next session picks new ground.

### The mechanical checks

Not a substitute for a scenario walk. These catch regressions, not design flaws.

```bash
cd <bld-package>

# every script still parses and runs
python -c "import ast,io;[ast.parse(io.open(p,encoding='utf-8').read()) for p in \
  ['skills/bld-setup/scripts/preflight.py', \
   'skills/bld-professional-settings/scripts/switch-mode.py', \
   'skills/bld-runtime-activate-mcps/run.py']];print('python parses')"
python skills/bld-setup/scripts/preflight.py >/dev/null && echo "preflight exit 0"
node --check skills/bld-optimize-app/scripts/lh-report.mjs && echo "lh-report ok"
python hooks/block-image-skills.py --selftest

# every skill folder matches its declared name
for d in skills/*/; do d=${d%/}; f=$(basename $d)
  n=$(grep -m1 '^name:' $d/SKILL.md | sed 's/^name: *//')
  [ "$f" = "$n" ] || echo "MISMATCH $f != $n"
done

# the naming switch is lossless in both directions
snap () { find skills templates README.md CLAUDE.md -type f | sort | xargs md5sum | md5sum; }
a=$(snap)
python skills/bld-professional-settings/scripts/switch-mode.py on  >/dev/null
python skills/bld-professional-settings/scripts/switch-mode.py off >/dev/null
[ "$a" = "$(snap)" ] && echo LOSSLESS || echo "BUG: round trip changed files"
```

---

## Known limits of this method

- **A simulation is not a run.** `/bld-setup` has still never been executed end to
  end by a real user on a real machine. Everything here is a model of one.
- **You cannot simulate ignorance you do not have.** An OS nobody in the loop uses
  will not get an honest scenario.
- **Returns have not diminished yet.** Three runs, nine bugs, and run three found
  the worst one. Do not treat "we did a few" as done.
- **The quiet mode can drift into reading rather than walking.** If you have not
  asked "would this command run" at least once per phase, you are reviewing, not
  testing.
