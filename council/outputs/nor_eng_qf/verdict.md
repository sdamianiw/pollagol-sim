# COUNCIL VERDICT — Norway vs England, WC-2026 QF3 (Jul-11 21:00Z, lock 20:50Z)

**ADVISORY (I-HITL — Sebas enters; nothing locked by the agent). Engine adjudicates EV (L44); lenses are
qualitative angles only. KO_SCORING = FULL120 (L57).**

## DECISION: **KEEP / CONFIRM ENGLAND 1-2** (already registered in-app) — DECISIVE, not razor.

Fixture `e66e4478b739fa0657a7a11235e1fcee`, snapshot `data/snapshots/md5_2026-07-11T19-03-03Z.json`
(fetched 19:03Z, quota 464, 3/3 F27 in-window==calendar, B4 byte-identical).

## Engine (frozen, market-only)
- Devig **NOR .2469 / D .2469 / ENG .5063** · total 2.5 · **p_over .5723** · μ_eff 2.980.
- 90' argmax **1-2** (2.638) · modal 1-1 · **FULL120 argmax 1-2 (E 2.9450)**, argmax at EVERY f.
- Candidates (FULL120): **1-2 = 2.945** · 0-1 = 2.837 (**gap +0.108 ≈ 3.6× razor**) · 0-2 = 2.690 ·
  2-1(NOR) = 1.792 · 1-1 = 1.346 (DEAD, L54) · 1-0(NOR) = 1.743 · 2-0(NOR) = 1.444.
- Flip-check vs Jul-10 baseline: **HOLD, gap_base +0.0000** (fresh argmax == baseline == registered).

## Drift harness (`drift_nor_eng.py`, CONTROL==LIVE exact 0.00e+00, B4 PASS)
- **10/10 stable on 1-2** across ENG±4pp / DRAW±2pp / totals±7pp.
- **Flip boundary: 0-1 becomes argmax only below p_over 0.51** — live .572 and 84-87% of totals money is
  pushing OVER (−115→−140): the market is moving AWAY from the only realistic flip. At po −7pp (0.502)
  the gap is still +0.0035 to 1-2.
- **No Norway scoreline is ever argmax until NOR ≥ .40 devig** (+15pp; a pre-KO impossibility short of a
  Kane+Bellingham-out shock).
- Plenos tiebreak (pool tiebreak = most exact scores; we hold 16): **P(exact@120') 1-2 = .1158** >
  0-1 = .0966 > 0-2 = .0823 > 2-1 = .0783 → the argmax is ALSO the max-pleno entry. No divergence.

## Team news (sourced dossier, ≥2 sources unless flagged; full citations in session log)
- **England**: Henderson OUT (wrist fracture, tournament over — Sky/Fox/Yahoo). Quansah SUSPENDED.
  **Rice** — the illness case (sickness bug + managed hamstring/neural issue): missed Wed-Thu, **returned
  FULL training Friday** (Sky Jul-11 00:01Z + Reuters/Yahoo 01:42Z); Tuchel: "everyone available except
  Quansah". **Guehi** — hamstring strain from R16, trained Friday, **genuinely 50/50 to start** (Burn on
  standby; predicted XIs split). James returns at RB. Kane "shape of his life" (Tuchel), 6 WC goals.
- **Norway**: camp virus CONFIRMED historical (Strand Larsen fever, Pedersen ill vs Brazil) but **team
  doctor Jul-9: "all players healthy now"**; the Ødegaard-ill report is single-source (Daily Cannon) and
  REFUTED by manager+doctor. Haaland fit, 7 WC goals. No official absentees.
- **Verified-vs-assumed**: both-camps-virus = VERIFIED but RESOLVED (Norway cleared; Rice trained).
  The user's "two England starters questionable" = **Rice + Guehi, VERIFIED**; Rice PROBABLE-starts,
  Guehi UNCERTAIN. Neither is OUT as of 19:45Z. → No engine-input event pre-lineups; odds already
  absorbed the week (England SHORTENED on advance −195→−215 through the news).

## Lens panel (isolated; all four independently converged)
- **Form/tactical**: BTTS-England-win (1-2 family) STRONGLY SUPPORTED — Guehi/Burn left-CB channel vs
  Haaland/Sørloth is the leak; Norway scored 2 on Brazil's similar template; clean sheet needs Rice at
  full intensity AND Guehi fit AND Norway misfiring simultaneously. Rank: 1-2 > draw > 0-1/0-2 > NOR win.
- **Market/historian**: Over money 84-87% tickets AND money (−115→−140) = sharp-aligned "goals, plural";
  elite-striker underdogs at ~.25 score in ~55-65% of such KOs (medium confidence); BTTS base rate ≥70%
  here (the 7/10 elite-Euro coin-flip KO count = Jul-10 session artifact, recorded in `tasks/HANDOFF.md`
  Jul-10 block / `memory` pollagol-state; that count was at ~2.0 totals — this board is 2.5 Over-leaning). The Southgate 1-0-grind prior
  is stale — the market total explicitly prices against it. Rank: 1-2 > draw > NOR win > 0-1/0-2.
- **Chalk/leader-doctrine + BIAS GUARD (the Kane node)**: **AUDIT PASS** — 1-2 is what a neutral leader
  with no Kane stake enters (argmax by +0.108, max-pleno, 10/10 drift); blocking/anti-correlation logic is
  NULL (picks hidden); deviating from argmax while +29 up is the only way to leak EV. 1-1 forbidden (L54).
  "Would we enter 1-2 from 3rd place?" — yes: it's the argmax regardless of standing.
- **Adversarial/premortem**: see addendum below (zero-tail + reopen triggers).

## Field/lead layer (`lead_max_scenarios.py`, exact enumeration, CONTROL==committed ESP-BEL, B4 PASS)
- **1-2 beats EVERY plausible rival entry in E[diff]**: vs 0-1 +0.108, vs 0-2 +0.255, vs 1-1 +1.599,
  vs 2-1(NOR) +1.153, vs 1-0(NOR) +1.202, vs 2-2 +1.788. No dominated direction.
- **Field-mixture sweep** (chalk-modal field vs contrarian NOR-side fraction q — chasers variance-hunting):
  1-2's edge over the field GROWS with q (+0.243 at q=0 → +0.752 at q=0.5) and stays #1 among our
  candidates at every q. **"They expect me on England" changes nothing: picks are hidden, and even if the
  field tilts Norway, 1-2 profits MORE.**
- **Joint (1-2, 1-0) two-game grid**: positive E vs every rival pair; P(net lose ≥6) ≤ .092 vs any pair.
- Advancement (engine, pens 50/50): **P(England adv) = .639** (market ~.65 ✓) · P(Argentina adv) = .711.

## Reopen triggers (T-75 lineup protocol — ONLY these reopen the pick; all else = noise)
1. **Kane OUT** of the XI → reopen (England's goal engine + our exact-shape anchor). Direction: 0-1.
2. **Haaland OUT** (adversarial lens addition) → Norway's goal threat collapses, p_over drops → re-fetch;
   direction: 0-1. Currently fit per doctor+manager; the name to watch on the sheet.
3. **Rice AND Guehi BOTH out** → reopen toward MORE Norway goals (1-2 → check 2-2/2-1 sensitivity via
   drift grid; note NOR-side never argmax until +15pp, so realistically 1-2 stands unless odds crater).
4. Odds move ≥3pp on ENG devig or p_over crosses **0.51** downward on a fresh fetch → re-run `ko`, enter
   the fresh FULL120 argmax (EV-UPDATE, L35).
Single-name absences other than Kane (incl. Guehi alone → Burn) are PRICED: the market watched this all
week and shortened England anyway. NEVER 1-1 (dead −1.60), NEVER a Norway scoreline as a "hedge" (−1.15+
EV give-up = pure tilt, L50).

## ADVERSARIAL ADDENDUM (lens attack → judge ruling on numbers)
- **Vector 1 (zero-tail)**: 1-2's zero-tail is modestly fatter than 0-1's (0-0@120' pens path: 0-1 floors
  +1, 1-2 floors 0; NOR 2-1: 0-1 gets +1, 1-2 gets 0). TRUE and already NET-PRICED inside the engine's
  E-gap (+0.108 to 1-2 despite those cells) and the harness P(lose)=.327. Not a flip argument.
- **Vector 2 (illness → chaos)**: England degradation routes toward NOR 2-1/2-2, not toward 0-1. TRUE
  directionally — but the drift grid shows no NOR scoreline is argmax until NOR +15pp; a 3-5pp tail-add
  doesn't reach it. Margin drag, not a flip.
- **Vector 3 (public-bias haircut on p_over) — THE ONLY ENTRY-THREATENING ATTACK. RULING: REFUTED.**
  The lens's own settling test is the line's direction vs the tickets: the Over price moved **-115→-140
  at the same 2.5 number** (implied UP ~5pp WITH the public), **money% ≈ tickets% (84-87% both)** — the
  square signature is tickets≫money, absent here — and our snapshot devig series rose **.479 → .553 →
  .5723** over 48h. That is sharp-confirmed steam (World A), not a reverse line move (World B). No
  haircut is licensed; the .062 buffer above the .51 flip boundary stands. (Had the price held or drifted
  Under against the tickets, we would have haircut and re-swept — registered as the standing test.)
- **Vector 4 (lineup triggers)**: adopted into the reopen list — **Haaland OUT added** (collapses p_over
  → re-fetch, likely flips 0-1). Guehi-vs-Burn confirmed NOISE (priced all week).
- **Vector 5 (ET decomposition)**: ET FAVORS 1-2 (England mild favorite to score next from 1-1; the
  1-1→ENG-ET-goal path lands EXACTLY 1-2 = pleno 9 — same mechanism that paid ESP-BEL 2-1). Lens agrees;
  two rubric slips in its illustrative table corrected by the engine's `points()` (0-1 vs actual 0-2 = 4
  not 3; the 1-1@120' pens branch scores BOTH picks 1, per the SUI-COL 0-0-pens precedent — outcome
  category pays the 120' DRAW, not the pens winner).

## Bias statement (explicit, per user mandate)
Our locked MVP = Kane (sole holder). England advancing helps our endgame → the stake pulls TOWARD England
picks. The pick survives removal of the stake: the engine (market-only, frozen, no knowledge of our
locked-50) produced 1-2 as argmax at every f, every drift cell, and max-P(exact). The council's job was to
try to break 1-2, not to confirm it; the only lens instructed to attack it (adversarial) had its numeric
challenges resolved by engine sweeps (boundaries above). No step deviated from the market-only path.

## T-75 lineup check (executed ~19:05-19:15Z — ahead of the sheets; re-glance at ~19:45Z)
Official sheets NOT yet posted at fetch time (FIFA/FA match centres = placeholder). Best post-presser
intel: **Guehi expected to START** (Tuchel 09:34 BST: "everyone available in training"; Burn = fallback
only), Rice expected, Kane/Saka/Bellingham in; Norway: Haaland + Ødegaard certain, no surprise absences.
England ML SHORTENED further (−105→−110), Over 2.5 held −140. **No reopen trigger fired.** Residual
instruction to Sebas: glance at the official sheet before 20:50Z — reopen ONLY on trigger 1/2 (Kane OUT
or Haaland OUT); Guehi→Burn = noise, priced.

## FINAL WORD (delivered ~19:15Z, T-95): **CONFIRM the registered ENGLAND 1-2. No change.**
Convergence: engine argmax (every f, 10/10 drift) == max-P(exact/plenos) == all 4 lenses' #1 shape ==
lead-protection argmax vs every rival entry and every contrarian-q mixture == market-modal direction.
Zero divergent signals above noise. The only attack that could have flipped the entry (public-bias
haircut on p_over) was refuted by the observed line direction (price moved WITH tickets, money aligned).

— Verdict drafted ~19:05Z; finalized ~19:15Z. Lock 20:50Z. I-HITL: Sebas enters/keeps the pick.
— Official-sheet glance at ~19:45Z remains on Sebas (or ask for a re-check): reopen ONLY on Kane/Haaland OUT.
