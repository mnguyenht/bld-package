---
name: bld-optimize-seo-indexing
description: Make an app in this workspace discoverable on Google — audit what the live site actually serves, add the missing crawl plumbing (sitemap, robots, canonical, hreflang, structured data), ship it, then hand the user the account steps only they can do. Use when the user says /bld-optimize-seo-indexing, /bld-optimize-seo-indexing, "get this on Google", "make it discoverable", "why isn't my site showing up", "index my site", "SEO this", or asks about meta titles and search results. Claude does the code half; the user does the Search Console / Business Profile / backlink half.
---

# bld-optimize-seo-indexing — get an app found on Google

Two halves that must not be confused: **the code** (Claude, one afternoon) and
**the accounts** (only the user, and the slow part). This file is the conductor.
The user-facing checklist lives in `references/user-steps.md` — read it only when
you reach Phase 4, so it doesn't cost context on every invoke.

## Say this before doing anything

The single most common confusion, and the one that wasted the most time on the
first run of this skill:

| | Question it answers | What fixes it |
|---|---|---|
| **Indexing** | Is this page in Google's database *at all*? | Crawlability + submitting the URL + **time** |
| **Ranking** | *Where* does it appear for a given search? | Titles, content, backlinks |

**Meta titles do not affect indexing.** YouTube SEO videos blur this constantly.
If the user is anxious that a two-day-old site isn't showing up, rewriting titles
will not help, and implying it will is a claim you'll have to walk back. Set the
timeline expectation in Phase 5 **before** they submit anything, not after they
worry.

## Phase 0 — audit the LIVE site with curl, never by reading code

Reading the source tells you what *should* be served. Only a request tells you
what *is*. On the first run, `SITE.url` still held the old `*.vercel.app` domain
that had since started 404ing, so every canonical URL and every `og:image` on the
live site pointed at a dead host. The code looked completely fine.

```bash
APP=https://www.example.com          # the real production domain

curl -s -o /dev/null -w "home     %{http_code}\n" $APP/
curl -s -o /dev/null -w "robots   %{http_code}\n" $APP/robots.txt
curl -s -o /dev/null -w "sitemap  %{http_code}\n" $APP/sitemap.xml
curl -sI $APP/ | grep -i "x-robots-tag\|^HTTP"

curl -s $APP/ | tr '>' '>\n' | grep -i 'canonical\|hreflang\|og:\|name="robots"'
```

Check every absolute URL you find actually resolves. A canonical pointing at a
404 is worse than no canonical at all.

> Gotcha: on Next.js with an `app/[locale]/` segment, a missing `/robots.txt`
> gets swallowed by the dynamic segment and returns a **full HTML error page**
> carrying `<meta name="robots" content="noindex">`. That noindex belongs to
> Next's 404 page, not your site. Don't misread it as the site being blocked.

## Phase 1 — the five code fixes

Next.js App Router shown; on plain Vite these become static files in `public/`.

**1. The canonical base URL.** Find where the site's own URL is hardcoded
(`lib/site.ts` in our apps) and confirm it matches the live domain. This is the
highest-value one-line fix in the whole skill.

**2. `app/robots.ts`** — allow crawling, block API routes, point at the sitemap.

```ts
import type { MetadataRoute } from "next";
import { SITE } from "@/lib/site";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: "/api/" },
    sitemap: `${SITE.url}/sitemap.xml`,
  };
}
```

**3. `app/sitemap.ts`** — every page, every locale. Pull dynamic slugs from the
CMS so publishing never needs a code change.

```ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const slugs = await getArticleSlugs();
  // Replace these with the routes THIS app actually serves. They are an
  // example shape, not a default: emitting a sitemap full of URLs that 404 is
  // worse for indexing than having no sitemap at all.
  const paths = ["", "/blog", "/privacy", "/terms",
                 ...slugs.map((s) => `/blog/${s}`)];
  return paths.flatMap((path) =>
    locales.map((locale) => ({
      url: `${SITE.url}/${locale}${path}`,
      alternates: { languages: Object.fromEntries(
        locales.map((l) => [l, `${SITE.url}/${l}${path}`])) },
    })),
  );
}
```

**4. Canonical + hreflang on every page.** Next does *not* emit canonical tags on
its own. One helper beats hand-writing them per page, and it's the only way
`x-default` stays consistent:

```ts
export function localeAlternates(locale: string, path = "") {
  return {
    canonical: `${SITE.url}/${locale}${path}`,
    languages: {
      vi: `${SITE.url}/vi${path}`,
      en: `${SITE.url}/en${path}`,
      "x-default": `${SITE.url}/vi${path}`,
    },
  };
}
```

Then `alternates: localeAlternates(locale, "/whatever")` in each
`generateMetadata`. A page-level `alternates` replaces the layout's, so the
layout can hold the home-page version and children override it.
**hreflang must be reciprocal** — every locale lists every other, itself
included, or Google discards the whole relationship.

**5. Organization JSON-LD** in the locale layout. The payload that matters is
`sameAs`: it claims the domain and the social accounts are one entity. Google
verifies by checking whether the profiles link back, which is why Phase 4 asks
the user to fill in those website fields.

> CSP check: JSON-LD is an inline `<script>`. If the app sends a
> Content-Security-Policy without `'unsafe-inline'` in `script-src`, it is
> blocked. Verify rather than assume.

## Phase 2 — verify from the build output, not from hope

```bash
npm run build
grep -c "<loc>" .next/server/app/sitemap.xml/route.body
cat .next/server/app/robots.txt.body
grep -o '<link rel="canonical"[^>]*>' .next/server/app/vi.html
```

Confirm the URL count matches expectation and every emitted URL uses the real
domain.

## Phase 3 — ship

Follow workspace deploy discipline: **stop any dev server first**, then
`tsc --noEmit`, lint, `npm run build`, commit, push. Then poll the live URL;
Vercel takes ~30s:

```bash
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w "%{http_code}" $APP/sitemap.xml)
  [ "$code" = "200" ] && { echo LIVE; break; }; sleep 8
done
```

Run that with `run_in_background` — foreground `sleep` is blocked.

> A live sitemap may hold **more** URLs than your local build produced, because
> production reads the live CMS. That is correct behaviour, not a bug. Say so
> before the user spots the mismatch.

## Phase 4 — hand over the account steps

Read `references/user-steps.md` and walk the user through it. **Never claim to
have done any of it.** Claude cannot add a DNS record, create a Business Profile,
or persuade a third party to add a link.

## Phase 5 — set expectations, then teach the right way to check

- New domain, zero backlinks: **days to a few weeks**. An hour is nothing.
- Submitting a sitemap adds URLs to the crawl queue. It does not jump the queue.
- **A Google search is the wrong instrument.** Use Search Console → **URL
  Inspection**. `URL is not on Google` and `Discovered – currently not indexed`
  are both normal early on. `Crawled – currently not indexed` is the one to watch.
- Claude's own `WebSearch` is **not Google** and returns noise for `site:`
  queries. Never present it as evidence about Google's index in either direction.

## Optional — the title & description audit

Only after the above, and only with the ranking-vs-indexing caveat restated.
Google truncates titles near **roughly 60 characters**, descriptions near **160**.
These are editorial rules of thumb, **not limits Google enforces**. Truncation is
by rendered pixel width, so it varies with the characters used and the device,
and Google frequently rewrites the description entirely from page content. Use
the counts to spot copy that is obviously too long, never as a pass/fail gate.

Write this to a temp `.py` file and run it — do not inline it as a nested
heredoc inside another heredoc, which is a quoting trap:

```python
import glob, re, unicodedata, html
for f in sorted(glob.glob('.next/server/app/**/*.html', recursive=True)):
    if 'not-found' in f or 'global-error' in f: continue
    s = open(f, encoding='utf-8').read()
    t = re.search(r'<title>(.*?)</title>', s)
    d = re.search(r'<meta name="description" content="(.*?)"', s)
    if not t: continue
    n = lambda x: unicodedata.normalize('NFC', html.unescape(x))
    t, d = n(t.group(1)), n(d.group(1)) if d else ''
    flags = []
    if len(t) > 60: flags.append(f"title +{len(t)-60}")
    if len(d) > 160: flags.append(f"desc +{len(d)-160}")
    print(f"{f:<58}{len(t):>4}{len(d):>5}  {', '.join(flags) or 'ok'}")
```

**Use Python, not bash `${#var}`** — bash miscounts Vietnamese diacritics badly
enough to send you chasing imaginary problems. Normalize to NFC first.

Two things to look for beyond raw length:

- A long `· Brand Name` title template eats the budget on every article page.
- **Brand-first titles only reach people who already know the brand.** If the
  generic phrase a stranger would actually type appears in zero titles, say so.
  That is usually the most valuable finding in the audit.

Report it. **Do not rewrite approved marketing copy without asking** — workspace
stay-in-scope rules apply, and site copy is often client-approved.

## Pitfalls

- **Trusting the source over the live response.** Phase 0 exists because of this.
- **Recommending a backlink target without checking it resolves.** On the first
  run, a national org domain cited across multiple news articles was **NXDOMAIN**.
  Search results happily cite dead domains. `curl` every target before naming it.
- **Trying to verify social profile links by fetching them.** YouTube About,
  Facebook and LinkedIn render client-side or sit behind a login; `WebFetch`
  returns page furniture. Say "couldn't verify" rather than guessing.
- **Treating social links as ranking wins.** They are `rel="nofollow"`. Worth
  doing for `sameAs` reciprocity and discovery, not for rank. Be precise.
- **Fabricating facts into a Business Profile description.** Use only claims the
  app's own copy makes. Figures from press coverage are not the client's word.
- **Rewriting copy uninvited** while "doing SEO". Report, don't fix.
- **Letting the user believe code work speeds up indexing.** It does not.
