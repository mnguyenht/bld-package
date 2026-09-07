---
name: bld-setup
description: Set up BLD on a machine, or add more of it later. Checks prerequisites, shows every tool it would install with a source link, installs only what you pick, and records where it got to so an interrupted setup resumes instead of restarting. Use when the user says /bld-setup, "set up BLD", "install the BLD toolkit", "add the rest of BLD", "what else can I install", or has just cloned bld-package. Never installs anything it did not list first.
---

# bld-setup

Installs other people's software onto someone's machine. That is a trust
transaction, so the order is fixed:

> **Check the machine → show the list → get a yes → install → record it.**

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

## Phase 0 — preflight (always first, even on a resume)

### 0a. Find the package, and never show a placeholder

Locate the folder holding `skills/` and `README.md`. Usually the current
directory, or the one they just cloned or unzipped. **Resolve it to a real
absolute path and use that in every command you show them.** A beginner cannot
substitute `<BLD>` and should never be asked to.

### 0b. Confirm Python exists BEFORE running a Python script

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

### 0c. Run preflight

Read-only: it installs nothing.

**On a first run, do not ask about scope here.** Nothing is installed yet, so
the answer cannot change what preflight finds, and scope is a Phase 4 question.
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
| `LIMITED` | **Keep going.** git is missing, which removes only deploy, gstack and impeccable. Say what is unavailable, do not treat it as a failure. **Skip Phase 2 entirely**, and skip those groups in Phase 3. |
| `FIRST RUN` | Full flow, Phase 1 onward. |
| `NO STATE FILE, but BLD is already on this machine` | **Not a first run.** BLD is on disk with no record of it: a hand install, or a deleted state file. Go to **Phase 6** and read its no-state note. |
| `STATE FILE UNREADABLE` | A setup interrupted while writing it. Same as the row above: **Phase 6**. Never run the full flow over it, and never delete their install to "start clean". |
| `RESUMING` | **Skip Phases 1-3.** Pick up at the first item in "Still to do". Do not re-ask what they already chose. Anything under `ALREADY DONE` is on disk already - record it, do not reinstall it. Anything under `RECHECK` is the opposite: claimed, absent, reinstall it. |
| `RETURNING USER` | Skip to **Phase 6**. Do not re-run the flow. |

Show the user the preflight output. It is short, and it is the honest picture of
their machine.

## Phase 1 — the manifest

Print all seven sections of `references/manifest.md` **verbatim**, tables and
source links intact.

Then, briefly:

- Nothing is installed yet.
- **Most of this installs machine-wide**, under `~/.claude/`. BLD's own commands
  can be scoped to a single project instead - say so and it will be. The other
  groups have no per-project form, so scoping BLD does not make the install
  machine-free. See "What scoping does and does not cover" below.
- **`Runs code?`** is the column that matters. `md` rows are text and can only
  suggest things. `code` rows execute on their machine.
- Section 7 is not installed. Both have working free tiers with low caps, so
  neither is a paid tool; a paid plan raises a ceiling, it does not unlock one.
- Uninstalling is mostly deleting files in `~/.claude/`, but not only: it also
  means `~/.agents/.skill-lock.json`, Playwright Chromium from
  `%LOCALAPPDATA%\ms-playwright` (Windows) or `~/.cache/ms-playwright`
  (macOS/Linux), and `react-doctor` / `react-scan` from the npm global prefix
  (`npm root -g`). Nothing touches their projects.

Lines, not paragraphs.

### Three kinds of thing, and users conflate them

Say this once. It is the most common confusion in the whole skill:

| Kind | What it is | Examples |
|---|---|---|
| **Plugin** | Claude Code extension, loads at startup | ponytail, ui-ux-pro-max |
| **CLI** | Ordinary command-line program | `gh`, `vercel`, `lighthouse` |
| **MCP server** | A data source Claude queries | jcodemunch, shadcn |

**There is no GitHub plugin and no Vercel plugin.** They are CLIs that
`/bld-util-deploy` shells out to.

## Phase 2 — deploy accounts, asked early on purpose

**Skip this entire phase if preflight said `LIMITED`.** That verdict means git is
missing, and `/bld-util-deploy` works by pushing a git repo, so there is nothing
here that can function. Offering it anyway spends five minutes of someone's time
on two account logins for a feature that cannot run. Say one line instead:

> *"Skipping deploy setup: it needs git, which is not installed yet. Install git
> from [git-scm.com](https://git-scm.com) and re-run `/bld-setup` when you want
> it. Everything else works fine without it."*

Otherwise, ask before the main install, because these need **human logins**
nobody else can do, and they are the slow part:

> *"Do you want `/bld-util-deploy`? It puts an app in a private GitHub repo and
> on a live URL, redeploying every time you push. It needs a GitHub account and a
> Vercel account, and you do both logins yourself. About five minutes. Skip it
> and everything else still works."*

If yes, and preflight showed them missing:

```bash
npm install -g vercel
```

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
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc   # or ~/.bashrc
```

Then re-open the shell and re-run the install. This is npm's own documented
remedy. Do not raise it pre-emptively: on most machines it never happens, and it
is one more thing to hold for someone who does not need it.

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
this shell is stale. `gh` shows the same thing from the other direction: Phase 0c
says `found at the default path but NOT on PATH` when it resolved the fallback.

**Record the answer either way, before moving on (Phase 5).** Yes puts `deploy`
in `done` once both CLIs are signed in; no puts it in `declined`.

**If they say no, `declined` is the half that matters.**
An unrecorded decline is not neutral: preflight has no way to tell "did not want
it" from "had it and lost it", so every future run lists `deploy` under
`MISSING NOW` with "Uninstalled, or a fresh machine", and Phase 6 offers it back
to someone who already said no.

## Phase 3 — pick what to install

⚠️ **`AskUserQuestion` allows a maximum of 4 options per question.** Eight
checkboxes in one question is not possible. Offer bundles first, and only fall
through to a group-by-group picker if they ask for it. Most people take the
first option and never see the second question.

Fire a `PushNotification` alongside the question. It blocks, and they may have
walked off during preflight.

**Question 1**, single select:

| Option | Installs |
|---|---|
| **Everything recommended** | Core skills, BLD, plugins, React tools. The usual answer. |
| **Everything, extras included** | The above plus token monitor, code search servers, gstack and impeccable. |
| **Just the essentials** | BLD and the plugins. The smallest setup that still works. |
| **Let me choose** | Falls through to the two questions below. |

If they pick "Let me choose", ask these two, both multi-select, four options each:

**Question 2 — the core four.** Core skills · BLD · Plugins · React tools.

**Question 3 — the extras.** Token monitor · Code search servers · gstack +
impeccable · Nothing else.

**"Nothing else" sits in a multi-select, so it can be ticked alongside a real
pick.** That is not an error to bounce back at them: the specific picks win and
"Nothing else" means "and nothing beyond these". Say which way you read it in one
line and carry on. Re-asking a question they already answered is worse than
reading it the obvious way.

**Everything not chosen goes into `declined`**, not just the groups they
discussed. See Phase 5 - a group that is in neither list is reported as missing
on every future run.

**Skip any group a missing prerequisite would block**, and say why rather than
silently dropping it. **That includes the Question 1 labels**, not just the
install step: "Everything, extras included" reads as a promise of gstack and
impeccable, and offering a bundle you already know cannot install all of it is
how a setup ends with someone asking where their tools went. Reword the option to
what they will actually get, and name what is holding the rest back.

Two prerequisites do this, and Phase 0c reports both:

- **git missing** (`LIMITED`) blocks `/bld-util-deploy`, gstack and impeccable.
- **bun missing** blocks gstack alone, because its installer is a bun script.
  impeccable is unaffected.

These two are not the same size of problem. git is a real detour and genuinely
gates three things, so reshape the bundle around it. **bun is one npm install**
(`npm install -g bun`, official package), and npm is already a prerequisite - so
keep gstack in the offer and mention the extra line, rather than quietly dropping
it. Only reshape the bundle if they decline the install.

**Question 2 lets them deselect BLD.** Honour it, but say what it means first:
without it there are no `/bld-*` commands at all, and the Phase 9 check will find
nothing. One line, then do as they asked - they may genuinely want only the
plugins.

### What each group actually is

Use these when describing the options. They name what it does and what it costs,
not just a category.

| Group | What you get |
|---|---|
| **Core skills** (11) | Design taste from a working design engineer, animation craft, marketing copy, WCAG accessibility audits, and draft terms/privacy pages. **9 are markdown and can only suggest. Two ship scripts that execute:** `a11y-audit` and `webapp-testing`, the latter driving a real browser through Playwright. |
| **BLD** (23 commands) | What you cloned this for. Also adds a hook that blocks AI image generation. |
| **Plugins** (3) | **ponytail** stops Claude over-building things you did not ask for. **ui-ux-pro-max** is the design engine `/bld-sprint-init` uses for palettes and type. Those two run code, and ui-ux-pro-max also ships image generation, which BLD blocks. **claude-code-setup** is Anthropic's official setup advisor: it reads a repo and suggests hooks, agents and skills. Markdown, so it can only suggest. |
| **React tools** (2 CLIs) | react-doctor and react-scan find real bugs, hook misuse, and needless re-renders. They power `/bld-optimize-react`. Adds two commands you can run from anywhere. |
| **Token monitor** | `/bld-runtime-tokens` shows how much Claude usage is left before a long session. Needs `uv`, one more installer. Skip it and you lose only that one command. |
| **Code search** (3 MCP servers) | Cheaper exploration of large codebases. Only pays off past roughly fifty files. **context-mode runs shell commands with your logged-in CLIs**, which makes it the highest-trust item on this list. Easy to add later. |
| **gstack + impeccable** | Two large opinionated suites: engineering specs, security review, deep design audits. Both ship code, both are big, and both need git. Nothing depends on them, so adding them later costs nothing. |

Record the answer in the state file (Phase 5) **before** installing, so an
interrupted run knows what they wanted.


## Phase 4 — install

Cheap and safe first, slow last, so a late failure does not block the rest.

**Explain each command the first time it appears.** One block, then move on.

**Every block below is bash. Run them through the Bash tool**, which exists on
Windows, macOS and Linux. This is not a style note: the gstack block is a shell
`if` and the prune is a heredoc, so in PowerShell they are syntax errors rather
than near misses. If the user is typing commands themselves in a PowerShell
window, translate before handing them over - the `cp` / `mkdir` forms are under
**BLD itself**, and `rm -rf` becomes `Remove-Item -Recurse -Force`.

### Core skills

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

### Plugins

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

**Recommend global** unless they already have a project in mind. A first-timer
has no project yet, so asking them to choose is asking about something they
cannot evaluate.

**On a re-run, check the naming mode FIRST.** Phase 0c prints it: `23 of 23
(global, pro mode)`. The package ships friendly names, so copying it over a pro
mode install adds a second full set beside the renamed one - measured, 42 folders
and nineteen commands answering to two names each, at twice the context cost.
Nothing errors and nothing reports it, because both sets are valid skills. A
*clean* pro install looks perfectly healthy right up until this copy.

If Phase 0c said pro mode, bracket the copy:

```bash
<PY> ~/.claude/skills/bld-professional-settings/scripts/switch-mode.py off
```

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r "<resolved path>/skills/"*  ~/.claude/skills/
cp -r "<resolved path>/agents/"*  ~/.claude/agents/
```

```bash
<PY> ~/.claude/skills/bld-professional-settings/scripts/switch-mode.py on
```

Skip both bracketing commands if Phase 0c said friendly mode. If it reported
folders in "the other naming mode", a rename stopped partway: finish that with
`/bld-professional-settings` before copying anything, or this same doubling
happens from the other direction.

**`cp` adds and overwrites; it never removes.** A skill that was dropped from the
package since their last install stays on their disk forever, and every session
keeps paying for it. Phase 0c lists what it did not expect to find - if it names
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
mkdir -p "<project>/.claude/skills" "<project>/.claude/agents"
cp -r "<resolved path>/skills/"*  "<project>/.claude/skills/"
cp -r "<resolved path>/agents/"*  "<project>/.claude/agents/"
```

Resolve `<project>` to an absolute path the same way as the package path in
Phase 0a, and record it in the state file (Phase 5) so later runs find it
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
| The image-gen hook file | global - `~/.claude/hooks/`, so it outlives the project |

Someone who picks project scope to keep a shared machine clean is not getting
that, and should hear it before the install rather than after. If that is their
actual goal, the honest answer is "scope BLD, and take Just the essentials", not
"scoped install".

**Copy the hook out of the package first.** The two `cp` lines above move
`skills/` and `agents/` but not `hooks/`, so registering the package's own copy
points the hook at a folder the user is likely to delete once setup "worked".
Nothing warns them: the hook stays registered, silently fails to run, and image
generation is quietly unblocked from then on. Give it a home that outlives the
clone:

```bash
mkdir -p ~/.claude/hooks
cp "<resolved path>/hooks/block-image-skills.py"  ~/.claude/hooks/
```

Then register **that** copy at the same scope BLD was installed at: a global
install uses `~/.claude/settings.json`; a project-scoped install uses that
project's `.claude/settings.local.json`. **Merge, do not overwrite.** If plugins
were installed, global settings already hold `enabledPlugins` and
`extraKnownMarketplaces`; read them, add the `hooks` key, and write back. **If
the file does not exist, create it with just the `hooks` key** - a user who
declined plugins on a fresh Claude Code install has no `settings.json` yet, and
reading one that is not there is not a reason to skip the hook. Use an
**absolute path** because the hook runs with an unpredictable working directory.
Expand `~` yourself: the hook command is not run through a shell, so a literal
`~` is looked up as a directory named `~` and never resolves.

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Skill", "hooks": [
  { "type": "command", "command": "<PY> \"<home>/.claude/hooks/block-image-skills.py\"" } ] } ] } }
```

**`<PY>` here is not optional.** Substitute the interpreter Phase 0b found. A hook
that names a missing interpreter still registers fine and then fails every single
time it fires, printing nothing the user will see. The result is a security
control that looks installed and is not running. After writing the file, run the
cheaper check: `<PY> ~/.claude/hooks/block-image-skills.py --selftest` prints
`selftest ok: N blocked, M allowed` and exits 0. A hook nobody tested is a hook
nobody has.

### React tools

```bash
npm install -g react-doctor react-scan
```

`npm install -g` adds commands you can run from anywhere. It does not touch their
projects.

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

Expect one of the two on Debian and Ubuntu, and `externally-managed-environment`
on Homebrew Python 3.11+. A python.org install on Windows or macOS takes the
plain `pip install` fine, which is where most users will be.

Nothing is written to `.mcp.json`. These stay on-demand unless the user later
runs `/bld-mcp-settings on`. Confirm with the `jcodemunch-mcp` row in preflight
rather than by starting a server, which would sit and wait for input.

### Token monitor (only if chosen)

```bash
uv tool install claude-monitor        # or: pipx install claude-monitor
```

If `uv` is missing and unwanted, skip. The only loss is `/bld-runtime-tokens`.
Say that plainly rather than pushing.

### gstack (only if chosen) — install, then immediately prune

**gstack's `setup` is a bun script, not a node one.** Check for bun BEFORE the
clone: without it `setup` exits 1 and leaves a cloned repo with no wrappers
generated, which is the confusing half-state the prune below then misreports.

**This is a one-line prerequisite, not a wall.** bun publishes an official npm
package (`oven-sh/bun`, maintained by its author), and npm is already required
before any of this runs, so there is no new toolchain to explain and no install
script to pipe into a shell. Say what it is for - gstack's installer, nothing
else in BLD - and install it if they want gstack:

```bash
npm install -g bun
```

```bash
command -v bun >/dev/null || { echo "gstack needs bun: run 'npm install -g bun', or skip gstack"; exit 1; }

# git clone into an existing directory fails outright, and this skill is built to
# be re-run. Three states to handle, not two: a real clone (pull it), a leftover
# directory from a clone that died partway (clear it), or nothing (clone).
if [ -d ~/.claude/skills/gstack/.git ]; then
  git -C ~/.claude/skills/gstack pull --ff-only
else
  rm -rf ~/.claude/skills/gstack
  git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
fi
bash ~/.claude/skills/gstack/setup
```

gstack links its wrappers under **bare names** (`spec`, `review`, `cso`,
`careful`, `investigate`), so they sit in `~/.claude/skills/` next to everything
else and collide with generic names. BLD keeps six: `spec`, `investigate`, `cso`,
`review`, `careful` and `gstack-upgrade`, plus the `gstack` root skill and the
`_gstack-command` router. The rest are iOS, paid-provider, browser, deploy and
team-process skills that duplicate what BLD does, and every one costs context on
every session.

```bash
cat > ~/.claude/skills/gstack-prune.sh <<'SH'
#!/usr/bin/env bash
# Deletes generated gstack skill wrappers from ~/.claude/skills. Idempotent.
# Matched by the gstack install path their body references, NOT by a name prefix:
# gstack links wrappers under BARE names (spec, review, ship, connect-chrome), so
# a `gstack-*` glob matches none of them and silently prunes nothing. The gstack
# repo is never touched, so re-running `setup` restores everything removed here.
keep=" gstack _gstack-command spec investigate cso review careful gstack-upgrade "
n=0
for d in ~/.claude/skills/*/; do
  s=$(basename "$d")
  case "$s" in bld-*) continue ;; esac          # never prune BLD's own skills
  case "$keep" in *" $s "*) continue ;; esac
  grep -q 'skills/gstack' "$d/SKILL.md" 2>/dev/null || continue
  rm -rf "$d" && echo "pruned $s" && n=$((n+1))
done
echo "pruned $n gstack wrappers"
SH
bash ~/.claude/skills/gstack-prune.sh
```

**The prune prints how many it removed. A run that prints
`pruned 0 gstack wrappers` right after `setup` is a failure, not a success — but
check the cause in this order, because the second one is far more common than the
first looks:**

1. **`setup` never ran.** Scroll up. `Error: bun is required but not installed.`
   means there are no wrappers to prune and the count is correctly zero. Install
   bun, re-run `setup`, then re-run the prune.
2. **The matcher is stale.** Only if `setup` actually succeeded. gstack changed
   its wrapper layout and `grep 'skills/gstack'` no longer matches them.

⚠️ **`setup` un-prunes.** Re-run the prune after every `git pull` or
`/gstack-upgrade`. Tell them once; it is the easiest way for a context budget to
quietly triple.

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
  "chose": ["core-skills", "bld", "plugins", "react-tools"],
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
| gstack + impeccable | Engineering specs, security review, deep design audits |
| Code search MCPs | Cheaper exploration once a codebase gets big |
| Codex or Gemini | Makes `/bld-runtime-agents` work |

**Check the prerequisites before offering that first row, the same way Phase 3
does.** It is a pair, and the two halves fail differently: no `git` blocks both,
no `bun` blocks gstack alone and leaves impeccable perfectly installable. Phase
0c reports both. Offering "gstack + impeccable" to someone who can only receive
half of it recreates, on the returning path, the exact problem Phase 3 exists to
prevent - and a returning user is *more* likely to hit it, because they declined
these once already and may have declined them for this very reason.

Split the row or drop the half they cannot have, name the missing tool and where
it comes from, and leave it in `declined` rather than silently marking it done.

Install only what they pick, then update `declined` and `done`. Nothing else.

### When there is no state file to read

`NO STATE FILE, but BLD is already on this machine` and `STATE FILE UNREADABLE`
land here too, with one difference that changes how you talk: **there is no
`declined` list.** Preflight's "On disk now" is what they have; "Not here" is
everything else, and it cannot tell *not wanted* from *not yet*.

So do not open with "three things you skipped" - you do not know that they
skipped anything. Show what is there, ask what they want from the rest, and write
the state file (Phase 5) so the next run does not have to ask again. Reinstalling
what is already on disk is the one clear mistake here: it re-clones gstack and
re-adds plugin marketplaces for no gain.

## Phase 7 — external coding agents (optional, free but capped)

`/bld-runtime-agents` is the one BLD skill needing an account elsewhere.
**Offer, do not push.** Skipping costs exactly one skill.

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

1. **Who they are** — decides how much gets explained. *(global)*
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
`--project` and fix the state file. Getting this wrong is worse here than in 0c:
the run happens seconds after a successful install, so a false "none installed"
reads as "setup failed" at the exact moment they are primed to believe it.

**Expect the verdict to say `RESUMING an unfinished setup`, and do not report
that as a problem.** `completed` is still `false` at this point - it is set at
the end of this phase, after the restart reminder - so a completely successful
install lands in the resume branch by design. What matters is the line below it:
`Still to do : finish up + restart` means everything installed. A list of real
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
- **Trying to fit every group into one `AskUserQuestion`.** The cap is 4 options.
  Offer bundles, then fall through.
- **Showing a `<BLD>` placeholder to the user.** Resolve the real path first.
- **Installing before printing the manifest.** Even when told "just install
  everything" — printing costs one message and is their only chance to object.
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
- **Asking a first-timer to choose global vs project scope.** Recommend global.
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
