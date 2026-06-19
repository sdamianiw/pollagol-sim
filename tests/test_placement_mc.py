"""TDD for pool/placement_mc.py - the single-entry field-diff E[prize] engine (BUILD-BUT-WAIT).

Covers the DoD checks (i)-(vi):
  (i)   k=0 -> Delta E == 0.0 EXACTLY (byte-exact CRN identity, not within-CI)
  (ii)  trailing + near-even boards -> Delta E > 0 (variance helps when behind)
  (iii) leading (us in podium) -> Delta E <= 0 (chalk wins when ahead)
  (iv)  determinism: fixed seed -> byte-identical E[prize] across two runs
  (v)   single-entry: exactly one "us" bracket (no portfolio)
  (vi)  orientation: matrix[i,j]=P(home=i,away=j) threaded the same way through draw and scorer
"""
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pool.placement_mc import (  # noqa: E402
    expected_prizes_placement, recommend_placement, is_coinflip,
    _toy_matrix, _draw_results, _cell, _POINTS_TABLE, MAX_GOALS,
)
from pool.pool_montecarlo import DEFAULT_SEED  # noqa: E402

SIGMA = 7.18                           # PART-0 measured sigma(g2) (scenario input)
# Near-even board where the favorite NARROWLY wins the EV, so EV-argmax == field modal == 1-0 (we are
# CORRELATED with the field by default). is_coinflip True: |P_home 0.45 - P_draw 0.40| = 0.05 < 0.08.
# decorrelating = 1-1 (the frequent draw the 1-0 field misses): EV 4.20 vs 4.45 (modest -0.25/board EV
# sacrifice) but ~+54 relative-to-field variance -> a near-pure decorrelation-variance add.
NEAR_EVEN = {"matrix": _toy_matrix(0.45, 0.40, 0.15), "modal": (1, 0),
             "us_baseline": (1, 0), "decorrelating": (1, 1)}


def _boards(n):
    return [dict(NEAR_EVEN) for _ in range(n)]


class TestPlacementMC(unittest.TestCase):

    def test_i_k0_identity_byte_exact(self):
        st = {f"opp{i:02d}": 60 for i in range(8)}
        st["us"] = 50
        r = expected_prizes_placement(st, "us", _boards(3), k=0, sigma_opp=SIGMA,
                                      n_sims=20000, seed=DEFAULT_SEED, return_sim_vectors=True)
        # k=0: treatment uses us_baseline on every board => identical to control, byte-exact.
        self.assertEqual(r["delta_E_prize"], 0.0)
        self.assertEqual(r["delta_p_top3"], 0.0)
        self.assertTrue(np.array_equal(r["_sim_prize_ctrl"], r["_sim_prize_trt"]))
        self.assertEqual(r["control"], r["treatment"])

    def test_ii_trailing_delta_positive(self):
        # us below the podium cut but within reach; near-even boards -> differentiation variance helps.
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58
        r = expected_prizes_placement(st, "us", _boards(3), k=3, sigma_opp=SIGMA,
                                      n_sims=30000, seed=DEFAULT_SEED)
        self.assertGreater(r["delta_E_prize"], 0.0,
                           f"trailing: expected Delta E > 0, got {r['delta_E_prize']}")
        self.assertGreater(r["treatment"]["p_top3"], r["control"]["p_top3"])

    def test_iii_leading_delta_nonpositive(self):
        # us comfortably 1st (the top 0.6 prize): one chaser modestly behind, the rest far below. Added
        # decorrelation variance can only REGRESS us off the top prize (no upside above 1st) and the EV
        # sacrifice compounds it -> Delta E <= 0.
        opps = [80, 48, 47, 46, 45, 44, 43, 42]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 92                                   # clear 1st; chaser 80, cluster <=48 far below
        r = expected_prizes_placement(st, "us", _boards(3), k=3, sigma_opp=SIGMA,
                                      n_sims=30000, seed=DEFAULT_SEED)
        self.assertLessEqual(r["delta_E_prize"], 0.0,
                             f"leading: expected Delta E <= 0, got {r['delta_E_prize']}")

    def test_iv_determinism(self):
        st = {f"opp{i:02d}": 60 for i in range(8)}
        st["us"] = 50
        a = expected_prizes_placement(st, "us", _boards(3), k=2, sigma_opp=SIGMA,
                                      n_sims=15000, seed=DEFAULT_SEED)
        b = expected_prizes_placement(st, "us", _boards(3), k=2, sigma_opp=SIGMA,
                                      n_sims=15000, seed=DEFAULT_SEED)
        self.assertEqual(a["control"], b["control"])
        self.assertEqual(a["treatment"], b["treatment"])
        self.assertEqual(a["delta_E_prize"], b["delta_E_prize"])

    def test_v_single_entry(self):
        # exactly one "us" bracket: two arms, a single delta - NOT a portfolio table; rank in [1, n].
        st = {f"opp{i:02d}": 60 for i in range(8)}
        st["us"] = 55
        r = expected_prizes_placement(st, "us", _boards(2), k=1, sigma_opp=SIGMA,
                                      n_sims=10000, seed=DEFAULT_SEED)
        self.assertEqual(set(r["control"].keys()),
                         {"E_prize", "P1", "P2", "P3", "p_top3", "mean_rank"})
        for arm in ("control", "treatment"):
            self.assertTrue(1.0 <= r[arm]["mean_rank"] <= len(st))
            self.assertAlmostEqual(r[arm]["P1"] + r[arm]["P2"] + r[arm]["P3"],
                                   r[arm]["p_top3"], places=12)   # P1+P2+P3 == p_top3 (single bracket)

    def test_vi_orientation_no_transpose(self):
        # board mass entirely on (home=2, away=0): the draw must return (2,0), and a (2,0) pick must
        # score the exact 9 while a transposed (0,2) pick scores 0 - guards a home/away swap.
        m = np.zeros((MAX_GOALS, MAX_GOALS))
        m[2, 0] = 1.0
        rng = np.random.default_rng(DEFAULT_SEED)
        (rh, ra), = _draw_results([{"matrix": m}], rng, 1000)
        self.assertTrue(np.all(rh == 2) and np.all(ra == 0), "draw orientation: expected home=2, away=0")
        self.assertEqual(int(_POINTS_TABLE[2, 0, 2, 0]), 9)      # pred 2-0 vs actual 2-0 -> exact
        self.assertEqual(int(_POINTS_TABLE[0, 2, 2, 0]), 0)      # transposed pred 0-2 vs 2-0 -> nothing
        self.assertEqual(_cell((2, 0)), 18)                       # 2*9+0; 18//9=2, 18%9=0 -> (2,0)

    def test_coinflip_predicate(self):
        self.assertTrue(is_coinflip(_toy_matrix(0.40, 0.38, 0.22)))     # |0.40-0.38|=0.02 < 0.08
        self.assertFalse(is_coinflip(_toy_matrix(0.70, 0.20, 0.10)))    # |0.70-0.20|=0.50 >= 0.08

    def test_sigma_required_and_guards(self):
        st = {"us": 50, "opp": 60}
        with self.assertRaises(ValueError):
            expected_prizes_placement(st, "us", _boards(1), k=0)        # sigma_opp required
        with self.assertRaises(ValueError):
            expected_prizes_placement(st, "missing", _boards(1), k=0, sigma_opp=SIGMA)
        with self.assertRaises(ValueError):
            expected_prizes_placement(st, "us", _boards(1), k=5, sigma_opp=SIGMA)   # k>len(boards)

    def test_recommend_smoke_not_fired(self):
        # recommend_placement runs the sweep + adverse-corner gate and reports P(top-3) headline.
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58
        out = recommend_placement(st, "us", _boards(2), sigma_opp=SIGMA,
                                  n_sims=8000, n_bootstrap=400)
        self.assertIn("p_top3_ctrl", out["headline"])
        self.assertIn("p_top3_trt", out["headline"])
        self.assertEqual(len(out["sweep"]), 3)                          # k=0,1,2
        self.assertEqual(out["sweep"][0]["delta_E_prize"], 0.0)         # k=0 in sweep is the identity
        self.assertIn("adverse_corner", out)
        self.assertIsInstance(out["fire"], bool)


if __name__ == "__main__":
    unittest.main()
