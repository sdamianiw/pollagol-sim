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

RHO = -0.05                      # Dixon-Coles low-score correction (frozen default; live path unless rho_fit)
RHO_LO, RHO_HI = -0.20, 0.10     # L19 fitted-ρ band (DC literature |ρ|~0.03-0.15 -> roomy; clamp telemetry G-RHO3)
MAX_GOALS = 8                    # score grid 0..8 per side
LAMBDA_MIN, LAMBDA_MAX = 0.15, 4.0   # clamp (R6)
PRIOR_MU = 2.6                   # tournament prior expected total goals (shrink target)
SHRINK = 0.10                    # shrink weight of total_line toward PRIOR_MU
TOTAL_LINE = 2.5                 # default O/U line for the price->mu_eff inversion (rules.md M7 design v, P4a)
_BISECT_ITERS = 50
_RHO_BISECT_ITERS = 18           # outer ρ search (range 0.30 -> ~1e-6 precision; inner _solve_s stays 50)

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


def fit_dc(probs: dict, mu: float, rho_fit: bool = True) -> tuple[float, float, float, str | None]:
    """L19 ρ-fit. With μ PINNED (from the totals price), solve (s, ρ) to match (P_home, P_draw):
    outer bisection on ρ to match the de-vig MARKET P_draw, inner `_solve_s` to match P_home at each ρ
    -> 2 DOF / 2 constraints, exactly identified. Implied draw is DECREASING in ρ (ρ↓ inflates the
    diagonal cells (0,0),(1,1)). ρ is clamped to [RHO_LO, RHO_HI]; `clamp` in {None,'lo','hi'} flags a
    band-edge clamp for telemetry (G-RHO3). rho_fit=False -> ρ frozen at RHO (byte-identical to the old
    fit_lambdas + RHO path). I3: reads ONLY de-vig market probs, NEVER a result.
    Returns (lambda_home, lambda_away, rho, clamp)."""
    mu = (1.0 - SHRINK) * float(mu) + SHRINK * PRIOR_MU     # R6 shrink, identical to fit_lambdas (totals path)
    if not rho_fit:
        lh, la = _split(mu, _solve_s(probs["home"], mu, RHO))
        return lh, la, RHO, None
    target = probs["draw"]

    def implied_draw(r: float) -> float:
        lh, la = _split(mu, _solve_s(probs["home"], mu, r))
        return implied_1x2(score_matrix(lh, la, r))["draw"]

    if target >= implied_draw(RHO_LO):          # most-negative ρ can't make enough draws -> under-deliver
        rho, clamp = RHO_LO, "lo"
    elif target <= implied_draw(RHO_HI):        # even least draws exceed target (rare; draw-poor board)
        rho, clamp = RHO_HI, "hi"
    else:
        lo, hi = RHO_LO, RHO_HI
        for _ in range(_RHO_BISECT_ITERS):
            rho = 0.5 * (lo + hi)
            if implied_draw(rho) > target:      # too many draws -> raise ρ (lowers draw)
                lo = rho
            else:                               # too few draws -> lower ρ
                hi = rho
        rho, clamp = 0.5 * (lo + hi), None
    lh, la = _split(mu, _solve_s(probs["home"], mu, rho))
    return lh, la, rho, clamp


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


def match_distribution(strength: dict, rho: float = RHO, max_goals: int = MAX_GOALS,
                       rho_fit: bool = False) -> np.ndarray:
    """End-to-end: M2 strength dict -> DC score matrix.

    P4a: when the totals PRICE is present, the total-goals signal enters via mu_eff = mu_from_pover(p_over)
    (rules.md M7 design v) - NOT the (often pinned) line - mirroring evals.backtest.fixture_eval. mu_eff is
    passed as the line to fit_lambdas. Falls back to the line / nested-solve when p_over is absent (e.g. Elo).

    L19: rho_fit=True unfreezes ρ (fit_dc) to match the market P_draw on the totals-present path -> clears
    L17 draw-compression + favorite-inversion. Default OFF -> byte-identical to the frozen ρ path (BUILD≠FIRE
    live; the flip to default-ON is Sebas's GO after the M7 re-run passes G-RHO2)."""
    p_over = strength.get("p_over")
    line = strength.get("total_line")
    if p_over is not None:
        mu_eff = mu_from_pover(p_over, line if line else TOTAL_LINE)
        if rho_fit:
            lh, la, rho_used, _ = fit_dc(strength["probs"], mu_eff, rho_fit=True)
            return score_matrix(lh, la, rho_used, max_goals)
        lh, la = fit_lambdas(strength["probs"], mu_eff, rho)
    else:
        lh, la = fit_lambdas(strength["probs"], line, rho)
    return score_matrix(lh, la, rho, max_goals)


def dc_fit_info(strength: dict, rho_fit: bool = False) -> tuple[float, str | None]:
    """Live DC-fit diagnostics (G-RHO3 telemetry): (rho_used, clamp). Frozen path / no totals -> (RHO, None).
    Deterministic mirror of the fit inside match_distribution -> same (probs, mu_eff) => same ρ."""
    p_over = strength.get("p_over")
    if p_over is None or not rho_fit:
        return RHO, None
    mu_eff = mu_from_pover(p_over, strength.get("total_line") or TOTAL_LINE)
    _, _, rho_used, clamp = fit_dc(strength["probs"], mu_eff, rho_fit=True)
    return rho_used, clamp


def rho_sensitivity(strength: dict) -> dict:
    """Implied 1X2 at rho=0 vs rho=RHO (R6 diagnostic; most relevant when totals absent)."""
    out = {}
    for r in (0.0, RHO):
        lh, la = fit_lambdas(strength["probs"], strength.get("total_line"), r)
        out[r] = implied_1x2(score_matrix(lh, la, r))
    return out
