#!/usr/bin/env python3
"""BLD setup preflight: what's here, what's missing, and where we left off.

    python preflight.py

Prints three things:
  1. PREREQUISITES  - the tools without which the install cannot start
  2. INVENTORY      - what BLD has already put on this machine
  3. VERDICT        - first run / resume / returning, and what to do next

Read-only. Installs nothing, changes nothing.

ASCII output only: Windows consoles default to cp1252 and a stray symbol here
would crash the one command that is supposed to tell you what is wrong.
"""

import io
import json
import os
import shutil
import subprocess
import sys

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


def run(args, timeout=15):
    """Return (ok, first-line-of-output). Never raises."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode == 0, out.strip().splitlines()[0] if out.strip() else ""
    except Exception as e:
        return False, str(e)[:60]


def row(label, ok, detail=""):
    mark = "[ok]  " if ok else "[--]  "
    print("  " + mark + label.ljust(20) + detail)
    return ok


def main():
    # ── 1. prerequisites ────────────────────────────────────────────────
    print("\nPREREQUISITES")
    print("  Without these the install cannot start.\n")

    blockers = []
    for cmd, why in [("node", "runs the skill installer"),
                     ("npm", "installs the CLI tools"),
                     ("git", "clones repos, and BLD's deploy skill needs it")]:
        if not row(cmd, bool(have(cmd)), why if not have(cmd) else ""):
            blockers.append(cmd)

    # python is obviously present (it is running this), note it for completeness
    row("python", True, "")

    print("\n  Optional, each unlocks one thing:\n")
    has_uv = bool(have("uv")) or bool(have("pipx"))
    row("uv or pipx", has_uv, "" if has_uv else "needed for /bld-runtime-tokens only")

    # ── 2. deploy accounts ──────────────────────────────────────────────
    print("\nDEPLOY TOOLING")
    print("  Needed only if you want /bld-util-deploy (private repo + live URL).\n")

    gh_path = have("gh") or (r"C:\Program Files\GitHub CLI\gh.exe"
                             if os.path.exists(r"C:\Program Files\GitHub CLI\gh.exe") else None)
    gh_authed = False
    if gh_path:
        gh_authed, line = run([gh_path, "auth", "status"])
        row("gh", True, "signed in" if gh_authed else "INSTALLED BUT NOT SIGNED IN -> gh auth login")
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
                     ("project", os.path.join(os.getcwd(), ".claude", "skills"))):
        if os.path.isdir(d):
            found = set(os.listdir(d))
            present |= found
            if any(s.startswith("bld-") for s in found):
                scopes.append(label)

    core_have = [s for s in CORE_SKILLS if s in present]
    bld_have = sorted(s for s in present if s.startswith("bld-"))
    gstack_have = "gstack" in present
    impec_have = "impeccable" in present

    print("")
    row("core skills", len(core_have) == len(CORE_SKILLS),
        "%d of %d" % (len(core_have), len(CORE_SKILLS)))
    row("bld-* skills", bool(bld_have),
        "%d found (%s)" % (len(bld_have), "+".join(scopes)) if bld_have else "none")
    row("gstack", gstack_have, "")
    row("impeccable", impec_have, "")

    settings = os.path.join(CLAUDE, "settings.json")
    enabled = {}
    if os.path.isfile(settings):
        try:
            enabled = json.load(io.open(settings, encoding="utf-8")).get("enabledPlugins", {})
        except Exception:
            pass
    plug_have = [p for p in PLUGINS if any(k.startswith(p) for k in enabled)]
    row("plugins", len(plug_have) == len(PLUGINS), "%d of %d" % (len(plug_have), len(PLUGINS)))

    for cli in ("react-doctor", "react-scan", "claude-monitor"):
        row(cli, bool(have(cli)), "")

    row("~/.claude/CLAUDE.md", os.path.isfile(os.path.join(CLAUDE, "CLAUDE.md")), "")

    # ── 4. verdict ──────────────────────────────────────────────────────
    state = {}
    if os.path.isfile(STATE):
        try:
            state = json.load(io.open(STATE, encoding="utf-8"))
        except Exception:
            state = {}

    print("\nVERDICT")
    if blockers:
        print("  BLOCKED: install " + ", ".join(blockers) + " first, then re-run.")
        print("    node + npm : nodejs.org (npm ships with node)")
        print("    git        : git-scm.com")
        sys.exit(1)

    if not state:
        print("  FIRST RUN. No prior setup recorded.")
        print("  -> Run the full flow from Phase 1.")
    elif not state.get("completed"):
        done = state.get("done", [])
        print("  RESUMING an unfinished setup.")
        print("  Done so far : " + (", ".join(done) if done else "nothing yet"))
        print("  Chose       : " + ", ".join(state.get("chose", [])))
        remaining = [g for g in state.get("chose", []) if g not in done]
        print("  Still to do : " + (", ".join(remaining) if remaining else "finish up + restart"))
        print("  -> Skip Phase 1-2. Pick up at the first item in 'Still to do'.")
    else:
        declined = state.get("declined", [])
        print("  RETURNING USER. Setup was completed on " + str(state.get("completed_on", "?")) + ".")
        print("  Previously declined: " + (", ".join(declined) if declined else "nothing"))
        print("  -> Do NOT re-run the full flow. Offer only what is missing or was declined.")

    print("\n  state file: " + (STATE if state else "none yet (" + STATE + ")"))


if __name__ == "__main__":
    main()
