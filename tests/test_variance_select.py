"""ANNEX V skeleton: the lambda risk-dial (src/variance_select). BUILD-NOT-FIRE.

Core invariants: lam=0 reproduces optimizer.optimize EXACTLY (so run_matchday's default path is byte-identical);
lam>0 tilts toward higher-variance picks at a non-negative, quantified E[pts] cost (ev_cost). Pure selection
layer over a frozen matrix - no model parameter touched.
"""
from __future__ import annotations
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import variance_select as vs
from src.optimizer import optimize, expected_points


def _matrix():
    """A deterministic, favorite-home-ish score distribution (rows = home goals, cols = away)."""
    vals = np.array([
        [0.08, 0.06, 0.03, 0.01, 0.0, 0.0],
        [0.18, 0.12, 0.05, 0.01, 0.0, 0.0],
        [0.10, 0.09, 0.04, 0.01, 0.0, 0.0],
        [0.05, 0.03, 0.01, 0.00, 0.0, 0.0],
        [0.01, 0.00, 0.00, 0.00, 0.0, 0.0],
        [0.00, 0.00, 0.00, 0.00, 0.0, 0.0],
    ], dtype=float)
    return vals / vals.sum()


def _flip_matrix():
    """A near-even, draw-heavy distribution with a genuine ev<->sd tradeoff. By hand: the EV-argmax is the
    modal draw 1-1 (ev 3.3, sd 3.74); the favorite wins 1-0 / 0-1 carry LOWER ev (3.2) but HIGHER sd (3.89),
    so for lambda > ~0.67 the mean-variance dial tilts off 1-1 onto a 1-0/0-1 at a real cost (ev 3.3->3.2)."""
    m = np.zeros((4, 4))
    m[1, 0] = 0.30; m[2, 0] = 0.05; m[0, 1] = 0.30; m[0, 2] = 0.05; m[1, 1] = 0.30
    return m


class TestLambdaZeroIsOptimizer(unittest.TestCase):
    def test_pick_and_ev_match_optimizer(self):
        m = _matrix()
        s = vs.select(m, lam=0.0)
        o = optimize(m)
        self.assertEqual(s["pick"], o["pick"])                  # identical scan + tie-break
        self.assertAlmostEqual(s["ev"], o["ev"], places=12)

    def test_ev_cost_zero_at_lam0(self):
        self.assertEqual(vs.ev_cost(_matrix(), 0.0), 0.0)


class TestVarianceTilt(unittest.TestCase):
    def test_tilt_moves_the_pick_at_a_positive_cost(self):
        m = _flip_matrix()
        # lam=0 picks the modal draw 1-1; a tilt moves OFF it onto a higher-sd favorite win, at ev_cost>0
        self.assertEqual(vs.select(m, 0.0)["pick"], optimize(m)["pick"])
        self.assertNotEqual(vs.select(m, 2.0)["pick"], optimize(m)["pick"])
        self.assertGreater(vs.ev_cost(m, 2.0), 0.0)

    def test_cost_nonnegative_across_sweep(self):
        m = _matrix()
        for lam in (0.5, 1.0, 2.0, 5.0):
            self.assertGreaterEqual(vs.ev_cost(m, lam), 0.0)

    def test_high_lambda_raises_sd(self):
        m = _matrix()
        self.assertGreaterEqual(vs.select(m, 10.0)["sd"], vs.select(m, 0.0)["sd"])

    def test_table_contract_keys(self):
        row = vs.select(_matrix(), 1.0)["table"][0]
        for k in ("pred", "ev", "p"):          # the optimizer.optimize contract run_matchday relies on
            self.assertIn(k, row)
        for k in ("sd", "score"):              # the dial extras
            self.assertIn(k, row)


class TestMeanSd(unittest.TestCase):
    def test_degenerate_matrix(self):
        md = np.zeros((4, 4)); md[1, 0] = 1.0           # all mass on 1-0
        ev, sd = vs.pts_mean_sd((1, 0), md)
        self.assertAlmostEqual(ev, 9.0, places=12)      # exact 1-0 vs 1-0 = 9
        self.assertAlmostEqual(sd, 0.0, places=12)      # no spread
        ev2, sd2 = vs.pts_mean_sd((0, 1), md)
        self.assertAlmostEqual(ev2, expected_points((0, 1), md), places=12)
        self.assertAlmostEqual(sd2, 0.0, places=12)

    def test_determinism(self):
        m = _matrix()
        self.assertEqual(vs.select(m, 2.0)["pick"], vs.select(m, 2.0)["pick"])


if __name__ == "__main__":
    unittest.main()
