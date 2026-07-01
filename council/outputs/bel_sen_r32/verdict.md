# COUNCIL VERDICT — Belgium vs Senegal (R32, 2026-07-01 20:00Z)

> I-HITL: this is a RECOMMENDATION. Sebas enters; nothing is locked. Entry deadline 19:50Z.
> Council is ADVISORY (L44): the FROZEN deterministic engine adjudicates E[pts]; no lens computes EV.
> Snapshot `data/snapshots/md4_2026-07-01T18-29-49Z.json` (fetched 18:29Z, quota 498). Branch `rho-fit`, engine FROZEN.

## MANDATE
Resolve the Belgium–Senegal entry. Sebas is torn between **Belgium** and **Senegal** and asked whether a **1-1 draw**
has upside over **Senegal 2-1**. Candidates faced off: **(A) Belgium 2-1 · (B) Belgium 1-0 · (C) 1-1 draw · (D) Senegal 2-1**.

## DETERMINISTIC BACKBONE (frozen engine on fresh odds; reproduce = exact)
- De-vig 1X2: **Belgium 44.7% / Draw 29.8% / Senegal 25.5%** (overround 1.0317) — Belgium a WEAK favorite.
- Totals: line 2.5, p_over 0.516, **mu_eff 2.740** (elevated → higher-scoring game). E[goals] Belgium 1.57 / Senegal 1.23.
- 90′ modal (most likely) = **1-1** (P 0.119). 90′ EV-argmax = **Belgium 1-0** (2.454), runner-up Belgium 2-1 (2.430, gap 0.025).
- Pool scores **FULL120** (120′ scoreline, penalties EXCLUDED; level after ET = scored draw). `ko_adjust` FULL120 (cageyness 0.65):

| Candidate | EV (90′) | **EV (FULL120)** | note |
|---|---|---|---|
| **Belgium 2-1** | 2.430 | **2.755** | FULL120 EV-argmax |
| **Belgium 1-0** | 2.454 | 2.720 | 90′ argmax; −0.035 vs 2-1 (sub-floor) |
| Belgium 2-0 | 2.257 | 2.477 | |
| **Senegal 2-1** | 1.800 | 2.039 | −0.72 vs argmax |
| Senegal 1-0 | 1.831 | 2.024 | |
| **1-1 draw** | 2.065 | **1.415** | WORST — craters under FULL120 |
| 0-0 draw | 1.757 | 1.171 | |

- p_draw_90 0.258 → p_draw_scored(120) 0.143 (f_model 0.553).

## KEY FINDINGS (deterministic, pre-panel)
1. **The 1-1 draw is the single WORST candidate under FULL120** (2.065 → 1.415), dominated by the best decisive pick by
   **+0.39 (draw-max, REG90) to +1.85 (draw-min, f 0.31)** — draw NEVER EV-justified at any penalty rate (confirms L54).
   Direct answer to Sebas: **no** upside to 1-1; in fact Senegal 2-1 (2.04) *beats* 1-1 (1.42). Both lose badly to Belgium.
2. **Senegal 2-1 is a −0.72 EV tilt** vs the argmax. Off the top-6 decisive picks; the engine has no basis for a Senegal
   scoreline (devig A 25.5%). Entering it from 1st place is exactly the discretionary variance L50 forbids.
3. **The KO rule flips the argmax 1-0 → Belgium 2-1**, robustly across the ET band (level-at-90′ games resolve to 2-1 in ET).
   But 2-1 vs 1-0 is a **coin-flip within noise** — |ΔEV| ≤ 0.035 (SUB-FLOOR) at EVERY plausible f (crossover at f≈0.83):

   | ET regime | f | 2-1 − 1-0 | argmax |
   |---|---|---|---|
   | REG90 (no ET) | 1.00 | −0.025 | 1-0 |
   | very cagey ET | 0.87–0.96 | −0.006…−0.018 | 1-0 |
   | crossover | ≈0.83 | ~0 | tie |
   | empirical WC KO (default) | 0.55 | **+0.035** | **2-1** |

   → **Belgium decisive win is LOCKED; 2-1 vs 1-0 is a judgment tie** (FULL120 + high total lean 2-1; pure-90′ leans 1-0).

## PANEL (isolated lenses — advisory, no lens computed EV)
**Form/tactical (MED-HIGH → Belgium 2-1):** Belgium 1-1/0-0/5-1 in groups (topped G); Senegal L/L/5-0 (3rd in I,
behind France+Norway). **Senegal #1 GK Edouard Mendy OUT** (knee, left camp) → backup Diaw = real Belgium edge;
Belgium CB Debast doubtful. Opta 46.8% ≈ market 44.7% (no mispricing). Open-game projection + mu_eff 2.74 → 2-1
> 1-0. Senegal-upset gut "does not survive the Mendy injury or Senegal's path." Sources: SportsMole/Opta/ESPN (2026-07-01).
**Chalk/leader-doctrine (HIGH → Belgium 2-1):** switching 1-0→2-1 = rule-grounded **EV-UPDATE** (permitted, L50);
Senegal 2-1 = a **−0.716 EV tilt**, strictly dominated under 60/20/10 ("the larger the lead, the more a tilt-miss
costs"); 1-1 = worst. Per-match scorelines hidden → no ownership counter-argument. "Would a disciplined leader
enter Senegal here? **No.**" Notes 2-1 vs 1-0 is a soft debate, both permitted.
**Adversarial/premortem (MED-HIGH → leans Belgium 1-0):** verified market current (FanDuel 44.9/29.6/25.5 ≈ engine),
Mendy OUT. Steelmanned Senegal (Mané elite AFCON'25 POTY; Belgium fragility; Morocco'22) → **fails**: 25.5% already
prices Mané; Mendy-out makes 25.5% generous. Rejects Senegal+draw. **Landed punch = ET-caginess:** conditional ET
goal-rate likely 25-40% below the engine's unconditional λ → narrows/flips 2-1→1-0; also Belgium's low-scoring group
pattern → prefers 1-0. Premortem FM#1 (~30-35%): Belgium wins 1-0 not 2-1 (miss exact bonus); FM#2 (~20-25%): 1-1@90'→Senegal wins ET.
**Historian/base-rate (LOW → leans Belgium 1-0):** empirical WC-KO penalty rate **f≈0.68** (full-ET 2006-22: 17/25
stay level; 2022 drift → 0.72-0.80), **above** the engine default 0.55. FLAG-1 challenge: "re-run at f=0.68 — does 2-1
still beat 1-0?" WC scoreline base rates: 1-0 = 19% (modal), 2-1 = 16%. AFR-EUR KO: Europe wins ~65-70% → Senegal 25.5%
correctly priced (Senegal 2-1 Sweden 2002 = anecdotal precedent, not base rate). 1-1@120' residual ~4-5% (confirms draw
dominated). Sources: Wikipedia penalty-shootout list, FIFA scoreline stats, African-nations-at-WC.
**→ ADVERSARIAL-VERIFY (engine, per FLAG-1, L54c):** at f=0.681 (cageyness 0.42) **Belgium 2-1 = 2.669 > 1-0 = 2.649
(+0.020)**; 2-1 stays argmax across f 0.55-0.80; flips to 1-0 only at f≥0.83 (near-zero-ET, contradicts the ET-goal
record). **The 2-1 edge is NOT an f=0.55 artifact — it survives the historian's empirical anchor.**

## SYNTHESIS
- **UNANIMOUS (4/4 lenses): a Belgium decisive win. Senegal 2-1 and 1-1 REJECTED on the merits** — not just on EV
  (Senegal −0.72, draw −1.34) but on football (Mendy out, Senegal's weaker path), history (Europe 65-70% AFR-EUR KO;
  25.5% correctly priced), and doctrine (tilt from 1st place). The gut Senegal case got its best adversarial + base-rate
  shot and did not survive.
- **The 2-1 vs 1-0 debate is WITHIN NOISE** (|ΔEV| ≤ 0.035) and the lenses split 2-2 (form+chalk → 2-1; adversarial+
  historian → 1-0) — but all four agree it's a coin-flip. **Engine adjudicates (L44), and it is ROBUST:** at the
  historian's empirical f=0.68 (not the default 0.55), **2-1 stays argmax by +0.020** (2.669 vs 2.649); it holds
  across f 0.55-0.80 and flips to 1-0 only at f≥0.83 (near-zero-ET, contradicting the WC ET-goal record). Both the
  adversarial ET-caginess attack (25-40% discount) and the historian f-challenge were run through the engine and
  **2-1 survived both.** mu_eff 2.74 + Mendy-out → a "both teams score, Belgium by 1" (2-1) is better-calibrated than
  a "Belgium clean sheet" (1-0). → **2-1 is the verified primary; 1-0 is a co-equal fallback (~0.02 EV cost, and the
  flip-floor-hold-baseline reading).**
- **Reframe of Sebas's instinct:** distrust of Belgium points NOT to Senegal (market prices it; Mendy out) but to
  **Belgium 1-0** (grind-out narrow win, matching their 1-1/0-0 group games). Either Belgium score is disciplined.

## SUCCESS CRITERIA
- SC1 backbone reproduced exactly (max|Δ| = 0). ✅
- SC2 panel grounded + cited (4/4 lenses, sources); no lens hand-rolled E[pts]; the 2 challenges (ET-caginess, f=0.68) engine-verified. ✅
- SC3 chalk/leader axis clean: 1-0→2-1 = EV-UPDATE (permitted); Senegal/1-1 = tilt (forbidden while leading). ✅
- SC4 decision adjudicated by the engine; draw + Senegal rejected on the deterministic backbone. ✅

## RECOMMENDATION (I-HITL — Sebas enters; lock 19:50Z)
**ENTER: Belgium 2-1** (FULL120 EV-argmax 2.755; high-total-calibrated; survives the adversarial's own ET-discount range).
**Co-equal fallback: Belgium 1-0** (baseline; if you read it as a grind — EV cost ~0.03, negligible).
**DO NOT enter Senegal 2-1** (−0.72 EV tilt; L50 forbids from 1st) **or 1-1** (worst pick; craters under FULL120).
**Pre-lock gate (re-check ~19:40-19:50Z):** (1) Mendy confirmed OUT / Diaw starts; (2) De Bruyne in the XI, no minute
limit; (3) Debast fitness; (4) weather at Lumen Field, Seattle (heavy rain = equalizer, nudges toward 1-0); (5) odds
stable (Senegal drifting ≥ +300 = confirmation). None of these flip Belgium-decisive; they only fine-tune 2-1 vs 1-0.
