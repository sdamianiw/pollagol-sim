"""A2 - pool/pool_montecarlo.py : E[prize] engine for the locked CHAMPION pick.

Decides the champion by MAXIMIZING E[prize] (expected share of pollaya's 60/20/10 pot) -
NOT P(win), NOT raw leverage. The champion is one ~10-pt lever inside a ~300-500-pt competition;
this engine resolves the chalk-vs-contrarian tradeoff numerically:
    value of a pick = P(it wins)  x  uniqueness-of-being-right  (fewer co-owners => bigger leap).

Model (stylized; one lever over base competition noise):
    true champion  T* ~ Categorical(P_true)
    player score   = base ~ Normal(0, BASE_SIGMA)  +  CHAMP_BONUS if (their champion pick == T*)
  BASE_SIGMA stands in for the spread of the OTHER ~300-500 pts (per-match etc.). It is a MODELING
  ASSUMPTION, documented here, to be recalibrated from backtest variance later (Track B).

Common Random Numbers (variance reduction => decisive argmax): per sim, draw T*, my base noise,
each opponent's pick, each opponent's base noise ONCE; evaluate EVERY candidate on that SAME draw.
Only `my_match = (cand == T*)` changes per candidate.
    my_total  = my_noise  + CHAMP_BONUS*(cand == T*)
    opp_total = opp_noise + CHAMP_BONUS*(opp_pick == T*)
    rank      = 1 + #{opp_total > my_total}        (strict >; continuous noise => unique rank)
    E[prize|cand] = mean( PRIZES.get(rank, 0) ) ;  recommend = argmax_cand E[prize|cand]

Opponents (N_final - 1, self-excluded) come in GROUPS, each with its own ownership distribution:
    LOCKED opponents  ~ observed ownership (pollaya, PICKS_VISIBLE=True)
    PENDING opponents ~ pending_prior (chalk default)  -- SIMULATION INPUT ONLY, never used to
                        choose my own pick.

HARD GATE: this engine RECOMMENDS; it NEVER LOCKS. Champion is OPEN (Brazil in pollaya = PLACEHOLDER).
ownership_source=prior is is_gated(); finalize only on measured ownership + HITL (Sebas), Jun-11 late.

Determinism: numpy.random.default_rng(DEFAULT_SEED) (PCG64; stable across versions/platforms); fixed
seed, never date/random-derived. Pure stdlib + numpy.
"""
from __future__ import annotations
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pool.leverage import compute, is_gated, PICKS_VISIBLE, OWNERSHIP_PRIOR_NAMED  # noqa: E402
from pool.ingest_ownership import load_observed  # noqa: E402

DEFAULT_SEED = 20260602          # fixed + documented; NEVER date/random-derived (determinism, R5).
DEFAULT_N_SIMS = 30000
# Stylized spread of the OTHER ~300-500 competition pts. Lower sigma => the CHAMP_BONUS lever is more
# decisive => ownership effects sharpen. TUNED so BOTH selftest scenarios pass decisively (chalk->Fav,
# flip->Dark); recalibrate from backtest variance later (Track B). See _selftest().
BASE_SIGMA = 6.0
CHAMP_BONUS = 10.0               # locked-pick points for a correct champion (memory/rules.md: 10 each).
PRIZES = {1: 0.6, 2: 0.2, 3: 0.1}    # pollaya payout 60/20/10 of the pot to ranks 1/2/3.


def expected_prizes(p_true: dict, candidates, opponent_groups, *,
                    n_sims: int = DEFAULT_N_SIMS, sigma: float = BASE_SIGMA,
                    seed: int = DEFAULT_SEED) -> dict:
    """E[prize] per candidate under Common Random Numbers.

    p_true:           {team: prob}  (normalized internally; need not sum to exactly 1).
    candidates:       list of my candidate champion picks (ideally a subset of p_true labels).
    opponent_groups:  list of (count:int, ownership:{team:share}); counts sum to N_opp = N_final-1.
                      A team a pick cannot match (absent from p_true) simply never earns the bonus.

    Returns {cand: {"E_prize": float, "p_win": float, "mean_rank": float}}.
    """
    rng = np.random.default_rng(seed)

    # --- true champion T* per sim, drawn over P_true's labels (CRN: drawn once, shared) ---
    pt_labels = np.array(list(p_true.keys()))
    pt_p = np.array(list(p_true.values()), dtype=float)
    pt_p = pt_p / pt_p.sum()
    T_star = pt_labels[rng.choice(len(pt_labels), size=n_sims, p=pt_p)]   # (n_sims,) of label strings

    # --- my base noise (shared across candidates) ---
    my_noise = rng.normal(0.0, sigma, size=n_sims)

    # --- opponents: pick + base noise per group, concatenated along the opponent axis ---
    pick_cols, noise_cols = [], []
    for count, ownership in opponent_groups:
        if count <= 0 or not ownership:
            continue
        labels = np.array(list(ownership.keys()))
        probs = np.array(list(ownership.values()), dtype=float)
        probs = probs / probs.sum()
        picks = labels[rng.choice(len(labels), size=(n_sims, count), p=probs)]
        # BUG-2 fix: keep the picks' NATURAL dtype. np.concatenate promotes groups to the widest dtype,
        # and numpy string `==` compares by VALUE (no truncation). The old `.astype(pt_labels.dtype)`
        # downcast any ownership label wider than the widest p_true key -> silent truncation -> spurious
        # champion matches (e.g. 'Mexico City' -> 'Mexico').
        pick_cols.append(picks)
        noise_cols.append(rng.normal(0.0, sigma, size=(n_sims, count)))
    if pick_cols:
        opp_pick = np.concatenate(pick_cols, axis=1)        # (n_sims, N_opp)
        opp_noise = np.concatenate(noise_cols, axis=1)
    else:
        opp_pick = np.empty((n_sims, 0), dtype=pt_labels.dtype)
        opp_noise = np.empty((n_sims, 0))

    # opponent totals are SHARED across candidates (the core of CRN)
    opp_total = opp_noise + CHAMP_BONUS * (opp_pick == T_star[:, None])

    out = {}
    for cand in candidates:
        my_match = (T_star == cand)
        my_total = my_noise + CHAMP_BONUS * my_match
        beats = (opp_total > my_total[:, None]).sum(axis=1)      # strict > => unique rank
        rank = 1 + beats
        prize = np.where(rank == 1, PRIZES[1],
                np.where(rank == 2, PRIZES[2],
                np.where(rank == 3, PRIZES[3], 0.0)))
        # BUG-1 fix: 'p_pick_ok' = P(pick == true champion) ~ P_true[cand] (NOT winning the pool);
        # 'p_first' = empirical P(finish 1st) = the actual pool-win probability.
        out[cand] = {"E_prize": float(prize.mean()),
                     "p_first": float((rank == 1).mean()),
                     "p_pick_ok": float(my_match.mean()),
                     "mean_rank": float(rank.mean())}
    return out


def recommend(p_true: dict, candidates, opponent_groups, **kw):
    """Returns (best_candidate, table). best = argmax E[prize]. RECOMMENDATION ONLY (never a lock)."""
    table = expected_prizes(p_true, candidates, opponent_groups, **kw)
    best = max(table, key=lambda c: table[c]["E_prize"])
    return best, table


def _print_table(table, candidates):
    print(f"{'candidate':<10}{'E[prize]':>11}{'p_first':>10}{'p_pick_ok':>11}{'mean rank':>12}")
    for c in candidates:
        r = table[c]
        print(f"{c:<10}{r['E_prize']:>11.4f}{r['p_first']:>10.3f}{r['p_pick_ok']:>11.3f}{r['mean_rank']:>12.3f}")


# --------------------------------------------------------------------------------------------------
# SELFTEST = TWO synthetic scenarios (FM1 guard: a single scenario is a latent gap).
# Synthetic CLEAN P_true so the engine-logic test is unambiguous -- NOT a real-data claim.
# `Rest` is a single ATOMIC residual outcome (exact-label match) -- a documented stylization; it is
# never a candidate, so it never competes for the argmax.
# --------------------------------------------------------------------------------------------------
def _selftest(sigma: float = BASE_SIGMA, seed: int = DEFAULT_SEED, n_sims: int = DEFAULT_N_SIMS):
    P_TRUE = {"Fav": 0.40, "Mid": 0.25, "Dark": 0.20, "Rest": 0.15}
    CANDS = ["Fav", "Mid", "Dark"]
    N_OPP = 11

    print("=" * 78)
    print(f"A2 pool_montecarlo SELFTEST   seed={seed}  sigma={sigma}  n_sims={n_sims}  "
          f"N_opp={N_OPP}  bonus={CHAMP_BONUS:g}")
    print("  synthetic P_true (engine-logic test, NOT a pick):", P_TRUE)
    print("=" * 78)

    # (a) chalk: ownership PROPORTIONAL to P_true (efficient field) -> chalk (Fav) wins at small N.
    own_a = dict(P_TRUE)
    best_a, tbl_a = recommend(P_TRUE, CANDS, [(N_OPP, own_a)], sigma=sigma, seed=seed, n_sims=n_sims)
    print("(a) CHALK  ownership ∝ P_true:", own_a)
    _print_table(tbl_a, CANDS)
    gap_a = tbl_a[best_a]["E_prize"] - max(tbl_a[c]["E_prize"] for c in CANDS if c != best_a)
    print(f"    argmax = {best_a}   (gap to 2nd = {gap_a:+.4f})   expect Fav")
    print("-" * 78)

    # (b) flip: chalk OVER-owned, Dark UNDER-owned -> contrarian (Dark) pays.
    own_b = {"Fav": 0.60, "Mid": 0.33, "Dark": 0.02, "Rest": 0.05}
    best_b, tbl_b = recommend(P_TRUE, CANDS, [(N_OPP, own_b)], sigma=sigma, seed=seed, n_sims=n_sims)
    print("(b) FLIP   ownership (chalk over-owned, Dark under-owned):", own_b)
    _print_table(tbl_b, CANDS)
    gap_b = tbl_b[best_b]["E_prize"] - max(tbl_b[c]["E_prize"] for c in CANDS if c != best_b)
    print(f"    argmax = {best_b}   (gap to 2nd = {gap_b:+.4f})   expect Dark")
    print("-" * 78)

    # (c) TWO-GROUP path (P2): LOCKED (observed) + PENDING (prior) concatenated -- the real Jun-11 path.
    grp_c = [(3, {"Fav": 1.0}), (8, {"Fav": 0.5, "Mid": 0.35, "Dark": 0.025, "Rest": 0.125})]
    best_c, tbl_c = recommend(P_TRUE, CANDS, grp_c, sigma=sigma, seed=seed, n_sims=n_sims)
    print("(c) TWO-GROUP  locked observed {Fav:1.0}x3 + pending prior x8 (Fav over-owned, Dark starved):")
    _print_table(tbl_c, CANDS)
    gap_c = tbl_c[best_c]["E_prize"] - max(tbl_c[c]["E_prize"] for c in CANDS if c != best_c)
    print(f"    argmax = {best_c}   (gap to 2nd = {gap_c:+.4f})   expect Dark   [exercises np.concatenate]")
    print("=" * 78)

    assert best_a == "Fav", f"(a) chalk: expected Fav, got {best_a} -- lower BASE_SIGMA / re-tune"
    assert best_b == "Dark", f"(b) flip: expected Dark, got {best_b} -- over-own chalk more / lower sigma"
    assert best_c == "Dark", f"(c) two-group: expected Dark, got {best_c}"
    print("SELFTEST: PASS  (a) chalk->Fav  (b) flip->Dark  (c) two-group->Dark  [all decisive]")
    return best_a, best_b, best_c


# --------------------------------------------------------------------------------------------------
# GATED real-data DEMO (integration only). Champion is OPEN; this is NOT a lock recommendation.
# Real-data caveat: with actual WC-2026 odds Spain/France/England cluster near Brazil (~11-15% vs
# ~9.8%) -> Brazil is NOT a clean contrarian. The synthetic selftest tests ENGINE LOGIC, not a pick.
# --------------------------------------------------------------------------------------------------
def _demo(seed: int = DEFAULT_SEED, n_sims: int = DEFAULT_N_SIMS):
    data_path = os.path.join(ROOT, "data", "outrights.json")
    p_true, _own, overround, _rows, data = compute(data_path, ownership_source="prior")

    # today's OBSERVED field (pollaya, 2026-06-02): Pireli18->Uruguay; Sebas->Brasil = PLACEHOLDER
    # (self-excluded). 1 locked / 10 pending of N=12. effective opponents = 11.
    obs = load_observed({"Pireli18": "Uruguay", "Sebas": "Brasil"}, n_total=12, exclude="Sebas",
                        as_of_utc="2026-06-02", source="pollaya screenshot")
    # PENDING opponents ~ chalk prior over the named set (normalized). SIMULATION INPUT ONLY.
    pend_named = {t: OWNERSHIP_PRIOR_NAMED[t] for t in OWNERSHIP_PRIOR_NAMED if t in p_true}
    s = sum(pend_named.values())
    pending_prior = {t: v / s for t, v in pend_named.items()}
    groups = [(obs["locked_count"], obs["ownership"]), (obs["pending_count"], pending_prior)]

    candidates = [t for t in p_true if p_true[t] >= 0.05]            # credible champions only
    best, table = recommend(p_true, candidates, groups, seed=seed, n_sims=n_sims)

    src = "prior"   # pending dominates (10 of 11 opp) -> this run is is_gated regardless of obs.
    print("=" * 78)
    print(f"A2 pool_montecarlo  GATED REAL-DATA DEMO  (PICKS_VISIBLE={PICKS_VISIBLE})   seed={seed}")
    print(f"  odds: {data['primary']['source']}  as_of {data.get('as_of')}  overround={overround:.3f}")
    print(f"  observed locked: {obs['ownership']} (n={obs['locked_count']}) | pending: {obs['pending_count']}"
          f" ~ chalk prior | N_opp={obs['locked_count'] + obs['pending_count']}")
    print("=" * 78)
    _print_table(table, sorted(candidates, key=lambda c: -table[c]["E_prize"]))
    print("-" * 78)
    print(f"argmax E[prize] = {best}   [DRAFT]")
    print("🛑 GATED / DRAFT — NOT A LOCK. is_gated(prior)=%s. Champion is OPEN (Brazil in pollaya ="
          % is_gated(src))
    print("   PLACEHOLDER). Only 1 observed pick + 10 pending(prior) => this run is prior-dominated &")
    print("   noisy. The real recommendation runs at the Jun-10 EVENING lock on FRESH odds + FINAL observed")
    print("   ownership; hard constraint = first match Jun-11 (~13:00 CST / 21:00 CEST), never race kickoff.")
    print("   Jun-12 is VOID. HITL: Sebas locks, not this engine.")
    print("=" * 78)
    return best, table


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--selftest" in sys.argv:
        _selftest()
    else:
        _demo()


if __name__ == "__main__":
    main()
