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

## Running tally — as of 2026-06-21 (post-MD-2 reconcile)
- **total dual-track gap = −3**  — `== script` (`cumulative()["override_value"]`, verified TA4 ingest + TA6 summary).
- **tilt-only override cost = −4**  — L32 headline metric `= total(−3) − NED-SWE EV-UPDATE(+1)`; the EV-UPDATE
  is a disciplined fresh-argmax switch, not tilt, so it is excluded from the tilt cost.
- reconciliation: **prior(≤Jun-19) −9  +  this period +6  =  −3**   (both CSV-backed — see tables).

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
  the OCR-confirmed Jun-21 picks-vs-actual screenshots (TA1, 12/12).
- **I-3 intact** — this ledger READS results + picks and computes numbers; it never writes a model parameter.
- Verified against the script: `cumulative()["override_value"] = −3` (TA4 ingest printed `override_value=-3`;
  re-confirmed at TA6 `summary`). If a future reconcile disagrees with the script, the script wins.
