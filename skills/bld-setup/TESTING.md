# Testing bld-setup

`/bld-setup` is the first thing a new user touches and the hardest thing to test,
because the only honest test is a machine that does not have BLD on it yet.

Simulated first-runs are the substitute. **Seven of them found thirty-seven real
bugs**, including a security control that registered and then failed silently on
every non-Windows machine, and a group offered in Phase 3 that Phase 4 never
installed. None were found by reading the skill. Reading finds typos; walking a
scenario finds the steps that cannot happen.

**Then run 8 was an actual machine, and found eight more in an afternoon** - one
severe enough to make a first install do nothing while reporting success, and one
that looked severe until the same command was measured on Windows and behaved
differently. Measure the claim on both platforms before writing down a severity.
Every one of them was invisible to simulation for the same structural reason: a
simulated machine has whatever the simulator assumes it has. Nobody imagined a
missing `bun`, because the machine doing the imagining had bun.

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
   burns output and finds nothing extra. Four of the six runs stopped early.

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
| 4 | Windows, **project-scoped install** (shared family machine) | **The verdict ignored the inventory it had just printed**, so a complete install was told to run the full flow · a truncated state file reported as "FIRST RUN … state file: none yet" while sitting on disk · **scope and project path were never recorded**, so a healthy scoped install read as `MISSING NOW: bld … Uninstalled, or a fresh machine` · Phase 4 had no project-scoped commands at all, only a sentence saying it "also works" · scoping was silently partial: core skills, plugins, gstack, impeccable and the hook all stay global · `--project` was required at Phase 0c but scope is not asked until Phase 4 |
| 5 | Ubuntu 24.04, distro Node, everything else normal | **`npm install -g` dies with `EACCES` on a distro-packaged Node**, which blocks vercel, react-doctor and react-scan, and it is the first install in the flow · `sudo apt install gh` fails on Ubuntu 22.04 LTS and on Debian, where `gh` is not in the repos at all · `bld-mcp-settings` told users `python` was the Windows spelling and then ran `python3` in every command |
| 6 | "Let me choose" branch, walked Phases 2-9 | **The `mcp` group was offered in Phase 3 and Phase 6 and had no Phase 4 install step**, so it could never leave "Still to do" · the pip install it needs was not in the manifest, breaking the skill's own "never install anything not in the printed table" rule · a resume reinstalled groups the disk already had · "Nothing else" sat in a multi-select with no precedence rule · `LIMITED` dropped git-blocked groups but still offered bundles promising them · Phase 2 recorded neither an accepted nor a declined deploy · Phase 9's own verification prints `RESUMING an unfinished setup` after a successful install and nothing said that was expected · Phase 8 counted the placeholders in one template and highlighted items from the other · Phase 7 told you to prove Codex works and only mentioned below that it refuses to run outside a git repo · the "run these through the Bash tool" note sat on the one block that survives PowerShell, not on the gstack conditional or the prune heredoc, which do not · preflight enforced a Python floor but never checked Node's version, so an ancient Node failed inside `npx` looking like a broken package · the hook's selftest printed a hardcoded tally that a later edit would silently make wrong, and its Skill-only scope was never written down |

| 7 | Windows, python.org install with "Add to PATH" unticked, so only the `py` launcher works | **Nothing.** Verified for real rather than reasoned: `py` satisfies the Phase 0b probe and the version gate, runs preflight, runs the hook selftest, and `py -m pip` covers the Phase 4 code-search step. `py.exe` lives in `C:\Windows`, which is always on PATH, so the registered hook command resolves. Recorded because a clean axis is worth knowing too - it stops the next session re-walking it. |
| 8 | **Real run, not a simulation.** Ubuntu 26.04 in WSL2, installed clean, Windows PATH inheritance disabled, non-root user, executed for real | **`npx skills add` has its own `Proceed with installation?` prompt; with no TTY, Linux reads EOF and exits 0 having installed nothing - all eleven core skills were silent no-ops. Windows was then measured on the same command and installs fine, so this is a Linux/macOS bug, not the cross-platform one it first looked like** · **gstack's `setup` is a bun script and nothing checked for bun, so `setup` exited 1 and the prune's `pruned 0` was then blamed on a stale matcher** · `bld-util-copywriting` carried the same skills-add command · `python3 -m pip` answers `No module named pip` on a minimal image, never reaching the `externally-managed-environment` error the skill said to expect · hook registration assumed `settings.json` existed because plugins wrote it · a CLI installed into a new PATH directory reports `[--]` until the shell restarts, which Phase 9 warns about for Claude Code but not for PATH · preflight trusted `/mnt/c/...` Windows shims found through the WSL PATH · `uv or pipx` was the only prerequisite naming no source |
| 9 | **Real run on Windows**, the actual target platform. HOME/USERPROFILE/CLAUDE_CONFIG_DIR redirected to a throwaway directory, real npx and real `claude plugin` against it | **The plugin phase, never cold-tested before, passes end to end**: three marketplaces added, three plugins installed, three enabled · 11 of 11 core skills and 23 of 23 bld skills install, hook selftest passes · **two severities from run 8 were wrong and got corrected here** - the skills-add prompt does not bite on Windows, and the ui-ux-pro-max long-path failure was the test rig's own 262-character path, not a user's 141 · `gh` resolved through its default-path fallback reported a plain "signed in" while a bare `gh` would still fail, so the row now says which way it was found. Isolation verified throughout: real skills count and both config hashes unchanged. |

Untested as of writing: a real Linux or macOS run rather than a reasoned walk,
interruption between groups, and the thing that matters most - **an end-to-end
run on a machine that has never had BLD.**

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

Run the scenario suite first. It builds a fake machine under a temp directory for
each case, runs preflight against it, and checks the verdict, so it covers the
states that are tedious to reach by hand: a corrupt state file, a scoped install
whose project was deleted, a naming switch that stopped partway. Every case in it
is a bug that was real once.

```bash
python skills/bld-setup/scripts/scenarios.py        # all of them
python skills/bld-setup/scripts/scenarios.py -v C07 # one, with full output
```

It is a regression net, not a walk: it can only fail on behaviour someone already
thought to encode. **A green suite is not evidence the skill is fine** - runs 4
to 6 found twenty bugs on a suite that was passing.

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

- **A simulation is not a run - and run 8 proved the gap is not small.** Seven
  simulations found nothing that a single real cold machine then found eight of.
  Simulate to explore an axis cheaply; run it for real before believing it works.
- **One platform is not a platform.** Two of run 8's findings were written up at
  the wrong severity because they were only ever measured on Linux. Run 9 put the
  same commands on Windows and both changed: one bug does not occur there at all,
  and the other was an artefact of the test rig's own directory depth. Measure a
  claim on the platform your users are on before you write down how bad it is.
- **Redirecting HOME is most of a cold machine, and it is nearly free.** Run 9
  needed no VM: HOME, USERPROFILE and CLAUDE_CONFIG_DIR pointed at a throwaway
  directory gave a genuine first-run home on Windows, including a working
  `claude plugin` phase that WSL could not run at all. Verify isolation while you
  do it - hash the real config before and after - and keep the fake path SHORT,
  because a deep one manufactures Windows path-length failures that no real user
  would see.
- **What is still untested:** the OS-level installers themselves (nothing here
  ever ran the node.js or gh installer), and a machine whose Claude Code has
  never been authenticated.
- **You cannot simulate ignorance you do not have.** An OS nobody in the loop uses
  will not get an honest scenario.
- **Returns have not diminished yet.** Six runs, thirty bugs, and run six found
  a group that was offered to users and never installed. Do not treat "we did a
  few" as done.
- **The fix round needs its own audit, every time.** Runs 4-6 introduced ten
  fresh defects while fixing others. A representative few: a "directory does not
  exist" warning that fired for `--project` but not for the path remembered from
  the state file; a valid-but-empty state file described as a missing one; an
  assertion in SKILL.md pinning an output string the hook had stopped printing;
  two new install notes scoped to "on Linux" when Homebrew Python and the macOS
  Node `.pkg` hit exactly the same wall; a new script that shipped to users'
  machines without being added to the manifest, which is the one promise this
  skill actually makes. Nine of the ten were caught by re-reading the diff as an
  adversary or by walking a second OS. **One was caught by the tests.** Write the
  tests anyway, but do not expect them to find this class.
- **The quiet mode can drift into reading rather than walking.** If you have not
  asked "would this command run" at least once per phase, you are reviewing, not
  testing.
