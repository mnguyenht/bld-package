# Manual install (macOS and Linux)

`/bld-setup` is the guided installer. It works by asking questions, checking your
machine, and recording what it did so an interrupted run can resume.

**It has been executed and verified on Windows. It has not been executed on
macOS.** The commands below are the same ones it runs, written out linearly with
macOS and Linux spellings, so you can install BLD by hand and skip the guided
flow entirely.

Everything ends up in the same place. The skills behave identically once
installed — nothing in BLD itself is platform-specific.

**Prefer `/bld-setup` if you are on Windows.** Prefer this page if you are not,
or if you would rather read a list than answer questions.

---

## Before you start

| Need | Check | If missing |
|---|---|---|
| Claude Code | `claude --version` | [claude.com/claude-code](https://claude.com/claude-code) |
| node 18+ | `node --version` | [nodejs.org](https://nodejs.org), or `brew install node` |
| npm | `npm --version` | ships with node |
| git | `git --version` | `brew install git`, or `sudo apt install git` |
| python3 | `python3 --version` | `brew install python3`, or `sudo apt install python3` |

Only node and npm are truly required. Without git you lose deploy, gstack and
impeccable; everything else installs fine.

**If `npm install -g` fails with `EACCES`**, your node puts its global packages
somewhere you do not own. This hits the nodejs.org `.pkg` on macOS and
`apt install nodejs` on Debian and Ubuntu. Homebrew, nvm, Volta and fnm do not.
Fix it with a user-owned prefix rather than `sudo`, which leaves root-owned files
in `~/.npm` that break later installs:

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export NPM_CONFIG_PREFIX=~/.npm-global' >> ~/.zshrc   # or ~/.bashrc
echo 'export PATH=~/.npm-global/bin:$PATH'    >> ~/.zshrc
export NPM_CONFIG_PREFIX=~/.npm-global; export PATH=~/.npm-global/bin:$PATH
```

**The `NPM_CONFIG_PREFIX` line is not redundant.** On Debian and Ubuntu the
packaged npm ships a builtin config pinning `prefix=/usr/local` that beats
`npm config set`, so the usual remedy is silently ignored on the one platform
that needs it. Measured on Ubuntu 26.04, npm 9.2.0.

Check it took with `npm prefix -g`, not `npm config get prefix`. Those two
disagree in exactly this case, and only the first says where packages really go.

---

## What you can install

Pick what you want. Each group is independent — skip any of them and the rest
still work. The full trust manifest, with a source link and a runs-code column
for every item, is at
[`skills/bld-setup/references/manifest.md`](skills/bld-setup/references/manifest.md).
Read it before installing anything you have not vetted.

| Group | What you get | Recommended |
|---|---|---|
| **BLD** | The 23 `/bld-*` commands and the executor agent | Yes |
| **Plugins** | ponytail, ui-ux-pro-max, claude-code-setup | Yes |
| **Core skills** | 11 standalone skills: design, animation, copy, a11y, legal | Yes |
| **React tools** | react-doctor and react-scan, for `/bld-optimize-react` | Yes |
| **Deploy** | `gh` + `vercel`, for `/bld-util-deploy` | If you plan to ship |
| **Code search** | jcodemunch, for cheaper exploration of large codebases | Later |
| **Token monitor** | claude-monitor, for `/bld-runtime-tokens` | Later |
| **gstack + impeccable** | Two large opinionated suites | Later |

Steps 1 and 2 are the minimum that gives you a working BLD.

---

## 1. BLD itself

**You do not have to take all 23 commands.** `skills/bld-setup/references/skills.md`
lists every one with what it does and what it needs; copy only the folders you
want, plus `bld-setup` and the agent. Every installed skill's description is
loaded into Claude Code at startup, so a shorter list is a real saving.

From inside the cloned `bld-package` directory:

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r skills/*  ~/.claude/skills/
cp -r agents/*  ~/.claude/agents/
```

`mkdir -p` is not optional — a fresh Claude Code install has no `agents/`
directory and `cp` into a missing target fails.

---

## 2. Plugins

```bash
claude plugin marketplace add https://github.com/DietrichGebert/ponytail.git
claude plugin marketplace add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
claude plugin marketplace add https://github.com/anthropics/claude-plugins-official.git
claude plugin install ponytail@ponytail
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
claude plugin install claude-code-setup@claude-plugins-official
claude plugin list
```

Confirm all three say `enabled`. Two notes:

- **Pass the full HTTPS URL, not `owner/repo`.** The short form resolves to SSH
  and fails on a machine with no GitHub SSH key.
- **`marketplace add` exits 0 even when the clone fails.** Judge it by the
  `✔ Successfully added marketplace` line or by `claude plugin list`.

---

## 3. Core skills

Eleven standalone skills. Run them one at a time — chaining with `&&` lets one
dead repo kill the batch.

```bash
npx -y skills add emilkowalski/skills --skill emil-design-eng      -g -a claude-code --copy -y
npx -y skills add emilkowalski/skills --skill animation-vocabulary -g -a claude-code --copy -y
npx -y skills add emilkowalski/skills --skill review-animations    -g -a claude-code --copy -y
npx -y skills add multica-ai/andrej-karpathy-skills --skill karpathy-guidelines -g -a claude-code --copy -y
npx -y skills add vercel-labs/skills --skill find-skills           -g -a claude-code --copy -y
npx -y skills add coreyhaines31/marketingskills --skill copywriting -g -a claude-code --copy -y
npx -y skills add alirezarezvani/claude-skills@a11y-audit          -g -a claude-code --copy -y
npx -y skills add dylantarre/animation-principles --skill framer-motion -g -a claude-code --copy -y
npx -y skills add anthropics/skills@webapp-testing                 -g -a claude-code --copy -y
npx -y skills add shawnpang/startup-founder-skills@terms-of-service -g -a claude-code --copy -y
npx -y skills add shawnpang/startup-founder-skills@privacy-policy   -g -a claude-code --copy -y
```

**The trailing `-y` is a different flag from the leading one**, and on Linux it
is load-bearing. `npx -y` auto-confirms npx's own download; the `skills` CLI then
asks its own `Proceed with installation?`. With no terminal to answer it, Linux
exits 0 having installed nothing. Verify by count, never by exit code:

```bash
ls ~/.claude/skills | wc -l
```

That should have gained 11 entries.

---

## 4. React tools

```bash
npm install -g react-doctor react-scan
```

Lighthouse is deliberately not installed — `/bld-optimize-app` runs it through
`npx` so the version is never stale.

---

## 5. The optional extras

**Code search.** Only one of the three servers installs anything; the other two
launch on demand through `npx`.

```bash
python3 -m pip install jcodemunch-mcp
```

If that answers `externally-managed-environment` or `No module named pip`, your
Python belongs to the OS or to Homebrew. Do not force it with
`--break-system-packages`. Use pipx or uv instead:

```bash
pipx install jcodemunch-mcp     # or: uv tool install jcodemunch-mcp
```

**On a minimal image none of the three exists.** Measured on Ubuntu 26.04: no
`pip`, no `pipx`, no `uv`. Get one first, or skip the group, which costs nothing
and can be added any time:

```bash
sudo apt install pipx           # or see astral.sh/uv
```

**Token monitor.** Powers `/bld-runtime-tokens` and nothing else.

```bash
uv tool install claude-monitor     # or: pipx install claude-monitor
```

**gstack.** Five of its 54 skills, and **not** its own `setup`: that installer
pulls in the whole suite, about 700 MB of Playwright Chromium, and a `Stop` hook
in your `settings.json`. The five ship pre-built in the repo, so copying them is
the whole install. The clone has to stay at `~/.claude/skills/gstack`, because
those skills call helper scripts inside it.

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
for s in spec investigate cso review careful; do
  rm -rf ~/.claude/skills/gstack-$s
  cp -r ~/.claude/skills/gstack/$s ~/.claude/skills/gstack-$s
done
~/.claude/skills/gstack/bin/gstack-config set update_check false
```

The last line switches off gstack's upgrade prompt, which would run `setup`.
To update gstack later, `git -C ~/.claude/skills/gstack pull --ff-only` and run
the loop again. Telemetry is off until a gstack skill asks you and you say yes.

**impeccable.** Skill files only.

```bash
rm -rf ~/.claude/skills/impeccable
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/pbakaus/impeccable.git "$tmp/impeccable"
cp -r "$tmp/impeccable/.claude/skills/impeccable" ~/.claude/skills/impeccable
rm -rf "$tmp"
```

The `rm -rf` on the first line is load-bearing. `cp -r src dest` copies *into*
`dest` when it already exists, so a second run produces
`~/.claude/skills/impeccable/impeccable/SKILL.md`, which never registers as a
skill and reports no error.

Never run `npx impeccable install` or `update` — both wire hooks into your
settings. Never run `/impeccable live`, which forwards your API key to a
third-party backend. Every other impeccable command is fine.

---

## 6. Deploy and coding agents (optional)

Needed only for `/bld-util-deploy`, which puts an app in a private GitHub repo
and on a live URL.

```bash
npm install -g vercel
brew install gh          # Debian/Ubuntu: see the note below
```

**`apt install gh` fails on a lot of Debian and Ubuntu machines.** `gh` only
reached Ubuntu's repos in 23.04 and is not in Debian's at all, so on 22.04 LTS it
answers `Unable to locate package gh`. Get it from
[cli.github.com](https://cli.github.com) rather than adding GitHub's apt
repository mid-install.

Then sign in. Both open a browser, and both are things only you can do:

```bash
gh auth login
vercel login
```

An installed CLI is not a signed-in CLI, and `--version` passes on both.

---

**Coding agents.** `/bld-runtime-agents` hands bulky work to Codex or Gemini
instead of your Claude usage. Free tiers, low caps, and you sign in yourself.

```bash
npm install -g @openai/codex        # then: codex login
npm install -g @google/gemini-cli   # then: gemini, and follow the prompt
```

Codex refuses to run outside a git repo, so prove it from inside one:
`codex exec "reply with one word: ready"`.

## 7. The rule files (optional)

BLD ships two opinionated CLAUDE.md files. They are an offer, not part of the
install, and every `/bld-*` command works without them. What they add is the
defaults: the dev loop, deploy conventions, and how much gets explained to you.

| File | Holds |
|---|---|
| `templates/CLAUDE.global.md` → `~/.claude/CLAUDE.md` | Machine-wide: who you are, security drill, dev loop |
| `templates/CLAUDE.workspace.md` → `<your workspace>/CLAUDE.md` | Mission, routing table, deploy conventions |

**A file already at either path is yours and outranks anything BLD ships.** Move
it aside first:

```bash
[ -e ~/.claude/CLAUDE.md ] && mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.old.md
cp templates/CLAUDE.global.md ~/.claude/CLAUDE.md
```

Both templates carry `<FILL IN>` blocks — **seven in the global file, five in the
workspace one.** Fill in the file you took. The four that matter most are who you
are, your GitHub username, whether you have Codex or Gemini, and the dev loop.

---

## 8. Restart, then check

**Skills, hooks and plugins register at startup.** Nothing you installed is live
until Claude Code restarts. This is the single most common reason a fresh setup
looks broken.

There is a second restart too: a CLI installed into a directory that was not
already on `PATH` stays invisible to your current shell. That hits
`claude-monitor` and `jcodemunch-mcp`, which uv puts in `~/.local/bin`. If a tool
reports missing seconds after installing cleanly, check `ls ~/.local/bin` before
assuming the install failed.

After restarting:

```bash
python3 skills/bld-setup/scripts/preflight.py
```

That prints what is present, what is missing, and a verdict. It installs nothing.
Then type `/bld-` in Claude Code and confirm the commands appear. A skill on disk
but missing from that list means its frontmatter did not parse.

---

## What you gave up

Installing by hand skips the state file at `~/.claude/.bld-setup.json`, which is
what lets `/bld-setup` resume an interrupted run and tell you later what you
skipped. Nothing depends on it — preflight reads your disk directly and reports
honestly either way.

If you want it, run `/bld-setup` once after installing. It reads the disk, sees
what is already there, and writes the record without reinstalling anything.

---

## Where to start

`/bld-sprint-planning` is where a first app starts. It interviews the idea,
cuts it to something shippable, and hands off to `/bld-sprint-init`.
