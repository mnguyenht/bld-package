---
name: bld-util-deploy
description: 'ud: Deploy an app to a private GitHub repo + Vercel with auto-deploy on push, and connect a domain the user bought. Use for "deploy this", "put this online", "get me a share link", "connect my domain".'
---

# Deploy an app (GitHub → Vercel)

Take an existing local app folder and put it online with a shareable
`*.vercel.app` URL. Bought a domain for it? That's the **Custom domain**
section near the end, and it runs only when the user asks.

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

## Custom domain (only when the user has bought one)

Buying `example.com` only buys the name. Nothing reaches the app until DNS
(the internet's phone book) says where the name points, and the DNS edits are
the user's: they happen in their registrar's dashboard, not in a CLI Claude
can run. Claude does the Vercel side, then hands over exact steps.

**1. Decide where the app lives. Default: the app IS the site.** Point the
domain straight at it: add `example.com` and `www.example.com`. Vercel
prompts for the `www` one and redirects one to the other.

Put the app on `app.example.com` **only if a separate marketing site already
owns `example.com`** (Framer, Webflow, a second project). Then marketing can
change the homepage without touching the app's repo. With no separate
marketing site, an `app.` subdomain just adds a second address to explain, so
skip it. Ask which case this is; don't assume the split.

**2. Add it on Vercel**, project name passed explicitly (the docs say to pass
it even from a linked folder):

```bash
vercel domains add <domain> <app> --cwd <app>
```

**3. Hand the user the DNS records, copied, never retyped.** The bare domain
(`example.com`, the "apex") gets an **A** record; a subdomain gets a **CNAME**
(an alias pointing at another name). Each Vercel project now has its own
CNAME value, shaped like `d1d4fc829fe7bc7c.vercel-dns-017.com`, so a value
from a tutorial or from another project can be wrong. Copy what this
project's **Settings → Domains** page shows. The records go in the DNS panel
of whoever serves the domain's nameservers. That's usually the registrar, but
not always: find the panel that's actually in charge first.

**4. Don't switch nameservers by default.** Vercel also offers its own
nameservers, which moves the domain's *whole* phone book to Vercel. Every
record not copied over first disappears. **MX** records (where the domain's
email is delivered) are the painful one: email stops arriving, with no error
anywhere the user is looking. TXT records proving ownership to Google Search
Console or Resend go too. Default to adding the A/CNAME records at the current
DNS host. Switch only if the user wants Vercel to run DNS, and only after
copying every existing record across.

**5. Verify, don't assume.** DNS takes minutes, sometimes hours. Then:

```bash
vercel domains verify <domain> --cwd <app>   # says what to fix if it's wrong
```

and open `https://<domain>` once it passes. Once it's live, `/bld-optimize-seo-indexing`
handles the sitemap, canonical URLs and Google Search Console on the new domain.

### Email, only if the app sends it

Password resets, receipts, sign-up confirmations, newsletters. If the app
sends none, skip this whole block.

- **Send from subdomains, never the bare domain, and split them.** One for app
  mail (`mail.example.com`: resets, receipts, sign-ups) and one for marketing
  (`news.example.com`: newsletters, campaigns). Every sending domain builds its
  own spam reputation, so a newsletter people mark as spam drags down only
  `news.`, and password resets keep reaching the inbox. Resend recommends both
  the subdomain and the split.
- **Add each subdomain in Resend** (resend.com → Domains → Add Domain) and paste
  the records from its **Records** tab into the same DNS panel. They're
  **SPF** (the list of servers allowed to send as this domain) and **DKIM** (a
  signature on every email that receivers check against a key in DNS). Without
  them Gmail treats the mail as possibly forged and it lands in spam.
- **Then DMARC**, after the domain verifies: one TXT record at `_dmarc.<domain>`
  telling receivers what to do with mail that fails those checks. Start at
  `v=DMARC1; p=none;` (watch, block nothing), as Resend's DMARC guide says,
  and tighten later.
- **Open and click tracking:** on for marketing mail, off for app mail.
  Tracking rewrites links, which a password-reset email shouldn't have.

End with a **Your turn** list naming each dashboard, the buttons in order, and
which record goes where. The user does every DNS step; Claude never has their
registrar login.

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

## Sources

- Custom domain section: from @buildwithnico's reel "3 things to do after
  buying your domain" (instagram.com/reel/DaSpPVGsu-o): app on a subdomain,
  separate email subdomains with SPF/DKIM/DMARC, then a sitemap. BLD makes the
  `app.` subdomain conditional on a separate marketing site, and adds the
  nameserver/MX warning.
- Vercel: "Adding & Configuring a Custom Domain" (vercel.com/docs, updated
  2026-09-16): A for apex, per-project CNAME for subdomains, copy MX before
  changing nameservers. `vercel domains add` / `verify` from CLI 54.20 `--help`.
- Resend: "Add a domain", "Domains" and "DMARC" docs: send from a subdomain,
  split transactional and marketing, SPF + DKIM records, DMARC starting at
  `p=none`.

Custom domain section checked 2026-11-08, docs-match against those pages. Not
run: it needs a bought domain and the user's registrar.
