# -*- coding: utf-8 -*-
"""ko_adjust - NON-FROZEN knockout post-process (L52). Transforms a 90'-regulation score matrix into a
FULL120 (extra-time, PENALTIES-EXCLUDED) knockout-scored distribution, then re-scores it with the FROZEN
src.optimizer (reused verbatim - no frozen edit). Standalone: NOT wired into run_matchday's live path
(the live cadence stays byte-identical).

FULL120 (Sebas-confirmed 2026-06-28): the pool scores the 120' scoreline with PENALTIES EXCLUDED -> a
game STILL LEVEL after 120' is scored as that level scoreline (a DRAW). A 90' draw won in extra time
scores as the decisive 120' scoreline, NOT a draw. Knockout games NOT level at 90' END at 90' (no extra
time), so their off-diagonal mass is unchanged. Only the diagonal (level-at-90') mass goes to extra time.

ET model: each side scores ET goals ~ Poisson(mu_et_side) over 30', mu_et_side = cageyness * lambda_side
* (30/90), where lambda_side = expected goals read off the 90' matrix. `cageyness` (< 1; ET is lower-tempo)
is the single free parameter - calibrate it so the model penalty rate f = P(level after 120' | level at
90') matches the empirical knockout base rate. A level-at-90' cell (k,k) redistributes to (k+a, k+b) with
weight Ph(a)*Pa(b); the share with a==b stays level -> scored draw. ET targets that overflow the 9x9 grid
are DROPPED and the distribution renormalized (never clamped onto the (8,8) corner - clamping an a!=b
overflow onto the diagonal would miscount a decisive result as a scored draw).

KNOWN STYLIZATIONS (documented, not bugs; immaterial to the draw-vs-decisive verdict, both absorbed by
the cageyness->empirical-f calibration): (1) `lambda_side` is the UNCONDITIONAL 90' expected goals, not the
goal rate CONDITIONAL on the game being level at 90' - so the home/away ET-rate asymmetry is approximate for
lopsided ties. (2) the optional explicit `mu_et` override is SYMMETRIC (both sides equal); for asymmetric
matches use the default `cageyness` path, which preserves the home/away ratio.
"""
from math import exp, factorial
import numpy as np
from src.model import implied_1x2
from src.optimizer import expected_points, PLAUSIBILITY_FLOOR

ET_FRACTION = 30.0 / 90.0      # extra time is 1/3 of regulation
DEFAULT_CAGEYNESS = 0.65       # ET scoring intensity vs regulation (calibrate to empirical f)
_ET_KMAX = 5                   # truncate the per-side ET Poisson tail (renormalized)


def _expected_goals(matrix):
    """E[home goals], E[away goals] read off the 90' score matrix."""
    n = matrix.shape[0]
    idx = np.arange(n)
    lam_h = float((matrix.sum(axis=1) * idx).sum())
    lam_a = float((matrix.sum(axis=0) * idx).sum())
    return lam_h, lam_a


def _et_pmf(mu, kmax=_ET_KMAX):
    """Truncated, renormalized Poisson pmf over 0..kmax. mu=0 -> all mass at 0 (no ET goals)."""
    pmf = np.array([exp(-mu) * mu ** k / factorial(k) for k in range(kmax + 1)], dtype=float)
    total = pmf.sum()
    return pmf / total if total > 0 else pmf


def _candidate_table(dist):
    """E[pts] for every plausible candidate scoreline (P >= optimizer floor) - same candidate set as
    optimize(). Falls back to the single modal cell when nothing clears the floor (mirrors optimize's
    fallback, so ev_argmax/best_draw/best_decisive are derived from ONE consistent scan and ev_argmax is
    never empty)."""
    n = dist.shape[0]
    rows = [{"pred": (i, j), "ev": expected_points((i, j), dist), "p": float(dist[i, j])}
            for i in range(n) for j in range(n) if dist[i, j] >= PLAUSIBILITY_FLOOR]
    if not rows:
        idx = np.unravel_index(int(np.argmax(dist)), dist.shape)
        cell = (int(idx[0]), int(idx[1]))
        rows = [{"pred": cell, "ev": expected_points(cell, dist), "p": float(dist[cell])}]
    return rows


def ko_adjust(matrix_90, cageyness=DEFAULT_CAGEYNESS, mu_et=None, ko_rule="FULL120"):
    """Transform a 90' score matrix into a knockout-scored distribution and re-score it.

    Args:
      matrix_90 : normalized 9x9 ndarray, P(home i, away j at 90').
      cageyness : ET scoring intensity vs regulation (ignored if mu_et is given).
      mu_et     : optional explicit per-side ET goal mean (overrides cageyness; symmetric).
      ko_rule   : "FULL120" (pens excluded; level-after-120' = scored draw) or "REG90" (identity).

    Returns dict: dist_120, ko_rule, p_home_win, p_draw_scored, p_away_win, p_draw_90, f_model,
      mu_et_home, mu_et_away, ev_argmax (pick tuple), ev_argmax_pts, best_draw, best_decisive, ev_table.
    """
    M = np.asarray(matrix_90, dtype=float)
    n = M.shape[0]
    if ko_rule not in ("FULL120", "REG90"):
        raise ValueError(f"ko_rule must be 'FULL120' or 'REG90', got {ko_rule!r}")

    if ko_rule == "REG90":
        dist = M.copy()
        mu_h = mu_a = 0.0
    else:
        if mu_et is not None:
            mu_h = mu_a = float(mu_et)
        else:
            lam_h, lam_a = _expected_goals(M)
            mu_h = cageyness * lam_h * ET_FRACTION
            mu_a = cageyness * lam_a * ET_FRACTION
        pmf_h, pmf_a = _et_pmf(mu_h), _et_pmf(mu_a)
        dist = M.copy()
        for k in range(n):
            p = M[k, k]
            if p <= 0.0:
                continue
            dist[k, k] = 0.0
            for a, ph in enumerate(pmf_h):
                if k + a >= n:
                    break                       # home ET goals overflow the grid -> DROP (never clamp onto
                for b, pa in enumerate(pmf_a):  # the diagonal; a is increasing so all larger a overflow too)
                    if k + b >= n:
                        break
                    w = ph * pa
                    if w > 0.0:
                        dist[k + a, k + b] += p * w
        s = dist.sum()
        if s > 0:
            dist = dist / s                     # renormalize away the (negligible) dropped Poisson tail

    # ONE scan -> ev_argmax, best_draw, best_decisive, ev_table all consistent (no optimize() top-10 re-scan).
    # ev_argmax equals optimize(dist)["pick"] by construction (same expected_points + floor); test asserts it.
    table = sorted(_candidate_table(dist), key=lambda r: -r["ev"])
    ev_argmax = table[0]
    best_draw = max((r for r in table if r["pred"][0] == r["pred"][1]), key=lambda r: r["ev"], default=None)
    best_decisive = max((r for r in table if r["pred"][0] != r["pred"][1]), key=lambda r: r["ev"], default=None)
    out_120 = implied_1x2(dist)                 # reuse the frozen helper, not a hand-rolled tril/trace/triu
    draw_90 = implied_1x2(M)["draw"]
    return {
        "dist_120": dist, "ko_rule": ko_rule,
        "p_home_win": out_120["home"],
        "p_draw_scored": out_120["draw"],
        "p_away_win": out_120["away"],
        "p_draw_90": draw_90,
        "f_model": (out_120["draw"] / draw_90) if draw_90 > 0 else 0.0,
        "mu_et_home": mu_h, "mu_et_away": mu_a,
        "ev_argmax": ev_argmax["pred"], "ev_argmax_pts": ev_argmax["ev"],
        "best_draw": best_draw, "best_decisive": best_decisive,
        "ev_table": table[:10],
    }
