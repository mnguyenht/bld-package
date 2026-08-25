# The 13 layers — coverage map for our stack

The user's 13-layer model, mapped to **what to actually check** for our typical
stack (Vite/React/TS or Next.js · Tailwind + shadcn · Vercel hosting · Supabase
for DB/auth when present · Stripe for payments when present · OpenRouter free
models for any AI feature) and **which tool/checklist covers it**.

Not every layer applies to every app. A static Vite landing page has no Layer 3/4;
a Supabase+Stripe SaaS has all 13. In Phase 0, mark each layer **applies / N/A**
and only audit the ones that apply. Skipping an N/A layer is correct; silently
skipping one that *applies* is a miss — say which you skipped and why.

| # | Layer | What to check (our stack) | Primary coverage |
|---|-------|---------------------------|------------------|
| 1 | Front-end foundations | XSS (`dangerouslySetInnerHTML`, unsanitized user HTML), CSP headers, no secrets in the client bundle (`VITE_*` / `NEXT_PUBLIC_*` leak everything they touch), safe external links (`rel="noopener"`) | ecc `security-review.md` §5 XSS; gstack-cso; built-in `/security-review` |
| 2 | APIs & backend logic | Input validation (zod) on every handler, server-side authz on every mutation, SSRF via user-controlled URLs, generic error messages (no stack traces to client), no injection into shell/SQL/template sinks | ecc `security-review.md` §2/§3/§8; `security-bounty-hunter.md`; gstack-cso |
| 3 | Database & storage | Parameterized queries only (no string-built SQL), Supabase Storage bucket ACLs (not public), migrations run forward + have rollback, service-role key never reaches the client | ecc `security-review.md` §3; `production-audit.md` (Data Integrity) |
| 4 | Auth & permissions | Tokens in httpOnly cookies (not localStorage), authz check *before* every sensitive op, RBAC roles enforced server-side, session expiry/rotation, password reset + email verification flows | ecc `security-review.md` §4 |
| 5 | Hosting & deployment | Secrets in Vercel env (not committed, not in build output), HTTPS enforced, security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, CSP), preview deploys not exposing prod data | ecc `cloud-infrastructure-security.md` §5/§6; `production-audit.md` (Operations) |
| 6 | Cloud & compute | Serverless/edge function least-privilege, secrets via platform secret store + rotation where it exists, no long-lived cloud credentials, no public storage buckets | ecc `cloud-infrastructure-security.md` §1/§2/§3 |
| 7 | CI/CD & version control | `.env`/`.env.*` gitignored (`!.env.example` allowed) **before first commit**, no secrets in git history, GitHub Actions least-privilege + secret scanning + `npm audit`, lock file committed + `npm ci`, branch protection | ecc `cloud-infrastructure-security.md` §5; `security-review.md` §10; workspace `.gitignore` rule |
| 8 | Security & row-level security | Supabase RLS **enabled on every table**, policies scope rows to `auth.uid()`, tenant isolation holds under multi-user, no table readable/writable by `anon` unintentionally | ecc `security-review.md` §4 (RLS); `production-audit.md` (Data Integrity) |
| 9 | Rate limiting | Limits on all API endpoints, stricter limits on expensive ops (search, AI calls, auth attempts), per-IP and per-user, brute-force protection on login | ecc `security-review.md` §7 |
| 10 | Caching & CDN | No sensitive/user-specific data in shared/CDN cache, correct `Cache-Control`/`Vary`, cache-poisoning resistance, edge security headers | ecc `cloud-infrastructure-security.md` §6 |
| 11 | Load balancing & scaling | Health checks that prove deps are reachable, writes/jobs/webhooks idempotent (safe to retry), graceful degradation when a dependency is down | ecc `production-audit.md` (Operations / Payments & Webhooks) |
| 12 | Error tracking & logs | No secrets/PII in logs, generic errors to users + detailed only server-side, log retention, alerts on auth failures + anomalies, admin actions audited | ecc `security-review.md` §8; `cloud-infrastructure-security.md` §4 |
| 13 | Availability & recovery | Automated backups + tested restore, documented rollback path for every high-impact release, RPO/RTO defined, deletion protection on prod DB | ecc `cloud-infrastructure-security.md` §7; `production-audit.md` (Operations) |

## Cross-cutting (not a numbered layer)

- **Layer 0 — the harness itself:** our `.claude/` config → `agentshield-checklist.md`.
- **Dynamic testing:** everything above is static/code review. Exercising layers 1–4 and 9 against a *running* target needs a live pentest, which is out of scope for BLD because that tooling is paid. Name the gap in the report rather than letting it read as though those layers were tested at runtime.
- **AI-feature apps only:** if the app embeds an LLM/agent, add `agent-architecture-audit.md` on top of the 13 layers.
