---
name: bld-util-legal-policies
description: 'ul: US legal check, plus a privacy policy and terms of service drafted from what the app really does. Use for "am I legal to launch", "how do I not get sued", "write a privacy policy", "write terms", before accounts or payments. US only.'
---

# legal-policies — US launch check, privacy policy, terms

Three jobs, one survey:

- **check**: walk the app against 16 US legal items and report what's
  covered, partial, missing or N/A.
- **privacy**: draft the app's privacy policy from what the code actually
  does.
- **terms**: draft the app's terms of service from the same survey.

`/bld-util-legal-policies` alone runs the check, then offers to draft
whichever of the two documents is missing (items 1 and 2). `check`,
`privacy` or `terms` after the command runs just that one. Draft the two
documents together when both are missing: they cross-reference each other,
and "personal information", "you" and "we" must mean the same thing in both.

**US law only.** Every output ends with the note in Step 6. **Not legal
advice**: it finds the gaps a first-time founder misses, and a lawyer still
signs off anything serious.

## Step 1 — Survey the app (every job starts here)

Read `package.json`, `.env.example`, the auth setup, API routes, and grep for
the services below. A privacy policy written from memory or from a template
is wrong about the app on day one, and a wrong policy is worse than a short
true one: the FTC treats a policy the app doesn't follow as deception.

Write one line each:

- **Personal data collected:** email, name, phone, location, photos, payment
  info, health, biometrics, IP/device info. Where each is collected (sign-up
  form, automatically, from a third party).
- **Services that receive data:** analytics (GA, PostHog, Vercel Analytics),
  auth (Supabase, Clerk), payments (Stripe), email (Resend), ad pixels, AI
  APIs that get user content. Each one, by name.
- **Money:** one-time payments, subscriptions, free trials that turn paid?
- **Messages:** marketing email? SMS?
- **Audience:** could under-13s use it? Is it aimed at kids?
- **User content:** can users post or upload things other people see?
- **Ships to:** web only, or App Store / Google Play too?

Never invent the operator's details. Legal name, postal address and contact
email come from the user; until they do, write `[ASK: legal name]` and keep
going.

## Step 2 — The check (16 items)

Each item: the rule, whether this app needs it, and what "covered" looks
like. An item that doesn't apply gets **N/A** with the reason (no payments →
item 9 N/A).

1. **Privacy policy.** CalOPPA requires any commercial site or app that
   collects personal info from California residents to post one
   conspicuously, so in practice every app with accounts or analytics needs
   one. Covered = a linked `/privacy` page that matches Step 1. Missing →
   Step 3.
2. **Terms of service.** Not legally required, but it's where you limit
   liability, set acceptable use and reserve the right to ban users. Covered
   = a linked `/terms` page, accepted at sign-up. Missing → Step 4.
3. **State privacy laws (CCPA/CPRA and ~20 other states).** CCPA applies only
   if the business meets one of: over $26,625,000 annual gross revenue
   (2025–26 figure, inflation-adjusted every two years), buys/sells/shares
   data of 100,000+ consumers or households, or gets 50%+ of revenue from
   selling or sharing data. Most pre-launch apps don't qualify. **Say so and
   note the threshold**, don't build compliance they don't need yet. If it
   applies: a "Do Not Sell or Share" link, honor Global Privacy Control,
   answer access and delete requests. For the other states, the IAPP US
   state privacy legislation tracker.
4. **Cookies and tracking.** The US has no general cookie-banner law.
   Disclose analytics and ad pixels in the policy; if CCPA applies and the
   app shares data for targeted ads, offer an opt-out. Don't add an EU-style
   banner because other sites have one: it costs conversions and buys
   nothing under US law.
5. **Account and data deletion.** Apple and Google Play both require in-app
   account deletion for any app that lets users create an account. Covered =
   a working "Delete account" that actually removes the rows. Follow the
   code path; a button that only signs the user out is the common miss.
6. **Data retention.** No single US law sets a period for small apps, but the
   policy must say how long data is kept, and the app shouldn't keep what it
   doesn't use. Flag tables or logs that hold personal data forever for no
   reason.
7. **Children (COPPA).** Applies if the app is aimed at under-13s, or the
   operator knows it collects data from under-13s. The amended rule's
   compliance date was 2026-04-22; it added biometrics to personal info and
   requires naming the third parties data goes to. Not a kids' app: say so in
   the terms, and don't collect birthdates you don't need. A kids' app: stop
   and recommend a lawyer. Verifiable parental consent is not a weekend task.
8. **Marketing email and SMS.** CAN-SPAM: every marketing email needs a
   working unsubscribe honored within 10 business days, a physical postal
   address, and an honest subject and sender. Transactional email (password
   resets, receipts) is exempt. TCPA: marketing texts need prior express
   written consent, so use an unchecked box and keep the record.
9. **Payments, subscriptions, free trials.** Show price, billing frequency
   and renewal terms before checkout. ROSCA and the FTC Act require clear
   disclosure, express consent and a simple way to cancel. The FTC's 2024
   click-to-cancel rule was vacated in July 2025 and was back at an early
   rulemaking stage in 2026, but about 30 states have their own auto-renewal
   laws. Build to California's (amended by AB 2863, effective 2025-07-01),
   the strictest common one: separate express consent to the renewal terms,
   keep proof of that consent, online cancellation if they signed up online
   with no retention maze, an annual reminder, and free-to-paid trials count.
   Stripe Checkout plus the Customer Portal covers most of it; check the
   portal's cancel link is reachable from inside the app.
10. **Third-party processors.** Every service from Step 1 belongs in the
    privacy policy by name. Accept each provider's standard data processing
    terms (most have a DPA page); no custom contract at this size.
11. **Data security.** FTC Section 5 treats unreasonable security as unfair.
    Covered = HTTPS, passwords hashed or handled by a managed auth provider,
    secrets out of the repo, row-level security on every Supabase table. For
    the full pass, `/bld-optimize-security`.
12. **Breach plan.** All 50 states have breach-notification laws. Covered = a
    few lines in the app's `planning.md`: who notices, who gets told, how to
    reach users fast.
13. **Who owns the code and assets.** Fonts, images, icons, music, AI
    output: check each licence allows commercial use. Code a friend wrote:
    get it in writing that it's assigned to the operator.
14. **Open-source licences.** `npx license-checker --summary` from the app
    folder, or read the dependency list. Flag GPL/AGPL in shipped code. MIT,
    Apache-2.0, BSD and ISC are fine with attribution.
15. **User-generated content.** If users post content others see: a takedown
    policy in the terms, and a DMCA designated agent registered with the US
    Copyright Office (online, small fee, renew every 3 years) for safe-harbor
    protection. Section 230 covers users' posts, not content the operator
    writes or edits.
16. **Accessibility.** Web-accessibility lawsuits under the ADA are common in
    the US. Not a checkbox law for a small app, but an `a11y-audit` pass
    before launch lowers the risk.

## Step 3 — The privacy policy

Draft from the Step 1 survey only. Plain words, short sentences, about an
8th-grade reading level. "We collect your email when you sign up", never "we
may process identifiers": "may" when the app *does* is the line that turns a
policy into a deception claim. Don't list data the app doesn't collect;
over-disclosure invites questions too.

Sections, in order:

1. **Who we are** — operator name, app name, effective date, contact email.
2. **What we collect** — grouped by how: you give it to us, collected
   automatically, from other services.
3. **How we use it** — one line per real purpose.
4. **Who we share it with** — every service from Step 1, by name, with what
   it gets and why. Say plainly whether the app sells data or shares it for
   targeted ads.
5. **Cookies and tracking** — the tools, what they do, how to opt out, and
   how the app responds to Do Not Track and Global Privacy Control signals.
   CalOPPA requires the Do Not Track disclosure, and it's the one most
   templates forget.
6. **How long we keep it** — per data type, real periods.
7. **Your choices** — access, correct, delete; the actual path in the app
   ("Settings → Delete account") and the email for anything else. Add
   state-law rights only if item 3 applies.
8. **Security** — what's actually in place, no "bank-grade" claims.
9. **Children** — not directed to under-13s and what happens if one signs up,
   or the COPPA section if item 7 applies.
10. **Changes to this policy** — how users are told (CalOPPA requires saying
    how), and the effective date.
11. **Contact** — email, and postal address if marketing email is sent
    (CAN-SPAM needs one anyway).

Write it to `<app>/legal/privacy-policy.md` first. Show it, get the user's
OK and the `[ASK: ...]` details, then wire a `/privacy` route from the app's
`design-system/MASTER.md` and link it in the footer and at sign-up. Copying
another company's policy is the classic mistake: their data practices aren't
this app's.

## Step 4 — The terms of service

Same rules as the policy: draft from the Step 1 survey, plain words, "you"
and "we" defined once at the top, and nothing the app doesn't do. A clause
about refunds the checkout doesn't offer, or content uploads the app doesn't
have, is a promise you will be held to or a sign nobody read it.

Sections, in order, skipping the ones Step 1 rules out:

1. **Agreeing to these terms.** Acceptance is clickwrap: an unchecked box,
   or "By creating an account you agree to the Terms and Privacy Policy"
   right beside the sign-up button, both linked. A footer link alone
   (browsewrap) is the version US courts most often refuse to enforce. Store
   the acceptance time and the terms version with the account.
2. **Who can use it.** 13 or older (item 7), or 18 or older when the app
   takes payments or is adult-only.
3. **The service.** What it does, provided "as is", and no uptime promise
   a solo-run app can't keep.
4. **Accounts.** The user keeps their login safe and is responsible for
   what happens on their account.
5. **Acceptable use.** The prohibited things that fit *this* app (scraping,
   spam, abuse, illegal content, reverse engineering), not a generic list.
6. **Your content.** Only if users post or upload: they keep ownership and
   grant the license the app needs to store and show it. Takedown process
   and the DMCA agent from item 15.
7. **Our stuff.** The operator owns the app, name and design; users get a
   limited license to use it.
8. **Payments, renewals, refunds.** Only if item 9 applies: price, billing
   cycle, auto-renewal, how to cancel and the refund rule, word for word
   what the checkout says. Put the renewal terms in bold; California's
   auto-renewal law wants them clear and conspicuous.
9. **Ending the account.** Either side can end it; what happens to the
   data, matching the privacy policy's retention section.
10. **Disclaimers and limit of liability.** Capped at what the user paid in
    the last 12 months (or a small fixed sum for a free app). Bold or
    all-caps, because a hidden liability cap is a weak one.
11. **Disputes.** Governing law of the operator's US state, and where
    disputes are heard. Arbitration with a class-action waiver is common but
    has to be conspicuous and fairly drafted: put `[LAWYER: arbitration?]`
    rather than writing one.
12. **Changes to these terms.** Email notice before material changes take
    effect, and an effective date. "We can change anything at any time,
    silently" is the clause courts scrutinize most.
13. **Contact.** The same email as the privacy policy.

Write it to `<app>/legal/terms.md`, link the privacy policy from it, and
wire a `/terms` route the same way as `/privacy` once the user approves.

## Step 5 — Report

For **check**, one table, every item:

| # | Item | Applies? | Status | What to do |
|---|---|---|---|---|

Status is **covered**, **partial**, **missing** or **N/A**. "What to do" is
one plain line naming the skill or step that fixes it. Then a short **Your
turn** list for what only the user can do: registering a DMCA agent,
accepting a provider's DPA, filling the `[ASK: ...]` details, asking a
lawyer.

Fix nothing during the check. Ask which missing items to fix, then do each
as its own approved change.

For **privacy** and **terms**, show the draft and list every `[ASK: ...]` and
`[LAWYER: ...]` left in it.

## Step 6 — End every output with this note, word for word

> **US only.** This covers US law only. EU and UK rules (GDPR, the ePrivacy
> cookie-consent rules, the UK GDPR) and any other country's laws are not
> accounted for. If the app has users there, it needs a separate check. Not
> legal advice.

## Sources

- Reel "How To NOT Get Sued When Launching An App" (creator unknown). Its 15
  headings are the skeleton of Step 2. The "full checklist" it promised was
  gated behind a comment, so the US detail under each item is BLD's, not the
  reel's.
- Privacy policy and terms structure adapted from the `privacy-policy` and
  `terms-of-service` skills in
  [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills)
  (MIT), cut to US law and to what a small pre-launch app needs.
- FTC click-to-cancel status: Jones Day, May 2026. CCPA threshold: Feroot
  (Feb 2026) and Jackson Lewis CCPA FAQ. Amended COPPA rule: Federal Register
  2025-05904. California ARL / AB 2863: Barnes & Thornburg, 2025.

Checked 2026-10-22 against those sources (law-firm summaries and the Federal
Register, not statute text). Not yet run end to end on a real app.
