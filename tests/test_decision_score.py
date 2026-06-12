"""Gate for Phase 2 (execution-discipline loop). TDD RED-first.

Scores recorded picks under the CORRECTED rubric (exact=3) against B1 (favorite 1-0/0-1) and B2 (model
modal), and tracks cumulative us-vs-B1-vs-B2 + two Brier conventions. NO result ever flows back into a
model parameter (I3) - this module reads decisions.csv and the optimizer's pure points(); it never writes
a model constant.

Brier conventions (F12):
  brier_model  = matrix-implied 1X2 from the PRE-context DC fit (implied_1x2(match_distribution)) - the
                 MODEL-HEALTH metric, the thing L17 draw-compression degrades; same object the L17
                 inversion guard reads (run_matchday.py). PRIMARY.
  brier_market = de-vigged MARKET 1X2 - INPUT-CALIBRATION reference (expected ~good by construction,
                 NOT a model signal). SECONDARY. Reproduces the auditor's hand-calc.

Targets are the Jun-11 snapshot replay (full precision -> 6dp stored), MEX-RSA 2-0 and KOR-CZE 2-1
(both home wins). brier_market(MEX)=0.1602 at full precision (auditor's 0.1603 used 3dp-rounded inputs;
the 0.0001 is pure input rounding, this pipeline is full-precision). Stdlib + the src engine.
"""
from __future__ import annotations
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import decision_score as ds
from src import decisionlog as dl

# Forecast values from the Jun-11 snapshot replay (6dp). devig_* = de-vig market 1X2;
# m_* = PRE-context DC implied_1x2 (the F12 model-health forecast).
MEX = {"home": "Mexico", "away": "South Africa", "pick": "1-0", "modal": "1-0", "favorite_pick": "1-0",
       "devig_h": "0.678787", "devig_d": "0.212568", "devig_a": "0.108646",
       "m_h": "0.678787", "m_d": "0.216839", "m_a": "0.104375"}
KOR = {"home": "South Korea", "away": "Czech Republic", "pick": "1-1", "modal": "1-1", "favorite_pick": "1-0",
       "devig_h": "0.365907", "devig_d": "0.309794", "devig_a": "0.324299",
       "m_h": "0.365907", "m_d": "0.290633", "m_a": "0.343459"}


class TestHelpers(unittest.TestCase):
    def test_parse_score(self):
        self.assertEqual(ds.parse_score("2-0"), (2, 0))
        self.assertEqual(ds.parse_score("1-1"), (1, 1))

    def test_outcome_class(self):
        self.assertEqual(ds.outcome_class((2, 0)), "home")
        self.assertEqual(ds.outcome_class((1, 1)), "draw")
        self.assertEqual(ds.outcome_class((0, 1)), "away")

    def test_favorite_pick_home_and_away(self):
        self.assertEqual(ds.favorite_pick({"home": 0.6, "draw": 0.2, "away": 0.2}), (1, 0))
        self.assertEqual(ds.favorite_pick({"home": 0.2, "draw": 0.2, "away": 0.6}), (0, 1))
        # B1 never picks a draw even when the draw is modal; ties on win-prob -> home
        self.assertEqual(ds.favorite_pick({"home": 0.3, "draw": 0.4, "away": 0.3}), (1, 0))

    def test_brier_multiclass(self):
        # uniform 1/3 over 3 classes -> 2/3 ; perfect -> 0
        p = {"home": 1 / 3, "draw": 1 / 3, "away": 1 / 3}
        self.assertAlmostEqual(ds.brier(p, "home"), 2 / 3, places=10)
        self.assertAlmostEqual(ds.brier({"home": 1.0, "draw": 0.0, "away": 0.0}, "home"), 0.0, places=10)


class TestScoring(unittest.TestCase):
    """points via the SINGLE corrected rubric (src.optimizer.points); both Brier conventions."""
    def test_points_mex(self):
        s = ds.score_row(MEX, (2, 0))
        self.assertEqual((s["points_actual"], s["points_b1"], s["points_b2"]), (4, 4, 4))

    def test_points_kor(self):
        s = ds.score_row(KOR, (2, 1))
        self.assertEqual((s["points_actual"], s["points_b1"], s["points_b2"]), (1, 4, 1))

    def test_brier_market(self):
        self.assertAlmostEqual(ds.score_row(MEX, (2, 0))["brier_market"], 0.1602, places=4)
        self.assertAlmostEqual(ds.score_row(KOR, (2, 1))["brier_market"], 0.6032, places=4)

    def test_brier_model_pre_context(self):
        self.assertAlmostEqual(ds.score_row(MEX, (2, 0))["brier_model"], 0.1611, places=4)
        self.assertAlmostEqual(ds.score_row(KOR, (2, 1))["brier_model"], 0.6045, places=4)


class TestCumulative(unittest.TestCase):
    def _scored(self):
        mex = {**MEX, "result": "2-0", **{k: str(v) for k, v in ds.score_row(MEX, (2, 0)).items()}}
        kor = {**KOR, "result": "2-1", **{k: str(v) for k, v in ds.score_row(KOR, (2, 1)).items()}}
        return [mex, kor]

    def test_totals_and_diffs(self):
        c = ds.cumulative(self._scored())
        self.assertEqual((c["us"], c["b1"], c["b2"]), (5, 8, 5))
        self.assertEqual((c["us_minus_b1"], c["us_minus_b2"]), (-3, 0))
        self.assertEqual(c["n"], 2)

    def test_mean_briers_both_conventions(self):
        c = ds.cumulative(self._scored())
        self.assertAlmostEqual(c["mean_brier_market"], 0.3817, places=4)   # input-cal reference
        self.assertAlmostEqual(c["mean_brier_model"], 0.3828, places=4)    # F12 PRIMARY (model-health)

    def test_skips_unplayed_rows(self):
        rows = self._scored() + [{**MEX, "result": ""}]   # an unplayed row is ignored
        self.assertEqual(ds.cumulative(rows)["n"], 2)

    def test_small_n_caveat_present(self):
        text = ds.summary_text(ds.cumulative(self._scored()))
        self.assertIn("280", text)                 # the ~280-match threshold
        self.assertRegex(text.lower(), r"do not act|don't act")


class TestSchemaMigrateUpdate(unittest.TestCase):
    OLD = ["utc", "fixture_id", "home", "away", "pick", "ev", "p_pick", "total_line",
           "context_flag", "source", "reasoning", "result", "reviewed"]

    def _write_old_csv(self):
        import csv
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=self.OLD)
            w.writeheader()
            w.writerow({"utc": "2026-06-11T19:00:00Z", "fixture_id": "FID1", "home": "Mexico",
                        "away": "South Africa", "pick": "1-0", "ev": "3.383", "p_pick": "0.1461",
                        "total_line": "2.5", "context_flag": "['neutral']", "source": "x",
                        "reasoning": "y, with a comma", "result": "", "reviewed": ""})
        return path

    def test_migrate_adds_new_cols_idempotently(self):
        path = self._write_old_csv()
        try:
            dl.migrate_schema(path)
            rows = dl.read_decisions(path)
            self.assertIn("brier_model", rows[0])
            self.assertIn("favorite_pick", rows[0])
            self.assertEqual(rows[0]["pick"], "1-0")            # existing value preserved
            self.assertEqual(rows[0]["reasoning"], "y, with a comma")  # comma survives quoting
            dl.migrate_schema(path)                              # idempotent
            self.assertEqual(len(dl.read_decisions(path)), 1)
        finally:
            os.unlink(path)

    def test_update_decision_writes_one_row(self):
        path = self._write_old_csv()
        try:
            dl.migrate_schema(path)
            dl.update_decision("FID1", {"result": "2-0", "points_actual": "4"}, path)
            rows = dl.read_decisions(path)
            self.assertEqual(rows[0]["result"], "2-0")
            self.assertEqual(rows[0]["points_actual"], "4")
            self.assertEqual(rows[0]["reasoning"], "y, with a comma")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
