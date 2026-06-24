"""Tests for pool/qual_state.py - the MD-3 qualification-state engine (read-only, BUILD-NOT-FIRE).

DoD checks covered:
  (1) MUTUAL-DRAW-SECURES anchor (SUI-CAN)         (2) STRICT-DEAD-RUBBER anchor (constructed both-SAFE-ANY)
  (3) 3RD-PENDING anchor (BIH-QAT, both ELIMINATED) (4) MUST-WIN/DRAW-SUFFICIENT threshold, pairing declared
  (5) precedence 3RD-PENDING > WIN-REQUIRED         (6) (s,t) classifier multi-tie + exhaustive sweep
  (7) DECIDED branch                                (8-9) integrity guard raises  (10) component-size guard
  (11) determinism (no RNG, 2x identical)           + synthesized-pair detection.
"""
from __future__ import annotations
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pool.qual_state import (  # noqa: E402
    build_groups, build_group_table, _integrity_check, find_md3_pairs,
    _classify, qualification_states, fixture_tags, analyze_group,
)


def _t(pts: dict) -> dict:
    """Minimal table: qualification_states reads only table[team]['pts']."""
    return {tm: {"pts": p} for tm, p in pts.items()}


def _row(home, away, result=""):
    return {"home": home, "away": away, "result": result, "fixture_id": f"{home}-{away}", "utc": "2026"}


class TestAnchors(unittest.TestCase):
    def test_1_mutual_draw_secures_sui_can(self):
        st = qualification_states(_t({"SUI": 4, "CAN": 4, "BIH": 1, "QAT": 1}), ("SUI", "CAN"), ("BIH", "QAT"))
        self.assertEqual(st["SUI"]["state"], "DRAW-SUFFICIENT")
        self.assertEqual(st["CAN"]["state"], "DRAW-SUFFICIENT")
        tags = {t["fixture"]: t["tag"] for t in fixture_tags(st, ("SUI", "CAN"), ("BIH", "QAT"))}
        self.assertEqual(tags[("SUI", "CAN")], "MUTUAL-DRAW-SECURES")

    def test_2_strict_dead_rubber_constructed(self):
        st = qualification_states(_t({"A": 6, "B": 6, "C": 0, "D": 0}), ("A", "B"), ("C", "D"))
        self.assertEqual(st["A"]["state"], "SAFE-ANY")
        self.assertEqual(st["B"]["state"], "SAFE-ANY")
        tags = {t["fixture"]: t["tag"] for t in fixture_tags(st, ("A", "B"), ("C", "D"))}
        self.assertEqual(tags[("A", "B")], "STRICT-DEAD-RUBBER")

    def test_3_third_pending_bih_qat_not_mustwin(self):
        st = qualification_states(_t({"SUI": 4, "CAN": 4, "BIH": 1, "QAT": 1}), ("SUI", "CAN"), ("BIH", "QAT"))
        self.assertEqual(st["BIH"]["state"], "ELIMINATED")   # not even winning guarantees top-2
        self.assertEqual(st["QAT"]["state"], "ELIMINATED")
        self.assertTrue(st["BIH"]["best_third_alive"])
        tags = {t["fixture"]: t["tag"] for t in fixture_tags(st, ("SUI", "CAN"), ("BIH", "QAT"))}
        self.assertEqual(tags[("BIH", "QAT")], "3RD-PENDING")

    def test_4_mustwin_threshold_pairing_declared(self):
        # pairing DECLARED: game1=(Scotland,Brazil), game2=(Morocco,Haiti).
        st = qualification_states(_t({"Brazil": 4, "Morocco": 4, "Scotland": 3, "Haiti": 0}),
                                  ("Scotland", "Brazil"), ("Morocco", "Haiti"))
        self.assertEqual(st["Scotland"]["state"], "MUST-WIN")        # a draw + Morocco-win => s=2 ELIMINATED
        self.assertFalse(st["Scotland"]["draw_secures"])
        self.assertEqual(st["Brazil"]["state"], "DRAW-SUFFICIENT")   # a loss + Morocco-win => ELIMINATED
        tags = {t["fixture"]: t["tag"] for t in fixture_tags(st, ("Scotland", "Brazil"), ("Morocco", "Haiti"))}
        self.assertEqual(tags[("Scotland", "Brazil")], "WIN-REQUIRED")


class TestPrecedence(unittest.TestCase):
    def test_5_third_pending_beats_win_required(self):
        # Synthetic states isolating the precedence: X triggers rule-1 (ELIMINATED+best_third),
        # Y triggers rule-4 (MUST-WIN, draw_secures False). Rule 1 must win -> 3RD-PENDING.
        states = {
            "X": {"state": "ELIMINATED", "draw_secures": False, "best_third_alive": True,
                  "tiebreak_sensitive": False},
            "Y": {"state": "MUST-WIN", "draw_secures": False, "best_third_alive": True,
                  "tiebreak_sensitive": False},
        }
        tags = fixture_tags(states, ("X", "Y"), ("X", "Y"))   # both slots = same pair; tag identical
        self.assertEqual(tags[0]["tag"], "3RD-PENDING")


class TestClassifier(unittest.TestCase):
    def test_6a_multi_tie_outcomes(self):
        self.assertEqual(_classify(5, [5, 5, 3]), "TOP2-TIEBREAK")   # s=0,t=2 (triple-tie-1st)
        self.assertEqual(_classify(5, [5, 5, 5]), "TOP2-TIEBREAK")   # s=0,t=3 (quad-level)
        self.assertEqual(_classify(5, [7, 5, 5]), "TOP2-TIEBREAK")   # s=1,t=2 (one-above-triple-tie)
        self.assertEqual(_classify(5, [3, 3, 3]), "TOP2-GUARANTEED")  # s=0,t=0
        self.assertEqual(_classify(5, [7, 3, 3]), "TOP2-GUARANTEED")  # s=1,t=0
        self.assertEqual(_classify(5, [7, 7, 3]), "ELIMINATED")       # s=2
        self.assertEqual(_classify(5, [7, 7, 7]), "ELIMINATED")       # s=3

    def test_6b_exhaustive_sweep_no_unclassified(self):
        valid = {"ELIMINATED", "TOP2-GUARANTEED", "TOP2-TIEBREAK"}
        for s in range(4):
            for t in range(4 - s):
                others = [10] * s + [5] * t + [0] * (3 - s - t)
                self.assertIn(_classify(5, others), valid, f"(s={s},t={t}) unclassified")


class TestDecidedBranch(unittest.TestCase):
    def test_7_decided(self):
        # Synthetic states (DECIDED is structurally unreachable in a real 4-team group): both
        # ELIMINATED and neither best_third_alive -> DECIDED (checked before WIN-REQUIRED).
        states = {
            "A": {"state": "ELIMINATED", "draw_secures": False, "best_third_alive": False,
                  "tiebreak_sensitive": False},
            "B": {"state": "ELIMINATED", "draw_secures": False, "best_third_alive": False,
                  "tiebreak_sensitive": False},
        }
        tags = fixture_tags(states, ("A", "B"), ("A", "B"))
        self.assertEqual(tags[0]["tag"], "DECIDED")


class TestIntegrityGuards(unittest.TestCase):
    def test_8_sum_pts_violation_raises(self):
        bad = {"A": {"pts": 9, "gf": 0, "ga": 0}, "B": {"pts": 0, "gf": 0, "ga": 0}}
        with self.assertRaises(ValueError):
            _integrity_check(bad, frozenset({"A", "B"}), n_dec=1, n_draw=0)  # 9 != 3·1

    def test_9_gf_ga_violation_raises(self):
        bad = {"A": {"pts": 3, "gf": 2, "ga": 0}, "B": {"pts": 0, "gf": 0, "ga": 0}}
        with self.assertRaises(ValueError):
            _integrity_check(bad, frozenset({"A", "B"}), n_dec=1, n_draw=0)  # ΣGF=2 != ΣGA=0

    def test_8b_valid_build_does_not_raise(self):
        rows = [_row("A", "B", "2-1"), _row("C", "D", "0-0")]
        tbl = build_group_table(rows, frozenset({"A", "B", "C", "D"}))
        self.assertEqual(tbl["A"]["pts"], 3)
        self.assertEqual(tbl["C"]["pts"], 1)


class TestGroupStructure(unittest.TestCase):
    def test_10_component_size_guard(self):
        rows = [_row("A", "B"), _row("B", "C"), _row("A", "C")]   # triangle -> component size 3
        with self.assertRaises(ValueError):
            build_groups(rows)

    def test_synthesized_pair_detection(self):
        # group with only 4 of 6 pairs recorded (played) -> the 2 complement pairs are synthesized.
        rows = [_row("A", "B", "1-0"), _row("C", "D", "1-0"),
                _row("A", "C", "1-0"), _row("B", "D", "1-0")]
        pairs = find_md3_pairs(rows, frozenset({"A", "B", "C", "D"}))
        self.assertEqual(len(pairs), 2)
        self.assertTrue(all(p["synthesized"] for p in pairs))
        got = {tuple(sorted((p["home"], p["away"]))) for p in pairs}
        self.assertEqual(got, {("A", "D"), ("B", "C")})


class TestDeterminism(unittest.TestCase):
    def test_11_qualification_states_identical_twice(self):
        tbl = _t({"SUI": 4, "CAN": 4, "BIH": 1, "QAT": 1})
        a = qualification_states(tbl, ("SUI", "CAN"), ("BIH", "QAT"))
        b = qualification_states(tbl, ("SUI", "CAN"), ("BIH", "QAT"))
        self.assertEqual(a, b)

    def test_analyze_group_identical_twice(self):
        rows = [_row("A", "B", "2-1"), _row("C", "D", "0-0"),
                _row("A", "C", "1-0"), _row("B", "D", "1-1")]
        members = frozenset({"A", "B", "C", "D"})
        self.assertEqual(str(analyze_group(members, rows)), str(analyze_group(members, rows)))


if __name__ == "__main__":
    unittest.main()
