"""M1 ingest - TDD (Gate 7). Parse + snapshot (reproducible replay) + 2-source cross-check; feeds M2.
Offline against a synthetic The Odds API event (no quota burned)."""
from __future__ import annotations
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ingest import parse_event, crosscheck_event, ingest_event, load_snapshot

# synthetic The Odds API event (shape per src/probe_oddssource), american odds, 2 books + totals
EVENT = {
    "id": "wc2026_ned_jpn",
    "commence_time": "2026-06-14T18:00:00Z",
    "home_team": "Netherlands",
    "away_team": "Japan",
    "bookmakers": [
        {"key": "pinnacle", "markets": [
            {"key": "h2h", "outcomes": [
                {"name": "Netherlands", "price": -160},
                {"name": "Japan", "price": 420},
                {"name": "Draw", "price": 280}]},
            {"key": "totals", "outcomes": [
                {"name": "Over", "price": -105, "point": 2.5},
                {"name": "Under", "price": -115, "point": 2.5}]}]},
        {"key": "marathonbet", "markets": [
            {"key": "h2h", "outcomes": [
                {"name": "Netherlands", "price": -150},
                {"name": "Japan", "price": 410},
                {"name": "Draw", "price": 270}]}]},
    ],
}


class TestIngest(unittest.TestCase):
    def test_parse_event(self):
        m = parse_event(EVENT)
        self.assertEqual(m["home"], "Netherlands")
        self.assertEqual(set(m["odds_1x2"]), {"home", "draw", "away"})
        self.assertEqual(m["totals"]["line"], 2.5)
        self.assertGreaterEqual(len(m["books"]), 2)
        self.assertEqual(m["fmt"], "american")
        # book-selection (H3): pinnacle (first book) has h2h + x.5 totals -> RB3-clean intra-book mu_eff
        bs = m["book_selection"]
        self.assertFalse(bs["totals_blind"])
        self.assertFalse(bs["cross_book"])
        self.assertEqual(bs["totals_book"], bs["h2h_book"])
        self.assertEqual(bs["x5_line"], 2.5)

    def test_crosscheck_passes(self):
        cc = crosscheck_event(EVENT)
        self.assertIsNotNone(cc)
        self.assertEqual(cc["favorite"], "Netherlands")
        self.assertTrue(cc["pass"])      # two books within 3pp

    def test_snapshot_roundtrip_reproduces(self):
        with tempfile.TemporaryDirectory() as d:
            res = ingest_event(EVENT, snap_dir=d)
            self.assertTrue(os.path.exists(res["snapshot_path"]))
            reloaded = load_snapshot(res["snapshot_path"])
            self.assertEqual(parse_event(reloaded["event"]), parse_event(EVENT))   # identical replay

    def test_ingest_feeds_strength(self):
        from src.strength import match_strength
        s = match_strength(parse_event(EVENT))
        self.assertAlmostEqual(sum(s["probs"].values()), 1.0, places=9)
        self.assertEqual(s["total_line"], 2.5)
        self.assertEqual(s["source"], "market")


if __name__ == "__main__":
    unittest.main()
