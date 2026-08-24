---
name: bld-strix
description: Run Strix, the autonomous AI pentester, as a DYNAMIC runtime attack pass against one of our own running/deployed apps. Separate and opt-in because it needs Docker running and a paid Anthropic API key (or a free-but-weak OpenRouter key) that the user supplies. Use when the user says /bld-strix, "run strix", "pentest the live app", "dynamic security test", or "attack my deployed app". This is the runtime complement to the static /bld-security pass. Claude never handles a key value — it prints the exact commands for the user to run.
---

# bld-strix — dynamic AI pentest (opt-in, costs money)

[Strix](https://github.com/usestrix/strix) runs attacker agents inside a Docker
sandbox against a **running or deployed** target and produces working
proof-of-concept exploits. It's the only *dynamic* tool in our kit — `/bld-security`
covers all the static/code review; this exercises a live target at runtime.

Split out from `/bld-security` on purpose: Strix needs Docker + a **paid** LLM key,
so running it is a deliberate choice, never automatic.

## Hard rules (do not bend these)

- **Only ever point Strix at an app you own.** Local dir, our GitHub repo, or our
  own `*.vercel.app` deployment. Scanning anything else is unauthorized.
- **Never feed Strix a Claude Code / Pro subscription token.** A Pro subscription
  is not an API key (it won't authenticate Strix), and forwarding session tokens to
  third-party tools is banned by our global rules. Use a purpose-made API key.
- **No unofficial "use my Pro plan as an API" proxies.** They violate Anthropic's
  ToS, match the banned token-forwarding pattern, and risk an account ban.
- **Claude never types a key value.** This skill prints the commands; the user runs
  them so the secret only ever exists in the user's own shell.

## Cost reality — pick the LLM path first

| Path | Cost | Notes |
|------|------|-------|
| Anthropic API key (`anthropic/claude-...`) | 💸 pay-per-token | Best results. A full pentest run is not cheap — set a low spend cap in the console. Separate billing from Pro. |
| OpenRouter free model (`openrouter/...`) | free | Matches our no-paid rule, but an autonomous multi-hour agent hits free-tier rate limits fast → thin results. Smoke test only. |

The Anthropic API key comes from https://console.anthropic.com (it wraps you in an
"Organization" even for personal use — that's just the billing container, still
personal). It is billed independently from any Pro/Max subscription.

## Prerequisites (the gate)

Run in order; stop at the first miss and fix it:

```
1. strix on PATH / at ~/.strix/bin ?
2. Docker installed AND running (`docker info` succeeds) ?
3. STRIX_LLM and LLM_API_KEY both set in this shell ?
```

### 1. Strix binary

Installed via the vetted script → `~/.strix/bin/strix.exe`. If missing, install it
(see the workspace's reviewed `strix-install.sh`, or
https://github.com/usestrix/strix). Verify:

```powershell
strix --version
```

### 2. Docker Desktop

Install: https://docs.docker.com/desktop/install/windows-install/ — launch it, wait
for "running", then verify:

```powershell
docker info
```

### 3. LLM key + model (user sets; Claude never touches the value)

Session-only (vanishes when the window closes — the key is not persisted to disk):

```powershell
# Option A — paid Anthropic API
$env:STRIX_LLM   = "anthropic/claude-sonnet-4-6"
$env:LLM_API_KEY = "sk-ant-...your-console-key..."

# Option B — free OpenRouter (weaker; check docs.strix.ai for exact model id)
$env:STRIX_LLM   = "openrouter/<a-free-model-id>"
$env:LLM_API_KEY = "sk-or-...your-openrouter-key..."
```

To persist across sessions (key then lives in your user environment — only on your
own machine):
`[Environment]::SetEnvironmentVariable("LLM_API_KEY","...","User")`

## Running

```bash
# local codebase
strix --target ./<app-folder>

# our deployed app (only ours)
strix --target https://<appname>.vercel.app
```

Results land in `strix_runs/<run-name>`.

## After the run

1. Read the findings in `strix_runs/<run-name>`.
2. If a `security-report.md` from `/bld-security` exists for this app, **fold Strix's
   PoC findings into it** — dedupe against what the static passes already flagged,
   then re-rank the union by severity. A live PoC outranks a theoretical static hit.
3. Propose fixes; don't auto-apply unless asked (same discipline as `/bld-security`).

## If a prerequisite is missing

Print the specific missing step above and stop — do not try to install a paid key,
do not fall back to a Pro token, do not run against a target we don't own.
