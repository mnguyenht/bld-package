#!/usr/bin/env python3
"""Scenario tests for preflight.py: build a fake machine, run it, check what it said.

    python scenarios.py            # run them all
    python scenarios.py -v C07     # run one, print its whole output

These are NOT a substitute for the scenario walks in TESTING.md. A walk finds
design flaws - a question asked before the information needed to answer it, a
step that cannot happen on some OS. This file only catches regressions in what
preflight concludes, which is the part that kept silently breaking while those
walks were being fixed.

Everything is built under a temp directory and torn down afterwards. Nothing
outside it is read or written, and preflight is read-only in any case.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "preflight.py")
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WIN = sys.platform == "win32"

CORE = ["emil-design-eng", "animation-vocabulary", "review-animations",
        "karpathy-guidelines", "find-skills", "copywriting", "a11y-audit",
        "framer-motion", "webapp-testing", "terms-of-service", "privacy-policy"]
PLUGINS = ["ponytail", "ui-ux-pro-max", "claude-code-setup"]


def bld_names():
    """(friendly, pro) folder-name lists, read from the canonical table.

    Hardcoding them here would mean this file goes stale the next time a skill is
    added, and a stale expectation in a test reads exactly like a passing one.
    """
    import importlib.util
    t = os.path.join(PKG, "skills", "bld-professional-settings",
                     "scripts", "switch-mode.py")
    spec = importlib.util.spec_from_file_location("bld_switch_mode", t)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return (sorted(f for _, f, _ in mod.SKILLS.values()),
            sorted(p for _, _, p in mod.SKILLS.values()))


FRIENDLY, PRO = bld_names()


def stub(d, name, code=0, out=None):
    """A fake executable that prints `out` and exits with `code`.

    preflight only asks whether most of these resolve. The exceptions are gh and
    vercel, which it runs to tell installed from signed-in (that is `code`), and
    node, which it runs for a version (that is `out`).
    """
    os.makedirs(d, exist_ok=True)
    if WIN:
        p = os.path.join(d, name + ".cmd")
        body = "@echo %s\r\n" % out if out else ""
        io.open(p, "w", newline="\r\n").write(body + "@exit /b %d\r\n" % code)
    else:
        p = os.path.join(d, name)
        body = 'echo "%s"\n' % out if out else ""
        io.open(p, "w", newline="\n").write("#!/bin/sh\n" + body + "exit %d\n" % code)
        os.chmod(p, 0o755)


def build(spec, root):
    home = os.path.join(root, "home")
    proj = os.path.join(root, "proj")
    claude = os.path.join(home, ".claude")
    os.makedirs(claude)
    os.makedirs(proj)

    names = PRO if spec.get("pro") else FRIENDLY
    if spec.get("mixed_names"):            # a naming switch that died partway
        names = list(dict.fromkeys(FRIENDLY[:12] + PRO[12:]))
    keep = names[:-spec["drop"]] if spec.get("drop") else names

    def put_bld(base):
        os.makedirs(os.path.join(base, "skills"), exist_ok=True)
        os.makedirs(os.path.join(base, "agents"), exist_ok=True)
        for s in keep:
            os.makedirs(os.path.join(base, "skills", s), exist_ok=True)
        if not spec.get("no_agent"):
            io.open(os.path.join(base, "agents", "bld-executor.md"), "w").write("x")

    if spec.get("global_bld"):
        put_bld(claude)
    # A bld-* folder in NEITHER naming mode - a skill dropped from the package
    # since their last install, which cp never removes.
    for s in spec.get("stray_skills", []):
        os.makedirs(os.path.join(claude, "skills", s), exist_ok=True)
    if spec.get("project_bld"):
        put_bld(os.path.join(proj, ".claude"))

    for s in CORE[: spec.get("core", 0)]:
        os.makedirs(os.path.join(claude, "skills", s), exist_ok=True)
    for extra in ("gstack", "impeccable"):
        if spec.get(extra):
            os.makedirs(os.path.join(claude, "skills", extra), exist_ok=True)

    plug = spec.get("plugins", "none")
    if plug in ("ok", "enabled-only"):
        io.open(os.path.join(claude, "settings.json"), "w").write(
            json.dumps({"enabledPlugins": dict((p + "@m", True) for p in PLUGINS)}))
    if plug in ("ok", "disk-only"):
        reg = {"plugins": {}}
        for p in PLUGINS:
            d = os.path.join(claude, "plugins", "cache", p)
            os.makedirs(d, exist_ok=True)
            reg["plugins"][p + "@m"] = [{"installPath": d}]
        io.open(os.path.join(claude, "plugins", "installed_plugins.json"), "w").write(
            json.dumps(reg))
    if spec.get("claudemd"):
        io.open(os.path.join(claude, "CLAUDE.md"), "w").write("# rules")
    if spec.get("proj_claudemd"):
        io.open(os.path.join(proj, "CLAUDE.md"), "w").write("# workspace rules")

    st = spec.get("state")
    sp = os.path.join(claude, ".bld-setup.json")
    if st == "corrupt":
        io.open(sp, "w").write('{\n  "chose": ["core-sk')     # killed mid-write
    elif st == "notdict":
        io.open(sp, "w").write('["core-skills"]')
    elif isinstance(st, dict):
        st = dict(st)
        if st.pop("_scoped", False):
            st["scope"], st["project"] = "project", proj
        io.open(sp, "w").write(json.dumps(st, indent=1))

    binp = os.path.join(root, "bin")
    for name in spec.get("bin", ["node", "npm", "git"]):
        if isinstance(name, tuple):
            stub(binp, *name)          # (name, exit code[, stdout])
        else:
            stub(binp, name)
    return home, proj, binp


def run(spec, root):
    home, proj, binp = build(spec, root)
    if spec.get("delete_proj"):
        shutil.rmtree(proj, ignore_errors=True)
    env = dict(os.environ)
    if WIN:
        rest = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
    else:
        rest = "/usr/bin" + os.pathsep + "/bin"
    env["PATH"] = binp + os.pathsep + rest
    env["HOME"] = home
    env["USERPROFILE"] = home
    for k in ("HOMEPATH", "HOMEDRIVE"):
        env.pop(k, None)
    args = [sys.executable, PRE]
    if spec.get("pass_project"):
        args += ["--project", proj]
    if spec.get("project_eq"):
        args += ["--project=" + proj]
    args += spec.get("raw_args", [])
    p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=root)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


DONE = {"chose": ["core-skills", "bld", "plugins"],
        "declined": ["gstack", "impeccable", "react-tools", "token-monitor",
                     "deploy", "agents", "mcp"],
        "done": ["prereqs", "core-skills", "plugins", "bld"],
        "completed": True, "completed_on": "2026-09-01"}


def scoped(**kw):
    s = dict(DONE)
    s.update(kw)
    s["_scoped"] = True
    return s


# (spec, expectations, exit code). An expectation starting with "!" must be ABSENT.
CASES = [
 ({"id": "C01", "desc": "fresh machine"}, ["FIRST RUN"], 0),

 ({"id": "C02", "desc": "hand install, state file deleted",
   "global_bld": 1, "core": 11, "plugins": "ok"},
  ["NO STATE FILE, but BLD is already", "!FIRST RUN"], 0),

 ({"id": "C03", "desc": "state truncated mid-write",
   "global_bld": 1, "state": "corrupt"},
  ["STATE FILE UNREADABLE", "UNREADABLE, see verdict", "!none yet"], 0),

 ({"id": "C04", "desc": "state file is a JSON list, not an object",
   "global_bld": 1, "state": "notdict"}, ["STATE FILE UNREADABLE"], 0),

 ({"id": "C05", "desc": "state file parses but is empty",
   "global_bld": 1, "state": {}}, ["STATE FILE IS EMPTY", "!NO STATE FILE"], 0),

 ({"id": "C06", "desc": "scoped install remembered from the state file",
   "project_bld": 1, "core": 11, "plugins": "ok", "state": scoped()},
  ["(remembered from your last setup)", "(project,", "!MISSING NOW : bld"], 0),

 ({"id": "C07", "desc": "remembered project has since been deleted",
   "project_bld": 1, "state": scoped(), "delete_proj": 1},
  ["does not exist", "moved or", "unproven until that path is fixed"], 0),

 ({"id": "C08", "desc": "resume: disk ahead of state (crash before recording)",
   "global_bld": 1, "core": 11,
   "state": {"chose": ["core-skills", "bld", "plugins"], "declined": [],
             "done": ["prereqs", "core-skills"], "completed": False}},
  ["RESUMING", "ALREADY DONE: bld"], 0),

 ({"id": "C09", "desc": "resume: state claims a group the disk denies",
   "global_bld": 1,
   "state": {"chose": ["core-skills", "bld"], "declined": [],
             "done": ["prereqs", "core-skills"], "completed": False}},
  ["RECHECK     : core-skills"], 0),

 ({"id": "C10", "desc": "node and npm missing", "bin": []}, ["BLOCKED"], 1),

 ({"id": "C11", "desc": "git missing (they downloaded a ZIP)",
   "bin": ["node", "npm"]}, ["LIMITED", "OPTIONAL - only gates deploy"], 0),

 ({"id": "C12", "desc": "plugin enabled in settings but absent on disk",
   "global_bld": 1, "plugins": "enabled-only"}, ["enabled but not on disk"], 0),

 ({"id": "C13", "desc": "plugin on disk but never enabled",
   "global_bld": 1, "plugins": "disk-only"}, ["on disk but not enabled"], 0),

 ({"id": "C14", "desc": "a typo'd flag must not silently default",
   "raw_args": ["--projekt", "x"]}, ["unrecognised argument"], 1),

 ({"id": "C15", "desc": "--project= equals form is honoured",
   "project_bld": 1, "project_eq": 1}, ["(--project)", "(project,"], 0),

 ({"id": "C16", "desc": "vercel installed but signed out",
   "bin": ["node", "npm", "git", ("vercel", 1)]},
  ["INSTALLED BUT NOT SIGNED IN"], 0),

 ({"id": "C17", "desc": "scoped install whose state omits the project path",
   "project_bld": 1, "core": 11, "plugins": "ok", "state": dict(DONE)},
  ["MISSING NOW"], 0),

 ({"id": "C18", "desc": "installed both globally and in the project",
   "global_bld": 1, "project_bld": 1, "pass_project": 1}, ["global+project"], 0),

 ({"id": "C19", "desc": "machine is in pro naming mode",
   "global_bld": 1, "pro": 1}, ["pro mode", "!use the other naming mode"], 0),

 ({"id": "C20", "desc": "half-copied install: 3 skills never landed",
   "global_bld": 1, "drop": 3}, ["MISSING:"], 0),

 ({"id": "C21", "desc": "skills copied but the agents/ copy failed",
   "global_bld": 1, "no_agent": 1}, ["bld-executor agent  MISSING"], 0),

 ({"id": "C22", "desc": "naming switch stopped partway",
   "global_bld": 1, "mixed_names": 1},
  ["use the other naming mode", "Do NOT re-copy BLD"], 0),

 ({"id": "C23", "desc": "mcp group unconfirmed until jcodemunch is installed",
   "global_bld": 1,
   "state": {"chose": ["bld", "mcp"], "declined": [], "done": ["bld"],
             "completed": False}}, ["Still to do : mcp"], 0),

 ({"id": "C24", "desc": "mcp group confirmed once jcodemunch is on PATH",
   "global_bld": 1, "bin": ["node", "npm", "git", "jcodemunch-mcp"],
   "state": {"chose": ["bld", "mcp"], "declined": [], "done": ["bld"],
             "completed": False}}, ["ALREADY DONE: mcp"], 0),

 ({"id": "C25", "desc": "Node too old for the skills installer",
   "bin": [("node", 0, "v12.22.12"), "npm", "git"]},
  ["Node 18+ is expected", "!BLOCKED"], 0),

 ({"id": "C33", "desc": "claude-md groups are real, not flagged as typos",
   "global_bld": 1, "claudemd": 1,
   "state": {"chose": ["bld", "claude-md-global"], "declined": ["claude-md-workspace"],
             "done": ["bld", "claude-md-global"], "completed": False}},
  ["!NOT REAL GROUP NAMES", "!RECHECK"], 0),

 ({"id": "C34", "desc": "state claims the global rule file that is not on disk",
   "global_bld": 1,
   "state": {"chose": ["bld", "claude-md-global"], "declined": [],
             "done": ["bld", "claude-md-global"], "completed": False}},
  ["RECHECK", "claude-md-global"], 0),

 ({"id": "C35", "desc": "workspace rule file counts independently of the global one",
   "global_bld": 1, "proj_claudemd": 1, "pass_project": 1,
   "state": {"chose": ["bld", "claude-md-workspace"], "declined": ["claude-md-global"],
             "done": ["bld", "claude-md-workspace"], "completed": False}},
  ["!NOT REAL GROUP NAMES", "!RECHECK"], 0),

 ({"id": "C27", "desc": "bun missing is named, with a source",
   "global_bld": 1}, ["bun                 needed for gstack only -> npm i -g bun"], 0),

 ({"id": "C28", "desc": "bun present is not nagged about",
   "global_bld": 1, "bin": ["node", "npm", "git", "bun"]},
  ["!needed for gstack only"], 0),

 ({"id": "C29", "desc": "a bld-* folder the package no longer ships",
   "global_bld": 1, "stray_skills": ["bld-dropped-thing"]},
  ["the package does not ship", "bld-dropped-thing", "!not on PATH"], 0),

 ({"id": "C30", "desc": "state file field is a string, not a list",
   "global_bld": 1,
   "state": {"chose": "bld", "declined": [], "done": [], "completed": False}},
  ["UNREADABLE FIELDS: chose", "!Chose       : b, l, d"], 0),

 ({"id": "C31", "desc": "state file names a group Phase 4 cannot install",
   "global_bld": 1,
   "state": {"chose": ["bld", "not-a-group"], "declined": [], "done": [],
             "completed": False}},
  ["NOT REAL GROUP NAMES: not-a-group"], 0),

 ({"id": "C32", "desc": "a healthy state file triggers neither warning",
   "global_bld": 1,
   "state": {"chose": ["bld"], "declined": [], "done": ["prereqs"],
             "completed": False}},
  ["!UNREADABLE FIELDS", "!NOT REAL GROUP NAMES"], 0),

 ({"id": "C26", "desc": "current Node is not warned about",
   "bin": [("node", 0, "v22.11.0"), "npm", "git"]},
  ["!Node 18+ is expected"], 0),
]


def check(musts, out):
    """Expectations this run failed. "!x" means x must NOT appear."""
    bad = []
    for m in musts:
        if m.startswith("!"):
            if m[1:] in out:
                bad.append(m)
        elif m not in out:
            bad.append(m)
    return bad


def main(argv):
    verbose = "-v" in argv
    only = [a for a in argv if not a.startswith("-")]
    bad = 0
    ran = 0
    root = tempfile.mkdtemp(prefix="bld-scenarios-")
    try:
        for spec, musts, want_rc in CASES:
            if only and spec["id"] not in only:
                continue
            ran += 1
            box = os.path.join(root, spec["id"])
            os.makedirs(box)
            rc, out = run(spec, box)
            miss = check(musts, out)
            ok = not miss and rc == want_rc
            print(("PASS " if ok else "FAIL ") + spec["id"] + "  " + spec["desc"])
            if not ok:
                bad += 1
                if rc != want_rc:
                    print("      exit %d, wanted %d" % (rc, want_rc))
                for m in miss:
                    print("      " + ("must NOT contain: " + m[1:]
                                      if m.startswith("!") else "missing: " + m))
            if verbose:
                print(out)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("\n%d/%d passed" % (ran - bad, ran))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
