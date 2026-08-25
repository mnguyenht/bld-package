---
name: bld-setup
description: Turn a fresh Claude Code install into a full BLD workstation — print a complete manifest of every skill, plugin, CLI and MCP server first, get consent, then install only what is missing and write the CLAUDE.md rule layers. Use when the user says /bld-setup, "set up BLD", "install the BLD toolkit", "make my Claude like yours", or has just cloned bld-package and wants it working. Idempotent, and never installs anything it did not list first.
---

# bld-setup — the manifest comes first, always

This skill installs other people's software onto someone's machine. That is a
trust transaction, so it runs in one fixed order and the order is not negotiable:

> **Show the whole list → get a yes → install → verify.**

**Never install anything that was not in the printed table.** If you find yourself
reaching for a package mid-install that the manifest doesn't name, stop and ask.

## Phase 0 — print the manifest (FIRST OUTPUT, no exceptions)

Read `references/manifest.md` and **print all seven sections verbatim** as your
first response. Not a summary, not "here's roughly what we'll install" — the
actual tables, with the GitHub column intact, so the user can click through and
read the source of anything before it lands.

Then say these four things in your own words:

1. **Nothing is installed yet.** This is a list, not a report.
2. **Which rows execute code** vs. which are pure markdown. Markdown skills can
   only ever suggest text at you. Anything marked `code` gets to run on their
   machine, and they should read it first.
3. **§7 is not installed by default.** It exists so they know those tools are
   real, optional, and cost money. Phase 3.5 offers to help set one up if they
   want `/bld-runtime-agents`.
4. **How to back out:** every install is a file in `~/.claude/` or a global
   package. Nothing touches their projects. `/bld-setup remove` is not a thing —
   deleting the folder is.

Only after that, ask what to install.

## Phase 1 — survey before asking

Run this first so the question in Phase 2 is about **what's missing**, not what
they already have. Nobody wants to be asked to install something twice.

```bash
echo "== plugins =="        ; cat ~/.claude/plugins/installed_plugins.json 2>/dev/null | grep -o '"[a-z-]*@[a-z-]*"' | sort -u
echo "== global skills =="  ; ls -1 ~/.claude/skills/ 2>/dev/null
echo "== CLIs =="           ; for c in react-doctor react-scan claude-monitor vercel gh node npm python uv; do printf "%-16s" "$c"; command -v $c 2>/dev/null || echo "MISSING"; done
echo "== MCP =="            ; pip show jcodemunch-mcp 2>/dev/null | head -2
echo "== leaks =="          ; ls ~/.claude/CLAUDE.md .mcp.json 2>/dev/null
```

Two things to look for beyond presence:

- **An existing `~/.claude/CLAUDE.md`.** If they have one, it is theirs and it has
  their rules in it. See Phase 4 — you merge, you never overwrite.
- **An existing `.mcp.json`** in the project. BLD's whole MCP posture is that this
  file does not exist. If it does, say so and ask before removing anything; it may
  be there for a reason that has nothing to do with BLD.

## Phase 2 — ask, in groups, once

One `AskUserQuestion`, multi-select, with the missing items only. Group them the
way the manifest does, because the groups have genuinely different trust profiles:

| Group | Default | Why |
|---|---|---|
| Core skills (§2, markdown) | ✅ recommended | Free, offline, can't do anything but talk. |
| BLD's own skills + hook + CLAUDE.md (§6) | ✅ recommended | This is the actual point of the package. |
| Plugins (§1) | ✅ recommended | ponytail and ui-ux-pro-max are load-bearing for `/bld-sprint-init` and `/bld-sprint-refine`. |
| CLIs (§4) | ask | Global installs. `react-doctor` and `lighthouse` power two BLD skills; the rest are situational. |
| gstack + impeccable (§3) | ask | Large, opinionated, and both ship code. Fine to skip and add later. |
| MCP servers (§5) | ask | `context-mode` in particular runs shell with their logged-in CLIs. |

Fire a `PushNotification` alongside the question — this is a blocking ask and they
may have walked away while the survey ran.

## Phase 3 — install what they picked

Order matters: skills and plugins before CLIs, because the CLIs are the slow part
and a failure there shouldn't block the cheap stuff.

**Explain every approval-required command before running it** — one sentence on
what it does, what the non-obvious flags mean, and whether it modifies anything.
That rule is in the CLAUDE.md this skill is about to install; apply it while
installing it.

### Global skills

```bash
npx -y skills add emilkowalski/skill --skill emil-design-eng     -g -a claude-code --copy
npx -y skills add emilkowalski/skill --skill animation-vocabulary -g -a claude-code --copy
npx -y skills add emilkowalski/skill --skill review-animations   -g -a claude-code --copy
npx -y skills add multica-ai/andrej-karpathy-skills --skill karpathy-guidelines -g -a claude-code --copy
npx -y skills add vercel-labs/skills --skill find-skills         -g -a claude-code --copy
npx -y skills add coreyhaines31/marketingskills --skill copywriting -g -a claude-code --copy
npx -y skills add alirezarezvani/claude-skills@a11y-audit        -g -a claude-code --copy
npx -y skills add dylantarre/animation-principles --skill framer-motion -g -a claude-code --copy
npx -y skills add anthropics/skills@webapp-testing               -g -a claude-code --copy
npx -y skills add shawnpang/startup-founder-skills@terms-of-service -g -a claude-code --copy
npx -y skills add shawnpang/startup-founder-skills@privacy-policy   -g -a claude-code --copy
```

Three flags that are not optional and one that is a trap:

- **`-a claude-code`**, not `-a claude`. `claude` fails with `Invalid agents: claude`.
  Without the flag entirely, skills land in `~/.agents/` and Claude Code never
  reads them.
- **`-g`** = global (`~/.claude/skills/`), so every project sees them.
- **`--copy`** = real files instead of symlinks. Windows symlinks are flaky enough
  that this is worth the disk.
- **`-y`** stops npx pausing to confirm the download.

Run them one at a time, not chained with `&&` — one 404 shouldn't kill the batch.

### Plugins

Plugins are normally added with the interactive `/plugin` command, which Claude
cannot run. Write the config instead and let startup do the download. Merge into
`~/.claude/settings.json` — **read it first, never clobber it**:

```json
{
  "enabledPlugins": {
    "ponytail@ponytail": true,
    "ui-ux-pro-max@ui-ux-pro-max-skill": true,
    "claude-code-setup@claude-plugins-official": true
  },
  "extraKnownMarketplaces": {
    "ponytail":              { "source": { "source": "github", "repo": "DietrichGebert/ponytail" } },
    "ui-ux-pro-max-skill":   { "source": { "source": "github", "repo": "nextlevelbuilder/ui-ux-pro-max-skill" } }
  }
}
```

`claude-plugins-official` is a built-in marketplace and needs no entry. If the
plugins don't appear after restart, fall back: tell the user to run
`/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail`
themselves, in an interactive terminal.

### gstack — install then immediately prune

```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
bash ~/.claude/skills/gstack/setup
```

`setup` generates **54** skill wrappers in `~/.claude/skills/`. BLD keeps six. The
other 48 are iOS, paid-provider, browser, deploy, design and team-process skills
that duplicate what BLD already does — and they cost context on every single
session. Write the prune script and run it:

```bash
cat > ~/.claude/skills/gstack-prune.sh <<'SH'
#!/usr/bin/env bash
# Deletes generated gstack wrappers in ~/.claude/skills. Idempotent.
# The gstack repo itself is never touched — re-run `setup` to undo this.
keep="gstack _gstack-command gstack-spec gstack-investigate gstack-cso gstack-review gstack-careful gstack-upgrade"
for d in ~/.claude/skills/gstack-*; do
  n=$(basename "$d")
  case " $keep " in *" $n "*) continue ;; esac
  [ -d "$d" ] && rm -rf "$d" && echo "pruned $n"
done
SH
bash ~/.claude/skills/gstack-prune.sh
```

**Re-run the prune after every `git pull` or `/gstack-upgrade`.** On Windows the
wrappers are file copies, not symlinks, so `setup` has to be re-run to refresh
them — and `setup` un-prunes. Tell the user this; it is the single easiest way for
their context budget to quietly triple.

Context cost after prune: ~160 tokens, down from ~1.5k. Note the *invoke* cost is
the heavy one — `gstack-spec`'s body is ~32k tokens, so it is reached for
deliberately, not reflexively.

### impeccable — skill files only

```bash
git clone --depth 1 https://github.com/pbakaus/impeccable.git /tmp/impeccable
cp -r /tmp/impeccable/skills/impeccable ~/.claude/skills/impeccable
rm -rf /tmp/impeccable
```

Check the repo layout before copying; if `skills/impeccable/` isn't where the
`SKILL.md` lives, find it and adjust rather than guessing.

**Do not run `npx impeccable install` or `npx impeccable update`.** Both wire
hooks into settings. Restate the `/impeccable live` warning from the manifest
when this one finishes — it is the highest-consequence item in the whole set.

### CLIs

```bash
npm install -g react-doctor react-scan vercel
uv tool install claude-monitor        # or: pipx install claude-monitor
pip install jcodemunch-mcp            # only if they took the MCP group
```

`lighthouse` is deliberately absent — `/bld-optimize-app` runs it through `npx`
so the version is never stale. `gh` has no npm package; point them at
https://cli.github.com or `winget install GitHub.cli` and let them do it.

### BLD's own files

```bash
BLD=<path to the cloned bld-package>
cp -r "$BLD/skills/"*      ~/.claude/skills/          # or <project>/.claude/skills/
cp -r "$BLD/agents/"*      ~/.claude/agents/
mkdir -p <project>/.claude/hooks && cp "$BLD/hooks/block-image-skills.py" $_
```

**Ask where they want the `bld-*` skills.** Global (`~/.claude/skills/`) makes
them available everywhere; project-level (`<project>/.claude/skills/`) keeps them
scoped to one workspace and is how the original machine runs them. Project-level
wins on a name clash.

The hook needs registering in the project's `.claude/settings.local.json`:

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Skill", "hooks": [
  { "type": "command", "command": "python \"<abs path>/.claude/hooks/block-image-skills.py\"" } ] } ] } }
```

Use an **absolute path** — the hook is invoked with an unpredictable cwd.

## Phase 3.5 — external coding agents (optional, and they cost money)

`/bld-runtime-agents` is the one BLD skill that needs something BLD cannot give
you: an account with another AI company. Everything else in the package is free.
**Offer this, do not push it.** Skipping it costs the user exactly one skill.

Ask first, in one line: *"`/bld-runtime-agents` hands bulky work to Codex or
Gemini so it does not spend your Claude window. Want help setting one up? It
needs a paid ChatGPT plan for Codex, or a Google account for Gemini's free
tier."*

If they say no, say which skill will not work and move on.

### The rule that outranks convenience here

> **Claude never touches the credentials.** Not the password, not the API key,
> not the browser login.

Print the commands. The user runs them, in their own terminal, and logs in
themselves. If a login flow asks for anything secret, hand it back to them
rather than helping past it. This is not a formality: these logins hold a paid
account, and an agent typing them is an agent that has seen them.

### Codex — the default executor

Needs a **paid ChatGPT plan**. There is no useful free tier, so if they do not
already pay for ChatGPT, Gemini is the better suggestion.

```bash
# Install: check the repo for the current method on their OS.
#   https://github.com/openai/codex
npm install -g @openai/codex        # or the platform installer

codex login                          # opens a browser; THE USER signs in
codex --version                      # verify it landed
```

Then prove it works end to end before claiming it does, because a CLI that
installs fine and cannot authenticate looks identical until you run it:

```bash
codex exec "reply with the single word: ready"
```

Three things to tell them once, because each has bitten:

- **Codex refuses to run outside a git repo** ("Not inside a trusted directory").
  `git init` first. `--skip-git-repo-check` exists but defeats the review step
  that makes delegation safe.
- **Every run costs roughly 15k input tokens before it reads your prompt** —
  system prompt plus repo context. Batch related work into one run; a dozen
  micro-handoffs are mostly floor.
- 🚩 **Never `--dangerously-bypass-approvals-and-sandbox`.** That is the YOLO
  switch and it drops the sandbox entirely. `-s workspace-write` is the flag
  BLD uses.

### Gemini — the fallback

Free tier, and the better first suggestion for anyone not already paying OpenAI.

```bash
npm install -g @google/gemini-cli
gemini                               # first run prompts for auth; THE USER signs in
```

- Sign in with a **Google account** rather than pasting an API key. The
  API-key free tier is roughly **20 requests a day** and runs dry after about
  one handoff; account auth raises it substantially.
- 🚩 **Never `-y` / `--yolo`.** `--approval-mode auto_edit` approves edit tools
  only, which is what BLD uses.
- Quirk worth pre-empting: **gemini exits 255 even on success.** Judge by the
  response and the diff, not the exit code, or you will chase a failure that
  did not happen.

### After either one

Update the delegation block in `~/.claude/CLAUDE.md` to name the executor they
actually installed and the account it uses. If they installed neither, say so in
that file explicitly, so Claude stops offering delegation it cannot perform.

## Phase 4 — the CLAUDE.md layers (merge, never overwrite)

BLD is three layers, each holding only what is true at that level:

| File | Holds | From |
|---|---|---|
| `~/.claude/CLAUDE.md` | Machine-wide: who you are, security drill, install rules, dev loop, delegation | `templates/CLAUDE.global.md` |
| `<workspace>/CLAUDE.md` | Mission, skill routing table, guardrails, deploy conventions | `templates/CLAUDE.workspace.md` |
| `<app>/CLAUDE.md` | Per-app purpose, stack, status. ~30 lines. | `/bld-sprint-init` writes it |

**If `~/.claude/CLAUDE.md` already exists, do not overwrite it.** Show them a diff
of what BLD would add, section by section, and let them choose. Their existing
file has their rules in it and those rules outrank yours.

Both templates ship with the personal details stripped and marked `<FILL IN>`.
Walk the user through the ones that actually change behaviour:

- **Who you're working with** — experience level drives how much gets explained.
- **Deploy target** — GitHub account, whether repos are private, Vercel or not.
- **Delegation** — the `/bld-runtime-agents` block assumes a Codex login. No Codex? Say so
  in the file, so Claude stops offering it.
- **The dev-loop rules** — never auto-push, always hand back a localhost link,
  keep the server running. These are the ones that change day-to-day behaviour
  most, so make sure they're actually wanted rather than pasted past.

## Phase 5 — restart, then verify

**Skills, hooks and plugins register at startup.** Nothing installed above is live
until Claude Code restarts. Say this plainly; it is the number one reason a fresh
setup looks broken.

After the restart, verify rather than assume:

```bash
ls -1 ~/.claude/skills/ | wc -l
react-doctor --version; claude-monitor --version; vercel --version
```

Then have them type `/bld-` and confirm the skills autocomplete. A skill that is
present on disk but absent from the picker means the frontmatter didn't parse —
check `name:` and `description:` are both present and unquoted-safe.

Close with what got installed, what got skipped and why, and the one-line
reminder that `/bld-sprint-init` is where a first app starts.

## Pitfalls

- **Installing before printing the manifest.** The whole skill exists to not do
  this. If the user says "just install everything", still print the table first —
  it takes one message and it is the only chance they get to object.
- **Overwriting an existing `~/.claude/CLAUDE.md`.** Merge or ask. Always.
- **Claiming success before restart.** Verify after, not before.
- **Chaining installs with `&&`.** One dead repo kills the rest of the batch.
- **Adding MCP servers to `.mcp.json`** because it's easier than the on-demand
  runner. That trades the entire trust model for a few saved keystrokes.
- **Forgetting the gstack re-prune** after an upgrade.
- **Assuming the skill-add flags.** `-a claude` is wrong, `-a claude-code` is right,
  and no flag at all silently installs somewhere Claude Code never looks.
