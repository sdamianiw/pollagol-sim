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
