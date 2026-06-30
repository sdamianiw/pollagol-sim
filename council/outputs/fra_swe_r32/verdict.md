# France–Sweden R32 — Scoreline Faceoff Council (2-0 vs 3-0 vs 3-1)

**Fixture:** France vs Sweden · R32 · KO 2026-06-30T21:00Z (lock ~20:50Z) · fixture_id `0b5491529142c9bcc3f88bf45ccb0a7b`
**Snapshot:** `md4_2026-06-30T19-16-45Z.json` (fetched 19:16Z; ~25 min old at council time; line stable)
**Mandate:** user-requested deep faceoff (NED-MAR pattern) — does the EV-argmax 2-0 hold vs 3-0 / 3-1
under the rising-totals signal? **Advisory; the frozen engine adjudicates E[pts] (L44/L50).** I-HITL.

## VERDICT — HOLD **2-0** (buy 3-0 = NO; buy 3-1 = NO while leading)
2-0 is the E[pts]-argmax AND the modal AND France's historical KO signature AND differentiated from the
likely 3-0 chalk. **3-0 is E[pts]-DOMINATED** — never the argmax at any total, and the weakest of the
three on every historical metric. 3-1 is the only legitimate alternative (the "more goals than market"
pick) but requires overriding the market's 3.5 total upward by ~+0.7 — a discretionary tilt declined
while rank-1 (L50/L32; the market carries the signal).

## Deterministic backbone (FAITHFUL — reproduce gate max|sweep−engine|=0.000000)
Live de-vig: **France 0.7699 / D 0.1514 / Sweden 0.0787**; line 3.5; **mu_eff 3.549**; context neutral (var 1.06).

| candidate | E[pts] @ live | P(score) | vs 2-0 |
|---|---|---|---|
| **2-0** | **3.5077** | 0.1076 | argmax |
| 3-0 | 3.4022 | 0.0964 | −0.1055 |
| 3-1 | 3.2970 | 0.0765 | −0.2107 |

**Rising-totals sweep (1X2 + variance fixed; the "over-goals rising" stress test):**
- 2-0 stays the argmax through **mu_eff ≈ 4.0** (line ~4.0). It only loses the argmax at **mu ≈ 4.25**, and
  the winner there is **3-1, NOT 3-0**.
- **3-0 crossover = mu 4.75** (line ~4.75, +1.2 over live); **3-1 crossover = mu 4.25** (+0.7 over live).
  Because 3-1 overtakes at a LOWER mu than 3-0, **3-0 is DOMINATED — never optimal at any goal level.**
- To dislodge 2-0, the market total would have to leap from 3.5 to ~4.0+ — the form lens confirms the line
  is stably 3.5 (Over 3.5 ≈ +100), so there is no live signal for that move.

## Panel (4 isolated lenses → advisory; no lens computes E[pts])
- **Form/market** (med): total stable 3.5 (no 24h move, ≥2 books); France 3.33 GPG, **zero rotation**
  (Mbappé/Dembélé starting); Sweden 2.33 conceded/g + **CB Isak Hien out (tournament)**. Lean **3+**;
  experts project **3-1**. Sources: CBS/ESPN/Rotowire/Goal/SportsMole/AlJazeera (2026-06-30).
- **Historian** (base rates): of the three, **2-0 most frequent all-time (47% vs 3-1 29% vs 3-0 24%)**;
  recent WC-R16 decisive: 2-0 & 3-1 tie (3 each), **3-0 only once**; **France's KO signature = the 2-0
  clean sheet** (Uruguay '18, Morocco '22, Nigeria '14 — not a blowout side in KO). **3-0 weakest on every
  metric.** Lean **2-0**, 3-1 close 2nd. Sources: thissportlife/Wikipedia-WC-KO/olympics (2026-06-30).
- **Chalk/ownership/leader-doctrine** (high): field-modal PRIOR = **3-0 then 3-1** (amateur pools overweight
  "statement" wins); **differentiation HURTS while leading** + per-match ownership is HIDDEN (§7d) →
  **CHALK_TRUMP = NO.** Picking 2-0 *because* the crowd is on 3-0 is forbidden; 2-0 differentiating from
  the chalk is a free byproduct of the EV pick, not the motive.
- **Adversarial/premortem**: best case for 3-0 = "shortening price / stale snapshot, argmax may have
  silently moved"; verdict overturn-to-3-0. **REFUTED:** snapshot fresh (19:16Z), line stable 3.5 (form
  lens, ≥2 books), and **3-0 is dominated by 3-1 even under the adversarial's own "more goals" premise** —
  so the adversarial's evidence, taken at face value, argues for 3-1, never 3-0.

## Synthesis
Three independent methods converge: **the engine (3-0 never argmax), the historian (3-0 weakest on every
metric), and the chalk lens (3-0 is the field-modal) — i.e. the crowd's favorite is the statistically worst
of the three.** The genuine debate is only 2-0 (trust the market's 3.5 total) vs 3-1 (override it upward).
Doctrine resolves it: the market carries the signal, the leader takes the EV-argmax, and the form lens's
"lean 3+" is already priced into the 3.5 line (Over 3.5 ≈ even money) — it is not new information.
**Bias check ("would I pick this from 3rd place?"):** even trailing, the differentiation pick would be 3-1,
never 3-0; we lead, so we take the argmax 2-0. No reconcile loop needed (no lens contests the engine on 3-0;
the 3-1 residual is a market-override declined while leading).

## Success criteria
- **SC1 backbone:** PASS (reproduce 0.000000; 2-0 argmax; 3-0 dominated; crossovers 4.25/4.75 ≫ live 3.549).
- **SC2 panel:** PASS (4 lenses, grounded + cited).
- **SC3 chalk axis:** PASS (differentiation -EV while leading + hidden ownership → no override; 3-0 = chalk-trap).
- **SC4 decision:** PASS (2-0, engine-adjudicated, robustness band, bias check).

## Recommendation (I-HITL — Sebas enters; nothing locked)
**Enter / keep France-Sweden = 2-0** before the 20:50Z lock. If you have a strong personal read that the game
goes 4+ goals (beyond the market's 3.5), the *only* defensible alternative is **3-1** (never 3-0) — but that
is a market-override tilt and, as leader, EV says hold 2-0.
