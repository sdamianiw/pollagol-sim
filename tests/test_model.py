"""M3 model - TDD (Gate 7). Dixon-Coles score distribution from de-vigged 1X2 (+ optional totals).
Distribution must sum to 1; fit must round-trip the de-vigged probs; clamp/shrink prevents extremes."""
from __future__ import annotations
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.model import score_matrix, implied_1x2, fit_lambdas, match_distribution, rho_sensitivity


class TestModel(unittest.TestCase):
    def test_matrix_sums_to_one(self):
        self.assertAlmostEqual(score_matrix(1.5, 1.1).sum(), 1.0, places=9)

    def test_symmetric_lambdas_symmetric_1x2(self):
        d = implied_1x2(score_matrix(1.3, 1.3))
        self.assertAlmostEqual(d["home"], d["away"], places=6)
        self.assertAlmostEqual(d["home"] + d["draw"] + d["away"], 1.0, places=9)

    def test_fit_recovers_probs_totals_present(self):
        truth = score_matrix(1.7, 0.9)
        d = implied_1x2(truth)
        lh, la = fit_lambdas(d, total_line=1.7 + 0.9)
        self.assertAlmostEqual(implied_1x2(score_matrix(lh, la))["home"], d["home"], places=2)

    def test_fit_recovers_probs_totals_absent(self):
        truth = score_matrix(1.7, 0.9)
        d = implied_1x2(truth)
        lh, la = fit_lambdas(d, total_line=None)
        got = implied_1x2(score_matrix(lh, la))
        self.assertAlmostEqual(got["home"], d["home"], places=2)
        self.assertAlmostEqual(got["draw"], d["draw"], places=2)

    def test_clamp_prevents_extreme_no_nan(self):
        m = match_distribution({"probs": {"home": 0.985, "draw": 0.010, "away": 0.005},
                                "total_line": None, "source": "market"})
        self.assertAlmostEqual(m.sum(), 1.0, places=9)
        self.assertFalse(np.isnan(m).any())

    def test_rho_sensitivity_reported(self):
        sens = rho_sensitivity({"probs": {"home": 0.5, "draw": 0.27, "away": 0.23}, "total_line": None})
        self.assertEqual(len(sens), 2)        # rho=0 vs rho=RHO
        for d in sens.values():
            self.assertAlmostEqual(sum(d.values()), 1.0, places=9)

    def _expected_total_goals(self, p_over, line=2.5):
        probs = {"home": 0.45, "draw": 0.27, "away": 0.28}
        m = match_distribution({"probs": probs, "total_line": line, "p_over": p_over, "source": "market"})
        idx = np.arange(m.shape[0])
        return float((m * (idx[:, None] + idx[None, :])).sum())   # E[total goals]

    def test_mu_tracks_pover_at_fixed_line(self):
        """M3 must read the totals PRICE (p_over), not just the LINE (rules.md M7 design v / P4a):
        at a FIXED line, higher p_over (market expects more goals) must LIFT the implied total.
        RED before the μ_eff port (totals-blind: μ=f(line) only -> identical at any p_over)."""
        lo, hi = self._expected_total_goals(0.45), self._expected_total_goals(0.75)
        self.assertGreater(hi, lo + 0.10,
                           f"μ must track p_over at a fixed line (E[tot] {lo:.3f} @0.45 vs {hi:.3f} @0.75)")


class TestMuEff(unittest.TestCase):
    """P4a: the μ_eff inversion ported into src/ (ONE model, I4) + hardening mirror of tests/test_backtest.py."""

    def test_one_model_object_shared_with_evals(self):
        from src.model import mu_from_pover as src_mu
        from evals.backtest import mu_from_pover as evals_mu
        self.assertIs(src_mu, evals_mu)   # evals re-imports src -> a single μ_eff model (no second model)

    def test_match_distribution_equals_evals_mu_eff_path(self):
        """src match_distribution == the M7-validated computation fit_lambdas(probs, mu_from_pover(p_over,line))
        (pre-home_zero) byte-equal on >=3 fixtures -> the live path now carries the same totals-aware edge."""
        from src.model import mu_from_pover
        fixtures = [
            {"probs": {"home": 0.55, "draw": 0.25, "away": 0.20}, "total_line": 2.5, "p_over": 0.62},
            {"probs": {"home": 0.40, "draw": 0.28, "away": 0.32}, "total_line": 2.5, "p_over": 0.48},
            {"probs": {"home": 0.70, "draw": 0.18, "away": 0.12}, "total_line": 3.0, "p_over": 0.71},
        ]
        for fx in fixtures:
            m_live = match_distribution(dict(fx, source="market"))
            lh, la = fit_lambdas(fx["probs"], mu_from_pover(fx["p_over"], fx["total_line"]))
            self.assertTrue(np.array_equal(m_live, score_matrix(lh, la)), f"live != evals μ_eff path on {fx}")

    def test_mu_eff_hand_point(self):
        from src.model import mu_from_pover, poisson_over_prob
        self.assertAlmostEqual(mu_from_pover(poisson_over_prob(3.0)), 3.0, places=4)

    def test_mu_eff_monotonic_in_pover(self):
        from src.model import mu_from_pover
        mus = [mu_from_pover(x) for x in (0.45, 0.55, 0.65, 0.75)]
        self.assertTrue(all(b > a for a, b in zip(mus, mus[1:])), mus)

    def test_mu_eff_roundtrip(self):
        from src.model import mu_from_pover, poisson_over_prob
        for mu in (1.5, 2.2, 3.0, 3.8):
            self.assertAlmostEqual(mu_from_pover(poisson_over_prob(mu)), mu, places=4)

    def test_poisson_over_prob_increasing(self):
        from src.model import poisson_over_prob
        self.assertLess(poisson_over_prob(2.0), poisson_over_prob(3.5))
        self.assertTrue(0.0 < poisson_over_prob(2.5) < 1.0)

    def test_mu_eff_corr_and_span(self):
        """P3 GREEN criterion: over a p_over sweep μ_eff spans a real range AND corr(μ, p_over) >= 0.9."""
        from src.model import mu_from_pover
        povers = np.array([0.30, 0.40, 0.50, 0.60, 0.70, 0.80])
        mus = np.array([mu_from_pover(p) for p in povers])
        self.assertGreater(mus.max() - mus.min(), 1.0, f"μ_eff span too small: {mus.max()-mus.min():.3f}")
        self.assertGreater(float(np.corrcoef(povers, mus)[0, 1]), 0.9)

    def test_mu_eff_clamp_not_biting_in_range(self):
        from src.model import mu_from_pover
        for p in (0.20, 0.50, 0.85):
            mu = mu_from_pover(p)
            self.assertGreater(mu, 0.25)   # off the lo=0.2 bound
            self.assertLess(mu, 7.5)       # off the hi=8.0 bound


if __name__ == "__main__":
    unittest.main()
