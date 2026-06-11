"""M4 optimizer - argmax E[competition points] over the DC score distribution (Track B).

Objective = the LOCKED additive rubric (memory/rules.md): exact 2 + outcome 3 + per-team goals (<=2)
+ GD 1. Optimize E[points], NOT P(exact). The 4 locked unit tests are the correctness gate. Rejects
scorelines below a plausibility floor (PM7: never recommend an implausible exact score). numpy.
"""
from __future__ import annotations
import numpy as np

PLAUSIBILITY_FLOOR = 0.005       # a recommended pick must carry at least this probability mass


def _sgn(x: int) -> int:
    return (x > 0) - (x < 0)


def points(pred: tuple[int, int], actual: tuple[int, int]) -> int:
    """Competition points for predicting `pred` when the result is `actual` (additive rubric)."""
    ph, pa = pred
    ah, aa = actual
    pts = 0
    if ph == ah and pa == aa:
        pts += 2                                              # exact score
    if _sgn(ph - pa) == _sgn(ah - aa):
        pts += 3                                              # correct outcome (1 / X / 2)
    pts += (1 if ph == ah else 0) + (1 if pa == aa else 0)    # team goals (max 2)
    if (ph - pa) == (ah - aa):
        pts += 1                                              # goal difference
    return pts


def expected_points(pred: tuple[int, int], matrix: np.ndarray) -> float:
    """E[points] of predicting `pred`, integrated against the score distribution."""
    n = matrix.shape[0]
    total = 0.0
    for a in range(n):
        for b in range(n):
            p = matrix[a, b]
            if p > 0.0:
                total += p * points(pred, (a, b))
    return total


def optimize(matrix: np.ndarray, plausibility_floor: float = PLAUSIBILITY_FLOOR) -> dict:
    """argmax E[points] over plausible candidate scorelines (P >= floor).

    Returns {'pick': (i,j), 'ev': float, 'table': top-10 [{pred, ev, p}]}.
    """
    n = matrix.shape[0]
    best, best_ev, table = None, -1.0, []
    for i in range(n):
        for j in range(n):
            if matrix[i, j] < plausibility_floor:
                continue
            ev = expected_points((i, j), matrix)
            table.append({"pred": (i, j), "ev": ev, "p": float(matrix[i, j])})
            if ev > best_ev:
                best, best_ev = (i, j), ev
    if best is None:                                          # floor too high -> fall back to modal
        idx = np.unravel_index(int(np.argmax(matrix)), matrix.shape)
        best = (int(idx[0]), int(idx[1]))
        best_ev = expected_points(best, matrix)
    table.sort(key=lambda r: -r["ev"])
    return {"pick": best, "ev": best_ev, "table": table[:10]}
