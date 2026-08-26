#!/usr/bin/env python3
"""Check the invariants CLAUDE.md describes in prose. Run before committing.

    python check.py

Exits 0 if clean, 1 with a list if not. Reads only; changes nothing.

Why this exists: `bld-professional-settings` is deliberately excluded from the
rename pass, because that pass would flatten its side-by-side naming examples.
The side effect is that NOTHING keeps it in sync, and it went stale twice in one
session - a missing category in its own type table, and a command count still
saying 21 when there were 22. A note asking maintainers to remember is weaker
than a check that fails.
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(ROOT, "skills")
# The one file allowed to contain command names from BOTH naming modes.
EXEMPT = "bld-professional-settings"

problems = []


def fail(what):
    problems.append(what)


def read(*parts):
    return io.open(os.path.join(ROOT, *parts), encoding="utf-8", newline="").read()


def load_table():
    """The canonical SKILLS taxonomy, imported from the script that owns it."""
    import importlib.util
    path = os.path.join(SKILLS_DIR, EXEMPT, "scripts", "switch-mode.py")
    spec = importlib.util.spec_from_file_location("bld_switch_mode", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    table = load_table()
    folders = sorted(d for d in os.listdir(SKILLS_DIR) if d.startswith("bld-"))
    friendly = set(f for _, f, _ in table.SKILLS.values())
    pro = set(p for _, _, p in table.SKILLS.values())
    n = len(table.SKILLS)

    # 1. folder name == frontmatter name. switch-mode's mode detection treats a
    #    disagreement as an interrupted rename and refuses to toggle.
    for d in folders:
        skill_md = os.path.join(SKILLS_DIR, d, "SKILL.md")
        if not os.path.isfile(skill_md):
            fail("%s has no SKILL.md" % d)
            continue
        m = re.search(r"^name:\s*(.+)$", read("skills", d, "SKILL.md"), re.M)
        declared = m.group(1).strip() if m else None
        if declared != d:
            fail("%s: frontmatter says name: %r" % (d, declared))

    # 2. the tree matches ONE mode exactly. A count would let an unrelated bld-*
    #    folder stand in for a skill that never got added.
    on_disk = set(folders)
    if on_disk not in (friendly, pro):
        near = min((friendly, pro), key=lambda s: len(s ^ on_disk))
        for miss in sorted(near - on_disk):
            fail("missing skill folder: %s" % miss)
        for extra in sorted(on_disk - near):
            fail("folder not in the SKILLS table: %s" % extra)

    # 3. every type in the table has a row in the type table, and a section in
    #    the README. This is the check that would have caught `settings` being
    #    added to the code and to nothing else.
    types = set(t for t, _, _ in table.SKILLS.values() if t)
    type_doc = read("skills", EXEMPT, "SKILL.md")
    readme = read("README.md")
    for t in sorted(types):
        if not re.search(r"^\|\s*\*\*%s\*\*\s*\|" % re.escape(t), type_doc, re.M):
            fail("type %r is in SKILLS but has no row in %s/SKILL.md's type table" % (t, EXEMPT))
        if not re.search(r"^### %s\s*$" % re.escape(t), readme, re.M):
            fail("type %r is in SKILLS but has no '### %s' section in README.md" % (t, t))

    # 4. every skill is named in all four required places (CLAUDE.md's rule).
    places = {"README.md": readme,
              "templates/CLAUDE.workspace.md": read("templates", "CLAUDE.workspace.md"),
              "switch-mode.py": read("skills", EXEMPT, "scripts", "switch-mode.py")}
    for d in folders:
        for where, text in places.items():
            if d not in text:
                fail("%s is not mentioned in %s" % (d, where))

    # 5. stated command counts. Each pattern is deliberately tied to a phrasing
    #    that can only be about BLD's own command set. A bare `\d+ skills` was
    #    tried first and was useless: it matched every mention of gstack's 54
    #    upstream skills and the 6 BLD keeps, which are counts of something else
    #    entirely. It also matched "16 of 21 skills", a dated incident record
    #    that is correct as written and must not be updated.
    count_claims = [
        r"(\d+) slash commands",
        r"\*\*BLD\*\* \((\d+) commands\)",
        r"a first-timer facing (\d+)",
        r"all (\d+) names",
        r"\*\*(\d+) `bld-\*` skills\*\*",
        r"^(\d+) skills[,.]",
        r"skills/\s+(\d+) commands",
    ]
    for base, _, files in os.walk(ROOT):
        if ".git" in base.split(os.sep):
            continue
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace("\\", "/")
            if "/ecc/" in rel:                     # vendored third-party checklists
                continue
            for i, line in enumerate(io.open(os.path.join(base, fn),
                                             encoding="utf-8", errors="replace"), 1):
                for pat in count_claims:
                    for got in re.findall(pat, line):
                        if int(got) != n:
                            fail("%s:%d claims %s where the table has %d: %s"
                                 % (rel, i, got, n, line.strip()[:70]))

    # 6. the flattening bug. A literal command name from the OTHER naming mode,
    #    in any file the rename pass rewrites, gets converted on the next switch.
    #    When a sentence contrasts both modes, both halves become the same
    #    string and the meaning is destroyed permanently. This ate the rule in
    #    CLAUDE.md that warns about it.
    current = friendly if on_disk == friendly else pro
    other = pro if current is friendly else friendly
    other_only = sorted(other - current, key=len, reverse=True)
    # 7. a path-shaped reference the rename pass cannot see. Its path pattern
    #    anchors on `skills/`, so a bare `bld-x/run.py` in a comment survives
    #    every mode switch and quietly goes stale. Only names that actually
    #    change between modes can rot this way.
    renameable = set(f for _, f, p in table.SKILLS.values() if f != p) | \
                 set(p for _, f, p in table.SKILLS.values() if f != p)
    bare_path = re.compile(r"(?<!skills/)\b(bld-[a-z0-9-]+)/")
    cmd_pat = None
    if other_only:
        cmd_pat = re.compile(r"(?<![\w-])/(" + "|".join(re.escape(x) for x in other_only) + r")(?![\w-])")
    for base, _, files in os.walk(ROOT):
        if ".git" in base.split(os.sep) or EXEMPT in base:
            continue
        for fn in sorted(files):
            if not fn.endswith((".md", ".py", ".mjs")):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace("\\", "/")
            for i, line in enumerate(io.open(os.path.join(base, fn),
                                             encoding="utf-8", errors="replace"), 1):
                hit = cmd_pat.search(line) if cmd_pat else None
                if hit:
                    fail("%s:%d writes /%s, a command name from the other naming "
                         "mode. The next mode switch rewrites it and the sentence "
                         "loses its meaning permanently." % (rel, i, hit.group(1)))
                for m in bare_path.finditer(line):
                    if m.group(1) in renameable:
                        fail("%s:%d writes the path %s/ without a skills/ prefix, so "
                             "the rename pass cannot see it and it goes stale on the "
                             "next mode switch." % (rel, i, m.group(1)))

    print("%d skills, %d types, %d problems" % (len(folders), len(types), len(problems)))
    for p in problems:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
