#!/usr/bin/env python3
"""Switch BLD command naming between friendly and pro mode.

    python switch-mode.py friendly   # bld-<type>-<skill>   e.g. /bld-sprint-init
    python switch-mode.py pro        # bld-<skill>-<type>   e.g. /bld-init-sprint
    python switch-mode.py status     # report, change nothing

Both modes carry all three parts. Pro moves the type to the end rather than
dropping it, so the distinctive word comes first and the name still says what
kind of command it is. Pro is NOT the shorter one; that was the old scheme.

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
    "planning":            ("sprint",       "bld-sprint-planning",            "bld-planning-sprint"),
    "init":                ("sprint",       "bld-sprint-init",                "bld-init-sprint"),
    "refine":              ("sprint",       "bld-sprint-refine",              "bld-refine-sprint"),

    "app":                 ("optimize",     "bld-optimize-app",               "bld-app-optimize"),
    "react":               ("optimize",     "bld-optimize-react",             "bld-react-optimize"),
    "security":            ("optimize",     "bld-optimize-security",          "bld-security-optimize"),
    "seo-indexing":        ("optimize",     "bld-optimize-seo-indexing",      "bld-seo-indexing-optimize"),

    "21st":                ("find",         "bld-find-21st",                  "bld-21st-find"),
    "spline":              ("find",         "bld-find-spline",                "bld-spline-find"),

    "agents":              ("runtime",      "bld-runtime-agents",             "bld-agents-runtime"),
    "tokens":              ("runtime",      "bld-runtime-tokens",             "bld-tokens-runtime"),
    "activate-mcps":       ("runtime",      "bld-runtime-activate-mcps",      "bld-activate-mcps-runtime"),

    "fable":               ("orchestrator", "bld-orchestrator-fable",         "bld-fable-orchestrator"),
    "opus":                ("orchestrator", "bld-orchestrator-opus",          "bld-opus-orchestrator"),

    "deploy":              ("util",         "bld-util-deploy",                "bld-deploy-util"),
    "handoff":             ("util",         "bld-util-handoff",               "bld-handoff-util"),
    "documentation":       ("util",         "bld-util-documentation",         "bld-documentation-util"),
    "customize-component": ("util",         "bld-util-customize-component",   "bld-customize-component-util"),
    "copywriting":         ("util",         "bld-util-copywriting",           "bld-copywriting-util"),

    # specials — identical in both modes
    "setup":               (None,           "bld-setup",                      "bld-setup"),
    "quiz":                (None,           "bld-quiz",                       "bld-quiz"),
    # "settings" is its own category: package settings you toggle on and off.
    # These never rename themselves, because a settings switch that changes name
    # depending on the setting is a trap. Both are identical in both modes.
    "professional-settings": ("settings",   "bld-professional-settings",      "bld-professional-settings"),
    "mcp-settings":          ("settings",   "bld-mcp-settings",               "bld-mcp-settings"),
}

# Names that existed before the current scheme, so an older install still
# migrates cleanly instead of leaving orphans.
#
# The bare `bld-<skill>` block is the one that matters most. Pro mode used to
# DELETE the type segment rather than move it, which was a third convention
# nobody sanctioned: there are two, `bld-<type>-<skill>` and `bld-<skill>-<type>`,
# and a name like `bld-app` belongs to neither. It also said less than the
# friendly name it replaced. Every install that ran the old pro mode is sitting
# on these names right now and has to be able to migrate off them.
LEGACY = {
    # the invented drop-the-type scheme, retired
    "bld-planning": "planning", "bld-init": "init", "bld-refine": "refine",
    "bld-app": "app", "bld-react": "react", "bld-security": "security",
    "bld-seo-indexing": "seo-indexing", "bld-21st": "21st", "bld-spline": "spline",
    "bld-agents": "agents", "bld-tokens": "tokens",
    "bld-activate-mcps": "activate-mcps",
    "bld-fable": "fable", "bld-opus": "opus",
    "bld-deploy": "deploy", "bld-handoff": "handoff",
    "bld-documentation": "documentation",
    "bld-customize-component": "customize-component",
    # older still
    "bld-optimize": "activate-mcps", "bld-optimize-sprint": "activate-mcps",
    "bld-seo": "seo-indexing", "bld-mode": "professional-settings",
    "bld-professional-mode": "professional-settings",
}

# Scripts too, not just markdown. The helper scripts print command names at the
# user ("needed for /bld-runtime-tokens only"), and .md-only meant those names
# never moved: in pro mode preflight told people to run four commands that did
# not exist. Every match is inside a string or a comment, so this rewrites
# prose that happens to live in a .py file, not code.
DOC_SUFFIXES = (".md", ".py", ".mjs")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SKILLS_DIR = os.path.join(ROOT, "skills")

# This skill's own docs deliberately contain BOTH naming schemes side by side as
# examples. Rewriting them collapses every contrast into "x becomes x", which is
# exactly what happened the first time this script ran. Never rewrite ourselves.
NO_REWRITE = (os.path.join(SKILLS_DIR, "bld-professional-settings"),)


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
    """Derive current mode from what is on disk. Ties or disagreement -> unknown.

    A skill has TWO names: its folder and its frontmatter. Counting only the
    frontmatter reported a clean mode on a tree where the folders still said
    something else, which is exactly the state an interrupted run leaves. That
    made `toggle`'s mixed-tree guard useless against the one failure it exists
    to catch, so a skill only votes when both of its names agree.
    """
    friendly = pro = 0
    for folder in os.listdir(SKILLS_DIR):
        path = os.path.join(SKILLS_DIR, folder, "SKILL.md")
        if not os.path.isfile(path):
            continue
        declared = read_name(path)
        if declared != folder and key_for(declared, folder) is not None:
            # A BLD skill whose folder and frontmatter disagree. Vote both ways
            # so the result can only ever be "mixed", the honest answer here.
            #
            # The key_for guard matters: installed globally, this directory also
            # holds every third-party skill on the machine, and plenty of those
            # legitimately declare a name that differs from their folder. Voting
            # on those pinned the mode to "mixed" forever and made `toggle`
            # permanently refuse for a reason that had nothing to do with BLD.
            friendly += 1
            pro += 1
            continue
        for key, (typ, f, p) in SKILLS.items():
            if f == p:
                continue          # same name in both modes: casts no vote
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


def docs_to_rewrite():
    """Only BLD's own markdown. Never a blind walk of ROOT.

    In a global install ROOT is ~/.claude, which on a real machine holds 1300+
    markdown files belonging to other skills, plugin caches and the user's own
    notes. Walking it would silently rewrite third-party docs, so enumerate what
    BLD actually owns instead.
    """
    owned = set(LEGACY)
    for _, friendly, pro in SKILLS.values():
        owned.add(friendly)
        owned.add(pro)

    out = []

    def collect(directory):
        for base, _, files in os.walk(directory):
            if ".git" in base.split(os.sep):
                continue
            if any(os.path.abspath(base).startswith(x) for x in NO_REWRITE):
                continue
            out.extend(os.path.join(base, fn) for fn in files
                       if fn.endswith(DOC_SUFFIXES))

    # BLD's own skill folders, matched by name against the table
    if os.path.isdir(SKILLS_DIR):
        for folder in os.listdir(SKILLS_DIR):
            if folder in owned:
                collect(os.path.join(SKILLS_DIR, folder))

    # sibling folders BLD owns, and the docs at the root. In a global install
    # the CLAUDE.md picked up here is the user's installed rule file, which
    # genuinely does reference these commands and should follow a rename.
    for sub in ("templates", "agents"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            collect(d)
    for name in ("README.md", "CLAUDE.md"):
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            out.append(p)

    return out


def git(*args):
    try:
        subprocess.run(["git", "-C", ROOT, *args], check=True,
                       capture_output=True, text=True)
        return True
    except Exception:
        return False


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    # "professional mode on/off" is how a person says this out loud, so accept it.
    mode = {"on": "pro", "off": "friendly"}.get(mode, mode)
    if mode not in ("friendly", "pro", "status", "toggle"):
        sys.exit("usage: switch-mode.py on|pro | off|friendly | toggle | status")

    current = detect_mode()

    # `toggle` flips to whichever mode is not the current one. It resolves here,
    # before any renaming, so the rest of main() only ever sees a real mode.
    # A mixed tree has no opposite to flip to, and guessing one would rename
    # half the tree the wrong way, so it refuses instead.
    if mode == "toggle":
        if current not in ("friendly", "pro"):
            sys.exit(
                f"cannot toggle: mode is {current}.\n"
                "Some skills are renamed and some are not, usually an interrupted\n"
                "run. Name the mode you want explicitly (on/pro or off/friendly)\n"
                "and it will bring the whole tree to that one."
            )
        mode = "friendly" if current == "pro" else "pro"

    if mode == "status":
        print(f"current mode: {current}\n")
        if current in ("friendly", "pro"):
            other = "friendly" if current == "pro" else "pro"
            flip = "off" if other == "friendly" else "on"
            print(f"  toggle -> {other}: switch-mode.py {flip}   (or: toggle)\n")
        for key, (typ, f, p) in SKILLS.items():
            print(f"  {typ or 'special':<13} {f:<32} {p}")
        return

    print(f"current mode: {current}  ->  switching to: {mode}\n")
    lookup = build_lookup(mode)
    renames = []

    # ── 1. folders + frontmatter ─────────────────────────────────────────
    # Plan the whole rename before touching anything. This used to rewrite each
    # SKILL.md's frontmatter and only THEN check the destination folder, so a
    # collision exited partway with earlier skills fully renamed and the current
    # one holding a new name in an old folder. That half-converted tree is the
    # worst state this script can leave behind, and it left it while reporting
    # a clean-looking error.
    plan = []
    for folder in sorted(os.listdir(SKILLS_DIR)):
        skill_md = os.path.join(SKILLS_DIR, folder, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        declared = read_name(skill_md)
        key = key_for(declared, folder)
        if key is None:
            print(f"  ?? {folder}: not in the table, left alone")
            continue
        plan.append((folder, skill_md, declared, target_name(key, mode)))

    moving_away = {f for f, _, _, w in plan if f != w}
    wants = [w for _, _, _, w in plan]
    problems = []
    for folder, _, _, want in plan:
        if folder == want:
            continue
        if wants.count(want) > 1:
            problems.append(f"two skills both want the name {want}")
        elif os.path.exists(os.path.join(SKILLS_DIR, want)) and want not in moving_away:
            problems.append(f"{folder} -> {want}, but {want} already exists")
    if problems:
        # ponytail: a rename cycle (A wants B's name while B wants A's) would
        # also need temp names, but the SKILLS table is a fixed bijection with
        # no such pair, so this validates rather than solves it.
        sys.exit("refusing to rename anything, nothing has been changed:\n  "
                 + "\n  ".join(sorted(set(problems))))

    for folder, skill_md, declared, want in plan:
        src = os.path.join(SKILLS_DIR, folder)

        if declared != want:
            s = io.open(skill_md, encoding="utf-8").read()
            s = re.sub(r"^name:.*$", f"name: {want}", s, count=1, flags=re.M)
            io.open(skill_md, "w", encoding="utf-8", newline="").write(s)

        if folder != want:
            dst = os.path.join(SKILLS_DIR, want)
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

    # A third kind: the H1 title, which carries the name with no leading slash
    # and so slipped past both patterns above. Sixteen of twenty-one skills sat
    # frozen at their pre-rename titles because of it, which is exactly the
    # "docs and commands disagree" state this skill exists to prevent.
    #
    # Anchored to the start of an H1 on purpose. Rewriting bare names anywhere
    # would hit prose describing the rename itself and collapse it into
    # "x becomes x", which is how this script destroyed its own docs once
    # already. No `$` in the lookahead either: these files are CRLF, and a `$`
    # anchor never matches with a \r sitting before the newline.
    h1_pattern = re.compile(r"(?<=^# )(" + alt + r")(?=[\s—-]|\Z)", re.M)

    touched = 0
    for path in docs_to_rewrite():
        # newline="" both ways: never silently convert CRLF to LF as a
        # side effect of a rename.
        s = io.open(path, encoding="utf-8", newline="").read()
        new = cmd_pattern.sub(lambda m: "/" + lookup[m.group(1)], s)
        new = path_pattern.sub(lambda m: lookup[m.group(1)], new)
        new = h1_pattern.sub(lambda m: lookup[m.group(1)], new)
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
