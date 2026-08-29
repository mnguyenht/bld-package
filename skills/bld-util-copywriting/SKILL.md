---
name: bld-util-copywriting
description: Write or rewrite the words in an app we are building — hero headline, subheadline, CTAs, feature sections, empty states, pricing, about. Runs the installed copywriting skill, then applies this workspace's constraints on top: pre-launch apps with no proof to cite, no litotes, no irony, and a hard list of phrasings that read as AI-written. Use when the user says /bld-util-copywriting, "write the copy", "fix this headline", "what should the hero say", "this text sounds like AI", or a screen is built and still holding placeholder words.
---

# bld-util-copywriting

Marketing copy for an app **we** are building. The general craft comes from
someone else's skill; the parts that make it sound like a person, and like this
workspace, live here.

## What this actually runs

The engine is the **`copywriting`** skill by Corey Haines
([coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)),
installed globally by `/bld-setup`. It carries the page frameworks, the CTA
guidance, the above-the-fold structure and the per-page-type advice. None of that
is reproduced here, because a copy of someone else's skill is a copy that goes
stale.

```
Invoke the copywriting skill for the craft  →  apply everything below on top
```

**If `copywriting` is not installed**, say so and offer
`npx -y skills add coreyhaines31/marketingskills --skill copywriting -g -a claude-code --copy`.
Do not silently freestyle the frameworks; the whole point of this file is that it
is a thin layer over a good source.

**Where this file and the source disagree, this file wins.** That happens in
three places, all of them deliberate, all of them below.

## The setting the source does not assume

The source skill is written for a company with customers. It reaches for case
studies, metrics, testimonials and logo walls, because for its usual reader those
exist.

**Ours usually do not.** The apps in this workspace are pre-launch or days old.
They have no users to quote, no numbers to cite, and no press. That single fact
drives most of the adaptation:

| The source suggests | Here instead |
|---|---|
| Social proof, logos, testimonials | Leave the slot out entirely. An empty testimonial section is worse than no section. |
| Concrete metrics ("cut costs 40%") | Describe the mechanism instead: what the app does, in what order, and how long it takes. |
| "Trusted by 10,000 teams" | Nothing. This is the single fastest way to lose a reader who can tell. |
| Founder story / About page depth | One honest line about why it exists, if the user wants an About page at all. |

**Never invent a statistic, a testimonial, a customer name, a rating, or a user
count.** The source already says fabricated proof erodes trust and creates legal
liability. In a workspace shipping to real URLs under the user's own name, treat
it as absolute: if the number is not real, the sentence does not ship. When a
section genuinely needs proof we do not have, say so and propose the section be
cut, rather than filling it.

**Write only about what the app actually does.** Read the screen, the component,
or the route before writing a word about it. Copy describing a feature that was
planned but not built is the same failure as a fake statistic, and it is easier
to commit by accident.

## Ban one: litotes

**Litotes** is saying a thing by denying its opposite. "Not bad" for good. "No
small feat" for hard. "This isn't your average todo app" for whatever it actually
is.

It is banned outright here. Two reasons, and the second is the real one:

1. It makes the reader do arithmetic to reach a plain meaning.
2. It is everywhere in AI-written copy, so it now reads as machine-written even
   when a person wrote it.

The most common form by far is the **"isn't just X, it's Y"** construction. It is
the single strongest tell in the list further down. Kill it on sight.

| Litotes | Say |
|---|---|
| "It isn't just a note app, it's a second brain." | "Notes that link themselves." |
| "Not a bad way to start the week." | "A good way to start the week." |
| "Getting this right is no small feat." | "Getting this right is hard." |
| "You won't be disappointed." | Cut the sentence. It carries nothing. |
| "This is not unlike a spreadsheet." | "It works like a spreadsheet." |

Negation itself is fine. "This does not sync to the cloud" is a plain factual
statement, not litotes, and often the most honest line on the page. The ban is on
negating the opposite to imply a positive.

## Ban two: irony

No saying the opposite of what is meant. No sarcasm, no winking at the reader, no
jokes at the product's own expense, no self-aware asides about being a startup or
about marketing copy itself.

Irony asks the reader to hold two meanings at once and pick the right one. A
first-time visitor deciding in four seconds whether to keep scrolling will not do
that, and a non-native reader may not catch it at all.

Banned in practice:

- "We promise not to spam you. Much."
- "Yes, another productivity app."
- "Revolutionary! (We're being sarcastic.)"
- Placeholder-as-joke copy: "Insert compelling headline here."

**This is not a ban on personality**, and over-correcting into flatness is its own
failure. The source's advice to be direct, to use rhetorical questions, and to use
analogies all still stands. Warmth and plain humor are allowed:

- "Hate chasing approvals?" — a rhetorical question, keep it.
- "Drag a file in. That's the whole setup." — direct and a little dry, keep it.
- "Your files, where you left them." — plain, warm, no second meaning.

The line is whether the sentence means what it says. If it does, it is fine no
matter how light the tone.

## Ban three: the phrasings that read as machine-written

⚠️ **Read this section as a disclaimer, not a style preference.** Copy that trips
these is not merely unfashionable; readers now recognise it as AI output, and the
moment they do, they stop believing the rest of the page. Every item below is
banned in produced copy.

**Punctuation and shape**

- **Em dashes.** Use a comma, a full stop, or a colon. This is a standing
  workspace rule, and it is the fastest visual tell in the list.
- Exactly three of everything. Three adjectives, three bullets, three benefits,
  every time. Vary the counts or cut to two.
- Perfectly parallel bullet lists where every line has the same rhythm.
- Emoji as section markers.

**Constructions**

- "It isn't just X, it's Y." (see litotes above)
- "Whether you're a X or a Y, ..."
- "In today's fast-paced world" and every variant.
- "Think of it as ..."
- "It's that simple." / "Simple as that."
- "Let's dive in." / "Let's take a look."
- Opening a section with a one-word sentence for drama. "Speed." "Focus."

**Vocabulary**

`leverage` · `seamless` · `robust` · `elevate` · `unlock` · `supercharge` ·
`game-changer` · `delve` · `harness` · `empower` · `streamline` · `cutting-edge` ·
`revolutionary` · `effortlessly` · `transform your workflow`

Most of these the source already discourages as vague. Here they are refused
outright rather than weighed.

> **A note on this file's own prose.** The SKILL.md files in this package are
> written in house style for a model to read, and that style uses em dashes and
> the occasional dry aside. The bans above apply to the **copy produced for the
> app**, not to this document. Do not read the surrounding formatting as
> permission.

## The source points at skills we do not have

Its "Related Skills" section sends you to `copy-editing`, `cro`, `emails`,
`popups`, `ab-testing` and `offers`. **`/bld-setup` installs none of them** — only
`copywriting` itself.

Do not go looking for them, and do not tell the user to invoke them. Where the
source defers to `copy-editing` for line-by-line polish, do that pass inline here
instead, against the three bans above.

## Output

Follow the source's output format, with two changes:

1. **Give the copy in a form that can be pasted.** These are React apps. A hero
   headline delivered as a bare line of prose gets retyped by hand; the same line
   given with its surrounding JSX does not. Match the file it is going into.
2. **Alternatives for the headline and the primary CTA only.** The source offers
   two or three options for both. Keep that. Do not produce three variants of
   every body paragraph; it buries the recommendation and the user has to do the
   choosing.

Keep the source's annotations. A one-line "why" under a headline is what lets the
user reject it for a real reason rather than a vibe.

## Scope

Copy only. **Do not restyle, re-space, or re-animate anything while you are in
the file**, and do not rewrite copy on screens the user did not name. If a
headline only works with a layout change, say so and wait rather than making the
change and mentioning it afterwards.

Follow the app's `design-system/MASTER.md` for anything type-related, and its
`CLAUDE.md` for tone if it declares one. A per-app voice outranks this file, the
same way this file outranks the source skill.

## Pitfalls

- **Reproducing the source's frameworks here.** They are one invocation away and
  they get updated upstream. This file is the delta, nothing else.
- **Over-correcting into flatness** after reading three bans in a row. Plain is
  the goal; lifeless is not.
- **Writing proof the app has not earned.** The most tempting single failure in
  this file, because the frameworks leave a slot open for it.
- **Describing the roadmap as though it shipped.** Read the code first.
- **Treating this file's own em dashes as permission.** See the note above.
