# bld-package — the BLD skillset, packaged for other people

This repo is **not an app.** It is the distributable copy of the `bld-*` skillset:
22 skills, one agent, one hook, two CLAUDE.md templates. Almost all of it is
markdown read by Claude Code on someone else's machine. The exceptions are the
five helper scripts below, which do execute, and the manifest lists them as such
because that column is the one users decide on.

- **Users:** people who want the BLD workflow without rebuilding it. Installed via
  `/bld-setup`.
- **Monetization:** none. Public, free, credit-the-sources.
- **Stack:** markdown, plus five helper scripts where the work must be deterministic:
  `bld-setup/scripts/preflight.py` (environment + resume state),
  `bld-professional-settings/scripts/switch-mode.py` (renames every command),
  `bld-mcp-settings/scripts/mcp-settings.py` (edits `.mcp.json` without clobbering it),
  `skills/bld-optimize-app/scripts/lh-report.mjs` (Lighthouse report reader),
  `skills/bld-runtime-activate-mcps/run.py` (MCP runner),
  plus `hooks/block-image-skills.py`, which is a hook rather than a helper.

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
| `hooks/block-image-skills.py` | PreToolUse hook blocking `ui-ux-pro-max:design` and any `banner-design`. Claude Code's own top-level `design` skill is deliberately NOT blocked; it generates no images. `--selftest` asserts both halves |
| `templates/CLAUDE.*.md` | The global + workspace rule layers, sanitised |

## Conventions

- **Folder name and frontmatter `name` must match.** They drifted apart
  historically and the frontmatter won, but every one of the 22 now agrees, and
  `switch-mode.py` relies on that: `detect_mode` treats a BLD skill whose folder
  and declared name disagree as evidence of an interrupted rename, and refuses to
  toggle. Renaming a folder by hand without its frontmatter now jams the mode
  switch.
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
  `bld-professional-settings/scripts/switch-mode.py` (the canonical taxonomy, and the
  rename breaks without it), the type table in `README.md`, and the routing table
  in `templates/CLAUDE.workspace.md`.
- **Renaming a command?** Add the old name to `LEGACY` in that same script rather
  than editing `SKILLS` in place, so existing installs still migrate.
- **`bld-professional-settings` is exempt from the rename pass** (`NO_REWRITE`). Its docs
  deliberately hold both naming schemes; rewriting them collapsed every example
  into "x becomes x" the first time it ran.
- **Never write a literal `/bld-*` example of the *other* naming mode in any file
  except that one.** Every other doc gets rewritten, so a sentence that names a
  command's short form and contrasts it with its type-prefixed form has BOTH
  halves converted to the same string on the next mode switch, and is left
  claiming that a name is silently converted into itself. Worse, the damage is
  permanent: once both halves match, no later switch can tell them apart again.
  This is not hypothetical and it is not rare. It happened to a line in
  `templates/CLAUDE.workspace.md` within an hour of it being written, and then it
  happened to this very rule, whose own worked example was flattened by the pass
  it exists to warn about — caught only because the naming round trip stopped
  coming back byte-identical. Describe the shape of the change in words instead
  of naming a command, and the rewriter has nothing to grab.
- **Run `python check.py` before committing.** Every convention on this page that
  can be checked mechanically, is: folder vs frontmatter names, the folder set
  against the table, a type existing in the code but in neither doc, a skill
  missing from one of the four places, a stated command count that went stale,
  and an other-mode command literal waiting to be flattened. It is the only
  thing standing over `bld-professional-settings`, which nothing else keeps in
  sync. Two of the bugs it now catches are ones it was written after.
- **Run the naming round trip before committing docs.** `switch-mode.py on`, then
  `off`, then `git status`. Anything but a clean tree means the pass is not
  reversible on your text, and the diff shows you exactly which sentence it ate.
  `check.py` catches the known cause; the round trip catches the rest.
- **The rename pass rewrites three shapes**, all in `switch-mode.py`: `/command`,
  `skills/<name>/` paths, and the `# <name>` H1 title. The H1 pattern was added
  after 16 of 21 skills were found still carrying their pre-rename titles, since
  a bare name in a heading has neither a leading slash nor a `skills/` prefix.

## Status

22 skills. **There are exactly two naming conventions and no third:**
prefix-type-skill (default) and prefix-skill-type (pro). Pro reorders; it never
drops a segment. A name missing its type belongs to neither convention — pro mode
shipped that way once, and every one of those names is now in `LEGACY`.
`/bld-professional-settings on` switches, and the round trip is verified
byte-identical.

Verified: `lh-report.mjs` against a live Lighthouse v13.4.1 report, `preflight.py`
on a real machine, `switch-mode.py` across two full round trips.

Not yet run end to end by a real new user: `/bld-setup`. MIT licensed.
