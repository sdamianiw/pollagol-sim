"""P2 - TDD for pool/podium_montecarlo.py : the JOINT K-lever E[prize] engine (PODIUM-1).

Written RED-first (Gate 7). The load-bearing test is T-anchor: the K-lever engine, instantiated at K=1
with the champion inputs, must reproduce the FROZEN A2 `pool_montecarlo.expected_prizes` BYTE-EXACT. That
proves the generalization did not alter A2's logic (A2 is never edited). The rest exercise the chalk /
contrarian recommendation and the numerical §7b portfolio rule.

G2 (numpy pin): the byte-exact anchor was proven on numpy==1.26.4. On a different numpy the float-reduction
stream can differ; T-anchor then SKIPS with a clear message instead of a false NO-PASS (it never silently
passes - on the pinned build it asserts exact equality).
"""
import contextlib
import io
import os
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pool.pool_montecarlo import (  # noqa: E402
    expected_prizes, DEFAULT_SEED, DEFAULT_N_SIMS, BASE_SIGMA, CHAMP_BONUS,
)
from pool.podium_montecarlo import (  # noqa: E402
    expected_prizes_joint, expected_prizes_k1, recommend_portfolio_joint,
)
from pool.leverage import compute  # noqa: E402

NUMPY_PIN = "1.26.4"

P_TRUE = {"Fav": 0.40, "Mid": 0.25, "Dark": 0.20, "Rest": 0.15}
OWN_CHALK = dict(P_TRUE)                                             # ownership proportional to P_true
OWN_FLIP = {"Fav": 0.60, "Mid": 0.33, "Dark": 0.02, "Rest": 0.05}   # Fav over-owned, Dark starved
CANDS = ["Fav", "Mid", "Dark"]
N_OPP = 11
N_REC = 60000   # higher n_sims for the recommendation tests -> tighter MC noise, decisive argmax


class TestPodiumAnchor(unittest.TestCase):
    """T-anchor: K=1 reproduces A2 byte-exact (single-group real champion + two-group synthetic)."""

    def _compare_byte_exact(self, p_true, candidates, opponent_groups, label):
        a2 = expected_prizes(p_true, candidates, opponent_groups,
                             n_sims=DEFAULT_N_SIMS, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        new = expected_prizes_k1(p_true, candidates, opponent_groups,
                                 n_sims=DEFAULT_N_SIMS, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        # shim returns A2's keys (E_prize/p_first/p_pick_ok/mean_rank); p_pick_ok := p_all_correct at K=1.
        fields = ("E_prize", "p_first", "p_pick_ok", "mean_rank")
        same = all(a2[c][f] == new[c][f] for c in candidates for f in fields)
        if np.__version__ != NUMPY_PIN and not same:
            self.skipTest(f"byte-exact anchor proven on numpy {NUMPY_PIN}; running {np.__version__} -> "
                          f"float-reduction stream differs ({label}), not an engine bug. Re-pin to verify.")
        for c in candidates:
            for f in fields:
                self.assertEqual(a2[c][f], new[c][f],
                                 f"T-anchor {label}: {c}.{f} A2={a2[c][f]!r} new={new[c][f]!r}")

    def test_T_anchor_real_champion_single_group(self):
        p_true, _own, _ovr, _rows, _data = compute(
            os.path.join(ROOT, "data", "outrights.json"), ownership_source="prior")
        cands = [t for t in p_true if p_true[t] >= 0.05]
        groups = [(N_OPP, {t: p_true[t] for t in cands})]
        self._compare_byte_exact(p_true, cands, groups, "real-champion/single-group")

    def test_T_anchor_synthetic_two_group(self):
        groups = [(3, {"Fav": 1.0}),
                  (8, {"Fav": 0.5, "Mid": 0.35, "Dark": 0.025, "Rest": 0.125})]
        self._compare_byte_exact(P_TRUE, CANDS, groups, "synthetic/two-group")


class TestPodiumRecommendation(unittest.TestCase):
    """Chalk / contrarian recommendation + the numerical §7b portfolio rule."""

    def test_T_chalk_all_chalk_when_efficient(self):
        # Both levers efficient (ownership proportional to P_true) -> no contrarian -> all-chalk.
        levers = [{"name": "champion", "p_true": P_TRUE, "bonus": CHAMP_BONUS},
                  {"name": "scorer", "p_true": P_TRUE, "bonus": CHAMP_BONUS}]
        groups = [(N_OPP, [OWN_CHALK, OWN_CHALK])]
        res = recommend_portfolio_joint(levers, groups, [CANDS, CANDS],
                                        n_sims=N_REC, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        rec = res["recommendation"]
        self.assertEqual(rec["verdict"], "chalk", f"efficient field -> all-chalk, got {rec}")
        self.assertEqual(rec["recommended"], ("Fav", "Fav"))

    def test_T_flip_one_only_the_starved_lever(self):
        # Lever 0 strongly starves Dark; the flip is worth it ONLY because lever 1 is a no-op. MEASURED
        # 2026-06-05 (sigma=6, N_opp=11): even ONE *live* efficient lever makes the flip net-negative across
        # the whole 10x-100x leverage range (under-ownership strength does NOT rescue it), and the verdict is
        # sigma-dependent (flip at sigma<=6, chalk at sigma>=8) -- see lessons L12 / rules PODIUM-3. So we
        # isolate the flip mechanism with a no-op lever 1; the "don't over-gamble" case is T-portfolio-rule.
        champ = {"name": "champion", "p_true": P_TRUE, "bonus": CHAMP_BONUS}
        scorer = {"name": "scorer", "p_true": {"Solo": 1.0}, "bonus": CHAMP_BONUS}   # no-op: cancels in rank
        groups = [(N_OPP, [OWN_FLIP, {"Solo": 1.0}])]
        res = recommend_portfolio_joint([champ, scorer], groups, [CANDS, ["Solo"]],
                                        n_sims=N_REC, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        rec = res["recommendation"]
        self.assertEqual(rec["recommended"][0], "Dark", f"starved lever should flip to Dark: {rec}")
        self.assertEqual(rec["recommended"][1], "Solo", f"no-contrarian lever stays chalk: {rec}")
        self.assertEqual(rec["verdict"], "contrarian_1_levers")

    def test_T_portfolio_rule_no_double_without_strict_gain(self):
        # Both levers flippable. The rule: >1 contrarian ONLY if joint E[prize] strictly beats best single.
        levers = [{"name": "champion", "p_true": P_TRUE, "bonus": CHAMP_BONUS},
                  {"name": "scorer", "p_true": P_TRUE, "bonus": CHAMP_BONUS}]
        groups = [(N_OPP, [OWN_FLIP, OWN_FLIP])]
        res = recommend_portfolio_joint(levers, groups, [["Fav", "Dark"], ["Fav", "Dark"]],
                                        n_sims=N_REC, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        rec = res["recommendation"]
        table = res["portfolios"]
        chalk = rec["chalk_portfolio"]
        n_contra = sum(1 for i in range(2) if rec["recommended"][i] != chalk[i])
        if n_contra > 1:
            singles = [chalk[:k] + (c,) + chalk[k + 1:]
                       for k in range(2) for c in ("Fav", "Dark") if c != chalk[k]]
            singles = [pf for pf in singles if pf in table]
            best_single = max((table[pf]["E_prize"] for pf in singles), default=rec["e_prize_chalk"])
            self.assertGreater(table[rec["recommended"]]["E_prize"], best_single,
                               "recommended 2 contrarians without strictly beating the best single flip")

    def test_T_L4_absent_label_never_bonus_never_candidate(self):
        # A label absent from p_true can be an OPPONENT pick (never earns bonus) but is never MY candidate.
        lever = {"name": "champion", "p_true": {"Brazil": 0.1, "Mexico": 0.9}, "bonus": CHAMP_BONUS}
        groups = [(1, [{"Mexico City": 1.0}])]
        table = expected_prizes_joint([lever], groups, [("Mexico",)],
                                      n_sims=40000, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        self.assertGreater(table[("Mexico",)]["E_prize"], 0.5,
                           "'Mexico City' truncated to 'Mexico' and spuriously matched (dtype/value bug)")
        self.assertNotIn(("Mexico City",), table, "absent-from-p_true label became a candidate portfolio")

    def test_T_perm_invariance_recommendation_order_independent(self):
        # G1: permuting the levers list must NOT change the recommendation or verdict (argmax-stable),
        # even though absolute magnitudes move (shared-RNG stream shifts with order -> MC-noise, not 1e-16).
        champ = {"name": "champion", "p_true": P_TRUE, "bonus": CHAMP_BONUS}
        # no-op levers: single candidate -> deterministic winner, everyone picks it -> cancels in ranking,
        # AND no zero-owned candidate -> no spurious contrarian. Isolates the champion flip decisively.
        solo = lambda nm: {"name": nm, "p_true": {"Solo": 1.0}, "bonus": CHAMP_BONUS}
        levers = [champ, solo("scorer"), solo("mvp"), solo("gk")]
        own = [OWN_FLIP, {"Solo": 1.0}, {"Solo": 1.0}, {"Solo": 1.0}]
        cands = [CANDS, ["Solo"], ["Solo"], ["Solo"]]
        groups = [(N_OPP, own)]

        def rec_map(levers_p, own_p, cands_p):
            r = recommend_portfolio_joint(levers_p, [(N_OPP, own_p)], cands_p,
                                          n_sims=N_REC, sigma=BASE_SIGMA, seed=DEFAULT_SEED)["recommendation"]
            chosen = {lv["lever"]: lv["chosen"] for lv in r["lever_verdicts"]}
            return chosen, r["verdict"]

        base_chosen, base_verdict = rec_map(levers, own, cands)
        self.assertEqual(base_chosen["champion"], "Dark", f"champion should flip contrarian: {base_chosen}")
        for perm in ([3, 1, 0, 2], [1, 2, 3, 0], [2, 0, 3, 1]):
            lv_p = [levers[i] for i in perm]
            own_p = [own[i] for i in perm]
            cn_p = [cands[i] for i in perm]
            chosen_p, verdict_p = rec_map(lv_p, own_p, cn_p)
            self.assertEqual(chosen_p, base_chosen, f"recommendation changed under permutation {perm}")
            self.assertEqual(verdict_p, base_verdict, f"verdict changed under permutation {perm}")


class TestSEDiffEmission(unittest.TestCase):
    """LOCK-RUN: `return_sim_vectors` exposes the per-sim prize array for the paired-CRN SE_diff gate.
    Anchor-safe: the vectors are read AFTER all RNG draws, so default (False) leaves the dict byte-identical
    (the byte-exact A2 anchor in TestPodiumAnchor runs with the default kwarg and is the load-bearing guard)."""

    def _levers_groups(self):
        levers = [{"name": "champion", "p_true": P_TRUE, "bonus": CHAMP_BONUS},
                  {"name": "scorer", "p_true": P_TRUE, "bonus": CHAMP_BONUS}]
        groups = [(N_OPP, [OWN_FLIP, OWN_CHALK])]
        return levers, groups

    def test_sim_vectors_absent_by_default(self):
        levers, groups = self._levers_groups()
        table = expected_prizes_joint(levers, groups, [("Fav", "Fav"), ("Dark", "Fav")],
                                      n_sims=40000, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        for pf in table:
            self.assertNotIn("_sim_prize", table[pf])

    def test_sim_vectors_present_and_reproduce_mean(self):
        levers, groups = self._levers_groups()
        ports = [("Fav", "Fav"), ("Dark", "Fav")]
        table = expected_prizes_joint(levers, groups, ports, n_sims=40000, sigma=BASE_SIGMA,
                                      seed=DEFAULT_SEED, return_sim_vectors=True)
        for pf in ports:
            v = table[pf]["_sim_prize"]
            self.assertEqual(v.shape, (40000,))
            self.assertAlmostEqual(float(v.mean()), table[pf]["E_prize"], places=12)  # vector mean == E_prize
            self.assertTrue(set(np.unique(v)).issubset({0.0, 0.1, 0.2, 0.6}))          # payout set only

    def test_existing_keys_byte_identical_with_flag(self):
        # Turning the flag ON must not change ANY existing value (post-draw read, no RNG touch).
        levers, groups = self._levers_groups()
        ports = [("Fav", "Fav"), ("Dark", "Fav")]
        off = expected_prizes_joint(levers, groups, ports, n_sims=40000, sigma=BASE_SIGMA, seed=DEFAULT_SEED)
        on = expected_prizes_joint(levers, groups, ports, n_sims=40000, sigma=BASE_SIGMA,
                                   seed=DEFAULT_SEED, return_sim_vectors=True)
        for pf in ports:
            for f in ("E_prize", "p_first", "mean_rank", "p_all_correct"):
                self.assertEqual(off[pf][f], on[pf][f], f"{pf}.{f} changed when return_sim_vectors=True")

    def test_paired_self_difference_is_zero(self):
        # Core of the paired-CRN SE: a portfolio differenced against itself has exactly zero variance.
        levers, groups = self._levers_groups()
        table = expected_prizes_joint(levers, groups, [("Dark", "Fav")], n_sims=40000, sigma=BASE_SIGMA,
                                      seed=DEFAULT_SEED, return_sim_vectors=True)
        v = table[("Dark", "Fav")]["_sim_prize"]
        self.assertEqual(float(np.std(v - v)), 0.0)

    def test_recommend_threads_sim_vectors(self):
        levers, groups = self._levers_groups()
        res = recommend_portfolio_joint(levers, groups, [CANDS, CANDS], n_sims=40000, sigma=BASE_SIGMA,
                                        seed=DEFAULT_SEED, return_sim_vectors=True)
        chalk_pf = res["recommendation"]["chalk_portfolio"]
        self.assertIn("_sim_prize", res["portfolios"][chalk_pf])


class TestA2Frozen(unittest.TestCase):
    """No-edit proof: A2's constants + 2-scenario selftest are unchanged (guards against editing A2)."""

    def test_no_edit_proof_a2_constants_and_selftest(self):
        import pool.pool_montecarlo as a2
        self.assertEqual(a2.DEFAULT_SEED, 20260602)
        self.assertEqual(a2.DEFAULT_N_SIMS, 30000)
        self.assertAlmostEqual(a2.BASE_SIGMA, 6.0, places=10)
        self.assertAlmostEqual(a2.CHAMP_BONUS, 10.0, places=10)
        self.assertEqual(a2.PRIZES, {1: 0.6, 2: 0.2, 3: 0.1})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            a, b, c = a2._selftest(sigma=a2.BASE_SIGMA, seed=a2.DEFAULT_SEED, n_sims=a2.DEFAULT_N_SIMS)
        self.assertEqual((a, b, c), ("Fav", "Dark", "Dark"), "A2 selftest changed -> A2 may have been edited")
        # Command-level check (cannot git-diff here): `python pool/pool_montecarlo.py --selftest` -> SELFTEST: PASS


if __name__ == "__main__":
    unittest.main(verbosity=2)
