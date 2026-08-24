#!/usr/bin/env python3
"""PreToolUse hook: block skills that generate images (Gemini/Imagen calls).

The user has a hard no-image-generation policy. These ui-ux-pro-max skills call
out to Google image models, so we deny them at the tool boundary rather than
relying on the model to remember not to invoke them.

Exit 2 = block the tool call and show the message to Claude.
"""
import json, sys

# Skills confirmed to generate images (logo/icon/banner/CIP/social-photo via Gemini).
BLOCKED = {
    "design",              # umbrella: logo, icon, CIP mockups, social photos — all image gen
    "banner-design",       # AI-generated banner visuals
    "ui-ux-pro-max:design",
    "ui-ux-pro-max:banner-design",
}

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # can't parse — don't block anything

if data.get("tool_name") != "Skill":
    sys.exit(0)

skill = (data.get("tool_input") or {}).get("skill", "")
# normalize: match bare name or plugin:name form
bare = skill.split(":")[-1]
if skill in BLOCKED or bare in BLOCKED:
    sys.stderr.write(
        f"BLOCKED: skill '{skill}' uses AI image generation (Gemini/Imagen), which is "
        "disallowed by policy. Use non-image design skills instead: ui-styling, "
        "design-system, ui-ux-pro-max, slides."
    )
    sys.exit(2)

sys.exit(0)
