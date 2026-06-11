"""M2 strength - TDD (Gate 7). de-vig 1X2 (single book-set) + Elo fallback.
Decimal odds carry vig -> the decimal path MUST de-vig (never raw 1/odds, L9)."""
from __future__ import annotations
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.strength import decimal_to_prob, devig_1x2, elo_probs, match_strength


class TestStrength(unittest.TestCase):
    def test_decimal_to_prob(self):
        self.assertAlmostEqual(decimal_to_prob(2.0), 0.5, places=12)
        self.assertAlmostEqual(decimal_to_prob(1.33), 1.0 / 1.33, places=12)

    def test_decimal_to_prob_rejects_bad_odds(self):
        with self.assertRaises(ValueError):
            decimal_to_prob(0.9)

    def test_devig_normalizes_and_overround(self):
        # Burnley v Man City, B365 decimal: H=8 D=5.5 A=1.33 (real probe row 2023-08-11)
        probs, overround = devig_1x2({"home": 8.0, "draw": 5.5, "away": 1.33}, fmt="decimal")
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=12)
        self.assertAlmostEqual(overround, 1.0 / 8 + 1.0 / 5.5 + 1.0 / 1.33, places=12)
        self.assertGreater(probs["away"], probs["home"])      # City heavy favorite
        self.assertGreater(probs["away"], probs["draw"])

    def test_decimal_path_devigs_not_raw(self):
        m = match_strength({"odds_1x2": {"home": 8.0, "draw": 5.5, "away": 1.33}, "fmt": "decimal"})
        self.assertAlmostEqual(sum(m["probs"].values()), 1.0, places=12)   # raw 1/odds would sum > 1
        self.assertEqual(m["source"], "market")
        self.assertGreater(m["overround"], 1.0)

    def test_american_path(self):
        probs, overround = devig_1x2({"home": 100, "draw": 240, "away": 150}, fmt="american")
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=12)
        self.assertGreater(overround, 1.0)

    def test_totals_threaded(self):
        m = match_strength({"odds_1x2": {"home": 2.1, "draw": 3.4, "away": 3.6},
                            "fmt": "decimal", "totals": {"over": 1.9, "under": 1.95, "line": 2.5}})
        self.assertEqual(m["total_line"], 2.5)
        self.assertTrue(0.0 < m["p_over"] < 1.0)

    def test_elo_sums_and_favors_stronger(self):
        p = elo_probs(2000, 1700)
        self.assertAlmostEqual(sum(p.values()), 1.0, places=9)
        self.assertGreater(p["home"], p["away"])

    def test_elo_neutral_reduces_home(self):
        self.assertGreater(elo_probs(1800, 1800)["home"], elo_probs(1800, 1800, neutral=True)["home"])

    def test_fallback_to_elo_when_no_odds(self):
        m = match_strength({"elo": {"home": 2000, "away": 1700}})
        self.assertEqual(m["source"], "elo")
        self.assertAlmostEqual(sum(m["probs"].values()), 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
