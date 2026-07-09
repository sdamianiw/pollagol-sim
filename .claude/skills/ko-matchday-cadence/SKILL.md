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
  draw is dominated at every penalty rate (**L54**). `ko_adjust` FULL120 is correct as of `bc8cdd2` — the
  diagonal-wipe that understated scored-draw mass AND overstated the council `dec−draw` gap (a silent
  no-fire window on tight boards) is fixed (**L58**); driver suite = **269/269**.
- **Doctrine = HOLD the freeze** (2026-07-03 contrarian MC, **L50**): while leading, per-match EV-argmax is
  E[prize]-optimal (deliberate deviations cost −8% to −20% of the pool); the **locked-50 is the dominant
  residual variance** and is NOT match-layer-addressable. **Contingent trigger:** re-evaluate the variance
  posture ONLY if España is eliminated pre-QF (a public observable) — never on a gut read.

## P0 — Context recovery  ·  gate: state restated from disk
Read `memory/MEMORY.md` → `pollagol-state.md` LATEST, `tasks/HANDOFF.md` top banner, `CLAUDE.md`,
`tasks/lessons.md` (esp. L33/L49/L50/L53/L54/L57/L59). Confirm: current rank/`us_entered`, HEAD commit,
`git rev-parse --abbrev-ref HEAD` (= `rho-fit`), frozen diff EMPTY, current UTC vs the next KO lock (10 min
pre-kickoff). PASS/FAIL.
- **Lag gate (L59, HARD):** diff the latest standings-board `us_entered` (newest screenshot) vs
  `cumulative(decisions.csv)["us_entered"]`. If the board is AHEAD, played KO games are UNRECORDED — a
  paused cadence silently accrues this (Jul-3: board 315 vs CSV 273 = 8 games behind). Run the **P4 record
  procedure** on the missing games BEFORE the cadence. Gate = board `us_entered` == CSV `us_entered`.

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

## P4 — Record played  ·  gate: cumulative `us_entered` == board (L45)  ·  DEFERRABLE
`record()` **cannot create a row** and `backfill` **aborts** on a fixture absent from its snapshot — so the
order is FIXED (L59). For each played game not yet in `decisions.csv`:
1. **log_decision** the row — `pick` MANDATORY-non-empty (else `record()` crashes): `pick` = the FULL120
   `ko_adjust` argmax IF its council fired (register the flip, L57/L44/NOR-FRA), **else** the 90' argmax
   (sub-floor favourite ET-flips are noise, not a pick change). Full team strings + `fixture_id` (L49).
   [`dl.log_decision({fixture_id, home, away, utc, pick, context_flag, source, reasoning})`]
2. **backfill** the model columns from the freshest **pre-lock** snapshot that CONTAINS the game —
   **TWO-BATCH** when games span snapshots (a game drops out of the API once played, so an early game needs
   its own earlier snapshot; ONE `backfill` call per snapshot, else the loop aborts on the absent fixture):
   `python -m src.decision_score backfill --snapshot data/snapshots/md4_<pre-lock-UTC>.json`
   **OVERLAP case (L61, 2026-07-09):** when the games' snapshots OVERLAP (an early snapshot also contains
   the later games), a chronological batch loop greedily backfills the later rows from the OLDEST snapshot
   (wrong provenance) and reverse order ABORTS on the earlier game. Blank/fill **ONE fixture at a time,
   freshest snapshot first** — the idempotent `modal`+`m_h` skip then protects each already-correct row.
3. **record** the 120' result (pens excluded) + entered pick:
   `python -m src.decision_score record <fid> "<H-A actual>" --entered-pick "<H-A entered>"`
4. **summary + reconcile:** `python -m src.decision_score summary` → `Σ us_entered == board` (L45 I-NOFAB);
   pre-existing rows byte-identical after the rewrite.
5. **override ledger** (`tasks/override_ledger.md`): classify each row {none · EV-UPDATE · TILT-OVERRIDE};
   identity `tilt + EV-UPDATE + DRAW-EXC == cumulative()["override_value"]` (the script wins on any dispute).
6. **standings** (when a board screenshot lands): create `standings/<date>/standings.json` (full N-array +
   `our_points` + `our_rank`) → `python -m src.decision_score standings <YYYY-MM-DD>` (auto-pulls
   `override_value`; appends `standings_log.csv`).
May be deferred to the next screenshot. Gate: cumulative `us_entered` == board. PASS/FAIL.

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

## Worked example — 2026-07-03 R32 day-5 (reproducible on committed artifacts, read-only)
Snapshot `data/snapshots/md4_2026-07-03T11-00-08Z.json` (quota 496, 3/3 F27). Fixture ids: Australia-Egypt
`fb270a3dac2b682c861bd674a5ff4a04` · Argentina-Cape Verde `3e161b2448ed76d6b0c0f5bda6fd5bf2` · Colombia-Ghana
`88e032a2b2e5042d26db3f0da1df924a`.
- **P2** `python -m src.ko_cadence flipcheck --snapshot data/snapshots/md4_2026-07-03T11-00-08Z.json --baseline-snapshot data/snapshots/md4_2026-07-01T18-29-49Z.json`
  → **3/3 HOLD**, `gap_base +0.0000` (fresh 90' argmax == baseline == entered: AUS 0-1 · ARG 2-0 · COL 1-0).
- **P3** `python -m src.ko_cadence ko --snapshot data/snapshots/md4_2026-07-03T11-00-08Z.json --fixture <id>`
  → FULL120 PICK **0-1** (E 2.969) · **2-0** (E 4.327) · **1-0** (E 3.840); **COUNCIL no-fire** on all three
  (all decisive). Odds-sensitivity note: AUS-EGY FIRED the council on the Jul-1 snapshot (modal 1-1 ≠ argmax)
  but NO-FIRE here (Egypt firmed → modal 0-1 == argmax) → **re-check any near-even board at T-1h** before lock.
- **Outcome:** picks ROCK-SOLID FROZEN, no council to launch; HOLD all three (I-HITL).
- **P4** verified 2026-07-03 (commit `e281987`): 8 played games → `us_entered` 273→315 == board, override
  +18→+23; sandbox-reproducible from `git show bc8cdd2:predictions/decisions.csv` (log→two-batch-backfill→
  record → `cumulative()["us_entered"] == 315`, real CSV untouched).
