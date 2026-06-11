# CLAUDE.md — Pollagol Mundialera 2026 Predictor

> ▶ **Resuming work?** Read `tasks/HANDOFF.md` first (deterministic resume point, 2026-06-02). Track-A
> pool engine phase **DONE through Step 7** (A2 `pool/pool_montecarlo.py` + `pool/decision_clock.md` + L5).
> Next (needs a new GO): **A3 council / other-4-picks**, then the **Jun-10 late decision run**.
> HARD GATE: never LOCK a pick; champion is OPEN.
>
> 🎯 **OBJECTIVE = HYBRID · HOUR_CAP = 6h** (DoD-1, 2026-06-02 — `memory/objective.md`,
> `pool/objective.py: read_objective()`). Cap = **STOP by HITL convention**; each DoD needs its own GO.
> Active work: the **DoD 1–4 contract** (order DoD-1→2→**4→3**; DoD-4 BUG-1/BUG-2 is a hard dep of DoD-3).

Operating contract for this workspace. Read `memory/` each session; update it when facts change.
Source of truth for pool rules is Spanish; all code/docs in English.

## What this is
A minimal, deterministic, auditable predictor for a private FIFA World Cup 2026 pool on **pollaya.com**
(N≈20–30 entrants, payout 60/20/10, entry $30.000 CLP, mostly-chalk field). It outputs, per match, a
calibrated scoreline distribution and the single scoreline that **maximizes expected competition points**
(not the most-probable score), plus the 5 one-time **locked picks** via a Chalk-vs-Contrarian engine.

## Non-negotiables (operating mode)
1. **Plan-first / HITL.** Recommend; the human approves. Never submit or finalize anything.
2. **Verification before done.** No module is "done" without a reproduced command + output + PASS/FAIL.
   No "should/probably" without a number, command, or cited source.
3. **No invented facts.** Every datum (lineup, injury, suspension, odd, stat) carries source + UTC date +
   URL. Unconfirmed XI → label `PROBABLE`. Cross-check critical inputs vs ≥2 sources. Never fabricate news.
4. **Simplicity / 80-20.** Minimum code that solves it. No bespoke ML training (market odds carry the
   signal). Statistical models only.
5. **Determinism = reproducible PIPELINE, not a certain outcome.** Fixed seed; timestamped inputs; logged
   sources; snapshots to `data/snapshots/<fixture_id>_<UTC>.json`.
6. **Self-improvement.** After any correction, append the pattern + a preventing rule to `tasks/lessons.md`.
7. **Sparring/PUSH-BACK.** Challenge assumptions with evidence before building.
8. **GOAL-DRIVEN EXECUTION**. Every task → verifiable goal with a check: 1. [step] → verify: [check].

## Objective function
Optimize **E[competition points]** under the rubric in `memory/rules.md` — NOT P(exact score). See that
file for the locked rubric and its 4 unit tests (R5 mitigation).

## §7d — Platform: pollaya.com  `[pick visibility = PENDING VERIFICATION]`
LatAm soccer-pool app, admin-configurable game modes. Our pool's custom admin config: per-match edits up
to **10 min pre-kickoff**; **5 pre-tournament locked picks** (champion · top scorer · top assister · MVP ·
best GK), not editable after tournament start.

**Pick visibility — CONFIRMED 2026-06-02 (pollaya screenshots; was PENDING/False, now FACT):**
**`PICKS_VISIBLE = True`** — premiation/locked picks (champion/scorer/assister/MVP/GK) ARE visible →
`ownership_source = observed` is REAL (measured over opponents). **Per-match scorelines stay HIDDEN** →
per-match ownership = prior only. The HITL gate persists: `prior` is still `is_gated`; the LOCK is a human
action. **Pool:** N=12 today → time-dependent ~20–25 final; **lock Jun-10 evening** (hard backstop = first
match Jun-11; Jun-12 02:00 = VOID, corrected 2026-06-06 — see `pool/decision_clock.md` / `tasks/lessons.md`);
symmetry (opponents see your pick).

**`ownership_source` flag** (`observed | polled | prior`) threads through `pool/`. **Default = `prior`.**
Do NOT assume visibility. **HITL GATE: no locked pick may be finalized while `ownership_source = prior`**
— it must be `observed` (verified in the real pollaya pool) or `polled` (the ~25 entrants) first.

## Key dates (verified 2026-05-30; FIFA/Sky/Al Jazeera/beIN)
- Final roster lock **2026-06-01**; FIFA publishes squads **2026-06-02**; kickoff **2026-06-11**.
- Run the locked-pick council **after Jun 2** (squads public); finalize by **~Jun 10**.
- Group matchdays: MD1 Jun 11–15 · MD2 Jun 18–23 · MD3 (simultaneous) Jun 24–27 · R32 from Jun 28.

## Layout
`src/` per-match engine · `pool/` E[prize] engine · `council/` 5-lens locked-pick council ·
`evals/` backtest · `predictions/` outputs + decisions.csv · `data/` cache + snapshots ·
`memory/` durable facts · `tasks/` todo + lessons. Build order + status: `tasks/todo.md`.

## Data
Primary = API-Football free tier (`league=1&season=2026`), **100 req/DAY**. Cache aggressively; prefetch
static once; don't re-poll odds faster than the ~3h server refresh. Mandatory web fallback when
rate-limited or missing. Odds/quota verdict from the Step-0 probe lives in `memory/rules.md`.
