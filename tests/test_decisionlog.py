"""M6 logging - TDD (Gate 7). Every row sourced+dated; review filter surfaces played-and-unreviewed."""
from __future__ import annotations
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.decisionlog import log_decision, read_decisions, played_unreviewed

_ROW = {"fixture_id": "wc2026_ned_jpn", "home": "Netherlands", "away": "Japan", "pick": "2-0",
        "ev": 3.9, "p_pick": 0.12, "total_line": 2.5, "context_flag": "neutral",
        "source": "The Odds API 2026-06-14", "reasoning": "argmax E[pts]; fav -160 de-vigged 0.61"}


class TestDecisionLog(unittest.TestCase):
    def test_requires_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "decisions.csv")
            with self.assertRaises(ValueError):
                log_decision({"home": "A", "away": "B", "pick": "1-0"}, path=p)   # no source/reasoning

    def test_log_and_read_stamps_utc(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "decisions.csv")
            log_decision(_ROW, path=p)
            log_decision({**_ROW, "pick": "1-0"}, path=p)
            rows = read_decisions(p)
            self.assertEqual(len(rows), 2)
            for r in rows:
                self.assertTrue(r["utc"] and r["source"] and r["reasoning"])

    def test_played_unreviewed_filter(self):
        rows = [{"result": "2-1", "reviewed": ""},      # played, unreviewed -> surfaced
                {"result": "", "reviewed": ""},          # not played -> hidden
                {"result": "0-0", "reviewed": "y"}]      # reviewed -> hidden
        out = played_unreviewed(rows)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["result"], "2-1")


if __name__ == "__main__":
    unittest.main()
