---
name: bld-settings-block-image-generation
description: The one switch for BLD's AI image-generation block, which is on by default. Use it to turn the block off, put it back, or check where it stands. Also for "allow image generation", "no AI images", "is the image hook on".
---

# bld-settings-block-image-generation

One PreToolUse hook that refuses AI image generation, and nothing else.

**It is on already.** `/bld-setup` copies this hook and registers it alongside
BLD's own skills, so blocking is the installed state rather than something to
remember. **This command is the off switch**, and the only one: the policy is not
restated in any skill, template or rule file, so there is nothing else to find
and nothing to keep in sync.

`off` unregisters it · `on` puts it back · `status` reports where it stands.
With no argument, run `status`.

**It fires silently, by design.** Nothing warns the model in advance; the call is
simply refused, with a message naming what to do instead. That costs one wasted
attempt in the rare session that tries, and buys a policy that cannot be
forgotten, edited around, or left behind when a skill is rewritten.

## What it catches

The hook is `scripts/block-image-generation.py`. Three surfaces, because the
first version of this only watched one:

| Surface | Matched on | Example it refuses |
|---|---|---|
| **Skill** | The namespaced skill name | `ui-ux-pro-max:design`, `ui-ux-pro-max:banner-design` |
| **Bash** | A generator path or endpoint **in a segment something actually runs** | a `python` call on the plugin's generator script, a `curl -X POST` to an image endpoint |
| **MCP and other tools** | The tool's own name | `mcp__images__generate_image`, `text_to_image`, `imagegen` |

**Bash is the surface that matters most**, and the one the old hook missed:
ui-ux-pro-max reaches the image models from a Python script, so a hook watching
only the Skill tool blocks the front door and leaves the side door open.

## What it deliberately does not catch

This is the half that keeps it from being intrusive. Say it when someone asks
why the block did not fire:

- **Claude Code's own `design` skill.** It lays out HTML artboards and generates
  no images. A plugin skill can only be invoked as `plugin:skill`, so a bare
  `design` is always the built-in one.
- **Anything that reads, uploads, screenshots, resizes, converts or crops an
  image.** Those all have "image" in the name and none of them generate.
  `sharp`, ImageMagick and ffmpeg are transforms on an asset that already
  exists, which is the workflow this policy protects.
- **Every tool but `Skill`, `Bash` and MCP calls.** The hook is registered
  against those names only, so `Read`, `Edit`, `Write`, `Grep` and `Glob` - the
  ones a session calls hundreds of times - never pay for it.
- **A model that draws with code.** SVG, canvas and CSS are not image
  generation, and nothing here looks at them.
- **Naming a generator without running it.** Reading the script, grepping for a
  model name, `git log` on that path, echoing a payload that quotes one: all
  allowed. The Bash check splits a command on `|`, `&&` and `;` and judges only
  segments that begin with an interpreter or fetcher (`python`, `node`, `npx`,
  `curl`, `sh`, ...). Matching the raw string blocked *inspecting* a generator,
  which is backwards when the house rule is to read the source of anything that
  executes. One exception: an interpreter reading from a heredoc or `-c` can run
  whatever is written further down, so there the whole command is searched.

## `on` — install and register

**Explain it in one line before running anything**: a hook is a script Claude
Code runs automatically before a tool call, and this one exits non-zero to
refuse image generation.

**1. Copy the hook out of the package.** `<PY>` is whichever of `python3`,
`python` or `py` works on this machine, and `<resolved path>` is the package
folder. Copy rather than register it in place: a hook pointing into a cloned
folder breaks silently the day that folder is deleted, and nothing reports it.

```bash
mkdir -p ~/.claude/hooks
cp "<resolved path>/skills/bld-settings-block-image-generation/scripts/block-image-generation.py" ~/.claude/hooks/
<PY> ~/.claude/hooks/block-image-generation.py --selftest
```

The selftest must print `selftest ok: 11 blocked, 15 allowed`. **A hook that
fails silently looks exactly like a working one**, so this is the only proof
that the matcher still does what this page claims.

**2. Register it in `~/.claude/settings.json`.** **Read the file first and merge
into it. Never overwrite it** - it holds their plugins, their permissions and
any hooks they already run. If it does not exist, create it with just this key.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill|Bash|mcp__.*",
        "hooks": [
          { "type": "command", "command": "<PY> \"<home>/.claude/hooks/block-image-generation.py\"" }
        ]
      }
    ]
  }
}
```

Three details in that block, each of which has its own failure:

- **`matcher` is a regex over tool names.** `Skill|Bash|mcp__.*` is the whole
  attack surface and skips the high-frequency file tools. `*` would work and
  would also spawn Python on every `Read`.
- **Use an absolute path, and expand `~` yourself.** The hook command is not run
  through a shell, so a literal `~` is passed as a directory name and the hook
  never runs.
- **`<PY>` is not optional.** Substitute the interpreter that actually exists. A
  hook whose command is `python` on a machine with only `python3` is registered,
  silent, and permanently not blocking anything.

**3. Say it needs a restart.** Hooks register at startup. Until Claude Code
restarts, the block is installed and inert.

**If a hook blocking image generation is already registered** - BLD's, or an
older one of their own - say so and change nothing. Two hooks refusing the same
call is harmless and confusing. If theirs is a different script doing the same
job, offer the swap rather than stacking them: one switch is the whole point.

## `off` — unregister

Remove **only the entry whose command names `block-image-generation.py`**, then
leave the rest of `settings.json` exactly as it was. Never rewrite the file from
a template, and never remove a hook entry this skill did not write: an unrelated
hook that disappears during a "turn this off" is the worst kind of side effect.

Leave the script in `~/.claude/hooks/`. It does nothing unregistered, and `on`
then costs one merge instead of a copy. Say that, so its presence is not read as
a failed removal.

Restart is needed here too, or the hook keeps blocking for the rest of the
session.

## `status`

Report three things, in three lines:

1. Whether an entry naming `block-image-generation.py` is in `settings.json`.
2. Whether the script exists in `~/.claude/hooks/`.
3. The result of `<PY> ~/.claude/hooks/block-image-generation.py --selftest`.

Registered plus a failing selftest is the one dangerous combination, and it
reads as "protected" from every other angle.

## Adding a generator the matcher does not know

Image tools appear constantly, and the lists in the script are explicit on
purpose: a matcher broad enough to catch everything blocks `upload_image` too.
To add one, edit `~/.claude/hooks/block-image-generation.py` - `SKILL_BLOCKED`
for a plugin skill, `BASH_BLOCK` for a path or endpoint, `TOOL_BLOCK` for an MCP
tool name - then **add it to the `must_block` list in the same file and re-run
`--selftest`**. A new pattern with no test is how the next person finds out it
was wrong.

Report the addition so it can go back into the package copy; an edit made only
to the installed hook is lost the next time the package is synced.
