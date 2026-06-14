"""ANNEX V (Track-B 2026-06-14) - the lambda risk-dial: a PURE selection layer over the FROZEN score matrix.

BUILD-NOT-FIRE skeleton. It switches the per-match objective from argmax E[pts] (the EV-optimizer) to a
mean-variance argmax  E[pts] + lambda * SD[pts]  -- a placement-bet (MAX P(top-3)) tilt that buys upside
variance when trailing, on the rationale that under 60/20/10 only a podium finish pays (4th = last = $0).

CONTRACT / INVARIANTS:
  * lambda = 0  reproduces the E[pts] argmax EXACTLY (same candidate scan + tie-break as optimizer.optimize),
    so run_matchday's DEFAULT path stays byte-identical (BUILD != FIRE).
  * SELECTION LAYER ONLY: reads the score matrix and returns a pick. It NEVER reads or writes a model
    parameter - optimizer/model/strength/context stay FROZEN; we import optimizer.points/expected_points
    READ-ONLY (exactly as the EV-optimizer is itself a selection layer over match_distribution).
  * It does NOT fire by itself. run_matchday invokes it only when variance_lam > 0, and WHEN to do that is
    the deferred activation gate (post-MD3: F35 needs H4-fixed §5; F34 needs >=2-3 matchdays of standings_log
    before any threshold is real - until then the placement-MC reports only a scenario band).

The deferred forensics (placement-MC, H1-H4 hypothesis tests, eval-panel, activation thresholds) consume
THIS module's `select`/`ev_cost`; they are out of scope for the skeleton.
"""
from __future__ import annotations
import math

import numpy as np

from src.optimizer import points, expected_points, PLAUSIBILITY_FLOOR


def points_second_moment(pred: tuple[int, int], matrix: np.ndarray) -> float:
    """E[pts^2] of predicting `pred`, integrated against the score distribution (mirrors expected_points)."""
    n = matrix.shape[0]
    total = 0.0
    for a in range(n):
        for b in range(n):
            p = matrix[a, b]
            if p > 0.0:
                total += p * points(pred, (a, b)) ** 2
    return total


def pts_mean_sd(pred: tuple[int, int], matrix: np.ndarray) -> tuple[float, float]:
    """(E[pts], SD[pts]) for a candidate pick over the score matrix. SD via E[pts^2] - E[pts]^2 (clamped >=0)."""
    ev = expected_points(pred, matrix)
    var = max(0.0, points_second_moment(pred, matrix) - ev * ev)
    return ev, math.sqrt(var)


def select(matrix: np.ndarray, lam: float = 0.0,
           plausibility_floor: float = PLAUSIBILITY_FLOOR) -> dict:
    """argmax over plausible scorelines of  E[pts] + lam * SD[pts].

    lam = 0 -> the pure E[pts] argmax == optimizer.optimize (identical scan order + strict-> tie-break).
    Returns {'pick','ev','sd','score','lam','table'} - the {pick,ev,table} keys mirror optimizer.optimize
    so run_matchday can swap this in transparently; table = top-10 by the mean-variance score.
    """
    n = matrix.shape[0]
    best, best_score, best_ev, best_sd, table = None, -1e18, 0.0, 0.0, []
    for i in range(n):
        for j in range(n):
            if matrix[i, j] < plausibility_floor:
                continue
            ev, sd = pts_mean_sd((i, j), matrix)
            score = ev + lam * sd
            table.append({"pred": (i, j), "ev": ev, "sd": sd, "score": score, "p": float(matrix[i, j])})
            if score > best_score:
                best, best_score, best_ev, best_sd = (i, j), score, ev, sd
    if best is None:                                  # floor too high -> fall back to modal (mirrors optimizer)
        idx = np.unravel_index(int(np.argmax(matrix)), matrix.shape)
        best = (int(idx[0]), int(idx[1]))
        best_ev, best_sd = pts_mean_sd(best, matrix)
        best_score = best_ev + lam * best_sd
    table.sort(key=lambda r: -r["score"])
    return {"pick": best, "ev": best_ev, "sd": best_sd, "score": best_score, "lam": lam, "table": table[:10]}


def ev_cost(matrix: np.ndarray, lam: float,
            plausibility_floor: float = PLAUSIBILITY_FLOOR) -> float:
    """Per-game E[pts] SACRIFICED by the lambda-tilt = E[pts](EV-argmax) - E[pts](variance pick).

    >= 0 by construction (the EV-argmax maximizes E[pts]); = 0 at lam = 0. This is the REAL per-game cost
    that replaces the auditor's stylized -0.4; the deferred placement-MC weighs it against the P(top-3) gain.
    """
    from src.optimizer import optimize
    ev_pick = optimize(matrix, plausibility_floor)["pick"]
    var_pick = select(matrix, lam, plausibility_floor)["pick"]
    return expected_points(ev_pick, matrix) - expected_points(var_pick, matrix)
