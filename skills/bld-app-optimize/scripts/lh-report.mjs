#!/usr/bin/env node
// Read one or more Lighthouse JSON reports and print the whole triage surface:
// median category scores, the five perf metrics with their real weights, the LCP
// phase breakdown, the ranked opportunities, and the payload fingerprint.
//
// Usage:  node lh-report.mjs run1.json [run2.json run3.json]
//
// Multiple runs => every number is the MEDIAN. Lighthouse is noisy; one run is a
// sample, not a measurement. See SKILL.md "three runs, always".
//
// ponytail: no deps, no formatting lib. Reads JSON, prints columns.

import { readFileSync } from "node:fs";

const files = process.argv.slice(2);
if (!files.length) {
  console.error("usage: node lh-report.mjs <report.json> [more.json ...]");
  process.exit(1);
}

const runs = files.map((f) => JSON.parse(readFileSync(f, "utf8")));
const median = (xs) => {
  const s = xs.filter((x) => typeof x === "number" && !Number.isNaN(x)).sort((a, b) => a - b);
  if (!s.length) return null;
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};
const pct = (x) => (x === null ? "  -" : String(Math.round(x * 100)).padStart(3));
const ms = (x) => (x === null ? "-" : x >= 1000 ? (x / 1000).toFixed(1) + " s" : Math.round(x) + " ms");
const first = runs[0];

// ── header ──────────────────────────────────────────────────────────────────
const formFactor = first.configSettings?.formFactor ?? "?";
console.log(`URL         ${first.finalDisplayedUrl ?? first.finalUrl}`);
console.log(`Lighthouse  v${first.lighthouseVersion}   form factor: ${formFactor}   runs: ${runs.length}`);
if (runs.length === 1) console.log(`⚠  ONE RUN — this is a sample, not a measurement. Run 3 and re-read.`);

// ── category scores ─────────────────────────────────────────────────────────
console.log(`\n== SCORES ${runs.length > 1 ? "(median)" : ""} ==`);
for (const key of Object.keys(first.categories)) {
  const vals = runs.map((r) => r.categories[key]?.score);
  const spread = vals.filter((v) => typeof v === "number");
  const range =
    runs.length > 1 && spread.length
      ? `   [${Math.round(Math.min(...spread) * 100)}–${Math.round(Math.max(...spread) * 100)}]`
      : "";
  console.log(`${pct(median(vals))}  ${first.categories[key].title}${range}`);
}

// ── the five metrics that ARE the performance score ─────────────────────────
// Weights come from the report itself, never from memory — they change between
// Lighthouse majors and the whole triage depends on getting them right.
const perfRefs = first.categories.performance?.auditRefs ?? [];
const weighted = perfRefs.filter((a) => a.weight > 0).sort((a, b) => b.weight - a.weight);

if (weighted.length) {
  const totalW = weighted.reduce((s, a) => s + a.weight, 0);
  console.log(`\n== PERFORMANCE METRICS — where the points actually are ==`);
  console.log(`     value    score  weight  lost   metric`);
  for (const ref of weighted) {
    const val = median(runs.map((r) => r.audits[ref.id]?.numericValue));
    const sc = median(runs.map((r) => r.audits[ref.id]?.score));
    const share = ref.weight / totalW;
    const lost = sc === null ? 0 : (1 - sc) * share * 100;
    const flag = lost >= 10 ? " ←── the problem" : lost >= 4 ? " ←" : "";
    console.log(
      `  ${ms(val).padStart(8)}  ${pct(sc)}   ${String(Math.round(share * 100)).padStart(3)}%  ` +
        `${("-" + lost.toFixed(0)).padStart(5)}   ${first.audits[ref.id].title}${flag}`,
    );
  }
  console.log(`  "lost" = points this metric costs the 100. Fix the biggest number, not the ugliest one.`);
}

// ── LCP phase breakdown: WHY is LCP slow, not just THAT it is ───────────────
const lcpPhases = first.audits["largest-contentful-paint-element"]?.details?.items?.find((i) => i.type === "table");
if (lcpPhases?.items?.length) {
  console.log(`\n== LCP BREAKDOWN ==`);
  const el = first.audits["largest-contentful-paint-element"]?.details?.items?.[0]?.items?.[0]?.node;
  if (el) console.log(`  element: ${(el.nodeLabel ?? el.snippet ?? "").slice(0, 90)}`);
  for (const row of lcpPhases.items) {
    const t = row.timing ?? 0;
    console.log(`  ${String(row.phase).padEnd(14)} ${ms(t).padStart(8)}`);
  }
  console.log(`  A large "Render delay" means the bytes arrived and nothing painted — that is a`);
  console.log(`  main-thread or hydration problem, NOT an image-size problem. Do not compress an image to fix it.`);
}

// ── ranked opportunities ────────────────────────────────────────────────────
const opps = Object.values(first.audits)
  .filter((a) => a.details && (a.details.overallSavingsMs > 0 || a.details.overallSavingsBytes > 0))
  .map((a) => ({
    title: a.title,
    savedMs: a.details.overallSavingsMs ?? 0,
    savedKb: Math.round((a.details.overallSavingsBytes ?? 0) / 1024),
  }))
  .sort((a, b) => b.savedMs - a.savedMs || b.savedKb - a.savedKb);

if (opps.length) {
  console.log(`\n== OPPORTUNITIES (Lighthouse's own estimate, treat as a hypothesis) ==`);
  for (const o of opps.slice(0, 12)) {
    console.log(`  ${(o.savedMs ? Math.round(o.savedMs) + " ms" : "").padStart(8)} ${(o.savedKb ? o.savedKb + " KB" : "").padStart(8)}  ${o.title}`);
  }
}

// ── failing non-perf audits ─────────────────────────────────────────────────
for (const cat of ["accessibility", "best-practices", "seo"]) {
  const refs = first.categories[cat]?.auditRefs ?? [];
  const failed = refs
    .map((r) => first.audits[r.id])
    .filter((a) => a && a.score !== null && a.score < 1 && a.scoreDisplayMode !== "informative");
  if (failed.length) {
    console.log(`\n== ${first.categories[cat].title.toUpperCase()} — ${failed.length} failing ==`);
    for (const a of failed) console.log(`  ${a.id.padEnd(38)} ${a.title}`);
  }
}

// ── payload fingerprint: the before/after proof ─────────────────────────────
// This is what settles "did my change cause the regression". If the payload is
// identical, the change CANNOT have moved FCP or LCP — there is no mechanism.
const bytes = median(runs.map((r) => r.audits["total-byte-weight"]?.numericValue));
const reqs = median(runs.map((r) => r.audits["network-requests"]?.details?.items?.length));
const jsBytes = median(
  runs.map((r) =>
    (r.audits["network-requests"]?.details?.items ?? [])
      .filter((i) => i.resourceType === "Script")
      .reduce((s, i) => s + (i.transferSize ?? 0), 0),
  ),
);
console.log(`\n== PAYLOAD FINGERPRINT (compare this before vs after a fix) ==`);
console.log(`  total weight    ${bytes ? Math.round(bytes / 1024) + " KB" : "-"}`);
console.log(`  requests        ${reqs ?? "-"}`);
console.log(`  JS transferred  ${jsBytes ? Math.round(jsBytes / 1024) + " KB" : "-"}`);
console.log(`  Identical fingerprint + a score swing = network noise, not your code.`);
