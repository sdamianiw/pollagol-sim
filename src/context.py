"""M5 context - §5 motivation / rotation / dead-rubber adjustments (Track B).

Applies a one-line, SOURCED context flag to a forecast score distribution, adjusting BOTH the mean
(expected total goals) and the variance (spread). Runs on the DC matrix so it is independent of M3's
solver; the optimizer (M4) then runs on the adjusted distribution. numpy.

Each flag carries (mu_factor, variance_factor): mu re-weights total-goal mass (mean); variance tempers
the distribution (>1 flattens -> wider, <1 sharpens -> tighter).

WARNING (H4, verified 2026-06-06 - post-DC tilt is NOT a pre-DC mu re-anchor):
This adjusts a FINISHED DC matrix POST-hoc; mu_factor is an exponential tilt (mu_f ** total), NOT a re-anchor
of mu fed to fit_lambdas (M3). They are NOT equivalent. Worse: the variance temper (m ** (1/var_f)) flattens a
RIGHT-SKEWED score distribution, which itself pushes the MEAN up - and for var_f>1 flags this OVERWHELMS
mu_factor and can INVERT the intended direction. Measured on score_matrix(1.5, 1.1):
  neutral     (mu_f1.00, var_f1.06): expected_total d=+0.069  (NOT mean-neutral)
  rotation    (mu_f0.96, var_f1.25): d=+0.179  (should LOWER goals -> moves UP = WRONG)
  dead_rubber (mu_f0.90, var_f1.35): d=+0.131  (should LOWER goals -> moves UP = WRONG)
The LIVE default is `neutral` (small +0.069 perturbation, tolerable). Do NOT trust non-neutral flags live
until M5 is re-architected to re-anchor mu PRE-DC (separate GO). Behavior is pinned in
tests/test_context.py (test_dead_rubber_pinned / test_neutral_not_strictly_mean_neutral) to catch drift.
"""
from __future__ import annotations
import numpy as np

# flag -> (mu_factor, variance_factor, note). Documented assumptions, not trained.
CONTEXT_RULES = {
    "dead_rubber": (0.90, 1.35, "dead rubber: low stakes -> fewer goals, wider spread"),
    "rotation":    (0.96, 1.25, "rotated XI -> less predictable, wider spread"),
    "high_stakes": (1.05, 0.90, "knockout/must-win -> a touch more open, tighter spread"),
    "neutral":     (1.00, 1.06, "neutral venue (WC group) -> mild extra uncertainty"),
}


def _totals_grid(n: int) -> np.ndarray:
    return np.add.outer(np.arange(n), np.arange(n))


def expected_total(matrix: np.ndarray) -> float:
    return float((matrix * _totals_grid(matrix.shape[0])).sum())


def var_total(matrix: np.ndarray) -> float:
    tg = _totals_grid(matrix.shape[0])
    mean = (matrix * tg).sum()
    return float((matrix * (tg - mean) ** 2).sum())


def apply_context(matrix: np.ndarray, flags, source: str = "manual") -> tuple[np.ndarray, dict]:
    """Adjust a score distribution for §5 context. Returns (matrix', context_flag).

    flags: a flag name or list of names from CONTEXT_RULES.
    context_flag: {text, source, flags, mu_factor, variance_factor} (one-line, sourced).
    """
    if isinstance(flags, str):
        flags = [flags]
    mu_f, var_f, notes = 1.0, 1.0, []
    for fl in flags:
        if fl not in CONTEXT_RULES:
            raise ValueError(f"unknown context flag: {fl!r} (known: {sorted(CONTEXT_RULES)})")
        mf, vf, note = CONTEXT_RULES[fl]
        mu_f *= mf
        var_f *= vf
        notes.append(note)
    n = matrix.shape[0]
    m = matrix * (mu_f ** _totals_grid(n))        # MEAN shift on total goals
    m = m / m.sum()
    if abs(var_f - 1.0) > 1e-12:
        m = m ** (1.0 / var_f)                     # VARIANCE temper (>1 widens, <1 sharpens)
        m = m / m.sum()
    flag = {"text": "; ".join(notes) if notes else "no context", "source": source,
            "flags": list(flags), "mu_factor": round(mu_f, 4), "variance_factor": round(var_f, 4)}
    return m, flag
