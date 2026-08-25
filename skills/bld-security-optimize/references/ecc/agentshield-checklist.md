# AgentShield config-security checklist (markdown-only)

> **This is the checklist-only adaptation.** The upstream ECC skill runs an
> executable scanner (`npx ecc-agentshield`). We deliberately do **not** run that
> — this file is the "what to check" so Claude audits our `.claude/` config by
> *reading* it. No third-party code executes. Source: ECC `skills/security-scan`
> (MIT). If you ever want the real automated scanner, that's a separate opt-in
> that must go through the full vetting drill first.

Audit the workspace's own Claude Code configuration — the harness that builds the
apps — because a poisoned config compromises every app it touches. Read each file
and check for the issues below.

## What to scan

| File | Check for |
|------|-----------|
| `CLAUDE.md` (all layers) | Hardcoded secrets, auto-run instructions, prompt-injection patterns, instructions telling Claude to exfiltrate or forward credentials |
| `.claude/settings.json` / `settings.local.json` | Overly permissive allow lists (`Bash(*)`), missing deny lists, dangerous bypass flags (`--dangerously-*`, `bypassPermissions`) |
| `.mcp.json` (should be **absent** here) | Any MCP server at all (this workspace mandates on-demand only), hardcoded env secrets, `npx -y` supply-chain auto-install |
| `.claude/hooks/*` | Command injection via `${var}`/`$FILE` interpolation, data exfiltration (curl/网络 calls to external hosts), silent error suppression (`2>/dev/null`, `\|\| true`) hiding failures |
| `.claude/agents/*.md`, `.claude/skills/*` | Unrestricted tool access, prompt-injection surface, missing model specs, skills that execute code without being flagged |

## Severity guide

**Critical — fix immediately**
- Hardcoded API keys / tokens in any config file
- `Bash(*)` (unrestricted shell) in an allow list
- Command injection in a hook via `${file}` interpolation
- A shell-running MCP server, or credential-forwarding to an external backend

**High — fix before shipping**
- Auto-run instructions in `CLAUDE.md` (a prompt-injection vector)
- Missing deny lists in permissions
- Agents/skills granted Bash they don't need

**Medium — recommended**
- Silent error suppression in hooks (`2>/dev/null`, `|| true`)
- `npx -y` auto-install in an MCP config
- Missing PreToolUse safety hooks where they'd help

**Info — awareness**
- Missing descriptions on skills/servers
- Prohibitive/safety instructions correctly present (flag as *good* practice)

## This workspace's baseline (what "good" looks like here)

- **No `.mcp.json`** — MCP is on-demand only (spawn → query → kill). Its presence is itself a finding.
- `.gitignore` ignores `.env`, `.env.*` (allows `!.env.example`), and `handoff.md`.
- The image-gen block hook (`.claude/hooks/block-image-skills.py`) is intentional, not a finding.
- Third-party skills were meant to be vetted before install (the "drill"). Re-confirm none execute code silently.
