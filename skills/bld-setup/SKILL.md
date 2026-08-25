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
python --version || python3 --version || py --version
```

If none work, check the rest by hand so they only install once:

```bash
node --version; npm --version; git --version
```

Then give them the fix and stop:

> **Python is missing.** BLD's setup check and two of its helper scripts need it.
> Get it from [python.org/downloads](https://python.org/downloads), and **tick
> "Add python.exe to PATH" on the first screen** — it is off by default and
> everything fails confusingly without it. Restart your terminal, then run
> `/bld-setup` again.

Note which of `python` / `python3` / `py` worked, and use that name from then on.

### 0c. Run preflight

Read-only: it installs nothing.

It prints prerequisites, deploy tooling, what BLD already installed, and a
**verdict**. Route on the verdict:

| Verdict | Do |
|---|---|
| `BLOCKED` | Stop. Only node and npm are truly required. Give the links it printed. |
| `LIMITED` | **Keep going.** git is missing, which removes only deploy, gstack and impeccable. Say what is unavailable, do not treat it as a failure, and skip those groups in Phase 3. |
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
- Section 7 is not installed. Those cost money.
- Uninstalling is deleting files in `~/.claude/`. Nothing touches their projects.

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

Ask before the main install, because these need **human logins** nobody else can
do, and they are the slow part:

> *"Do you want `/bld-util-deploy`? It puts an app in a private GitHub repo and
> on a live URL, redeploying every time you push. It needs a GitHub account and a
> Vercel account, and you do both logins yourself. About five minutes. Skip it
> and everything else still works."*

If yes, and preflight showed them missing:

```bash
npm install -g vercel
# gh has no npm package: cli.github.com, or `winget install GitHub.cli`
```

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
| **Core skills** (11) | Design taste from a working design engineer, animation craft, marketing copy, WCAG accessibility audits, and draft terms/privacy pages. All markdown, so they can only suggest, never execute. |
| **BLD** (21 commands) | What you cloned this for. Also adds a hook that blocks AI image generation. |
| **Plugins** (3) | **ponytail** stops Claude over-building things you did not ask for. **ui-ux-pro-max** is the design engine `/bld-sprint-init` uses for palettes and type. Both run code. ui-ux-pro-max also ships image generation, which BLD blocks. |
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
npx -y skills add emilkowalski/skill --skill emil-design-eng      -g -a claude-code --copy
npx -y skills add emilkowalski/skill --skill animation-vocabulary -g -a claude-code --copy
npx -y skills add emilkowalski/skill --skill review-animations    -g -a claude-code --copy
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

Plugins normally install through the interactive `/plugin` command, which Claude
cannot run. Write the config and let startup fetch them. **Read
`~/.claude/settings.json` first and merge. Never overwrite it.**

```json
{
  "enabledPlugins": {
    "ponytail@ponytail": true,
    "ui-ux-pro-max@ui-ux-pro-max-skill": true,
    "claude-code-setup@claude-plugins-official": true
  },
  "extraKnownMarketplaces": {
    "ponytail":            { "source": { "source": "github", "repo": "DietrichGebert/ponytail" } },
    "ui-ux-pro-max-skill": { "source": { "source": "github", "repo": "nextlevelbuilder/ui-ux-pro-max-skill" } }
  }
}
```

`claude-plugins-official` is built in and needs no marketplace entry. If plugins
do not appear after restart, have them run
`/plugin marketplace add DietrichGebert/ponytail` themselves.

### BLD itself

**Recommend global** unless they already have a project in mind. A first-timer
has no project yet, so asking them to choose is asking about something they
cannot evaluate.

```bash
cp -r <resolved path>/skills/*  ~/.claude/skills/
cp -r <resolved path>/agents/*  ~/.claude/agents/
```

Run this through the Bash tool, which has `cp` on every platform. If the user
runs it themselves in PowerShell, `cp` is an alias for `Copy-Item` and needs
`-Recurse` instead of `-r`. Give them that form rather than watching it fail.

Project-scoped (`<project>/.claude/skills/`) also works and wins on a name clash.
One line about it; do not turn it into a decision.

The hook needs registering in the project's `.claude/settings.local.json`, with
an **absolute path** (it runs with an unpredictable working directory):

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Skill", "hooks": [
  { "type": "command", "command": "python \"<abs path>/hooks/block-image-skills.py\"" } ] } ] } }
```

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
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
bash ~/.claude/skills/gstack/setup
```

`setup` generates **54** skill wrappers. BLD keeps six. The other 48 are iOS,
paid-provider, browser, deploy and team-process skills that duplicate what BLD
does, and every one costs context on every session.

```bash
cat > ~/.claude/skills/gstack-prune.sh <<'SH'
#!/usr/bin/env bash
# Deletes generated gstack wrappers in ~/.claude/skills. Idempotent.
# The gstack repo is never touched, so re-running `setup` undoes this.
keep="gstack _gstack-command gstack-spec gstack-investigate gstack-cso gstack-review gstack-careful gstack-upgrade"
for d in ~/.claude/skills/gstack-*; do
  n=$(basename "$d")
  case " $keep " in *" $n "*) continue ;; esac
  [ -d "$d" ] && rm -rf "$d" && echo "pruned $n"
done
SH
bash ~/.claude/skills/gstack-prune.sh
```

⚠️ **`setup` un-prunes.** Re-run the prune after every `git pull` or
`/gstack-upgrade`. Tell them once; it is the easiest way for a context budget to
quietly triple.

### impeccable (only if chosen) — skill files only

```bash
git clone --depth 1 https://github.com/pbakaus/impeccable.git /tmp/impeccable
cp -r /tmp/impeccable/skills/impeccable ~/.claude/skills/impeccable
rm -rf /tmp/impeccable
```

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

## Phase 7 — external coding agents (optional, cost money)

`/bld-runtime-agents` is the one BLD skill needing an account elsewhere.
**Offer, do not push.** Skipping costs exactly one skill.

> **Claude never touches the credentials.** Print the commands; the user runs
> them and logs in. If a flow asks for anything secret, hand it back.

**Codex** needs a paid ChatGPT plan. **Gemini** has a free tier, so suggest it
first to anyone not already paying OpenAI.

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

Four `<FILL IN>` blocks change behaviour and deserve their attention:

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
python <resolved path>/skills/bld-setup/scripts/preflight.py
```

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
