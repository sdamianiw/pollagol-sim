"""Shared total-line helpers (Track B).

is_half_line is the x.5-only invariant (H1 / P4c): the run_matchday x.5 guard AND the line-distribution
probe both consume ONE definition here - no split, no drift. poisson_over_prob/mu_from_pover (src/model.py,
FROZEN) are correct ONLY for half-lines (x.5); integer/quarter lines (2.0, 2.25, 2.75, 3.0) collapse via
floor(line)+1 and ignore push/split semantics, so the live engine must STOP on them (never coerce). Stdlib only.
"""
from __future__ import annotations


def is_half_line(line) -> bool:
    """True iff `line` is an x.5 half-line (1.5, 2.5, 3.5, ...). Integer (2.0/3.0) and quarter (2.25/2.75)
    lines are FALSE. None is FALSE (no totals -> caller falls back to the h2h/Elo path, not the guard)."""
    if line is None:
        return False
    x2 = float(line) * 2.0
    return abs(x2 - round(x2)) < 1e-9 and int(round(x2)) % 2 == 1
