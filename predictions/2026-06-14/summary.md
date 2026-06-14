# MATCHDAY refresh — 2026-06-14 (Track B, DRY-RUN / HITL) — dual-track + MD1 cadence complete

**Source:** The Odds API (snapshot `md1_2026-06-14T12-14-52Z.json`, fetched 2026-06-14T12:14:51Z; quota 487→481).
**Engine:** FROZEN (exact=3) — M1 ingest → M2 strength → M3 DC(μ_eff) → M5 neutral → M4 argmax E[pts]. **0 edits** to model/optimizer/strength/context.
**Schema:** additive dual-track (26→28 cols: `entered_pick`, `pts_entered`). Suite **188/188**.
**STATUS:** RECOMMENDATIONS only. CC never enters/locks pollaya — Sebas types every pick.

## 🚨 TODAY's revert call (deadline-critical)
- **GER-CUW — revert `4-0` → `3-0`** (editable until **16:50Z**). 3-0 = model EV-argmax = modal (Germany de-vig 91.8%, totals 4.5); 4-0 is a strictly lower-EV scoreline. `is_model_high_confidence` = TRUE → override only with a logged reason.
- **NED-JPN — `1-1` → `1-0`** (editable until **19:50Z**) — the judgment fixture. 1-0 = E[pts] argmax; 1-1 = modal on a near-even board (NED 48 / draw 26 / JPN 25). Keep 1-1 **only** with a logged draw-lean thesis; else revert.
- CIV-ECU `0-1` / SWE-TUN `1-0`: model-aligned, no change.

## Dual-track standing (n=8 played)
**us_entered 15 / us_model 19 / B1 23 / B2 17 · field median 19 · rank 20/27 · override −4.**
`us_entered` is the REAL pollaya total (independently confirmed by the standings screenshots). Following the model (19) would sit at the **field median** (≈ rank 13–14). The override cost is essentially one fixture.

| fixture | entered | model | B1 | actual | pts_ent | pts_model | override |
|---|---|---|---|---|---|---|---|
| MEX-RSA | 1-0 | 1-0 | 1-0 | 2-0 | 4 | 4 | 0 |
| KOR-CZE | 1-1 | 1-1 | 1-0 | 2-1 | 1 | 1 | 0 |
| CAN-BIH | 1-0 | 1-0 | 1-0 | 1-1 | 1 | 1 | 0 |
| USA-PAR | 2-1 | 1-0 | 1-0 | 4-1 | 4 | 3 | **+1** |
| QAT-SUI | 0-3 | 0-2 | 0-1 | 1-1 | 0 | 0 | 0 |
| BRA-MAR | 2-1 | 1-0 | 1-0 | 1-1 | 1 | 1 | 0 |
| HAI-SCO | 0-2 | 0-1 | 0-1 | 0-1 | 4 | 9 | **−5** |
| AUS-TUR | 0-2 | 0-1 | 0-1 | 2-0 | 0 | 0 | 0 |
| **Σ** | | | | | **15** | **19** | **−4** |

**HAI-SCO −5** dominates: entered 0-2, but the model's 0-1 hit the exact score (9 pts). USA-PAR +1 (the 2-1 caught a goal). The other 6 net 0.

## MD1 baselines — 24 rows complete (FROZEN model; refresh before each deadline)
- **Today (entered):** GER-CUW 3-0¹, NED-JPN 1-0¹, CIV-ECU 0-1, SWE-TUN 1-0.
- **Jun-15:** ESP-CPV 3-0, BEL-EGY 1-0, KSA-URU 0-1, IRN-NZL 1-0 (KO Jun-16 01:00Z).
- **Jun-16:** FRA-SEN 1-0, IRQ-NOR 0-2, ARG-ALG 1-0², AUT-JOR 2-0.
- **Jun-17:** POR-COD 2-0, ENG-CRO 1-0, GHA-PAN 1-0², UZB-COL 0-1².

¹ = entered currently deviates → revert above. ² = EV≠modal flip-watch.

## Guards (8 newly-logged Jun-16/17 fixtures + replays)
- x.5 totals guard: **clean ×8** (all half-lines). L17 favorite-inversion: **fired 0×**. Determinism: byte-identical replay on the same snapshot. backfill idempotent (re-run filled 0). decisions.csv: 24 rows, 24 unique ids, no dup/orphan (F30).

## EV-vs-modal divergence (the only fresh-odds flip candidates, F13)
USA-PAR (played), NED-JPN, CIV-ECU, ARG-ALG (1-0 vs modal 2-0), GHA-PAN (1-0 vs 1-1), UZB-COL (0-1 vs 0-2).

## Caveat (n=8)
override −4 and every Brier/points diff are **NOISE** at n=8 (~280 matches for a ±0.05 pts/match paired-SE). Instrument + compare everything; act on NOTHING result-driven (I3 — no result→model path, ever).

## Refresh schedule (10-min pre-KO deadlines, UTC)
- **Jun-15 ~14:00Z:** ESP-CPV (15:50), BEL-EGY (18:50), KSA-URU (21:50), IRN-NZL (Tue 00:50Z).
- **Jun-16 ~14:00Z:** FRA-SEN (18:50), IRQ-NOR (21:50), ARG-ALG (Wed 00:50Z), AUT-JOR (03:50Z).
- **Jun-17 ~14:00Z:** POR-COD (16:50), ENG-CRO (19:50), GHA-PAN (22:50), UZB-COL (Thu 01:50Z).
