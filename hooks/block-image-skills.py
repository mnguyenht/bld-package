#!/usr/bin/env python3
"""PreToolUse hook: block skills that generate images (Gemini/Imagen calls).

The user has a hard no-image-generation policy. These ui-ux-pro-max skills call
out to Google image models, so we deny them at the tool boundary rather than
relying on the model to remember not to invoke them.

Exit 2 = block the tool call and show the message to Claude.
"""
import json, sys

# Skills confirmed to generate images (logo/icon/banner/CIP/social-photo via Gemini).
# Matched on the full namespaced name only.
BLOCKED = {
    "ui-ux-pro-max:design",         # umbrella: logo, icon, CIP mockups, social photos
    "ui-ux-pro-max:banner-design",  # AI-generated banner visuals
}

# Bare names blocked whatever plugin they came from. `design` is deliberately NOT
# here: Claude Code ships its own top-level `design` skill that lays out HTML
# artboards and generates no images, and blocking it refuses a legitimate tool
# while citing an image-generation policy that does not apply to it. Plugin
# skills can only be invoked as `plugin:skill`, so a bare `design` is always the
# built-in one and the namespaced entry above still catches ui-ux-pro-max's.
BLOCKED_BARE = {
    "banner-design",
}

def blocks(skill):
    """True if this skill name would be denied. The whole policy, in one place."""
    return skill in BLOCKED or skill.split(":")[-1] in BLOCKED_BARE


# Ceiling, named rather than implied: this matcher sees the Skill tool only. The
# image models are actually reached by `python .../skills/design/scripts/logo/
# generate.py`, so a Bash call straight to those scripts is NOT blocked here -
# the no-image-generation rule in CLAUDE.md is what covers that path. Verified
# against ui-ux-pro-max 2.6.2, where exactly two of its seven sub-skills touch
# image generation (design, banner-design) and both are listed above. Add a Bash
# matcher only if the CLAUDE.md rule stops being enough.


# `python block-image-skills.py --selftest` proves the matcher still does what it
# claims. Worth having: this hook fails silently by nature, so a broken matcher
# looks exactly like a working one until someone checks.
if "--selftest" in sys.argv:
    must_block = ("ui-ux-pro-max:design", "ui-ux-pro-max:banner-design", "banner-design")
    must_allow = ("design", "ui-ux-pro-max:ui-styling", "ui-ux-pro-max:brand",
                  "slides", "bld-sprint-init")
    for name in must_block:
        assert blocks(name), "should block: " + name
    for name in must_allow:
        assert not blocks(name), "should allow: " + name
    # Counted, not typed. A hardcoded tally goes stale the first time someone
    # adds a case, and then a security control's only test reports a number that
    # is not what it checked.
    print("selftest ok: %d blocked, %d allowed" % (len(must_block), len(must_allow)))
    sys.exit(0)

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # can't parse — don't block anything

if data.get("tool_name") != "Skill":
    sys.exit(0)

skill = (data.get("tool_input") or {}).get("skill", "")
if blocks(skill):
    sys.stderr.write(
        f"BLOCKED: skill '{skill}' uses AI image generation (Gemini/Imagen), which is "
        "disallowed by policy. Use non-image design skills instead: ui-styling, "
        "design-system, ui-ux-pro-max, slides."
    )
    sys.exit(2)

sys.exit(0)
