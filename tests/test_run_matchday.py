"""M8 run_matchday - TDD (P4c). Orchestrator wiring + the x.5 runtime guard (H1) + offline purity
(no evals/M7 import) + determinism (snapshot-reproducible). The guard MUST STOP on non-x.5 totals lines
(never coerce to 2.5), because the live WC board is NON_X5_PRESENT (src/probe_lines.py, 2026-06-06)."""
from __future__ import annotations
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.lines import is_half_line
from src.run_matchday import run_match, guard_total_line, LineGuardStop


def _event(line=2.5, with_totals=True):
    """Minimal The-Odds-API-shaped event (american). home=Mexico fav, away=South Africa."""
    markets = [{"key": "h2h", "outcomes": [
        {"name": "Mexico", "price": -150},
        {"name": "South Africa", "price": 400},
        {"name": "Draw", "price": 300},
    ]}]
    if with_totals:
        markets.append({"key": "totals", "outcomes": [
            {"name": "Over", "price": -110, "point": line},
            {"name": "Under", "price": -110, "point": line},
        ]})
    return {"id": "TEST1", "home_team": "Mexico", "away_team": "South Africa",
            "commence_time": "2026-06-11T19:00:00Z", "bookmakers": [{"key": "pinnacle", "markets": markets}]}


def _book(key, line):
    """A bookmaker with h2h + (optional) totals at `line` (None = h2h only)."""
    mk = [{"key": "h2h", "outcomes": [
        {"name": "Mexico", "price": -150}, {"name": "South Africa", "price": 400}, {"name": "Draw", "price": 300}]}]
    if line is not None:
        mk.append({"key": "totals", "outcomes": [
            {"name": "Over", "price": -110, "point": line}, {"name": "Under", "price": -110, "point": line}]})
    return {"key": key, "markets": mk}


def _multi_event(*books):
    return {"id": "M", "home_team": "Mexico", "away_team": "South Africa",
            "commence_time": "2026-06-11T19:00:00Z", "bookmakers": list(books)}


# --- Real events for the L17 favorite-inversion guard, trimmed to the single book parse_event would
# select (first with h2h + x.5 totals). Prices extracted VERBATIM from the Jun-6 board snapshot
# data/snapshots/probe_lines_2026-06-06T13-23-59Z.json (reproduced 2026-06-11, see lessons.md L17). ---
_KOR_CZE_EVENT = {   # betonlineag: de-vig H=0.3539/D=0.3107/A=0.3355 (Korea fav) but DC matrix A=0.3605 (Czech) -> FIRES
    "id": "384cbb5d76b535896a24fe65f93cfac8",
    "home_team": "South Korea", "away_team": "Czech Republic",
    "commence_time": "2026-06-12T02:00:00Z",
    "bookmakers": [{"key": "betonlineag", "markets": [
        {"key": "h2h", "outcomes": [
            {"name": "Czech Republic", "price": 188},
            {"name": "South Korea", "price": 173},
            {"name": "Draw", "price": 211}]},
        {"key": "totals", "outcomes": [
            {"name": "Over", "price": 118, "point": 2.5},
            {"name": "Under", "price": -138, "point": 2.5}]}]}],
}
_MEX_RSA_EVENT = {   # coolbet: Mexico dominant (de-vig H=0.6727, matrix H=0.6727) -> guard SILENT
    "id": "80d82d1113934bfbea4ce8daf37a2433",
    "home_team": "Mexico", "away_team": "South Africa",
    "commence_time": "2026-06-11T19:00:00Z",
    "bookmakers": [{"key": "coolbet", "markets": [
        {"key": "h2h", "outcomes": [
            {"name": "Mexico", "price": -227},
            {"name": "South Africa", "price": 850},
            {"name": "Draw", "price": 330}]},
        {"key": "totals", "outcomes": [
            {"name": "Over", "price": 115, "point": 2.5},
            {"name": "Under", "price": -141, "point": 2.5}]}]}],
}


class TestFavoriteInversionGuard(unittest.TestCase):
    """L17 output-layer guard: detection-only flag when the DC matrix favorite disagrees with the
    de-vigged h2h market favorite. NEVER changes the pick (anti-tuning)."""

    def test_guard_fires_on_kor_cze(self):
        ig = run_match(_KOR_CZE_EVENT)["inversion_guard"]
        self.assertTrue(ig["fired"], "near-even KOR-CZE should invert (draw deficit leaks to away)")
        self.assertEqual(ig["dv_fav"], "home")      # market: South Korea
        self.assertEqual(ig["matrix_fav"], "away")  # matrix: Czech Republic

    def test_guard_silent_on_mex_rsa(self):
        ig = run_match(_MEX_RSA_EVENT)["inversion_guard"]
        self.assertFalse(ig["fired"], "dominant favorite MEX-RSA must NOT invert")
        self.assertEqual(ig["dv_fav"], "home")
        self.assertEqual(ig["matrix_fav"], "home")

    def test_guard_key_always_in_summary(self):
        s = run_match(_MEX_RSA_EVENT)
        self.assertIn("inversion_guard", s)
        self.assertIn("fired", s["inversion_guard"])

    def test_guard_does_not_fire_on_elo_source(self):
        # Elo-sourced strength has no h2h market to compare -> guard skips gracefully (fired False).
        from src.run_matchday import guard_favorite_inversion
        from src.strength import match_strength
        from src.model import match_distribution
        st = match_strength({"elo": {"home": 1800, "away": 1800}})
        mat = match_distribution(st)
        ig = guard_favorite_inversion(st, mat, "ELO1")
        self.assertFalse(ig["fired"])

    def test_guard_never_mutates_pick(self):
        # Detection only: the EV pick on KOR-CZE is identical whether or not we read the guard.
        s = run_match(_KOR_CZE_EVENT)
        self.assertTrue(s["inversion_guard"]["fired"])
        self.assertEqual(len(s["opt"]["pick"]), 2)   # pick still produced, unchanged by the guard


class TestHalfLine(unittest.TestCase):
    def test_x5_true(self):
        for v in (1.5, 2.5, 3.5, 4.5):
            self.assertTrue(is_half_line(v), v)

    def test_non_x5_false(self):
        for v in (1.75, 2.0, 2.25, 2.75, 3.0, 4.0, 4.25):
            self.assertFalse(is_half_line(v), v)

    def test_none_false(self):
        self.assertFalse(is_half_line(None))


class TestGuard(unittest.TestCase):
    def test_integer_line_only_goes_totals_blind(self):
        # book-selection: a non-x.5-ONLY board -> totals-blind fallback (graceful, flagged), NOT a guard STOP
        s = run_match(_event(line=2.0))
        self.assertIsNone(s["mu_eff"])
        self.assertTrue(s["match"]["book_selection"]["totals_blind"])
        self.assertEqual(len(s["opt"]["pick"]), 2)

    def test_quarter_line_only_goes_totals_blind(self):
        s = run_match(_event(line=2.25))
        self.assertIsNone(s["mu_eff"])
        self.assertTrue(s["match"]["book_selection"]["totals_blind"])

    def test_x5_line_runs(self):
        s = run_match(_event(line=2.5))
        self.assertEqual(len(s["opt"]["pick"]), 2)
        self.assertIsNotNone(s["mu_eff"])
        bs = s["match"]["book_selection"]
        self.assertFalse(bs["totals_blind"])
        self.assertEqual(bs["x5_line"], 2.5)
        self.assertEqual(bs["totals_book"], bs["h2h_book"])     # RB3-clean: same book

    def test_no_totals_runs_nested_solve(self):
        s = run_match(_event(with_totals=False))   # p_over None -> guard does NOT fire
        self.assertEqual(len(s["opt"]["pick"]), 2)
        self.assertIsNone(s["mu_eff"])
        self.assertTrue(s["match"]["book_selection"]["totals_blind"])

    def test_guard_does_not_coerce(self):
        # defense-in-depth: a non-x.5 strength dict (bypassing book-selection) must RAISE, never coerce to 2.5
        with self.assertRaises(LineGuardStop):
            guard_total_line({"p_over": 0.55, "total_line": 2.0}, "X")
        guard_total_line({"p_over": 0.55, "total_line": 2.5}, "X")    # x.5 passes through
        guard_total_line({"p_over": None, "total_line": None}, "X")   # no totals passes through


class TestBookSelection(unittest.TestCase):
    def test_recovers_x5_from_later_book(self):
        # opener case: first h2h book has NO totals; a later book has h2h + 2.5 -> mu_eff recovered, RB3-clean
        s = run_match(_multi_event(_book("marathonbet", None), _book("pinnacle", 2.5)))
        bs = s["match"]["book_selection"]
        self.assertFalse(bs["totals_blind"])
        self.assertEqual(bs["h2h_book"], "pinnacle")
        self.assertEqual(bs["totals_book"], "pinnacle")            # same book (RB3-clean)
        self.assertIsNotNone(s["mu_eff"])

    def test_prefers_x5_over_non_x5(self):
        # first book h2h + 2.25 (non-x.5), second h2h + 2.5 -> selects the x.5 book
        s = run_match(_multi_event(_book("pinnacle", 2.25), _book("bet365", 2.5)))
        bs = s["match"]["book_selection"]
        self.assertEqual(bs["h2h_book"], "bet365")
        self.assertEqual(bs["x5_line"], 2.5)
        self.assertFalse(bs["totals_blind"])

    def test_all_non_x5_totals_blind(self):
        # no book has x.5 totals -> totals-blind fallback, hard flag, 1X2 from the FIRST h2h book
        s = run_match(_multi_event(_book("pinnacle", 2.25), _book("bet365", 2.0)))
        bs = s["match"]["book_selection"]
        self.assertTrue(bs["totals_blind"])
        self.assertEqual(bs["h2h_book"], "pinnacle")
        self.assertIsNone(bs["totals_book"])
        self.assertIsNone(s["mu_eff"])
        self.assertIn("totals-blind", bs["text"])

    def test_first_book_x5_unchanged(self):
        s = run_match(_multi_event(_book("pinnacle", 2.5), _book("bet365", 2.0)))
        bs = s["match"]["book_selection"]
        self.assertEqual(bs["h2h_book"], "pinnacle")
        self.assertFalse(bs["cross_book"])
        self.assertFalse(bs["totals_blind"])


class TestDeterminism(unittest.TestCase):
    def test_reproducible(self):
        a = run_match(_event(line=2.5))
        b = run_match(_event(line=2.5))
        self.assertEqual(a["opt"]["pick"], b["opt"]["pick"])
        self.assertEqual(a["opt"]["ev"], b["opt"]["ev"])
        self.assertEqual(a["modal"], b["modal"])


class TestOfflinePurity(unittest.TestCase):
    def test_no_evals_import_statement(self):
        # the word "evals" may appear in the docstring; what matters is no IMPORT of it
        with open(os.path.join(ROOT, "src", "run_matchday.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("import evals", src)
        self.assertNotIn("from evals", src)

    def test_no_evals_imported_at_runtime(self):
        code = ("import sys; import src.run_matchday; "
                "bad=[m for m in sys.modules if m=='evals' or m.startswith('evals.')]; "
                "sys.exit(1 if bad else 0)")
        r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"evals imported by run_matchday: {r.stdout} {r.stderr}")


if __name__ == "__main__":
    unittest.main()
