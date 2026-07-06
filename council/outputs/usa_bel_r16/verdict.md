# COUNCIL VERDICT — USA vs Belgium (R16, 2026-07-07 00:00Z) — CONDITIONAL, T-1h ADJUDICATION

> I-HITL: RECOMMENDATION only. Sebas enters; nothing locked. Entry deadline **23:50Z tonight**.
> Council ADVISORY (L44); the FROZEN engine adjudicates E[pts]. Snapshot `md4_2026-07-06T17-33-02Z.json`
> (17:33Z = T-6.4h). Trigger: **FIRE** (weak-fav 0.384<0.55 AND argmax 2-1 ≠ modal 1-1). This board is
> the Jul-5 DEFER (baseline argmax 1-2 → Jul-5 2-1); Sebas moved his entry 1-1 → 2-1 accordingly.

## DETERMINISTIC BACKBONE (frozen engine on the 17:33Z odds)
- De-vig 1X2: **USA 38.4% / Draw 27.9% / Belgium 33.7%** — USA a nose ahead. Totals 2.5, p_over 0.565,
  mu_eff 2.950 (open game).
- **FULL120 argmax = 2-1 (E 2.449)**; 1-2 = 2.329 (gap +0.120); modal 1-1 dead (1.399, −1.05).
  f-band: 2-1 at every cageyness. Jul-5 flip CONFIRMED on these odds → board's 2-1 == argmax at 17:33Z.

## DRIFT HARNESS (scratchpad `drift_usa_bel.py`, CONTROL==live PASS, B4 PASS) — **CONDITIONAL**
- **Flip boundary: argmax 2-1 → 1-2 when USA's devig lead over Belgium shrinks below ~3pp**
  (at USA 0.364/BEL 0.357 the argmax is already 1-2 by −0.053). Live lead 4.7pp — INSIDE the empirical
  1pp/5h drift band but with almost no margin.
- Draw ±2pp: 2-1 holds (tightest +0.023 at draw 0.299). Totals: 2-1 holds to p_over 0.50; migrates to
  1-0 (still USA) only at ≤0.45. **The ONLY live axis is the USA↔BEL favorite axis.**

## PANEL (2 lenses + harness; both agents' full texts in session log)
- **Historian/form:** Belgium 6 straight H2H wins over USA incl. 2014 WC R16 (2-1 AET) and a 5-2
  friendly Mar-2026 — but form points the other way: Belgium's group was poor (1-1 EGY, 0-0 IRN, 5-1 NZL),
  their R32 needed a 0-2→3-2 AET miracle vs Senegal **five days ago (120′ fatigue, same XI all
  tournament, no rotation buffer)**; USA topped their group GF 8, beat Bosnia 2-0 playing 35′ a man down.
  **Root cause of the Jul-4→Jul-5 flip identified: the Balogun red-card overturn** (FIFA suspended the
  ban Jul-4/5; he's available, 3 WC goals) — and that surge is now RETRACING: FanDuel Jul-6 devigs to
  **USA ~35.7 / draw ~27.8 / BEL ~36.5** (−2.7pp USA vs our snapshot; 55% of tickets on Belgium).
- **Adversarial:** FM1 co-host soft-money contamination of US-facing books = real, unquantified (our
  snapshot IS a US-book consensus) → cross-check a sharp book pre-lock; FM2 the direction call IS the
  pick — scoreline width within a USA win is secondary, REFUTED as a switch reason; FM3 revert-to-1-1
  REFUTED (−1.05 EV unconditional, differentiation upside needs hidden-pick clustering we can't see and
  we LEAD — maximize score, not differential); FM5 recency/patriot narrative can't leak into the engine
  (market-only input) but can inflate the input itself.

## ADJUDICATION — CONDITIONAL, resolved by the T-1h refetch (engine, not narrative)
The 17:33Z engine says 2-1. The freshest single-book read says the board has drifted PAST the flip
boundary (BEL fractionally ahead → argmax would be 1-2). One book's devig is not a rule-confirmed
EV-UPDATE; the Jul-5 DEFER protocol already prescribes the answer:
**→ RE-FETCH at ~23:00Z (T-1h), run `ko` on the fresh snapshot, and enter the FULL120 argmax it prints.**
Quota 486 = no constraint. This is the NOR-FRA/L44 pattern: pick changes only on a fresh engine argmax.

## DECISION TREE FOR THE 23:00Z RECHECK (fixed now, before the data)
1. Fresh devig USA lead ≥ +3pp → **KEEP 2-1** (harness says argmax robust).
2. Fresh devig USA lead < +3pp or Belgium ahead → **ENTER 1-2** (engine argmax will flip; register as
   EV-UPDATE, not tilt — L35 re-derivation from the fresh snapshot is the classifier).
3. Any case: **NEVER 1-1** (dead by ≥1.0 EV at every point of the drift band; the original instinct
   stays refuted).
4. If the fetch fails: fall back to the app-visible rule — if Belgium's displayed odds are equal to or
   shorter than USA's at entry time, enter 1-2; if USA clearly shorter (≥0.15 decimal / ~15 US cents),
   keep 2-1.

## VERDICT
**CONDITIONAL: hold 2-1 on the board now; final entry = fresh FULL120 argmax at the 23:00Z T-1h
recheck** (expected: genuinely close; the Balogun retrace determines it). Deadline 23:50Z.

---

## FINAL COUNCIL ADDENDUM — full-drill adjudication at T-2.5h (2026-07-06 ~21:30Z)

> Sebas-mandated deep council on the T-1h FLIP (2-1 -> 1-2). Pre-registered success criteria SC1-SC5
> fixed BEFORE the lens outputs. Deterministic layer this session: symmetry decomposition
> (`usabel_symmetry.py`), H-pin pattern scan (12/12 recorded boards), drift trajectory, P(exact) table.

### Deterministic findings (all reproduced, zero-invasive)
1. **21:06Z market: PERFECTLY even** (devig USA .357895 / BEL .357895, six decimals).
2. **The FULL120 gap 1-2 minus 2-1 (+0.130) is 100% engine-internal**: with rho frozen the model holds
   24.8% draw vs the market's 28.4%; the residual spills to the AWAY column (matrix-implied BEL 39.0 /
   USA 36.2; symmetrized matrix -> gap exactly 0.0000). NOT a tonight-bug: **H-pinned 12/12** recorded
   boards (engine always matches home devig exactly; draw-vs-model residual flows to away, 9/12) —
   the same pre-registered character that produced all 92 rows, rank 1/27, and the MEX-ING 0-1 hit.
   It also EXPLAINS the drift-harness flip boundary (+3pp == the internal away-offset).
3. **Trajectory** (5 snapshots Jul-4 -> Jul-6): BEL +2.6pp -> BEL +1.6 -> USA +3.1 (Balogun overturn)
   -> USA +4.7 (peak) -> 0.0 (full retrace). Totals monotonic UP (p_over .541 -> .583, mu 2.84 -> 3.03).
4. **P(exact@120')**: 1-2 = .1028 > 2-1 = .0986 (same internal tilt; symmetrized they tie).
5. **Coolbet 21:20Z (Sebas's own NON-US book, photo): USA 2.60 / 3.50 / 2.85 -> devig USA +3.3pp** —
   contradicts the patriot-inflation hypothesis (non-US book prices USA AHEAD); sits exactly AT the
   crossover -> even on Coolbet's prices 1-2 vs 2-1 is sub-noise (~+0.01 for 2-1, < 0.030 floor).

### Panel split and resolution (SC1-SC5)
- **Doctrine lens: 1-2 MANDATORY.** The frozen engine is the pre-registered decision procedure;
  symmetrizing the matrix at T-2.5h is itself the unfrozen intervention. Under co-argmax framing every
  tie-breaker (P(exact) under the frozen engine, ledger none-vs-TILT, zero switching cost, bias guard)
  independently selects 1-2. 2-1 from-3rd-place test FAILS (coin-flip differentiation = tilt).
- **Adversarial lens: STAY 2-1** — FM1: entering 1-2 launders a calibration artifact into a direction
  call; coin goes to the entered pick. Its externals: patriot-money = soft BEL shadow; fatigue/H2H
  priced; lineup EV ~0.03-0.05 pts (De Bruyne = the one real unknown); FM5 0-1/1-0 REFUTED (mu 3.03).
- **Resolution (per pre-registered SC):** SC1 — the market is directionless and NO sourced external
  lean survives scrutiny: the patriot-money shadow (the adversarial's strongest external, its basis for
  a "true" BEL lean) is CONTRADICTED by the Coolbet observation; fatigue + H2H were available to the
  market that prices even; the pre-spike BEL equilibrium is superseded by the live price (martingale).
  SC2 therefore applies: **absent sourced external evidence, the pre-registered procedure's argmax
  stands — 1-2.** The adversarial's remaining case reduces to churn-avoidance (which it itself called
  operationally addressable) plus a NEW ledger class ("COIN-FLIP-NEUTRAL") that does not exist in the
  standing taxonomy — inventing it at T-2.5h is exactly the unfrozen intervention FM1 warns against,
  applied to the other side. Symmetric interventions cancel; process remains; process says 1-2.
- Both lenses AGREE on: never 1-1 (SC4); 0-1/1-0 refuted; the EV stakes of the direction call are tiny
  (symmetrized gap 0.0000; regret bounds ~0.01-0.05 pts) — this is a governance decision, not an EV one.

### VERDICT — ENTER **Belgium 1-2** before 23:50Z (change from 2-1)
Classification when recorded: `pick = 1-2` (L57, council fired) and entered 1-2 -> **`none`** (clean).
Sleep protocol: no rule requires staying awake (drift re-flip P ~0.4% normal / ~19% under 3-sigma news;
regret ~0.01). OPTIONAL 23:30Z alarm per adversarial FM4: the single name that shifts direction is
**De Bruyne OUT (-> USA lean; would reopen 2-1)**; Pulisic OUT reinforces 1-2. If asleep: 1-2 stands,
tail regret ~0.03-0.05 pts accepted and documented.

### SHARP-MARKET LENS (landed post-adjudication; confirms + sharpens, no verdict change)
- **Sharp reference = perfect pick'em:** VSiN USA 36.0/BEL 36.0 devig; **Asian handicap = level ball (0)**
  — the cleanest direction signal there is. bet365 UK to-advance **exactly 50/50**.
- **Patriot premium quantified:** FanDuel USA +6.1pp vs VSiN 0pp (≈3pp USA premium on FD, 1.5pp on DK);
  our Odds-API consensus (0.0pp) and Coolbet (+3.3pp) sit between retail and sharp. Confirms the premium
  EXISTS on retail books but the sharp read is EVEN — not Belgium-ahead: SC1 resolution unchanged.
- **External scoreline models lean 1-2:** OddsShark computer projects BEL 1.8 vs USA 1.4 goals; decisive
  correct-score ranking **1-2 > 0-1 > 2-1 > 1-0** (Dimers/OddsShark). Independent of our engine, the
  external Poisson layer puts 1-2 as the TOP decisive scoreline — the engine's argmax and the outside
  models agree even though they disagree with the retail moneyline. Strengthens 1-2.
- **Lineups ~21:25Z: both XIs fully fit** (De Bruyne/Doku/Lukaku/Trossard confirmed; Balogun eligible;
  only Roldan doubtful, non-starter). No reopen trigger live; the 23:00Z lineup drop is residual tail only.
- Drift driver confirmed: 55% of tickets Belgium + Balogun-bump mean reversion + model xG leans.

**FINAL (unchanged): ENTER Belgium 1-2 before 23:50Z.** Direction = sharp pick'em; scoreline = engine
argmax + external-model top decisive + P(exact) + ledger `none` all select 1-2; only retail patriot
premium argues 2-1 and it is the one input class every lens agreed to distrust.
