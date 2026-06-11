import os, sys, json, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pool.ingest_ownership import (
    load_observed, load_observed_from_snapshot, laplace_ownership, laplace_ownership_with_residual,
    blanks_chalk_resolved, ownership_model_declared, _assert_ownership_model_declared, SENTINEL,
)
from pool.podium_montecarlo import _SENTINEL
from council.run_council import market_p_true

SNAP = os.path.join(ROOT, "data", "snapshots", "observed_ownership_2026-06-06.json")
AWARDS = ["champion", "top_scorer", "mvp", "best_gk"]
# Champion observed (Sebas excluded): 7 deciders / 12 blanks; union K_cand = 7 (top-6 + Uruguay).
CHAMP_COUNTS = {"Brazil": 2, "Portugal": 2, "Spain": 2, "Uruguay": 1}
CHAMP_NAMED = ["Spain", "France", "England", "Brazil", "Argentina", "Portugal", "Uruguay"]


class TestLaplaceSmoothing(unittest.TestCase):
    def test_sum_to_one_with_sentinel(self):
        own = laplace_ownership_with_residual(CHAMP_COUNTS, n_opp=19, alpha=1.0, candidate_names=CHAMP_NAMED)
        self.assertAlmostEqual(sum(own.values()), 1.0, places=9)
        self.assertIn(SENTINEL, own)

    def test_no_infinite_leverage(self):
        # Every named candidate (incl. France with 0 picks) gets a non-zero floor -> finite leverage.
        own = laplace_ownership_with_residual(CHAMP_COUNTS, n_opp=19, alpha=1.0, candidate_names=CHAMP_NAMED)
        p_full, _, _ = market_p_true("champion", top_n=6)
        for c in CHAMP_NAMED:
            self.assertGreater(own[c], 0.0, f"{c} has zero ownership -> infinite leverage")
            self.assertTrue((p_full[c] / own[c]) < float("inf"))
        self.assertGreater(own["France"], 0.0)                     # France: 0 picks but floored

    def test_hand_check_champion(self):
        own = laplace_ownership_with_residual(CHAMP_COUNTS, n_opp=19, alpha=1.0, candidate_names=CHAMP_NAMED)
        self.assertAlmostEqual(own["Brazil"], 3 / 26, places=12)   # (2+1)/(19+7)
        self.assertAlmostEqual(own["Spain"], 3 / 26, places=12)
        self.assertAlmostEqual(own["France"], 1 / 26, places=12)   # (0+1)/(19+7)
        self.assertAlmostEqual(own[SENTINEL], 12 / 26, places=12)  # 12 blanks

    def test_n_opp_must_be_positive(self):
        with self.assertRaises(AssertionError):
            laplace_ownership(CHAMP_COUNTS, n_opp=0, candidate_names=CHAMP_NAMED)
        with self.assertRaises(AssertionError):
            laplace_ownership(CHAMP_COUNTS, n_opp=-1, candidate_names=CHAMP_NAMED)

    def test_model_b_sums_to_one_no_sentinel(self):
        # P2-a: blank mass redistributed over named P_true (renormalized over named); no blank SENTINEL.
        named_shares = laplace_ownership(CHAMP_COUNTS, n_opp=19, alpha=1.0, candidate_names=CHAMP_NAMED)
        p_full, _, _ = market_p_true("champion", top_n=6)
        own_b = blanks_chalk_resolved(named_shares, blank_mass=12 / 26, p_true=p_full)
        self.assertNotIn(SENTINEL, own_b)
        self.assertAlmostEqual(sum(own_b.values()), 1.0, places=9)


class TestSentinelGate(unittest.TestCase):
    def test_sentinel_present_in_real_rules(self):
        self.assertTrue(ownership_model_declared())                # memory/rules.md has the block

    def test_absent_sentinel_raises(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("# no sentinel here\n")
            tmp = f.name
        try:
            self.assertFalse(ownership_model_declared(tmp))
            with self.assertRaises(RuntimeError):
                _assert_ownership_model_declared(tmp)
        finally:
            os.unlink(tmp)

    def test_sentinel_constant_matches_engine(self):
        # L14: no split convention -> ingest SENTINEL must equal the engine's _SENTINEL.
        self.assertEqual(SENTINEL, _SENTINEL)


class TestObservedLoadRoundtrip(unittest.TestCase):
    def setUp(self):
        self.bk = {aw: set(market_p_true(aw, top_n=6)[0]) for aw in AWARDS}
        self.loaded = load_observed_from_snapshot(SNAP, board_keys=self.bk)

    def test_n_opp_and_levers(self):
        self.assertEqual(self.loaded["n_opp"], 19)
        for aw in AWARDS:
            self.assertIn(aw, self.loaded["levers"])
            self.assertEqual(self.loaded["levers"][aw]["n_opp"], 19)
        self.assertTrue(self.loaded["levers"]["assister"]["advisory"])

    def test_all_engine_picks_resolve(self):
        for aw in AWARDS:
            self.assertEqual(self.loaded["levers"][aw]["offboard_counts"], {},
                             f"{aw}: observed pick fell off-board this run (expected offboard=0)")

    def test_counts_match_snapshot_sebas_excluded(self):
        self.assertEqual(self.loaded["levers"]["champion"]["resolved_counts"], CHAMP_COUNTS)
        self.assertEqual(self.loaded["levers"]["champion"]["deciders"], 7)
        self.assertEqual(self.loaded["levers"]["champion"]["blanks"], 12)

    def test_p2b_offboard_folds_without_raise(self):
        # Strip 'Uruguay' from the champion board -> it must FOLD (blank-equiv), not raise.
        bk = {aw: set(self.bk[aw]) for aw in AWARDS}
        bk["champion"].discard("Uruguay")
        loaded = load_observed_from_snapshot(SNAP, board_keys=bk)
        self.assertIn("Uruguay", loaded["levers"]["champion"]["offboard_counts"])
        self.assertNotIn("Uruguay", loaded["levers"]["champion"]["resolved_counts"])

    def test_malformed_token_raises(self):
        snap = json.load(open(SNAP, encoding="utf-8"))
        snap["levers"]["champion"]["raw_counts"] = {"": 1, "Spain": 2}   # empty token = malformed
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(snap, f)
            tmp = f.name
        try:
            with self.assertRaises(ValueError):
                load_observed_from_snapshot(tmp, board_keys=self.bk)
        finally:
            os.unlink(tmp)


class TestObservedEngine(unittest.TestCase):
    def setUp(self):
        from pool.run_podium_draft import _build_observed_all, _recommend_observed
        self._build = _build_observed_all
        self._recommend = _recommend_observed
        bk = {aw: set(market_p_true(aw, top_n=6)[0]) for aw in AWARDS}
        self.builds = _build_observed_all(load_observed_from_snapshot(SNAP, board_keys=bk))

    def test_both_models_run(self):
        ra = self._recommend(self.builds, 13.7782, "A")["recommendation"]
        rb = self._recommend(self.builds, 13.7782, "B")["recommendation"]
        self.assertEqual(len(ra["recommended"]), 4)                # K=4
        self.assertEqual(len(rb["recommended"]), 4)
        for r in (ra, rb):
            self.assertIn(r["verdict"], {"chalk"} | {f"contrarian_{n}_levers" for n in range(1, 5)})

    def test_sentinel_never_a_winner(self):
        # T* is drawn from each lever's p_true; SENTINEL is not a p_true key -> can never win.
        for b in self.builds:
            self.assertNotIn(SENTINEL, b["lever"]["p_true"])

    def test_ownership_dicts_sum_to_one(self):
        for b in self.builds:
            self.assertAlmostEqual(sum(b["own_a"].values()), 1.0, places=9)
            self.assertAlmostEqual(sum(b["own_b"].values()), 1.0, places=9)
            self.assertNotIn(SENTINEL, b["own_b"])                 # offboard=0 this run -> no SENTINEL in B


class TestLockRunSnapshot(unittest.TestCase):
    """Jun-10 LOCK-RUN snapshot (N_opp=24). Guarded: SKIPS until Step 4 writes the snapshot, then asserts
    n_opp=24 ingestion + the Laplace floor (sums to 1, finite leverage incl. the 0-pick England/Argentina
    champion contrarians). The Jun-6 snapshot + N_opp=19 constants/tests are untouched."""
    SNAP_LOCK = os.path.join(ROOT, "data", "snapshots", "observed_ownership_2026-06-10.json")

    def setUp(self):
        if not os.path.exists(self.SNAP_LOCK):
            self.skipTest("observed_ownership_2026-06-10.json not yet written (Step 4)")
        self.bk = {aw: set(market_p_true(aw, top_n=6)[0]) for aw in AWARDS}
        self.loaded = load_observed_from_snapshot(self.SNAP_LOCK, board_keys=self.bk)

    def test_n_opp_24(self):
        snap = json.load(open(self.SNAP_LOCK, encoding="utf-8"))
        self.assertEqual(snap["n_opp"], 24)
        self.assertEqual(snap["n_total"], 25)
        self.assertEqual(self.loaded["n_opp"], 24)
        for aw in AWARDS:
            self.assertEqual(self.loaded["levers"][aw]["n_opp"], 24)

    def test_laplace_floor_sums_to_one_and_finite(self):
        # Mirrors pool/run_podium_draft._build_observed_all: named set = top-6 UNION observed.
        for aw in AWARDS:
            lv = self.loaded["levers"][aw]
            top = market_p_true(aw, top_n=6)[1]
            named = sorted(set(top) | set(lv["resolved_counts"]))
            own = laplace_ownership_with_residual(lv["resolved_counts"], 24, 1.0, named)
            self.assertAlmostEqual(sum(own.values()), 1.0, places=9)
            for c in named:
                self.assertGreater(own[c], 0.0, f"{aw}/{c}: zero ownership -> infinite leverage")

    def test_champion_england_argentina_zero_owned_but_floored(self):
        lv = self.loaded["levers"]["champion"]
        top = market_p_true("champion", top_n=6)[1]
        named = sorted(set(top) | set(lv["resolved_counts"]))
        own = laplace_ownership_with_residual(lv["resolved_counts"], 24, 1.0, named)
        for team in ("England", "Argentina"):
            self.assertNotIn(team, lv["resolved_counts"], f"{team} unexpectedly owned (lock-run = 0 owners)")
            self.assertGreater(own.get(team, 0.0), 0.0, f"{team} not floored -> infinite leverage")


if __name__ == "__main__":
    unittest.main(verbosity=2)
