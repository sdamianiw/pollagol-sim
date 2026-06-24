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

## Running tally — as of 2026-06-24 (post Jun-23→24 tail reconcile)
- **total dual-track gap = +1**  — `== script` (`cumulative()["override_value"] = +1`, TA6 summary verified;
  `us_entered = 151 == board`). FLIPPED back toward neutral vs Jun-23 (+6 → +1) on the PAN-CRO tilt loss.
- **tilt-only override cost = −5**  — L32 headline metric `= total(+1) − EV-UPDATE cumulative(+6: NED-SWE +1 +
  FRA-IRQ +5)`; flipped 0 → −5, driven ENTIRELY by PAN-CRO (−5).
- reconciliation: **prior(as of Jun-23) +6  +  this period (Jun-23→24) −5  =  +1**   (all CSV-backed — see tables).
- ⚠ HONEST READ (L8/L32 — now EMPIRICAL, not asserted): PAN-CRO −5 (TILT lost) is the **symmetric twin** of
  ARG-AUT +5 (TILT won) — same |5|, opposite sign, both discretionary deviations from the EV-optimal pick. The
  two net to ~0, leaving only the **variance + bias risk** L32 warns about. **L32 confirmed empirically: tilt is
  zero-mean noise, not skill → NO tilt in MD-3** (the systematic version of this is the gated field-diff, not gut).
- prior Jun-23 snapshot (retained): total +6 / tilt 0 = prior(≤Jun-21) −3 + MD-2-late(Jun-21→23) +9.
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

## This period — Jun-23 → Jun-24 (4 played fixtures, rows 46-49)
> MD-2 tail. entered/actual per the Jun-24 reconcile; recompute green via `record` (recomputed by
> `src.optimizer.points`); us_entered gate 151==board (TA6 summary). Standings board:
> `standings/standings 24-06-2026/` 074954+075011 (us=151, rank 6/27, leader 164, podium_cut 162).
| fixture  | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|----------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| POR-UZB  | 2-0 | 2-0 | 5-0 | 4 | 4 | 0 | none (EV-pick) |
| ENG-GHA  | 2-0 | 2-0 | 0-0 | 1 | 1 | 0 | none (EV-pick; Ghana held 0-0) |
| PAN-CRO  | 0-2 | 0-1 | 0-1 | 4 | 9 | **−5** | TILT-OVERRIDE (lost; model 0-1 hit exact 9) |
| COL-COD  | 1-0 | 1-0 | 1-0 | 9 | 9 | 0 | none (EV-pick, exact HIT) |
| **period total** | | | | **18** | **23** | **−5** | TILT −5 · EV-UPDATE 0 · none 0 |

PAN-CRO is the **symmetric twin** of ARG-AUT (prior period): the EV-argmax 0-1 was exact (9 pts); Sebas
deviated to the "exciting" 0-2 (away-by-2), which scored 4 (correct outcome, one team's goals). A move
toward MORE goals than the EV pick — the same tilt direction as ARG-AUT, here it LOST. (cf. the MD-3
field-diff refinement: the valid systematic override is toward FEWER goals / the field-avoided draw, NEVER
toward more — that direction is exactly this tilt.)

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
- Verified against the script: `cumulative()["override_value"] = +1` (Jun-24 TA6 `summary` printed
  `override_value=+1`, `us_entered=151`). If a future reconcile disagrees with the script, the script wins.
  (Jun-23 snapshot was +6; Jun-21 was −3.)
