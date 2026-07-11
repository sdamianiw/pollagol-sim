# LEAD-MAXIMIZATION SCENARIO VERDICT — QF day-3 (2026-07-11, board: us 365, +29/+30/+36/+37/+39)

**ADVISORY. Harnesses: `lead_max_scenarios.py` (exact enumeration, CONTROL==committed ESP-BEL, B4 PASS) +
`endgame_branches.py` (deterministic branch table + seeded MC 200k, B4 PASS). Objective = E[prize] under
60/20/10 with tiebreak = most plenos (we hold 16).**

## Headline (judge's consensus after convergence checks)
1. **The lead is near-locked if we keep entering the argmax: P(hold #1 vs ALL top-5) ≥ 0.998 in EVERY
   champion branch — including France title.** The chaser who closes 29+ needs a ~3.2σ six-game run ON
   TOP of the best locked-50 branch. The match layer is OUR weapon, not theirs (+0.24 to +0.75 E[gap]
   per game vs the field, growing if they variance-hunt).
2. **France title is the single worst world, and it is 3-of-5 common-mode**: Gonzalo +16.2 and Rodrigo
   +19.2 expected locked-50 recovery (champion + Olise/Maignan/Mbappé-MVP legs), Greg +6.2, Lucas +4.5,
   felipe +7.3. Even so, none closes the CURRENT gap on locked-50 alone (max +19.2 vs gap +39).
3. **Best worlds ranked: England title (Kane MVP = ours alone) > Argentina (Dibu; felipe common-mode) >
   España (+10 us, cancels Greg, buries Lucas/felipe/Rodrigo at −10 to −11) > NOR/SUI chaos > France.**
   Extends the Jul-9 table (3 chasers) to 5: confirms England-title-best and France-title-worst, and adds
   that felipe's Kane-SCORER leg makes an England title slightly less lopsided vs him (+0.35·10 Kane boot).
4. **Tonight changes nothing you control and one thing you can't**: the entry (1-2) is lead-optimal vs
   every rival entry (Bucket A) — but the OUTCOME England-advance (P .639) prunes P(France title) via the
   final matchup and keeps our best world (ENG title, P .164) alive. Rooting = England; entry = already
   optimal; no lever moves (L50 verified with numbers, not assumed).

## Bucket A — tonight's match layer (exact, VERIFIED)
- 1-2 vs rival entries E[diff]: +0.108 (0-1) · +0.255 (0-2) · +1.599 (1-1) · +1.153 (2-1 NOR) ·
  +1.202 (1-0 NOR) · +1.788 (2-2). Positive against ALL.
- Field mixture (contrarian q swept 0/.25/.50): 1-2 E[edge] +0.243 → +0.498 → +0.752, #1 at every q.
  **The "they expect me on England (Kane)" variable is defused twice over: picks are hidden (no reaction
  channel), and if chasers DO tilt Norway our edge grows.**
- Joint (1-2, 1-0): positive E vs every rival pair; P(net lose ≥6) ≤ .092 worst pair.
- Advancement (engine): P(ENG adv) .639 · P(ARG adv) .711 — both == market to-advance within ~1pp.

## Bucket B — endgame branches (deterministic + MC; assumptions LABELED)
P(champion) via chain (tonight VERIFIED, SF2/final pairwise ASSUMED ±10pp swept):
**FRA .317 [.264–.371] > ESP .241 > ARG .180 > ENG .164 > NOR .064 > SUI .033.**
Branch table + gap coverage + P(hold #1) tables: see `endgame_branches.py` output (committed run).
Sweeps: Olise-frozen prob .15→.55 moves Gonzalo's ESP-branch delta −8.8→−4.8 (never sign-flips);
Kane-MVP-if-ENG .35→.75 moves Greg's ENG-branch delta −2.6→−6.6 (never sign-flips). Conclusions robust.

## Verified vs ASSUMED ledger
| Item | Status |
|---|---|
| Board 365 / gaps +29..+39 | VERIFIED (screenshots 18:42Z, cross-footed, == CSV cumulative) |
| Locked-50 ownership top-10 | VERIFIED-OBSERVED (Jun-28 screenshots via `pool/locked_ownership_2026-06-28.md`) |
| Tonight + SF1 win probs | VERIFIED (frozen engine on 19:03Z snapshot; == market within 1pp) |
| Rubric / tiebreak=plenos | VERIFIED (`memory/rules.md` + Sebas in-app Jul-10) |
| SF2/final pairwise probs | ASSUMED (labeled, ±10pp sweep — champion ORDER stable, FRA .26–.37) |
| Award-leg conditionals | ASSUMED (labeled; two most sensitive swept, no sign-flips) |
| Field-entry mixture weights | ASSUMED (chalk-field anchor; q swept 0–.50, ordering invariant) |
| Match-layer proxy for future games | ASSUMED (tonight's dist reused; conservative — chaser tilting raises our edge) |
| 3rd-place game scored by pool | ASSUMED (pool has scored every KO game; if absent, variance shrinks → helps us hold) |

## Failure modes registered
- F-A: a chaser mirrors our entries game-for-game → gap frozen at +29 → we win on the current lead.
- F-B: France title (P ~.32) → worst world but P(hold) still .998; the real damage is prize-share risk
  ONLY if combined with a chaser pleno run (3.2σ). Not actionable tonight; re-run after each round.
- F-C: assumption drift — SF2/final pairwise probs replaceable with REAL odds after tonight (re-run then).
- F-D: our own tilt = the one lever that CAN lose this (L50). The sim's loudest message.

## Convergence count (scenarios reconciled)
6 champion branches × 5 chasers × {branch table, per-chaser MC, joint MC, sweeps ×4, pairwise ±10pp} all
reconcile to the same two conclusions (hold ≥.998; France-title worst). Bucket A (3 harness views: single,
mixture, joint) reconciles with the ESP-BEL precedent and the council verdict. **Zero divergent cells.**
