#!/usr/bin/env python3
"""Switch BLD command naming between friendly and pro mode.

    python switch-mode.py friendly   # bld-<type>-<skill>   e.g. /bld-sprint-init
    python switch-mode.py pro        # bld-<skill>          e.g. /bld-init
    python switch-mode.py status     # report, change nothing

Renames the skill folders, rewrites the `name:` frontmatter (which is what you
actually type), and updates every /bld-* cross-reference in the docs so nothing
points at a command that no longer exists.

Idempotent: running the same mode twice is a no-op.

>> Skills register at STARTUP. Restart Claude Code after switching.

ponytail: one table, one regex pass. No config file, no state file — current mode
is derived from what's on disk.
"""

import io
import os
import re
import subprocess
import sys

# ─────────────────────────────────────────────────────────────────────────────
# The canonical table. skill-key: (type, friendly, pro)
# type None = "special": acts on BLD itself, so the name never changes.
# ─────────────────────────────────────────────────────────────────────────────
SKILLS = {
    "planning":            ("sprint",       "bld-sprint-planning",            "bld-planning"),
    "init":                ("sprint",       "bld-sprint-init",                "bld-init"),
    "refine":              ("sprint",       "bld-sprint-refine",              "bld-refine"),

    "app":                 ("optimize",     "bld-optimize-app",               "bld-app"),
    "react":               ("optimize",     "bld-optimize-react",             "bld-react"),
    "security":            ("optimize",     "bld-optimize-security",          "bld-security"),
    "seo-indexing":        ("optimize",     "bld-optimize-seo-indexing",      "bld-seo-indexing"),

    "21st":                ("find",         "bld-find-21st",                  "bld-21st"),
    "spline":              ("find",         "bld-find-spline",                "bld-spline"),

    "agents":              ("runtime",      "bld-runtime-agents",             "bld-agents"),
    "tokens":              ("runtime",      "bld-runtime-tokens",             "bld-tokens"),
    "activate-mcps":       ("runtime",      "bld-runtime-activate-mcps",      "bld-activate-mcps"),

    "fable":               ("orchestrator", "bld-orchestrator-fable",         "bld-fable"),
    "opus":                ("orchestrator", "bld-orchestrator-opus",          "bld-opus"),

    "deploy":              ("util",         "bld-util-deploy",                "bld-deploy"),
    "handoff":             ("util",         "bld-util-handoff",               "bld-handoff"),
    "documentation":       ("util",         "bld-util-documentation",         "bld-documentation"),
    "customize-component": ("util",         "bld-util-customize-component",   "bld-customize-component"),

    # specials — identical in both modes
    "setup":               (None,           "bld-setup",                      "bld-setup"),
    "quiz":                (None,           "bld-quiz",                       "bld-quiz"),
    "mode":                (None,           "bld-mode",                       "bld-mode"),
}

# Names that existed before this scheme, so an older install still migrates cleanly.
LEGACY = {
    "bld-app-optimize": "app", "bld-react-optimize": "react",
    "bld-find-21st": "21st", "bld-find-spline": "spline",
    "bld-fable-orchestrator": "fable", "bld-opus-orchestrator": "opus",
    "bld-optimize": "activate-mcps", "bld-optimize-sprint": "activate-mcps",
    "bld-seo": "seo-indexing",
}

DOC_SUFFIXES = (".md",)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SKILLS_DIR = os.path.join(ROOT, "skills")

# This skill's own docs deliberately contain BOTH naming schemes side by side as
# examples. Rewriting them collapses every contrast into "x becomes x", which is
# exactly what happened the first time this script ran. Never rewrite ourselves.
NO_REWRITE = (os.path.join(SKILLS_DIR, "bld-mode"),)


def target_name(key, mode):
    _, friendly, pro = SKILLS[key]
    return friendly if mode == "friendly" else pro


def build_lookup(mode):
    """Every name we might encounter -> the name it should become in `mode`."""
    out = {}
    for key in SKILLS:
        _, friendly, pro = SKILLS[key]
        for alias in (friendly, pro):
            out[alias] = target_name(key, mode)
    for alias, key in LEGACY.items():
        out[alias] = target_name(key, mode)
    return out


def detect_mode():
    """Derive current mode from the declared names on disk. Ties -> unknown."""
    friendly = pro = 0
    for folder in os.listdir(SKILLS_DIR):
        path = os.path.join(SKILLS_DIR, folder, "SKILL.md")
        if not os.path.isfile(path):
            continue
        declared = read_name(path)
        for key, (typ, f, p) in SKILLS.items():
            if typ is None:
                continue          # specials are identical, they cast no vote
            if declared == f:
                friendly += 1
            elif declared == p:
                pro += 1
    if friendly and not pro:
        return "friendly"
    if pro and not friendly:
        return "pro"
    return f"mixed (friendly={friendly}, pro={pro})"


def read_name(path):
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip()
    return None


def key_for(declared, folder):
    """Which table row does this skill belong to?"""
    for key, (_, f, p) in SKILLS.items():
        if declared in (f, p):
            return key
    if declared in LEGACY:
        return LEGACY[declared]
    # last resort: match on folder, tolerating any word order
    parts = set(folder.replace("bld-", "").split("-"))
    for key in SKILLS:
        if set(key.split("-")) <= parts:
            return key
    return None


def git(*args):
    try:
        subprocess.run(["git", "-C", ROOT, *args], check=True,
                       capture_output=True, text=True)
        return True
    except Exception:
        return False


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    if mode not in ("friendly", "pro", "status"):
        sys.exit("usage: switch-mode.py friendly|pro|status")

    current = detect_mode()
    if mode == "status":
        print(f"current mode: {current}\n")
        for key, (typ, f, p) in SKILLS.items():
            print(f"  {typ or 'special':<13} {f:<32} {p}")
        return

    print(f"current mode: {current}  ->  switching to: {mode}\n")
    lookup = build_lookup(mode)
    renames = []

    # ── 1. folders + frontmatter ─────────────────────────────────────────
    for folder in sorted(os.listdir(SKILLS_DIR)):
        src = os.path.join(SKILLS_DIR, folder)
        skill_md = os.path.join(src, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue

        declared = read_name(skill_md)
        key = key_for(declared, folder)
        if key is None:
            print(f"  ?? {folder}: not in the table, left alone")
            continue

        want = target_name(key, mode)

        if declared != want:
            s = io.open(skill_md, encoding="utf-8").read()
            s = re.sub(r"^name:.*$", f"name: {want}", s, count=1, flags=re.M)
            io.open(skill_md, "w", encoding="utf-8", newline="").write(s)

        if folder != want:
            dst = os.path.join(SKILLS_DIR, want)
            if os.path.exists(dst):
                sys.exit(f"refusing to overwrite existing folder: {want}")
            if not git("mv", f"skills/{folder}", f"skills/{want}"):
                os.rename(src, dst)
            renames.append((folder, want))
        if declared != want or folder != want:
            print(f"  ok {declared or folder}  ->  {want}")

    # ── 2. every /bld-* reference in every doc ───────────────────────────
    # Longest first, so /bld-sprint-init is matched before /bld-init.
    keys = sorted(lookup, key=len, reverse=True)
    alt = "|".join(re.escape(k) for k in keys)

    # Two different things carry a skill name, and BOTH break on a rename:
    #   commands  "/bld-init"                    - what the user types
    #   paths     "skills/bld-init/SKILL.md"     - what Claude is told to read/run
    # Missing the second kind leaves skills pointing at files that no longer
    # exist, which fails at runtime rather than loudly at rename time.
    cmd_pattern = re.compile(r"(?<![\w-])/(" + alt + r")(?![\w-])")
    path_pattern = re.compile(r"(?<=skills/)(" + alt + r")(?=[/\\])")

    touched = 0
    for base, _, files in os.walk(ROOT):
        if ".git" in base.split(os.sep):
            continue
        if any(os.path.abspath(base).startswith(x) for x in NO_REWRITE):
            continue
        for fn in files:
            if not fn.endswith(DOC_SUFFIXES):
                continue
            path = os.path.join(base, fn)
            # newline="" both ways: never silently convert CRLF to LF as a
            # side effect of a rename.
            s = io.open(path, encoding="utf-8", newline="").read()
            new = cmd_pattern.sub(lambda m: "/" + lookup[m.group(1)], s)
            new = path_pattern.sub(lambda m: lookup[m.group(1)], new)
            if new != s:
                io.open(path, "w", encoding="utf-8", newline="").write(new)
                touched += 1

    print(f"\n  folders renamed: {len(renames)}")
    print(f"  docs updated:    {touched}")
    # ASCII only, and no escapes: Windows consoles default to cp1252, so a stray
    # emoji here crashes AFTER all the work is done and reads as a total failure.
    print()
    print(">> RESTART Claude Code - skills only register at startup.")


if __name__ == "__main__":
    main()
