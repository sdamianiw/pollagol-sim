# COUNCIL VERDICT — Mexico vs England (R16, Estadio Azteca, 2026-07-06 00:00Z)

> I-HITL: this is a RECOMMENDATION. Sebas enters; nothing is locked. Entry deadline **2026-07-05 23:50Z**.
> Council is ADVISORY (L44): the FROZEN deterministic engine adjudicates E[pts]; no lens computes EV.
> Snapshot `data/snapshots/md4_2026-07-05T18-21-51Z.json` (fetched 18:21Z). Branch `rho-fit`, engine FROZEN.
> Trigger: **FIRE** (weak-fav 0.382 < 0.55 AND argmax 0-1 ≠ modal 1-1) **+ MANDATORY by Sebas** (deep panel:
> 3 historians + 4 lenses + metacognitive synthesis). **NO-REFETCH constraint**: decision final on these odds.

## MANDATE
Sebas has PRE-ENTERED **1-1** (deviating from the engine's 0-1) and asked the deep question: *"if the game
ends level at 90', is an ET winner or penalties historically more likely — and does that make 1-1 smart?"*
Candidates: **0-1 · 1-1 · 1-0 · 0-0 · 1-2 · 2-1**.

## DETERMINISTIC BACKBONE (frozen engine on fresh odds; reproduce = exact)
- De-vig 1X2: **Mexico 30.9% / Draw 30.9% / England 38.2%** — the tightest board of the R16.
- Totals: line 2.5, p_over 0.398, **mu_eff 2.279** (LOW-scoring projection).
- 90′ argmax **0-1** (2.438) vs modal **1-1** (2.254) — close at 90′. But the pool scores **FULL120**:
  **PICK = 0-1 (E 2.676)**; **1-1 = 1.671 (gap +1.00)**; p_draw_90 0.287 → p_draw_scored(120) 0.183 (f_model 0.637).
- f-band: argmax **0-1 at EVERY cageyness**; dec−draw gap +0.58 (max-cagey) → +1.25 (REG90).

### Drift-sensitivity (no-refetch protocol; harness: synthetic h2h at exact target devig, totals untouched)
| scenario | devig H/D/A | FULL120 PICK | best_draw 1-1 |
|---|---|---|---|
| CONTROL | .309/.309/.382 | **0-1** (2.676) | 1.671 |
| ENG +2pp | .299/.299/.401 | **0-1** (2.725) | 1.668 |
| ENG +4pp | .289/.289/.422 | **0-1** (2.778) | 1.663 |
| ENG −2pp | .319/.319/.362 | **0-1** (2.626) | 1.674 |
| ENG −4pp | .329/.329/.342 | **0-1** (2.576) | 1.676 |
| DRAW +2pp | .300/.329/.371 | **0-1** (2.719) | 1.668 |
| DRAW −2pp | .319/.289/.392 | **0-1** (2.628) | 1.674 |

**→ STABLE.** 0-1 is argmax in all 7 runs; 1-1 trails by ≥ +0.90 everywhere. A Mexico-win flip would need
England below ~34% — outside any plausible 5h drift (empirical T-7h→T-1h drift ≤ 1pp).

## HISTORIAN PANEL (sourced counts, accessed 2026-07-05)
**Historian-A — 90′-draw base rate:** 1986→2022, **55/160 WC KO games level at 90′ = 34.4% ±3pp**
(Wikipedia PSO list + per-tournament KO pages; range 25–56% by tournament). Market draw 30.9% =
**typical-to-slightly-conservative — NOT underpriced**. Close-matchup stratum: unverified (no citable study).
**Historian-B — given level at 90′ (N=49):** **69% went to PENALTIES vs 31% decided in ET** (modern era 32%;
2022: 5/5 pens). Of the 34 pens games, the 120′ score was **1-1 in 50%**, 0-0 in 35%, 2-2+ in 15%.
**Net: P(exactly 1-1 at 120′ | level at 90′) ≈ 35% → unconditional P(1-1 final) ≈ 11%.**
*(Independently validates the engine: f_model 0.637 ≈ the historical 69% pens survival.)*
**Historian-C — specifics:** Mexico 4W/0GA (R32 2-0 Ecuador at Azteca); England shaky (0-0 Ghana, 2-1 DRC);
England OUT: James, Quansah; **Rice played R32 in "terrible pain"**; Azteca = 2 losses in 89 competitive
games, 2,240m, England unacclimatized (Kansas City base, sea-level groups), **England never won on Mexican
soil (0W-1D-2L)**; 1966 the only competitive H2H (ENG 2-0). Lean Mexico/draw — but see synthesis audit.

## LENSES
**Form/tactical (MED → leans Mexico 1-0):** elite Aguirre block (0 GA), altitude ~10-15% aerobic hit,
England reputation-priced; ranks 1-0 > 0-1 > 1-1 > 0-0. Claims true Mexico ~40-42% (8-11pp vs market).
**Chalk/leader-doctrine (HIGH → REVERT to 0-1):** 1-1 = textbook tilt (L50). On the modal England-win the
1-1 entry collects **1 pt vs a 0-1 holder's 9 = −8 relative swing** from 1st place, chasing an ~11% scenario.
1-1 collects fully ONLY at pens-with-1-1; partials: 1 pt on any 0-1/1-0/2-1/1-2; 4 pts on 0-0/2-2 pens.
**Adversarial/premortem (MED → 0-1 survives):** 1-1 steelman "survives as atmosphere narrative, **dies on
the math**" (~11%). Real attack = Mexico 1-0 (public money 50% MEX / 38% ENG) — but insufficient vs +1.00 gap.
Low-total attack FAILS (altitude fatigue → late decisive goals → favors 0-1). Premortem: lineups ~22:45Z.
**Market (PARTIAL agreement, fair basis):** snapshot within 1-2pp of FanDuel/bet365; England opened +125
(42.4% w/vig) → drifted +140/150 on public Mexico money; draw +210 = joint-tightest R16 board; totals
p_over ≈ 0.406 ≈ engine 0.398. **Snapshot = fair no-refetch basis.**

## METACOGNITIVE SYNTHESIS (recursive audit)
- **Historian-C drift claim REFUTED**: compared vig-inclusive 40.8% to de-vigged 38.2% (apples-oranges);
  de-vigged current ≈ 38-39% = unchanged. England drifted OUT, not firmer; "altitude unpriced" = narrative.
- **Form-lens 8-11pp Mexico edge = NOT VERIFIED** (context narrative, no second model/sharp signal; public
  tailing ≈ popularity bias). Strongest surviving counter-argument, still short of the L50 threshold.
- **Historian-B 2022 sub-sample (0/5 ET)** cannot override the 49-game base rate; both converge ~69% pens.
- **Self-critique:** snapshot partially prices Rice/James/Quansah; "Mexico 1-0 is genuinely near coin-flip —
  but close ≠ model-grounded edge above threshold. The doctrine threshold exists precisely for this."
- **Aggregate: NO rule-confirmed, model-grounded EV-UPDATE away from 0-1 exists in the panel's evidence.**

## VERDICT
**ENTER: England 0-1 — REVERT the pre-entered 1-1 before 23:50Z.** Label: **STABLE** (drift-proof band ±4pp).

**22:45Z lineup-window protocol (conservative):** eyeball the official XIs (~T-75min). The ONLY reconsider
trigger = **Rice AND Kane both out** (unpriced double collapse → consider Mexico 1-0, NOT 1-1). A single
absence does not clear the threshold. Optional 30-second odds glance ~23:30Z; no re-fetch needed.

**Direct answer to Sebas:** if it ends level at 90′, **penalties are ~2× more likely than an ET winner
(69% vs 31%, N=49, 1986–2022)** — and even on the pens path only half stand at 1-1, so the 1-1 final is an
**~11% unconditional scenario**. Entering it trades the modal 9-pt outcome (England 0-1) for a lottery
ticket that pays 1 pt on the most likely result. From 1st place at +15: **not smart math** — the same
verdict our own Belgium-Senegal council reached in R32, now with the full historical record behind it.

---

## AUDIT ADDENDUM (post-synthesis self-audit, Sebas-mandated; binary gates vs frozen code + recount)
- **C2 — rubric payoffs: 8/8 PASS** against `src.optimizer.points` (the adjudicator): 1-1 entry collects
  1 on 0-1/1-0, 4 on 0-0/2-2 pens, 9 only at 1-1 pens; 0-1 entry collects 9 modal / 1 at 1-1 / 0 at 1-0.
- **C3 — Historian-C refutation verified numerically:** devig(+145/+210/+210) → ENG 38.8% ≈ snapshot 38.2%
  (the "40.8% firmer" claim was vig-inclusive). Synthesis PASS.
- **C1 — Historian-B recount (game-by-game): CORRECTED.** Pens = 34 ✓ and the 120′-score distribution
  17×1-1 / 12×0-0 / 4×2-2 / 1×3-3 ✓ EXACT; but ET-decided = **19, not 15** (missed BEL-URS '86 aet +
  CMR-COL, YUG-ESP, ENG-BEL '90 aet). Historian-A conversely OVERCOUNTED ET-wins (BUL-GER '94 and
  ITA-ENG '90 3PO were 90′ results). **Corrected: N=53 level-at-90′ (33.1% of 160); 64.2% pens /
  35.8% ET-decided (pens ~1.8×, not 2×).**
- **C5 — verdict invariance: PASS, STRENGTHENED.** P(1-1@120′ | level) = 17/53 = **32.1%** →
  **P(1-1 final) ≈ 9.9%** (below the 11% quoted). And corrected pens share **0.642 vs engine f_model
  0.637** = a near-exact independent calibration match. Every correction moves AGAINST the 1-1 entry;
  the **ENTER 0-1** verdict is unchanged and firmer.

---

## FACE-OFF ADDENDUM — 0-1 vs 1-2 (Sebas-mandated second council, 2026-07-05 ~19:20Z)
> Zero-invasive: public `ko_candidates` API on scratchpad snapshot copies; frozen files untouched;
> B4 replay byte-identical. Success criteria defined BEFORE running (G1–G6).

### Deterministic backbone
FULL120 EVs: **0-1 = 2.676 > 1-2 = 2.534 (+0.142)** > 0-2 = 2.286 > 1-0 = 2.257 > 2-1 = 2.136 > 1-1 = 1.671.
Both picks = one-goal England win → the face-off is EXACTLY **P(Mexico scores | one-goal England win)**;
engine conditional = **0.477** (to-nil 0.523). Engine grid: P(MEX≥1) 0.661, **P(BTTS) 0.479**.

| Gate | Test | Result |
|---|---|---|
| G1 base gap | ≥ +0.035 noise floor | **PASS** +0.142 (4× floor) |
| G2 totals sweep | crossover p_over* vs market | **PASS** — bisected **p_over* = 0.4866**; cross-book de-vig 0.38–0.41, juice drifting UNDER; +8.9pp gap, no evidence |
| G3 ENG-prob sweep | crossover vs drift band | **PASS** — England firming WIDENS 0-1's lead (+0.19 @45% → +0.53 @60%); 1-2 has NO route via team strength (0-2 passes it by ENG 55%) |
| G4 f-band | ordering all cageyness | **PASS** — 0-1 leads +0.118…+0.175 at every f |
| G5 council | any rule-confirmed EV-UPDATE to 1-2? | **NONE** (3 lenses + synthesis, below) |
| G6 B4 | byte-identical replay | **PASS** |

### Panel (3 lenses + synthesis; sourced 2026-07-05)
**Totals-market:** cross-book p_over(2.5) **0.38–0.41** (DK 38.1 / consensus 40.6), juice moved mildly
toward the UNDER; **BTTS Yes de-vig ≈ 46% vs engine 47.9% — market and engine AGREE** (the lens mis-guessed
the engine number; audited). Altitude consensus = low-total-REINFORCING (England can't press at 2,240m;
Mexico 4 straight Azteca clean sheets). Zero evidence for 0.49.
**Adversarial (1-2 steelman, LOW):** landed = Rice nerve-pain, Azteca 1985 (England's only visit, lost 0-1),
late-push dynamics — all public/priced. **Premise-correction: England have 2 clean sheets in 4** (0-0 Ghana,
2-0 Panama), not 1; Mexico's 8 GF came vs RSA/KOR/CZE/ECU; Aguirre's low block produces 0-1 losses, not 1-2.
**Historian-D:** England KO-win shape ~50% to-nil (4 nil / 4 conceding since 2018); Mexico scored in all
4 games, unbeaten at Azteca since 2013 (W70 D17 L2/89); Azteca '86 inflator negligible (2.6 vs 2.54 g/g);
**all-WC one-goal wins split 1-0:2-1 = 182:152 = 54.5% to-nil**. Leaned "context favors 1-2".
**Synthesis (audited):** the historian's OWN base rate (54.5/45.5) matches the engine conditional
(52.3/47.7) within 2pp — **model, raw history, and the live totals market converge independently on 0-1**;
the contextual 1-2 narrative explains the number post-hoc, it does not update it.

### VERDICT — HOLD England 0-1 (entered pick correct; no change)
**Reopen condition at the 22:45Z lineup reveal (conservative, BOTH required):** Rice absent/restricted AND
England fielding a high line that exposes Spence to Quinones/Alvarado pace. Either alone is priced.
**Plain answer:** the totals market already knows Mexico always scores at the Azteca — and still prices the
game under (0.40). Switching to 1-2 requires a 9pp totals-market error that the base rate, the engine, and
the drift direction all independently contradict.
