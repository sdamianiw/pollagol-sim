# COUNCIL VERDICT — España vs Belgium (QF2, 2026-07-10 19:00Z) — **ENTER SPAIN 2-1** (conditional T-15 check)

> I-HITL: RECOMMENDATION only; Sebas enters. Deadline **18:50Z today**. Council ADVISORY (L44);
> the FROZEN engine adjudicates. Convened: MANDATORY (Sebas; champion node) — deterministic trigger
> technically no-fire but the board is a sub-noise razor, the exact case the plenos-tiebreak governs.
> Snapshot `md5_2026-07-10T17-34-17Z.json` (T-1.4h, 25 books, quota ~470). Sebas's fork: 1-0 vs 2-0.

## DETERMINISTIC BACKBONE (frozen engine, 17:34Z)
- De-vig: **ESP 58.7 / draw 24.0 / BEL 17.2**; totals 2.5, **p_over 0.544**, mu_eff 2.857; engine-fitted
  λ = **ESP 1.92 / BEL 0.98** (the market prices Belgium at ~1 expected goal).
- **FULL120 argmax = 2-1 (3.226) — flipped overnight from 1-0** (3.210, gap +0.016 SUB-NOISE < 0.030);
  2-0 = 3.097 (third); 1-1 DEAD (1.323); 0-1 = 1.457. 2-1 argmax at every cageyness f in [0.45, 1.00]
  incl. the MEX-ING-validated empirical f≈0.64; only the extreme-cagey corner (f≥0.80) returns 1-0.
- **Plenos tiebreak (pool-confirmed 2026-07-10: most exact scores): P(exact@120') 2-1 = .1195 > 1-0
  = .1155 > 2-0 = .1033** — the tiebreak axis AGREES with the EV axis (they crossed together when the
  totals moved).
- **Odds-drift series** (Jul-7 13:44Z → Jul-9 17:23Z → Jul-9 18:37Z → Jul-10 17:34Z): ESP .575→.582→
  .582→.587 (slow firm), p_over .526→.526→.526→**.544** (today's move = the flip's cause). Fresh
  books corroborate BEYOND our snapshot: DK Over −125 (~.556 devig, 72% tickets/67% cash on Over),
  Spain line SOFTENING (−160→−155, BEL 450→425). **Both live drift axes point toward 2-1.**
- **Drift harness** (`drift_esp_bel.py`, CONTROL==LIVE exact 0.00e+00, B4 PASS): 6/10 grid points hold
  2-1; flips back to 1-0 at ESP+2pp or p_over−1pp — a genuine knife-edge. **Boundaries: 2-1 argmax for
  p_over ≥ 0.54** (live .544, DK .556); at fixed total, 1-0 needs **ESP ≥ 0.61** (live .587, softening).
- **2-0 (Sebas's second candidate) is DOMINATED:** argmax nowhere reachable — requires ESP ≥ 0.70 AND
  p_over ≥ 0.58 simultaneously. Do not enter it.
- **ET decomposition favors 2-1 here** (mirror of FRA-MAR): modal 90'-level score is **1-1**, and Spain
  winning in ET from 1-1 ends **2-1 = our exact 9**; 2-1 gains more from FULL120 than 1-0 (+0.328 vs
  +0.260).
- **Lead-protection enumeration** (`lead_protect_esp_bel.py`, exact 81-cell, B4): objective "CANNOT LOSE
  THE LEAD" — 2-1 has ≥ E[gap-swing] vs EVERY plausible rival entry (by exactly its EV edge) and the
  pleno-tail P(rival gains ≥5) is symmetric (.116 vs .120). **Chalk logic survives the ownership test;
  no E[prize]-vs-EV divergence.** With picks hidden, entering the argmax remains the defense (L50).

## LENSES (isolated; synthesis audited every load-bearing number)
- **Historian (recounted, consistent):** the "1-0 dynasty" prior belongs to 2008-2012 (five 1-0s). The
  CURRENT squad's KO signature (Euro-2020→now, 10 games): **2-1 ×3 (Euro-2024 QF/SF/Final vs Germany/
  France/England), 1-0 ×1 (Portugal last week), 2-0 ×0**, 3+ ×3, pens ×3. Comparable ~59% WC favorites:
  win-by-exactly-1 outnumbers win-by-2+ **6:3**; underdog scored in **65%** (11/17). Counter-datum: QFs
  run −0.25..−1.0 goals/game vs R16 (2018/2022) — an aggregate lean the live market has already priced
  (Over still favored for THIS game).
- **Form/market:** Onana (BEL's defensive engine) ACL-OUT; Belgium 13 GF/5 with Trossard (17 chances
  created, tournament high)/De Ketelaere (brace + assist vs USA)/Lukaku; Spain 9 GF / **0 GA in 5**,
  Simón record streak — but the market prices the streak at BTTS-No only +110 (BEL ~52-57% to score)
  and win-to-nil +185 (~35%). EU correct-score book: 1-0 = 1-1 = 7.00, 2-0 = 2-1 = 7.50 — near-flat.
  External models: Opta ESP 58.3, Dimers 60.6, modal 1-0 — modal ≠ rubric-argmax (our modal is 1-1;
  the engine exists precisely to optimize E[pts], not P(mode)).
- **Adversarial (pro-1-0) — numeric core REFUTED on audit (L44/L-audit):** its P(exact) tiebreak
  (1-0 .147 vs 2-1 .093, "decisive") used a hand-rolled independent Poisson at λ_BEL 0.75 ⇒ total 2.4,
  INCONSISTENT with the priced p_over .544 (same class as the MEX-ING vig-vs-devig error); the frozen
  engine's exact distribution says 2-1 .1195 > 1-0 .1155. Its zero-point edge claim (~10pp) collapses
  to **0.4pp** on exact enumeration (1-0 .171 vs 2-1 .175). What SURVIVES: the gap is sub-noise (true),
  and the p_over-composition question — answered in odds-space: the "Spain-does-the-scoring" world is
  ESP ≥ .61 at this total, and the market is moving the OTHER way.
- **Champion-node bias audit (FM5, POR-ESP precedent):** the España stake biases toward Spain
  ADVANCING — both candidates are Spain wins; no scoreline-bias vector. Hedge re-run NOT triggered
  (BEL .172 << the .45 coin-flip threshold); the Jul-9 locked-50 table already covers España-out
  (≈neutral vs Greg, negative vs Lucas) — posture unchanged either way tonight.

## VERDICT — **ENTER España 2-1** (deadline 18:50Z), with the T-15 conditional below.
Every live axis agrees: EV argmax (razor +0.016), plenos-tiebreak P(exact) (+0.004), intraday drift
(totals up + Spain softening, both toward 2-1), fresh-book money (Over −125, 72% public), the modern-era
Spain KO base rate (2-1 ×3 in the last four elite KO wins), and the lead-protection table. The lone
1-0 case standing after audit — QF-round caginess — is an aggregate the priced market has already
rejected for this fixture. **The razor is real: this is a ~52/48 call, and 1-0 costs only ~0.016 E[pts]
if preferred — but on the pool's own tiebreak currency (plenos) 2-1 is the higher-probability exact.**
- **T-15 protocol (~18:25-30Z refetch):** if fresh **p_over ≥ 0.54** → confirm 2-1; if the total
  RETRACED **< 0.54** → enter 1-0 (the boundary is engine-exact). Fetch-fail fallback = app odds rule:
  Over 2.5 clearly shorter than Under → 2-1; Over ≈ or longer than Under → 1-0.
- **NEVER 1-1** (dead −1.9) · **NEVER 2-0** (dominated everywhere reachable).
Classification when recorded: trigger no-fire but user-mandate convening; pick = FULL120 argmax at the
final pre-lock read (L57); entered == that argmax → `none`.

## T-15 ADDENDUM (18:26Z refetch `md5_2026-07-10T18-26-03Z`) — **CONDITION RESOLVED: 2-1 CONFIRMED, FINAL**
Fresh odds byte-equal to 17:34Z (devig .5874/.2404/.1721, p_over **0.544** >= the 0.54 boundary; no
retrace). Flip-check 3/3 HOLD gap +0.0000, B4 byte-identical; fresh FULL120 argmax 2-1 (3.226) == the
boundary-gate conclusion (two independent paths agree). Sebas ENTERED 2-1 pre-confirmation (18:0xZ);
entered == final argmax -> classification when recorded: `none`. Delivered T-24min (lock 18:50Z).

## Siblings (17:34Z board)
- **NOR-ENG (Jul-11 21:00Z): council FIRES tomorrow at its own T-1h ~20:00Z** — fresh 90' argmax 1-2
  vs registered 0-1, gap 0.001 razor-within-winner; FULL120 will adjudicate on fresh odds. Kane node.
- **ARG-SUI (Jul-12 01:00Z): HOLD 1-0** (ARG .58, argmax==modal, no-fire; recheck ~00:00Z Jul-12).
