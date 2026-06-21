# Matchday Cadence Summary — 2026-06-17

**Run:** Ronda-1 finish + MD2 seed · span **Tue 16-Jun → Fri 19-Jun (German/CEST = UTC+2)** · ONE API call.  
**Mode:** DRY-RUN / recommend-only. CC never enters or locks — Sebas types into pollaya (I-HITL).  
**Engine (FROZEN):** M1 ingest → M2 de-vig → x.5 guard → M3 Dixon-Coles (μ_eff from totals price) → M5 neutral → M4 argmax E[pts]. `rho_fit` OFF (ρ=−0.05); seed-deterministic; snapshot-reproducible (same snapshot ⇒ byte-identical).  
**Objective:** maximize **E[competition points]** under the locked rubric (exact=3, outcome=3, team-goals 1/team max 2, GD=1). **Pure EV-argmax — no draw-lean (I-NOTILT); P_draw is context only.**  
**Source:** The Odds API · snapshot `data/snapshots/md1_2026-06-16T15-59-46Z.json` (fetched 2026-06-16T15:59:45Z; quota 481→479, ~2cr) · de-vig proportional · single-book h2h+x.5-totals (RB3-clean).  
**Generated:** 2026-06-17T16:40:30Z (deterministic from the snapshot; engine git-clean on the 6 frozen paths).

## Standing context (post-MD4/MD5 — info only, does NOT alter picks)
Cumulative n=16: **us = 28 pts**, override **+0** (us_model = us_entered = 28 = observed pollaya board). **[Override tally SUPERSEDED -> canonical: tasks/override_ledger.md.]** **Rank 21/27**, leader 44, podium cut 42, **gap to podium −14**. Field-differentiation is the gated post-MD3 lever; this slate stays chalk-disciplined EV-argmax.

## SYSTEMATIC VERDICT — per-fixture EV-argmax recommendation (13 fixtures)

| # | Fixture | Slate | KO (UTC) | **EV-pick** | E[pts] | P(1/X/2) | P_draw | Coin | vs modal | Conf |
|--:|---|:--:|---|:--:|--:|:--:|--:|:--:|:--:|:--:|
| 1 | **FRA-SEN** France–Senegal | R1·I | 2026-06-16T19:00:00Z | **1-0** | 3.23 | 0.66/0.21/0.13 | 0.21 | – | ⚑ 2-0 | HIGH |
| 2 | **IRQ-NOR** Iraq–Norway | R1·I | 2026-06-16T22:00:00Z | **0-2** | 3.71 | 0.07/0.13/0.80 | 0.13 | – | = | HIGH |
| 3 | **ARG-ALG** Argentina–Algeria | R1·J | 2026-06-17T01:00:00Z | **1-0** | 3.43 | 0.68/0.21/0.11 | 0.21 | – | ⚑ 2-0 | HIGH |
| 4 | **AUT-JOR** Austria–Jordan | R1·J | 2026-06-17T04:00:00Z | **2-0** | 3.51 | 0.72/0.18/0.10 | 0.18 | – | = | HIGH |
| 5 | **POR-COD** Portugal–DR Congo | R1·K | 2026-06-17T17:00:00Z | **2-0** | 3.65 | 0.75/0.17/0.08 | 0.17 | – | = | HIGH |
| 6 | **ENG-CRO** England–Croatia | R1·L | 2026-06-17T20:00:00Z | **1-0** | 3.02 | 0.55/0.26/0.19 | 0.26 | – | = | MED |
| 7 | **GHA-PAN** Ghana–Panama | R1·L | 2026-06-17T23:00:00Z | **1-0** | 2.52 | 0.43/0.28/0.28 | 0.28 | – | ⚑ 1-1 | LOW |
| 8 | **UZB-COL** Uzbekistan–Colombia | R1·K | 2026-06-18T02:00:00Z | **0-1** | 3.47 | 0.10/0.20/0.70 | 0.20 | – | ⚑ 0-2 | HIGH |
| 9 | **CZE-RSA** `[B]` Czech Republic–South Africa | MD2 | 2026-06-18T16:00:00Z | **1-0** | 3.04 | 0.56/0.25/0.19 | 0.25 | – | = | MED |
| 10 | **SUI-BIH** `[B]` Switzerland–Bosnia & Herzegovina | MD2 | 2026-06-18T19:00:00Z | **1-0** | 3.26 | 0.62/0.23/0.15 | 0.23 | – | = | MED |
| 11 | **CAN-QAT** `[B]` Canada–Qatar | MD2 | 2026-06-18T22:00:00Z | **2-0** | 3.82 | 0.78/0.15/0.07 | 0.15 | – | = | HIGH |
| 12 | **MEX-KOR** `[B]` Mexico–South Korea | MD2 | 2026-06-19T01:00:00Z | **1-0** | 2.76 | 0.47/0.30/0.23 | 0.30 | – | ⚑ 1-1 | LOW |
| 13 | **USA-AUS** `[B]` USA–Australia | MD2 | 2026-06-19T19:00:00Z | **1-0** | 3.11 | 0.60/0.22/0.18 | 0.22 | – | = | MED |

*Legend:* P(1/X/2) = de-vig market outcome probs. **Coin**flip = |P_top − P_draw| < 0.08. **Conf:** HIGH (fav ≥ 0.62) / MED (0.50–0.62) / LOW (< 0.50 or coinflip). **⚑** = EV-pick diverges from the modal (most-likely) score. **`[B]`** = new MD2 baseline (pending entry); the 8 Ronda-1 are fresh-odds and showed **0 flips** vs the logged baseline.

## FINAL RECOMMENDATION (deterministic)
**Enter the EV-pick column as-is for all 13** — each maximizes E[pts] on the current de-vig odds. Diagnostics: **0 coinflips · 0 favorite-inversions · all x.5 guards clean · ρ frozen −0.05**.

- **HIGH (enter directly):** FRA-SEN 1-0, IRQ-NOR 0-2, ARG-ALG 1-0, AUT-JOR 2-0, POR-COD 2-0, UZB-COL 0-1, CAN-QAT 2-0
- **MED:** ENG-CRO 1-0, CZE-RSA 1-0, SUI-BIH 1-0, USA-AUS 1-0
- **LOW / near-even (watch; recommendation stays EV-argmax, NO draw-lean):** GHA-PAN 1-0, MEX-KOR 1-0
- **Flip-watch (EV ≠ modal):** FRA-SEN, ARG-ALG, GHA-PAN, UZB-COL, MEX-KOR
- Re-check fresh odds ~10 min pre-KO for any not yet kicked off; refresh K/L + MD2 before each deadline.

## Excluded
- **SCO-MAR** (Scotland–Morocco) KO 2026-06-19T22:00Z = **00:00 CEST Saturday** → outside the Friday-German window. Present in the snapshot; add as a 6th MD2 baseline on request.

## HITL — nothing entered or locked by CC
Record post-match (per fixture):  
```
python -m src.decision_score record <fid> <H-A> --entered-pick <typed>
```
Fixture ids:

| Fixture | fixture_id |
|---|---|
| FRA-SEN | `73a4fcd14cc9766b9b9bfd50b8ca153a` |
| IRQ-NOR | `4d4f2b9b78182b557d4fbf8dcf4f4af2` |
| ARG-ALG | `f31b2ee9e1cc6f7e641467f8237eaa21` |
| AUT-JOR | `25161cf6cf0cd9be17ae2e7e224a1f45` |
| POR-COD | `6cc871c121a1869b4612d3fb22fa9d55` |
| ENG-CRO | `689096c8cd7e2753b9fec95321943c5d` |
| GHA-PAN | `87afdb85c977b451e1c00f5e3e632601` |
| UZB-COL | `22083e7a8e5362c711bc05c1e1319a1f` |
| CZE-RSA | `66ebb9e3f949caded535d97ce686ca09` |
| SUI-BIH | `289bc2e9f5adad8ae4d9a75a7c5461ad` |
| CAN-QAT | `fa9502285b257b03e62968d50d9229fc` |
| MEX-KOR | `0f2aeae6ac8e77223848d23a4ca86b0d` |
| USA-AUS | `065b3573e875f8d23803357f73e5b99e` |

> Canonical picks live in `predictions/decisions.csv` (`pick` column). This file is the formatted, deterministic verdict for the 16-Jun cadence run; after these play and are recorded, **Ronda-1 = 24/24** and MD2 is seeded through Fri 19-Jun (German).
