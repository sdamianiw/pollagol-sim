"""M2 strength - per-match outcome probabilities (Track B).

de-vig market 1X2 (single book-set policy) -> {home,draw,away}; optional totals -> p_over + line;
Elo fallback for illiquid/missing markets. Reuses pool/leverage.py de-vig (no second copy).

Book-set policy (memory/rules.md RB3): ONE book/format per call; overround re-derived per set and
returned. Decimal odds carry vig -> decimal_to_prob is RAW; ALWAYS de-vig it (never use 1/odds as a
clean probability, L9). Live The-Odds-API path = american; football-data.co.uk backtest path = decimal.
Pure stdlib + reuse.
"""
from __future__ import annotations
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pool.leverage import american_to_prob, devig

# Elo fallback constants (documented modeling assumptions; NOT trained/ML).
HOME_ADV_ELO = 65.0     # ~standard home-field Elo bonus; 0 when neutral (WC group = neutral)
DRAW_MAX = 0.28         # peak draw rate for evenly-matched sides (tournament-ish prior)
DRAW_SCALE = 380.0      # Elo-diff scale over which the draw probability decays
EPS = 1e-9


def decimal_to_prob(odds: float) -> float:
    """Decimal odds -> RAW (vig-inclusive) implied probability = 1/odds.
    Carries the book's overround; callers MUST de-vig (see devig_1x2)."""
    o = float(odds)
    if o <= 1.0:
        raise ValueError(f"decimal odds must be > 1.0, got {o}")
    return 1.0 / o


def _to_implied(odds: dict, fmt: str) -> dict:
    try:
        conv = {"decimal": decimal_to_prob, "american": american_to_prob}[fmt]
    except KeyError:
        raise ValueError(f"unknown odds fmt: {fmt!r} (expected 'decimal' or 'american')")
    return {k: conv(v) for k, v in odds.items()}


def devig_1x2(odds: dict, fmt: str = "decimal") -> tuple[dict, float]:
    """1X2 odds {home,draw,away} -> (de-vigged probs summing to 1, overround). Single book-set."""
    return devig(_to_implied(odds, fmt))


def totals_to_probs(over_odds: float, under_odds: float, fmt: str = "decimal") -> tuple[dict, float]:
    """Two-way over/under -> (de-vigged {over,under}, overround)."""
    return devig(_to_implied({"over": over_odds, "under": under_odds}, fmt))


def elo_probs(elo_home: float, elo_away: float, neutral: bool = False) -> dict:
    """Minimal draw-aware Elo -> {home,draw,away}, used when the market is illiquid/missing (R1).
    W = expected score for home (draw counts half) via logistic Elo; draw peaks when evenly matched."""
    dr = float(elo_home) - float(elo_away) + (0.0 if neutral else HOME_ADV_ELO)
    w = 1.0 / (1.0 + 10.0 ** (-dr / 400.0))
    p_draw = DRAW_MAX * math.exp(-(dr / DRAW_SCALE) ** 2)
    p = {"home": max(w - p_draw / 2.0, EPS),
         "draw": max(p_draw, EPS),
         "away": max((1.0 - w) - p_draw / 2.0, EPS)}
    tot = sum(p.values())
    return {k: v / tot for k, v in p.items()}


def match_strength(match: dict) -> dict:
    """Unified per-match strength.

    match (market): {'odds_1x2': {'home','draw','away'}, 'fmt': 'decimal'|'american',
                     optional 'totals': {'over','under','line'}}
    match (fallback): {'elo': {'home','away', optional 'neutral'}}

    Returns {probs, overround, total_line, p_over, source}; source='market' if odds present else 'elo'.
    """
    if match.get("odds_1x2"):
        fmt = match.get("fmt", "decimal")
        probs, overround = devig_1x2(match["odds_1x2"], fmt)
        total_line, p_over = None, None
        tot = match.get("totals")
        if tot:
            tp, _ = totals_to_probs(tot["over"], tot["under"], fmt)
            total_line, p_over = tot.get("line"), tp["over"]
        return {"probs": probs, "overround": overround, "total_line": total_line,
                "p_over": p_over, "source": "market"}
    if match.get("elo"):
        e = match["elo"]
        return {"probs": elo_probs(e["home"], e["away"], neutral=e.get("neutral", False)),
                "overround": None, "total_line": None, "p_over": None, "source": "elo"}
    raise ValueError("match needs 'odds_1x2' or 'elo'")
