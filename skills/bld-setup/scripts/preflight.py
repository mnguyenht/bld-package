#!/usr/bin/env python3
"""BLD setup preflight: what's here, what's missing, and where we left off.

    python preflight.py
    python preflight.py --project /path/to/your-app

Prints three things:
  1. PREREQUISITES  - the tools without which the install cannot start
  2. INVENTORY      - what BLD has already put on this machine
  3. VERDICT        - first run / resume / returning, and what to do next

Read-only. Installs nothing, changes nothing.

ASCII output only: Windows consoles default to cp1252 and a stray symbol here
would crash the one command that is supposed to tell you what is wrong.
"""

import sys

# This file parses cleanly on Python 2, so without this guard it gets all the
# way to `shutil.which` (3.3+) or `subprocess.run(capture_output=)` (3.7+) and
# dies on an AttributeError that reads like "BLD is broken" rather than "your
# Python is too old". Plain % formatting and no f-strings, so the message itself
# survives on any interpreter old enough to hit it.
if sys.version_info[:2] < (3, 7):
    sys.stderr.write(
        "BLD preflight needs Python 3.7 or newer. This is %d.%d (%s).\n"
        "Nothing is wrong with BLD. Try `python3 preflight.py` instead:\n"
        "macOS and Linux ship Python 3 as `python3` and often leave `python`\n"
        "pointing at an old Python 2.\n"
        % (sys.version_info[0], sys.version_info[1], sys.executable)
    )
    sys.exit(1)

# The docstring above promises ASCII-only output, and every literal in this file
# keeps it. The USER'S PATH does not: it is interpolated into the report, and a
# home like C:\Users\<a non-Latin name> cannot be encoded to cp1252, which is what a
# Windows console still defaults to. Observed there - the whole report printed,
# then the closing "state file:" line raised UnicodeEncodeError and the script
# exited non-zero, which reads as "BLD is broken" from the one command that
# exists to say what is. Latin-1 names survive cp1252 and hid this for a long
# time. errors="replace" matters as much as the encoding: a console that truly
# cannot render the characters then shows placeholders instead of dying.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass

import io
import json
import os
import shutil
import subprocess

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
STATE = os.path.join(CLAUDE, ".bld-setup.json")


# skill-group key -> the skills it installs, for inventory purposes
CORE_SKILLS = [
    "emil-design-eng", "animation-vocabulary", "review-animations",
    "karpathy-guidelines", "find-skills", "copywriting", "a11y-audit",
    "framer-motion", "webapp-testing", "terms-of-service", "privacy-policy",
]
PLUGINS = ["ponytail", "ui-ux-pro-max", "claude-code-setup"]

# Groups whose presence on disk PROVES BLD was installed here, used when there
# is no state file to consult. react-tools, deploy, token-monitor and agents are
# deliberately absent: react-doctor, gh, vercel, uv and codex are ordinary tools
# a developer may already have for unrelated reasons, so finding them proves
# nothing about BLD and would turn a genuine first run into "already installed".
BLD_PROOF = ("bld", "core-skills", "plugins", "gstack", "impeccable")

# Group slugs are what the state file stores and what Phase 4 keys off, so they
# stay first on every line. The gloss is for the human reading the same output:
# "agents" meaning the external Codex/Gemini CLIs sat two lines below a row
# literally called "bld-executor agent", which is a different thing entirely.
# Only the slugs that are actually ambiguous get a gloss. Glossing all of them
# pushed these lines past 150 characters, which in a terminal is worse than the
# jargon it was fixing.
LABEL = {
    "deploy": "gh + vercel",
    "agents": "Codex/Gemini",
    "mcp":    "MCP servers",
}


def named(groups):
    """'slug (what it is)' for output a beginner has to act on."""
    return ", ".join((g + " (" + LABEL[g] + ")") if g in LABEL else g
                     for g in groups)


def have(cmd):
    """Resolve a command to a path we can actually execute.

    On Windows, npm-installed tools exist twice: a shell shim with no extension
    (for Git Bash) and a .cmd (for CreateProcess). shutil.which finds the shim
    first, and subprocess cannot run it, so a perfectly working `vercel` reports
    as broken. Prefer the executable forms.
    """
    if sys.platform == "win32":
        for ext in (".cmd", ".exe", ".bat"):
            found = shutil.which(cmd + ext)
            if found:
                return found
        return shutil.which(cmd)

    found = shutil.which(cmd)
    # Under WSL the Windows PATH is inherited by default, so /mnt/c/... shims for
    # npm-installed tools resolve here and look installed. They are not runnable
    # from Linux: they exec `node`, which resolves to the Windows binary they
    # cannot reach, and die with "exec: node: not found" long after this check
    # said ok. Report them as missing so the install offers them properly.
    if found and found.startswith("/mnt/") and _WSL:
        return None
    return found


def run(args, timeout=15):
    """Return (ok, first-line-of-output). Never raises."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode == 0, out.strip().splitlines()[0] if out.strip() else ""
    except Exception as e:
        return False, str(e)[:60]


def project_dir(argv):
    """Where a project-scoped install would live.

    Defaults to the current directory, which is wrong more often than it looks:
    /bld-setup runs this from the package folder it was cloned into, so a real
    project-scoped install in some other directory read as "nothing installed",
    and the verdict then told a returning user to install everything again.
    Name the project instead:  --project /path/to/your-app

    Returns (path, was_given_explicitly).
    """
    path, explicit, i = os.getcwd(), False, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--project="):
            path, explicit = os.path.abspath(a.split("=", 1)[1]), True
        elif a == "--project" and i + 1 < len(argv):
            path, explicit, i = os.path.abspath(argv[i + 1]), True, i + 1
        else:
            # Never ignore an argument we do not understand. A typo'd flag that
            # silently falls back to the current directory recreates the exact
            # bug --project exists to fix, and does it invisibly.
            sys.exit("preflight: unrecognised argument %r\n"
                     "usage: preflight.py [--project <dir>]" % a)
        i += 1
    return path, explicit


def read_state():
    """Return (state_dict, status) where status is "none", "ok" or "broken".

    A corrupt state file used to be indistinguishable from no state file at
    all: both produced {} and a "FIRST RUN. No prior setup recorded" verdict,
    followed by a "state file: none yet" line naming a path sitting right there
    on disk. Phase 5 writes this file incrementally *during* the install, so a
    crash mid-write is its designed failure mode rather than an exotic one, and
    the result was a silent full reinstall over a half-finished one.
    """
    if not os.path.isfile(STATE):
        return {}, "none"
    try:
        data = json.load(io.open(STATE, encoding="utf-8"))
    except Exception:
        return {}, "broken"
    # A file holding a bare list or string parses fine and then fails on every
    # .get() below, so type-check here rather than crashing 200 lines later.
    if not isinstance(data, dict):
        return {}, "broken"
    return data, "ok"


def disk_summary(evidence):
    """What the machine itself proves, for when the state file cannot be read."""
    on = sorted(g for g, ok in evidence.items() if ok)
    off = sorted(g for g, ok in evidence.items() if not ok)
    print("  On disk now : " + (named(on) if on else "nothing"))
    print("  Not here    : " + (named(off) if off else "nothing"))


def expected_bld_names():
    """{"friendly": {folder names...}, "pro": {...}}, or {} if unknown.

    The canonical table lives in the professional-settings skill. That skill is
    a sibling of this one in BOTH layouts (the package, and ~/.claude/skills
    after install) and is one of the few whose own name never changes between
    modes, so this relative path holds either way.

    Reading names beats counting folders. The old count came from listing the
    package's own skills/ directory, which had two failure modes: an unrelated
    bld-* folder on the machine silently stood in for a skill that never copied,
    and when preflight ran from an installed copy the same walk landed on
    ~/.claude/skills itself, comparing the install to itself.
    """
    table = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                         "bld-professional-settings", "scripts", "switch-mode.py")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bld_switch_mode", table)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {"friendly": set(f for _, f, _ in mod.SKILLS.values()),
                "pro": set(p for _, _, p in mod.SKILLS.values())}
    except Exception:
        return {}


def installed_plugins():
    """Plugin names whose files are actually on disk.

    settings.json's enabledPlugins records intent only: a plugin whose download
    failed, or whose cache was deleted later, still sits in that list forever.
    Claude Code writes the real install path into the plugin registry, so check
    that the directory it names is still there.
    """
    reg = os.path.join(CLAUDE, "plugins", "installed_plugins.json")
    out = set()
    try:
        data = json.load(io.open(reg, encoding="utf-8")).get("plugins", {})
    except Exception:
        return out
    for key, entries in data.items():
        if not isinstance(entries, list):
            entries = [entries]
        for e in entries:
            if isinstance(e, dict) and os.path.isdir(e.get("installPath") or ""):
                out.add(key.split("@")[0])
    return out


# Only WSL inherits the Windows PATH, and only there is a /mnt/... hit a Windows
# binary rather than an ordinary mounted disk. Gating on this keeps a Linux box
# with tools under /mnt/data from having them declared missing.
try:
    with open("/proc/version") as _f:
        _WSL = "microsoft" in _f.read().lower()
except OSError:
    _WSL = False


def slist(state, key):
    """A list field from the state file, defended against the shapes it arrives in.

    The file is written by Claude, not by a schema, so `"chose": "bld"` is a
    plausible slip and is valid JSON. Iterated straight, it reads out as three
    groups named 'b', 'l' and 'd' and the resume branch dutifully offers to
    install them. Anything that is not a list of strings is treated as absent;
    the verdict then names the dropped field rather than printing nonsense.
    """
    v = state.get(key, [])
    if not isinstance(v, list):
        return []
    return [x for x in v if isinstance(x, str)]


def row(label, ok, detail=""):
    mark = "[ok]  " if ok else "[--]  "
    print("  " + mark + label.ljust(20) + detail)
    return ok


def main():
    # Parsed here rather than at module level. At module level this ran on
    # import, so anything that imported preflight - a test, another script -
    # got its OWN argv parsed and sys.exit'd out from under it.
    project, project_given = project_dir(sys.argv[1:])

    # Read before anything else. The state file sits at a fixed path, and it
    # remembers which project a scoped install went into. Without that, anyone
    # who scoped BLD to one project had to remember --project on every future
    # run, and forgetting it reported a healthy install as
    # "MISSING NOW: bld, core-skills, plugins ... Uninstalled, or a fresh
    # machine reusing an old state file."
    state, state_status = read_state()
    project_from_state = False
    if not project_given and isinstance(state.get("project"), str) and state["project"]:
        project, project_from_state = os.path.abspath(state["project"]), True

    # ── 1. prerequisites ────────────────────────────────────────────────
    print("\nPREREQUISITES")
    print("  Without these the install cannot start.\n")

    blockers = []
    for cmd, why in [("node", "runs the skill installer"),
                     ("npm", "installs the CLI tools")]:
        found = have(cmd)
        if not row(cmd, bool(found), why if not found else ""):
            blockers.append(cmd)
        elif cmd == "node":
            # Present is not the same as usable, which is why there is a Python
            # floor at the top of this file. Node had no equivalent: `npx -y`
            # needs npm 7 (Node 15+) and the skills installer assumes 18, so an
            # ancient Node passed this check and then failed inside npx with an
            # error that reads like a broken third-party package rather than an
            # old runtime. Printed here, under its own row, rather than after
            # the loop, where it read as a note about npm.
            ok, line = run([found, "--version"])
            major = 0
            if ok and line.startswith("v"):
                head = line[1:].split(".")[0]
                major = int(head) if head.isdigit() else 0
            if major and major < 18:
                print("        this is %s, and Node 18+ is expected. `npx -y`" % line)
                print("        needs npm 7 and the skills installer assumes 18.")
                print("        Upgrade at nodejs.org first, or every failure")
                print("        lands inside npx looking like someone else's bug.")

    # git is NOT a hard blocker. Core skills, plugins, BLD itself and the React
    # tools all install without it. It only gates deploy and the two suites that
    # arrive by clone. Treating it as fatal turned an optional feature into a
    # wall, and anyone hitting it got the package some other way (a ZIP), which
    # already proves they got this far without git.
    has_git = bool(have("git"))
    row("git", has_git, "" if has_git else "OPTIONAL - only gates deploy, gstack and impeccable")

    # python is obviously present (it is running this), note it for completeness
    row("python", True, "")

    print("\n  Optional, each unlocks one thing:\n")
    has_uv = bool(have("uv")) or bool(have("pipx"))
    # "only /bld-runtime-tokens" was true on Windows and wrong on Linux. A
    # minimal Debian or Ubuntu ships python3 with no pip at all - measured on
    # Ubuntu 26.04, `python3 -m pip` answers `No module named pip` - so the
    # code-search group needs one of these too, and naming just the token
    # monitor sends people past the row that would have unblocked them.
    row("uv or pipx", has_uv, "" if has_uv else
        "needed for /bld-runtime-tokens, and for code search where pip is absent"
        " -> astral.sh/uv, or apt install pipx")

    # gstack's own `setup` is a bun script and refuses to run without it. Nothing
    # else in BLD needs bun, so it is optional - but a missing bun is worth
    # naming HERE, because the failure downstream is misleading: setup exits 1,
    # the prune that follows finds no wrappers to remove, and prints
    # "pruned 0 gstack wrappers" - which the skill reads as a stale matcher
    # rather than a runtime that was never installed.
    has_bun = bool(have("bun"))
    row("bun", has_bun, "" if has_bun else "needed for gstack only -> npm i -g bun")

    # ── 2. deploy accounts ──────────────────────────────────────────────
    print("\nDEPLOY TOOLING")
    print("  Needed only if you want /bld-util-deploy (private repo + live URL).\n")

    # winget installs gh here and does not always put it on PATH straight away, so
    # the absolute path is a legitimate fallback. Say when it was the only hit,
    # though: every later step calls a bare `gh`, which still fails until the
    # shell picks up the new PATH. Reporting a plain "ok" there sends people to
    # debug `gh auth login` instead of restarting their terminal.
    gh_on_path = have("gh")
    # An absolute path ignores PATH by design, which is the point for a user and
    # a problem for the scenario suite: a fake machine built under a temp HOME
    # still finds the host's real, signed-in gh here, so "a machine without gh"
    # could not be expressed as a test at all. The override lets scenarios.py
    # point it at nothing. Users never set it.
    gh_fallback = os.environ.get("BLD_GH_PATH", r"C:\Program Files\GitHub CLI\gh.exe")
    gh_path = gh_on_path or (gh_fallback if os.path.exists(gh_fallback) else None)
    gh_authed = False
    if gh_path:
        gh_authed, line = run([gh_path, "auth", "status"])
        auth = "signed in" if gh_authed else "NOT SIGNED IN -> gh auth login"
        if not gh_on_path:
            # Both facts matter and they are independent: Phase 2 needs to know
            # whether they are authenticated, and every later step calls a bare
            # `gh` that will not resolve until the shell is restarted.
            row("gh", True, auth + ", but NOT on PATH -> restart the shell")
        else:
            row("gh", True, auth if gh_authed else "INSTALLED BUT " + auth)
    else:
        row("gh", False, "not installed -> cli.github.com")

    v_authed = False
    if have("vercel"):
        # The vercel CLI takes ~10s just to boot on a cold start. A short
        # timeout here reports a signed-in user as signed out, which sends
        # everyone down a login rabbit hole they did not need.
        v_authed, line = run([have("vercel"), "whoami"], timeout=45)
        row("vercel", True, "signed in" if v_authed else "INSTALLED BUT NOT SIGNED IN -> vercel login")
    else:
        row("vercel", False, "not installed -> npm i -g vercel")

    # ── 3. inventory ────────────────────────────────────────────────────
    print("\nALREADY INSTALLED BY BLD")

    # BLD can live globally (~/.claude/skills) or scoped to one project
    # (<project>/.claude/skills). Checking only the first reports a working
    # project-scoped install as "nothing installed".
    present = set()
    scopes = []
    for label, d in (("global", os.path.join(CLAUDE, "skills")),
                     ("project", os.path.join(project, ".claude", "skills"))):
        if os.path.isdir(d):
            found = set(os.listdir(d))
            present |= found
            if any(s.startswith("bld-") for s in found):
                scopes.append(label)
    scope_src = ""
    if project_from_state:
        scope_src = "  (remembered from your last setup)"
    elif project_given:
        scope_src = "  (--project)"
    # Recognised by a path only the BLD package has. During setup `project`
    # defaults to the package folder, and the package ships its own CLAUDE.md,
    # which used to read as the user's installed workspace rules.
    project_is_package = os.path.isfile(
        os.path.join(project, "skills", "bld-setup", "scripts", "preflight.py"))
    if project_is_package and not (project_given or project_from_state):
        scope_src += "  (the package folder, not a workspace)"
    print("  project scope checked: " + os.path.join(project, ".claude") + scope_src)
    project_missing = (project_given or project_from_state) and not os.path.isdir(project)
    if project_missing:
        print("  !! that directory does not exist. Everything below will read as")
        print("     'not installed' whether it is or not.")
        if project_from_state:
            print("     It came from the state file, so the project was moved or")
            print("     deleted since setup. Re-run with --project <new path>.")
        else:
            print("     Check the --project path.")

    core_have = [s for s in CORE_SKILLS if s in present]
    bld_names = set(s for s in present if s.startswith("bld-"))
    bld_have = sorted(bld_names)

    # Which bld-* skills SHOULD be there, by NAME, in whichever naming mode this
    # machine is in. Comparing sets rather than counts is the point: a count let
    # any unrelated bld-* folder cover for a skill that never copied.
    expected = expected_bld_names()
    bld_strays = []
    bld_unknown = []
    bld_missing = []
    bld_expected = 0
    mode_note = ""
    if expected:
        # Whichever mode is closer to what is on disk is the one being run. A
        # tree that matches neither is usually a half-finished mode switch, and
        # naming the leftovers from the nearer mode is the useful thing to say.
        best = min(expected, key=lambda m: len(expected[m] - bld_names))
        bld_missing = sorted(expected[best] - bld_names)
        bld_expected = len(expected[best])
        mode_note = best
        # Folders belonging to the OTHER mode are the tell. Without naming them
        # the row reads "13 of 23 MISSING ..." on a machine that has all 23
        # folders, and the obvious remedy - re-copy BLD - restores the missing
        # names while leaving these, so the user ends up with both sets and
        # double the context cost.
        other = "pro" if best == "friendly" else "friendly"
        bld_strays = sorted((bld_names & expected[other]) - expected[best])
        # A third category, and the one nothing used to catch: a bld-* folder in
        # NEITHER naming mode. `cp` adds and overwrites but never removes, so a
        # skill dropped from the package since their last install sits there
        # forever, costing context every session, and every re-run walks past it.
        bld_unknown = sorted(bld_names - expected["friendly"] - expected["pro"])
    gstack_have = "gstack" in present
    impec_have = "impeccable" in present

    print("")
    row("core skills", len(core_have) == len(CORE_SKILLS),
        "%d of %d" % (len(core_have), len(CORE_SKILLS)))
    # The bld group installs the skills AND the bld-executor agent, so both have
    # to be there for the group to count as done.
    # Check both scopes, exactly as the skill inventory above does. A
    # project-scoped install puts the agent in <project>/.claude/agents/, and
    # looking only in the home directory reported a working install as broken.
    agent_have = any(
        os.path.isfile(os.path.join(d, "agents", "bld-executor.md"))
        for d in (CLAUDE, os.path.join(project, ".claude")))
    bld_ok = bool(bld_names) and not bld_missing and agent_have
    if not bld_have:
        bld_note = "none"
    elif bld_expected:
        bld_note = "%d of %d (%s, %s mode)" % (
            len(expected[mode_note] & bld_names), bld_expected,
            "+".join(scopes), mode_note)
        if bld_missing:
            bld_note += "  MISSING: " + ", ".join(bld_missing[:4])
            if len(bld_missing) > 4:
                bld_note += " +%d more" % (len(bld_missing) - 4)
    else:
        bld_note = "%d found (%s), expected names unknown" % (
            len(bld_have), "+".join(scopes))
    row("bld-* skills", bld_ok, bld_note)
    if bld_unknown:
        print("        %d bld-* folder(s) the package does not ship: %s%s"
              % (len(bld_unknown), ", ".join(bld_unknown[:3]),
                 ", ..." if len(bld_unknown) > 3 else ""))
        print("        Dropped from BLD since their last install, or their own.")
        print("        Copying BLD again will not remove them. Say so and let")
        print("        them choose; do not delete anything on their behalf.")
    if bld_strays:
        print("        %d folder(s) use the other naming mode: %s%s"
              % (len(bld_strays), ", ".join(bld_strays[:3]),
                 ", ..." if len(bld_strays) > 3 else ""))
        print("        That is a naming switch that stopped partway. Finish it")
        print("        with /bld-professional-settings. Do NOT re-copy BLD: that")
        print("        restores the missing names and leaves these, giving you")
        print("        both sets and twice the context cost.")
    row("gstack", gstack_have, "")
    row("impeccable", impec_have, "")

    settings = os.path.join(CLAUDE, "settings.json")
    enabled = {}
    if os.path.isfile(settings):
        try:
            enabled = json.load(io.open(settings, encoding="utf-8")).get("enabledPlugins", {})
        except Exception:
            pass
    # A plugin counts as installed only when it is BOTH enabled in settings and
    # present on disk. Enabled-only was the old test, and it reported a plugin
    # that failed to load as fine. Exact key match, too: `startswith` let a
    # `ponytail-something@...` key answer for `ponytail`.
    on_disk = installed_plugins()
    enabled_names = set(k.split("@")[0] for k in enabled)
    plug_have = [p for p in PLUGINS if p in enabled_names and p in on_disk]
    plug_note = "%d of %d" % (len(plug_have), len(PLUGINS))
    for p in PLUGINS:
        if p in enabled_names and p not in on_disk:
            plug_note += "  %s: enabled but not on disk (did not install)" % p
        elif p in on_disk and p not in enabled_names:
            plug_note += "  %s: on disk but not enabled" % p
    row("plugins", len(plug_have) == len(PLUGINS), plug_note)

    cli_have = {}
    for cli in ("react-doctor", "react-scan", "claude-monitor", "jcodemunch-mcp"):
        cli_have[cli] = bool(have(cli))
        row(cli, cli_have[cli], "")

    # Both orchestrator skills fan out to the bld-executor subagent, so a BLD
    # install whose agents/ copy silently failed leaves them broken with nothing
    # reporting why. Cheap to check, and it is the only file that group installs.
    row("bld-executor agent", agent_have,
        "" if agent_have else "MISSING - the orchestrator skills cannot run without it")

    # Phase 8 offers these two rather than installing them, so they are groups
    # like any other: recorded in done/declined, and re-offered by Phase 6 only
    # when they are in neither. Two slugs, not one - the picker lets someone take
    # the machine-wide rules and skip the workspace ones, or the reverse.
    claudemd_global  = os.path.isfile(os.path.join(CLAUDE, "CLAUDE.md"))
    # The package folder ships its OWN CLAUDE.md - a guide for people working on
    # BLD, not the workspace rules Phase 8 offers - and during setup the package
    # folder is exactly what `project` defaults to, because nobody has passed
    # --project yet. So every first run read "the workspace rules are already
    # installed", Phase 8 had no reason to offer them, and the user silently
    # never got the file. Recognise the package by a path only it has.
    claudemd_project = (not project_is_package
                        and os.path.isfile(os.path.join(project, "CLAUDE.md")))
    row("~/.claude/CLAUDE.md", claudemd_global, "")

    # What the disk actually proves, keyed by the group slugs written to
    # .bld-setup.json. Used below to catch a state file that claims a group
    # finished when it did not. Only `prereqs` has no reliable on-disk
    # signature and is deliberately absent rather than guessed at.
    evidence = {
        "core-skills":   len(core_have) == len(CORE_SKILLS),
        "bld":           bld_ok,
        "plugins":       len(plug_have) == len(PLUGINS),
        "react-tools":   cli_have["react-doctor"] and cli_have["react-scan"],
        "token-monitor": cli_have["claude-monitor"],
        "gstack":        gstack_have,
        "impeccable":    impec_have,
        "deploy":        bool(gh_path) and bool(have("vercel")),
        # Two of the three code-search servers run through `npx -y` at query
        # time and install nothing, so the whole group reduces to jcodemunch,
        # which does put a binary on PATH. This was listed as having no on-disk
        # signature, which meant a group offered in Phase 3 could never be
        # confirmed and sat in "Still to do" forever.
        "mcp":           cli_have["jcodemunch-mcp"],
        # The "agents" group is the EXTERNAL executor CLIs (Codex or Gemini)
        # that /bld-runtime-agents drives. It is NOT the bundled bld-executor
        # subagent file, which arrives with the bld group. Checking that file
        # here made a resume conclude Codex was installed because an unrelated
        # markdown file had been copied.
        "agents":        bool(have("codex")) or bool(have("gemini")),
        "claude-md-global":    claudemd_global,
        "claude-md-workspace": claudemd_project,
    }

    # ── 4. verdict ──────────────────────────────────────────────────────
    # state was read at the top of main(), before the project path was needed.

    print("\nVERDICT")
    # Every branch below reasons from what it could see. If the project it was
    # told to look in is not there, it saw nothing, and each branch has its own
    # confident wrong explanation for that ("Uninstalled, or a fresh machine").
    # Say it once, up front, rather than in five places.
    if project_missing:
        print("  !! The project directory checked above does not exist, so any")
        print("     project-scoped install is invisible to this run. Treat every")
        print("     'missing' below as unproven until that path is fixed.")
        print("")
    if blockers:
        print("  BLOCKED: install " + ", ".join(blockers) + " first, then re-run.")
        print("    node + npm : nodejs.org (npm ships with node)")
        sys.exit(1)

    if not has_git:
        print("  LIMITED: git is missing, so these are unavailable for now:")
        print("    /bld-util-deploy, gstack, impeccable")
        print("    Everything else installs fine. Add git later: git-scm.com")
        print("")

    if state_status == "broken":
        print("  STATE FILE UNREADABLE. It exists, but is not valid JSON:")
        print("    " + STATE)
        print("  Most likely a setup that was interrupted while writing it.")
        print("  This is NOT a fresh machine. Do not run the full flow blind.")
        disk_summary(evidence)
        print("  -> Treat 'On disk now' as done. Ask about the rest rather")
        print("     than installing it: the record of what they declined went")
        print("     with the file. Then rewrite the state file from disk.")
    elif not state:
        # No state file is not the same as nothing installed. A hand install, a
        # deleted dotfile, or a state file that never got written all land here,
        # and the old code told every one of them to reinstall a working setup.
        proof = [g for g in BLD_PROOF if evidence.get(g)]
        # status "ok" here means the file parsed but held {}. Saying "no state
        # file" about a file that exists sends someone looking for the wrong
        # thing, so name what actually happened.
        empty = state_status == "ok"
        if proof:
            print("  %s, but BLD is already on this machine."
                  % ("STATE FILE IS EMPTY" if empty else "NO STATE FILE"))
            print("  Installed by hand, or the state file was %s."
                  % ("emptied" if empty else "deleted"))
            disk_summary(evidence)
            print("  -> Do NOT re-run the full flow. Offer what is not here,")
            print("     ask rather than assume, then write the state file.")
        else:
            print("  FIRST RUN. No prior setup recorded.")
            print("  -> Run the full flow from Phase 1.")
    elif not state.get("completed"):
        done = slist(state, "done")
        print("  RESUMING an unfinished setup.")
        print("  Done so far : " + (", ".join(done) if done else "nothing yet"))
        print("  Chose       : " + ", ".join(slist(state, "chose")))
        # A group name Phase 4 has no step for can never leave "Still to do".
        # That already happened once with a real slug (mcp, offered in Phase 3
        # with no install step); a typo or an invented name does the same thing.
        # A key that is present but not a list of strings has been dropped by
        # slist(), so it reads as empty here rather than as whatever it was.
        # Say which key, or the resume looks like it simply chose nothing.
        malformed = [k for k in ("chose", "done", "declined")
                     if k in state and not slist(state, k) and state[k]]
        if malformed:
            print("  !! UNREADABLE FIELDS: " + ", ".join(malformed))
            print("     Present in the state file but not a list of strings,")
            print("     so they were ignored. Rewrite the file from the disk")
            print("     inventory above rather than trusting the lines below.")
        unknown = [g for g in slist(state, "chose") + slist(state, "done")
                   if g not in evidence and g != "prereqs"]
        if unknown:
            print("  !! NOT REAL GROUP NAMES: " + ", ".join(sorted(set(unknown))))
            print("     Phase 4 has no step for these, so they can never")
            print("     finish. Fix the state file before continuing.")
        # A crash between installing and writing leaves the state file lying in
        # both directions, so trust the disk over the claim.
        unproven = [g for g in done if evidence.get(g) is False]
        # The disk can also be AHEAD of the state file. A crash after a group
        # installed but before `done` was appended left it looking unfinished
        # forever, and the resume reinstalled it - re-cloning gstack, re-adding
        # plugin marketplaces. The comment above always claimed both directions;
        # only one was implemented.
        already = [g for g in slist(state, "chose")
                   if g not in done and evidence.get(g) is True]
        remaining = [g for g in slist(state, "chose")
                     if g not in done and g not in already] + unproven
        print("  Still to do : " + (named(remaining) if remaining else "finish up + restart"))
        if already:
            print("  ALREADY DONE: " + named(already))
            print("                installed, but the state file never recorded")
            print("                it. Skip these and just add them to `done`.")
        if unproven:
            print("  RECHECK     : " + named(unproven))
            print("                marked done, but not found on disk. The state")
            print("                file is wrong. Re-install these, do not skip them.")
        # This instruction exists twice - here and in SKILL.md's verdict table -
        # and this is the copy the session actually reads. They said "Skip Phases
        # 1-3" while deploy's only install step IS Phase 2, so the resume was
        # told to skip the phase it was being sent to. Keep both wordings in step.
        print("  -> Skip Phases 1 and 3. Pick up at the first item in 'Still to do'.")
        if "deploy" in remaining:
            print("     deploy is the exception: its step is Phase 2, not Phase 4,")
            print("     so go there for it. They already said yes - do not re-ask.")
        else:
            print("     Skip Phase 2 as well: deploy is not in the list above.")
    else:
        declined = slist(state, "declined")
        print("  RETURNING USER. Setup was completed on " + str(state.get("completed_on", "?")) + ".")
        print("  Previously declined: " + (", ".join(declined) if declined else "nothing"))
        # "Absent" has two causes and they need opposite responses. A group that
        # was recorded done and is gone today really did vanish. A group in
        # neither list was never answered at all - which is what an interrupted
        # run leaves behind for every phase it did not reach, Phase 8's two rule
        # files most of all. Reporting those as "uninstalled, or a fresh machine"
        # tells someone their setup broke when it simply never got that far.
        done_once = slist(state, "done")
        absent = [g for g, ok in sorted(evidence.items())
                  if ok is False and g not in declined]
        gone = [g for g in absent if g in done_once]
        never = [g for g in absent if g not in done_once]
        if gone:
            print("  MISSING NOW : " + named(gone))
            print("                completed once, absent today. Uninstalled, or a")
            print("                fresh machine reusing an old state file.")
        if never:
            print("  NEVER SET UP: " + named(never))
            print("                in neither `done` nor `declined`, so it was never")
            print("                answered - usually a run that ended early. Offer")
            print("                these, then record the answer either way.")
        print("  -> Do NOT re-run the full flow. Offer only what is missing or was declined.")

    # Six commands across Phases 0c, 4, 8 and 9 interpolate the package path, and
    # a resuming session has no other way to know it: it did not just clone
    # anything and may be running from anywhere. Surfacing it here means the
    # resume reads one report instead of opening the state file separately.
    pkg = state.get("package") if isinstance(state, dict) else None
    if isinstance(pkg, str) and pkg:
        print("\n  package   : " + pkg
              + ("" if os.path.isdir(pkg) else "   <- GONE, ask where they moved it"))

    if state_status == "ok":
        print("\n  state file: " + STATE)
    elif state_status == "broken":
        print("\n  state file: " + STATE + "   <- UNREADABLE, see verdict")
    else:
        print("\n  state file: none yet (" + STATE + ")")


if __name__ == "__main__":
    main()
