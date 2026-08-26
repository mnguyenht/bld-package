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

const runs = files.map((f) => {
  let r;
  try {
    r = JSON.parse(readFileSync(f, "utf8"));
  } catch (e) {
    console.error(`${f}: cannot read as JSON (${e.message})`);
    process.exit(1);
  }
  // Refuse anything that is not a Lighthouse report. Without this, a wrong file
  // either crashed with a raw Node traceback after already printing a header of
  // "undefined", or, worse, printed a clean-looking report with no numbers in
  // it and exited 0. A confident empty report reads as "nothing is wrong".
  if (!r || typeof r !== "object" || !r.categories || !r.audits || !r.lighthouseVersion) {
    console.error(
      `${f}: not a Lighthouse report.\n` +
      `Expected an object with categories, audits and lighthouseVersion.\n` +
      `Lighthouse writes this with --output=json; an --output=html file or a\n` +
      `wrapper that nests the report under another key will not work.`,
    );
    process.exit(1);
  }
  return r;
});

// Medianing runs of different pages or form factors produces a number that
// describes nothing. The header only ever showed run 0, so this was invisible.
const urlOf = (r) => r.finalDisplayedUrl ?? r.finalUrl;
for (const [i, r] of runs.entries()) {
  if (urlOf(r) !== urlOf(runs[0]) ||
      r.configSettings?.formFactor !== runs[0].configSettings?.formFactor) {
    console.error(
      `${files[i]} is not the same measurement as ${files[0]}:\n` +
      `  ${files[0]}: ${urlOf(runs[0])} (${runs[0].configSettings?.formFactor ?? "?"})\n` +
      `  ${files[i]}: ${urlOf(r)} (${r.configSettings?.formFactor ?? "?"})\n` +
      `Median across different pages or form factors is meaningless.`,
    );
    process.exit(1);
  }
  // Not fatal, but worth saying: the performance score is a weighted sum, and
  // the weights change between major Lighthouse versions. Scores medianed
  // across versions are not measuring quite the same thing.
  if (r.lighthouseVersion.split(".")[0] !== runs[0].lighthouseVersion.split(".")[0]) {
    console.error(
      `⚠  ${files[i]} is Lighthouse v${r.lighthouseVersion} but ${files[0]} is ` +
      `v${runs[0].lighthouseVersion}.\n` +
      `   Metric weights differ across major versions, so this median blends two ` +
      `different scoring formulas.`,
    );
  }
}
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
  // Score every metric BEFORE dividing up the weight. An audit that did not run
  // — errored, or notApplicable on this page — medians to a null score. It used
  // to keep its weight in the denominator anyway, which quietly shrank every
  // other metric's share, and it printed "-0" lost, which reads as "measured,
  // costing nothing". Both are wrong: nothing was measured. Shares are now over
  // the metrics that actually ran, and the ones that didn't say so.
  const rows = weighted.map((ref) => ({
    ref,
    val: median(runs.map((r) => r.audits[ref.id]?.numericValue)),
    sc: median(runs.map((r) => r.audits[ref.id]?.score)),
  }));
  const measured = rows.filter((r) => r.sc !== null);
  const totalW = measured.reduce((s, r) => s + r.ref.weight, 0);
  console.log(`\n== PERFORMANCE METRICS — where the points actually are ==`);
  console.log(`     value    score  weight  lost   metric`);
  for (const row of rows) {
    const title = first.audits[row.ref.id]?.title ?? row.ref.id;
    if (row.sc === null || !totalW) {
      console.log(`  ${ms(row.val).padStart(8)}  ${pct(null)}     -      -   ${title}  (not measured)`);
      continue;
    }
    const share = row.ref.weight / totalW;
    const lost = (1 - row.sc) * share * 100;
    const flag = lost >= 10 ? " ←── the problem" : lost >= 4 ? " ←" : "";
    console.log(
      `  ${ms(row.val).padStart(8)}  ${pct(row.sc)}   ${String(Math.round(share * 100)).padStart(3)}%  ` +
        `${("-" + lost.toFixed(0)).padStart(5)}   ${title}${flag}`,
    );
  }
  console.log(`  "lost" = points this metric costs the 100. Fix the biggest number, not the ugliest one.`);
  if (measured.length < rows.length) {
    console.log(
      `  ${rows.length - measured.length} metric(s) did not run, so the weights above are shares of the ` +
        `${Math.round((totalW / weighted.reduce((s, a) => s + a.weight, 0)) * 100)}% that did.`,
    );
  }
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
// Medianed across runs like everything else above. This used to read run 0
// only, while the header promised medians, so one unlucky run could put a
// nonexistent 1000 ms opportunity at the top of the list, or bury a real one.
const opps = Object.entries(first.audits)
  .filter(([, a]) => a.details && (a.details.overallSavingsMs > 0 || a.details.overallSavingsBytes > 0))
  .map(([id, a]) => ({
    title: a.title,
    savedMs: median(runs.map((r) => r.audits[id]?.details?.overallSavingsMs ?? 0)) ?? 0,
    savedKb: Math.round((median(runs.map((r) => r.audits[id]?.details?.overallSavingsBytes ?? 0)) ?? 0) / 1024),
  }))
  .filter((o) => o.savedMs > 0 || o.savedKb > 0)
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
console.log(`  Identical fingerprint + a score swing usually means noise, not your code.`);
console.log(`  Usually, not always: this counts bytes and requests, so it cannot see a change`);
console.log(`  that kept the payload the same size. A rewritten hot loop, a new render path,`);
console.log(`  or a same-sized bundle doing different work all move the score silently.`);
