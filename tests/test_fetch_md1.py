"""Track B - fetch_md1 window/expect parametrization (TDD).

The MD1 fetch hardcoded a [2026-06-11T00:00Z, 2026-06-14T06:00Z] window + a count-guard of exactly 8.
That silently dropped the remaining MD1 fixtures (Sun Jun-14 + Mon Jun-15). These tests pin:
  1. the DEFAULT window constants are unchanged (byte-identical MD1 replay/provenance), and
  2. filter_window is a pure, parametrized, inclusive, sorted filter.
Offline - no network, no quota."""
from __future__ import annotations
import os
import sys
import unittest
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import fetch_md1 as fm

UTC = timezone.utc


def _ev(cid: str, iso: str) -> dict:
    return {"id": cid, "commence_time": iso, "home_team": "H", "away_team": "A"}


# 13 synthetic events spanning the real MD1 schedule shape (2 already-played dropped by the API in
# reality, so the live window starts at CAN-BIH); order is deliberately shuffled to test the sort.
EVENTS = [
    _ev("ksa_uru", "2026-06-15T22:00:00Z"),  # Mon - outside default window
    _ev("can_bih", "2026-06-12T19:00:00Z"),
    _ev("ger_cuw", "2026-06-14T17:00:00Z"),  # Sun - outside default window (after 06:00Z)
    _ev("usa_par", "2026-06-13T01:00:00Z"),
    _ev("aus_tur", "2026-06-14T04:00:00Z"),  # last fixture inside the default window
    _ev("bra_mar", "2026-06-13T22:00:00Z"),
    _ev("ned_jpn", "2026-06-14T20:00:00Z"),  # Sun - outside default window
]


class TestDefaultsUnchanged(unittest.TestCase):
    """The MD1 defaults must stay byte-identical so the frozen replay/provenance is untouched."""

    def test_win_lo_default(self):
        self.assertEqual(fm.WIN_LO, datetime(2026, 6, 11, 0, 0, tzinfo=UTC))

    def test_win_hi_default(self):
        self.assertEqual(fm.WIN_HI, datetime(2026, 6, 14, 6, 0, tzinfo=UTC))


class TestFilterWindow(unittest.TestCase):
    def test_default_window_keeps_md1_only(self):
        # default win_hi = 2026-06-14T06:00Z -> only the 4 fixtures on/before AUS-TUR (04:00Z)
        ids = [e["id"] for e in fm.filter_window(EVENTS)]
        self.assertEqual(ids, ["can_bih", "usa_par", "bra_mar", "aus_tur"])

    def test_widened_window_keeps_all(self):
        ids = [e["id"] for e in fm.filter_window(EVENTS, win_hi=datetime(2026, 6, 15, 23, 0, tzinfo=UTC))]
        self.assertEqual(ids, ["can_bih", "usa_par", "bra_mar", "aus_tur",
                               "ger_cuw", "ned_jpn", "ksa_uru"])

    def test_sorted_by_commence(self):
        out = fm.filter_window(EVENTS, win_hi=datetime(2026, 6, 16, 0, 0, tzinfo=UTC))
        times = [e["commence_time"] for e in out]
        self.assertEqual(times, sorted(times))

    def test_bounds_inclusive(self):
        lo = _ev("at_lo", "2026-06-11T00:00:00Z")
        hi = _ev("at_hi", "2026-06-14T06:00:00Z")
        ids = [e["id"] for e in fm.filter_window([lo, hi])]
        self.assertEqual(ids, ["at_lo", "at_hi"])

    def test_custom_lo(self):
        ids = [e["id"] for e in fm.filter_window(
            EVENTS, win_lo=datetime(2026, 6, 13, 0, 0, tzinfo=UTC),
            win_hi=datetime(2026, 6, 16, 0, 0, tzinfo=UTC))]
        self.assertNotIn("can_bih", ids)          # 06-12 dropped by the later lo
        self.assertIn("usa_par", ids)


if __name__ == "__main__":
    unittest.main()
