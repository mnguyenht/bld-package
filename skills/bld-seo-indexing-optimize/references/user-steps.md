# The account steps — only the user can do these

Claude cannot do anything on this page. No API, no CLI, no browser automation
substitutes for it: these need a logged-in human, a real address, and in one case
a postcard. Walk the user through them, then stop and let them work.

Order matters. 1 is required, 2 is the biggest lever for a local organisation,
3 is the slow compounding one.

---

## 1. Google Search Console — required

**https://search.google.com/search-console**

This is how you tell Google the site exists, and the only authoritative place to
see whether it worked.

1. **Add property.** Choose **URL prefix** and enter the exact live origin,
   including `www` if the site uses it (`https://www.example.com`). A `www` and a
   non-`www` property are different properties to Google.
2. **Verify ownership.** DNS TXT record is the most durable option: it survives
   redeploys and framework changes, unlike the HTML-file method.
   - Copy the TXT value Search Console shows.
   - Add it in the **DNS panel**, which is the registrar's nameserver host, not
     necessarily the registrar. These are often different companies: on one real
     site the domain was bought from one registrar while DNS was hosted
     elsewhere, and the TXT record only works in the panel that actually
     serves the nameservers. Find that panel first.
   - DNS propagation is usually minutes, occasionally hours. Verify again later
     rather than assuming failure.
3. **Submit the sitemap.** Index → Sitemaps → type just `sitemap.xml` (the domain
   is prefilled) → Submit. Expect *Success*. *Couldn't fetch* almost always means
   the code was never pushed.
4. **Request indexing** for the homepage: paste the full URL into the inspection
   bar at the top → **Request Indexing**. One URL at a time, and it is a nudge,
   not a guarantee.

**How to check progress afterwards** — URL Inspection, not a Google search:

| Status | Meaning |
|---|---|
| `URL is not on Google` | Not indexed yet. Normal in the first days. |
| `Discovered – currently not indexed` | Queued, not yet crawled. Normal. |
| `Crawled – currently not indexed` | Crawled and passed over. Worth investigating. |
| `URL is on Google` | Done. |

---

## 2. Google Business Profile — the biggest local lever

**https://business.google.com**

Puts the organisation in Google Maps and the local sidebar, which for a
city-specific business outranks anything the website will do in its first months.
Needs a real address and postcard or phone verification.

**Category.** Don't browse the suggested list, none of it fits a niche
organisation. Type a keyword into the search field and take what autocompletes.
The primary category is what Google actually ranks on; extra categories can be
added later.

**Description.** 750 characters max. Rules that get a description rejected:

- No URLs and no phone numbers — both have their own fields.
- No superlatives (`hàng đầu`, `số 1`, `best`). Promotional language is
  prohibited.
- No offers, prices, or discounts. A free trial session counts as an offer here,
  even when it is a genuine standing feature. Put it on the site or in a Post.

Draft it from the app's **own copy only**. Figures found in press coverage are
not the client's word and must not be asserted on their behalf. Lead with who it
serves, spend the middle on the one genuinely distinctive fact, and close with
concrete numbers, which read as verifiable rather than promotional.

---

## 3. Backlinks — the slow compounding one

A backlink is one `<a href>` on someone else's site pointing at this one. It does
two separate jobs: it gives Googlebot a path to the site, and it acts as a vote
of confidence that feeds ranking.

**Before recommending any target, `curl` it.** On the first run, a national
organisation domain cited across several news articles turned out to be
**NXDOMAIN**. Dead domains persist in search results indefinitely.

```bash
curl -sL -o /dev/null -w "%{http_code}\n" https://target.example
curl -sL https://target.example/ | grep -o 'ourdomain[^"<) ]*' | sort -u
```

**Rank targets by three things at once:** is the site established, is the topic
related, and is the page already about this client? All three lining up is rare
and valuable. The strongest example is a parent or industry body that already
has a live page *about this client* and links to nothing of theirs — an
established site, an on-topic page, and a link that is trivially justified.

Give the user a message they can forward rather than an instruction to "reach
out". In the client's language:

> <Greeting>, <organisation> now has its own website: <https://the-site.com>
> Could you add this link to <the existing page about them> and to their
> profile page? Thank you.
>
> (Write it in the language the recipient actually uses, not English by
> default. A message someone can forward unedited gets sent; an instruction
> to "reach out" does not.)

**Social profile link fields** — Facebook About → Website, LinkedIn Contact info
→ Website, YouTube Customization → Basic info → Links.

Be precise about what these are worth: all three are `rel="nofollow"`, so they
pass little ranking signal. Do them anyway, because they confirm the `sameAs`
claim in the structured data. Google checks whether the profile links back.

Two things worth flagging rather than fixing:

- A LinkedIn **personal** profile (`/in/...`) is not a Company Page
  (`/company/...`). Google associates the latter with a brand entity.
- Social About pages can't be verified programmatically. Say so.

---

## What to tell the user about timing

Indexed in days to a few weeks. Ranking for the brand name in roughly two to four
weeks. Ranking for generic phrases takes months and depends mostly on section 3,
which is the part no amount of code can accelerate.
