# COUNCIL VERDICT — France vs Spain, WC-2026 SF1 (Jul-14 19:00Z, lock 18:50Z)

**ADVISORY (I-HITL — Sebas enters; nothing locked by the agent). Engine adjudicates EV (L44); lenses are
qualitative angles only. KO_SCORING = FULL120 (L57). CHAMPION NODE — bias guard INVERTED (see §Bias).**

## DECISION (on the 16:52Z board): **ENTER FRANCE 1-0.** Razor vs 2-1 France; a totals-driven margin call.
Fixture `f9aa13a662d1658e5a02cfc06d6a2d73`, snapshot `data/snapshots/md6_2026-07-14T16-52-55Z.json`
(fetched 16:52Z, quota 458, 2/2 == calendar, full-string bound, flipcheck HOLD, B4 byte-identical).

## Engine (frozen, market-only)
- Devig **FRA .3905 / D .2998 / ESP .3098** · total 2.5 · **p_over .4797** · μ_eff 2.593.
- 90' argmax **1-0** (2.289) · modal 1-1 · **FULL120 argmax 1-0 (E 2.5084)**.
- Candidates (FULL120): **1-0 = 2.5084** · 2-1 = 2.5020 (**gap +0.0064 = razor, both France-win**) ·
  0-1 = 2.2521 · 1-2 = 2.2434 · 2-0 = 2.202 · 1-1 = 1.541 (DEAD, L54) · 0-2 = 1.915.
- **COUNCIL FIRES** (weak-fav .390 < .55 AND EV-argmax 1-0 ≠ modal 1-1). Flip-check vs Jul-12 baseline:
  **HOLD, gap_base +0.0000** (fresh argmax == baseline).

## The decision variable (Sebas's framing: "account for variable change" = YES, as a policy not a point)
The pick is a **policy over the fresh totals number**, re-verified on live odds — the crossover did NOT drift:
- **p_over ≥ 0.49 → 2-1 France** · **p_over < 0.49 → 1-0 France.** Live p_over **.4797 → 1-0**, margin **+1.0pp**.
  (Boundary recomputed on the fresh board via `drift_fra_esp.py`: still exactly 0.49, same as Jul-12.)
- **ESP devig ≥ 0.34 → re-derive (0-1 España territory).** Live ESP .3098 → **+2.9pp away** (Jul-12 threshold
  was .36; it tightened to .34 as Spain firmed +1.1pp). The `FRA−4pp` drift cell already prints 0-1 — i.e. a
  ~4pp France softening (a CB-shock scenario) crosses the winner side.
- Drift stability **7/10** on 1-0: the 3 flips are `po+3.5`/`po+7` → 2-1 (totals up) and `FRA−4pp` → 0-1
  (Spain becomes co-favorite). Every flip is a NAMED, bounded move, not noise.
- Plenos tiebreak (we hold 17): **P(exact@120') 1-0 = .1056 > 2-1 .1047 > 0-1 .0960** → the argmax is ALSO
  the max-pleno entry. No divergence.

## Team news (sourced dossier, ≥2 sources; full citations in session log — ESPN/Al Jazeera/Yahoo/WST, Jul-13/14)
- **France**: **Tchouaméni RETURNS to midfield** (fully recovered; Koné → bench) = net POSITIVE, no star lost.
  **Mbappé AVAILABLE** (minor ankle from the QF; Deschamps "Kylian is fine", precautionary load-management).
  **Saliba + Upamecano** both missed Saturday training (managed back/foot; both **expected to start**) — the
  ONLY engine-relevant risk flag: if EITHER CB is scratched pre-KO, France softens and the winner side moves.
  Maignan/Olise/Dembélé fit. Predicted XI (4-2-3-1): Maignan; Koundé, Upamecano, Saliba, Digne; Tchouaméni,
  Rabiot; Dembélé, Olise, Doué; Mbappé.
- **Spain**: **fully available** — Yamal, Simón, Fabián Ruiz, Rodri, Merino (impact sub) all fit; **no QF
  suspensions**. Predicted XI: Simón; Porro, Cubarsí, Laporte, Cucurella; Rodri, Fabián Ruiz; Yamal, Olmo,
  Baena; Oyarzabal.
- **Official lineups**: NOT posted at fetch (expected ~17:45–18:00Z). **Sebas's T-40 refetch (~18:20Z) lands
  AFTER the sheets + after the odds absorb them** — so his fresh number is the decisive one.
- Verified-vs-assumed: no confirmed absentee either side as of 17:00Z → no engine-input event; France's 1.2pp
  softening since Jul-12 is market breathing, not a news event (would re-classify if a CB is ruled out).

## Lens panel — 4 ISOLATED subagents, blind to each other, reconciled by the judge (L44; engine adjudicates)
All four AGREE 1-0 France on the current board. ZERO dissent to a different pick today. Confidences and
catches:
- **Form/tactical (AGREE, MED)**: the counter-punch archetype fits — Mbappé/Dembélé behind Spain's high line
  is France's most repeatable route; both keepers elite → total mechanically compressed (μ_eff 2.59 is
  tactically honest); Tchouaméni's return stabilises the pivot vs Rodri/Fabián. Load-bearing risk: the two
  managed CBs — "if either is sub-100%, Yamal-Olmo find the crack → Spain 0-1 becomes live."
- **Market/historian (AGREE, MED)**: France's ML shortened −144→−155 on 79% PUBLIC money WHILE the devig
  SOFTENED −1.2pp and Spain firmed +1.1pp = a textbook **mild reverse-line-move — the sharp handle is on
  SPAIN.** The total is dead-flat with no steam → **nothing licenses shading p_over up; the .49 flip is
  safe, sharp flow is toward TIGHTER scores.** Base rate: elite ≤2.5-total KO → ~55-60% land a 1-goal
  decisive; 1-0-favourite ~16-18% modal, edging 2-1 ~12-14%; FULL120 disproportionately yields 1-0 (ET goals
  come single). Caution flag: Euro-2024 Spain beat France 2-1 in this exact node.
- **Chalk/leader-doctrine + BIAS GUARD (YES disciplined, HIGH)**: France 1-0 is the neutral-leader entry
  ("from 3rd place, no question"). The Spain-lean is a **PURE TILT** — costs −0.256 EV, and the hedge motive
  is neutralised because **P(hold #1 | France title) = .998**; the lead absorbs the worst world. A +28 lead
  at .998 hold is NOT a variance-reduction situation. Only-legitimate-Spain condition: **the engine itself
  flips (Spain devig ≥ .34)** — market signal only, no other trigger.
- **Adversarial/premortem (survives, MED)**: strongest attack = **a CB scratch crossing Spain to ≥ .34**
  (one starting-CB out ≈ +2-3pp opponent, both ≈ +4-5pp; live flip is +2.9pp away — resolved in ~60-90 min
  at the sheet drop). Secondary: a +1pp totals tick → 2-1 France (margin only, still France). Level-at-120
  tail (~.18-.22 survive to 120', France 1-0 scores 0 there) — real, unhedgeable, already net-priced.
  Refuted: Spain 1-2 / France 2-0 (dominated by >0.25), locked-champion correlation (known, doesn't move the
  argmax). "Would any flip the pick TODAY? Yes — one observable: a confirmed CB scratch."

**JUDGE RECONCILIATION.** Three independent lenses (market, adversarial, form) converge on ONE hinge that a
single synthesizer would under-weight: **the live axis is the winner side (Spain firming via the CB
question), NOT the totals.** The market is already leaning that way (sharp handle on Spain, Spain +1.1pp).
The disciplined response is NOT a pre-emptive Spain hedge (bias-guard: pure tilt, HIGH) — it is the T-40
re-derive: hold France 1-0 unless the ENGINE flips (ESP ≥ .34) on a confirmed CB scratch, at which point
engine and España-instinct CONVERGE. The 2-1 branch is minor and sharp-flow-disfavoured. Nothing dissents;
the council STRENGTHENS 1-0 France while correctly relocating the watch from p_over to the ESP-devig/CB axis.

## Field / lead layer (`lead_max_sf.py` fresh, CONTROL == committed +0.1084, B4 PASS)
- **1-0 France beats the field at every contrarian-q**: +0.2415 (q=0) → +0.2754 (q=.50); 1-0 > 2-1 > 0-1
  throughout. The ownership-optimal pick == the engine argmax. No tension.
- Advancement (FULL120, pens 50/50): **P(France adv) = .5306** (softened from .5432 Jul-12; still favorite).
- Endgame (`endgame_branches_sf.py` fresh, MC seed 42): **P(hold #1 vs ALL top-5) = .998 (FRA title) /
  1.000 (ESP·ENG·ARG)** — UNCHANGED from Jul-12 (gaps static, no games played). P(champ) FRA .292 / ENG .243 /
  ESP .235 / ARG .230 (pack tightened as France softened). **España title = our best world, France = worst** —
  but the lead absorbs the worst world; no match-layer deviation improves it (L50 verified numerically).

## Bias statement (INVERTED node — explicit, per mandate)
Our locked champion = **España**, and **France-title = our single worst world** (3 chasers hold Francia).
Both stakes pull TOWARD entering a Spain scoreline (0-1). The engine — market-only, frozen, blind to our
locked-50 — produced **1-0 France** as argmax, max-pleno, and ownership-optimal. The pick survives removal of
BOTH stakes (it is the neutral-leader entry). Entering 0-1 Spain here would (a) cost −0.256 EV vs the argmax,
(b) be a root-for-España tilt (L50: rooting ≠ betting), and (c) be UNNECESSARY — we hold #1 with p .998 even
in the France-title branch. The only path to a legitimate Spain entry is the ENGINE flipping (ESP devig ≥ .34
on a France CB shock), at which point instinct and engine agree.

## Reopen triggers (T-40 sheet protocol — ONLY these; all else = priced noise)
1. **Mbappé OUT** → France's ceiling collapses, re-fetch, re-derive (likely toward 0-1/lower total).
2. **Simón OUT** (Spain keeper) → Spain softens, France firms — 1-0/2-1 stays, possibly firmer.
3. **Saliba AND Upamecano BOTH out** → France softens toward the A≥.34 winner-flip → re-derive (0-1 Spain).
4. **Maignan OUT** → France softens; re-fetch.
5. **p_over crosses 0.49** on the fresh number → **2-1 France** (still France; margin only).
6. **ESP devig ≥ 0.34** → re-derive (0-1 España — engine and instinct converge here).
NEVER 1-1 (dead −0.97). NEVER a Spain scoreline as a "hedge" against our own champion pick while France is
the engine favorite (that is the inverted-bias tilt this verdict exists to prevent).

## FINAL WORD (delivered ~17:25Z, T-1h35, post 4-lens council): **ENTER FRANCE 1-0 on the current board.**
At Sebas's T-40 refetch (~18:20Z, post-lineups), in priority order the council RELOCATED the watch to:
1. **ESP devig ≥ .34 (the LIVE axis — sharp flow + CB question point here) → re-derive: 0-1 Spain.**
   Trigger = a confirmed Saliba/Upamecano scratch at the sheet drop; live +2.9pp away. Here engine and
   España-instinct converge — the only legitimate Spain entry.
2. **p_over ≥ .49 → 2-1 France** (margin only, still France; sharp flow disfavours this — minor branch).
3. Else (today's state) **→ 1-0 France.**
Convergence: 4/4 isolated lenses AGREE (bias-guard HIGH, others MED) == engine argmax == max-P(exact/plenos)
== ownership-optimal at every q == flip-check HOLD. NEVER a pre-emptive Spain hedge (pure tilt, −0.256 EV,
unnecessary at P(hold #1)=.998). Zero divergent signals above noise; the council STRENGTHENED the pick and
correctly moved the watch from totals to the winner-side/CB axis.

— Drafted ~17:10Z from the 16:52Z snapshot. Lock 18:50Z. I-HITL: Sebas enters/keeps the pick at his T-40.
