---
name: bld-setup
description: Install BLD or add more of it. Checks prerequisites, lists every tool with its source, installs only what the user picks, resumes if interrupted. Use for "set up BLD", "install the BLD toolkit", "what else can I install".
---

# bld-setup

Installs other people's software onto someone's machine. That is a trust
transaction, so the order is fixed:

> **Welcome them → check the machine → show the list → get a yes → install →
> record it.**

**Never install anything that was not in the printed table.** If you reach for a
package mid-install that the manifest does not name, stop and ask.

## Say this before anything else

> **Worth running this one on Opus 5 with extra reasoning effort or higher.**
>
> Setup makes decisions that are irritating to undo. It merges into config you
> already have instead of overwriting it, works out what is already installed,
> and reads a trust manifest before touching your machine. Lighter models can
> run it, they are just likelier to skip a step or replace a file you wanted
> kept.

One short note, then carry on. Do not refuse to run on a smaller model.

## How to talk during this skill

Most people running this are new to Claude Code. **Explain what you are doing.**
Just do it briefly, and format it so it can be scanned.

- **A line or two before an action, then act.** Say what you are running and why
  it matters to them. That is context, not padding, and skipping it leaves a
  beginner watching commands they do not understand.
- **Explain a command the first time it appears**, then stop re-explaining it.
- **Format for scanning.** Tables, short bullets, bold on the words carrying the
  meaning. A dense paragraph is where a beginner stops reading.
- **Say the trade-off, not the reassurance.** "Adds a command you can run from
  anywhere" tells them more than "this is completely safe."
- **Name a risk once, clearly, then move on.** Repeating a caveat three times
  reads as nervousness, not care.
- **Never ask a question without printing its table first.** Every choice in this
  skill has a table that says what each option is: the commands in Phase 2, the
  tools in Phase 3, the extensions in Phase 7, the rule files in Phase 8. Print
  it, then ask. "Do you want react-doctor?" asked of someone who has never seen
  the word is not consent, it is a coin toss, and the answer they give is not the
  one they would have given informed.

## Phase 0 — welcome

**Skip this phase entirely if `~/.claude/.bld-setup.json` exists, or if
`~/.claude/skills` already holds any `bld-*` folder.** One `ls` covers both. The
state file alone is not enough: a hand install or a deleted state file is still
not a first run, and those are exactly the cases where the file cannot answer. Someone resuming or coming back does not need the welcome again, and a
returning user re-reading a thank-you note for a package they installed last week
reads as a script, not a greeting.

### The note, printed exactly as written

**Print it verbatim, quotation marks included.** The quotes are what make it read
as the author's note to the person who just downloaded this, rather than as
something Claude wrote. Do not paraphrase it, shorten it, translate it, add a
greeting above it or a comment under it.

> "Thank you for downloading bld-package! I created this agent skill set as a byproduct after months of obsessing over Claude Code and learning as much as I could about the full development process, whilst testing hundreds of tools to help me along the way.
>
> Bld-package is a compilation of my own learnings + UI/UX experience, combined with skills and tools from others' learnings as well. Please be sure to check out the tools and skills that makes bld-package what it is! I hope you'll be able to find much value from this skill set."

### Then ask what kind of builder they are

One `AskUserQuestion`, single select. Print the table, then ask:

| Option | Who it is |
|---|---|
| **Just starting** | First apps. Learning the tools while building with them. |
| **Hobbyist or student** | Has shipped a few things. Comfortable with the basics, still meets a lot of new terms. |
| **Working developer** | Builds software regularly and knows the stack. |
| **Senior engineer** | Deep experience. Wants the trade-off, not the tutorial. |

**This answer sets how much gets explained for the rest of the run**, which is
the one lever that changes every later message: a senior engineer does not need
`npm install -g` explained, and someone just starting needs exactly that. It does
not change what gets installed. Nothing here is gated on the answer.

Record it as `builder` in the state file (Phase 5) on the first write. Phase 8
reuses it for the "who I'm working with" blank in the global rule file, which is
the same question asked twice if you do not.

## Phase 1 — preflight (always first, even on a resume)

### 1a. Find the package, and never show a placeholder

Locate the folder holding `skills/` and `README.md`. Usually the current
directory, or the one they just cloned or unzipped. **Resolve it to a real
absolute path and use that in every command you show them.** A beginner cannot
substitute `<BLD>` and should never be asked to.

**On a resume, read it back rather than guessing.** Phase 5 records it as
`package` in the state file and preflight prints it as `package:`. A later
session did not just clone anything and may be running from a completely
different directory, so "the current directory" is first-run advice only - and
six commands across Phases 1c, 4, 8 and 9 need this path. If the line is absent
or points somewhere that no longer exists, ask them where they put it, then
write the corrected path back to the state file.

### 1b. Confirm Python exists BEFORE running a Python script

`preflight.py` is written in Python. If Python is missing, the script whose whole
job is reporting what is missing cannot run, and their first experience of BLD is
a raw `'python' is not recognized`. **Windows does not ship Python**, so this is
common, not an edge case.

```bash
python3 --version || python --version || py --version
```

If none work, check the rest by hand so they only install once:

```bash
node --version; npm --version; git --version
```

Then give them the fix and stop:

**Give them the line for their OS only.** The Windows advice below is actively
wrong on macOS and Linux, where there is no installer and no checkbox:

| OS | What to say |
|---|---|
| **Windows** | Get it from [python.org/downloads](https://python.org/downloads), and **tick "Add python.exe to PATH" on the first screen**. It is off by default and everything fails confusingly without it. |
| **macOS** | `brew install python3`, or [python.org/downloads](https://python.org/downloads) if they have no Homebrew. macOS ships `python3` already on current versions, so check `python3 --version` before sending them anywhere. |
| **Debian / Ubuntu** | `sudo apt install python3`. Almost always already present, so check `python3 --version` first. |

Then: restart the terminal, run `/bld-setup` again.

**On macOS and Linux, "Python is missing" is usually wrong.** They typically
have `python3` and typically have no bare `python`, so a failed `python` proves
nothing on its own. Typically is not always: a stripped container or a macOS
without developer tools really can lack it. Confirm all three names failed
before telling anyone to install anything.

**Check the version too, not just that it runs.** `python --version` succeeds on a
Python 2 install. `preflight.py` then *parses* fine and dies partway through on
`shutil.which`, which reads to a beginner as "BLD is broken" rather than "my
Python is too old". Preflight now catches this itself and says so, but catching it
here means they never see a traceback at all. Anything
below 3.7 is too old (preflight uses `subprocess.run(capture_output=)`):

```bash
python3 -c "import sys;print(sys.version_info[:2])" || python -c "import sys;print(sys.version_info[:2])" || py -c "import sys;print(sys.version_info[:2])"
```

Note which of `python` / `python3` / `py` worked. That is `<PY>` for the rest of
this run: **every command below that shows `<PY>` gets the name that actually
worked**, never a guess. On macOS and most Linux distros bare `python` does not
exist at all, so guessing it silently breaks things that never report an error.

### 1c. Run preflight

Read-only: it installs nothing.

**On a first run, do not ask about scope here.** Nothing is installed yet, so
the answer cannot change what preflight finds, and scope is a Phase 3 question.
Run it bare.

**On any later run it matters, and preflight handles it itself:** Phase 5 records
the project path in the state file, and preflight reads it back. The line it
prints says where it looked and whether that came from the file:
`project scope checked: ... (remembered from your last setup)`.

Only pass `--project "<project dir>"` when that line points somewhere wrong, or
when the state file is gone:

```
<PY> "<resolved path>/skills/bld-setup/scripts/preflight.py" --project "<project dir>"
```

Without either, preflight looks in the *current* directory, which during setup is
the package folder, so a real install in their project reads as absent and the
verdict says to install it all again.

It prints prerequisites, deploy tooling, what BLD already installed, and a
**verdict**. Route on the verdict:

| Verdict | Do |
|---|---|
| `BLOCKED` | Stop. Only node and npm are truly required. Give the links it printed. |
| `LIMITED` | **Keep going.** git is missing, which removes only deploy, gstack and impeccable. Say what is unavailable, do not treat it as a failure. **Skip gstack and impeccable in Phase 3, and deploy in Phase 7.** |
| `FIRST RUN` | Full flow, Phase 2 onward. |
| `NO STATE FILE` / `STATE FILE IS EMPTY`, but BLD is already on this machine | **Not a first run.** BLD is on disk with no record of it: a hand install, or a deleted state file. Go to **Phase 6** and read its no-state note. |
| `STATE FILE UNREADABLE` | A setup interrupted while writing it. Same as the row above: **Phase 6**. Never run the full flow over it, and never delete their install to "start clean". |
| `RESUMING` | **Skip Phases 0, 2 and 3.** Pick up at the first item in "Still to do". **`deploy` and `agents` are the two groups whose install step is not in Phase 4** - both live in Phase 7, so go there for them and take the rest in Phase 4 order. Do not re-ask what they already chose. Anything under `ALREADY DONE` is on disk already - record it, do not reinstall it. Anything under `RECHECK` is the opposite: claimed, absent, reinstall it. |
| `RETURNING USER` | Skip to **Phase 6**. Do not re-run the flow. |

Show the user the preflight output. It is short, and it is the honest picture of
their machine.

## Phase 2 — what BLD is, and which commands they want

Print `references/skills.md` **verbatim**: all 24 commands grouped by type, each
with one line on what it does and a **Needs** column. Nobody can choose from a
list they have not read, and this is the only table that makes the question below
answerable.

Then two lines, not paragraphs:

- Nothing is installed yet.
- Every command they take costs a little context in **every** session, because
  Claude Code loads each skill's description at startup into a listing capped at
  about 1% of the context window. Taking fewer is a real choice, not a lesser
  one. The closing note in that table has the numbers.

Fire a `PushNotification` alongside the question. It blocks, and they may have
walked off during preflight.

One `AskUserQuestion`, single select:

| Option | Installs |
|---|---|
| **All 24 commands** | The whole set. Phase 3 then asks which supporting tools to add. |
| **Only the self-contained 16** | Every command whose Needs column is a dash. Nothing else to install, nothing half-working. |
| **Let me pick** | They write in the ones they want. `AskUserQuestion` always renders a write-in box, so this is that box - do not build a fourth option for it. |

**Do not ask about tools in this phase.** Not react-doctor, not the plugins, not
gstack. The commands are the thing they came for and the thing they can judge;
the tools are an implication of that choice, and Phase 3 derives them. Asking
"do you want react-doctor?" before they have seen `/bld-optimize-react` is asking
someone to consent to a word.

**Always copy `bld-setup`, `bld-settings-block-image-generation` and the
`bld-executor` agent**, whatever they picked. Setup is how they add the rest
later; the agent is one small file both orchestrators need; and the image-block
command is the off switch for a hook Phase 4 registers by default, so leaving it
out would install a block with no way to lift it.

**Record the chosen command names in `skills`, and put `bld` in `chose`** (Phase
5), before installing. The names drive the copy; the `bld` slug is what preflight
and the resume path count as a group, and a run interrupted here with `bld` in
neither `chose` nor `done` resumes believing BLD was never wanted. Add `prereqs`
to `done` on the same write, since Phase 1 has passed by then.
Preflight reads that list on every later run and reports only those as expected,
so a deliberate subset never gets reported as a half-finished install.

**A subset is not a smaller BLD, it is a shorter list.** Say once that re-running
`/bld-setup` adds any command later, with nothing lost and nothing to undo.

### Three kinds of thing, and users conflate them

Say this once, here, because Phase 3 is about to offer all three:

| Kind | What it is | Examples |
|---|---|---|
| **Plugin** | Claude Code extension, loads at startup | ponytail, ui-ux-pro-max |
| **CLI** | Ordinary command-line program | `gh`, `vercel`, `lighthouse` |
| **MCP server** | A data source Claude queries | jcodemunch, shadcn |

**There is no GitHub plugin and no Vercel plugin.** They are CLIs that
`/bld-util-deploy` shells out to.

## Phase 3 — the tools those commands need

**Derive the list from their Phase 2 picks. Never offer a tool no chosen command
uses.** Take the Needs column of every command they took; that set is this
phase's entire subject.

**Two entries in that column are not this phase's, and both say so:** `gh +
vercel` for `/bld-util-deploy` and `Codex or Gemini` for `/bld-runtime-agents`
are marked `(Phase 7)`. Drop them from the derived set, from the rows you print,
and from the picker, and do not write `deploy` or `agents` into `chose` here.
Phase 4 has no install step for either, so offering them in this phase recreates
the failure this skill already shipped once: a group chosen in the picker that
the install never reaches. If every pick has a dash there, say so in one line and go
straight to the scope question below - there is nothing to install and nothing to
ask.

Print the matching rows of the **At a glance** table in `references/manifest.md`
**verbatim**, with the warnings attached to those rows. It carries what each tool
is, whether it runs code, its source link, and which commands stop working
without it. Say in one line that full details for any row, with install commands,
are one request away - they are sections 1-7 of that file, which run to about 150
lines and are exactly where a beginner stops reading.

Then one `AskUserQuestion`, single select:

| Option | Installs |
|---|---|
| **Everything they need** (recommended) | Every tool the picked commands use. Nothing lands half-working. |
| **Skip the ones needing another installer** | Leaves out the token monitor (`uv` or `pipx`) and code search (`pip`). Everything else installs. |
| **Let me choose** | Multi-select. Four options per question is the cap, so ask twice rather than cramming. |
| **None for now** | The commands still install. The ones needing a tool sit inert until they re-run `/bld-setup`. |

**Everything not chosen goes into `declined`**, not just the tools they discussed.
See Phase 5: anything in neither `chose` nor `declined` is reported as missing on
every future run, and Phase 6 offers it back forever.

### Name what each declined tool costs

**After the answer, list the commands that will not work.** One line per declined
tool: the tool, a colon, its commands. Read them off the Needs column in
`skills.md` - it is the inverse of the lookup that built this phase.

```
React tools: /bld-optimize-react
Token monitor: /bld-runtime-tokens
gstack: /bld-optimize-security
```

That is the whole step. No paragraph, no persuasion, no second question: they
chose, and this is the receipt. Skip a tool they never declined, and print
nothing at all when they took everything.

**Skip any tool a missing prerequisite blocks**, and say why rather than dropping
it silently. One prerequisite does this, and Phase 1c reports it: **git missing**
(`LIMITED`) blocks gstack and impeccable here, and deploy in Phase 7, since all
three work by cloning or pushing a repo.

gstack used to need bun as well, because its own installer is a bun script. BLD
does not run that installer (Phase 4), so bun is not a prerequisite of anything.
Do not ask for it.

### Optional enhancements, asked separately

A Needs cell can hold a dash followed by an *italic* tool: the command runs
without it and does more with it. Today that is gstack, which adds four passes to
`/bld-optimize-security` and a deeper spec option to `/bld-sprint-planning`.

**Ask about these only after the required tools, as their own question, and only
if they did not take the self-contained bundle.** That bundle promises nothing
else installs; following it with an optional install offer breaks the promise the
picker just made. For everyone else, one question, with the At a glance row
printed first and skipping as the obvious default.

### What each tool actually is

Use these lines when describing a row. They name what it does and what it costs,
not just a category.

| Tool | What you get |
|---|---|
| **Core skills** (11) | Design taste from a working design engineer, animation craft, marketing copy, WCAG accessibility audits, and draft terms/privacy pages. **9 are markdown and can only suggest. Two ship scripts that execute:** `a11y-audit` and `webapp-testing`, the latter driving a real browser through Playwright. |
| **Plugins** (3) | **ponytail** stops Claude over-building things you did not ask for. **ui-ux-pro-max** is the design engine `/bld-sprint-init` uses for palettes and type. Those two run code, and ui-ux-pro-max also ships image generation, which BLD's hook blocks by default. **claude-code-setup** is Anthropic's official setup advisor: it reads a repo and suggests hooks, agents and skills. Markdown, so it can only suggest. |
| **React tools** (2 CLIs) | react-doctor and react-scan find real bugs, hook misuse, and needless re-renders. They power `/bld-optimize-react`. Adds two commands you can run from anywhere. |
| **Token monitor** | `/bld-runtime-tokens` shows how much Claude usage is left before a long session. Needs `uv` or `pipx`, one more installer. |
| **Code search** (3 MCP servers) | Cheaper exploration of large codebases. Only pays off past roughly fifty files. Only jcodemunch installs anything; the other two fetch themselves at query time. **context-mode runs shell commands with your logged-in CLIs**, which makes it the highest-trust item on this list. |
| **gstack** (5 skills) | Engineering specs, security review, root-cause debugging. **Only the five skills BLD uses**, copied out of the clone; never the 54-skill suite, its browser download, its hook, or its updater. |
| **impeccable** | Design craft and audit, 23 sub-commands. Clones skill files only, no installer, no hooks. |

### Then ask where BLD itself goes

**Lead with the recommendation, not the choice.** A first-timer has no project
yet, and a bare "global or project?" is a question they cannot evaluate. Say
which one you would pick and why, then let them override it:

> *"I'd put BLD on your machine globally, so the `/bld-*` commands work in every
> project. The alternative is scoping it to one folder, which is worth it if you
> share this machine or only want BLD in one repo. Global unless you say
> otherwise."*

One `AskUserQuestion`, single select:

| Option | What it does |
|---|---|
| **Global (recommended)** | `~/.claude/skills`. Every project sees the commands. |
| **This one project** | `<project>/.claude/skills`. Only that folder sees them, and it wins over a global copy on a name clash. |

**If they pick project, get the path and say what scoping does not cover** -
before installing, not after. Only BLD's own skills and the executor agent are
scoped. Core skills, plugins, React tools, gstack and impeccable are all
machine-wide with no per-project form, so scoping BLD does not give them a
machine-free install. The full table is in Phase 4 under "What scoping does and
does not cover"; if keeping a shared machine clean is the actual goal, the honest
answer is "scope BLD, and take the self-contained fifteen".

Resolve the project to an absolute path the same way Phase 1a resolves the
package, and **record `scope` and `project` in the state file now**. A scoped
install whose path was never recorded reports as vanished on every later run.

Record every answer in the state file (Phase 5) **before** installing, so an
interrupted run knows what they wanted.

## Phase 4 — install

Cheap and safe first, slow last, so a late failure does not block the rest.

**Run only the blocks for groups in `chose`. Skip every other block silently.**
Someone who took the self-contained fifteen has no tools in `chose` at all, so
this phase is one copy and nothing else; running the core-skills or plugins block
anyway installs what they just declined.

**Explain each command the first time it appears.** One block, then move on.

**Every block below is bash. Run them through the Bash tool**, which exists on
Windows, macOS and Linux. This is not a style note: the gstack block is a shell
`if` and a `for` loop, so in PowerShell it is a syntax error rather than a near
miss. If the user is typing commands themselves in a PowerShell
window, translate before handing them over - the `cp` / `mkdir` forms are under
**BLD itself**, and `rm -rf` becomes `Remove-Item -Recurse -Force`.

### Core skills (only if chosen)

```bash
npx -y skills add emilkowalski/skills --skill emil-design-eng      -g -a claude-code --copy -y
npx -y skills add emilkowalski/skills --skill animation-vocabulary -g -a claude-code --copy -y
npx -y skills add emilkowalski/skills --skill review-animations    -g -a claude-code --copy -y
npx -y skills add multica-ai/andrej-karpathy-skills --skill karpathy-guidelines -g -a claude-code --copy -y
npx -y skills add vercel-labs/skills --skill find-skills          -g -a claude-code --copy -y
npx -y skills add coreyhaines31/marketingskills --skill copywriting -g -a claude-code --copy -y
npx -y skills add alirezarezvani/claude-skills@a11y-audit         -g -a claude-code --copy -y
npx -y skills add dylantarre/animation-principles --skill framer-motion -g -a claude-code --copy -y
npx -y skills add anthropics/skills@webapp-testing                -g -a claude-code --copy -y
npx -y skills add shawnpang/startup-founder-skills@terms-of-service -g -a claude-code --copy -y
npx -y skills add shawnpang/startup-founder-skills@privacy-policy   -g -a claude-code --copy -y
```

Flags that matter:

- **`-a claude-code`**, never `-a claude` (fails: `Invalid agents: claude`). Omit
  it entirely and skills land in `~/.agents/`, where Claude Code never looks.
- **`-g`** installs globally, so every project sees them.
- **`--copy`** writes real files instead of symlinks. Windows symlinks are flaky.
- **The trailing `-y` is a different flag from the leading one.** `npx -y` only
  auto-confirms npx's own package download; the `skills` CLI then asks its *own*
  `Proceed with installation?` question. What happens with no TTY to answer it is
  **platform-dependent**, which is why this went unnoticed for so long. Measured
  2026-09-04, same command, same repo, fresh home, stdin from `/dev/null`:
  **Linux exits 0 having installed nothing**; **Windows proceeds and installs
  normally**. So the flag is load-bearing on Linux, presumably on macOS (untested),
  and harmless on Windows. Pass it everywhere rather than reasoning about which
  box you are on. Either way, verify by count and not by exit code:
  `ls ~/.claude/skills` should gain 11 entries.

Run them one at a time. Chaining with `&&` lets one dead repo kill the batch.

### Plugins (only if chosen)

Install through the headless CLI, then confirm all three say `enabled`:

```bash
claude plugin marketplace add https://github.com/DietrichGebert/ponytail.git
claude plugin marketplace add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
claude plugin marketplace add https://github.com/anthropics/claude-plugins-official.git
claude plugin install ponytail@ponytail
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
claude plugin install claude-code-setup@claude-plugins-official
claude plugin list        # confirm all three say: enabled
```

- **Pass the full HTTPS URL, not `owner/repo`.** The short form resolves to SSH
  and fails on a fresh machine with no GitHub SSH key: `No ED25519 host key is
  known for github.com ... Host key verification failed`.
- **`marketplace add` exits 0 even when the clone fails.** Judge it by the
  `✔ Successfully added marketplace` line or by `claude plugin list`, never by
  the exit code.
- **On Windows, ui-ux-pro-max can hit the 260-character path limit.** The fix is
  `git config --global core.longpaths true`, then re-run the add. Two things to
  know before chasing it. **The clone does not fail** - it succeeds and the
  *checkout* fails, so the message to look for is
  `error: unable to create file src/ui-ux-pro-max/scripts/tests/fixtures/catalogs/phosphor-react-exports.json: Filename too long`
  followed by `warning: Clone succeeded, but checkout failed`, which leaves a
  half-populated marketplace directory rather than no directory at all. And **it
  is unlikely at a normal install path**: measured 2026-09-04, that deepest file
  lands at 141 characters under `C:\Users\<name>`, and 166 even with a
  thirty-character username, both well under the limit. It was only reproducible
  from a deliberately deep directory totalling 262. Treat it as a remedy for a
  custom or deeply-nested install location, not something to expect.

If the CLI path fails, hand-write the same config and let startup fetch the
plugins. **Read `~/.claude/settings.json` first and merge. Never overwrite it.**
If it is absent, create it with just the keys below.

```json
{
  "enabledPlugins": {
    "ponytail@ponytail": true,
    "ui-ux-pro-max@ui-ux-pro-max-skill": true,
    "claude-code-setup@claude-plugins-official": true
  },
  "extraKnownMarketplaces": {
    "ponytail":            { "source": { "source": "github", "repo": "DietrichGebert/ponytail" } },
    "ui-ux-pro-max-skill": { "source": { "source": "github", "repo": "nextlevelbuilder/ui-ux-pro-max-skill" } },
    "claude-plugins-official": { "source": { "source": "github", "repo": "anthropics/claude-plugins-official" } }
  }
}
```

### BLD itself

**Phase 3 already asked where this goes.** Use that answer rather than asking
again. If it said global, run the block below; if it said project, skip to
"Project-scoped instead". Global is the recommendation and the common case.

**On a re-run, check the naming mode FIRST.** Phase 1c prints it: `24 of 24
(global, pro mode)`. The package ships friendly names, so copying it over a pro
mode install adds a second full set beside the renamed one - measured, 42 folders
and nineteen commands answering to two names each, at twice the context cost.
Nothing errors and nothing reports it, because both sets are valid skills. A
*clean* pro install looks perfectly healthy right up until this copy.

If Phase 1c said pro mode, bracket the copy:

```bash
<PY> ~/.claude/skills/bld-settings-professional/scripts/switch-mode.py off
```

**Copy the commands they chose in Phase 2, not the folder.** `SKILLS` is that
list, plus `bld-setup` and the agent, which always go.

**On a resume, Phase 2 was skipped, so read the list back from the state file's
`skills` array** rather than inventing one. If that array is missing or empty on
a resume, ask which commands they want instead of guessing: copying all 24 over a
deliberate subset is the one outcome the subset was chosen to avoid.

```bash
SKILLS="bld-setup bld-sprint-planning ..."   # their Phase 2 picks, space separated
mkdir -p ~/.claude/skills ~/.claude/agents
for s in $SKILLS; do
  rm -rf ~/.claude/skills/"$s"
  cp -r "<resolved path>/skills/$s" ~/.claude/skills/
done
cp -r "<resolved path>/agents/"*  ~/.claude/agents/
```

**Register the image-generation block in the same step.** BLD ships a
PreToolUse hook that refuses AI image generation, and it is on by default: copy
it next to the skills and add one entry to `~/.claude/settings.json`, reading and
merging that file rather than overwriting it.

```bash
mkdir -p ~/.claude/hooks
cp "<resolved path>/skills/bld-settings-block-image-generation/scripts/block-image-generation.py" ~/.claude/hooks/
<PY> ~/.claude/hooks/block-image-generation.py --selftest
```

The entry, merged into `hooks.PreToolUse`, with `<PY>` and `<home>` substituted
and `~` expanded (the command is not run through a shell):

```json
{ "matcher": "Skill|Bash|mcp__.*",
  "hooks": [ { "type": "command", "command": "<PY> \"<home>/.claude/hooks/block-image-generation.py\"" } ] }
```

**Say it in one line, then move on**: image generation is blocked from now on,
and `/bld-settings-block-image-generation off` is the switch. Full detail,
including what it deliberately does not catch, lives in that skill.

**The `rm -rf` before each copy is what keeps a re-run clean.** `cp -r src dest`
copies *into* `dest` when `dest` exists, so the second run of a plain copy
produces `~/.claude/skills/bld-quiz/bld-quiz/SKILL.md`, which never registers as
a skill and reports nothing. It only ever clears a folder this same list is about
to rewrite.

```bash
<PY> ~/.claude/skills/bld-settings-professional/scripts/switch-mode.py on
```

Skip both bracketing commands if Phase 1c said friendly mode. If it reported
folders in "the other naming mode", a rename stopped partway: finish that with
`/bld-settings-professional` before copying anything, or this same doubling
happens from the other direction.

**`cp` adds and overwrites; it never removes.** A skill that was dropped from the
package since their last install stays on their disk forever, and every session
keeps paying for it. Phase 1c lists what it did not expect to find - if it names
a `bld-*` folder the package no longer ships, say so and let them decide. Do not
delete it for them: on a project-scoped install that folder may be theirs.

**The `mkdir -p` is not optional.** A fresh Claude Code install has no
`~/.claude/agents/` directory, and `cp` into a missing target fails with
`No such file or directory`. Every first-time user is in exactly that state,
which is the one this skill exists for. `-p` also makes it a no-op when the
directories already exist, so it is safe on a re-run.

**Quote the path, leave the `*` outside the quotes.** The resolved path routinely
contains a space (`C:\Users\Firstname Lastname\...`), and unquoted it splits into
two arguments and the copy fails. Quoting the `*` too would stop it expanding.

Run this through the Bash tool, which has `cp` and `mkdir` on every platform. If
the user runs it themselves in PowerShell, `cp` is an alias for `Copy-Item` and
needs `-Recurse` instead of `-r`, and `mkdir -p` becomes
`New-Item -ItemType Directory -Force`. Give them that form rather than watching
it fail.

#### Project-scoped instead

Only if they asked for it. Same two directories, rooted in their project, which
wins over the global copy on a name clash:

```bash
SKILLS="bld-setup bld-sprint-planning ..."   # the same Phase 2 list
mkdir -p "<project>/.claude/skills" "<project>/.claude/agents"
for s in $SKILLS; do
  rm -rf "<project>/.claude/skills/$s"
  cp -r "<resolved path>/skills/$s" "<project>/.claude/skills/"
done
cp -r "<resolved path>/agents/"*  "<project>/.claude/agents/"
```

Resolve `<project>` to an absolute path the same way as the package path in
Phase 1a, and record it in the state file (Phase 5) so later runs find it
without being told.

**What scoping does and does not cover.** Say this plainly rather than letting
them discover it. Only the block above is scoped. Everything else in Phase 4 is
machine-wide and has no per-project form:

| Group | Where it actually goes |
|---|---|
| BLD skills + `bld-executor` | the project, if scoped |
| Core skills (11) | global - `npx skills add` is run with `-g` |
| Plugins (3) | global - Claude Code installs plugins per machine |
| React tools | global - `npm install -g` |
| gstack, impeccable | global - both clone into `~/.claude/skills/` |

Someone who picks project scope to keep a shared machine clean is not getting
that, and should hear it before the install rather than after. If that is their
actual goal, the honest answer is "scope BLD, and take the self-contained
fifteen", not "scoped install".

### React tools (only if chosen)

```bash
npm install -g react-doctor react-scan
```

`npm install -g` adds commands you can run from anywhere. It does not touch their
projects.

**This is the first `npm install -g` in the flow, so the permission failure
belongs here.** Codex, Gemini and vercel in Phase 7 hit exactly the same wall.

**If this dies with `EACCES ... mkdir /usr/local/lib/node_modules`**, it is the
first thing in the whole flow they see fail, and it will take react-doctor and
react-scan down with it later. The Node they have puts its global prefix
somewhere they do not own. Judge it by the error, not by the OS: a distro
`apt install nodejs npm` and the nodejs.org `.pkg` on macOS both land there,
while Homebrew, nvm, Volta, fnm and Windows do not.

**The fix is a user-owned prefix, not `sudo`.** `sudo npm install -g` succeeds
once and leaves root-owned files in `~/.npm` that make later non-sudo installs
fail in a way nobody connects back to this:

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export NPM_CONFIG_PREFIX=~/.npm-global' >> ~/.zshrc   # or ~/.bashrc
echo 'export PATH=~/.npm-global/bin:$PATH'    >> ~/.zshrc
export NPM_CONFIG_PREFIX=~/.npm-global; export PATH=~/.npm-global/bin:$PATH
```

Then re-run the install. `npm config set prefix` is npm's own documented remedy,
and the `NPM_CONFIG_PREFIX` line beside it is not redundant.

**On Debian and Ubuntu the documented remedy alone does nothing, silently** -
which is unfortunate, because that is precisely where the `EACCES` comes from.
The packaged npm ships a builtin config at `/usr/share/npm/npmrc` pinning
`prefix=/usr/local`, and it wins. Measured on Ubuntu 26.04 with npm 9.2.0:
after `npm config set prefix`, `npm config get prefix` reports the new directory
while `npm prefix -g` still answers `/usr/local`, and `npm install -g` installs
there and fails for the same reason as before. The environment variable is read
earlier and does win.

**Verify with `npm prefix -g`, never `npm config get prefix`.** They disagree in
exactly this case, and only the first one describes where packages actually go. Do not raise it pre-emptively: on most machines it never happens, and it
is one more thing to hold for someone who does not need it.

**Lighthouse is deliberately not installed.** `/bld-optimize-app` runs it through
`npx` so the version is never stale.

### Code search servers (only if chosen)

**Only one of the three installs anything.** `context-mode` and `shadcn` are
launched with `npx -y` at query time by `/bld-runtime-activate-mcps`, so there is
nothing to do for them now. `jcodemunch` is a Python package and has to exist on
PATH before that skill can start it:

```bash
<PY> -m pip install jcodemunch-mcp
```

The package name is `jcodemunch-mcp`, and it is also the command it installs.

**Two different errors land here, and both mean the same thing: use pipx or uv.**

- `error: externally-managed-environment` - that Python belongs to the OS or to
  Homebrew and will not take packages directly (PEP 668). **Do not force it with
  `--break-system-packages`**, which is how a system Python gets quietly broken
  for everything else on the machine.
- `No module named pip` - a minimal Debian/Ubuntu image ships `python3` without
  `pip` at all, so the command above fails before PEP 668 can even apply. Do not
  send them to `apt install python3-pip` for this; the pipx route below needs no
  system pip.

Neither is a BLD problem. Use the same tools the token monitor uses:

```bash
pipx install jcodemunch-mcp     # or: uv tool install jcodemunch-mcp
```

**On a minimal image neither of those exists either, and that is where this
dead-ends if you do not say so.** Measured on Ubuntu 26.04: no `pip`, no `pipx`,
no `uv`. Give them one line to get one, then continue:

```bash
sudo apt install pipx           # Debian/Ubuntu; or see astral.sh/uv for uv
```

If they do not want a third installer for an optional group, **say it is fine to
skip.** Code search only pays off past roughly fifty files and costs nothing to
add later.

Expect one of the two on Debian and Ubuntu, and `externally-managed-environment`
on Homebrew Python 3.11+. A python.org install on Windows or macOS takes the
plain `pip install` fine, which is where most users will be.

Nothing is written to `.mcp.json`. These stay on-demand unless the user later
runs `/bld-settings-mcp on`. Confirm with the `jcodemunch-mcp` row in preflight
rather than by starting a server, which would sit and wait for input.

### Token monitor (only if chosen)

```bash
uv tool install claude-monitor        # or: pipx install claude-monitor
```

**Neither `uv` nor `pipx` on the machine?** Preflight's `uv or pipx` row says so.
Ask once, then use the one route for their OS:

| OS | Route |
|---|---|
| **Windows** | `<PY> -m pip install --user pipx`, then `<PY> -m pipx install claude-monitor` |
| **macOS** | `brew install uv`, then the `uv` line above |
| **Debian / Ubuntu** | `sudo apt install pipx`, then `pipx install claude-monitor` |
| **Anything else** | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |

**The Windows route goes through Python on purpose.** An installer like
`winget install astral-sh.uv` works, but the new `uv` is not on the `PATH` of
the shell that installed it (Phase 9), so the very next line fails with
`'uv' is not recognized`. `<PY> -m pipx` needs no `PATH` change at all.
`claude-monitor` itself still lands in `~/.local/bin`, which is Phase 9's
second restart, not a failed install.

If they would rather not add an installer, skip. The only loss is
`/bld-runtime-tokens`. Say that plainly rather than pushing.

### gstack (only if chosen) — five skills, never the whole suite

**BLD does not run gstack's own `setup`.** That installer is what brings in the
whole suite: all 54 skills, about 700 MB of Playwright Chromium, a `Stop` hook in
`settings.json`, and a bun requirement before any of it can start. BLD uses five
of those skills, and all five ship pre-built in the repo under the names their
frontmatter declares (`gstack-spec`, `gstack-review`, ...), so copying them is the
whole install.

**The repo is still cloned, and it has to live at `~/.claude/skills/gstack`.**
The five skills call helper scripts by that path (`gstack/bin/gstack-config` and
others, plain bash). The clone also registers gstack's root `gstack` skill,
because it sits in the skills folder; that is expected.

```bash
# git clone into an existing directory fails outright, and this skill is built to
# be re-run. Three states to handle, not two: a real clone (pull it), a leftover
# directory from a clone that died partway (clear it), or nothing (clone).
if [ -d ~/.claude/skills/gstack/.git ]; then
  git -C ~/.claude/skills/gstack pull --ff-only
else
  rm -rf ~/.claude/skills/gstack
  git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
fi

# Turn on only the five skills BLD uses. Clear each target first: `cp -r src dest`
# copies INTO a dest that already exists, so a re-run would nest the skill one
# level down, where it never registers.
for s in spec investigate cso review careful; do
  rm -rf ~/.claude/skills/gstack-$s
  cp -r ~/.claude/skills/gstack/$s ~/.claude/skills/gstack-$s
done

# gstack's skills offer to upgrade gstack when a new version is out, and that
# upgrade runs the full `setup` this section exists to avoid. Switch the check off.
~/.claude/skills/gstack/bin/gstack-config set update_check false
```

**Verify five files before moving on:**
`ls ~/.claude/skills/gstack-{spec,investigate,cso,review,careful}/SKILL.md`.

**To update gstack later, re-run this block** (through `/bld-setup`). The pull
fetches the new version and the loop re-copies the five. Never run gstack's
`setup` or `/gstack-upgrade` for this: both install the full suite.

**`gstack-upgrade` is deliberately not one of the five.** It is gstack's own
updater, and it finishes by running `setup`.

**Telemetry is off by default.** The first gstack skill they run asks once
whether to turn it on. Their answer, not BLD's.

**An install made by an older BLD** ran `setup` and then pruned it back. This
block leaves that install working; it does not remove the Chromium download or
the hook `setup` added. The manifest's gstack warning names the command for the
hook, if they want it gone.

### impeccable (only if chosen) — skill files only

```bash
rm -rf ~/.claude/skills/impeccable
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/pbakaus/impeccable.git "$tmp/impeccable"
cp -r "$tmp/impeccable/.claude/skills/impeccable" ~/.claude/skills/impeccable
rm -rf "$tmp"
```

**Verify `~/.claude/skills/impeccable/SKILL.md` exists before moving on.**

**The `rm -rf` on the first line is load-bearing on a re-run**, and this skill is
built to be re-run. `mktemp -d` gives the clone a fresh directory every time, so
an interrupted run cannot leave one behind for the retry to collide with. The
target still has to go first: `cp -r src dest` copies *into* `dest`
when `dest` already exists, so a second pass produces
`~/.claude/skills/impeccable/impeccable/SKILL.md`. That path never registers as a
skill, and nothing reports an error: impeccable simply is not there.

Clearing the target first also means any local edits to the installed copy are
discarded. Say so if they might have made some; this is a reinstall, not a merge.

🚩 **Never run `npx impeccable install` or `update`** — both wire hooks into
their settings. And **never `/impeccable live`**: it forwards
`ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` to a third-party backend. Every
other impeccable command is fine.

## Phase 5 — record what happened

Write `~/.claude/.bld-setup.json` **as you go**, not at the end. An interrupted
setup that recorded nothing is a setup that starts over.

```json
{
  "scope": "global",
  "project": null,
  "package": "C:/Users/you/Downloads/bld-package",
  "builder": "hobbyist",
  "workspace": null,
  "skills": ["bld-setup", "bld-sprint-planning", "bld-sprint-init", "..."],
  "chose": ["bld", "core-skills", "plugins", "react-tools"],
  "declined": ["deploy", "gstack", "impeccable", "mcp", "token-monitor", "agents"],
  "done": ["prereqs", "core-skills", "plugins"],
  "completed": false,
  "completed_on": null,
  "notes": { "uv": "declined, /bld-runtime-tokens unavailable" }
}
```

- **`scope` and `project` are how a scoped install survives.** `"scope": "project"`
  with `"project": "C:/Users/you/code/your-app"` (absolute) lets preflight find it
  on every later run without anyone remembering `--project`. Leave `project` null
  for a global install. Omit them and a healthy scoped install reports as
  `MISSING NOW: bld ... Uninstalled, or a fresh machine reusing an old state file`,
  which is alarming and wrong.
- **`skills` is the list of `/bld-*` commands they chose in Phase 2.** Preflight
  reads it and expects exactly those, so a deliberate subset stops reporting as a
  half-finished install. Omit it and every later run lists the commands they
  never wanted under `MISSING`.
- **`builder` is the Phase 0 answer** (`starting` / `hobbyist` / `developer` /
  `senior`). It sets how much gets explained on a resume too, and Phase 8 fills
  the global rule file's "who I'm working with" blank from it.
- **`package` is how a resume finds the files.** Write the absolute path Phase 1a
  resolved, on the first write, before any install. Every `cp` in Phase 4, both
  template copies in Phase 8 and the verify command in Phase 9 read from it, and
  a fresh session has no other way to know where they put it.
- Append to `done` after each group finishes.
- **`declined` is every group they did not choose**, not just the ones they
  argued about: a declined deploy, the extras they skipped in Phase 3, `agents`
  if they skipped Phase 7. It is the difference between *not yet* and *not
  wanted*. Anything left out of both `chose` and `declined` reappears under
  `MISSING NOW` on every future run, and Phase 6 offers it back forever.
- Set `completed: true` and `completed_on` only after the restart reminder.
- **Never write this file by hand from memory on a resume.** Preflight has
  already compared it to the disk; take `ALREADY DONE` into `done` and drop
  anything under `RECHECK` back out of it.

## Phase 6 — returning user

Preflight said `RETURNING USER`. They already have BLD. **Do not re-run the
flow, and do not re-print the manifest.**

Open with what is actually available to them, as a short table:

- Anything in `declined` they might now want.
- Anything in the manifest that is missing.
- Anything installed but **unauthenticated** (`gh`, `vercel`).

> *"You already have core skills, plugins and the BLD commands. Three things you
> skipped are still available:"*

| | What it adds |
|---|---|
| gstack (5 skills) + impeccable | Engineering specs, security review, deep design audits |
| Code search MCPs | Cheaper exploration once a codebase gets big |
| Codex or Gemini | Makes `/bld-runtime-agents` work (Phase 7) |
| Deploy (`gh` + `vercel`) | Makes `/bld-util-deploy` work (Phase 7) |

**Check git before offering the gstack/impeccable and deploy rows, the same way
Phases 3 and 7 do.** Both
halves arrive by clone, so no `git` blocks the pair, and Phase 1c reports it.
Offering "gstack + impeccable" to someone who cannot receive either recreates,
on the returning path, the exact problem Phase 3 exists to prevent - and a
returning user is *more* likely to hit it, because they declined these once
already and may have declined them for this very reason.

Drop the row, name git and where it comes from
([git-scm.com](https://git-scm.com)), and leave both in `declined` rather than
silently marking them done.

Install only what they pick, then update `declined` and `done`. Nothing else.

### When there is no state file to read

`NO STATE FILE`, `STATE FILE IS EMPTY` (it parsed but held nothing) and
`STATE FILE UNREADABLE` all land here too, with one difference that changes how you talk: **there is no
`declined` list.** Preflight's "On disk now" is what they have; "Not here" is
everything else, and it cannot tell *not wanted* from *not yet*.

So do not open with "three things you skipped" - you do not know that they
skipped anything. Show what is there, ask what they want from the rest, and write
the state file (Phase 5) so the next run does not have to ask again. Reinstalling
what is already on disk is the one clear mistake here: it re-clones gstack and
re-adds plugin marketplaces for no gain.

## Phase 7 — extensions: coding agents, then deploy

Three optional extensions, and nothing in BLD depends on any of them. All three
work the same way: a CLI, then a login **only the user can do**. They sit here,
after the install, because the logins are the slow part and none of them blocks a
single `/bld-*` command from existing.

Print this table first, then ask:

| Extension | What it unlocks | What it costs |
|---|---|---|
| **Codex** (OpenAI) | `/bld-runtime-agents` hands bulky, repetitive coding work to it instead of your Claude usage | Free tier with low caps. A paid ChatGPT plan raises the ceiling, it does not unlock it |
| **Gemini** (Google) | The same command, as the fallback executor | Free tier, small enough to exhaust in one handoff |
| **Deploy** (`gh` + `vercel`) | `/bld-util-deploy`: a private GitHub repo and a live URL that redeploys on every push | Two browser logins, about five minutes. Needs git |

**Skip a row whose command they did not take in Phase 2**, and say so in one
line. Offering the deploy logins to someone who declined `/bld-util-deploy` is
five minutes spent on a command they will not have.

**`LIMITED` means no deploy row at all.** git is missing, `/bld-util-deploy`
works by pushing a git repo, so there is nothing here that can function:

> *"Skipping deploy setup: it needs git, which is not installed yet. Install git
> from [git-scm.com](https://git-scm.com) and re-run `/bld-setup` when you want
> it. Everything else works fine without it."*

**A resume can land in this phase too.** If `deploy` or `agents` is sitting in
"Still to do", they already said yes on an earlier run - skip the question and
pick up at whichever half is unfinished, which preflight's DEPLOY TOOLING rows
name exactly. Re-asking a question they have already answered is the thing the
resume path exists to avoid.

### The coding agents

Ask it in these words, then one single-select `AskUserQuestion` with Codex,
Gemini and Skip:

> *"Do you want to set up an external coding agent? `/bld-runtime-agents` hands
> bulky, repetitive coding work to Codex (OpenAI) or Gemini (Google), so it does
> not use up your Claude usage. Both have free tiers with low limits, and you do
> the sign-in yourself. Skip it and only that one command is unavailable."*

Lead with the question, not the command name. "Set up an agent for
`/bld-runtime-agents`?" asks a first-timer to evaluate a command they have
never seen; "external coding agent" names the thing they are actually agreeing
to install.

> **Claude never touches the credentials.** Print the commands; the user runs
> them and logs in. If a flow asks for anything secret, hand it back.

**Both have free tiers that work**, with caps low enough to matter. A paid
ChatGPT plan raises Codex's ceiling; it is not what makes Codex run. Suggest
whichever they can sign into today, and let `/bld-runtime-agents` detect what is
actually installed rather than promising either.

```bash
npm install -g @openai/codex     # see github.com/openai/codex for your OS
codex login                      # opens a browser; THE USER signs in

npm install -g @google/gemini-cli
gemini                           # first run prompts for auth; THE USER signs in
```

Prove it works rather than assuming, **from inside a git repo** - Codex refuses to
start anywhere else, and running the proof from a home directory reports a working
install as broken:

```bash
codex exec "reply with one word: ready"
```

Four things that have actually bitten:

- **Codex refuses to run outside a git repo.** `git init` first. This is the one
  above, and it bites hardest on the verification step, where the error looks
  like the install failed.
- **Each `codex exec` costs ~15k input tokens before reading your prompt.** Batch
  work; many small handoffs are mostly floor.
- **Gemini exits 255 even on success.** Judge by the diff, not the exit code.
- 🚩 **Never `--dangerously-bypass-approvals-and-sandbox` (Codex) or `-y` /
  `--yolo` (Gemini).** Those drop the sandbox. BLD uses `-s workspace-write` and
  `--approval-mode auto_edit`.

Then update the delegation block in `~/.claude/CLAUDE.md` to name what they
installed, or mark it unavailable so Claude stops offering it.

### Deploy: GitHub and Vercel

Ask it in these words, then install what preflight showed missing:

> *"Do you want `/bld-util-deploy`? It puts an app in a private GitHub repo and
> on a live URL, redeploying every time you push. It needs a GitHub account and a
> Vercel account, and you do both logins yourself. About five minutes. Skip it
> and everything else still works."*

```bash
npm install -g vercel
```

If that fails with `EACCES`, it is the same wall as Phase 4's React tools, and
the remedy is the user-owned npm prefix written out there. Do not reach for
`sudo`.

`gh` has no npm package, so it installs per-platform. **Give them the one line for
their OS, not all four** — a beginner reading a menu of package managers they do
not have will pick the wrong one:

| OS | Command |
|---|---|
| Windows | `winget install GitHub.cli` |
| macOS | `brew install gh` |
| Debian / Ubuntu | `sudo apt install gh` |
| Anything else | [cli.github.com](https://cli.github.com) |

**`apt install gh` fails on a lot of Debian and Ubuntu machines.** `gh` only
reached Ubuntu's own repos in 23.04 and is not in Debian's at all, so on Ubuntu
22.04 LTS - still one of the most common - it answers
`Unable to locate package gh`. When it does, send them to
[cli.github.com](https://cli.github.com). Do **not** walk them through adding
GitHub's apt repository: that is a keyring-and-sources-list detour in the middle
of a setup, for a CLI they can install from a page in one step.

If `brew` or `winget` is itself missing, same answer: `cli.github.com` rather than
starting a second install project. Setting up a package manager is not this
skill's job.

Then hand over the logins. **You cannot run these** — both open a browser and ask
for credentials:

```bash
gh auth login
vercel login
```

Wait, then confirm with `preflight.py` rather than assuming. **An installed CLI
is not a signed-in CLI**, and `--version` passes on both.

**A `vercel` you just installed can still report missing here, and it is not a
failed install.** They signed in from their own terminal; preflight runs in this
session's shell, which still has the `PATH` it started with. That is the second
restart described in Phase 9, arriving early. Before treating it as a problem,
check whether the binary exists - `ls "$(npm prefix -g)/bin"` on macOS and Linux,
`ls "$(npm prefix -g)"` on Windows. If it is there, the install worked and only
this shell is stale. `gh` shows the same thing from the other direction: Phase 1c's row reads
`signed in, but NOT on PATH -> restart the shell` when it resolved the fallback.

**Record the answer either way, before moving on (Phase 5).** A yes puts `deploy`
in `chose` **straight away, before the installs**, and moves it into `done` once
both CLIs are signed in. A no puts it in `declined`.

**Write `chose` before the logins, not after them.** Those two logins are the
longest human step in the setup and the likeliest place for it to be
interrupted. A yes recorded only on completion is a yes that disappears:
`deploy` lands in neither `chose` nor `declined`, so the resume never mentions
it again and every later run files it under `MISSING NOW` as "uninstalled, or a
fresh machine" - to someone who said yes and did both logins.

**If they say no, `declined` is the half that matters.**
An unrecorded decline is not neutral: preflight has no way to tell "did not want
it" from "had it and lost it", so every future run lists `deploy` under
`MISSING NOW` with "Uninstalled, or a fresh machine", and Phase 6 offers it back
to someone who already said no.

## Phase 8 — offer the CLAUDE.md rules (opt-in, never automatic)

BLD ships two opinionated rule files. **They are an offer, not part of the
install.** Someone already running Claude Code has their own way of working, and
a CLAUDE.md is the most personal file in the whole toolkit - it decides how every
answer is written. Installing one uninvited is the rudest thing this skill could
do.

| File | Holds | From |
|---|---|---|
| `~/.claude/CLAUDE.md` | Machine-wide: who you are, security drill, dev loop | `templates/CLAUDE.global.md` |
| `<workspace>/CLAUDE.md` | Mission, routing table, guardrails, deploy conventions | `templates/CLAUDE.workspace.md` |

### Ask, with the stakes stated

Say what each file changes before asking, in two lines - not everyone knows what
a CLAUDE.md does. Then one `AskUserQuestion`, single select:

| Option | Installs |
|---|---|
| **Both** | The machine-wide rules and this workspace's rules. |
| **Global only** | Machine-wide rules; leaves the workspace alone. |
| **This workspace only** | Workspace rules; leaves their global file alone. |
| **Neither** | Nothing. BLD's commands all work without these files. |

**"Neither" is a real answer, and the skill works fine after it.** Every `/bld-*`
command runs without either file. What is lost is the *defaults* - the dev loop,
the deploy conventions, the who-am-I block that decides how much gets explained.
Say that in one line and take the answer.

**Show them what they would be getting** if they ask, or if they hesitate: the
templates are plain markdown and reading one takes a minute. Never install
something this opinionated on a shrug.

### Which workspace, exactly

**`<workspace>` is not a value this flow has yet.** Phase 3 resolves a project
path only when someone picks a scoped install, and the recommended global answer
leaves it null. Settle it before any copy:

1. If the state file has `project`, offer that path as the default.
2. Otherwise ask for the folder where they keep their apps, and resolve it to an
   absolute path the same way Phase 1a resolves the package.
3. **Refuse the package folder.** It ships its own `CLAUDE.md`, a guide for
   people working on BLD, and writing the workspace template over it destroys
   that file and teaches every session in that repo the wrong rules. Recognise it
   the way preflight does, by `skills/bld-setup/scripts/preflight.py` sitting
   inside it.
4. Record it as `workspace` in the state file, so a later run can find the file
   it installed rather than asking again.

### Installing: rename theirs, never overwrite it

**A file already at either path is theirs and outranks anything BLD ships.** Move
it aside under a name they will recognise; do not merge, do not diff-and-patch,
do not delete.

```bash
if [ -e ~/.claude/CLAUDE.md ]; then
  if [ -e ~/.claude/CLAUDE.old.md ]; then
    echo "STOP: ~/.claude/CLAUDE.old.md already exists - not clobbering it"; exit 1
  fi
  mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.old.md
  echo "their file kept at ~/.claude/CLAUDE.old.md"
fi
cp "<resolved path>/templates/CLAUDE.global.md" ~/.claude/CLAUDE.md
```

```bash
if [ -e "<workspace>/CLAUDE.md" ]; then
  if [ -e "<workspace>/CLAUDE.old.md" ]; then
    echo "STOP: <workspace>/CLAUDE.old.md already exists - not clobbering it"; exit 1
  fi
  mv "<workspace>/CLAUDE.md" "<workspace>/CLAUDE.old.md"
  echo "their file kept at <workspace>/CLAUDE.old.md"
fi
cp "<resolved path>/templates/CLAUDE.workspace.md" "<workspace>/CLAUDE.md"
```

**The `CLAUDE.old.md` guard is the important half of that block, not padding.**
On a second run the file at `CLAUDE.md` is BLD's copy and `CLAUDE.old.md` is
their original - renaming again would overwrite the only copy of the thing this
whole phase exists to protect. Refusing is correct; tell them the path and let
them decide.

**Tell them the backup path in the same breath as "done".** A rule file that
silently stopped applying is indistinguishable from Claude behaving oddly, and
nobody thinks to look for `CLAUDE.old.md` a week later. Also say they can merge
the two by hand at any time - their old rules are text, not lost.

Record the answer in the state file (Phase 5) either way, as two independent
groups - someone can take the machine-wide rules and skip the workspace ones:

| Slug | The file |
|---|---|
| `claude-md-global` | `~/.claude/CLAUDE.md` |
| `claude-md-workspace` | `<workspace>/CLAUDE.md` |

**Write the answer the moment they give it**, into `chose` for the file(s) they
took and `declined` for the ones they refused - then move `chose` to `done` once
the copy lands. Recording only on success is the mistake Phase 7's
`deploy` step is written to avoid: an interruption between the answer and the copy leaves the group in
neither list, so the resume never mentions it and preflight has to report it as
`NEVER SET UP` afterwards. This phase is the likeliest one to be interrupted,
because it is last.

Installed goes in `done`, declined goes in `declined`. Left out of both, Phase 6
re-offers it on every future run - which is the wrong outcome for someone who has
already said no once.

### Filling in the blanks

Only for the file(s) they took.

**Twelve `<FILL IN>` blocks across the two templates: seven in the global one,
five in the workspace one.** Count the ones you installed. Someone who takes both
and fills in "the seven" ships a workspace file titled `<FILL IN: workspace name>`
with no GitHub account for `/bld-util-deploy`, because that one lives in the
workspace file. (Each file also mentions `<FILL IN>` once inside its opening HTML
comment. Those explain the convention; they are not blanks.)

These four deserve the most attention:

1. **Who they are** — decides how much gets explained. Phase 0 already asked;
   fill it from that answer rather than asking twice. *(global)*
2. **GitHub username** — used by `/bld-util-deploy`. *(workspace)*
3. **Delegation** — mark unavailable if they skipped Phase 7. *(global)*
4. **The dev loop** — server stays up, localhost link instead of opening their
   browser, and **never push without being asked**. Worth reading, not skimming.

**Both files carry a block saying they are living documents.** Point at it once:
the who-they-are answer is a starting guess Claude is expected to revise as it
learns how they actually work, not a form filled in once and obeyed forever.

## Phase 9 — restart, then verify

**Skills, hooks and plugins register at startup.** Nothing installed is live
until Claude Code restarts. Say this plainly. It is the number one reason a fresh
setup looks broken.

**There is a second restart, and it is not the same one.** A CLI installed into a
directory that was not already on `PATH` stays invisible to *this* shell, and so
to preflight, until a new shell starts. It hits `claude-monitor` and
`jcodemunch-mcp` (uv puts them in `~/.local/bin`), and anything installed after
an npm prefix change (`~/.npm-global/bin`). uv and npm both append the directory
to `~/.profile` and `~/.bashrc`, which is enough for a human opening a terminal
and not enough for a non-interactive shell, which reads neither. So a tool that
installed perfectly reports `[--]` seconds later. Before treating that as a
failed install, check the binary directly - `ls ~/.local/bin` and
`ls ~/.npm-global/bin` - and if it is there, the install worked and only the
`PATH` is stale. On Windows the same thing happens for a different reason: PATH
comes from the environment block a process inherited at launch, so a running
terminal never sees an installer's change.

After restarting:

```bash
<PY> "<resolved path>/skills/bld-setup/scripts/preflight.py"
```

A scoped install needs no flag here, as long as Phase 5 wrote `project`. Confirm
it did by reading the line preflight prints: `project scope checked: ...
(remembered from your last setup)`. If that names the wrong directory, pass
`--project` and fix the state file. Getting this wrong is worse here than in 1c:
the run happens seconds after a successful install, so a false "none installed"
reads as "setup failed" at the exact moment they are primed to believe it.

**Expect the verdict to say `RESUMING an unfinished setup`, and do not report
that as a problem.** `completed` is still `false` at this point - it is set at
the end of this phase, after the restart reminder - so a completely successful
install lands in the resume branch by design. What matters is the line below it:
`Still to do : finish up + restart` means every group installed. A list of real
group names there does not, and that is the failure worth reading out.

Then have them type `/bld-` and confirm the commands appear. A skill on disk but
missing from the list means its frontmatter did not parse.

Close with what was installed, what was skipped, and that
`/bld-sprint-planning` is where a first app starts.

Set `completed: true` in the state file.

## Pitfalls

- **Reaching for `preflight.py` before confirming Python exists.** It is a Python
  script. On a machine without Python the first thing a new user sees is a raw
  interpreter error from the tool meant to diagnose them.
- **Treating a missing `git` as fatal.** It only gates deploy, gstack and
  impeccable. Everything else installs without it.
- **Trying to fit every option into one `AskUserQuestion`.** The cap is 4.
  Offer bundles, then fall through.
- **Showing a `<BLD>` placeholder to the user.** Resolve the real path first.
- **Asking a question whose table you never printed.** The commands in Phase 2,
  the tools in Phase 3, the extensions in Phase 7: print, then ask.
- **Rewriting the welcome note.** It is quoted because it is the author's, not
  yours. Print it or skip the phase; never paraphrase it.
- **Asking about tools in Phase 2.** The commands are what they can judge. The
  tools follow from that pick, in Phase 3, and only the ones their picks need.
- **Printing all of the manifest unprompted.** The At a glance table is the
  consent surface; sections 1-7 are reference, on request.
- **Forgetting `skills` in the state file.** A deliberate subset then reads as a
  broken install on every later run.
- **Running gstack's `setup`, or accepting its upgrade offer.** Either one
  installs the whole suite BLD deliberately leaves out.
- **Skipping preflight on a resume.** It is what tells you where you are.
- **Overwriting an existing `~/.claude/CLAUDE.md`.** Merge or ask.
- **Treating installed as authenticated.** `gh --version` passes on a signed-out
  CLI, and `/bld-util-deploy` fails on one.
- **Claiming success before a restart.**
- **Chaining installs with `&&`.** One dead repo kills the batch.
- **Re-running the full flow for a returning user.** That is Phase 6.
- **Reading "no state file" as "nothing installed".** They are different, and
  preflight now says which. A hand install or a deleted dotfile is not a first
  run, and reinstalling over it wastes their time and re-clones what is there.
- **Finishing a scoped install without writing `scope` and `project`.** The
  install works; every later run then reports it as vanished.
- **Asking global vs project as a bare question.** Phase 3 asks it, but it always
  leads with the recommendation. "Global or project?" with no steer is a question
  a first-timer cannot answer, and the honest default is global.
- **Letting "scoped" imply a machine-free install.** Only BLD's own skills and the
  executor agent are scoped. Say so before installing, not after.
- **Over-explaining.** See the voice rules at the top. Beginners need the
  unfamiliar explained, not everything.

## Refining this skill

Do not read `TESTING.md` during a normal run. It is for sessions working *on*
this skill rather than *with* it.

It holds the method that has found every real bug in here: walk a deliberately
awkward machine through the phases and record what cannot happen. Six runs found
thirty-seven bugs, including a security control that registered and then failed
silently on every non-Windows machine, and a group offered in Phase 3 that
Phase 4 never installed. Reading the skill found none of them.

`scripts/scenarios.py` is the regression net that grew out of those runs. It is
worth running after any change to `preflight.py`, and it is not a substitute for
a walk: every bug above was found by walking, on a suite that was passing.

Default to a quiet audit that reports only findings. Produce the full role-played
transcript **only when the user asks for a simulation**.
