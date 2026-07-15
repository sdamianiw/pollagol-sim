# COUNCIL VERDICT — England vs Argentina, WC-2026 SF2 (Jul-15 19:00Z, lock 18:50Z)

## ⚠️ CORRECTED FINAL VERDICT (~18:10Z, post-/evaluate): **ENTER ARGENTINA 0-1 — the cover. The
original "England 1-0, decline the cover" ruling below was adjudicated on a BUGGY number and is
SUPERSEDED.**

**What happened (the /evaluate loop working as designed):** the goal-mandated evaluation phase built an
EXACT loss-path enumeration (`greg_paths.py`, pure convolution, no MC) as a cross-validation of the
`greg_block.py` MC — and they DISAGREED 15×. Root cause: **numpy boolean `+` is logical OR**, so
`LOCK * ((champ=="ESP") + (mvp=="Yamal") + ...)` capped every award payout at ONE leg — **Greg's
Yamal-MVP + Messi-assist PARLAY (the exact threat) could never stack.** The "4bp" edge the council
declined was computed in a world without award parlays. Fixed (`.astype(float)` per leg), re-run, and the
two independent implementations now agree: P(no-hold | 1-0) = 0.824% (MC) vs 0.826% (exact) ✓.

**Corrected decision table (gap +24, strict tie=loss):**
- **1-0 England: P(hold #1) = 0.9918** (P(Greg passes/ties) = 0.82%)
- **0-1 Argentina: P(hold #1) = 0.9961** (0.39%) → **the cover HALVES the loss tail, buying ~42bp**
  (was mis-measured at 4bp). Sign-robust in ALL 9 sweeps; GROWS in the adverse cells (yamal .40 → 58bp,
  messi .25 → 77bp). Exact loss autopsy: under 1-0, **42% of ALL losing universes are the single path
  "ARG wins tonight × Yamal-MVP × Messi-assist parlay, needing only M ≤ −5"** — the cover closes
  precisely that branch (tonight contributes ~0 instead of −5..−9, forcing Greg to find the swing from
  the last two games alone).
- Re-adjudication of the 3-1 council: the three HOLD lenses all anchored on "4bp = sub-material" — that
  premise is now false at 10× the magnitude. The bias-hygiene lens's logic (P(1st) governs at +24; the
  cover IS the P(1st)-argmax; Sebas's instinct vindicated) stands unrebutted at 42bp. The EV give-up
  (−0.12 pts, −0.56pp pleno rate) has near-zero prize value at this gap (rest of field P(pass) ≈ 0.0003).
- Gap-sweep doctrine confirmed: at +20 the cover buys 80bp, at +15 163bp — the direction of travel says
  cover NOW, not later.

**FINAL: ENTER ARGENTINA 0-1** (Greg-cover; his modal pick). T-15: if fresh ARG devig ≥ .34 the ENGINE
also flips to 0-1 and the entry is unanimous; no fresh number reverses the cover while Greg is ARG-side.
NEVER 1-1. I-HITL: Sebas enters. — The original analysis below is preserved for the audit trail.

---

**ADVISORY / I-HITL (Sebas enters). Engine adjudicates EV (L44). KO_SCORING = FULL120 (L57). This is the
GREG-BLOCKING node — a NOVEL decision type: EV-argmax vs P(hold #1) cover of a ~known chaser.**

## DECISION (16:52–17:11Z board): **ENTER ENGLAND 1-0.** Cover-with-Argentina-0-1 considered and DECLINED
— it is the P(hold)-argmax but by a sub-material, model-fragile 4bp. Your covering instinct is CORRECT IN
KIND but premature IN DEGREE at a +24 lead; the tool is preserved for the final.

Fixture `ced22494ae0bbb8cc4f7108bf6f493df`, snapshot `data/snapshots/md6_2026-07-15T17-11-10Z.json`
(17:11Z, quota 454, flipcheck HOLD gap +0.0000, B4 identical).

## What changed (why this node is structurally new)
Spain 2-0 France (Oyarzabal 22' pen, Porro 58'; VERIFIED ×5) → our France 2-1 = **0 pts**, Greg +4 →
**gap +28 → +24** (us 377, Greg 353). **España in the final = our champion leg alive but COMMON-MODE with
Greg.** Every France award leg (Maignan GK, Mbappé MVP) DEAD → Gonzalo/felipe/Lucas/Rodrigo gutted, floor
P(pass) ≈ 0.0003. **Greg is the only live threat.** His differential legs vs us: **Messi-assist (live) +
Yamal-MVP (now live, Spain in final)**; ours: Kane-MVP (needs ENG title) + Dibu-GK (needs ARG title) — our
award slate is internally HEDGED on tonight, his leans Spain/Argentina. **Sebas's read: ~95% Greg enters an
Argentina scoreline** (Messi stake + fandom) → the L50 "picks-hidden → defensive-chalk unimplementable"
premise is VOID → the covering question is legitimately on the table.

## Engine (frozen, market-only)
- Devig **ENG .363 / D .332 / ARG .305** · total 2.5 · **p_over .385 (heavy Under)** · μ_eff 2.227.
- **FULL120 argmax 1-0 ENG (E 2.5414)** · 0-1 ARG (2.4179) · 2-1 ENG (2.387) · 1-2 ARG (2.271) ·
  1-1 (1.700, DEAD). Council FIRES (weak-fav .363, argmax≠modal 1-1).
- Winner-flip: 0-1 ARG becomes EV-argmax at **ARG devig ≥ .33** (live .3054, **+2.5pp away**). Drift
  8/10 stable, CONTROL==LIVE 0.00e+00. Plenos: **1-0 .1265 > 0-1 .1209 > 2-1 .0975** (1-0 = max-pleno).

## The Greg-block harness (`greg_block.py`, CONTROL identity PASS ×3, B4, floor-check others 0.0003)
- **0-1 Argentina MAXIMIZES P(hold #1 vs Greg) = 0.99984** vs **1-0 England (EV-argmax) = 0.99945** →
  **+0.00039 (4bp)**. STABLE: 0-1 wins P(hold) in ALL 9 sweep cells (p95 .80–1.00, yamal .15–.40, messi
  .05–.25, pairESP .40–.60). Mechanism: 1-0 ENG is ANTI-correlated with Greg (Argentina win → he scores,
  we get 0, −9 swing); 0-1 ARG is CORRELATED (both score or both miss → gap ~flat) = a variance-min cover.
- **BOTH entries hold #1 at ≥ 0.9994.** The harness did its job: it PROVED the cover is the P(hold)-argmax
  and quantified the edge at 4bp — which is exactly what lets the council reject it with confidence.

## Council — 4 ISOLATED parallel lenses + judge reconciliation (fan-out rule, Jul-14)
| Lens | Verdict | Conf | Core |
|---|---|---|---|
| Form/market/news | **England 1-0** | Med | Market won't flip (ARG +205→+200 = vig noise; ENG *lengthening* = public-on-ARG, books fading); Under −170 = 1-goal shape; Rice fit, Konsa in for Quansah, O'Reilly the one late doubt |
| Game-theory/covering | **England 1-0** | High | Covering rule applies in DIRECTION but 4bp is below the sim's own parameter uncertainty → fails materiality; keep pleno insurance for the tie that actually decides prizes |
| Adversarial | **England 1-0** | High | 4bp is SUB-NOISE (inside ±1-2pp Greg-prior error, a subjective read); concave prize-utility flat near P=1 (~$0.02/bp); 0.12 EV + pleno cost is real & certain; backfire tail if Greg→England |
| Bias-hygiene | **Argentina 0-1** | High | P(1st) governs; doctrine-exception legitimately triggered; 0-1 IS the P(1st)-argmax; Sebas's instinct VINDICATED in direction (rhetoric overblown, conclusion right) |

**JUDGE RECONCILIATION (3-1, but the split is on ONE principle, not the facts).** All four agree: (a) 0-1 is
the P(hold)-argmax, (b) both entries hold ≥ .9994, (c) P(1st) is the governing objective, (d) the
doctrine-exception is real. The ONLY disagreement: is a 4bp edge **actionable** when it sits inside the
model's noise? Ruling for **England 1-0** on four grounds the dissent doesn't overcome:
1. **Fragile signal vs robust cost.** The 4bp P(hold) edge rests on a *subjective* 95% Greg-prior + ASSUMED
   award/final odds. The 0.12 EV + 0.56pp/game pleno edge rests on *observed* market odds. Under model
   uncertainty you take the robust edge. (E[prize] value of the 4bp ≈ **190 CLP** — two hundred pesos.)
2. **The cover defends the wrong flank.** Tonight's scoreline choice only touches MATCH variance (±9, vs a
   +24 lead). The real residual threat to #1 is Greg's **Yamal-MVP + Messi-assist award parlay in a
   Spain-title world** — an awards/final problem the tonight-cover does nothing about.
3. **It trades our best branch for a non-dangerous one.** England 1-0 + England win = we PLENO, gap → +33
   (the market-modal result). The cover forfeits that to soften the Argentina-win branch, which only takes
   us to +15 — still P(hold) ≈ .997. A safe leader doesn't sell his highest-upside, market-likely branch.
4. **Preserve the tool.** Covering value is highest when the race is TIGHT and games are FEW; tonight
   (+24, 3 games) is its lowest-value moment. Spend it at the FINAL if Greg is within ~10 and his pick is
   known.

## Bias statement (per mandate)
Sebas leaned "pick the same as Greg — can't afford the risk." The council VINDICATES the instinct's
direction (covering a known chaser is the correct *type* of move; 0-1 genuinely is the P(hold)-argmax) and
REJECTS its application here (the edge is inside the noise; the cost is real; you're already safe). This is
not variance-phobia producing a wrong answer — it's a sound instinct fired one node too early. The
disciplined entry (England 1-0) is what a neutral +24 leader enters; it survives removal of the Greg-fear.

## ENTER line + T-15 rule (Sebas's own refetch ~18:20Z, post-lineups)
- **Fresh ARG devig ≥ .33** (a real Argentina firm on late money/O'Reilly-out news) → **0-1 Argentina** —
  because then the ENGINE argmax and the cover AGREE, and the decision is unanimous. This is the one clean
  path to the Argentina scoreline.
- **Else → ENGLAND 1-0** (EV-argmax, max-pleno). p_over is irrelevant (dead at .385; 2-1 needs ≥ .49).
- Reopen triggers: Kane/Bellingham OUT → England softens (→ re-derive); Messi OUT → Argentina softens
  (firmer 1-0); O'Reilly OUT confirmed → ARG firms toward the .33 flip (watch it). NEVER 1-1 (dead).
- **Covering doctrine (NEW, logged):** re-arm the cover at the FINAL if gap ≤ ~10 and Greg's pick is known.

## FINAL WORD (delivered ~17:40Z, T-1h10): **ENTER ENGLAND 1-0.** Cover DECLINED (4bp, sub-material,
model-fragile; the EV+pleno edge is robust; the real threat is Greg's award parlay, not tonight's score).
At T-15: ARG devig ≥ .33 → 0-1 Argentina (engine+cover agree); else England 1-0. I-HITL: Sebas enters.
