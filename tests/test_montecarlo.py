"""DoD-4 - TDD reproducing tests for the 3 A2 defects in pool/pool_montecarlo.py.
Written RED-first (Gate 7): they FAIL on the current code, PASS after the surgical fixes.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pool.pool_montecarlo import expected_prizes, DEFAULT_SEED  # noqa: E402

P_TRUE = {"Fav": 0.40, "Mid": 0.25, "Dark": 0.20, "Rest": 0.15}


class TestMonteCarloFixes(unittest.TestCase):
    def test_BUG1_pwin_relabeled_and_pfirst_added(self):
        # 'p_win' was P(pick == true champion) ~ P_true[cand] -- NOT the prob of winning the pool.
        # Fix: rename -> 'p_pick_ok' AND add 'p_first' = empirical P(rank == 1).
        t = expected_prizes(P_TRUE, ["Fav"], [(11, P_TRUE)], n_sims=40000, sigma=6.0, seed=DEFAULT_SEED)
        row = t["Fav"]
        self.assertNotIn("p_win", row, "mislabeled key 'p_win' must be renamed (it is not P(win pool))")
        self.assertIn("p_pick_ok", row)
        self.assertIn("p_first", row)
        self.assertAlmostEqual(row["p_pick_ok"], 0.40, delta=0.02)      # == P_true[Fav] (pick-correct prob)
        self.assertTrue(0.0 <= row["p_first"] <= 1.0)
        self.assertLess(row["p_first"], row["p_pick_ok"] - 0.05,
                        "p_first (finish 1st of 12) must be a different, smaller quantity than p_pick_ok")

    def test_BUG2_no_dtype_truncation(self):
        # An ownership label wider than the widest p_true key must NOT be truncated and spuriously match.
        p_true = {"Brazil": 0.1, "Mexico": 0.9}          # widest key = 6 chars -> numpy dtype <U6
        t = expected_prizes(p_true, ["Mexico"], [(1, {"Mexico City": 1.0})],
                            n_sims=40000, sigma=6.0, seed=DEFAULT_SEED)
        # Buggy: 'Mexico City'[:6] == 'Mexico' spuriously matches T*=='Mexico' (0.9) -> lone opp also
        #        bonuses -> ~50/50 -> E_prize ~0.40.  Fixed: 'Mexico City' != 'Mexico' -> E_prize ~0.58.
        self.assertGreater(t["Mexico"]["E_prize"], 0.5,
                           "dtype truncation: 'Mexico City' collapsed to 'Mexico' and spuriously matched")

    def test_P2_two_group_path_runs(self):
        # The real Jun-11 path concatenates a LOCKED (observed) group + a PENDING (prior) group.
        t = expected_prizes(P_TRUE, ["Fav", "Mid", "Dark"],
                            [(3, {"Fav": 1.0}), (8, {"Fav": 0.5, "Mid": 0.35, "Dark": 0.025, "Rest": 0.125})],
                            n_sims=40000, sigma=6.0, seed=DEFAULT_SEED)
        best = max(t, key=lambda c: t[c]["E_prize"])
        # Aggregate ownership over-owns Fav (~0.64) and starves Dark (~0.018) -> contrarian Dark wins.
        self.assertEqual(best, "Dark", f"two-group concatenate path: expected Dark, got {best} ({t})")


if __name__ == "__main__":
    unittest.main(verbosity=2)
