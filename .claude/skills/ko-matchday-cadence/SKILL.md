---
name: ko-matchday-cadence
description: >
  Run one knockout-round cadence for the Pollagol WC-2026 pool: ONE amortized fetch of the remaining
  KO fixtures, a deterministic flip-check vs the frozen baselines, FULL120 ko_adjust per KO game, the
  advisory LLM council on any genuine near-even board, and a HITL entry recommendation. Use at each
  KO fixture's T-1h window (R32/R16/QF/SF/final). Read-only + I-HITL: recommend, never lock.
---

# KO Matchday Cadence

Deterministic, auditable knockout cadence. The engine is **FROZEN**; this skill only *reads* it via the
non-frozen `src/ko_cadence.py` driver + `src/ko_adjust.py`. Nothing is entered or locked by the agent
(**I-HITL** — Sebas types every pick). Every phase has a binary gate; show the command output.

## Invariants (verify, don't assume)
- **Engine FROZEN**: 0 edits to `src/model.py`, `optimizer.py`, `strength.py`, `context.py`,
  `pool/pool_montecarlo.py`, `evals/backtest_results.json`, `decisionlog.py`, `decision_score.py`,
  `run_matchday.py` → `git diff --stat` on these = EMPTY.
- **I-3**: no result→model path. **I-HITL**: recommend only. **Determinism (B4)**: replay byte-identical.
- **L50 chalk-protect** (while leading): enter the EV-argmax; the only override is a rule-confirmed,
  model-grounded EV-UPDATE, never a gut tilt. **L49**: bind every fixture by full team string + fixture_id.
- **KO_SCORING = FULL120** (120', pens excluded): the pool scores the KO result, so the KO-correct pick is
  the `ko_adjust` FULL120 argmax, **not** the raw 90' argmax the live cadence prints (**L57**). The 1-1
  draw is dominated at every penalty rate (**L54**).

## P0 — Context recovery  ·  gate: state restated from disk
Read `memory/MEMORY.md` → `pollagol-state.md` LATEST, `tasks/HANDOFF.md` top banner, `CLAUDE.md`,
`tasks/lessons.md` (esp. L33/L49/L50/L53/L54/L57/L59). Confirm: current rank/`us_entered`, HEAD commit,
`git rev-parse --abbrev-ref HEAD` (= `rho-fit`), frozen diff EMPTY, current UTC vs the next KO lock (10 min
pre-kickoff). PASS/FAIL.
- **Lag gate (L59, HARD):** diff the latest standings-board `us_entered` (newest screenshot) vs
  `cumulative(decisions.csv)["us_entered"]`. If the board is AHEAD, played KO games are UNRECORDED — a
  paused cadence silently accrues this (Jul-3: board 315 vs CSV 273 = 8 games behind). RECORD them
  (`log_decision` → `backfill` from the freshest **pre-lock** snapshot per game — a game not in the latest
  snapshot needs its own earlier one, else `backfill` aborts the loop — → `record`) and reconcile the
  ledger BEFORE running the cadence. Gate = board `us_entered` == CSV `us_entered`.

## P1 — ONE amortized fetch  ·  gate: HTTP-200 + in-window == calendar count
`--win-lo` excludes already-played games; `--expect` = the **FIFA-calendar** count of remaining KO fixtures
with kickoff > now (never a probe of the same endpoint — F23/L25):
```
python -m src.fetch_md1 --md 4 --win-lo <UTC-after-last-played> --win-hi <UTC> --expect <N>
```
Snapshot → `data/snapshots/md4_<UTC>.json`. Verify the target fixture_id is present and played games ABSENT.
Odds quota resets monthly; don't re-poll faster than the ~3h refresh. PASS/FAIL.

## P2 — Flip-check all returned  ·  gate: verdicts + B4 determinism
```
python -m src.ko_cadence flipcheck --snapshot <new.json> --baseline-snapshot <prior md4.json>
# or, once picks are logged:  --baseline-csv   (reads predictions/decisions.csv `pick`)
```
Per fixture: fresh 90' EV-argmax vs baseline + `gap_base` → **HOLD** (<0.030) · **DEFER** (0.030–0.040,
re-check at T-1h) · **FLIP** (>0.040, a real EV-UPDATE — re-derive, L35). `GUARD-STOP` = non-x.5 line (rare).
Re-run once → byte-identical (B4). Most fixtures HOLD; a FLIP while leading is an EV-UPDATE, never a tilt (L50).
PASS/FAIL.

## P3 — KO analysis + conditional council  ·  gate: FULL120 argmax + council decision
For each **KO fixture** (draws resolve in ET, so run this for EVERY KO game, not only draw-modal ones):
```
python -m src.ko_cadence ko --snapshot <new.json> --fixture <id> [--candidates 1-0,2-1,1-1,1-2]
#   --ko-rule REG90   for a 90'-scoring sensitivity check
```
Read: the **FULL120 PICK (argmax)** (this is the recommendation — note `[flipped from 90' …]` when the KO
rule moves the pick, L57), the candidate E[pts] (90' vs FULL120), the f-band (best_decisive vs best_draw —
draw dominated at every f, L54), and **COUNCIL: FIRE / no-fire**.

**Council FIRES** on a genuine near-even board (L53): weak favourite (`max(devig)<0.55`) AND EV-argmax ≠ modal,
OR the FULL120 best-draw within ε of best-decisive, OR an opposite-winner divergence vs the human's intent.
When it fires, convene the advisory panel (isolated lenses: form/tactical · market/historian base-rate ·
chalk/leader-doctrine · adversarial/premortem) → write `council/outputs/<slug>/verdict.md` (NED-MAR /
France-Sweden / Belgium-Senegal template). **The council is ADVISORY (L44): the frozen engine adjudicates
E[pts]; no lens computes EV.** Resolve any parameter challenge (e.g. the penalty rate f) by **sweeping the
engine** across the challenger's range and reading the argmax — verify on a number, not vibes (L54c). If the
board is clear, state "no council — argmax decisive." PASS/FAIL.

## P4 — Record played  ·  gate: recompute == board (L45)  ·  DEFERRABLE
When results post (or a standings screenshot lands): `python -m src.decision_score record <fid> "H-A"
--entered-pick "H-A"`; `… summary`; reconcile Σ pts_entered against the board delta (L45 I-NOFAB gate).
May be deferred to the next screenshot. PASS/FAIL.

## P5 — Closeout  ·  gate: frozen diff EMPTY + recommendation delivered
Frozen `git diff --stat` EMPTY; I-3 grep clean; `predictions/decisions.csv` untouched unless P4 ran. Deliver
per-fixture **HITL recommendations** with UTC deadlines (10 min pre-KO). Update `memory/pollagol-state` LATEST
+ `tasks/HANDOFF.md` banner; append a `tasks/lessons.md` gate-log line. Commit data/doc (+ any new code with a
`/code-review` gate first). **Nothing locked.** PASS/FAIL.

## Verification ladder (RED → AMBER → DEFER; gate on RED)
- **RED (block):** frozen-diff empty · B4 determinism · fetch completeness (calendar denominator) · full-string
  bind · I-3 clean.
- **AMBER:** per-fixture flip gaps · FULL120 argmax + council trigger · EV-UPDATE vs tilt classification.
- **DEFER:** later-round fixtures at their own T-1h · P4 recording until results/board · a not-yet-played result.
