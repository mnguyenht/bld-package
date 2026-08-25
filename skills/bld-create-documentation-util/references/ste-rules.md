# ASD-STE100 — the working rule set for app docs

Simplified Technical English (STE) is a controlled-language standard from the
AeroSpace and Defence Industries Association of Europe. It exists so that a
reader with weak English still reads a procedure correctly the first time.

This file is a **paraphrase of the rules we apply**, written for software docs.
It is not the specification and it is not the approved-word dictionary. The real
spec (Issue 9) is free from `asd-ste100.org` after a request form. Do not paste
the dictionary into this repo.

STE has ~65 rules in 9 sections plus a dictionary of ~900 approved words. The
rules below are the ones that change how a docs page reads.

---

## 1. Words

- **One word, one meaning.** Pick a meaning and keep it. `close` = shut a panel;
  it never also means "near".
- **One meaning, one word.** Do not rotate synonyms for variety. If the button
  is a *button*, it is never later a *control* or a *element*.
- **Use the approved part of speech.** Do not turn a noun into a verb
  (`to inbox`, `to onboard`, `to action`).
- **Prefer the short common word.** Replacements that come up constantly:

  | Not this | This |
  |---|---|
  | utilize, employ | use |
  | perform, execute, carry out | do |
  | prior to | before |
  | subsequent to, following | after |
  | in order to | to |
  | is able to, has the ability to | can |
  | attempt | try |
  | commence, initiate | start |
  | terminate | stop |
  | require | need |
  | additional | more |
  | approximately | about |
  | assist | help |
  | obtain, acquire | get |
  | display (verb) | show |
  | modify | change |
  | permit | let |
  | sufficient | enough |
  | ensure | make sure |
  | in the event that | if |
  | at this point in time | now |
  | a number of | some, or the real count |

- **Technical names and technical verbs are allowed.** STE was written for
  aerospace, so it has no software vocabulary. Treat product names, UI labels,
  file names, code identifiers, and the standard interface verbs
  (`click`, `select`, `type`, `sign in`, `download`, `upload`, `refresh`,
  `install`) as technical terms. Use each one consistently and never invent a
  second name for the same thing.
- **Quote the interface exactly.** Never rewrite a real button label, error
  string, route, or identifier to fit STE. Copy it verbatim and put it in code
  style or quotes.

## 2. Nouns and adjectives

- **No noun cluster longer than three words.** `user account settings page` →
  `the settings page for the user account`.
- **Keep the articles.** Write `the file`, not `file`. Telegraphic style is
  banned.
- Use a hyphen when it removes an ambiguity (`read-only file`).

## 3. Verbs

- Allowed forms: infinitive, imperative, simple present, simple past, simple
  future, and the past participle used as an adjective.
- **No `-ing` form.** `The app is saving your work` → `The app saves your work`.
  Exception: it is part of a technical name or an exact UI string (`Loading…`).
- **Active voice in every instruction.** `Click Save.` not `Save must be
  clicked.` Passive is tolerated only in descriptive text, and only when the
  actor is genuinely unknown.
- **`must` = required. `can` = permitted or possible. `do not` = forbidden.**
  Never `shall`, `should`, `may`, or `might` — each one is ambiguous.

## 4. Sentences

- Instruction: **20 words maximum**.
- Descriptive sentence: **25 words maximum**.
- **One instruction per sentence.** Two actions that must happen together may
  share a sentence; a sequence may not.
- Put the condition first: `If the list is empty, click Import.`
- Descriptive paragraph: **6 sentences maximum**, one topic each. Start the
  paragraph with its topic sentence.

## 5. Procedures

- Number the steps. One action per step, in the real order.
- Start each step with the command verb.
- Put a warning or a caution **before** the step it protects, and start it with
  the command: `Do not close the tab before the upload finishes.`
- Use a vertical list for anything with more than two parts.

## 6. Punctuation and abbreviations

- Simple punctuation only. No slashes for `and/or`, no parentheses that carry
  meaning the sentence needs, no dashes doing the work of a full stop.
- Spell an abbreviation out at first use, then use it: `two-factor
  authentication (2FA)`.
- Keep well-known technical abbreviations as they are: `URL`, `API`, `PDF`, `CSV`.

## 7. What STE deliberately costs you

Marketing tone. STE text reads flat and repetitive on purpose, because
repetition is what makes it unambiguous. Do not "improve" it back toward
variety — that is the failure mode of this skill.

---

## Compliance checklist

Run this over every paragraph before the page ships.

- [ ] Every instruction is imperative and starts with its verb.
- [ ] No instruction is over 20 words; no descriptive sentence is over 25.
- [ ] No paragraph is over 6 sentences.
- [ ] No `-ing` verb outside a quoted UI string or technical name.
- [ ] No passive voice in any instruction.
- [ ] Only `must` / `can` / `do not` for obligation. No `shall`/`should`/`may`.
- [ ] Each thing has exactly one name across the whole page.
- [ ] No noun cluster over three words.
- [ ] Articles present everywhere.
- [ ] Each abbreviation is defined at first use.
- [ ] Every UI label, path, and identifier is copied verbatim from the code.
