# NED–MAR R32 Deep Council — VERDICT (2026-06-29)

> **DRAFT / GATED — advisory triangulation, NOT a lock. The frozen engine + `ko_adjust` adjudicate; Sebas enters.**

**Fixture:** Netherlands (home) vs Morocco (away) · R32 · KO 2026-06-30 01:00Z · fixture_id `5a34afe2de99513ba48360b983cfe80c`
**Snapshot:** `md4_2026-06-29T19-53-06Z.json` (quota 433). 90′ de-vig (frozen engine, neutral, ρ=−0.05): **NL 0.412 / Draw 0.311 / Morocco 0.276**. NL decimal drifted 2.2→2.4 (confirmed mild sharp money off NL).
**Scoring rule:** `KO_SCORING = FULL120` — 120′ scoreline scored, **penalties EXCLUDED** ⇒ still-level-after-120′ = scored DRAW.

## DECISION — enter **Netherlands `1-0`**. Buy the draw? **NO.**
The EV-argmax is **1-0 at every plausible penalty rate** (f), and the draw is dominated **under every scoring rule**.

### Deterministic backbone — `ko_adjust` FULL120 across the f-band (the adjudicator)
| f (P pens \| level@90′) | P(NL win) | P(scored-draw) | P(MOR win) | argmax | best decisive | best draw | **dec − draw** |
|---|---|---|---|---|---|---|---|
| 0.30 | 0.523 | 0.083 | 0.394 | 1-0 | 1-0 (2.840) | 1-1 (1.090) | **+1.750** |
| 0.50 | 0.491 | 0.138 | 0.371 | 1-0 | 1-0 (2.746) | 1-1 (1.413) | **+1.334** |
| 0.70 (historian central) | 0.460 | 0.193 | 0.347 | 1-0 | 1-0 (2.631) | 1-1 (1.727) | **+0.905** |
| 0.83 (historian hi) | 0.440 | 0.229 | 0.331 | 1-0 | 1-0 (2.549) | 1-1 (1.928) | **+0.621** |
| 1.00 (= REG90, draw-maximal bound) | — | 0.311 | — | 1-0 | 1-0 (2.436) | 1-1 (2.189) | **+0.247** |

**The draw never wins.** The gap is *smallest* at f=1.0 (REG90, the most draw-favorable case) at +0.247, and only *widens* as extra time resolves draws. The FULL120 rule makes the draw strictly **worse**, never better — a 1-1 at 90′ won in ET becomes a 2-1 (not a scored draw), so the 1-1 pick craters while 0-0→1-0 ET resolution reinforces 1-0.

### Adversarial challenge (re-derived vs the engine, L44)
Strongest case against 1-0 = **2-1** (both teams score, NL never kept a clean sheet, ET-bump). FULL120 *does* narrow it: 1-0 vs 2-1 goes from +0.133 (90′) to **+0.066** (FULL120 @ f=0.50) — 2-1 is the genuine #2. But **1-0 still wins on E[pts] (2.746 vs 2.680) AND raw probability (0.124 vs 0.111)**. Engine refutes the "2-1 is better-calibrated" narrative. The clean-sheet fragility is already priced into the full distribution.

### Panel (5 isolated lenses → unanimous NL_win; contested = FALSE)
- **Market** (NL 0.420/0.295/0.285): de-vig confirmed across FanDuel/DK/BetMGM/Betfair/Opta; NL drift = mild sharp money.
- **Form/tactical** (0.40/0.32/0.28): ET-prone **HIGH** (Opta 29% ET); Morocco elite shot-restriction (0.09 xG/shot); NL 0 clean sheets, conceded every group game; NL absences (Timber, de Ligt, Simons).
- **Historian** (0.468/0.218/0.313): **f≈0.70** [lo 0.50 / hi 0.83] from WC KO 1982–2022 (35 pens / ~50 ET games); P(pens this game)≈0.22 ≈ all-time R16 base rate 18%; BTTS **75%** (Qatar 2022 R16 = 6/8, **confirmed**); NL 3/3 recent ET games → pens.
- **Contrarian/ownership** (0.49/0.17/0.34): per-match picks HIDDEN (prior only); RANK-1 +4/+9/+14 ⇒ **chalk-protect**, no deviation — our differentiation already lives in the locked-50 (Kane/Bruno), don't add per-match variance.
- **Adversarial** (0.46/0.17/0.37): Morocco genuinely live; biggest 1-0 failure mode = clean-sheet assumption; bias check = leader should MAXIMIZE E[pts], and 1-0 does.

### Decision rule (pre-registered) — applied
Enter FULL120-EV-argmax (**1-0**). Draw recommended **only if** `best_draw_ev ≥ best_decisive_ev − ε` across the f-band AND ≥2 lenses + historian corroborate ⇒ **condition FAILS** (gap +0.25…+1.75, never within ε). **KO-DRAW-EXCEPTION NOT triggered.** Bias check "would I pick 1-0 from 3rd place?" → **yes** (it's the EV-argmax independent of standings).

**Confidence:** HIGH that it is **not a draw / NL_win**. Scoreline **1-0** is the EV-argmax; **2-1** is the close #2 under FULL120 (the only honest alternative). Morocco win (~0.33–0.37) is live but second — 1-0 maximizes E[pts] regardless.

### Live urgency (HITL)
Lineups not out at T-5h; a material NL/Morocco absence at T-1h could move it. Sebas enters before sleeping (cannot reach T-1h = 03:00 German); 1-0 is robust to the f-uncertainty, so the recommendation is stable.
