# bld-package — the BLD skillset, packaged for other people

This repo is **not an app.** It is the distributable copy of the `bld-*` skillset:
21 skills, one agent, one hook, two CLAUDE.md templates. Nothing here runs; it is
read by Claude Code on someone else's machine.

- **Users:** people who want the BLD workflow without rebuilding it. Installed via
  `/bld-setup`.
- **Monetization:** none. Public, free, credit-the-sources.
- **Stack:** markdown, plus four helper scripts where the work must be deterministic:
  `bld-setup/scripts/preflight.py` (environment + resume state),
  `bld-professional-mode/scripts/switch-mode.py` (renames every command),
  `bld-optimize-app/scripts/lh-report.mjs` (Lighthouse report reader),
  `bld-runtime-activate-mcps/run.py` (MCP runner).

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
- **Three things must stay in sync:** the credits table in `README.md`, the
  manifest at `skills/bld-setup/references/manifest.md`, and the "What each group
  actually is" table in `bld-setup/SKILL.md` Phase 3. Different readers, same
  facts. **The Phase 3 table is the one users actually consent against**, so a
  `code` row in the manifest that reads as markdown in the picker is a consent
  bug, not a wording slip. It shipped once: the picker called all 11 core skills
  "all markdown" while `a11y-audit` and `webapp-testing` ship executable scripts.
- **Adding a skill? Four places.** Its own `SKILL.md`, the `SKILLS` table in
  `bld-professional-mode/scripts/switch-mode.py` (the canonical taxonomy, and the
  rename breaks without it), the type table in `README.md`, and the routing table
  in `templates/CLAUDE.workspace.md`.
- **Renaming a command?** Add the old name to `LEGACY` in that same script rather
  than editing `SKILLS` in place, so existing installs still migrate.
- **`bld-professional-mode` is exempt from the rename pass** (`NO_REWRITE`). Its docs
  deliberately hold both naming schemes; rewriting them collapsed every example
  into "x becomes x" the first time it ran.
- **Never write a literal `/bld-*` example of the *other* naming mode in any file
  except that one.** Every other doc gets rewritten, so an example like "becomes
  the short name `/bld-refine`" is silently converted to `/bld-sprint-refine` on
  the next mode switch and the sentence ends up contradicting itself. This is not
  hypothetical: it happened to a line in `templates/CLAUDE.workspace.md` within an
  hour of it being written. Describe the shape of the change in words instead of
  naming a command, and the rewriter has nothing to grab.
- **The rename pass rewrites three shapes**, all in `switch-mode.py`: `/command`,
  `skills/<name>/` paths, and the `# <name>` H1 title. The H1 pattern was added
  after 16 of 21 skills were found still carrying their pre-rename titles, since
  a bare name in a heading has neither a leading slash nor a `skills/` prefix.

## Status

21 skills. Naming is prefix-type-skill by default; `/bld-professional-mode on`
switches to short names and the round trip is verified byte-identical.

Verified: `lh-report.mjs` against a live Lighthouse v13.4.1 report, `preflight.py`
on a real machine, `switch-mode.py` across two full round trips.

Not yet run end to end by a real new user: `/bld-setup`. No LICENSE file.
