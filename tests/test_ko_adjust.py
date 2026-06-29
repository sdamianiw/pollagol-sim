# -*- coding: utf-8 -*-
"""TDD for src/ko_adjust.py (non-frozen KO 90'->120' transform; FULL120 = pens excluded).
Mirrors tests/test_optimizer.py style: locked boundary identities first, then integration."""
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ko_adjust import ko_adjust, _et_pmf            # noqa: E402
from src.model import score_matrix                       # noqa: E402  (frozen, read-only)
from src.optimizer import optimize                       # noqa: E402  (frozen, read-only)

N = 9  # MAX_GOALS+1


def _zeros():
    return np.zeros((N, N), dtype=float)


class TestKoAdjust(unittest.TestCase):

    # 1 - off-diagonal mass is invariant (KO games not level at 90' END at 90')
    def test_off_diagonal_invariant(self):
        M = _zeros()
        M[1, 0] = 0.5  # home win at 90'
        M[0, 1] = 0.5  # away win at 90'
        r = ko_adjust(M, ko_rule="FULL120")
        self.assertTrue(np.allclose(r["dist_120"], M))
        self.assertAlmostEqual(r["p_draw_scored"], 0.0, places=12)

    # 2 - normalization invariant
    def test_dist_120_sums_to_one(self):
        M = score_matrix(1.3, 1.0)
        r = ko_adjust(M, ko_rule="FULL120")
        self.assertAlmostEqual(float(r["dist_120"].sum()), 1.0, places=9)

    # 3 - CORRECTED FULL120 semantics: scored-draw mass is POSITIVE and SMALLER than the 90' draw mass
    def test_full120_scored_draw_positive_and_below_90(self):
        M = score_matrix(1.3, 1.0)
        r = ko_adjust(M, cageyness=0.65, ko_rule="FULL120")
        self.assertGreater(r["p_draw_scored"], 0.0)                 # pens excluded -> a draw CAN be scored
        self.assertLess(r["p_draw_scored"], r["p_draw_90"])         # ET resolves some 90' draws
        # outcome masses sum to 1
        self.assertAlmostEqual(r["p_home_win"] + r["p_draw_scored"] + r["p_away_win"], 1.0, places=9)

    # 4 - cageyness=0 (no ET goals) -> all 90' draws stay level -> FULL120 == REG90 == identity
    def test_cageyness_zero_is_identity(self):
        M = score_matrix(1.3, 1.0)
        r = ko_adjust(M, cageyness=0.0, ko_rule="FULL120")
        self.assertTrue(np.allclose(r["dist_120"], M, atol=1e-12))
        self.assertAlmostEqual(r["p_draw_scored"], r["p_draw_90"], places=12)

    # 5 - f is monotonically DECREASING in cageyness (more ET scoring -> fewer scored draws)
    def test_f_monotonic_in_cageyness(self):
        M = score_matrix(1.3, 1.0)
        f_lo = ko_adjust(M, cageyness=0.3, ko_rule="FULL120")["f_model"]
        f_hi = ko_adjust(M, cageyness=0.9, ko_rule="FULL120")["f_model"]
        self.assertGreater(f_lo, f_hi)
        self.assertLessEqual(f_hi, 1.0)
        self.assertGreaterEqual(f_lo, 0.0)

    # 6 - REG90 is the exact identity
    def test_reg90_identity(self):
        M = score_matrix(1.3, 1.0)
        r = ko_adjust(M, ko_rule="REG90")
        self.assertTrue(np.allclose(r["dist_120"], M, atol=1e-12))
        self.assertAlmostEqual(r["f_model"], 1.0, places=9)

    # 7 - optimizer reuse contract: the overall argmax == better of {best_draw, best_decisive}
    def test_optimizer_reuse_contract(self):
        M = score_matrix(1.3, 1.0)
        r = ko_adjust(M, ko_rule="FULL120")
        # independently re-run optimize on the transformed distribution
        self.assertEqual(tuple(r["ev_argmax"]), tuple(optimize(r["dist_120"])["pick"]))
        better = max([x for x in (r["best_draw"], r["best_decisive"]) if x is not None], key=lambda x: x["ev"])
        self.assertEqual(tuple(better["pred"]), tuple(r["ev_argmax"]))

    # 8 - GOLDEN hand-case: all mass on (1,1), mu_et=0.5 -> p_draw_scored = sum_n P(n)^2 ~ 0.4658
    def test_golden_handcase(self):
        M = _zeros()
        M[1, 1] = 1.0
        r = ko_adjust(M, mu_et=0.5, ko_rule="FULL120")
        pmf = _et_pmf(0.5)
        expected_draw = float((pmf * pmf).sum())               # P(a == b)
        self.assertAlmostEqual(r["p_draw_scored"], expected_draw, places=9)
        self.assertAlmostEqual(r["p_draw_scored"], 0.4658, places=3)
        self.assertAlmostEqual(float(r["dist_120"].sum()), 1.0, places=9)


    # 9 - GRID-EDGE: an a!=b ET outcome must NEVER be clamped onto the diagonal (regression for the
    #     min(k+a,n-1) false-draw bug). M=(7,7), mu_et=1.0: only a,b in {0,1} stay on-grid; since Poisson(1)
    #     has pmf[0]==pmf[1], the kept mass is symmetric -> scored-draw is EXACTLY 0.5, wins 0.25/0.25.
    def test_grid_edge_no_false_diagonal(self):
        M = _zeros()
        M[7, 7] = 1.0
        r = ko_adjust(M, mu_et=1.0, ko_rule="FULL120")
        self.assertAlmostEqual(r["p_draw_scored"], 0.5, places=9)
        self.assertAlmostEqual(r["p_home_win"], 0.25, places=9)
        self.assertAlmostEqual(r["p_away_win"], 0.25, places=9)
        self.assertAlmostEqual(float(r["dist_120"].sum()), 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
