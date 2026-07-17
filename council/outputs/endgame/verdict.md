# ENDGAME COUNCIL VERDICT — 3rd-place (FRA-ENG, Jul-18 21:00Z) + FINAL (ESP-ARG, Jul-19 19:00Z)

**Written 2026-07-17 ~13:4xZ · ADVISORY / I-HITL (Sebas enters) · engine FROZEN · KO = FULL120 pens
excluded (L57) · snapshot `md7_2026-07-17T10-48-15Z.json` (quota 452, 2/2 == calendar, L49 full-string
binds) · harness `greg_endgame.py` EXACT convolution, MC cross-validated 5/5 within 3×SE (L62 rule),
B4 ×3 identical, pytest 269/269.**

## VERDICTS (preliminary today; BINDING at each game's own T-1h)
- **3rd-place Jul-18: ENTER FRANCE 2-1** — engine FULL120 argmax (E 2.854) AND P(hold)-argmax
  (0.217% loss risk vs 0.226% for 1-0; England-side ~doubles it). Unanimous 4/4 lenses.
- **FINAL Jul-19: ENTER SPAIN 1-0** — engine FULL120 argmax (E 2.728) AND P(hold)-argmax for every
  realistic read of Greg. **The cover (0-1 ARG) does NOT fire at +24** — see the q-analysis below.
  Unanimous 4/4 lenses + the Greg role-play's own math.
- NEVER 1-1 (dominated, L54). I-HITL: Sebas types both entries at his refetch.

## Board state (recorded today, cross-foot ✓)
SF2 ENG 1-2 ARG recorded (×6 sources, 90'+stoppage no ET): pick 1-0 (engine track) = 1, **entered 1-2 =
PLENO +9** (Greg also plenoed) → **us 386 / Greg 362, gap +24 UNCHANGED**, n=102, 18 plenos (Greg ~14-16
→ WE WIN TIES), override +30 (ledger reconciled: EV-UPD +3 cover-direction / TILT +5 exact-score), 3rd
place felipe/Gonzalo 342 (+44, deterministic floor ~0.0003 — dead).

## The structural fact that reshapes everything (vs SF2)
**Max match-layer swing = 9+9 = 18 < 24 (< 25 counting our pleno tiebreak): Greg CANNOT pass on match
points — award parlays are MANDATORY.** Champion-España and Mbappé-Boot are common-mode (cancel). His
live legs: **Messi-assister** (4 vs Olise 5, plays the final — in 100% of top loss paths) + Yamal-MVP
(market ~3-6%) + Maignan (~1%). Ours: Dibu-GK (~35% if ARG champ) + Kane (~1%, dead). The final's result
region IS the champion (no PAIR assumption left).

## Harness decision tables (exact; full run `greg_endgame_run_2026-07-17.txt`)
- **[A] FINAL at gap +24, P(pass+tie) by q = P(Greg ARG-side):** chalk 1-0 best for q ≤ **0.81**
  (crossover corrected per adversarial lens; was loosely "~0.85"); cover 0-1 best above, buying at most
  **10bp at q=1.0**. **STRICT-pass (our true metric — ties are wins, plenos 18):** cover's ceiling falls
  to **+2–3bp at q=1.0 in EVERY stressed award scenario** (joint q×{messi .55, yamal .12, dibu .20}
  sweep — closes the adversarial lens's scope gap). Chalk 1-0's risk FALLS as q rises (his ARG entry is
  anti-correlated with our Spain chalk).
- **[B] 3rd place:** FRA 2-1 → 0.217% (best), 1-0 → 0.226%, 2-0 → 0.246%, ENG-side 0.37–0.41%.
- **[C] chalk-chalk autopsy:** P(pass strict)=0.136%, P(tie)=0.083% → **P(hold) = 99.86% true /
  99.78% conservative**. Top path (32%): **ESP-champ × Yamal-MVP × Messi-AST** — his parlay pays even in
  our best world; Dibu never protects there. ALL top-10 paths contain Messi-AST.
- **[D] adversarial (Greg pure best-response):** worst-case vs (2-1, 1-0) = 0.501%; minimax (1-0, 1-0)
  = 0.465%. **3.6bp of insurance for ~9bp behavioral cost (2.5:1 against) → stay behavioral-best 2-1.**
  Greg's computed best responses: g1 = 1-2 ENG, g2 = **2-1 ESP** (see role-play convergence below).
- **[E] FINAL lookup by realized gap after Jul-18:** chalk 1-0 best at +22 (0.17%) and +24 (0.13%);
  +20 → 0.70%; +18 → ~1.9%; +15 → ~3.1% — cover never argmin at default q even at +15.
- **[F] sweeps:** argmin stable at q=.5 across yamal .03–.12 / messi .10–.55 / dibu .20–.45 / pens
  .30–.70; joint high-q × award sweep run separately (see [A] strict result).

## THE READ — "will Greg stay Spain or flip to Argentina?" (the user's tight call)
**Answer: it does not matter for our entry — and his own math says Spain anyway.**
1. **q-insensitivity (the load-bearing result):** under the strict-pass metric the cover buys ≤ 2–3bp
   at ANY q ∈ [0,1] under EVERY stressed award scenario. There is no value of the Greg-read that flips
   our final entry at +24. The SF2 42bp existed because 3 games remained (27 max swing > 24 = live
   match-layer threat that mirroring neutralized); with 18 < 24 that channel is EXTINCT and award legs
   are score-independent — mirroring neutralizes nothing that matters (game-theory lens).
2. **Rational-Greg goes SPAIN-side (role-play, independent):** an ARG title triggers our Dibu (+10 us),
   canceling his Messi-AST → his ARG-title branch needs >24 match swing = impossible. **His ONLY viable
   universe is a Spain title** (our award slate all-dead there, his Yamal+Messi live) → he must harvest
   match points in Spain-wins worlds → his optimal entry is a SPAIN score differentiated from ours
   (**Spain 2-1**), plus contrarian **England 1-2** for variance. Self-assessed P(#1) ≈ 1%. This EXACTLY
   matches the harness's computed pure best-responses in [D] — two independent derivations, same answer.
3. **Behavioral estimates split but converge:** bias-hygiene q ≈ 0.20 (champion-lock anchor; SF2 was a
   different incentive state) vs game-theory q ≈ 0.90 (fandom + revealed SF2 behavior + accepts lock
   dissonance). The split is irrelevant — same pick either way. Role-play's Dibu|ARG ≈ .60 (vs our .35)
   would only shrink the ARG-branch loss paths further → strengthens chalk.

## Council reconciliation (4 isolated lenses + role-play + judge)
| Lens | 3rd place | Final | Conf | Core |
|---|---|---|---|---|
| Form/market/news | FRA 2-1 | ESP 1-0 | MED-HIGH / MED | Saliba OUT, FRA line firmed +105→-115; bronze avg 3.80 goals, Mbappé needs 2+ (Messi holds assist tiebreak) → 2-1 shape; Spain 1-conceded, score-once-and-control → 1-0; Yamal AND Porro officially doubtful (Sat presser = T-24h event) |
| Game-theory/covering | FRA 2-1 | ESP 1-0 | HIGH | Channel extinction (18<24); cover ≤5bp even at his q=.90; minimax not worth 2.5:1; strict metric correct → P(hold) 99.86% |
| Adversarial | (claims 2-4 survive) | crossover q*=0.81 not .85 | — | Harness sound: gap arithmetic verified, MC 5/5, award independence & Olise-coupling biases both CONSERVATIVE (overstate risk); decision hinges on q ONLY in the tie-as-loss convention (superseded by strict metric) |
| Bias-hygiene | FRA 2-1 | ESP 1-0 | HIGH | q ≈ 0.20 [.08-.32]; loudest bias = DOCTRINE INERTIA (SF2's cover doesn't generalize); guru consensus = tautology (same market the engine prices); boring answer is correct |
**JUDGE: UNANIMOUS chalk-chalk — FRANCE 2-1 + SPAIN 1-0.** For the first council this tournament there
is no dissent to adjudicate: the engine EV-argmax, the P(hold)-argmax, the minimax-adjacent behavioral
best, all four lenses, the pundit consensus (weightless but aligned), Sebas's own France lean, and
rational-Greg's implied fear (a leader who enters the modal Spain score blocks his exact-2-1 kill-shot
path at the pleno cell) all point at the same two entries. The SF2 cover doctrine is preserved and
CORRECTLY NOT FIRING: its trigger (a live, mirrorable match-layer threat) no longer exists.

## T-1h ENTER rules (numeric; re-run `greg_endgame.py <fresh-snap>` + `ko` at each node)
**Jul-18 ~20:00Z (lock 20:50Z) — 3rd place:**
- Default **FRANCE 2-1**. p_over ≥ .52 → evaluate 3-1 FRA vs 2-1 (re-run ko). ENG devig ≥ .30 (ML < +240)
  → re-derive (England-side may go live). Mbappé confirmed OUT → drop to 1-0 FRA (re-run ko). Else 2-1.
**Jul-19 ~18:00Z (lock 18:50Z) — FINAL (re-run at REALIZED gap):**
- Default **SPAIN 1-0**. p_over ≥ .50 → 2-1 ESP competes (re-run ko). ARG devig ≥ .33 (engine winner-flip
  boundary) → re-derive; ARG ≥ .38 + credible Greg-ARG signal → re-run cover harness with fresh numbers.
  Yamal AND Porro both OUT → 0-0 mass rises; re-run ko before locking 1-0.
- **COVER (0-1 ARG) fires ONLY if ALL THREE hold (game-theory gate):** realized gap ≤ +20 AND hard
  q-evidence ≥ 0.9 (his stated/observed pick) AND Messi-AST still live (Olise adds 0 assists Jul-18 —
  if Olise reaches 6+, Messi needs 3+ in one final → his dominant leg ~dies and with it the threat).
  At the current +24 the gate CANNOT open (gap condition already fails).

## What must happen for Greg (kill-shot map, for the record)
~95% of his ~1% lives in SPAIN-TITLE worlds: (A) Yamal-MVP × Messi-AST parlay + any small match edge
(0.35%); (B) one award + near-perfect match sweep (~0.5%). ARG-title branch ≈ dead (Dibu cancels).
Watch Jul-18 for: Olise assists (kills/keeps Messi-AST), Mbappé Boot goals (common-mode, cosmetic).

## Code-review gate (post-verdict hardening, same session)
6 findings from the isolated review agent, all verified then applied surgically; ZERO number changes:
candidate set extended with draws (1-1/0-0 NEVER argmin at any q — 0.108–0.423%, dominated, so the
argmin claims are now complete, not just believed); adversarial sets extended with long-shots (3-0/0-3/
2-2/0-0 — every worst case and Greg best-response byte-identical); `joint()` gap parameterized (removes
the latent global-GAP trap for the Jul-19 realized-gap re-run); MC `rng.choice` p-vector normalized
(robustness); LEV award-mass assert added; [F] sweep hoisted (90→8 convolutions). Post-fix: B4 ×3 one
hash, MC cross-val 5/5 in 3×SE, hand-checks PASS. L62 grep clean; I-3 clean (review-verified read-only).

## ADDENDUM (same day, ~15:3xZ) — TWO-FRONT GREG: seed-2 defense vs #1 hunt (Sebas's follow-up angle)
**Question:** does Greg "risk it" with England, and what does it cost him against HIS chasers (felipe/
Gonzalo 342 = −20, Lucas 339, Rodrigo 327 — ALL with dead champion legs)? **Harness:**
`greg_two_front.py` (joint MC N=1M seed 42 over the top-6, REAL 2026-06-28 ownership slates, prize
.60/.20/.10; pairwise cross-val vs the exact convolution 3/3 in 3×SE; B4; verified by a 2-agent
metacognitive+adversarial panel — both SURVIVES — plus an independent seed-7 replication).
**Slate structure (the analytical core):** Yamal-MVP is COMMON to Greg+Gonzalo+felipe → useless for his
seed-2 defense; the ASSISTER award is the two-front pivot (Messi→Greg+10 vs everyone / OLISE→Gonzalo+10
vs Greg); Dibu-GK (us+felipe) fires only in ARG-title worlds → an Argentina title hurts Greg on BOTH
fronts; and **his España champion lock walls off seed-2 in ALL Spain-title worlds** (V2's exact
decomposition: chaser max bridge 9+9+10=28 < the 30-pt barrier → P(drop to 3rd)=0 there; his entire
chaser risk lives in ARG-title worlds).
**Greg strategy table (P1 / P2 / P3 / E[pot-share]; ties-to-chasers conservative):** chalk-chalk .009/
99.43/0.55/.1995 · **ENG-gamble alone .110/98.42/1.44/.1989 = his WORST** (P3 triples: France wins ~.56
and Gonzalo's Olise-AST path opens — V2 tail audit: 93% of those losses are FRA-win worlds, Gonzalo 73%
of passers) · ARG-fandom .077/99.79/0.13/.2002 (the ARG-side final entry is a seed-2 HEDGE: harvests a
pleno exactly in the Dibu-firing worlds, P3 ÷4, mechanism exactly derived + seed-stable) · **ENG+ARG
double .393/99.27/0.33/.2012 = his E-max**. Whole spread = **23bp of pot = 1,863 CLP** — his choice is
economically near-irrelevant; the P2 fortress (~99%) dominates everything.
**RECONCILIATION vs the main verdict (does chalk-chalk hold? YES — strengthened):**
1. The E[prize]-rational Greg tilts to the DOUBLE differential (ENG 1-2 + **ARG 0-1** — the two-front
   frame flips his rational final entry ARG-side, unlike the P(#1)-only role-play's Spain-2-1). His
   P(pass us) under that E-max strategy = **0.393% — inside the adversarial ceiling (0.501%) our [D]
   already priced**, and our chalk 1-0 remains the argmin vs ARG-side Greg (that's the q-insensitivity
   result: cover ≤2-3bp strict at any q). Correction of an earlier framing (V1 audit): rational Greg
   does NOT necessarily avoid the England leg — he avoids it ALONE (S3 worst) but pairs it in his E-max;
   either way Q3_ENG mis-estimates are bounded by [D] and change nothing.
2. Sebas's headline question answered: **the England gamble ALONE is Greg's worst move** (−6bp E,
   P3 ×2.6, buys 0.10pp vs us). If we SEE an England-side Greg signal it implies the double-gamble
   profile — which our chalk pair already worst-cases at 99.5% hold.
3. Panel fixes applied post-audit: Olise-sweep sign inverted (V1) → fixed + re-run (orderings
   unchanged); unused boot key removed; S5 mechanism now exactly derived (V2), not just simulated.
**GREG ROLE-PLAY #2 (two-front frame, independent):** concludes CHALK-CHALK from his own seat — "P(2nd)
drives >90% of my E[prize]; the England gamble nets <2k CLP and accelerates Gonzalo's Olise path; ARG
fandom is my WORST option (an ARG title fires Dibu for Sebas AND felipe against me in the same stroke)."
His P(Olise-AST)=.82 (higher than our .53-.68 — strengthens his defensive motive; a sensitivity our
sweep covered). His whisper: "France 2-1, Spain 1-0 — and I check Olise's assist column at halftime."
Note the residual model-spread on Greg's rational FINAL entry: P(#1)-maximizer → Spain 2-1 · E[prize]
harness → thin S6 (ENG+ARG) edge inside noise · two-front role-play → Spain 1-0 chalk. All three are
Spain-side-or-noise, none is the fandom-ARG-alone profile, and OUR entry is identical against all three.
**VERDICT UNCHANGED AND RE-CONFIRMED: FRANCE 2-1 + SPAIN 1-0. The cover gate stays shut at +24.**

## Bias statement (mandate)
Sebas's instinct was "guess his side and play the man." The council's answer: we played the man HARDER
than that — we computed his entire strategy space (exact best-response + role-play) and found the man's
optimal play is Spain-side, his fandom play is ARG-side, and OUR entry is identical against both. The
protective move at this node is not mirroring; it is holding the modal Spain cell (1-0) that blocks his
exact-score kill-shot and keeps our pleno-tiebreak fortress. Chalk here IS playing the man.
