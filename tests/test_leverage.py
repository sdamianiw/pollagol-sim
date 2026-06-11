import os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pool.leverage import compute, OWNERSHIP_PRIOR_NAMED

DATA = os.path.join(ROOT, "data", "outrights.json")

class TestLeverageContract(unittest.TestCase):
    def setUp(self):
        self.p_true, self.own, self.over, self.rows, _ = compute(DATA, ownership_source="prior")
        self.named = set(OWNERSHIP_PRIOR_NAMED)

    def test_T1_ptrue_normalized(self):
        self.assertAlmostEqual(sum(self.p_true.values()), 1.0, places=6)

    def test_T2_tail_leverage_undefined(self):
        # Any team without a defensible ownership prior must NOT receive a leverage number.
        for r in self.rows:
            if r["team"] not in self.named:
                self.assertIsNone(r["leverage"],
                    f'{r["team"]} got leverage {r["leverage"]} from synthetic ownership; must be None')

    def test_T3_candidates_subset_of_named(self):
        cands = {r["team"] for r in self.rows if r.get("contrarian_candidate")}
        self.assertTrue(cands.issubset(self.named),
            f"contrarian candidates {cands} leak outside the prior-defensible named set {self.named}")

    def test_T4_candidates_invariant_to_gamma(self):
        lo = {r["team"] for r in compute(DATA, "prior", gamma=0.5)[3] if r.get("contrarian_candidate")}
        hi = {r["team"] for r in compute(DATA, "prior", gamma=3.0)[3] if r.get("contrarian_candidate")}
        self.assertEqual(lo, hi,
            f"candidate set changes with gamma ({lo} vs {hi}) -> gamma is generating candidates (artifact)")

    def test_T5_prior_candidate_has_inversion_note(self):
        for r in self.rows:
            if r.get("contrarian_candidate"):
                self.assertIn("inverts", (r.get("note") or "").lower(),
                    f'{r["team"]} candidate lacks the prior-inversion break-even note')

    def test_T6_observed_runs_with_override(self):
        # PICKS_VISIBLE flipped True (pollaya screenshots 2026-05-30): observed is now REAL.
        from pool.leverage import PICKS_VISIBLE
        self.assertTrue(PICKS_VISIBLE, "PICKS_VISIBLE must be True after platform evidence")
        ov = {"Spain": 0.5, "Brazil": 0.5}
        p, o, ovr, rows, _ = compute(DATA, ownership_source="observed", ownership_override=ov)
        self.assertEqual(o, ov)                              # observed uses the snapshot
        with self.assertRaises(ValueError):                 # observed w/o override -> needs snapshot
            compute(DATA, ownership_source="observed")
        with self.assertRaises(ValueError):                 # polled still needs override
            compute(DATA, ownership_source="polled")

    def test_T7_prior_still_gated(self):
        from pool.leverage import is_gated
        self.assertTrue(is_gated("prior"))                  # visibility does NOT auto-finalize prior
        self.assertFalse(is_gated("observed"))
        self.assertFalse(is_gated("polled"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
