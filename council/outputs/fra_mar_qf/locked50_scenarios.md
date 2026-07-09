# Locked-50 scenario cross-check — "hope España + France both lose?" (2026-07-09, QF stage)

> Sebas's hypothesis (Jul-9, voice): *"the best thing that could happen is that Spain and France both get
> eliminated — then the podium and player awards go out the window and we're left with current standings."*
> ADVISORY, deterministic where possible; changes NO lever we control (match layer stays EV-argmax chalk,
> L50; picks are locked and unchangeable). Inputs: `pool/locked_ownership_2026-06-28.md` (observed, picks
> fixed), Jul-9 board (us 352, +24 Greg 328 / +25 Lucas 327 / +31 Gonzalo 321), stat counts web-re-verified
> 2026-07-09 (NBC/Goal/Fox/MoroccoWN/Tribuna, ≥2 sources; PARTIAL flags carried honestly).

## Leg-state board (QF stage, post-R16 eliminations: POR, BRA, MEX, USA, SUI-adv/COL-out, CAN, PRY, EGY)

| award (state 2026-07-09) | us | Greg (+24 behind) | Lucas (+25) | Gonzalo (+31) |
|---|---|---|---|---|
| Champion | **España — LIVE** | España — LIVE (same) | Portugal — **DEAD** | Francia — LIVE |
| Scorer (Messi 8 > Mbappé 7 = Haaland 7 > Kane 6) | Mbappé — live, −1 behind | Mbappé (same) | Mbappé (same) | Mbappé (same) |
| Assister (Olise 5 = leader; Bruno frozen ~1 PARTIAL; Messi ~1) | Bruno — **frozen/dead** | Messi — ~dead | Bruno — frozen/dead (same as us) | **Olise — LIVE LEADER** |
| MVP (Goal.com Jul-9: Messi > Mbappé > Haaland > Kane(4) > Olise; Yamal NOT top-10) | **Kane — live #4** | Yamal — faded | Mbappé — live #2 | Yamal — faded |
| GK (Simón 5 CS record; Maignan 3, Courtois 3 PARTIAL, Dibu 2; Alisson/Costa frozen-out) | Dibu — live, trailing | Maignan — live, trailing | Diogo Costa — **DEAD** | Alisson — **DEAD** |

**Scorer is common-mode across all four** → cancels in every pairwise race (a Messi Boot hurts everyone
equally; Jun-28 read unchanged). **Simón winning the Glove is ALSO common-mode null** (nobody in the
top-4 holds him) — it kills our Dibu and Greg's Maignan together.

## Scenario table — net locked-50 swing vs each chaser (10 pts/leg, `memory/rules.md` locked-50)

Convention: "+" = good for US relative to that chaser. Frozen-count legs (Olise 5) do NOT die on
elimination — the leader stays ahead unless passed (Diaz 4 is one assist behind and plays TODAY).

| scenario | vs Greg (+24) | vs Lucas (+25) | vs Gonzalo (+31) | net read |
|---|---|---|---|---|
| **FRA out today (MAR wins)** | **+** kills Maignan path; Kane/Yamal axis untouched | **+** kills his ONE live diff leg (Mbappé MVP #2) | **++** kills his champion (−10-class) AND freezes Olise at 5 (passable by Diaz/Saka) | **clearly good** |
| **ESP out (QF vs BEL)** | **0/+** champion cancels (shared!); kills Yamal deader; Simón freezes at 5-6 (still GG favourite → GK axis stays null) | **−** surrenders our biggest live edge (his champion is already dead; ours dying = convergence he WANTS) | **0/−** our champion dies, his (FRA) lives | **mixed, NOT clearly good** |
| **BOTH out** | **+** (Yamal, Maignan dead; our Kane still live via ENG) | **−/0** (we lose the champion edge; he loses Mbappé MVP) | **++** (his champion + Yamal dead; Olise frozen) | **net positive but NOT the clean sweep hypothesized** |
| **FRA champion (the nightmare)** | **−** Maignan GG live + Mbappé Boot(common) | **−−** Mbappé likely Golden Ball → his +10 | **−−−** Francia +10 AND Olise +10 → Gonzalo recovers ~20 of 31 | **the single worst world — rooting AGAINST France is data-correct** |
| **ESP champion** | **−** champion cancels but Yamal Ball revives (winner-team bias) → Greg +10 swing | **++** our +10, his dead | **++** our +10 vs his dead FRA path | **good vs 2 of 3, ~neutral-to-negative vs the CLOSEST chaser** |
| **ENG champion** | **++** Kane MVP (likely Ball on a title run, currently #4) + Kane Boot possible; Yamal/Maignan dead | **++** Kane MVP beats Mbappé MVP; champion edge kept (ESP alive ≥ his dead) | **++** | **best single world for us** |
| **ARG champion** | **+** Messi Boot/Ball common-mode-ish; Dibu GK activates (deep-run CS) — our diff leg | **+** Dibu vs dead Costa | **+** Dibu vs dead Alisson; his FRA dead | **second-best world** |

## Verdict on the hypothesis
1. **Directionally half-right, importantly wrong on España.** "France out" is unambiguously good — it
   kills Lucas's Mbappé-MVP, Greg's Maignan and Gonzalo's champion+Olise cluster in one stroke, and the
   France-title world is our single worst scenario. But "España out" is NOT clearly good: vs Greg the
   champion leg CANCELS (he holds España too — elimination does zero relative damage), and vs Lucas it
   surrenders the largest live edge we hold (live champion vs his dead one). The clean win-win is
   **"France loses, España's fate ≈ neutral-to-mildly-positive-to-keep"**.
2. **"Left with current standings" is imprecise:** the match layer keeps accruing ~4-9 pts/game for
   everyone across the ~7 remaining boards, and frozen-count legs (Olise 5) can still WIN their award.
   Both-out compresses locked-50 variance vs Greg/Gonzalo but mildly opens the door vs Lucas.
3. **The actual best-case ranking for us: England title > Argentina title > España title > any-other >
   France title.** (Kane MVP is our only strongly-differentiated live leg — 1/10 top-10 ownership.)
4. **No lever changes.** Rooting interest ≠ picks: today's FRA-MAR entry stays the FULL120 EV-argmax
   (France 1-0) — the −8%..−20% cost of deviation (Jul-3 contrarian MC, L50) dwarfs any correlation story,
   and the POR-ESP hedge harness precedent showed chalk beats hedging vs every chaser posture. Betting
   AGAINST France on the board while hoping France loses would be a tilt, not a hedge.
5. **Doctrine branch check (`[[ko-leader-doctrine]]` / ownership re-check step 3):** no chaser is
   "clearly locked-ahead" — Gonzalo's Olise leg is leading but he trails by 31; Greg/Lucas hold no
   leading differentiated leg. Trigger NOT fired; FREEZE holds. Contingent España-out doctrine trigger
   (pre-QF) expired un-fired — España reached the QF; if España exits vs Belgium tomorrow, re-run THIS
   table (it already covers that branch: mixed, no posture change warranted).

Sources: Goal.com Golden Boot (Jul-7) + Golden Ball power rankings (Jul-9); NBC Sports scorers (Jul-8);
Fox Sports Boot tracker + GK CS table; Morocco World News assists-after-R16 (Jul-8); Tribuna/worldcuplocaltime
(Bruno 1 assist PARTIAL; Courtois 3 CS PARTIAL); Al Jazeera QF field (Jul-6). PARTIAL flags: Bruno assists
(1, conflation risk w/ Bruno Guimarães 4), Courtois CS, Yamal Ball positioning (pre-tournament market lead,
now outside top-10 narrative).
