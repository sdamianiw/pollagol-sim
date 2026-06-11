"""M3 model - Dixon-Coles bivariate-Poisson score distribution (Track B).

de-vigged 1X2 (+ optional totals line) -> (lambda_home, lambda_away) -> score matrix P(i,j).
Fixed low-score correction rho. clamp + shrink toward a tournament prior (R6: prevent the
'one factor -> extreme scoreline' failure). numpy.

lambda split (memory/rules.md / MASTER S4): lambda_home=(mu+s)/2, lambda_away=(mu-s)/2, clamped.
  totals present -> mu = shrink(total_line); 1-D solve supremacy s to match de-vigged P(home win).
  totals absent  -> nested solve: mu (to match P(draw)) outer, s (to match P(home win)) inner.
"""
from __future__ import annotations
import math
from math import factorial

import numpy as np

RHO = -0.05                      # Dixon-Coles low-score correction (fixed, documented)
MAX_GOALS = 8                    # score grid 0..8 per side
LAMBDA_MIN, LAMBDA_MAX = 0.15, 4.0   # clamp (R6)
PRIOR_MU = 2.6                   # tournament prior expected total goals (shrink target)
SHRINK = 0.10                    # shrink weight of total_line toward PRIOR_MU
TOTAL_LINE = 2.5                 # default O/U line for the price->mu_eff inversion (rules.md M7 design v, P4a)
_BISECT_ITERS = 50

_FACT = np.array([factorial(k) for k in range(MAX_GOALS + 1)], dtype=float)


def _poisson_col(lam: float) -> np.ndarray:
    k = np.arange(MAX_GOALS + 1)
    return np.exp(-lam) * lam ** k / _FACT


def _tau(rho: float, lh: float, la: float) -> np.ndarray:
    """Dixon-Coles correction on the four low-score cells."""
    t = np.ones((MAX_GOALS + 1, MAX_GOALS + 1))
    t[0, 0] = 1.0 - lh * la * rho
    t[0, 1] = 1.0 + lh * rho
    t[1, 0] = 1.0 + la * rho
    t[1, 1] = 1.0 - rho
    return t


def score_matrix(lambda_home: float, lambda_away: float, rho: float = RHO,
                 max_goals: int = MAX_GOALS) -> np.ndarray:
    """P(i goals home, j goals away), i,j in 0..max_goals. Clamped + normalized to sum 1."""
    lh = min(max(lambda_home, LAMBDA_MIN), LAMBDA_MAX)
    la = min(max(lambda_away, LAMBDA_MIN), LAMBDA_MAX)
    m = _tau(rho, lh, la) * _poisson_col(lh)[:, None] * _poisson_col(la)[None, :]
    m = np.clip(m, 0.0, None)
    return m / m.sum()


def implied_1x2(matrix: np.ndarray) -> dict:
    """Outcome probabilities implied by a score matrix."""
    return {"home": float(np.tril(matrix, -1).sum()),   # i > j
            "draw": float(np.trace(matrix)),            # i == j
            "away": float(np.triu(matrix, 1).sum())}    # j > i


def _split(mu: float, s: float) -> tuple[float, float]:
    return max((mu + s) / 2.0, LAMBDA_MIN), max((mu - s) / 2.0, LAMBDA_MIN)


def _solve_s(target_home: float, mu: float, rho: float) -> float:
    """Bisection on supremacy s to match P(home win)=target_home (monotone increasing in s)."""
    lo, hi = -mu + 1e-3, mu - 1e-3
    for _ in range(_BISECT_ITERS):
        s = 0.5 * (lo + hi)
        lh, la = _split(mu, s)
        if implied_1x2(score_matrix(lh, la, rho))["home"] < target_home:
            lo = s
        else:
            hi = s
    return 0.5 * (lo + hi)


def fit_lambdas(probs: dict, total_line: float | None = None, rho: float = RHO) -> tuple[float, float]:
    """Solve (lambda_home, lambda_away) so DC-implied 1X2 ~ de-vigged probs."""
    if total_line is not None:
        mu = (1.0 - SHRINK) * float(total_line) + SHRINK * PRIOR_MU
        return _split(mu, _solve_s(probs["home"], mu, rho))
    # totals absent: outer bisection on mu to match P(draw) (draw decreases as mu rises)
    lo, hi = 0.6, 5.0
    for _ in range(_BISECT_ITERS):
        mu = 0.5 * (lo + hi)
        lh, la = _split(mu, _solve_s(probs["home"], mu, rho))
        if implied_1x2(score_matrix(lh, la, rho))["draw"] > probs["draw"]:
            lo = mu
        else:
            hi = mu
    mu = 0.5 * (lo + hi)
    return _split(mu, _solve_s(probs["home"], mu, rho))


def poisson_over_prob(mu: float, line: float = TOTAL_LINE) -> float:
    """P(total goals > line) for total ~ Poisson(mu). For line=2.5 -> P(T>=3). Monotone increasing in mu.

    VALID FOR HALF-LINES (x.5) ONLY. Integer/quarter lines collapse via floor(line)+1 to the same threshold
    as the adjacent x.5 (2.0/2.25/2.5/2.75 -> P(T>=3)) and IGNORE push/split semantics -- handling those is
    pending P4c (enforced at runtime by the x.5 guard in src/run_matchday.py; do NOT assume generalization).
    Demonstrated: mu_from_pover(0.55, 2.0) == mu_from_pover(0.55, 2.5) == 2.8826."""
    k = int(math.floor(line)) + 1                  # 2.5 -> threshold T>=3 -> sum P(T<=2)
    cum = term = math.exp(-mu)                      # i = 0
    for i in range(1, k):
        term *= mu / i
        cum += term
    return 1.0 - cum


def mu_from_pover(p_over: float, line: float = TOTAL_LINE, lo: float = 0.2, hi: float = 8.0,
                  iters: int = 60) -> float:
    """Effective total mu s.t. P(T>line)=p_over, T~Poisson (rules.md M7 design v, FROZEN 2026-06-03).
    The total-goals signal lives in the over/under PRICE, not the (often pinned) line -> recover mu by
    inverting the de-vigged over prob (monotone -> bisection). Fed to the FROZEN fit_lambdas as the line.
    P4a: this is the ONE μ_eff model (relocated into src/; the backtest re-imports it) - no second model (I4).
    Inherits the x.5-only validity of poisson_over_prob (integer/quarter lines need push/split semantics, P4c)."""
    p = min(max(p_over, 1e-6), 1.0 - 1e-6)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if poisson_over_prob(mid, line) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def match_distribution(strength: dict, rho: float = RHO, max_goals: int = MAX_GOALS) -> np.ndarray:
    """End-to-end: M2 strength dict -> DC score matrix.

    P4a: when the totals PRICE is present, the total-goals signal enters via mu_eff = mu_from_pover(p_over)
    (rules.md M7 design v) - NOT the (often pinned) line - mirroring evals.backtest.fixture_eval. mu_eff is
    passed as the line to the FROZEN fit_lambdas. Falls back to the line / nested-solve when p_over is absent
    (e.g. Elo source)."""
    p_over = strength.get("p_over")
    line = strength.get("total_line")
    if p_over is not None:
        mu_eff = mu_from_pover(p_over, line if line else TOTAL_LINE)
        lh, la = fit_lambdas(strength["probs"], mu_eff, rho)
    else:
        lh, la = fit_lambdas(strength["probs"], line, rho)
    return score_matrix(lh, la, rho, max_goals)


def rho_sensitivity(strength: dict) -> dict:
    """Implied 1X2 at rho=0 vs rho=RHO (R6 diagnostic; most relevant when totals absent)."""
    out = {}
    for r in (0.0, RHO):
        lh, la = fit_lambdas(strength["probs"], strength.get("total_line"), r)
        out[r] = implied_1x2(score_matrix(lh, la, r))
    return out
