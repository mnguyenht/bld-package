---
name: bld-util-deploy
description: Deploy an app in this workspace to a private GitHub repo + Vercel with auto-deploy on push. Use when the user says /bld-util-deploy, "deploy this", "put this online", or "get me a share link".
---

# Deploy an app (GitHub → Vercel)

Take an existing local app folder and put it online with a shareable
`*.vercel.app` URL.

## First: is this app ALREADY deployed?

Check for `<app>/.vercel/project.json` (and a git remote). **If it exists, skip the
whole first-time sequence below — "deploy" now just means push the current changes:**

```bash
git -C <app> add -A
git -C <app> status --short          # sanity: no real .env/secret staged
git -C <app> commit -m "<what changed>"
git -C <app> push                    # auto-redeploys via the connected repo (~30s)
```

Then verify the new build actually went live (the production alias sometimes lags):

```bash
vercel ls <app> --cwd <app>            # newest deployment should be ● Ready
# If the alias is stale, promote the deployment that is ALREADY built:
vercel promote <deployment-url> --yes --cwd <app>

# `vercel --prod` is NOT a promote. It uploads and builds whatever is on disk
# right now, which is only the same thing if the working tree matches the commit
# that was pushed. Reach for it to deploy, never to fix a stale alias.
```

That's the entire job for an established app. The rest of this file is **first-time
setup only**.

> Note: `git push` already redeploys — you do **not** run `/bld-util-deploy` after every
> change. Deploy is an explicit, user-requested step (see the deploy-discipline rule
> in the workspace `CLAUDE.md`). Develop and verify locally; ship when the user says so.

## Ground rules

- Repos go on the **personal account `<your-github-username>`** — NEVER a free-plan org
  (Vercel's free Hobby plan refuses private org repos; personal private repos work).
- Repo naming: **`<appname>`**, always **`--private`**.
- Explain each approval-required command in beginner terms before running it
  (what it does, part by part, read-only vs. modifies).
- Tools live at:
  - `gh`: **use the bare `gh` command.** It is on PATH on every platform after a
    normal install. Only if that genuinely fails on Windows, fall back to
    `C:\Program Files\GitHub CLI\gh.exe`, and never hand a macOS or Linux user a
    Windows path.
  - `vercel`: on PATH (npm global)

## Pre-flight checks (read-only)

1. Confirm you're deploying the right folder — ask if ambiguous.
2. `git -C <app> status` — repo exists? uncommitted changes?
3. Check `.gitignore` covers: `node_modules`, `dist`, `.env`, `.env.*`,
   `!.env.example`, `.vercel`. Add what's missing BEFORE the first commit.
4. Verify no secrets are staged (search for API keys in tracked files if `.env`
   handling looks off).
5. Auth sanity (only if something fails later): `gh auth status`, `vercel whoami`.

## The sequence

Run from the workspace root, using `-C <app>` / `--cwd <app>`:

```bash
# 1. Version control (skip any step already done)
git -C <app> init -b main
git -C <app> add -A
git -C <app> commit -m "Initial commit"

# 2. Private GitHub repo on personal account + push (one command)
gh repo create <your-github-username>/<app> --private --source=<app> --push

# 3. Create Vercel project — this also auto-connects the GitHub repo
vercel link --yes --project <app> --cwd <app>

# 4. Belt-and-suspenders: confirm git connection (fine if "already connected")
vercel git connect --yes --cwd <app>

# 5. First production deploy → prints the live URL
vercel --prod --yes --cwd <app>
```

## Verify before declaring success

- Deploy output shows an **Aliased** URL like `https://<app>.vercel.app` — that's the shareable link. Give it to the user.
- Confirm the repo is private: `gh repo view <your-github-username>/<app> --json visibility`.
- Ideally prove auto-deploy: push a trivial commit, then `vercel ls <app> --cwd <app>` — a new deployment should appear on its own within ~30s.
- Remind the user: from now on `git push` = redeploy.

## Known gotchas (all hit and solved before)

- **"Failed to connect ... private repository"** → the Vercel GitHub App lacks
  access. Fix: user opens `https://github.com/settings/installations` →
  Vercel → Configure → All repositories. (Org repos additionally need Pro — don't use the org.)
- **PowerShell "running scripts is disabled"** on npm CLIs → user runs
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. Already done on this machine.
- **`winget` not found** → it's not on PATH; use
  `$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe`.
- **Red PowerShell text from git/gh** → often just stderr progress noise, not
  failure. Check exit status / actual output lines like `* [new branch]`.
- **LF/CRLF warnings** from git → harmless on Windows, ignore.
- Vercel auto-appends `.vercel` and `.env*` to `.gitignore` during link — keep it.
