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
| 10 | **Adversarial state and re-run cases**, run for real on Windows against throwaway homes | **A pro-mode install plus a setup re-run gives 42 skill folders** - the package ships friendly names, the copy adds them beside the renamed set, nineteen commands answer to two names each and nothing errors, because both sets are valid skills. preflight warned about this only for a half-finished rename; a clean pro install reads healthy right up until the copy · `"chose": "bld"` is valid JSON and iterated into three groups named b, l and d · group names Phase 4 has no step for passed through unvalidated, the same shape as the old mcp bug · a bld-* folder in neither naming mode was invisible, which is how bld-use-strix survived package syncs · **a non-ASCII home path crashes preflight with UnicodeEncodeError on Windows** (cp1252); Latin-1 names like Zoe Muller survive and hid it. Passing: project scope end to end including a deleted project directory, re-run idempotency, the manifest contract in both directions, and Phase 8's placeholder tally - whose check.py guard was confirmed by deliberately breaking it. |
| 11 | **Narrated simulation: Windows first run, everything-plus-extras, no `bun`** - then an audit of this session's own fixes | **The simulation's finding was a hole in a fix made hours earlier**: the bun check went into Phase 4 and never reached Phase 3, so the picker still offered "Everything, extras included" - a promise of gstack - and Phase 4 then refused. Phase 3 already had that exact guard, for git. Auditing outward from there: **Phase 6 offers "gstack + impeccable" as one row and checked neither prerequisite** (pre-existing, and worse on the returning path, since the two halves fail differently) · Phase 2 tells you to confirm a fresh vercel with preflight, which can report it missing on a stale PATH · **`run.py` picked `/mnt/c/.../npx.cmd` over `/usr/bin/npx` under WSL**, the same root cause as the preflight `/mnt` fix, in another skill · and three regressions in **my own** preflight edits: the gh row replaced the auth status instead of joining it, the `/mnt` guard rejected every Linux path under `/mnt/` rather than only WSL interop, and a docstring described behaviour the code did not have. Closed by adding six mutation-tested cases to `scenarios.py`, which had never been run against any of this session's changes. |

| 12 | **Narrated simulation: Windows first run, everything recommended, deploy accepted, interrupted between groups** - the axis this table had listed as untested since run 6. Preflight output taken from real fake machines rather than imagined | **The whole continuation path was broken in the same shape as the old `mcp` bug, and nobody had walked it.** `deploy` is the one group whose install step lives outside Phase 4, so a resume printed `Still to do: deploy` directly above `Skip Phases 1-3` - sending the session to the phase it had just forbidden · **and the wording that mattered was in `preflight.py`, not SKILL.md**, which is the copy a session actually reads; fixing the table alone would have changed nothing · Phase 2 recorded a yes into `done` only *after* both browser logins, so an interruption during the slowest human step in the setup left `deploy` in neither list, dropped from the resume and reported forever as "uninstalled, or a fresh machine" · that same gap hits `claude-md-*` on any run ending before Phase 8, so the returning branch now splits **NEVER SET UP** from **MISSING NOW** · **the image-gen hook had no inventory row at all**, so a run interrupted between the skill copy and the registration reported `bld 23 of 23` + `finish up + restart` over a security control that was not running - the run-3 archetype again, from the other direction · nothing recorded the package path, though six commands interpolate it and Phase 0a's only guidance was first-run language · **and the suite could not express "a machine without gh"**: preflight's absolute-path fallback reached past the fake HOME to the host's own signed-in `gh`, silently contaminating every case that touched deploy |

| 13 | **Short walk of Phase 8 only**, following run 12's fixes to see whether the same defect existed elsewhere | **It did.** Phase 8 recorded the CLAUDE.md answer into `done` only on success, exactly as Phase 2 had with `deploy`, so an interruption between the answer and the copy lost it - and Phase 8 is the likeliest phase to be interrupted, because it is last. Same one-line fix. Both `CLAUDE.old.md` guard interruption points were walked and the guard is sound: it refuses correctly rather than overwriting the only copy of their original. Recorded because "same bug, second site" is the pattern most worth checking after any fix round. |

| 14 | **Real Linux run**, executed not reasoned. WSL2 Ubuntu 26.04, root, python3 only, Windows PATH inherited, isolated HOME | **Three bugs, and the worst one was platform-independent all along.** `preflight` counted the *package's own* `CLAUDE.md` as the user's installed workspace rules - and since `project` defaults to the current directory, which during setup IS the package folder, that fired on **every first run on every OS**, so Phase 8 saw `claude-md-workspace` already satisfied and never offered the file · **Phase 4's gstack guard used a bare `command -v bun`** while preflight filters `/mnt/` shims, so under WSL the Windows bun passes the guard, answers `--version`, and then cannot read one Linux path: `setup` dies with `Module not found` and the documented diagnostic ("look for `bun is required`") never appears. Third site of the root cause runs 11 fixed in two other files; replaced with a probe of the capability that matters · the `uv or pipx` row said "needed for /bld-runtime-tokens only", which is false on Linux, where a minimal image has no `pip` and the code-search group needs one too - and the documented fallback dead-ended, because `pipx` and `uv` are both absent there as well. **Plus a harness bug that had hidden two cases forever:** the fake machine's PATH included `/usr/bin`, which on Linux is where the real node, npm and git live, so C10 ("node and npm missing") and C11 ("git missing") could not fail there. The suite was 48/50 on Linux while reading 50/50 on Windows. **Confirmed working, and worth recording as clean:** the trailing `-y` fix from run 8 (never re-verified until now - the control still reproduces exit 0 / installed 0), preflight's `/mnt/` guard, `No module named pip` exactly as documented, the 23-skill copy, and the hook selftest under `python3`. Suite now 50/50 on both platforms. |

| 15 | **Second real Linux run**, executing the shell blocks and the remedies rather than reading them. Same WSL2 Ubuntu 26.04, isolated HOME per test | **The `EACCES` remedy does not work on the platform that produces `EACCES`.** Debian and Ubuntu's packaged npm ships a builtin config at `/usr/share/npm/npmrc` pinning `prefix=/usr/local`, which beats the user config: after the documented `npm config set prefix ~/.npm-global`, `npm config get prefix` cheerfully reports the new directory while `npm prefix -g` still answers `/usr/local` and `npm install -g` installs there anyway. A non-root user would hit `EACCES`, follow the remedy exactly, and hit it again. Measured both working alternatives - `NPM_CONFIG_PREFIX` and `--prefix` - and the env var is now in the fix, with a note to verify using `npm prefix -g` rather than `npm config get prefix`, since those two disagree in precisely this case. **Everything else executed clean and is now verified rather than assumed:** all **11 of 11** core skills install on Linux (run 8's headline finding, only ever spot-checked on one skill before), the gstack prune removes exactly the right five wrappers and spares a `bld-*` skill that mentions `skills/gstack` in prose, the impeccable block is idempotent - and running it *without* its `rm -rf` reproduced the nested `impeccable/impeccable/SKILL.md` the comment warns about, so that warning is now measured too - and the whole continuation path, deploy exception line and remembered package path included, behaves identically to Windows. |

Untested as of writing: a real macOS run rather than a reasoned walk, and the
thing that matters most - **an end-to-end run on a machine that has never had
BLD.** macOS is now deliberately served by `MANUAL-INSTALL.md` instead.

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
- **The fix round needs its own audit, every time, and run 11 is the cleanest
  proof of it.** Every finding that day came from auditing fixes made hours
  earlier, not from the skill's original text: a guard added to one phase and
  never carried to the phase that makes the promise, a root cause fixed in one
  script and left standing in a sibling, and three regressions inside the fixes
  themselves. Budget for this pass. It is not optional cleanup, it is where a
  third of the findings live.
- **A green suite you did not run is not a green suite.** `scenarios.py` passed
  26/26 after eight changes to preflight - and covered none of them, because
  every case predated the changes. Run it, then add a case per new behaviour, and
  break each new case on purpose before believing it. **Run 12 proved why that
  last step is not optional:** two of its ten new cases asserted only absences
  (`"!NOT REGISTERED"`), so deleting the entire row they were written to check
  left both of them passing. A negative-only assertion cannot tell "correct" from
  "missing". Every case needs at least one thing that must be *present*.
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
