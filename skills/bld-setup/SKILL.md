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

**If they want BLD scoped to one project rather than global, pass that project:**
`<PY> "<resolved path>/skills/bld-setup/scripts/preflight.py" --project "<project dir>"`.
Without it preflight looks for a project-scoped install in the *current*
directory, which during setup is the package folder, so a real install sitting
in their project reads as absent and the verdict says to install it all again.
Global installs need no flag. The line it prints names the directory it checked.

It prints prerequisites, deploy tooling, what BLD already installed, and a
**verdict**. Route on the verdict:

| Verdict | Do |
|---|---|
| `BLOCKED` | Stop. Only node and npm are truly required. Give the links it printed. |
| `LIMITED` | **Keep going.** git is missing, which removes only deploy, gstack and impeccable. Say what is unavailable, do not treat it as a failure. **Skip Phase 2 entirely**, and skip those groups in Phase 3. |
| `FIRST RUN` | Full flow, Phase 1 onward. |
| `RESUMING` | **Skip Phases 1-3.** Pick up at the first item in "Still to do". Do not re-ask what they already chose. |
| `RETURNING USER` | Skip to **Phase 6**. Do not re-run the flow. |

Show the user the preflight output. It is short, and it is the honest picture of
their machine.

## Phase 1 — the manifest

Print all seven sections of `references/manifest.md` **verbatim**, tables and
source links intact.

Then, briefly:

- Nothing is installed yet.
- **`Runs code?`** is the column that matters. `md` rows are text and can only
  suggest things. `code` rows execute on their machine.
- Section 7 is not installed. Both have working free tiers with low caps, so
  neither is a paid tool; a paid plan raises a ceiling, it does not unlock one.
- Uninstalling is mostly deleting files in `~/.claude/`, but not only: it also
  means `~/.agents/.skill-lock.json`, Playwright Chromium from
  `%LOCALAPPDATA%\ms-playwright` (Windows) or `~/.cache/ms-playwright`
  (macOS/Linux), and `react-doctor` / `react-scan` from the npm global prefix
  (`npm root -g`). Nothing touches their projects.

Four lines, not four paragraphs.

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

`gh` has no npm package, so it installs per-platform. **Give them the one line for
their OS, not all four** — a beginner reading a menu of package managers they do
not have will pick the wrong one:

| OS | Command |
|---|---|
| Windows | `winget install GitHub.cli` |
| macOS | `brew install gh` |
| Debian / Ubuntu | `sudo apt install gh` |
| Anything else | [cli.github.com](https://cli.github.com) |

If `brew` or `winget` is itself missing, send them to `cli.github.com` rather than
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

**Skip any group git would block** if preflight said `LIMITED`, and say why
rather than silently dropping it.

### What each group actually is

Use these when describing the options. They name what it does and what it costs,
not just a category.

| Group | What you get |
|---|---|
| **Core skills** (11) | Design taste from a working design engineer, animation craft, marketing copy, WCAG accessibility audits, and draft terms/privacy pages. **9 are markdown and can only suggest. Two ship scripts that execute:** `a11y-audit` and `webapp-testing`, the latter driving a real browser through Playwright. |
| **BLD** (22 commands) | What you cloned this for. Also adds a hook that blocks AI image generation. |
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

### Core skills

```bash
npx -y skills add emilkowalski/skills --skill emil-design-eng      -g -a claude-code --copy
npx -y skills add emilkowalski/skills --skill animation-vocabulary -g -a claude-code --copy
npx -y skills add emilkowalski/skills --skill review-animations    -g -a claude-code --copy
npx -y skills add multica-ai/andrej-karpathy-skills --skill karpathy-guidelines -g -a claude-code --copy
npx -y skills add vercel-labs/skills --skill find-skills          -g -a claude-code --copy
npx -y skills add coreyhaines31/marketingskills --skill copywriting -g -a claude-code --copy
npx -y skills add alirezarezvani/claude-skills@a11y-audit         -g -a claude-code --copy
npx -y skills add dylantarre/animation-principles --skill framer-motion -g -a claude-code --copy
npx -y skills add anthropics/skills@webapp-testing                -g -a claude-code --copy
npx -y skills add shawnpang/startup-founder-skills@terms-of-service -g -a claude-code --copy
npx -y skills add shawnpang/startup-founder-skills@privacy-policy   -g -a claude-code --copy
```

Flags that matter:

- **`-a claude-code`**, never `-a claude` (fails: `Invalid agents: claude`). Omit
  it entirely and skills land in `~/.agents/`, where Claude Code never looks.
- **`-g`** installs globally, so every project sees them.
- **`--copy`** writes real files instead of symlinks. Windows symlinks are flaky.

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
- **On Windows, enable long paths once if ui-ux-pro-max fails to clone:**
  `git config --global core.longpaths true`, then re-run the add. The failure is
  `fatal: cannot create directory at '.claude/skills/ui-ux-pro-max/scripts/tests/fixtures/catalogs': Filename too long`.

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

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r "<resolved path>/skills/"*  ~/.claude/skills/
cp -r "<resolved path>/agents/"*  ~/.claude/agents/
```

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

Project-scoped (`<project>/.claude/skills/`) also works and wins on a name clash.
One line about it; do not turn it into a decision.

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
project's `.claude/settings.local.json`. **Merge, do not overwrite.** By this
point global settings already hold `enabledPlugins` and
`extraKnownMarketplaces`; read them, add the `hooks` key, and write back. Use an
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
`selftest ok: 3 blocked, 4 allowed` and exits 0. A hook nobody tested is a hook
nobody has.

### React tools

```bash
npm install -g react-doctor react-scan
```

`npm install -g` adds commands you can run from anywhere. It does not touch their
projects.

**Lighthouse is deliberately not installed.** `/bld-optimize-app` runs it through
`npx` so the version is never stale.

### Token monitor (only if chosen)

```bash
uv tool install claude-monitor        # or: pipx install claude-monitor
```

If `uv` is missing and unwanted, skip. The only loss is `/bld-runtime-tokens`.
Say that plainly rather than pushing.

### gstack (only if chosen) — install, then immediately prune

```bash
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
`pruned 0 gstack wrappers` right after `setup` means the matcher is stale — do
not treat it as success.**

⚠️ **`setup` un-prunes.** Re-run the prune after every `git pull` or
`/gstack-upgrade`. Tell them once; it is the easiest way for a context budget to
quietly triple.

### impeccable (only if chosen) — skill files only

```bash
rm -rf /tmp/impeccable ~/.claude/skills/impeccable
git clone --depth 1 https://github.com/pbakaus/impeccable.git /tmp/impeccable
cp -r /tmp/impeccable/.claude/skills/impeccable ~/.claude/skills/impeccable
rm -rf /tmp/impeccable
```

**Verify `~/.claude/skills/impeccable/SKILL.md` exists before moving on.**

**Both `rm -rf`s on the first line are load-bearing on a re-run**, and this skill
is built to be re-run. The trailing cleanup only happens when the block succeeds,
so an interrupted setup leaves `/tmp/impeccable` behind and the retry dies on
`destination path already exists`. Worse, `cp -r src dest` copies *into* `dest`
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
  "chose": ["core-skills", "bld", "plugins", "react-tools"],
  "declined": ["gstack", "impeccable", "mcp", "token-monitor", "agents"],
  "done": ["prereqs", "deploy", "core-skills", "plugins"],
  "completed": false,
  "completed_on": null,
  "notes": { "uv": "declined, /bld-runtime-tokens unavailable" }
}
```

- Append to `done` after each group finishes.
- `declined` is what they said no to. It is the difference between *not yet* and
  *not wanted*, and Phase 6 depends on it.
- Set `completed: true` and `completed_on` only after the restart reminder.

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

Install only what they pick, then update `declined` and `done`. Nothing else.

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

Prove it works rather than assuming: `codex exec "reply with one word: ready"`.

Four things that have actually bitten:

- **Codex refuses to run outside a git repo.** `git init` first.
- **Each `codex exec` costs ~15k input tokens before reading your prompt.** Batch
  work; many small handoffs are mostly floor.
- **Gemini exits 255 even on success.** Judge by the diff, not the exit code.
- 🚩 **Never `--dangerously-bypass-approvals-and-sandbox` (Codex) or `-y` /
  `--yolo` (Gemini).** Those drop the sandbox. BLD uses `-s workspace-write` and
  `--approval-mode auto_edit`.

Then update the delegation block in `~/.claude/CLAUDE.md` to name what they
installed, or mark it unavailable so Claude stops offering it.

## Phase 8 — the CLAUDE.md rules

Two layers:

| File | Holds | From |
|---|---|---|
| `~/.claude/CLAUDE.md` | Machine-wide: who you are, security drill, dev loop | `templates/CLAUDE.global.md` |
| `<workspace>/CLAUDE.md` | Mission, routing table, guardrails, deploy conventions | `templates/CLAUDE.workspace.md` |

**If `~/.claude/CLAUDE.md` exists, do not overwrite it.** Show a diff of what BLD
would add and let them choose. Their rules outrank yours.

Seven `<FILL IN>` blocks change behaviour. These four deserve the most attention:

1. **Who they are** — decides how much gets explained.
2. **GitHub username** — used by `/bld-util-deploy`.
3. **Delegation** — mark unavailable if they skipped Phase 7.
4. **The dev loop** — server stays up, localhost link instead of opening their
   browser, and **never push without being asked**. Worth reading, not skimming.

## Phase 9 — restart, then verify

**Skills, hooks and plugins register at startup.** Nothing installed is live
until Claude Code restarts. Say this plainly. It is the number one reason a fresh
setup looks broken.

After restarting:

```bash
<PY> "<resolved path>/skills/bld-setup/scripts/preflight.py"
```

Same `--project <project dir>` rule as Phase 0c if the install was scoped to one
project. Getting it wrong here is worse than getting it wrong in 0c: this run
happens seconds after a successful install, so a false "none installed" reads as
"setup failed" at the exact moment they are already primed to believe it.

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
- **Asking a first-timer to choose global vs project scope.** Recommend global.
- **Over-explaining.** See the voice rules at the top. Beginners need the
  unfamiliar explained, not everything.
