# COUNCIL VERDICT (PRELIMINARY) — England vs Argentina, WC-2026 SF2 (Jul-15 19:00Z, lock 18:50Z)

**ADVISORY / I-HITL. PRELIMINARY — the binding council is TOMORROW at its own T-1h (~18:00Z Jul-15) on
fresh odds + confirmed lineups. This is the same-principles baseline landed a day early per Sebas's ask.
KO_SCORING = FULL120 (L57).**

## PRELIMINARY DECISION (on the 16:52Z board, T-26h): **1-0 England** — but the winner side is LIVE.
Fixture `ced22494ae0bbb8cc4f7108bf6f493df`, snapshot `data/snapshots/md6_2026-07-14T16-52-55Z.json`.

## Engine (frozen, market-only)
- Devig **ENG .3659 / D .3171 / ARG .3171** · total 2.5 · **p_over .4088** · μ_eff 2.318.
- **FULL120 argmax 1-0 England (E 2.5142)** vs 2-1 (2.4004) vs **0-1 Argentina (2.3948)** vs 1-2 (2.286).
  1-0 clear by ~+0.114; **argmax 1-0 at EVERY f** (no totals flip — p_over .409 is a dead axis).
- **COUNCIL FIRES** (weak-fav .366 < .55 AND argmax 1-0 ≠ modal 1-1). Flip-check HOLD vs Jul-12.
- Plenos (we hold 17): **P(exact@120') 1-0 = .1203 > 0-1 .1152 > 2-1 .0991** → argmax == max-pleno.

## The ACTIVE variable here is DIFFERENT from SF1 — the WINNER SIDE, and it is trending toward the flip
- **Winner-flip boundary (recomputed fresh): 0-1 Argentina becomes argmax at ARG devig ≥ 0.34 (H ≤ .35).**
  Live ARG **.3171 → +2.3pp away** (drift `drift_eng_arg.py`). Totals are NOT the lever (2-1 needs p_over
  ≥ .49; live .409 — never reached).
- **Trend + incongruence to watch**: Argentina firmed **+1.1pp** since Jul-12 (.3056 → .3171, now level with
  the draw); England softened −0.7pp. Some sportsbooks (Yahoo, Jul-14) price **Argentina as the favorite to
  advance** — which CONFLICTS with our fetched aggregate devig (England .366 > ARG .317, England ~52.5% to
  advance). The market may resolve toward Argentina by tomorrow. **If the T-1h ENG-ARG fetch shows ARG ≥ .34
  (or ENG ≤ .35), the pick flips to 0-1 Argentina** — a genuine live possibility, not today's call.
- Team news (Jul-14): **Quansah SUSPENDED (confirmed OUT)** → England CB reshuffle; **Rice a late illness
  doubt**; Bellingham/Kane/Guehi fit. Argentina: **Messi minor eye knock (plays)**, Romero fatigued (may sit
  for Medina — CB, non-star). Yellow cards reset both sides. Net: England's CB disruption (Quansah + possible
  Rice) is the news vector that could push the devig toward Argentina — consistent with the market drift.

## Field / lead layer (`lead_max_sf.py` fresh)
- **1-0 England beats the field at every q**: +0.2583 (q=0) → +0.2240 (q=.75). Note the edge SHRINKS as q
  rises (opposite of SF1) because chasers piling onto Argentina scorelines narrows our margin — but it stays
  firmly positive even if 75% of this Chilean pool backs Argentina/Messi. The "everyone's on Messi" worry is
  numerically defused; it does NOT justify deviating in either direction.
- Advancement (FULL120): P(England adv) = .5135 (softened from .5205). P(hold #1) ≥ .998 all branches.

## SAME PRINCIPLES, DIFFERENT BINDING CONSTRAINT — the answer to "same approach or different?"
SF2 uses the IDENTICAL policy framework as SF1 (frozen argmax over the full dist_120, re-conditioned on the
fresh market state at T-1h, convergence stack as the Goodhart guard). What differs is only the ACTIVE
coordinate: SF1's razor is on TOTALS (1-0 vs 2-1, both France); SF2's razor is on the WINNER SIDE (1-0
England vs 0-1 Argentina). No different machinery is needed — the framework is variable-agnostic; the binding
constraint moved from p_over to the ENG/ARG devig gap. There is NO bias inversion here (we have no locked
stake on either England or Argentina beyond Kane-MVP, which merely wants England to advance — an aligned,
not inverted, pull; and it does not reach into the 1-0-vs-0-1 choice, which is market-only).

## T-1h protocol (Jul-15 ~18:00Z — the binding decision)
Refetch → **ENG devig > .35 AND ARG < .34 → 1-0 England** (today's state) · **ARG ≥ .34 (or ENG ≤ .35) →
0-1 Argentina** (re-derive; the market/news trend points this way) · p_over irrelevant unless ≥ .49.
Reopen triggers: Bellingham/Kane OUT (England collapses → 0-1), Messi OUT (Argentina softens → firmer 1-0),
Rice confirmed out + CB reshuffle (softens England). NEVER 1-1 (dead). Council runs at its own T-1h — this
preliminary is a baseline, not the final word.

— Drafted ~17:15Z from the 16:52Z snapshot (T-26h). Binding council: Jul-15 ~18:00Z. I-HITL.
