# Override Ledger — CANONICAL (Pollagol Mundialera 2026)

> **Single source of truth** for the dual-track OVERRIDE classification + running tally.
> Created **2026-06-21** (MD-2 reconcile, contract `contract-md-2-ledger`). This file SUPERSEDES every
> scattered override total in prose (tasks/HANDOFF.md, tasks/lessons.md, predictions/*/summary.md).
>
> RAW facts (entered / actual / points) live in `predictions/decisions.csv`. This file holds the
> **classification** `{none, EV-UPDATE, TILT-OVERRIDE}` + the running `override_value`, which MUST reconcile
> to `cumulative(decisions.csv)["override_value"]` (the script — `src/decision_score.py:131`).

## Definitions
- **override (per row)** = `pts_entered − points_actual` = the entered pick's score minus the MODEL pick's
  (`pick` column) score. `< 0` = the human override cost points; `> 0` = it gained; `0` = neutral/none.
- **deviation_flag** — lives ONLY here (NOT a CSV column; adding one would edit `src/decisionlog.py`,
  outside the allowed write-set → FM-scope-creep). Derivable from CSV via `entered_pick != pick`.
  - `none` — entered == model `pick` (an EV-pick the human typed faithfully).
  - `EV-UPDATE` — entered != `pick` but followed a disciplined fresh-argmax switch (e.g. NED-SWE). NOT tilt.
  - `TILT-OVERRIDE` — entered != `pick`, discretionary/gut (e.g. BRA-HAI, USA-AUS).

## Running tally — as of 2026-06-23 (post Jun-21→23 reconcile)
- **total dual-track gap = +6**  — `== script` (`cumulative()["override_value"]`, verified TA4 ingest printed
  `override_value=6` + TA6 summary). The dual-track FLIPPED sign vs Jun-21 (was −3, model ahead → now +6, entered ahead).
- **tilt-only override cost = 0**  — L32 headline metric `= total(+6) − EV-UPDATE cumulative(+6: NED-SWE +1 +
  FRA-IRQ +5)`; EV-UPDATEs are disciplined fresh-argmax switches, excluded from the tilt cost.
- reconciliation: **prior(as of Jun-21) −3  +  this period (Jun-21→23) +9  =  +6**   (all CSV-backed — see tables).
- ⚠ HONEST READ (L8/L32): the +9 period = FRA-IRQ +5 (legit EV-UPDATE, engine flip) + ARG-AUT +5 (discretionary
  TILT that HIT on variance) + BEL-IRN −1 (tilt lost) + NOR-SEN 0. tilt-only returned to 0 driven by ONE lucky
  hit (ARG-AUT), not skill — a winning override carries the same bias risk as a losing one. **L32 stands.**
- prior Jun-21 snapshot (retained): total −3 / tilt −4 = prior(≤Jun-19) −9 + MD-2(Jun-19→21) +6.

## This period — MD-2 (Jun-19 → Jun-21), 8 played fixtures
| fixture  | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|----------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| BRA-HAI  | 3-0 | 2-0 | 3-0 | 9 | 4 | **+5** | TILT-OVERRIDE (HIT) |
| USA-AUS  | 2-1 | 1-0 | 2-0 | 4 | 4 | **+0** | TILT-OVERRIDE (neutral) |
| NED-SWE  | 2-1 | 1-0 | 5-1 | 4 | 3 | **+1** | EV-UPDATE (disciplined fresh-argmax) |
| SCT-MAR  | 0-1 | 0-1 | 0-1 | 9 | 9 | 0 | none (EV-pick, exact HIT) |
| TUR-PAR  | 1-0 | 1-0 | 0-1 | 0 | 0 | 0 | none (EV-pick; Paraguay upset) |
| GER-CIV  | 2-0 | 2-0 | 2-1 | 4 | 4 | 0 | none (EV-pick) |
| ECU-CUW  | 2-0 | 2-0 | 0-0 | 1 | 1 | 0 | none (EV-pick; 0.87-fav drew) |
| TUN-JAP  | 0-1 | 0-1 | 0-4 | 4 | 4 | 0 | none (EV-pick) |
| **period total** | | | | **35** | **29** | **+6** | TILT +5 · EV-UPDATE +1 · none 0 |

## This period — Jun-21 → Jun-23 (8 played fixtures, rows 38-45)
> OCR-confirmed vs the Jun-23 pollaya board (`PICKS VS ACTUAL RESULTS/` screenshots 073151+073201, format
> `ENTERED(actual)`); recompute green (TA2 16/16); us_entered gate 133==board (TA6). Resolved by full team
> strings (L34); JOR opponent = Algeria (green/crescent flag), NOT the board "ARG" code.
| fixture  | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|----------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| ESP-KSA  | 2-0 | 2-0 | 4-0 | 4 | 4 | 0 | none (EV-pick) |
| BEL-IRN  | 2-1 | 1-0 | 0-0 | 0 | 1 | **−1** | TILT-OVERRIDE (lost; Iran held 0-0) |
| URU-CPV  | 1-0 | 1-0 | 2-2 | 0 | 0 | 0 | none (EV-pick; Cape Verde drew) |
| NZL-EGY  | 0-1 | 0-1 | 1-3 | 3 | 3 | 0 | none (EV-pick) |
| ARG-AUT  | 2-0 | 1-0 | 2-0 | 9 | 4 | **+5** | TILT-OVERRIDE (entered modal 2-0, no engine flip; HIT) |
| FRA-IRQ  | 3-0 | 2-0 | 3-0 | 9 | 4 | **+5** | EV-UPDATE (Jun-22 cadence flip 2-0→3-0, gap +0.047 SIGNAL; HIT) |
| NOR-SEN  | 2-1 | 1-0 | 3-2 | 4 | 4 | 0 | TILT-OVERRIDE (neutral) |
| JOR-ALG  | 0-1 | 0-1 | 1-2 | 4 | 4 | 0 | none (EV-pick) |
| **period total** | | | | **33** | **24** | **+9** | TILT +4 · EV-UPDATE +5 · none 0 |

Both Jun-22 deviations are artifact-grounded from the same pre-lock snapshot `md1_2026-06-22T16-57-21Z.json`
(fetched 16:57Z, ~3min before ARG-AUT KO; the last pre-lock read), re-derived with the frozen engine:
- **FRA-IRQ = EV-UPDATE**: argmax=3-0 (modal 3-0), EV 4.053 vs baseline-2-0 EV 4.006, gap **+0.047 > 0.040**
  floor — a disciplined fresh-argmax switch Sebas followed.
- **ARG-AUT = TILT**: argmax stayed **1-0** (= baseline; no flip), modal 2-0. Sebas entered the modal 2-0,
  whose EV 3.277 is **−0.042 BELOW** the argmax EV 3.319 — a discretionary move away from the EV-optimal pick,
  not an engine signal. (It HIT on variance; that does not make it EV-UPDATE — L8 symmetry.)

## Historical (rows played ≤ Jun-19) — CSV-backed, sums to prior −9
Non-zero override rows (`override = pts_entered − points_actual`; all other dual rows = 0):
| fixture | override | note |
|---------|:--------:|------|
| Haiti–Scotland | −5 | entered 0-2 vs model 0-1 (actual 0-1) — MD1 |
| Netherlands–Japan | +4 | entered 1-1 vs model 1-0 (actual 2-2) |
| USA–Paraguay | +1 | |
| France–Senegal | +1 | |
| Portugal–DR Congo | +1 | |
| Uzbekistan–Colombia | +1 | |
| Switzerland–Bosnia & H. | +1 | |
| **Ghana–Panama** | **−8** | entered 1-1 vs model 1-0; actual 1-0 (model hit exact 9) — **L32 driver** |
| **Mexico–South Korea** | **−5** | entered 2-1 vs model 1-0; actual 1-0 (model hit exact 9) — **L32 driver** |
| **prior total** | **−9** | `= (+4+1+1+1+1+1) − (5+8+5)` ; recomputed from CSV, verified C-B1 |

## Provenance / invariants
- Every entry traces to `predictions/decisions.csv` (`entered_pick`/`pts_entered`/`points_actual`) +
  the OCR-confirmed picks-vs-actual screenshots (Jun-21 TA1 12/12; Jun-23 `PICKS VS ACTUAL RESULTS/`
  073151+073201, all 8 legible, format `ENTERED(actual)`).
- **I-3 intact** — this ledger READS results + picks and computes numbers; it never writes a model parameter.
- Verified against the script: `cumulative()["override_value"] = +6` (Jun-23 TA4 ingest printed
  `override_value=6`; re-confirmed at TA6 `summary`). If a future reconcile disagrees with the script, the
  script wins. (Jun-21 snapshot was −3.)
