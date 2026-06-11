"""podium_montecarlo.py - JOINT K-lever E[prize] engine for the 5 locked picks (PODIUM-1).

Generalizes the FROZEN A2 engine (`pool/pool_montecarlo.py`) from ONE categorical lever (champion) to K
JOINT levers (champion + the award picks). Each lever is a categorical winner T*_k ~ Categorical(P_true_k)
plus a 10-pt bonus that fires on label-equality. A player's score is the JOINT total:

    total = base ~ Normal(0, BASE_SIGMA)  +  Sum_k  bonus_k * [pick_k == T*_k]
    rank  = 1 + #{opponent total > my total}    (strict >; continuous noise => unique rank)
    E[prize | portfolio] = mean( PRIZES.get(rank, 0) )

E[prize] is a function of the rank of the TOTAL and is NON-ADDITIVE across picks: optimize the JOINT E[prize]
over candidate PORTFOLIOS, NEVER the sum of per-award E[prize], NEVER P(pick correct). Running A2 five times
and summing/arg-maxing per-award is BANNED (PODIUM-1; misses joint separation -> MASTER §7b portfolio rule).

A2 IS FROZEN and never edited. This module reproduces it BYTE-EXACT at K=1: the constants are IMPORTED from A2
(identical float literals) and the RNG draw order at K=1 collapses to A2's exact stream
    choice(T*) -> normal(my_noise) -> [per group: choice(picks) -> normal(noise)]
because (i) the winner loop runs once, (ii) my_noise is one shared draw, (iii) the group loop is OUTER and
draws K pick-columns then ONE shared noise block per group (one base noise per opponent, not per lever), and
(iv) a group is skipped (before any draw) iff count<=0 or all levers' ownership is empty - matching A2's
`count<=0 or not ownership`. See tests/test_podium_montecarlo.py::TestPodiumAnchor (T-anchor).

Independent levers is a documented stylization (champion<->award correlation not modeled, §2.6/PA7).
HARD GATE: this engine RECOMMENDS; it NEVER LOCKS. Not decision-grade until Track-B P4 σ-calibration.
Pure stdlib + numpy.
"""
from __future__ import annotations

import os
import sys
from itertools import combinations

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import (do NOT redefine) A2's constants -> identical float literals are required for byte-exactness.
from pool.pool_montecarlo import (  # noqa: E402
    DEFAULT_SEED, DEFAULT_N_SIMS, BASE_SIGMA, CHAMP_BONUS, PRIZES,
)
from pool.leverage import LEVERAGE_THRESHOLD, MIN_PTRUE_FOR_CONTRARIAN  # noqa: E402

DEFAULT_BONUS = CHAMP_BONUS       # 10.0 pts per locked pick (memory/rules.md).
_SENTINEL = "__unknown__"         # a lever's opponents with no ownership pick this -> never matches a winner.


def expected_prizes_joint(levers, opponent_groups, portfolios, *,
                          n_sims: int = DEFAULT_N_SIMS, sigma: float = BASE_SIGMA,
                          seed: int = DEFAULT_SEED, return_sim_vectors: bool = False) -> dict:
    """JOINT E[prize] per candidate-portfolio under Common Random Numbers.

    levers:           list of K dicts {name, p_true:{label:prob}, bonus:float}; p_true normalized internally.
    opponent_groups:  list of (count:int, [ownership_k for k in range(K)]); ownership_k = {label:share} for
                      lever k among that group's `count` opponents. A group is skipped (no RNG drawn) iff
                      count<=0 or ALL levers' ownership are empty. A lever with empty ownership inside a kept
                      group has its opponents pick a non-matching sentinel (0 bonus) but the group's single
                      shared base-noise draw still happens.
    portfolios:       iterable of K-tuples (one candidate label per lever), all evaluated on the SAME draw.
    return_sim_vectors: if True, each result also carries "_sim_prize" = the raw (n_sims,) per-sim prize
                      array. CRN means these arrays are PAIRABLE across portfolios -> a paired SE of the
                      prize DIFFERENCE (std(prize_i - prize_chalk)/sqrt(n)) for the lock-run 2*SE_diff gate.
                      The arrays are read AFTER every RNG draw, so this flag has ZERO effect on the draw
                      stream or on any existing return value (the byte-exact K=1 anchor is unaffected).

    Returns {portfolio_tuple: {"E_prize", "p_first", "mean_rank", "p_all_correct"[, "_sim_prize"]}}.
    """
    K = len(levers)
    rng = np.random.default_rng(seed)

    # --- 1) true winner per lever (CRN: each drawn once, in lever order). At K=1 this is A2's T_star draw. ---
    T_star = []
    for lev in levers:
        labels = np.array(list(lev["p_true"].keys()))
        p = np.array(list(lev["p_true"].values()), dtype=float)
        p = p / p.sum()
        T_star.append(labels[rng.choice(len(labels), size=n_sims, p=p)])

    # --- 2) my base noise (shared across all portfolios). At K=1 this is A2's my_noise draw. ---
    my_noise = rng.normal(0.0, sigma, size=n_sims)

    # --- 3) opponents: per kept group, draw K pick-columns (lever order) THEN one shared noise block. ---
    pick_cols = [[] for _ in range(K)]
    noise_cols = []
    for count, lever_ownerships in opponent_groups:
        if count <= 0 or not any(lever_ownerships):       # skip BEFORE any draw (matches A2's skip)
            continue
        for k in range(K):
            own = lever_ownerships[k] if k < len(lever_ownerships) else None
            if not own:
                pick_cols[k].append(np.full((n_sims, count), _SENTINEL))     # no RNG; never matches a winner
            else:
                labels = np.array(list(own.keys()))
                probs = np.array(list(own.values()), dtype=float)
                probs = probs / probs.sum()
                pick_cols[k].append(labels[rng.choice(len(labels), size=(n_sims, count), p=probs)])
        noise_cols.append(rng.normal(0.0, sigma, size=(n_sims, count)))       # ONE base noise per opponent

    if noise_cols:
        opp_noise = np.concatenate(noise_cols, axis=1)                        # (n_sims, N_opp)
        opp_picks = [np.concatenate(pick_cols[k], axis=1) for k in range(K)]  # each (n_sims, N_opp)
    else:
        opp_noise = np.empty((n_sims, 0))
        opp_picks = [np.empty((n_sims, 0), dtype=T_star[k].dtype) for k in range(K)]

    # opponents' totals are SHARED across portfolios (core of CRN); accumulate levers in list order.
    opp_total = opp_noise
    for k in range(K):
        opp_total = opp_total + levers[k]["bonus"] * (opp_picks[k] == T_star[k][:, None])

    out = {}
    for portfolio in portfolios:
        portfolio = tuple(portfolio)
        my_total = my_noise
        all_correct = np.ones(n_sims, dtype=bool)
        for k in range(K):
            match_k = (T_star[k] == portfolio[k])
            my_total = my_total + levers[k]["bonus"] * match_k
            all_correct = all_correct & match_k
        beats = (opp_total > my_total[:, None]).sum(axis=1)     # strict > => unique rank
        rank = 1 + beats
        prize = np.where(rank == 1, PRIZES[1],
                np.where(rank == 2, PRIZES[2],
                np.where(rank == 3, PRIZES[3], 0.0)))
        out[portfolio] = {"E_prize": float(prize.mean()),
                          "p_first": float((rank == 1).mean()),
                          "mean_rank": float(rank.mean()),
                          "p_all_correct": float(all_correct.mean())}
        if return_sim_vectors:                       # post-draw read: no effect on RNG or existing values
            out[portfolio]["_sim_prize"] = prize
    return out


def expected_prizes_k1(p_true: dict, candidates, opponent_groups, *,
                       n_sims: int = DEFAULT_N_SIMS, sigma: float = BASE_SIGMA,
                       seed: int = DEFAULT_SEED) -> dict:
    """K=1 shim (one champion lever). Reproduces `pool_montecarlo.expected_prizes` BYTE-EXACT.

    Maps A2-shape inputs `opponent_groups=[(count, ownership), ...]` to the joint shape and returns A2's
    `{cand: {E_prize, p_first, p_pick_ok, mean_rank}}` (p_pick_ok := p_all_correct at K=1).
    """
    lever = {"name": "champion", "p_true": p_true, "bonus": CHAMP_BONUS}
    joint_groups = [(count, [ownership]) for count, ownership in opponent_groups]
    raw = expected_prizes_joint([lever], joint_groups, [(c,) for c in candidates],
                                n_sims=n_sims, sigma=sigma, seed=seed)
    return {c: {"E_prize": raw[(c,)]["E_prize"],
                "p_first": raw[(c,)]["p_first"],
                "p_pick_ok": raw[(c,)]["p_all_correct"],
                "mean_rank": raw[(c,)]["mean_rank"]} for c in candidates}


def _aggregate_ownership(opponent_groups, k):
    """Count-weighted field ownership for lever k across groups (for leverage). Each group's dict is
    normalized first, then weighted by its opponent count."""
    agg, total = {}, 0
    for count, lever_ownerships in opponent_groups:
        if count <= 0:
            continue
        own = lever_ownerships[k] if k < len(lever_ownerships) else None
        if not own:
            continue
        s = sum(own.values())
        for label, v in own.items():
            agg[label] = agg.get(label, 0.0) + count * (v / s)
        total += count
    return {label: v / total for label, v in agg.items()} if total else {}


def _classify(lever, candidates, ownership):
    """chalk = highest-P_true candidate. contrarian = the highest-leverage candidate (leverage =
    P_true/ownership) clearing LEVERAGE_THRESHOLD and MIN_PTRUE_FOR_CONTRARIAN, else None."""
    p_true = lever["p_true"]
    chalk = max(candidates, key=lambda c: p_true.get(c, 0.0))
    contrarian, best = None, LEVERAGE_THRESHOLD
    for c in candidates:
        if c == chalk:
            continue
        pt = p_true.get(c, 0.0)
        if pt < MIN_PTRUE_FOR_CONTRARIAN:
            continue
        own = ownership.get(c, 0.0)
        lev = float("inf") if own <= 0 else pt / own
        if lev > best:
            best, contrarian = lev, c
    return chalk, contrarian


def recommend_portfolio_joint(levers, opponent_groups, candidates_per_lever, *,
                              n_sims: int = DEFAULT_N_SIMS, sigma: float = BASE_SIGMA,
                              seed: int = DEFAULT_SEED, return_sim_vectors: bool = False) -> dict:
    """Bounded-enumeration recommendation under the §7b portfolio rule. RECOMMENDATION ONLY (never a lock).

    Enumerates: all-chalk + each single-lever-contrarian flip + each pairwise flip. §7b (numerical): recommend
    all-chalk unless one flip strictly increases joint E[prize]; adopt a SECOND contrarian flip only if it
    strictly beats the best single flip. Returns the per-portfolio table + the recommendation block.
    return_sim_vectors threads to expected_prizes_joint so the lock-run can compute paired SE_diff over the
    enumerated portfolios (the chalk reference is recommendation["chalk_portfolio"]).
    """
    K = len(levers)
    chalk, contrarian = [], []
    for k in range(K):
        own_k = _aggregate_ownership(opponent_groups, k)
        ch, co = _classify(levers[k], candidates_per_lever[k], own_k)
        chalk.append(ch)
        contrarian.append(co)
    chalk_pf = tuple(chalk)

    portfolios = {chalk_pf}
    single = {}
    for k in range(K):
        if contrarian[k] is not None:
            pf = tuple(contrarian[k] if i == k else chalk[i] for i in range(K))
            portfolios.add(pf)
            single[k] = pf
    double = {}
    for k, j in combinations(range(K), 2):
        if contrarian[k] is not None and contrarian[j] is not None:
            pf = tuple(contrarian[i] if i in (k, j) else chalk[i] for i in range(K))
            portfolios.add(pf)
            double[(k, j)] = pf

    table = expected_prizes_joint(levers, opponent_groups, list(portfolios),
                                  n_sims=n_sims, sigma=sigma, seed=seed,
                                  return_sim_vectors=return_sim_vectors)

    e_chalk = table[chalk_pf]["E_prize"]
    best_single_pf, best_single_ev = None, e_chalk
    for pf in single.values():
        if table[pf]["E_prize"] > best_single_ev:        # must strictly beat all-chalk
            best_single_ev, best_single_pf = table[pf]["E_prize"], pf

    if best_single_pf is None:
        recommended = chalk_pf
    else:
        best_double_pf, best_double_ev = None, best_single_ev
        for pf in double.values():
            if table[pf]["E_prize"] > best_double_ev:     # must STRICTLY beat the best single flip
                best_double_ev, best_double_pf = table[pf]["E_prize"], pf
        recommended = best_double_pf if best_double_pf is not None else best_single_pf

    n_contra = sum(1 for i in range(K) if recommended[i] != chalk_pf[i])
    verdict = "chalk" if n_contra == 0 else f"contrarian_{n_contra}_levers"
    lever_verdicts = [{"lever": levers[k]["name"], "chalk": chalk[k],
                       "contrarian": contrarian[k], "chosen": recommended[k]} for k in range(K)]
    return {"portfolios": table,
            "recommendation": {"recommended": recommended, "verdict": verdict,
                               "chalk_portfolio": chalk_pf, "lever_verdicts": lever_verdicts,
                               "e_prize_chalk": e_chalk,
                               "e_prize_recommended": table[recommended]["E_prize"],
                               "improvement": table[recommended]["E_prize"] - e_chalk}}


# --------------------------------------------------------------------------------------------------
# SELFTEST: K=1 byte-exact anchor vs A2 + chalk/flip recommendation (engine-logic, NOT a pick).
# --------------------------------------------------------------------------------------------------
def _selftest(sigma: float = BASE_SIGMA, seed: int = DEFAULT_SEED, n_sims: int = DEFAULT_N_SIMS):
    from pool.pool_montecarlo import expected_prizes
    P = {"Fav": 0.40, "Mid": 0.25, "Dark": 0.20, "Rest": 0.15}
    cands = ["Fav", "Mid", "Dark"]
    groups_a2 = [(3, {"Fav": 1.0}), (8, {"Fav": 0.5, "Mid": 0.35, "Dark": 0.025, "Rest": 0.125})]

    a2 = expected_prizes(P, cands, groups_a2, n_sims=n_sims, sigma=sigma, seed=seed)
    new = expected_prizes_k1(P, cands, groups_a2, n_sims=n_sims, sigma=sigma, seed=seed)
    exact = all(a2[c][f] == new[c][f] for c in cands for f in ("E_prize", "p_first", "mean_rank"))
    print("=" * 78)
    print(f"podium_montecarlo SELFTEST  seed={seed} sigma={sigma} n_sims={n_sims}")
    print(f"  (1) K=1 two-group anchor reproduces A2 byte-exact: {exact}")
    for c in cands:
        print(f"      {c:<5} A2 E={a2[c]['E_prize']:.6f}  new E={new[c]['E_prize']:.6f}")
    assert exact, "K=1 anchor does NOT reproduce A2 byte-exact"

    eff = [{"name": "champion", "p_true": P, "bonus": CHAMP_BONUS},
           {"name": "scorer", "p_true": P, "bonus": CHAMP_BONUS}]
    rc = recommend_portfolio_joint(eff, [(11, [dict(P), dict(P)])], [cands, cands],
                                   n_sims=n_sims, sigma=sigma, seed=seed)["recommendation"]
    # flip case: lever-1 is a no-op (single candidate, everyone picks it -> cancels in rank) so the lever-0
    # contrarian flip is decisive. With several LIVE efficient levers the joint dilution can correctly
    # suppress a lone flip (§7b) -- that is the engine working, not a bug.
    flip = [{"name": "champion", "p_true": P, "bonus": CHAMP_BONUS},
            {"name": "scorer", "p_true": {"Solo": 1.0}, "bonus": CHAMP_BONUS}]
    rf = recommend_portfolio_joint(flip, [(11, [{"Fav": 0.60, "Mid": 0.33, "Dark": 0.02, "Rest": 0.05},
                                                {"Solo": 1.0}])], [cands, ["Solo"]],
                                   n_sims=n_sims, sigma=sigma, seed=seed)["recommendation"]
    print(f"  (2) efficient field  -> {rc['recommended']} [{rc['verdict']}]  (expect all-chalk)")
    print(f"  (3) lever-0 starved  -> {rf['recommended']} [{rf['verdict']}]  (expect Dark on lever-0)")
    assert rc["verdict"] == "chalk", f"(2) expected chalk, got {rc}"
    assert rf["recommended"][0] == "Dark" and rf["verdict"] == "contrarian_1_levers", f"(3) got {rf}"
    print("SELFTEST: PASS  (1) byte-exact K=1  (2) chalk  (3) flip-one")
    print("=" * 78)
    return exact, rc["verdict"], rf["recommended"]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _selftest()


if __name__ == "__main__":
    main()
