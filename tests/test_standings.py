"""Gate 6: standings ingest - DETERMINISTIC field statistics only (no Monte Carlo, no council)."""
from __future__ import annotations
import csv
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import decision_score as ds
from src import decisionlog as dl

# Small synthetic field. desc = [15, 12, 11, 10, 8]; median 11; mean 11.2; 3rd place (podium_cut) = 11.
SAMPLE = {"date": "2026-06-14", "n": 5, "points": [10, 12, 8, 15, 11],
          "our_points": 11, "our_rank": 3, "source": "synthetic"}


class TestStandingsStats(unittest.TestCase):
    def setUp(self):
        self.s = ds.standings_stats(SAMPLE, override_value=-4)

    def test_fields_complete(self):
        for f in ds.STANDINGS_LOG_FIELDS:
            self.assertIn(f, self.s)
        self.assertEqual(set(self.s), set(ds.STANDINGS_LOG_FIELDS))

    def test_mean_median_leader(self):
        self.assertAlmostEqual(self.s["mean"], 11.2, places=3)
        self.assertEqual(self.s["median"], 11)
        self.assertEqual(self.s["leader"], 15)

    def test_podium_cut_and_gaps(self):
        self.assertEqual(self.s["podium_cut"], 11)      # 3rd of [15,12,11,10,8]
        self.assertEqual(self.s["gap_podium"], 0)       # our 11 - 11
        self.assertEqual(self.s["gap_median"], 0)       # our 11 - 11

    def test_percentile(self):
        # points <= 11 -> {10, 8, 11} = 3/5 = 0.6
        self.assertAlmostEqual(self.s["our_pctl"], 0.6, places=4)

    def test_override_threaded(self):
        self.assertEqual(self.s["override_value"], "-4")
        self.assertEqual(ds.standings_stats(SAMPLE, None)["override_value"], "")

    def test_deterministic_no_monte_carlo_keys(self):
        for forbidden in ("council", "monte_carlo", "sim", "rng", "seed"):
            self.assertNotIn(forbidden, self.s)
        # determinism: identical input -> identical output
        self.assertEqual(ds.standings_stats(SAMPLE, -4), self.s)


class TestIngestStandings(unittest.TestCase):
    def test_appends_row_with_override_from_decisions(self):
        with tempfile.TemporaryDirectory() as d:
            # a decisions.csv with one dual played row -> override_value = pts_entered - points_actual = 0
            dec = os.path.join(d, "decisions.csv")
            with open(dec, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=dl.FIELDS)
                w.writeheader()
                row = {k: "" for k in dl.FIELDS}
                row.update({"fixture_id": "F", "result": "2-0", "points_actual": "4", "points_b1": "4",
                            "points_b2": "4", "brier_model": "0.1", "brier_market": "0.1", "pts_entered": "4"})
                w.writerow(row)
            sroot = os.path.join(d, "standings")
            os.makedirs(os.path.join(sroot, "2026-06-14"))
            with open(os.path.join(sroot, "2026-06-14", "standings.json"), "w", encoding="utf-8") as f:
                json.dump(SAMPLE, f)
            logp = os.path.join(d, "standings_log.csv")
            s = ds.ingest_standings("2026-06-14", decisions_path=dec, log_path=logp, standings_root=sroot)
            self.assertEqual(s["override_value"], "0")          # 4 - 4 from the one dual row
            self.assertTrue(os.path.exists(logp))
            with open(logp, encoding="utf-8") as f:
                logged = list(csv.DictReader(f))
            self.assertEqual(len(logged), 1)
            self.assertEqual(logged[0]["our_pts"], "11")
            self.assertEqual(logged[0]["n"], "5")

    def test_missing_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                ds.ingest_standings("2099-01-01", decisions_path=os.path.join(d, "x.csv"),
                                    log_path=os.path.join(d, "log.csv"), standings_root=d)


if __name__ == "__main__":
    unittest.main()
