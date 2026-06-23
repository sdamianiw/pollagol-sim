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
    expected_prizes_placement, recommend_placement, is_coinflip, board_lever_status,
    _gate_decision, _toy_matrix, _draw_results, _cell, _POINTS_TABLE, MAX_GOALS,
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
        # CONDITIONAL property (NOT universal): trailing -> Delta E > 0 holds ONLY on a LEVER-ACTIVE board
        # (us_baseline == field modal, so decorrelating ADDS relative-to-field variance). NEAR_EVEN is
        # lever-active by construction. See test_inverting_regime for the off-eligibility counter-case.
        self.assertEqual(board_lever_status(NEAR_EVEN), "active")
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58
        r = expected_prizes_placement(st, "us", _boards(3), k=3, sigma_opp=SIGMA,
                                      n_sims=30000, seed=DEFAULT_SEED)
        self.assertGreater(r["delta_E_prize"], 0.0,
                           f"trailing+lever-active: expected Delta E > 0, got {r['delta_E_prize']}")
        self.assertGreater(r["treatment"]["p_top3"], r["control"]["p_top3"])

    def test_iii_leading_delta_nonpositive(self):
        # CONDITIONAL (lever-active): us comfortably 1st (the top 0.6 prize): one chaser modestly behind,
        # the rest far below. Added decorrelation variance can only REGRESS us off the top prize (no upside
        # above 1st) and the EV sacrifice compounds it -> Delta E <= 0.
        opps = [80, 48, 47, 46, 45, 44, 43, 42]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 92                                   # clear 1st; chaser 80, cluster <=48 far below
        r = expected_prizes_placement(st, "us", _boards(3), k=3, sigma_opp=SIGMA,
                                      n_sims=30000, seed=DEFAULT_SEED)
        self.assertLessEqual(r["delta_E_prize"], 0.0,
                             f"leading+lever-active: expected Delta E <= 0, got {r['delta_E_prize']}")

    def test_inverting_regime_trailing_can_be_negative(self):
        # LEVER-INVERTED board: us_baseline = EV-argmax = 1-1 != field modal = 1-0, decorrelating = 0-1 is
        # BOTH lower-EV AND lower-relative-to-field-variance. Then even TRAILING, differentiating HURTS
        # (Delta E <= 0). This is the P1.1 counter-case: trailing->+ is CONDITIONAL on lever-eligibility.
        inv = {"matrix": _toy_matrix(0.40, 0.38, 0.22), "modal": (1, 0),
               "us_baseline": (1, 1), "decorrelating": (0, 1)}
        self.assertEqual(board_lever_status(inv), "inverted-risk")
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58                                   # same trailing field as (ii), but lever inverted
        r = expected_prizes_placement(st, "us", [dict(inv) for _ in range(3)], k=3, sigma_opp=SIGMA,
                                      n_sims=30000, seed=DEFAULT_SEED)
        self.assertLessEqual(r["delta_E_prize"], 0.0,
                             f"inverted+trailing: expected Delta E <= 0, got {r['delta_E_prize']}")

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

    def test_recommend_diagnostics_surfaced(self):
        # P1.2 lever eligibility + P2.3 eps_min HITL flag + P2.5 sigma-grid top are all surfaced.
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58
        # default eps_min -> demo-flagged; lever-active boards -> 0 ineligible; default grid top = 19.5
        out = recommend_placement(st, "us", _boards(2), sigma_opp=SIGMA, n_sims=6000, n_bootstrap=300)
        self.assertTrue(out["eps_min_is_demo"])
        self.assertEqual(out["eps_min"], 0.02)
        self.assertTrue(all(lv["eligible"] for lv in out["board_levers"]))
        self.assertEqual(out["n_ineligible_boards"], 0)
        self.assertEqual(out["sigma_grid_top"], 19.5)
        # inverted board -> flagged ineligible; HITL eps_min + sigma_top_extra honored
        inv = {"matrix": _toy_matrix(0.40, 0.38, 0.22), "modal": (1, 0),
               "us_baseline": (1, 1), "decorrelating": (0, 1)}
        out2 = recommend_placement(st, "us", [dict(inv)], sigma_opp=SIGMA, n_sims=6000, n_bootstrap=300,
                                   eps_min=0.05, sigma_top_extra=25.0)
        self.assertEqual(out2["n_ineligible_boards"], 1)
        self.assertFalse(out2["board_levers"][0]["eligible"])
        self.assertFalse(out2["eps_min_is_demo"])
        self.assertEqual(out2["eps_min"], 0.05)
        self.assertEqual(out2["sigma_grid_top"], 25.0)

    def test_bubble_internal_consistency(self):
        # PODIUM BUBBLE: us fighting for 3rd against a cluster straddling the cut. Variance is double-edged
        # here, so NO a-priori sign on Delta E. Assert only INTERNAL CONSISTENCY of the fire decision.
        opps = [90, 85, 67, 66, 65, 64, 63, 62]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 66                                   # mid-cluster, on the 3rd-place bubble
        out = recommend_placement(st, "us", _boards(3), sigma_opp=SIGMA, n_sims=12000, n_bootstrap=600)
        adv = out["adverse_corner"]
        self.assertLessEqual(adv["ci_lo"], adv["ci_hi"])                 # CI well-formed
        # fire is EXACTLY its own corner-by-corner gate predicate (#1 + #3): worst-case CI_lo > 0 AND
        # Delta p_top3 >= eps_min at ITS OWN worst corner AND every board lever-active.
        worst_ci_lo = min(g["ci_lo"] for g in out["sigma_grid"])
        adv_p3 = min(out["sigma_grid"], key=lambda g: g["delta_p_top3"])
        expected = bool(worst_ci_lo > 0.0 and adv_p3["delta_p_top3"] >= out["eps_min"]
                        and out["n_ineligible_boards"] == 0)
        self.assertEqual(out["fire"], expected)
        # adverse_corner is the grid-min Delta E (worst sigma for the treatment); adverse_corner_p3 the
        # grid-min Delta p_top3 (the corner that binds the effect-size floor).
        self.assertEqual(adv["delta_E_prize"], min(g["delta_E_prize"] for g in out["sigma_grid"]))
        self.assertEqual(out["adverse_corner_p3"]["delta_p_top3"],
                         min(g["delta_p_top3"] for g in out["sigma_grid"]))


class TestFireGateCornerByCorner(unittest.TestCase):
    """Regression for findings #1 (P(top-3) floor at its OWN worst corner, not the min-Delta-E corner)
    and #3 (n_ineligible == 0 wired into `fire`). Uses synthetic grids -> tests the pure gate logic."""

    # divergent grid: min(Delta_E) corner (sigma=19.5) PASSES the floor, but a different corner
    # (sigma=6, min Delta_p_top3) shows the treatment REDUCING P(top-3) by 5pp. The old single-corner
    # gate fired here; the corner-by-corner gate must NOT.
    DIVERGENT = [
        {"sigma": 6.0,  "delta_E_prize": +0.002, "ci_lo": +0.003, "ci_hi": +0.02, "delta_p_top3": -0.05},
        {"sigma": 19.5, "delta_E_prize": +0.001, "ci_lo": +0.002, "ci_hi": +0.02, "delta_p_top3": +0.05},
    ]
    ALL_PASS = [
        {"sigma": 6.0,  "delta_E_prize": +0.010, "ci_lo": +0.004, "ci_hi": +0.03, "delta_p_top3": +0.03},
        {"sigma": 19.5, "delta_E_prize": +0.008, "ci_lo": +0.002, "ci_hi": +0.03, "delta_p_top3": +0.04},
    ]

    def test_divergent_grid_blocks_fire(self):
        g = _gate_decision(self.DIVERGENT, eps_min=0.02, n_ineligible=0)
        self.assertFalse(g["fire"], "min-DeltaE corner passes but min-p_top3 corner (-0.05) must block")
        self.assertEqual(g["adverse_corner_p3"]["sigma"], 6.0)          # the binding (worst-p3) corner
        self.assertEqual(g["adverse_corner"]["sigma"], 19.5)            # min-Delta-E corner (reporting)

    def test_old_single_corner_would_have_fired(self):
        # documents the bug: at the min-Delta-E corner alone, both old conditions pass.
        adv_E = min(self.DIVERGENT, key=lambda x: x["delta_E_prize"])
        old_fire = bool(adv_E["ci_lo"] > 0.0 and adv_E["delta_p_top3"] >= 0.02)
        self.assertTrue(old_fire)                                      # the latent false-fire
        self.assertFalse(_gate_decision(self.DIVERGENT, 0.02, 0)["fire"])   # fixed

    def test_all_corners_pass_fires(self):
        self.assertTrue(_gate_decision(self.ALL_PASS, eps_min=0.02, n_ineligible=0)["fire"])

    def test_worst_ci_lo_blocks(self):
        grid = [dict(g) for g in self.ALL_PASS]
        grid[0]["ci_lo"] = -0.001                                      # one corner's CI dips below 0
        self.assertFalse(_gate_decision(grid, eps_min=0.02, n_ineligible=0)["fire"])

    def test_ineligible_board_blocks_fire(self):
        # finding #3: every metric passes, but a lever-ineligible board is present -> no fire.
        self.assertTrue(_gate_decision(self.ALL_PASS, eps_min=0.02, n_ineligible=0)["fire"])
        self.assertFalse(_gate_decision(self.ALL_PASS, eps_min=0.02, n_ineligible=1)["fire"])

    def test_recommend_ineligible_does_not_fire(self):
        # end-to-end: an inverted (ineligible) board can never produce fire=True regardless of metrics.
        inv = {"matrix": _toy_matrix(0.40, 0.38, 0.22), "modal": (1, 0),
               "us_baseline": (1, 1), "decorrelating": (0, 1)}
        opps = [75, 72, 70, 68, 66, 64, 62, 60]
        st = {f"opp{i:02d}": p for i, p in enumerate(opps)}
        st["us"] = 58
        out = recommend_placement(st, "us", [dict(inv)], sigma_opp=SIGMA, n_sims=6000, n_bootstrap=300)
        self.assertEqual(out["n_ineligible_boards"], 1)
        self.assertFalse(out["fire"], "ineligible board must force fire=False (#3)")


class TestValidateShape(unittest.TestCase):
    """Finding #4: _validate must reject a non-9x9 board matrix (the flat-cell decode assumes 9x9)."""

    def test_non_9x9_matrix_rejected(self):
        bad = {"matrix": np.ones((8, 8)) / 64.0, "modal": (1, 0),
               "us_baseline": (1, 0), "decorrelating": (1, 1)}
        with self.assertRaises(ValueError):
            expected_prizes_placement({"us": 50, "opp": 60}, "us", [bad], k=1,
                                      sigma_opp=SIGMA, n_sims=100, seed=DEFAULT_SEED)

    def test_9x9_matrix_accepted(self):
        ok = dict(NEAR_EVEN)                                           # _toy_matrix -> (9,9)
        r = expected_prizes_placement({"us": 50, "opp": 60}, "us", [ok], k=1,
                                      sigma_opp=SIGMA, n_sims=100, seed=DEFAULT_SEED)
        self.assertIn("delta_E_prize", r)


if __name__ == "__main__":
    unittest.main()
