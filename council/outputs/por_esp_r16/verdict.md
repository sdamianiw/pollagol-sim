# COUNCIL VERDICT — Portugal vs España (R16, 2026-07-06 19:00Z) — THE CHAMPION NODE

> I-HITL: RECOMMENDATION only. Sebas enters; nothing locked. Entry deadline **18:50Z**.
> Council ADVISORY (L44); the FROZEN engine adjudicates E[pts]. Snapshot `md4_2026-07-06T17-33-02Z.json`
> (17:33Z, T-1.5h). Branch `rho-fit`, engine FROZEN. Trigger: **FIRE** (weak-fav 0.495<0.55 AND 90′
> argmax 0-1 ≠ modal 1-1) + Sebas-mandated deep council (champion double-exposure vs Lucas's Portugal).

## MANDATE
Confirm or challenge the pre-entered **España 1-2**; adjudicate the placement/hedge question ("fire
placement-MC or stay chalk?") given our España champion + Lucas LDC (2nd, −17, Portugal champion).

## DETERMINISTIC BACKBONE (frozen engine, fresh odds; reproduce = exact)
- De-vig 1X2: **POR 23.6% / Draw 26.9% / ESP 49.5%**. Totals 2.5, p_over 0.534, mu_eff 2.815.
- 90′ argmax 0-1 (2.681), modal 1-1. **FULL120 PICK = 1-2 (E 2.977)** [ET-flip from 90′ 0-1].
- Candidate table (FULL120): **1-2 = 2.977 · 0-1 = 2.930 (gap +0.047) · 0-2 = 2.753 · 2-1 = 1.745 ·
  1-0 = 1.735 · 1-1 = 1.401 · 0-0 = 1.163**. Draw dead (flip-threshold corollary).
- f-band: argmax **1-2 at every cageyness 0.25→1.00** (gap +0.012 → +0.067, tightest at most-cagey).
- Flip-check vs Jul-5 baseline: HOLD (90′ argmax 0-1 == baseline; FULL120 1-2 == pre-entered).

## HARNESS (scratchpad `hedge_por_esp.py`, zero-invasive, CONTROL==live PASS)
- **G2 totals sweep** (the ONE live sensitivity): argmax 1-2 holds at p_over ≥ 0.51; **flips to 0-1 at
  p_over ≤ 0.48** (crossover ≈ 0.50). Live books straddle: our devig 0.534; DK current Over −125
  (~0.53 devig, total FLIPPED open Under→Over, 82% of money Over per Action Network 15:30Z); an earlier
  under-lean read (~0.48) was stale. Freshest consensus ≥ 0.51 → **1-2 stands on live data**.
- **G3 ESP devig ±4pp: 1-2 argmax across the whole band** (gap +0.017 … +0.064). 1X2 drift can't flip it.
- **G5 hedge portfolio (binary criterion, fixed before running):** branch probs at 120′: ESP-win 0.575 /
  POR-win 0.280 / pens 0.144; P(adv) ESP 0.648 (== market to-advance 65.4%, independent cross-check).
  Expected gap-change vs Lucas tonight (match + champion-liveness swing, q = P(title|QF) ∈ {.15,.25,.35};
  market lens: q ≈ 0.19 BOTH teams):
  chalk **1-2: +1.68…+2.27** · 0-1: +1.63…+2.22 · **hedge POR 2-1: +0.44…+1.03** (Lucas-enters-POR case);
  in the Lucas-chalk case hedge goes NEGATIVE (−0.79…−0.20). **Hedge dominated everywhere in the band →
  criterion says STAY CHALK.** placement_mc stays PARKED (prereqs unmet; this bounded harness answers
  tonight's question).

## PANEL (6 lenses, isolated, advisory — full texts in session log)
- **Historian:** 7 competitive meetings 2004-25: Spain 3W-2D-2L; 5/7 ≤2 goals in 90′; 4/7 level at 90′
  (57% vs 33% KO base rate); only WC KO precedent = Spain 1-0 (2010 R16); most recent = Portugal on pens
  (2025 NL final, 2-2). Lean: under-2.5, draw-at-90′ not overpriced. Sources cited.
- **Form/tactical:** CONFIRMED XIs — Spain full (Simón; Porro-Cubarsí-Laporte-Cucurella; Rodri-Pedri;
  Yamal-Olmo-Baena; Oyarzabal); Portugal full (Costa; Cancelo-Veiga-Dias-Mendes; Neves-Vitinha; Neto-
  Bruno-Leão/Félix; Ronaldo). Nico Williams available (sub), Pino out. Spain 0 GA in 4 (Simón 519′ WC
  clean-sheet record); Portugal 2 GA, nervy R32. Cagey read; skeptical of over-2.5.
- **Market:** no meaningful late drift (DK/b365/FD devig ≈ snapshot ±0.8pp); correct-score board: 1-1
  modal 15.4%, then **1-2 (13.3%) ABOVE 0-1 (12.5%)** — the market itself ranks 1-2 over 0-1, engine-
  concordant; to-advance ESP 65.4%; P(title|adv) ≈ 19% BOTH (Kalshi devig). POR firmed +295←+310 despite
  one-way Spain handle (mild sharp interest, noise-level).
- **Chalk/doctrine:** HOLD 1-2; hedging = leader bias in pure form; locked-50 not match-addressable;
  bias-guard "from 3rd place I'd enter the same" PASSES.
- **Adversarial/premortem:** FM1 (POR wins → Lucas overtakes: −3 net after champion swing) = LANDS-BUT-
  PRICED, unhedgeable at match layer, HOLD; FM3 draw = REFUTED (2.977 vs 1.401); FM5 bias-audit: our
  España stake pulls toward "dominant" 1-2 over historically-grounded 0-1 — flagged, adjudicated below;
  FM4 lineup triggers: RESOLVED (both XIs confirmed full-strength — no reopen condition live).
- **Rival/field:** Spain-advance = best branch on BOTH layers (kills Lucas's champion+GK, neutral vs
  Greg); Portugal-advance = common-mode España kill WITH Greg (he also loses Yamal MVP → actually widens
  our Greg gap) — the two-front problem resolves in favor of chalk; Lucas PRIOR 80-90% enters a POR win.
  Tiebreaker rule still UNVERIFIED (check in-app before QF locks — material only if gap ≤ ~5 later).

## ADJUDICATION (engine + fixed criteria; synthesis addendum may follow post-lock)
1. **España-win direction: unanimous** (engine argmax, doctrine, rival branch table, hedge criterion).
2. **Hedge/placement question: STAY CHALK — binary criterion decisive** (chalk beats hedge by ~+1.2
   expected gap-points vs Lucas in EVERY q × Lucas-entry scenario; hedge also bleeds vs Greg and field).
3. **1-2 vs 0-1 (the razor):** gap +0.047 at live odds, 1-2 argmax at every f and every 1X2 drift ±4pp;
   only totals ≤0.48 flips it, and the freshest market reads ≥0.51 with money moving OVER. The
   adversarial bias-flag (prefer 0-1) does not constitute a rule-confirmed EV-UPDATE — the engine on
   live data says 1-2, the correct-score market independently ranks 1-2 above 0-1, and switching would
   BE the override. L50: enter the argmax.

## VERDICT
**KEEP the pre-entered España 1-2.** No hedge, no draw, no switch to 0-1. Deadline **18:50Z**.
App-visible flip rule (only condition that reopens the scoreline): if the app's Under 2.5 price at entry
time implies p_over ≤ 0.48 (Under ≈ −140 or shorter), 0-1 overtakes — cosmetic (both Spain wins, ±0.05 EV).
Worst-case on record (FM1): POR advances (35.2%) → our España dies, Lucas's lives; gap math says we then
lead the match layer by +17 minus his tonight's gain, champion swing −10q lands at the FINAL, not now;
response = out-execute the remaining ~6 boards, doctrine trigger "re-eval if España out pre-QF" FIRES then.

---

## SYNTHESIS ADDENDUM — metacognitive audit (post-recommendation, pre-result)
*Audits reasoning/consistency only; no EV recomputation. Full lens texts in session log.*

| Section | Verdict |
|---|---|
| A — Contradiction resolution (historian/form UNDER-lean vs market OVER-flip) | **SOUND** — anchoring on the 17:33Z devig (p_over 0.534) over the stale ~0.48 read was correct: the totals market already aggregates the H2H/defensive-record evidence the qualitative lenses cite. Nuance for the record: the correct-score board's 1-2 > 0-1 margin (13.3 vs 12.5) is thinly-traded, directionally consistent but NOT independent corroboration — the load-bearing signal is the totals price. |
| B — FM5 bias-flag vs the +0.047 razor | **SOUND, and stronger than written**: FM5's mechanism has a logical gap — the España champion stake biases toward *Spain advancing* (win/loss direction), NOT toward 1-2 over 0-1 *within* Spain wins (both serve the champion identically). The bias argument does not operate at the margin it was aimed at; "switching to 0-1 would itself be the override" stands cleanly (L50). |
| C — Hedge criterion construction | **SOUND** — the whole-band requirement (q up to 0.35, market-implied ≈0.19) is the conservative direction; the Lucas-entry prior (80-90% POR) is unverified but the conclusion is robust to it being wrong (hedge goes negative in the Lucas-chalk case). No circularity. |
| D — Missing modalities | **FLAWED-BUT-IMMATERIAL** — rest-day differential and venue/surface unexamined by any lens; f-band + ±4pp stability means a realistic 2-3pp fatigue shift in p_over cannot cross the 0.50 flip point (margin 0.034). Add to the standing lens checklist. |
| E — Recursion (self-audit) | Anchoring risk named (auditing a delivered verdict); complexity-deference flagged; the honest residual uncertainty lives in A: **gap +0.047 rides on a p_over 3.4pp above its flip point, with two qualitative lenses leaning Under** — the market-over-narrative hierarchy is a design choice doing real work here, recorded as such. |

**No verdict change recommended.** (KEEP España 1-2 stood; delivered 18:22Z, pre-lock.)
