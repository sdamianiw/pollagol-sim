# MEX-ING flip-threshold analysis — what would make the engine recommend a DRAW? (2026-07-05)

> Deterministic sweeps on the frozen engine (`src.ko_cadence ko`, snapshot `md4_2026-07-05T18-21-51Z.json`,
> harness = synthetic h2h/totals prices at exact target devig, engine untouched). Sebas's question after
> reverting 1-1 → 0-1: "numbers-wise, what would have had to happen to overturn the England win to a draw?"

## Lever 1 — draw price ↑ (devig 31% → 55%): DEAD LEVER, gap WIDENS
| draw devig | fair odds | FULL120 PICK | EV(1-1) | gap |
|---|---|---|---|---|
| 31% (live) | 3.24 | 0-1 (2.673) | 1.671 | +1.00 |
| 39% | 2.56 | 0-1 (2.861) | 1.654 | +1.21 |
| 47% | 2.13 | 0-1 (3.055) | 1.626 | +1.43 |
| 55% | 1.82 | 0-1 (3.259) | 1.584 | +1.67 |

**Why:** the frozen engine fits λs from team-balance + totals with ρ pinned at −0.05 (L19: ρ-fit built,
edge NO-PASS, kept gated OFF). The market draw price is an OUTPUT the engine cross-checks, never an INPUT
it chases. Raising D (scaling H/A down proportionally) leaves the decisive ratio intact and cannot flip it.

## Levers 2+3 — team balance + totals collapse, under BOTH scoring rules
| p_over(2.5) | fair Over | REG90 pick (gap) | FULL120 pick (gap) |
|---|---|---|---|
| 40% (live) | 2.51 | 0-1 (+0.19) | **0-1 (+1.00)** |
| 30% | 3.33 | 0-1 (+0.07) | 0-1 (+0.88) |
| 22% | 4.55 | **0-0 (−0.26) ← draw WINS** | 0-1 (+0.63) |
| 15% | 6.67 | **0-0 (−0.67)** | 1-0 (+0.24) |
| 10% (absurd) | 10.0 | **0-0 (−0.93)** | 1-0 (+0.002) |

(Equal-teams variant H=A=0.3455: REG90 knife-edge already at live totals (+0.01); FULL120 still +0.25
even at p_over 10%.)

## Findings
1. **Under REG90 (group-stage) scoring, draws go live easily** — crossover ≈ p_over 28% at this board's
   balance; equal teams put today's board on the knife-edge. This is why MD-3 draw-exceptions (SUI-CAN)
   were legitimate.
2. **Under FULL120 the draw NEVER becomes argmax anywhere in the reachable market space** — even a
   1.2-goal-total market (p_over 10%) with the real teams closes the gap only to +0.002, and the pick
   migrates 0-1 → 1-0 with the best draw becoming 0-0, NOT 1-1.
3. **Mechanism = the ET tax (precise):** of 53 audited WC KO games level at 90′ (1986–2022), **36% (19)
   died to an ET goal and 64% (34) survived to pens as scored draws** — the engine's f_model 0.637 IS this
   survival fraction. The tax on a 1-1 pick is two-fold: it loses the 36% ET-resolved branch AND its
   surviving 64% splits across 0-0/1-1/2-2 (only 17/53 = 32% of level games end exactly 1-1) — while every
   decisive pick GAINS the ET-resolved branch on top of its 90′ wins. Net: REG90 gap +0.19 → FULL120 +1.00.
4. **Corollary for the rest of the tournament:** no KO board will produce an engine draw recommendation
   unless the pool's scoring rule changes. Draw entries in the KO are always tilts, never EV-updates.
