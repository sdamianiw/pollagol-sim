"""P3 - tests for council/run_council.py synthesis math (deterministic aggregation over lens snapshots).

Guards the apples-to-apples leverage fix (2026-06-05): council median is normalized over the reference
candidates, so the market must be too -- comparing to the FULL-board P_true inflates leverage uniformly
(a renormalization artifact). Also checks consensus / vote-tally / dissent detection.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from council.run_council import synthesize  # noqa: E402


def _rows(picks):
    """picks: list of (lens, {cand:prob}, top)."""
    return [{"lens": ln, "probs": p, "top": t, "rationale": "x", "sources": []} for ln, p, t in picks]


class TestCouncilSynthesis(unittest.TestCase):
    def test_consensus_votes_dissent_median(self):
        cands = ["A", "B", "C"]
        market = {"A": 0.50, "B": 0.30, "C": 0.20}
        rows = _rows([
            ("market",     {"A": 0.50, "B": 0.30, "C": 0.20}, "A"),
            ("form",       {"A": 0.60, "B": 0.25, "C": 0.15}, "A"),
            ("tactical",   {"A": 0.55, "B": 0.30, "C": 0.15}, "A"),
            ("baserate",   {"A": 0.45, "B": 0.35, "C": 0.20}, "A"),
            ("contrarian", {"A": 0.20, "B": 0.55, "C": 0.25}, "B"),
        ])
        syn = synthesize("t", market, cands, rows)
        self.assertEqual(syn["consensus"], "A")
        self.assertEqual(syn["votes"], {"A": 4, "B": 1})
        self.assertEqual([d["lens"] for d in syn["dissent"]], ["contrarian"])
        self.assertAlmostEqual(syn["median"]["A"], 0.50, places=9)       # median{.50,.60,.55,.45,.20}=.50
        self.assertAlmostEqual(sum(syn["council_p_true"].values()), 1.0, places=9)

    def test_vote_tie_is_no_majority_not_forced_consensus(self):
        # 2-2-1 vote split (FLAG 1): must report vote_verdict="no-majority" + contested=True, NOT a clean win.
        cands = ["X", "Y", "Z"]
        market = {"X": 0.34, "Y": 0.33, "Z": 0.33}
        rows = _rows([
            ("market",     {"X": 0.30, "Y": 0.40, "Z": 0.30}, "Y"),   # vote Y
            ("form",       {"X": 0.30, "Y": 0.45, "Z": 0.25}, "Y"),   # vote Y
            ("tactical",   {"X": 0.50, "Y": 0.30, "Z": 0.20}, "X"),   # vote X
            ("baserate",   {"X": 0.48, "Y": 0.32, "Z": 0.20}, "X"),   # vote X
            ("contrarian", {"X": 0.20, "Y": 0.25, "Z": 0.55}, "Z"),   # vote Z
        ])
        syn = synthesize("t", market, cands, rows)
        self.assertEqual(syn["vote_verdict"], "no-majority")
        self.assertEqual(syn["plurality"], ["X", "Y"])      # tie for top, sorted
        self.assertTrue(syn["contested"])

    def test_clear_majority_not_contested(self):
        cands = ["A", "B"]
        market = {"A": 0.6, "B": 0.4}
        rows = _rows([(ln, {"A": 0.7, "B": 0.3}, "A") for ln in
                      ("market", "form", "tactical", "baserate", "contrarian")])
        syn = synthesize("t", market, cands, rows)
        self.assertEqual(syn["vote_verdict"], "majority")
        self.assertFalse(syn["contested"])

    def test_leverage_uses_reference_basis_not_fullboard(self):
        # market here is FULL-board (A,B each 0.10 -> implicit tail 0.80). Over the 2 reference candidates
        # the market renormalizes to {A:0.5, B:0.5}. Lenses that exactly match -> leverage must be ~1.0,
        # NOT 5.0 (which the full-board comparison bug would produce: 0.5 / 0.10).
        cands = ["A", "B"]
        market = {"A": 0.10, "B": 0.10}
        rows = _rows([(ln, {"A": 0.5, "B": 0.5}, "A") for ln in
                      ("market", "form", "tactical", "baserate", "contrarian")])
        syn = synthesize("t", market, cands, rows)
        self.assertAlmostEqual(syn["market_ref"]["A"], 0.5, places=9)
        self.assertAlmostEqual(syn["leverage_council_vs_market"], 1.0, places=6)
        self.assertAlmostEqual(syn["market_full"]["A"], 0.10, places=9)  # full-board still available for context


if __name__ == "__main__":
    unittest.main(verbosity=2)
