# PART 0 — Player panel + skill-persistence (2026-06-19/20)

Built by `standings/build_player_panel.py` (reproducible; OCR'd NAMES validated against the authoritative
`standings/<date>/standings.json` `points[]` arrays). Artifact: `standings/player_panel.csv` (27 players).
Source boards: Jun-14 (`standings 14-06-26/`, 3 PNGs), Jun-16 (`standings 16-06-26/`, 2 PNGs),
Jun-19 (`stadings 19-06-26/`, 2 PNGs). **S2/Jun-15 is a phantom — 3 boards, 2 gain-periods.**

## OCR-integrity (I-NOFAB) — ALL PASS
- **(a) Ordered match** — board points, position-by-position, == json `points[]` for all 3 dates; us row
  matches json `our_points`/`our_rank` each date.
- **(b) Per-player monotonicity** — `pts_14 ≤ pts_16 ≤ pts_19` (g1≥0, g2≥0) for all 27 (pool points
  only accumulate).
- **(c) Roster constancy** — identical 27 players across all 3 boards.

## Skill-persistence (the methodologically-correct test)

Per-period gains `g1 = pts_16 − pts_14`, `g2 = pts_19 − pts_16`:

| period | mean μ | cross-player σ | min | max |
|---|---|---|---|---|
| g1 (Jun14→16) | 13.37 | **3.532** | 9 | 23 |
| g2 (Jun16→19) | 37.89 | **7.181** | 22 | 51 |

- **PRIMARY — Spearman ρ(g1, g2) = −0.052** (n=27; `|ρ_crit| ≈ 0.38` at 5% two-sided; power at a true
  ρ=0.3 only ~0.31 → LOW power). **Verdict: CONSISTENT-WITH-LUCK; cannot exclude moderate skill
  (|ρ| ≲ 0.4).** NOT "no-skill proven" — n is small and the test is underpowered.
- **SECONDARY (descriptive, sticky/OVERSTATED — not the verdict):** cumulative-rank autocorr
  ρ(rank14,rank16)=+0.864, ρ(rank16,rank19)=+0.653. Points never decrease → cumulative ranks are sticky
  BY CONSTRUCTION; this overstates skill and is reported only for contrast.
- **Leader persistence:** Jun-19 leader Lucas LDC (91) climbed rank **6 → 4 → 1** — a mid-pack climb, a
  luck signature, not a sustained top seat.

## Opponent-variance params emitted for PART 1 (placement_mc `sigma_opp`)
- per-period mean gain μ: g1=13.37, g2=37.89
- cross-player gain σ: σ(g1)=3.53, **σ(g2)=7.18 → `sigma_opp` PRIMARY**, with ±25% sweep {5.39, 7.18, 8.98}
- gain-autocorr ρ(g1,g2) = −0.052
- **cross-check σ(g2)=7.18 ≈ BASE_SIGMA=6.0** (same order; sanity-consistent). NOTE the variance is
  RISING (σ(g1)=3.53 → σ(g2)=7.18), so σ(g2) may UNDERSTATE the MD3 residual — hence the ±25% sweep and
  the upper {13.78, 19.5} secondary anchors in PART 1.

## Beatability
19 players are strictly ahead of us at Jun-19 (us = 65, tied with SEBASTIAN MERA, rank 21). The low
ρ(g1,g2)=−0.052 says per-period gains are luck-like (≈iid) → **the lead is not a skill wall**, so
differentiation variance is the relevant lever. First estimate only (n=27, 2 periods); firm up post-MD2.

## Tie-break (pollaya, from the board footer — feeds PART 1 doc)
*"En caso de haber empate en puntos entre algunos integrantes de la polla, serán los mismos integrantes
los que decidirán el modo de desempate."* → A points tie is resolved **ad-hoc by the tied members**;
there is no deterministic split or pre-set tiebreaker. placement_mc uses strict `>` (ties → us optimistic),
which only bites at an exact boundary tie — measure-zero under continuous noise, so negligible but noted.
