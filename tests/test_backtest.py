"""P3 / M7 - TDD for evals/backtest.py. Tests the pure functions of the success-proof:
B1 mirror + away-fav gap-0, total-level segmentation, home-zero transform, the vectorized EV picker
== the FROZEN optimizer.optimize (no shadow SUT), leakage guard, deterministic bootstrap CI, verdict,
Brier/log-loss, and the row builder (drop on bad odds). No network; tiny synthetic inputs."""
from __future__ import annotations
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.strength import match_strength
from src.model import fit_lambdas, score_matrix
from src.optimizer import optimize
from evals.backtest import (
    assert_no_leakage, LeakageError, build_match, home_zero, b1_pick, fixture_eval,
    ev_pick, ev_grid, paired_bootstrap_ci, normal_ci, verdict, brier_logloss, _POINTS,
    HIGH_TOTAL_P, mu_from_pover, poisson_over_prob,
)


def _matrix(home, draw, away, over, under, line=2.5):
    s = match_strength({"odds_1x2": {"home": home, "draw": draw, "away": away}, "fmt": "decimal",
                        "totals": {"over": over, "under": under, "line": line}})
    lh, la = fit_lambdas(s["probs"], s["total_line"])
    return score_matrix(lh, la)


class TestBacktest(unittest.TestCase):
    # --- B1 = 1-0 favorite, MIRRORED (user 2026-06-03) ---
    def test_b1_mirrors(self):
        self.assertEqual(b1_pick(1.6, 0.8), (1, 0))     # home favored
        self.assertEqual(b1_pick(0.8, 1.6), (0, 1))     # away favored -> 0-1, not 1-0
        self.assertEqual(b1_pick(1.1, 1.1), (1, 0))     # tie -> home (lh>=la)

    def test_away_fav_low_total_is_gap0(self):
        # clear away favorite, LOW total -> EV and B1 BOTH pick the favorite's low win (0,1) -> gap 0
        match = {"odds_1x2": {"home": 4.5, "draw": 3.6, "away": 1.75}, "fmt": "decimal",
                 "totals": {"over": 2.3, "under": 1.65, "line": 2.5}}
        ev, b1, _p, p_over, _rho, _clamp = fixture_eval(match, delta=0.0)
        self.assertEqual(b1, (0, 1))
        self.assertEqual(ev, (0, 1))
        self.assertEqual(ev, b1)                          # gap-0 by construction
        self.assertLess(p_over, HIGH_TOTAL_P)             # genuinely low-total

    def test_high_total_diverges(self):
        # home favorite but HIGH total (price-driven mu_eff, rules.md v) -> EV lifts above 1-0,
        # B1 stays 1-0 -> divergence. (RED before mu_eff was wired: mu pinned at 2.5 -> EV picked 1-0.)
        match = {"odds_1x2": {"home": 1.65, "draw": 4.3, "away": 4.8}, "fmt": "decimal",
                 "totals": {"over": 1.5, "under": 2.6, "line": 2.5}}
        ev, b1, _p, p_over, _rho, _clamp = fixture_eval(match, delta=0.0)
        self.assertGreaterEqual(p_over, HIGH_TOTAL_P)
        self.assertEqual(b1, (1, 0))
        self.assertNotEqual(ev, (1, 0))
        self.assertGreaterEqual(sum(ev), 3)               # high total -> higher scoreline
        self.assertGreater(ev[0], ev[1])                  # home still wins

    # --- home-zero transform ---
    def test_home_zero_reduces_supremacy(self):
        lh, la = home_zero(1.6, 0.8, 0.30)                # s: 0.8 -> 0.5; mu stays 2.4
        self.assertAlmostEqual(lh + la, 2.4, places=9)
        self.assertAlmostEqual(lh - la, 0.5, places=9)

    def test_home_zero_can_flip_favorite(self):
        lh, la = home_zero(1.2, 1.0, 0.30)                # s: 0.2 -> -0.1 -> away favored
        self.assertLess(lh, la)
        self.assertEqual(b1_pick(lh, la), (0, 1))

    def test_home_zero_identity_at_zero(self):
        # delta=0 is the identity in REAL-number terms; the re-split add/sub/divide carries IEEE-754
        # round-off (la=0.9000000000000001), so assert numeric equality, not bit-identity (root-cause).
        lh, la = home_zero(1.7, 0.9, 0.0)
        self.assertAlmostEqual(lh, 1.7, places=12)
        self.assertAlmostEqual(la, 0.9, places=12)

    # --- mu_eff inversion (rules.md M7 design v, FROZEN before reading the number) ---
    def test_mu_eff_hand_point(self):
        # mu=3.0 -> P(T>=3); inverting that probability must return mu=3.0
        self.assertAlmostEqual(mu_from_pover(poisson_over_prob(3.0)), 3.0, places=4)

    def test_mu_eff_monotonic(self):
        mus = [mu_from_pover(x) for x in (0.45, 0.55, 0.65, 0.75)]
        self.assertTrue(all(mus[i] < mus[i + 1] for i in range(len(mus) - 1)))

    def test_mu_eff_roundtrip(self):
        for mu in (2.0, 2.6, 3.2, 4.0):
            self.assertAlmostEqual(mu_from_pover(poisson_over_prob(mu)), mu, places=4)

    def test_poisson_over_prob_increasing(self):
        self.assertLess(poisson_over_prob(2.0), poisson_over_prob(3.5))
        self.assertTrue(0.0 < poisson_over_prob(2.5) < 1.0)

    # --- vectorized EV picker == FROZEN optimizer.optimize (no shadow SUT) ---
    def test_points_tensor_is_locked_rubric(self):
        self.assertEqual(int(_POINTS[1, 0, 1, 0]), 9)
        self.assertEqual(int(_POINTS[2, 1, 1, 0]), 4)
        self.assertEqual(int(_POINTS[1, 1, 2, 2]), 4)
        self.assertEqual(int(_POINTS[2, 1, 0, 3]), 0)

    def test_ev_pick_matches_optimize(self):
        regimes = [
            (1.6, 3.8, 5.5, 1.9, 1.9),    # home fav, mid total
            (1.55, 4.5, 5.5, 1.65, 2.25), # home fav, high total
            (4.5, 3.6, 1.75, 2.3, 1.65),  # away fav, low total
            (2.9, 3.0, 2.8, 2.0, 1.85),   # even, mid total
            (1.33, 5.5, 8.0, 1.67, 2.2),  # heavy home fav, low total (the Burnley-ManCity shape)
            (2.4, 3.2, 3.0, 1.7, 2.15),   # slight home fav, low total
        ]
        for h, d, a, o, u in regimes:
            m = _matrix(h, d, a, o, u)
            self.assertEqual(ev_pick(m), optimize(m)["pick"], msg=f"mismatch at {(h, d, a, o, u)}")

    def test_ev_grid_matches_optimize_ev(self):
        m = _matrix(1.6, 3.8, 5.5, 1.9, 1.9)
        grid = ev_grid(m)
        res = optimize(m)
        self.assertAlmostEqual(float(grid[res["pick"]]), res["ev"], places=9)

    # --- leakage guard (PM1) ---
    def test_leakage_guard_accepts_clean(self):
        self.assertTrue(assert_no_leakage(
            {"odds_1x2": {"home": 2.0, "draw": 3.0, "away": 4.0}, "fmt": "decimal",
             "totals": {"over": 1.9, "under": 1.9, "line": 2.5}}))

    def test_leakage_guard_rejects_result(self):
        with self.assertRaises(LeakageError):
            assert_no_leakage({"odds_1x2": {"home": 2.0, "draw": 3.0, "away": 4.0}, "FTHG": 1})

    def test_build_match_has_no_result_keys(self):
        row = {"B365H": "2.0", "B365D": "3.4", "B365A": "3.6", "B365>2.5": "1.9", "B365<2.5": "1.9",
               "FTHG": "2", "FTAG": "1", "FTR": "H"}
        m = build_match(row)
        self.assertEqual(set(m), {"odds_1x2", "fmt", "totals"})
        self.assertNotIn("FTHG", m)

    def test_build_match_drops_bad_rows(self):
        base = {"B365H": "2.0", "B365D": "3.4", "B365A": "3.6", "B365>2.5": "1.9", "B365<2.5": "1.9"}
        self.assertIsNotNone(build_match(base))
        self.assertIsNone(build_match({**base, "B365H": ""}))      # missing -> drop
        self.assertIsNone(build_match({**base, "B365A": "1.0"}))   # odds <= 1.0 -> drop
        bad = dict(base); del bad["B365D"]
        self.assertIsNone(build_match(bad))                        # absent column -> drop

    # --- statistics ---
    def test_bootstrap_deterministic_and_brackets_mean(self):
        d = np.array([0.0, 1.0, -1.0, 2.0, 0.5, -0.5, 1.5, 0.0, 0.0, 1.0])
        ci1 = paired_bootstrap_ci(d)
        ci2 = paired_bootstrap_ci(d)
        self.assertEqual(ci1, ci2)                                 # fresh RandomState -> reproducible
        self.assertLessEqual(ci1[0], d.mean())
        self.assertGreaterEqual(ci1[1], d.mean())

    def test_normal_ci_sane(self):
        d = np.zeros(100)
        lo, hi = normal_ci(d)
        self.assertAlmostEqual(lo, 0.0, places=9)
        self.assertAlmostEqual(hi, 0.0, places=9)

    def test_verdict(self):
        self.assertEqual(verdict(0.10, 0.20), "PASS")
        self.assertEqual(verdict(-0.20, -0.10), "FAIL")
        self.assertEqual(verdict(-0.10, 0.20), "NO-EDGE")

    def test_brier_logloss_known(self):
        # perfect forecast -> Brier 0, log-loss ~0
        b, ll = brier_logloss([{"home": 1.0, "draw": 0.0, "away": 0.0}], ["home"])
        self.assertAlmostEqual(b, 0.0, places=9)
        self.assertAlmostEqual(ll, 0.0, places=6)
        # uniform 1/3 -> Brier 2/3, log-loss ln(3)
        b2, ll2 = brier_logloss([{"home": 1 / 3, "draw": 1 / 3, "away": 1 / 3}], ["away"])
        self.assertAlmostEqual(b2, 2 / 3, places=9)
        self.assertAlmostEqual(ll2, np.log(3), places=9)


if __name__ == "__main__":
    unittest.main()
