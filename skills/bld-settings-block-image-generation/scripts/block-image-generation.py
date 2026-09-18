#!/usr/bin/env python3
"""PreToolUse hook: refuse AI image generation, whichever tool asks for it.

BLD's convention is to find existing assets rather than generate them. A
convention in a rule file is a reminder; this is the enforcement, at the tool
boundary, where forgetting is not possible.

Exit 2 blocks the call and shows the message to Claude. Exit 0 allows it.
Anything unparseable exits 0: a hook that cannot read its input must not be the
reason a session stops working.

    python block-image-generation.py --selftest

Three surfaces, because the first version of this hook watched only one. It
matched the Skill tool, and ui-ux-pro-max reaches the image models from
`python .../skills/design/scripts/logo/generate.py` - a Bash call the hook never
saw. Skill alone is not "blocked", it is "blocked by the front door".
"""
import json
import re
import sys

# ---------------------------------------------------------------- 1. skills
# Matched on the full namespaced name. `design` is deliberately absent from the
# bare set: Claude Code ships its own top-level `design` skill that lays out HTML
# artboards and generates nothing, and refusing it while citing an
# image-generation policy denies a legitimate tool for a reason that is not true
# of it. Plugin skills can only be invoked as `plugin:skill`, so a bare `design`
# is always the built-in one, and the namespaced entry still catches the plugin's.
SKILL_BLOCKED = {
    "ui-ux-pro-max:design",         # umbrella: logo, icon, CIP mockups, social photos
    "ui-ux-pro-max:banner-design",  # AI-generated banner visuals
}
SKILL_BLOCKED_BARE = {"banner-design"}

# ------------------------------------------------------- 2. tool names (MCP)
# An image-generation MCP server names its tool after what it does, so the name
# is the signal. The allow list runs FIRST and is the half that keeps this hook
# out of the way: reading, uploading, screenshotting, resizing and converting
# images all have "image" in the name and none of them generate anything.
TOOL_ALLOW = re.compile(
    r"read|upload|screenshot|capture|gif|resize|convert|compress|crop|optimi[sz]e"
    r"|download|fetch|view|list|search|analy|describe|ocr|diff",
    re.I)
TOOL_BLOCK = re.compile(
    r"(?:^|[_-])(?:generate|create|make|render|draw|text[_-]?to)[_-]?image"
    r"|image[_-]?gen|imagen|dall[_-]?e|midjourney|stable[_-]?diffusion|sdxl"
    r"|txt2img|text2image",
    re.I)

# ------------------------------------------------------------- 3. bash calls
# Only paths and endpoints that exist to generate images. Deliberately NOT here:
# a bare `flux` (a state library), `sharp`, `imagemagick`, `convert`, `ffmpeg` -
# all of them transform images someone already has, which is the workflow this
# policy is protecting, not the one it refuses.
BASH_BLOCK = [
    re.compile(r"skills/(?:design|banner-design)/scripts/[^\s]*generate", re.I),
    re.compile(r"ui-ux-pro-max[^\s]*(?:banner-design|design/scripts)", re.I),
    re.compile(r"api\.openai\.com/v\d+/images|images/generations", re.I),
    re.compile(r"imagegeneration@|imagen-\d|:predictLongRunning", re.I),
    re.compile(r"dall[_-]?e|midjourney|stable[_-]?diffusion|sdxl|black-forest-labs", re.I),
    re.compile(r"replicate\.(?:com|run)/[^\s]*(?:flux|sdxl|stable-diffusion|imagen)", re.I),
]

# A command is judged by SHAPE, not by substring. Matching the whole string
# blocked `cat`-ing the generator to read it, `grep`-ing for its name, and
# writing documentation that quotes an endpoint - it refused inspection of the
# thing rather than its use, which is backwards when the house rule is to read
# the source of anything that executes. So: split into segments, and block a
# segment only when something in it actually runs.
_SEGMENT = re.compile(r"\|\||&&|[|;\n]")
_EXEC_HEAD = re.compile(
    r"^(?:\w+=\S+\s+)*(?:sudo\s+)?"
    r"(?:python3?|py|node|npx|bun|deno|uv|uvx|pipx|curl|wget|sh|bash|zsh|pwsh|powershell)\b",
    re.I)
# An interpreter reading code from a heredoc or -c/-e can run anything written
# later in the command, so for those the whole command is the haystack again.
_INLINE_CODE = re.compile(r"<<|(?:^|\s)-(?:c|e)\b")


def _bash_blocks(cmd):
    for segment in _SEGMENT.split(cmd or ""):
        seg = segment.strip()
        if not _EXEC_HEAD.search(seg):
            continue                       # cat, grep, git, echo, ls: reading, not running
        haystack = cmd if _INLINE_CODE.search(seg) else seg
        for pat in BASH_BLOCK:
            hit = pat.search(haystack)
            if hit:
                return True, "this command runs an image generator (%s)" % hit.group(0)[:40]
    return False, ""


def blocks(tool, payload):
    """(True, why) if this call generates images. The whole policy, in one place."""
    if tool == "Skill":
        skill = (payload or {}).get("skill", "") or ""
        if skill in SKILL_BLOCKED or skill.split(":")[-1] in SKILL_BLOCKED_BARE:
            return True, "the '%s' skill generates images" % skill
        return False, ""

    if tool == "Bash":
        return _bash_blocks((payload or {}).get("command", "") or "")

    # Everything else is judged by its name, which is how an MCP image tool
    # announces itself. Allow list first, so read/upload/screenshot survive.
    if TOOL_ALLOW.search(tool or ""):
        return False, ""
    if TOOL_BLOCK.search(tool or ""):
        return True, "the '%s' tool generates images" % tool
    return False, ""


MESSAGE = (
    "BLOCKED by /bld-settings-block-image-generation: %s, and this machine's "
    "policy is to find existing assets rather than generate them. Non-image "
    "design paths are fine: ui-styling, design-system, brand, slides, or an "
    "existing asset from 21st.dev or Spline. Turn the block off with "
    "`/bld-settings-block-image-generation off` if the policy has changed."
)

_GEN = "skills/design/scripts/logo/gen" + "erate.py"   # split so this file's own
_API = "api.openai." + "com/v1/images/generations"     # selftest data cannot trip
_REP = "black-forest" + "-labs/flux-dev"               # a hook watching THIS command

if "--selftest" in sys.argv:
    must_block = [
        ("Skill", {"skill": "ui-ux-pro-max:design"}),
        ("Skill", {"skill": "ui-ux-pro-max:banner-design"}),
        ("Skill", {"skill": "banner-design"}),
        ("Bash", {"command": "python ~/.claude/plugins/ui-ux-pro-max/" + _GEN + " --name x"}),
        ("Bash", {"command": "cd /tmp && python3 ../ui-ux-pro-max/" + _GEN}),
        ("Bash", {"command": "curl -X POST https://" + _API + " -d '{}'"}),
        ("Bash", {"command": "npx replicate run " + _REP}),
        # an interpreter reading code from a heredoc can run anything below it
        ("Bash", {"command": "python - <<'PY'\nrun('" + _GEN + "')\nPY"}),
        ("mcp__images__generate_image", {"prompt": "a cat"}),
        ("mcp__fal__text_to_image", {"prompt": "a cat"}),
        ("imagegen", {}),
    ]
    must_allow = [
        ("Skill", {"skill": "design"}),                 # Claude Code's own, no images
        ("Skill", {"skill": "ui-ux-pro-max:ui-styling"}),
        ("Skill", {"skill": "ui-ux-pro-max:brand"}),
        ("Skill", {"skill": "bld-sprint-init"}),
        # naming a generator is not running one: reading, searching, documenting
        ("Bash", {"command": "cat ~/.claude/plugins/ui-ux-pro-max/" + _GEN}),
        ("Bash", {"command": 'grep -rn "dall-e" src/'}),
        ("Bash", {"command": "git log --oneline -- " + _GEN}),
        ("Bash", {"command": "echo '{\"cmd\":\"" + _GEN + "\"}' | python hook.py"}),
        ("Bash", {"command": "npm install flux"}),      # a state library
        ("Bash", {"command": "npx sharp resize logo.png"}),
        ("Bash", {"command": "ffmpeg -i in.mov out.gif"}),
        ("Read", {"file_path": "logo.png"}),
        ("mcp__claude-in-chrome__upload_image", {}),
        ("mcp__computer-use__screenshot", {}),
        ("mcp__Claude_Browser__read_page", {}),
    ]
    for tool, payload in must_block:
        ok, _ = blocks(tool, payload)
        assert ok, "should block: %s %s" % (tool, payload)
    for tool, payload in must_allow:
        ok, why = blocks(tool, payload)
        assert not ok, "should allow: %s %s (%s)" % (tool, payload, why)
    # Counted, not typed: a hardcoded tally goes stale the first time someone
    # adds a case, and then the only test of a security control reports a number
    # that is not what it checked.
    print("selftest ok: %d blocked, %d allowed" % (len(must_block), len(must_allow)))
    sys.exit(0)


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

hit, why = blocks(data.get("tool_name") or "", data.get("tool_input") or {})
if hit:
    sys.stderr.write(MESSAGE % why)
    sys.exit(2)
sys.exit(0)
