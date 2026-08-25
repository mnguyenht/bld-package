# bld-package — the BLD skillset, packaged for other people

This repo is **not an app.** It is the distributable copy of the `bld-*` skillset:
20 skills, one agent, one hook, two CLAUDE.md templates. Nothing here runs; it is
read by Claude Code on someone else's machine.

- **Users:** people who want the BLD workflow without rebuilding it. Installed via
  `/bld-setup`.
- **Monetization:** none. Public, free, credit-the-sources.
- **Stack:** markdown, plus `skills/bld-optimize-sprint/run.py` (MCP runner) and
  `skills/bld-app-optimize/scripts/lh-report.mjs` (Lighthouse report reader).

## The rule that matters here

**Everything in this repo is public.** No names, emails, GitHub handles, client
domains, local paths, or app names. The lessons stay, the identities go: keep
"a fix that passed one scanner was rejected by another (2026-07-29)", drop whose
project it happened on.

Before any commit:

```bash
grep -rniE '<your-name>|<your-handle>|<your-email>|C:.Users|/home/[a-z]' . --include=*.md --include=*.py --include=*.mjs
```

## Where things live

| Path | Holds |
|---|---|
| `README.md` | Public front door: positioning, skills by phase, credits table |
| `skills/bld-*/SKILL.md` | One skill each. Frontmatter `name` + `description` drives invocation |
| `skills/bld-setup/references/manifest.md` | The operational install table, with the trust column |
| `agents/bld-executor.md` | The worker the orchestrator skills fan out to |
| `hooks/block-image-skills.py` | PreToolUse hook blocking `design` / `banner-design` |
| `templates/CLAUDE.*.md` | The global + workspace rule layers, sanitised |

## Conventions

- **Skill folder names may differ from the invoked name.** `bld-react-review/`
  declares `name: bld-react-optimize`. The frontmatter wins; don't "fix" the
  folder to match without checking every cross-reference.
- **House voice:** dense, opinionated, table-first. Every non-obvious rule carries
  its *why*, usually a dated incident. A rule without a reason gets ignored under
  pressure, so the reasons are the point, not padding.
- **The README is marketing copy, so no em dashes there.** The SKILL.md files are
  instructions to a model and follow the existing house style instead.
- **Two things must stay in sync:** the credits table in `README.md` and
  `skills/bld-setup/references/manifest.md`. Different readers, same facts.
- **Adding a skill?** Update three places: its own `SKILL.md`, the phase table in
  `README.md`, and the routing table in `templates/CLAUDE.workspace.md`.

## Status

All 20 skills present. `bld-setup`, `bld-app-optimize` and `bld-planning` are new
and have not been run end to end by a real user yet. `lh-report.mjs` is verified
against a live Lighthouse v13.4.1 report. No LICENSE file yet.
