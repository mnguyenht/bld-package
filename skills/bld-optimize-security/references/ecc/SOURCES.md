# Vendored from ECC — attribution

These checklist files are copied from the **ECC** project by Affaan Mustafa.

- **Repo:** https://github.com/affaan-m/ECC
- **License:** MIT — Copyright (c) 2026 Affaan Mustafa. Full text in `LICENSE`
  beside this file, as MIT requires.
- **Vendored from commit:** `591ab5cbd3f2f65860ea91c226e410b1502c8e2e` (main)
- **Fetched:** 2026-07-29

## Why vendored, not installed

ECC is a ~4,600-file plugin that ships hooks, an MCP server, a GitHub App, and an
npm package. Installing the whole thing conflicts with this workspace's security
posture (pure-markdown skills preferred; MCP on-demand only; foreign hooks never
auto-registered). Every file here is **pure markdown** — instructions Claude reads
and follows. No ECC code executes.

## File-by-file

| File | Source path in ECC | Copied |
|------|--------------------|--------|
| `security-review.md` | `skills/security-review/SKILL.md` | verbatim |
| `cloud-infrastructure-security.md` | `skills/security-review/cloud-infrastructure-security.md` | verbatim |
| `production-audit.md` | `skills/production-audit/SKILL.md` | verbatim |
| `security-bounty-hunter.md` | `skills/security-bounty-hunter/SKILL.md` | verbatim |
| `agent-architecture-audit.md` | `skills/agent-architecture-audit/SKILL.md` | verbatim |
| `agentshield-checklist.md` | `skills/security-scan/SKILL.md` | **adapted** — stripped to checklist-only; the executable `npx ecc-agentshield` scanner is intentionally omitted |

## Deliberately NOT vendored

Framework-specific (`django/laravel/quarkus/springboot/perl-security`) — wrong
stack. ECC-setup meta-skills (`workspace-surface-audit`, `automation-audit-ops`)
— more ECC onboarding than app security. `click-path-audit` — correctness/state
bug finder, not security. To refresh any vendored file, re-fetch from the raw URL
at the commit above.
