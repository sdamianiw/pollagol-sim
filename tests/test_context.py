"""M5 context - TDD (Gate 7). Sourced context_flag; adjusts BOTH mean and variance of the forecast."""
from __future__ import annotations
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.model import score_matrix
from src.context import apply_context, expected_total, var_total


class TestContext(unittest.TestCase):
    def setUp(self):
        self.m = score_matrix(1.5, 1.1)

    def test_flag_is_sourced_one_line(self):
        _, flag = apply_context(self.m, "dead_rubber", source="group-table 2026-06-24 (FIFA)")
        self.assertIn("source", flag)
        self.assertTrue(flag["source"])
        self.assertTrue(flag["text"])
        self.assertEqual(flag["flags"], ["dead_rubber"])

    def test_adjusts_mean_and_variance(self):
        adj, _ = apply_context(self.m, "dead_rubber")
        self.assertNotAlmostEqual(expected_total(adj), expected_total(self.m), places=3)  # MEAN moved
        self.assertGreater(var_total(adj), var_total(self.m))                              # VARIANCE up

    def test_high_stakes_tightens_variance(self):
        adj, _ = apply_context(self.m, "high_stakes")
        self.assertLess(var_total(adj), var_total(self.m))

    def test_no_flags_is_passthrough(self):
        adj, flag = apply_context(self.m, [])
        self.assertEqual(flag["text"], "no context")
        self.assertAlmostEqual(expected_total(adj), expected_total(self.m), places=9)

    def test_unknown_flag_raises(self):
        with self.assertRaises(ValueError):
            apply_context(self.m, "made_up_flag")

    def test_output_is_a_distribution(self):
        adj, _ = apply_context(self.m, ["dead_rubber", "neutral"])
        self.assertAlmostEqual(adj.sum(), 1.0, places=9)

    def test_dead_rubber_pinned(self):
        # H4: pins the CURRENT post-DC behavior so drift is caught. KNOWN LIMITATION: dead_rubber
        # ("fewer goals", mu_f=0.90) moves expected_total UP (+0.131) = the WRONG direction - the var-temper
        # on a right-skewed matrix dominates mu_f (see context.py WARNING; fix = pre-DC re-anchor, separate GO).
        adj, _ = apply_context(self.m, "dead_rubber")
        self.assertAlmostEqual(expected_total(self.m), 2.5998, places=4)
        self.assertAlmostEqual(expected_total(adj), 2.7304, places=4)     # UP, not down (documented issue)
        self.assertAlmostEqual(var_total(adj), 3.2072, places=4)

    def test_neutral_not_strictly_mean_neutral(self):
        # H4: even the LIVE default `neutral` (mu_f=1.0) shifts the mean +0.069 via the var-temper.
        adj, _ = apply_context(self.m, "neutral")
        self.assertAlmostEqual(expected_total(adj) - expected_total(self.m), 0.0689, places=4)


if __name__ == "__main__":
    unittest.main()
