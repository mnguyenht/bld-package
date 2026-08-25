---
name: bld-sprint-planning
description: Decide what to build before anything gets built — interview the idea, pressure-test the assumption it rests on, cut it to a shippable v1, and write the durable planning artifacts (PRODUCT.md, planning.md, progress.md). Use when the user says /bld-sprint-planning, "help me plan this", "I have an idea", "what should I build", "plan the next feature", or arrives with a vague idea and no shape. Ends by handing off to /bld-sprint-init. Does not write app code.
---

# bld-planning — what should exist, and what gets cut

Plan mode already exists and it is good at what it does. Be honest about the
difference rather than pretending this replaces it:

| | Answers | Survives the session? |
|---|---|---|
| **Plan mode** | *How do I build this?* Files to touch, order, architecture. | No. It dies with the conversation. |
| **`/bld-sprint-planning`** | *Should this exist, for whom, paid for how, and what is the smallest version?* | Yes. Three files on disk. |
| **`gstack-spec`** | *What exactly must this code do?* A precise engineering spec. | Yes, but it is ~32k tokens to invoke. |

Use this one **before** plan mode, not instead of it. It stops upstream of code:
no files scaffolded, no components written. If the user starts describing
implementation, note it in the backlog and steer back.

> **When to skip it entirely.** A bug fix, a copy change, a one-screen tweak, or
> anything the user has already decided. Planning a two-line change is theatre.
> Say "this doesn't need a planning pass" and just do the work.

## The one rule that outranks everything here

> **Never invent a fact to fill a gap.**

Prices, competitor claims, market sizes, user counts, testimonials, "studies
show" — if the user did not say it and you did not verify it, it does not go in
the file. Write **`[NEEDS INPUT]`** instead, and keep a list of them.

This matters more in planning than anywhere else, because a planning document is
the thing everything downstream trusts. A plausible invented price gets built into
a pricing page, then into copy, then quoted back to a real customer. A
`[NEEDS INPUT]` is a task; a fabricated number is a landmine.

## Phase 0 — what kind of planning is this

Three shapes, and they run differently. Ask if it is not obvious:

| Shape | Signal | Where to start |
|---|---|---|
| **New idea** | "I want to build…", or no idea at all yet | Phase 1, the whole way through |
| **New feature** on a live app | "should I add…" | Read the existing `planning.md` + `PRODUCT.md` first, then Phase 2 only |
| **Rescue** | "this isn't working", "nobody uses it" | Phase 3 first. The problem is almost always an assumption, not a missing feature. |

**If there is no idea yet**, that is a legitimate starting point and this skill's
job. Do not demand one. Pull on what they already have: what they are annoyed by,
what they do manually every week, who they already have access to. The best small
app is usually downstream of an annoyance the builder personally has, because that
is the only market they can reach for free.

## Phase 1 — the existence ladder

Before scoping anything, climb this. Stop at the first rung that holds, and say so
in one line rather than writing an essay about it.

1. **Does this need to exist?** If the honest answer is "probably not, but I want
   to build it to learn X" — that is a fine answer. Write it down as the goal,
   because it changes every later decision. Learning projects should optimise for
   interesting, not for market fit, and pretending otherwise wastes both.
2. **Does it already exist, free, and good?** Look. If a well-known free tool does
   this, the plan needs a reason it loses. "Theirs is ugly" is a real reason.
   "Mine will have more features" is not.
3. **Is it a feature, not a product?** Many ideas are one screen bolted onto
   something that already exists. That is not a criticism, it is a scope
   reduction, and it usually makes the thing shippable this week.
4. **Can it be one screen?** Most first versions can. Say what the one screen is.

## Phase 2 — the interview

Ask upfront, not at the end. This is the documented exception to "ask last":
nothing should get built before direction is set, and a design system generated
from a guess has to be regenerated.

Batch it. **Two `AskUserQuestion` rounds, not twenty messages.** Fire a
`PushNotification` with each, since these block and the user may have walked off.

### Round 1 — the five that decide everything

1. **Who is the one person this is for?** Push back on "everyone", "students",
   "small businesses". Push until it is a person you could picture. Vague audience
   is the single most reliable predictor that an app gets built and then goes
   unused, because you cannot design for an average.
2. **What do they do about this today?** There is always an incumbent, even if it
   is a spreadsheet, a group chat, or nothing. Name it. You are not competing with
   an empty space, and "nothing" is the toughest incumbent of all — it is free and
   already installed.
3. **What is the one job it does?** One sentence. If it did *only* this and
   nothing else, would they still use it? If not, the one job is something else,
   so find it before scoping.
4. **Who pays, how much, at what moment?** This workspace builds apps that could
   make money, so ask it early rather than bolting pricing on later. Three honest
   answers: someone pays *£X at moment Y*; nobody pays and it feeds something
   offline that does; nobody pays and that is fine. All three are valid. **Silence
   is not.** Record which one, because it decides whether accounts, a database,
   and payments are v1 or never.
5. **How does anyone find out it exists?** The step solo builders skip and then
   blame the product for. If the honest answer is "I'll post it once", the plan
   should be sized to that, not to a launch.

### Round 2 — direction and budget

6. **Design direction.** Vibe (playful · serious · minimal · bold), light/dark/
   both, brand colours if any, two or three reference apps they like.
7. **Anti-references.** *What must it not look or feel like?* Ask this explicitly
   — it is the highest-value question in the round and almost nobody volunteers
   the answer. It rules out a whole region of the design space in one line, and
   it later stops the app drifting into whatever the model's default is.
8. **Time budget**, which scales everything downstream:

| Tier | Rough time | What v1 means |
|---|---|---|
| ⚡ **Quick** | ~10–15 min | One polished screen, deployed |
| 🎯 **Standard** | ~30–45 min | All core screens, responsive, on-brand |
| 🏗️ **Thorough** | ~60+ min | Standard plus a real polish pass |

## Phase 3 — pressure-test, then say the uncomfortable thing

This is the phase that earns the skill its place. Plan mode will happily produce
an excellent implementation plan for a bad idea. **Be a skeptic here, then go back
to being helpful.** One short pass, four questions:

1. **The load-bearing assumption.** Which single belief, if false, makes the whole
   thing pointless? Name it out loud. Usually it is "people will bother", and
   usually nobody has checked.
2. **The incumbent test.** Why doesn't the spreadsheet / group chat / doing-nothing
   already win? If the honest answer is "it mostly does", the plan needs to change
   shape, not gain features.
3. **The ten-name test.** Can they name ten real people who would use this? Not ten
   thousand — ten, with names. If not, the audience from Q1 is still too vague,
   and that is fixable right now for free.
4. **The cheapest disproof.** What is the smallest thing that would show this is
   wrong, before writing code? A message to three people usually beats a weekend.

Deliver this as **a few sentences, not a report**, and give a recommendation
rather than a survey. Then respect the answer: if the user hears it and still
wants to build it, that is their call and it is a legitimate one. Build it
properly, note the risk once in `planning.md`, and stop raising it.

## Phase 4 — cut it to v1

Write the full wish list down, then draw a hard line through it. Everything below
the line goes in the backlog, not in the bin, so nothing feels lost.

The cut rule: **v1 is the smallest thing that does the one job from Q3 end to
end.** End to end matters — half of two features is worth nothing; all of one is
a product. Concretely, for v1 default to:

- **No accounts** unless the one job is impossible without them. Auth is the
  single biggest v1 time sink and `localStorage` covers a surprising amount.
- **No database** until data must outlive one browser.
- **No payments** until someone has asked to pay.
- **No settings screen.** Pick sensible defaults; settings are where scope goes to
  hide.
- **Real content, not lorem ipsum**, in the screens that do exist.

Then state the deferred list back as *deferred*, with the trigger that promotes
each one ("accounts when two people need the same data").

## Phase 5 — write the artifacts

Three files, three different jobs. They are not interchangeable and one does not
replace another.

### `PRODUCT.md` — what this is and who it is for

Durable. Changes only when the product changes.

```markdown
# PRODUCT.md — <name>

## Register
<Brand / tool / utility> — one line on what kind of thing this is.

## Users & purpose
Who, specifically. What job they hire it for. What they do today instead.

## Monetization
Who pays, how much, at what moment — or an explicit "nobody, and here is why
that's fine".

## Brand personality
Three adjectives and the emotion it should produce. Voice.

## Visual system (committed — do not reinvent)
Palette, type, light/dark. Points at design-system/MASTER.md once it exists.

## Anti-references
What it must NOT look or feel like. Name names.

## Accessibility
The bar: WCAG AA contrast, keyboard focus, reduced-motion, 44px targets.
```

### `planning.md` — vision, decisions, and the backlog

Durable. **The `## Working backlog` section is mandatory** and is the single home
for the to-do list. No separate `todo.md`; fold stray notes back in.

```markdown
# <name> — planning

## Vision
What it is, in a paragraph a stranger understands.

## Source documents
Any brief, deck, or transcript this derives from — and **which wins on conflict.**

## Decisions
Dated, with who decided. "Price = 120–150 (from <person>, 05/08/2026, via chat.
Authoritative, not inferred.)" Decisions with a source and a date stop getting
relitigated every session.

## Open questions / [NEEDS INPUT]
Every gap from Phase 2 that got no answer. This list is the point.

## The load-bearing assumption
From Phase 3, and how it could be checked cheaply.

## Working backlog
### v1 — the line
- [ ] ...
### Deferred (with the trigger that promotes it)
- [ ] Accounts — when two people need the same data
### Content / assets needed from a human
- [ ] Real photos, real prices, real testimonials — never invented
```

### `progress.md` — where it stands right now

Volatile. Rewritten as work moves. **This is a different file from `planning.md`
and neither replaces the other**: `planning.md` answers *what is the plan*,
`progress.md` answers *what is the state*. Seed it at the end of this skill with
"planned, not started", what is next, and what is blocked.

### `<app>/CLAUDE.md`

Under ~30 lines, written by `/bld-sprint-init` at scaffold time. If the app already
exists, update its **Status** line here instead.

## Phase 6 — hand off

Close with:

1. **The one-sentence version** of what is being built. If you cannot write it,
   planning is not finished.
2. **What v1 contains**, as a short list, and what got deferred.
3. **The `[NEEDS INPUT]` list** — the things only the user can supply, and which
   of them block the build versus which can wait.
4. **The next command.** `/bld-sprint-init` for a new app; plan mode or straight to work
   for a feature on an existing one.

Do not start building in the same turn. Let them read the plan first.

## Pitfalls

- **Filling a gap with a plausible number.** The rule at the top. Every time.
- **Planning a two-line change.** Skip the skill and do the work.
- **Twenty questions.** Two batched rounds. Interrogation kills the idea's energy,
  and a tired user answers "sure, whatever" to everything after round three.
- **Accepting "everyone" as an audience.** Ask again, once, kindly.
- **Skipping the money question** because it is awkward. It decides the
  architecture.
- **Writing an implementation plan.** That is plan mode. Stop at *what* and *why*.
- **Pressure-testing forever.** One pass, a recommendation, then move on. If the
  user has heard the risk and chosen to proceed, that decision is made — build it
  and stop re-arguing it.
- **A backlog with no line through it.** An uncut list is a wish, not a plan.
- **Duplicating the backlog into `progress.md`.** They have different jobs.
