# -*- coding: utf-8 -*-
"""Tests for src/ko_cadence.py (non-frozen KO cadence driver).

Golden values are the deterministic output of the FROZEN engine + ko_adjust on the committed
snapshot data/snapshots/md4_2026-07-01T18-29-49Z.json (2026-07-01 R32 day-4 run) - i.e. the module
is pinned to reproduce the verified manual Belgium-Senegal analysis. If the frozen engine changes
these must be regenerated with it (they are an E2E regression tie, not an independent oracle).

Guard tests (None-safety, I-3, band classification) are SNAP-independent and run unconditionally.
"""
import inspect
import os
import unittest

from src import ko_cadence as kc

SNAP = "data/snapshots/md4_2026-07-01T18-29-49Z.json"
CSV = "predictions/decisions.csv"
BEL_SEN = "658ac8cbf214ca3cc150109b4ddc1e74"   # Belgium (home) vs Senegal (away)
USA_BIH = "9eeb4876001f5a52ce3c3641bd5f1f2f"   # USA vs Bosnia & Herzegovina
ARG_CPV = "3e161b2448ed76d6b0c0f5bda6fd5bf2"   # Argentina vs Cape Verde (heavy favourite)
SA_CAN = "def55b09ef3d6854e3c01e74b5c63415"    # South Africa vs Canada (recorded, pick 0-1)


class KoCadenceGuardsTest(unittest.TestCase):
    """SNAP-independent structural + None-safety guards. Always run (no skip)."""

    def test_classify_bands(self):
        self.assertEqual(kc.classify(0.010), "HOLD")
        self.assertEqual(kc.classify(0.035), "DEFER")
        self.assertEqual(kc.classify(0.060), "FLIP")

    def test_pred_helper_none_safe(self):
        self.assertIsNone(kc._pred(None))
        self.assertEqual(kc._pred({"pred": (2, 1), "ev": 1.0}), (2, 1))

    def test_council_trigger_handles_none_candidates(self):
        # ko_adjust can return best_draw/best_decisive = None (heavy favourite, floor'd out).
        fx = {"devig": {"home": 0.84, "draw": 0.10, "away": 0.06}, "argmax": (2, 0), "modal": (2, 0)}
        ko = {"best_draw": None, "best_decisive": None, "ev_argmax": (2, 0)}
        out = kc.council_trigger(fx, ko)                     # must not raise
        self.assertFalse(out["fires"])
        self.assertFalse(out["ko_flip"])

    def test_print_ko_handles_none_candidates(self):
        # Bugs 1-3 regression: best_draw / best_decisive None must not crash the print path.
        res = {
            "fixture_id": "x", "home": "A", "away": "B", "ko_rule": "FULL120",
            "devig": {"home": 0.9, "draw": 0.07, "away": 0.03},
            "total_line": 2.5, "p_over": 0.6, "mu_eff": 2.5,
            "argmax_90": (3, 0), "ev_90": 4.0, "modal_90": (3, 0),
            "ko_argmax": (3, 0), "ko_argmax_pts": 4.3,
            "best_decisive": {"pred": (3, 0), "ev": 4.3}, "best_draw": None,
            "p_draw_90": 0.02, "p_draw_scored": 0.005, "f_model": 0.25,
            "candidates": [{"pred": (3, 0), "ev_90": 4.0, "ev_120": 4.3}],
            "f_band": [{"cageyness": 0.65, "f_model": 0.5, "argmax": (3, 0),
                        "best_decisive": (3, 0), "dec_ev": 4.3, "best_draw": None, "draw_ev": None}],
            "council": {"fires": False, "reasons": [], "ko_flip": False, "ko_flip_note": None},
        }
        kc._print_ko(res)                                    # must not raise (None -> "n/a")

    def test_i3_no_result_read_no_write(self):
        """Cardinal invariant, runs UNCONDITIONALLY + CWD-independent (inspect.getsource)."""
        src = inspect.getsource(kc)
        for banned in ("points_actual", "pts_entered", "entered_pick"):
            self.assertNotIn(banned, src, f"ko_cadence must not read the result column {banned!r}")
        self.assertNotIn('"w"', src)       # no write-mode file open
        self.assertNotIn("'w'", src)
        self.assertNotIn("update_decision", src)
        self.assertNotIn("log_decision", src)


@unittest.skipUnless(os.path.exists(SNAP), f"missing committed snapshot {SNAP}")
class KoCadenceGoldenTest(unittest.TestCase):
    """Pinned to the FROZEN engine's output on the committed 2026-07-01 snapshot."""

    # ---- determinism (B4) ----
    def test_determinism_byte_identical(self):
        base = kc.baselines_from_snapshot(SNAP)
        self.assertEqual(repr(kc.flip_check(SNAP, base)), repr(kc.flip_check(SNAP, base)))

    # ---- flip_check: self-baseline -> every fixture HOLDs at exactly gap 0 ----
    def test_self_baseline_all_hold(self):
        rows = kc.flip_check(SNAP, kc.baselines_from_snapshot(SNAP))
        self.assertEqual(len(rows), 8)
        for r in rows:
            self.assertEqual(r["verdict"], "HOLD", r["home"])
            self.assertEqual(r["gap_base"], 0.0, r["home"])

    def test_no_baseline_is_reported_not_skipped(self):
        rows = kc.flip_check(SNAP, {})
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(r["verdict"] == "NO-BASELINE" for r in rows))

    # ---- flip_check: USA-Bosnia 1-0 baseline -> fresh argmax 2-0, DEFER in the ambiguous band ----
    def test_usa_bosnia_defer(self):
        rows = kc.flip_check(SNAP, {USA_BIH: (1, 0)})
        row = next(r for r in rows if r["fixture_id"] == USA_BIH)
        self.assertEqual(row["argmax"], (2, 0))
        self.assertEqual(row["verdict"], "DEFER")
        self.assertAlmostEqual(row["gap_base"], 0.0375, places=3)

    def test_baselines_from_csv(self):
        b = kc.baselines_from_csv(CSV)                       # all logged picks (new signature)
        self.assertEqual(b[SA_CAN], (0, 1))                  # recorded row, pick 0-1
        self.assertEqual(kc.baselines_from_csv(CSV, [SA_CAN]), {SA_CAN: (0, 1)})   # filtered

    # ---- ko_candidates: Belgium-Senegal GOLDEN (reproduces the verified manual run) ----
    def test_belgium_senegal_golden(self):
        res = kc.ko_candidates(SNAP, BEL_SEN)
        self.assertEqual(res["argmax_90"], (1, 0))
        self.assertAlmostEqual(res["ev_90"], 2.4543, places=3)
        self.assertEqual(res["modal_90"], (1, 1))
        self.assertAlmostEqual(res["devig"]["home"], 0.4467, places=3)
        self.assertAlmostEqual(res["mu_eff"], 2.7402, places=3)
        self.assertEqual(res["ko_argmax"], (2, 1))          # FULL120 flips 1-0 -> 2-1 (L57)
        self.assertAlmostEqual(res["ko_argmax_pts"], 2.7550, places=3)
        self.assertEqual(res["best_decisive"]["pred"], (2, 1))
        self.assertEqual(res["best_draw"]["pred"], (1, 1))
        self.assertAlmostEqual(res["best_draw"]["ev"], 1.4145, places=3)
        self.assertAlmostEqual(res["f_model"], 0.5530, places=3)

    def test_belgium_senegal_candidate_evs(self):
        res = kc.ko_candidates(SNAP, BEL_SEN, candidates=[(1, 0), (2, 1), (1, 1), (1, 2)])
        ev120 = {c["pred"]: c["ev_120"] for c in res["candidates"]}
        ev90 = {c["pred"]: c["ev_90"] for c in res["candidates"]}
        self.assertAlmostEqual(ev120[(1, 0)], 2.7199, places=3)
        self.assertAlmostEqual(ev120[(2, 1)], 2.7550, places=3)
        self.assertAlmostEqual(ev120[(1, 1)], 1.4145, places=3)   # draw craters (L54)
        self.assertAlmostEqual(ev120[(1, 2)], 2.0388, places=3)   # Senegal 2-1
        self.assertAlmostEqual(ev90[(1, 1)], 2.0650, places=3)
        self.assertLess(ev120[(1, 1)], ev90[(1, 1)])              # draw worse under FULL120

    # ---- ko_rule sensitivity: REG90 = 90' scoring (no ET) -> no flip, no f-band ----
    def test_ko_rule_reg90(self):
        res = kc.ko_candidates(SNAP, BEL_SEN, ko_rule="REG90")
        self.assertEqual(res["ko_argmax"], res["argmax_90"])     # REG90 == 90' argmax (1-0)
        self.assertEqual(res["ko_argmax"], (1, 0))
        self.assertEqual(res["f_band"], [])                      # f-band is FULL120-only
        self.assertFalse(res["council"]["ko_flip"])

    # ---- council trigger discrimination (L53) ----
    def test_council_fires_on_bel_sen(self):
        c = kc.ko_candidates(SNAP, BEL_SEN)["council"]
        self.assertTrue(c["fires"])
        self.assertTrue(any("weak-fav" in r for r in c["reasons"]))
        self.assertTrue(c["ko_flip"])

    def test_council_no_fire_on_clear_favorite(self):
        res = kc.ko_candidates(SNAP, ARG_CPV)
        self.assertGreaterEqual(max(res["devig"]["home"], res["devig"]["away"]), kc.WEAK_FAV)
        self.assertFalse(res["council"]["fires"], res["council"]["reasons"])

    # ---- ko_adjust draw domination (L54): decisive beats draw at every f ----
    def test_draw_dominated_across_f_band(self):
        res = kc.ko_candidates(SNAP, BEL_SEN)
        for s in res["f_band"]:
            if s["dec_ev"] is not None and s["draw_ev"] is not None:
                self.assertGreater(s["dec_ev"], s["draw_ev"], f"cageyness={s['cageyness']}")

    # ---- LineGuardStop robustness: every fixture in this snapshot is x.5 (no GUARD-STOP) ----
    def test_no_guard_stop_on_clean_snapshot(self):
        rows = kc.flip_check(SNAP, {})
        self.assertFalse(any(r["verdict"] == "GUARD-STOP" for r in rows))


if __name__ == "__main__":
    unittest.main()
