# COUNCIL VERDICT — Switzerland vs Colombia (R16, 2026-07-07 20:00Z) — KEEP 0-1, DECISIVE

> I-HITL: RECOMMENDATION only. Sebas enters; nothing locked. Entry deadline **19:50Z today**.
> Council ADVISORY (L44); the FROZEN engine adjudicates E[pts]. Snapshot `md4_2026-07-07T13-44-24Z.json`
> (13:44Z = T-6.25h; Sebas cannot fetch again pre-lock — this council runs at T-6h by design).
> Trigger: **FIRE** (weak-fav 0.418<0.55 AND EV-argmax 0-1 ≠ modal 1-1).

## DETERMINISTIC BACKBONE (frozen engine, 13:44Z odds)
- De-vig 1X2: **SUI 27.1% / Draw 31.1% / COL 41.8%** — Colombia lead 14.7pp. Totals 2.5, p_over 0.403,
  mu_eff 2.296 (LOW-scoring market).
- **FULL120 argmax = 0-1 (E 2.868)**; runner-up 1-2 (2.713, gap 0.155 > noise 0.030); 0-2 (2.506);
  modal 1-1 DEAD (1.646, −1.22). Argmax 0-1 at EVERY cageyness f 0.25–1.00.
- Flip-check vs Jul-6 22:16Z baseline: **HOLD, gap_base +0.0000** (argmax identical).
- Drift harness (`drift_arg_sui.py`, fresh snapshot, CONTROL==live PASS, B4 PASS): **22/22 STABLE** —
  0-1 holds under fav-axis ±4pp, draw ±2pp, p_over ±7pp. Second consecutive day fully stable.
- Flip boundary < 6.7pp COL lead (live 14.7pp) → needs an ~8pp swing ≈ **4.6σ** under the empirical
  drift model (σ=0.0069/√h over 6.25h). P(flip) ≈ 0 even at 3σ fat-tail stress.
- Tiebreak (P-exact secondary sort, 0.030 band): 0-1 = **13.7% P(exact@120′), the max** — reinforces.

## FORM/NEWS LENS (all sourced 2026-07-07; full cites in session log)
- **Switzerland injury crisis, late-breaking:** Manzambi (3G+2A, their breakout attacker) **CONFIRMED OUT**
  (knee, final training Jul-7; ESPN/OneFootball/Yahoo). Vargas (2G+1A), Sow, Aebischer, Jaquez all
  DOUBTFUL (left/skipped Monday training; ESPN/Sports Mole). No suspensions.
- **Colombia:** Cordoba out (tournament, hamstring — already priced); James Rodriguez PROBABLE (squad
  flu-virus watch, included in published XIs; UNVERIFIED full fitness). L. Suarez starts. Best defensive
  record in the draw (1 GA in 4); Luis Diaz the consensus difference-maker.
- **Fresh books vs our 13:44Z devig:** Rotowire consensus implies COL 44.4 / D 31.3 / SUI 26.3;
  FanDuel +125/+200/+250; Kalshi traders 43/32/27 — market **equal-or-stronger Colombia** than our read.
- **External models:** Dimers COL 43% (top score 1-1 13.1% — dead under FULL120, modal≠optimal);
  Rotowire analyst pick literally **1-2 Colombia**; OddsShark computer anomalous (flagged stale by lens).
- **Lens verdict: NO Colombia-weakening vector exists**; the Swiss injury cluster pushes the market
  FURTHER toward Colombia — the direction that widens 0-1's edge (fav-axis +4pp: 0-1 E 3.085).

## ADVERSARIAL/PREMORTEM LENS (attack 0-1; full text in session log)
- **1-2 steelman fails:** needs p_over ≥ 0.52 (live 0.403); conjunction COL-win AND over-2.5 contradicts
  the totals market; P(exact) 10.8 < 13.7. Symmetric 4-vs-9 exchange doesn't cover the 0.155 EV gap.
- **0-2 fails:** a 31% draw price is inconsistent with a dominant-COL story; would need COL ≥55% + draw <22%.
- **1-0/SUI fails:** negative-EV insurance (sacrifices 0.806 E[pts] for a 27% world); SUI would need to be
  a true ~40% favorite to flip the argmax — no basis.
- **ET decomposition is 0-1's FRIEND:** the modal 90′-draw path under p_over 0.40 is 0-0→ET; Colombia
  winning in ET ends **0-1 = our exact 9**. Only the smaller 1-1→COL-ET path (~5-7%) favors 1-2, and even
  there we bank 4.
- **Premortem (0 pts):** requires a SUI clean-sheet win (1-0 ~9-10%, 2-0 ~4-6%) or 2-2-pens (<2%);
  total zero-exposure ~13-18%, bounded by SUI's 27%, irreducible without worse expected cost.
- **Lens verdict: HOLD 0-1.**

## ADJUDICATION
Engine, drift model, tiebreak rule, news lens, and adversarial lens are **unanimous** — the trigger fired
on the weak-fav/modal-vs-argmax condition, and the council's answer is that the modal 1-1 is a FULL120
artifact, exactly the case the KO draw-suppression doctrine anticipated. News flow (Swiss injury cluster)
points the market toward MORE Colombia, i.e. deeper into 0-1 territory.

## VERDICT — **KEEP Switzerland 0 – 1 Colombia** (board already correct). DECISIVE, no conditional.
Residual app-visible rule (formality, P≈0): at entry time, only if the app shows **Switzerland's win odds
equal to or SHORTER than Colombia's** (a full market reversal) would the pick be in question — in that
world enter 1-0; any lesser move changes nothing. 1-1 is NEVER correct (dead ≥1.2 EV everywhere).
Classification when recorded: council FIRED → pick = FULL120 argmax **0-1** (L57); entered 0-1 → `none`.

## Same-day siblings (closed this cadence, 13:44Z)
- **ARG-EGI (lock 15:50Z): HOLD 1-0** — no-fire (fav 0.717), argmax 1-0 at every f, 11/11 drift-stable,
  max-P(exact) 16.2%. Board correct. No council (trigger requires weak-fav).
- **QF baselines registered** `md5_2026-07-07T13-44-44Z.json` (3/3 determined QFs, calendar-verified
  externally): FRA-MAR Jul-9 20:00Z argmax 1-0 no-fire · **ESP-BEL Jul-10 19:00Z argmax 1-0, Spain 57.5%**
  (f-band splits 1-0→2-1 at f≥0.85 — real decision at its own T-1h; champion node) · NOR-ENG Jul-11
  21:00Z argmax 1-2, weak-fav 0.506 → **its council WILL fire** at T-1h Jul-11. QF4 (tonight's winners)
  undetermined — window-scoped out; baseline after tonight.
