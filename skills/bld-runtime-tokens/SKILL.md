---
name: bld-runtime-tokens
description: Check how much of the Claude token window is left by pinging the locally-installed claude-monitor, then say what to do about it — keep going, batch, delegate to Codex, or hand off. Use when the user says /bld-runtime-tokens, "how many tokens left", "am I about to run out", "check my usage", "how much budget do we have", or is about to start a long sprint. Also run it unprompted when a sprint has been running long and the answer would change the plan.
---

# bld-tokens — know the budget before spending it

One command, one line back, then a recommendation. This is a status check, not a
project: **never turn it into a report**.

## The command

`claude-monitor` is already installed (`~/.local/bin/claude-monitor`,
v4.0.0). It reads the local Claude Code transcripts in `~/.claude/projects` — no
network, no key, no account access.

```powershell
claude-monitor --once --output json --no-emoji --plan max20 | ConvertFrom-Json
```

🚩 **`--once` is mandatory.** Without it the tool is a live-refreshing TUI that never
exits — the call hangs until the tool times out. There is no interactive terminal here.

⚠️ **Don't truncate the pipe** (`| Select-Object -First N`). Breaking the pipeline
early kills the process and returns exit 255 with half the JSON. Capture it whole,
then read fields off the object.

## Fields that matter

| Field | Use |
|---|---|
| `limits.five_hour.used_percentage` | how much of the current window is gone |
| `forecast.tokens_remaining` | tokens left in the window |
| `forecast.minutes_remaining` | how long that lasts at the current burn |
| `forecast.display` | human clock time it runs out |
| `pace.label` | the tool's own verdict (`slow down`, `on track`, …) |
| `pace.used_percentage` vs `pace.elapsed_percentage` | spending faster than the clock? |
| `local.burn_rate_tokens_per_minute` | current burn |

`limits.seven_day` is **null** — the weekly window can't be derived from local files.
Only the 5-hour window is real here. Don't report a weekly number.

## Report it in one line

```
Tokens: 48% of 5h window · 114k left · est. empty 09:37 (~1h53m) · pace: slow down
```

Then **one** sentence of recommendation. Nothing else.

## Thresholds → what to actually do

**This check exists to stop the window from running out mid-piece — it is not a
mandate to economize early.** The ceiling that matters is ~93%; below that, spend
normally. (Changed 2026-08-07: the old version called for economizing from 60%,
which read as "restrict usage overall." That was never the intent — the point is
never hitting the wall unexpectedly, not curbing usage in general.)

- **under ~90%** — say the line, carry on. No advice needed, no economizing — ignore
  `pace.label` saying "slow down" at this range, it's a straight-line projection, not
  a limit.
- **~90–93%** — start economizing without being asked: stop re-reading files already
  in context, review diffs instead of whole files, batch remaining work into fewer,
  larger steps.
- **over ~93%, or `forecast.minutes_remaining` under ~15** — say so *before* starting
  the next piece, not after. Then either:
  - **route the build work to Codex** (`/bld-runtime-agents`) — it spends the ChatGPT Plus
    quota, not the Claude window. This is the single biggest lever when Claude is the
    constrained side, and the whole reason the split exists.
  - **or `/bld-util-handoff`** if the sprint is genuinely mid-flight — a handoff written
    with tokens left is worth far more than one attempted at 98%.
- **window about to reset** (`limits.five_hour.resets_at` is close) — say how long, and
  suggest parking a big piece until after it rather than starting and stalling halfway.

Never silently keep going into an empty window. Running out mid-piece leaves work in a
half-applied state, which is worse than pausing on purpose.

## When to run it unprompted

Sparingly — it's cheap but not free, and a status line nobody asked for is noise.

- at the start of a sprint the user has flagged as long
- when the user asks for something clearly large (a full app, a mass refactor)
- once mid-sprint if the session has been heavy, and only if the answer would change
  the plan

Not every turn. Not as a habit.

## Accuracy caveats — state these when they matter

- **Everything is `confidence: local_estimate`.** These numbers are computed from local
  transcript files, not from Anthropic's official accounting. Treat as a good estimate,
  never as an exact remaining balance.
- **The plan is auto-detected and can be wrong.** Confirmed twice now (2026-08-05 and
  2026-08-07): auto-detect reported `pro` (19k/5h, giving a nonsense 400%+ reading) when
  the real plan is **`max20`** (220k/5h). Always pass `--plan max20` explicitly for this
  account — don't trust the auto-detected value:
  ```powershell
  claude-monitor --once --output json --plan max20
  ```
  Valid: `pro`, `max5`, `max20`, `team`, `custom` (with `--custom-limit-tokens`).
- **The forecast is a straight-line projection** off the current burn rate. A spike from
  one big file read will make it look far more dire than it is. Sanity-check it against
  `pace.elapsed_percentage` before raising an alarm.

## Notes

- Cost figures (`local.cost_usd`) are the tool's estimate of API-equivalent price. On a
  subscription that is **not** a bill — don't present it as money owed.
- This is about the **Claude** window. Codex's separate quota is read a different way
  (see the `agent-delegation` block in `~/.claude/CLAUDE.md`). When Claude is low and
  Codex is not, that asymmetry *is* the plan.
