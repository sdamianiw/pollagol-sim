"""M4 optimizer - TDD (Gate 7). argmax E[competition points] over the DC score distribution.
The 4 LOCKED unit tests (memory/rules.md) are the non-negotiable correctness gate.
points(predicted, actual); rubric = outcome 3 + GD 1 + per-team goals (<=2) + exact 3 (additive)."""
from __future__ import annotations
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.optimizer import points, expected_points, optimize, PLAUSIBILITY_FLOOR


def _toy_matrix():
    from src.model import score_matrix
    return score_matrix(1.6, 0.8)   # heavy home favorite, low-scoring


class TestOptimizer(unittest.TestCase):
    # --- the 4 LOCKED unit tests (rules.md) ---
    def test_locked_1_0_vs_1_0(self):
        self.assertEqual(points((1, 0), (1, 0)), 9)   # exact3 + outcome3 + team2 + GD1

    def test_locked_2_1_vs_1_0(self):
        self.assertEqual(points((2, 1), (1, 0)), 4)   # outcome3 + GD1

    def test_locked_3_2_vs_1_0(self):
        self.assertEqual(points((3, 2), (1, 0)), 4)   # outcome3 + GD1

    def test_locked_1_1_vs_2_2(self):
        self.assertEqual(points((1, 1), (2, 2)), 4)   # outcome(draw)3 + GD1

    def test_gd_proof_2_1_vs_3_2(self):
        # GD survives the exact-weight change: predict 2-1, actual 3-2 -> outcome3 + GD1, no exact/team hit
        self.assertEqual(points((2, 1), (3, 2)), 4)   # outcome3 + GD1 (exact-weight-independent)

    def test_points_beyond_the_locked_four(self):
        # the 4 locked cases are NECESSARY but NOT SUFFICIENT (anti-overfit gate, L10)
        self.assertEqual(points((2, 0), (2, 1)), 4)   # home win, 1 team-goal + outcome
        self.assertEqual(points((0, 0), (0, 0)), 9)   # exact 0-0 (all categories)
        self.assertEqual(points((2, 1), (0, 3)), 0)   # wrong outcome -> nothing
        self.assertEqual(points((1, 2), (0, 3)), 3)   # right outcome (away), wrong GD + goals
        self.assertEqual(points((3, 1), (1, 3)), 0)   # opposite winners -> nothing
        self.assertEqual(points((2, 2), (1, 1)), 4)   # draw outcome + GD

    # --- optimizer behaviour ---
    def test_optimize_is_argmax_over_plausible(self):
        m = _toy_matrix()
        res = optimize(m)
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                if m[i, j] >= PLAUSIBILITY_FLOOR:
                    self.assertLessEqual(expected_points((i, j), m), res["ev"] + 1e-9)

    def test_pick_respects_plausibility_floor(self):
        m = _toy_matrix()
        res = optimize(m, plausibility_floor=0.02)
        i, j = res["pick"]
        self.assertGreaterEqual(m[i, j], 0.02)

    def test_favorite_pick_is_low_scoring_home_win(self):
        # rubric gravitates to the modal low-scoring favorite win (R6 guard), not an extreme score
        res = optimize(_toy_matrix())
        i, j = res["pick"]
        self.assertGreater(i, j)            # home win
        self.assertLessEqual(i + j, 4)      # low-scoring

    # --- NOT a "1-0 machine": engine must diverge from B1 where the edge lives (finding C, L10) ---
    def test_diverges_from_b1_on_high_total(self):
        from src.strength import match_strength
        from src.model import match_distribution
        d = match_distribution(match_strength(
            {"odds_1x2": {"home": 1.7, "draw": 4.2, "away": 4.5}, "fmt": "decimal",
             "totals": {"over": 1.8, "under": 2.05, "line": 3.5}}))
        pick = optimize(d)["pick"]
        self.assertNotEqual(pick, (1, 0))           # B1 would say 1-0; engine must not
        self.assertGreaterEqual(sum(pick), 3)       # high-total -> higher scoreline
        self.assertGreater(pick[0], pick[1])        # home favourite still wins

    def test_picks_away_win_when_away_favored(self):
        from src.strength import match_strength
        from src.model import match_distribution
        d = match_distribution(match_strength(
            {"odds_1x2": {"home": 2.9, "draw": 3.0, "away": 2.8}, "fmt": "decimal",
             "totals": {"over": 2.0, "under": 1.85, "line": 2.5}}))
        self.assertGreater(optimize(d)["pick"][1], optimize(d)["pick"][0])   # away win (j > i)


if __name__ == "__main__":
    unittest.main()
