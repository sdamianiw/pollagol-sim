# COUNCIL VERDICT — France vs Morocco (QF1, 2026-07-09 20:00Z) — **ENTER FRANCE 1-0**, DECISIVE

> I-HITL: RECOMMENDATION only. Sebas enters; nothing locked. Entry deadline **19:50Z today**.
> Council ADVISORY (L44); the FROZEN engine adjudicates E[pts]. Trigger: deterministic no-fire
> (argmax==modal==1-0, fav 0.612) — convened by **USER MANDATE** (Sebas face-off request: 1-0 vs 2-1,
> "close call… France by one goal… or 2-1 with both teams scoring, especially over 120'").
> Snapshot `md5_2026-07-09T17-23-16Z.json` (T-2.6h, 25 books, quota 472). T-1h refetch protocol below.

## DETERMINISTIC BACKBONE (frozen engine, 17:23Z odds)
- De-vig 1X2: **FRA 61.2% / draw 24.8% / MAR 14.0%**. Totals 2.5, p_over **0.479** (under-leaning),
  mu_eff 2.588. Flip-check vs Jul-7 baseline: **HOLD, gap_base +0.0000**; B4 byte-identical.
- **FULL120 argmax = 1-0 (E 3.460)**; the face-off: **2-1 = 3.309 (−0.151 ≈ 5× the 0.030 noise floor)**;
  2-0 = 3.304; 3-1 = 2.937; 1-1 DEAD (1.375, −2.09); 0-1 = 1.361. **1-0 argmax at EVERY cageyness
  f ∈ [0.25, 1.00]** (dec−draw ≥ +1.67 everywhere — no council-eps proximity).
- **Drift harness** (`drift_fra_mar.py`, scratchpad; **CONTROL==LIVE exact, max|ΔEV| 0.00e+00; B4 PASS**):
  **9/10 grid points stable** — 1-0 survives FRA ±4pp, draw ±2pp, p_over −7pp; the ONLY break is
  p_over +7pp (0.549) where 2-1 wins by a razor −0.0002.
- **Flip boundary (fine-scan): 2-1 becomes argmax only at p_over ≥ 0.55** — a +7pp totals move AGAINST
  the live under-lean (O/U −105/−115 Under-side). Joint stress corner (FRA−4pp AND p_over+7pp): 2-1 by
  −0.036 — a world contradicted on both axes by the priced market.
- **Tiebreak P(exact@120'): 1-0 = 14.2% (max)** > 2-0 12.1% > 2-1 11.8%. ET decomposition: FULL120
  RAISES 1-0's EV (+0.278 vs 90') — the modal level-at-90' path is 0-0, and France winning in ET ends
  **1-0 = our exact 9**. Sebas's "2-1 if it goes the distance" intuition points the wrong way: the
  120' structure is 1-0's FRIEND (needs the smaller 1-1@90' branch to favor 2-1).

## FORM/NEWS LENS (sourced 2026-07-09; cites in session log)
- **Morocco: Saibari (their tournament-best creator, scored in all 3 group games) CONFIRMED OUT**
  (hamstring; Al Jazeera/RotoWire) — directly deflates the "Morocco scores" leg 2-1 needs. Five Moroccans
  incl. Hakimi one yellow from a ban; 120'+pens played in R32 (fatigue). Bounou fit.
- **France:** W5, 14 GF / 2 GA, never >1 conceded, zero ET played; Mbappé 7 goals, scored in every KO
  game; Tchouameni doubtful (Kone deputizes), Saliba expected. WC-2022 semi precedent: FRA 2-0 MAR.
- **Market:** FRA −170 (~63%), stable since open — NO drift; Over/Under 2.5 = −105/−115 (Under-lean);
  BTTS No-lean; **correct-score ranks: 1-0 +500 (#1)** > 2-0 +600 = 1-1 > 2-1 +650; France win-to-nil +150.
- **External models:** Opta FRA 62.2%; Dimers FRA 59.8% with **top score 1-0 (16.0%)**; RotoWire pick =
  France win + Under 2.5. Engine/market/models triple-convergent.

## ADVERSARIAL/PREMORTEM LENS (attack both candidates; full text in session log)
- **2-1 steelman FAILS:** needs BTTS-Yes AND ≥3 goals (jointly capped by p_over 0.479); needs p_over ≥0.55
  vs an under-leaning book; the one big team-news item (Saibari OUT) attacks it; Mbappé's form is already
  in the price. France's 2.8 GF/game is a group-stage composite, not a Morocco-adjusted number.
- **2-0 = the only near alternative** (−0.156) — more market-consistent than 2-1 (clean-sheet lean) but
  doesn't beat 1-0 at any evidenced parameter.
- **Premortem (zero points):** 1-0 zeroes only on a Morocco win with France blanked or 2-2+ (~8-11%,
  bounded by MAR 14%); 2-1 zeroes on 0-0 or 0-2+ (~10-13% — HIGHER, 0-0 is the most common draw).
- **Bias audit (FM5 analog):** our locked stakes (Mbappé scorer; the locked-50 table says "root against
  France") pull in OPPOSITE directions and neither touches the engine — the pick is market-derived; no
  contamination vector. Verdict: HOLD 1-0.

## CHALK / FIELD-SEPARATION QUESTION (Sebas: "most people aren't picking 1-0")
Per-match scorelines are HIDDEN on pollaya → any field claim is a PRIOR, not an observation. On this
board there is NO tension to balance: 1-0 is simultaneously (a) the EV-argmax, (b) the market's #1-priced
correct score, (c) the external models' modal score, and (d) the max-P(exact) score. If the field's prior
mass sits on 2-0/2-1 (Mbappé narrative), 1-0 hitting yields exact-9 vs their 4 = **+5 separation per
chaser as a BYPRODUCT of the chalk-EV pick** — no deviation needed to buy it. L50 stands: leader plays
argmax; deviations cost −8% to −20% (Jul-3 MC). The POR-ESP hedge harness precedent (STAY-CHALK decisive)
generalizes: entering the argmax IS the defense.

## VERDICT — **ENTER France 1-0** (all lenses + engine unanimous; gap to runner-up 5× noise floor).
**T-1h protocol (~18:50Z refetch, quota fine):** flip-check vs `md5_2026-07-09T17-23-16Z` baseline.
Enter 1-0 UNLESS the fresh snapshot shows **p_over ≥ 0.55** (then 2-1 is a rule-confirmed EV-UPDATE, L35)
— any lesser totals move changes nothing (boundary engine-verified). **NEVER 1-1** (dead −2.09 at every f;
KO draw entries are ALWAYS tilts, MEX-ING corollary). If the refetch fails: app-odds rule — only if the
app shows the Over CLEARLY favored (≥ ~-140-equivalent on O2.5) would 2-1 be in question; else 1-0.
Classification when recorded: council no-fire (user-mandate convening) → pick = 90'==FULL120 argmax 1-0;
entered 1-0 → `none`.

## Same-cadence siblings (17:23Z board, `md5_2026-07-09T17-23-16Z`)
- **ESP-BEL (Jul-10 19:00Z, lock 18:50Z): RAZOR** — FULL120 1-0 (3.228) vs 2-1 (3.213) = +0.015 SUB-FLOOR,
  argmax flips to 2-1 at f=1.00; p_over 0.526 and rising would flip it. **Council at its own T-1h
  MANDATORY** (champion node: España + Greg common-mode; locked-50 table pre-computed for the España-out
  branch — no posture change either way).
- **NOR-ENG (Jul-11 21:00Z): council WILL FIRE** (weak-fav ENG 0.514; FULL120 1-2 flipped from 90' 0-1;
  within-winner drift 1-2→0-1 gap 0.008 sub-floor). Adjudicate on fresh odds at T-1h. Kane-MVP watch node.
- **ARG-SUI (Jul-12 01:00Z): HOLD 1-0** — decisive (ARG 0.564, argmax==modal, dec−draw +1.88 at f_model;
  no-fire). Baseline registered this fetch (NO-BASELINE → first-fetch establishment).
