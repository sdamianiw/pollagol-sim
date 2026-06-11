"""Gate for P4b σ-calibration (pool/sigma_calibration.py). TDD RED-first.

Covers: bootstrap-of-std determinism + bracketing, the two-bound formulas, the anti-FM1 model gate,
the runtime reader read_sigma_cal(), and a locality guard that A2's BASE_SIGMA stays 6.0 (I1).
The one integration test runs the real M7 backtest read-only (cached fixtures, no network).
"""
import os
import sys
import tempfile
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pool import sigma_calibration as sc


class TestBootstrapStd(unittest.TestCase):
    def test_deterministic_same_seed(self):
        a = np.array([0.0, 1.0, 3.0, 4.0, 8.0, 0.0, 3.0, 4.0, 0.0, 1.0])
        self.assertEqual(sc.bootstrap_std_ci(a, n_boot=500, seed=20260603),
                         sc.bootstrap_std_ci(a, n_boot=500, seed=20260603))

    def test_ci_brackets_sample_std(self):
        rng = np.random.RandomState(1)
        a = rng.choice([0, 1, 3, 4, 8], size=4000, p=[0.42, 0.10, 0.20, 0.20, 0.08]).astype(float)
        lo, hi = sc.bootstrap_std_ci(a, n_boot=1000, seed=20260603)
        self.assertLess(lo, a.std(ddof=1))
        self.assertGreater(hi, a.std(ddof=1))

    def test_small_n_is_nan(self):
        lo, hi = sc.bootstrap_std_ci(np.array([1.0]))
        self.assertTrue(np.isnan(lo) and np.isnan(hi))


class TestBounds(unittest.TestCase):
    def test_upper_formula_exact(self):
        self.assertAlmostEqual(sc.sigma_upper(104, 2.5), float(np.sqrt(104) * 2.5), places=12)

    def test_lower_below_upper_across_d_grid(self):
        s = 2.5
        up = sc.sigma_upper(104, s)
        for d in sc.D_GRID:
            self.assertLess(sc.sigma_lower(104, s, d=d, f_div=sc.DEFAULT_F_DIV), up,
                            f"σ_lower(d={d}) must be < σ_upper (f_div·d < 1)")

    def test_lower_monotone_in_d(self):
        s = 2.5
        vals = [sc.sigma_lower(104, s, d=d) for d in sc.D_GRID]
        self.assertEqual(vals, sorted(vals), "σ_lower must increase with d")


class TestModelGate(unittest.TestCase):
    def test_real_rules_has_sentinel(self):
        self.assertTrue(sc.model_declared(sc.RULES_PATH), "rules.md must carry SIGMA_CAL_MODEL: declared")

    def test_missing_sentinel_blocks_compute(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("no sentinel here\n")
            tmp = f.name
        try:
            self.assertFalse(sc.model_declared(tmp))
            with self.assertRaises(AssertionError):
                sc.compute_sigma_cal(rules_path=tmp)   # gate raises BEFORE any backtest runs
        finally:
            os.unlink(tmp)


class TestReadSigmaCal(unittest.TestCase):
    def _write(self, body):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        f.write(body)
        f.close()
        return f.name

    def test_parse_value(self):
        p = self._write("# header\nSIGMA_CAL: 7.53\nmore\n")
        try:
            self.assertAlmostEqual(sc.read_sigma_cal(p), 7.53, places=10)
        finally:
            os.unlink(p)

    def test_missing_key_raises(self):
        p = self._write("# header\nno key\n")
        try:
            with self.assertRaises(ValueError):
                sc.read_sigma_cal(p)
        finally:
            os.unlink(p)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            sc.read_sigma_cal(os.path.join(tempfile.gettempdir(), "definitely_absent_sigma_cal.md"))

    def test_out_of_range_raises(self):
        p = self._write("SIGMA_CAL: 250.0\n")
        try:
            with self.assertRaises(ValueError):
                sc.read_sigma_cal(p)
        finally:
            os.unlink(p)


class TestComputeIntegration(unittest.TestCase):
    """Runs the real backtest read-only (cached fixtures). Slower but deterministic."""
    def test_structural_invariants(self):
        r = sc.compute_sigma_cal()
        up, lo = r["sigma_upper"], r["sigma_lower"]
        self.assertGreater(up["point"], lo["point"])
        self.assertLess(up["ci"][0], up["point"])
        self.assertGreater(up["ci"][1], up["point"])
        self.assertIn(r["stylized_verdict"], {"robust_chalk", "robust_flip", "straddle_escalate"})
        self.assertAlmostEqual(r["sigma_cal"], lo["point"], places=10)   # σ_cal = conservative σ_lower
        self.assertGreater(r["s_pm"]["ev_spm"], 0.0)


class TestA2Unchanged(unittest.TestCase):
    def test_base_sigma_still_six(self):
        from pool import pool_montecarlo as a2
        self.assertAlmostEqual(a2.BASE_SIGMA, 6.0, places=10)


if __name__ == "__main__":
    unittest.main()
