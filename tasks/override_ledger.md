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

## Running tally - as of 2026-06-28 (post KNOCKOUT v1 Phase A reconcile; GROUP STAGE CLOSED - all 72 fixtures played, J/K/L recorded)
- **total dual-track gap = +8**  - `== script` (`cumulative()["override_value"] = +8`, TA7 `summary` verified
  2026-06-28: `us_entered = 245 == board` (**RANK 1/27**), `us_model = 237`). Moved +1 -> +8 this batch (the 6 J/K/L
  fixtures); the two overrides are Colombia-Portugal (+3) and Algeria-Austria (+4), BOTH DRAW-EXCEPTIONS that WON.
- **tilt-only override cost = -2 (points)**  - UNCHANGED (no tilt this batch; both J/K/L overrides are DRAW-EXCEPTION, not tilt).
- **EV-UPDATE cumulative = +6 (points)**  - UNCHANGED (no EV-UPDATE flip this batch).
- **DRAW-EXCEPTION cumulative = -3 -> +4 (points)**  - **+7 this batch**: Colombia-Portugal entered 1-1 (EV 0-1) vs
  actual 0-0 = +3; Algeria-Austria entered 1-1 (EV 0-1) vs actual 3-3 = +4. Both are real engine blind-spots (under-
  priced mutual-draw incentive in a DEAD RUBBER) that WON - but per **L51** this is VARIANCE on a now-CLOSED edge (KO
  has no dead rubbers; the reflex STOPS at the group stage). L46/L8: a winning override is still variance, not skill.
- reconciliation: **tilt(-2) + EV-UPDATE(+6) + DRAW-EXCEPTION(+4) + none(0) = +8 == script.**
- prior Jun-27 snapshot (retained): total +1 / tilt -2 (full chain in the Jun-27 block below).

## Running tally - as of 2026-06-27 (post MD-3 day-4 FINAL reconcile; GROUP STAGE CLOSED, 18 MD-3 fixtures played)
- **total dual-track gap = +1**  - `== script` (`cumulative()["override_value"] = +1`, TA7 `summary` verified
  2026-06-27: `us_entered = 217 == board` (rank 2/27), `us_model = 216`). Moved -2 -> +1 this batch; the lone
  override is Cape Verde-Saudi (+3, a TILT-OVERRIDE that WON).
- **tilt-only override cost = -2 (points)**  - prior -5 + **Cape Verde-Saudi +3** (entered MODAL 1-1 over EV pick
  1-0 on a near-coinflip; gained +3 because it drew). **tilt COUNT +1.** L46: a WINNING override carries the SAME
  bias risk as a losing one (L8 symmetry) - the +3 is variance, NOT edge; it does NOT launder the no-tilt rule.
- **EV-UPDATE cumulative = +6 (points)**  - UNCHANGED in points (NED-SWE +1, FRA-IRQ +5). **count +1:** Norway-France
  is a NEW EV-UPDATE flip-switch but **override 0** - the recorded `pick` was registered 0-1 -> 1-2 (the engine's
  final pre-KO argmax, verified on `md1_2026-06-26T18-17-02Z`, E[pts]=3.045), so the entered 1-2 followed the model.
  Sebas-directed (2026-06-27) + engine-adjudicated (L35/L44). See the NOR-FRA consistency note in the day-4 period.
- **DRAW-EXCEPTION cumulative = -3 (points)**  - UNCHANGED (SUI-CAN day-1, the only fire).
- reconciliation: **tilt(-2) + EV-UPDATE(+6) + DRAW-EXCEPTION(-3) + none(0) = +1 == script.**
- prior Jun-26 snapshot (retained): total -2 / tilt -5 = Jun-25 -2 + MD-3-day-2/3 net-0 (JAP-SUE+TUN-NED tilt count +2, points +0).
- prior Jun-25 snapshot (retained): total -2 / tilt -5 = Jun-24 +1 + MD-3-day-1 SUI-CAN DRAW-EXCEPTION -3.
- prior Jun-24 snapshot (retained): total +1 / tilt -5 = prior(<=Jun-23) +6 + MD-2-tail(Jun-23->24) -5.
- prior Jun-23 snapshot (retained): total +6 / tilt 0 = prior(<=Jun-21) -3 + MD-2-late(Jun-21->23) +9.
- prior Jun-21 snapshot (retained): total -3 / tilt -4 = prior(<=Jun-19) -9 + MD-2(Jun-19->21) +6.

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

## This period — MD-3 day-1 (Jun-24 → Jun-25), 6 played fixtures (rows 50-55)
> Recorded 2026-06-25 from the Jun-25 07:59 pollaya board (`standings/standings 25-06-2026/` + `PICKS VS
> ACTUAL RESULTS/...2026-06-25 1735*.png`); recompute green (TA2/3 6/6 via `record` → `src.optimizer.points`);
> CONFIRM-GATE "confirmado"; us_entered gate 168 == board (TA6). Resolved by full team strings (L34): the board
> codes CRS = South Korea (NOT Costa Rica), RCH = Czechia (NOT Chile); keyed by fixture_id, never the 3-letter code.
| fixture  | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|----------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| Switzerland-Canada       | 1-1 | 1-0 | 2-1 | 1 | 4 | **−3** | DRAW-EXCEPTION (1st live fire; MISS) |
| Bosnia & H.-Qatar        | 2-0 | 2-0 | 3-1 | 4 | 4 | 0 | none (EV-pick) |
| Morocco-Haiti            | 2-0 | 2-0 | 4-2 | 4 | 4 | 0 | none (EV-pick) |
| Scotland-Brazil          | 0-2 | 0-2 | 0-3 | 4 | 4 | 0 | none (EV-pick) |
| South Africa-South Korea | 0-1 | 0-1 | 1-0 | 0 | 0 | 0 | none (EV-pick; RSA upset) |
| Czech Republic-Mexico    | 0-1 | 0-1 | 0-3 | 4 | 4 | 0 | none (EV-pick) |
| **period total** | | | | **17** | **20** | **−3** | DRAW-EXCEPTION −3 · tilt 0 · EV-UPDATE 0 · none 0 |

SUI-CAN is the **FIRST live fire** of the qual_state draw-signal (MUTUAL-DRAW-SECURES: both Switzerland & Canada
were DRAW-SUFFICIENT → a mutual draw secured both top-2 spots). Sebas entered 1-1 (market drawP ~0.31) against
the EV-argmax 1-0. It **MISSED** (actual 2-1, Switzerland won) → −3. This is the **sanctioned DRAW-EXCEPTION**,
categorically distinct from TILT (L32): it follows the qual-state signal, not gut, so it is logged on its own
DRAW-EXCEPTION line and does NOT touch the tilt-only metric (still −5).

## This period — MD-3 day-2/3 (Jun-25 → Jun-26), 6 played fixtures (Groups E/F/D)
> Recorded 2026-06-26 from the Jun-26 18:27 picks-vs-actual screenshots (`PICKS VS ACTUAL RESULTS/...2026-06-26
> 1827*.png`, format BIG=entered `(paren)`=actual) + board (`standings/standings 26-06-2026/`). Recompute green
> (TA2 6/6 both tracks + `record` → `src.optimizer.points`); CONFIRM-GATE "confirmado"; us_entered gate 192 ==
> board (TA7). Divergences classified by re-running the frozen engine on the T-1h lock snapshot
> `md1_2026-06-25T22-07-56Z` (L40), resolved by full team strings (L34).
| fixture  | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|----------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| Curaçao-Ivory Coast    | 0-2 | 0-2 | 0-2 | 9 | 9 | 0 | none (EV-pick, exact PLENO) |
| Ecuador-Germany        | 1-2 | 1-2 | 2-1 | 0 | 0 | 0 | none (EV-pick; Germany comeback) |
| Japan-Sweden           | 2-1 | 1-0 | 1-1 | 1 | 1 | **+0** | TILT-OVERRIDE (off lock-argmax 1-0; net-0) |
| Tunisia-Netherlands    | 0-3 | 0-2 | 1-3 | 4 | 4 | **+0** | TILT-OVERRIDE (off lock-argmax 0-2; net-0) |
| Turkey-USA             | 1-2 | 1-2 | 3-2 | 1 | 1 | 0 | none (EV-pick; Turkey 3-2 UPSET — L41) |
| Paraguay-Australia     | 0-0 | 0-0 | 0-0 | 9 | 9 | 0 | none (EV-pick, exact PLENO; blind-lock paid) |
| **period total** | | | | **24** | **24** | **+0** | TILT 0pts (count +2) · EV-UPDATE 0 · DRAW-EXCEPTION 0 · none 0 |

JAP-SUE + TUN-NED are **TILT-OVERRIDE / net-0** (L40): at the T-1h lock fetch the engine argmax HELD at the
baselines (1-0, 0-2), but Sebas entered the flickers (2-1, 0-3). Both happened to score identically to the
baseline (1 and 4) → net-0, but the **count** increments — net-0 does NOT launder the tilt (the only sanctioned
systematic override is the gated field-diff, never a gut flicker). Group D blind-locks net **+10** (PAR-AUS 9
PLENO + TUR-USA 1): the flagged Turkey rotation/upset tail materialized (3-2) but PAR-AUS's pleno more than
offset it — L41 "grid-invariant ≠ upset-safe".

## This period - MD-3 day-4 / FINAL (Jun-26 -> 27), 6 played fixtures (Groups I/G/H) - GROUP STAGE CLOSED
> Recorded 2026-06-27 from the MD-3 day-4 contract inputs (BIG=entered, (paren)=actual) + Jun-27 board (us=217
> rank 2/27, gap_podium +1 - IN PODIUM for the first time). CONFIRM-GATE "confirmado" (Sebas). I-NOFAB gate (L45):
> the 2026-06-27 screenshot is NOT in-repo, so the gate is Sebas confirmado + the independent reconcile
> Sigma pts_entered = 25 == board delta (217-192). Recompute green (record -> src.optimizer.points, 6/6 both
> tracks). Resolved by fixture_id / full team strings (L34).
| fixture | entered | model pick (base) | actual | pts_ent | pts_model | override | flag |
|---------|:-------:|:-----------------:|:------:|:-------:|:---------:|:--------:|------|
| Norway-France | 1-2 | 1-2 | 1-4 | 4 | 4 | **+0** | EV-UPDATE flip-switch (pick registered 0-1->1-2, engine-verified) |
| Senegal-Iraq | 2-0 | 2-0 | 5-0 | 4 | 4 | 0 | none (EV-pick; Senegal 5-0) |
| New Zealand-Belgium | 0-2 | 0-2 | 1-5 | 3 | 3 | 0 | none (EV-pick; Belgium 5-1) |
| Egypt-Iran | 1-0 | 1-0 | 1-1 | 1 | 1 | 0 | none (EV-pick; drew) |
| Cape Verde-Saudi Arabia | 1-1 | 1-0 | 0-0 | 4 | 1 | **+3** | TILT-OVERRIDE (WON; modal hedge; L46 variance != edge) |
| Uruguay-Spain | 0-1 | 0-1 | 0-1 | 9 | 9 | 0 | none (EV-pick, exact PLENO) |
| **period total** | | | | **25** | **22** | **+3** | TILT +3 (Cape Verde, won) - EV-UPDATE +0 (NOR-FRA flip absorbed) - none 0 |

**NOR-FRA consistency note.** Booked EV-UPDATE / override 0: the recorded `pick` was updated 0-1->1-2 to the
engine's final pre-KO argmax (verified on `md1_2026-06-26T18-17-02Z`, neutral, rho=-0.05 frozen; E[pts]=3.045),
so the entered 1-2 followed the model. This DIFFERS from the FRA-IRQ (Jun-23) EV-UPDATE, which kept `pick` at the
baseline 2-0 and COUNTED the gap +5. Per Sebas's explicit 2026-06-27 directive (flip-switch != tilt; register the
argmax change in decisions) + L44 (engine adjudicates the number), NOR-FRA reflects the verified flip. The
historical FRA-IRQ row is NOT re-opened - the divergence is flagged here for separate adjudication.

**Cape Verde (L46).** Entered MODAL 1-1 over EV-argmax 1-0 (sub-floor margin, near-coinflip), gained +3 because
the game drew. Logged TILT-OVERRIDE that WON - by L8 symmetry a winning override carries the SAME bias risk as a
losing one; +3 is variance, not edge.

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
- Verified against the script: `cumulative()["override_value"] = +1` (Jun-27 TA7 `summary` printed
  `override_value=+1`, `us_entered=217`, `us_model=216`). If a future reconcile disagrees with the script,
  the script wins. (Jun-25 snapshot −2; Jun-24 +1; Jun-23 +6; Jun-21 −3.)
