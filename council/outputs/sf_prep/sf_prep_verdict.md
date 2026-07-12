# SF PREP VERDICT — semifinal baselines, boundaries, endgame branches (2026-07-12)

**ADVISORY (I-HITL — Sebas enters; nothing locked today). Engine adjudicates EV (L44). KO_SCORING =
FULL120 (L57). The ENTRY DECISIONS happen at each fixture's own T-1h on fresh odds — today's deliverable
is the boundary map + the endgame audit, not a premature lean.**

Snapshot `data/snapshots/md6_2026-07-12T12-14-09Z.json` (12:14Z, quota 460, 2/2 == FIFA calendar,
full-string bound, B4 PASS). Board reconciled first: **us 377 rank 1/27** (NOR-ENG 1-2 PLENO +9,
ARG-SUI 3-1 +3; Σ CSV == board; 17 plenos; override +22 unchanged).

## SF1 — France vs Spain (Jul-14 19:00Z, lock 18:50Z) — THE RAZOR, NOW ON THE BOUNDARY
- Devig **FRA .4026 / D .2987 / ESP .2987** · p_over **.4797** · FULL120 argmax **1-0 (2.5619)** vs
  2-1 (2.5544) = **+0.0075 sub-noise**. 90' argmax 1-0, modal 1-1 → **COUNCIL FIRES (mandatory Jul-14
  ~18:00Z)**.
- **The decision IS the totals number: 2-1 takes argmax at p_over ≥ 0.49; the board sits at .4797.**
  It printed 2-1 yesterday at .500 and 1-0 today at .480 — the market is oscillating exactly on the
  crossover. Fresh T-1h p_over decides; f-band agrees (1-0 at f ≤ .65, 2-1 at f ≥ .85).
- Winner side: **0-1 (España) becomes argmax only if ESP devig ≥ .36** (a +6pp move / sides swapping
  favorite). Reachable on a bad France team-news day — the Jul-14 council must check news BOTH camps.
- Plenos tiebreak: P(exact@120') 1-0 = .1076 vs 2-1 = .1063 — razor there too; no tiebreak override
  either way. Drift grid 8/10 stable (only the two totals-up cells flip).
- **BIAS NODE (INVERTED — per handoff):** our España-champion leg + France-title-worst-world both pull
  TOWARD España picks. Guard: the engine is market-only and currently says FRANCE 1-0; entering an
  España scoreline against the argmax would be the tilt this time. L50: rooting ≠ lever.

## SF2 — England vs Argentina (Jul-15 19:00Z, lock 18:50Z) — FIRST BASELINE
- Devig **ENG .3729 / D .3215 / ARG .3056** · p_over **.4124** · FULL120 argmax **1-0 (2.5412)** vs
  2-1 (2.4317) and 0-1 (2.3605). Modal 1-1 → **COUNCIL FIRES Jul-15 ~18:00Z**. No prior baseline (this
  fetch is the baseline).
- **Tightest winner-boundary of the tournament: 0-1 (Argentina) takes argmax at just ARG +2pp**
  (H ≤ .35 / A ≥ .33). A morning-of line move flips the pick side — the Jul-15 T-1h fetch is decisive,
  and team news (Bellingham/Kane/Messi fitness) is a live engine input.
- Totals boundary far: 2-1 needs p_over ≥ .49 (live .412, deep Under lean). Plenos: 1-0 = .1207 top,
  0-1 = .1130, 2-1 = .1003.
- **Field-composition defused numerically**: even if 75% of this Chilean pool piles onto Argentina
  scorelines, our 1-0's edge over the field GROWS (+0.263 at q=0 → +0.270 at q=0.75) — the "everyone
  picks Messi" effect is not a reason to deviate in EITHER direction.

## Endgame / lead audit (`endgame_branches_sf.py`, real SF odds, MC seed 42, B4 + CONTROL PASS)
- Advancement (FULL120, pens 50/50): **FRA .543 / ESP .457 · ENG .521 / ARG .479** — two coin-flips.
- P(champion) (final pairwise ASSUMED ±10pp swept): **FRA .299 · ENG .246 · ESP .228 · ARG .227**.
- Branch table (chaser-minus-us locked-50 delta): **France title stays the worst world**
  (Gonzalo +16.7, Rodrigo +18.7, Greg +6.7) — but the gap-coverage line shows every chaser still needs
  **+18 to +34 MORE from a 4-game match layer** whose per-game drift is +0.27 in OUR favor (sd 3.2).
  **España title = best world** (every chaser ≤ +0.7, most strongly negative). England/Argentina titles
  mildly favorable — sole exception Gonzalo (+1.9 ENG / +0.5 ARG; his Olise leg pays in any branch),
  still ~3σ short and P(hold) = 1.000 in both.
- **P(hold #1 vs ALL top-5): FRA-title .998 · ESP 1.000 · ENG 1.000 · ARG 1.000.** No sweep
  (olise_else .30–.70, kane_mvp .15–.45, dibu_gk .30–.60, mbappé-boot ±.10, PAIR ±.10) flips any sign.
- Award refresh baked in (sourced Jul-12: ESPN/Fox/FIFA/NBC ×2-source): **Kane did NOT score — Bellingham
  braced (6==6) and owns the England Ball narrative → kane_mvp_if_eng haircut .55→.30** (swept; Greg's
  ENG-branch delta stays negative at both ends, so this hurts pride, not the hold). **Mbappé 8 == Messi 8**
  Boot tie (our shared Mbappé leg fine; felipe's Kane-boot leg cut to .20). **Maignan 4 CS vs Simón 5**
  (FRA-title Glove flip intact). **Olise 5 with every 4-assist chaser eliminated** → his no-France floor
  raised to .50 (Gonzalo's best asset; swept, no sign flip).

## Convergence count (final judge)
Seven independent layers, **zero divergences**: engine argmax (both SFs) == plenos-max == drift-grid
majority == lead-protection A1 (1-0 non-negative vs every rival entry in both games) == field-mixture
argmax at every q == joint two-game grid (no dominated pair) == endgame hold-floor ≥ .998 in all
branches. The two REAL open questions are market numbers, not model choices: **SF1 p_over vs .49** and
**SF2 ENG/ARG devig gap vs 2pp** — both resolve at their T-1h fetch.

## Verified vs ASSUMED ledger
- VERIFIED: board 377/rank1/gaps (screenshots + Σ CSV) · both SF devigs/dists (md6 snapshot, frozen
  engine) · advancement probs (FULL120) · QF results + scorers (≥2 sources each) · award standings
  (Boot 8/8/7/6/6, Olise 5, Simón 5/Maignan 4) · ownership table (Jun-28 observed) · tiebreak = plenos.
- ASSUMED (labeled + swept): final pairwise PAIR (±10pp) · award conditionals (kane_mvp .30, dibu .45,
  olise_else .50, mbappé-boot table) · field-entry mixtures (CHALK/CONTRA weights, q swept) ·
  match-layer proxy = SF2 dist for all 4 remaining games · pool scores 3rd-place game.
- Sensitivity verdict: NO assumption, at either sweep end, changes a hold-sign or an entry argmax.

## Protocol for the two councils (what fresh data decides)
1. **Jul-14 ~18:00Z FRA-ESP**: refetch → if p_over < .49 → 1-0 FRA; ≥ .49 → 2-1 FRA; ESP devig ≥ .36 →
   re-derive (0-1 territory). Team news both camps (≥2 sources); bias-guard statement (España stake —
   INVERTED direction); verdict → `council/outputs/fra_esp_sf/verdict.md`; final word ≥ T-30.
2. **Jul-15 ~18:00Z ENG-ARG**: refetch → if ENG-ARG devig gap < ~2pp or ARG ≥ .33 → 0-1 territory,
   re-derive; totals irrelevant unless p_over ≥ .49. Bellingham/Kane/Messi news = engine inputs.
3. Reopen triggers between now and then: a named-star OUT (Mbappé/Yamal/Bellingham/Kane/Messi) or a
   ≥3pp line move on a fresh snapshot = EV-UPDATE re-derivation (L35), never a tilt (L50).

— Drafted 2026-07-12 ~12:45Z from the 12:14Z snapshot. Harness artifacts + run outputs alongside this
file. Nothing entered today; next HITL action = Jul-14 council.
