"""placement_mc.py - single-entry FIELD-DIFFERENTIATION E[prize] engine (BUILD-BUT-WAIT).

WHY (L27/L28 meta-lesson): two per-match probability levers (the draw-dial, the rho-fit) are both
E[pts]-inert -> the binding constraint on a top-3 finish is the OBJECTIVE, not probabilities. The only
remaining top-3 torque while TRAILING is to swap E[pts] -> P(top-3) by DIFFERENTIATING our scoreline on
the few near-even / dead-rubber MD3 boards (Clair-Letscher SINGLE-entry; NOT HVZ multi-entry portfolios).

WHAT this computes: for our single bracket, does picking a DECORRELATING scoreline (a plausible draw/upset,
NOT an inflated scoreline) instead of our EV pick on the first k of the candidate boards INCREASE E[prize]?
    objective = E[prize] = 0.6*P(1st) + 0.2*P(2nd) + 0.1*P(3rd)   (pollaya 60/20/10)
    reported per arm: P(1st), P(2nd), P(3rd), P(top-3) [HEADLINE], E[prize], mean_rank.

MODEL (mirrors the FROZEN A2 `pool_montecarlo.py` CRN/rank/prize PATTERN; A2 is champion-only so we do NOT
edit it - we IMPORT its constants and reimplement a per-match sibling):
    player final score = current_points  +  base ~ Normal(0, sigma_opp)  +  sum_b rubric(pick_b, result_b)
where the explicitly-modeled MD3 boards are a COMMON-MODE contribution (every opponent plays the field
modal -> zero cross-player spread on those cells), so the residual cross-player spread is carried entirely
by `base ~ N(0, sigma_opp)`. sigma_opp is the per-period cross-player points-GAIN dispersion measured in
PART 0 (`standings/player_panel_analysis.md`): sigma(g2) ~= 7.18 ~ BASE_SIGMA(6.0) (sanity-consistent).
CAVEAT: variance is RISING (sigma(g1)=3.53 -> sigma(g2)=7.18) so sigma(g2) may UNDERSTATE the MD3 residual
-> the gate sweeps +-25% and the absolute {6,8,13.78,19.5} anchors. (Do not read these figures as fixed
model constants; they are scenario inputs / PART-0 measurements, recomputed each matchday. I-3 holds: no
recorded result/standing writes a model parameter - everything here is an ARGUMENT.)

THREE pick-roles per board (distinct): `modal` = the field's most-probable-cell pick (what opponents
play); `us_baseline` = OUR actual control pick (default modal, but on a near-even board the EV-argmax pick
!= the modal-prob cell, so it is distinct); `decorrelating` = the contrarian draw/upset used in treatment.
=> Delta E measures decorrelating-vs-our-actual-pick, NOT vs the field modal.

LOCKED picks (champion + 4 awards, 10 pts each) are EXCLUDED: identical in both arms and already baked into
`current_points` -> they cancel EXACTLY in Delta E. The champion lottery is common-mode -> irrelevant.

Common Random Numbers: per sim draw player base-noise, each board's realized scoreline, and (optionally)
opponents' picks ONCE; evaluate BOTH arms (control = us_baseline everywhere; treatment = decorrelating on
the first k) on that SAME draw. Only our k picks differ -> k=0 => Delta E == 0.0 byte-exact (int rubric).

PODIUM TIE-BREAK (pollaya board footer): a points tie is resolved AD-HOC by the tied members (no
deterministic split / preset tiebreaker). This sim uses strict `>` for rank (`rank = 1 + #{opp > us}`),
so an exact tie favors us (optimistic); with continuous `base` noise exact ties are measure-zero -> the
convention only bites at an exact boundary tie -> negligible, documented.

BUILD != FIRE: default-OFF (imported by no live/cadence path), RECOMMENDS only, changes NO pick. The real
MD3 run is P4 (Jun-24, separate GO + a trailing-status read). Determinism: numpy default_rng(DEFAULT_SEED),
sorted player order, int64 board-point accumulation, re-normalized scoreline draws.
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import (do NOT redefine) A2's constants -> identical literals; never edit pool_montecarlo.py.
from pool.pool_montecarlo import DEFAULT_SEED, DEFAULT_N_SIMS, PRIZES  # noqa: E402
from pool.sigma_calibration import BOOT_SEED  # noqa: E402  (secondary cross-check seed)
from src.optimizer import points, PLAUSIBILITY_FLOOR  # noqa: E402  (LOCKED rubric - reuse, never reimplement)
from src.model import implied_1x2  # noqa: E402

MAX_GOALS = 9                                   # score matrices are 9x9 (src.model.score_matrix default)
COINFLIP_THRESHOLD = 0.08                       # |P_top - P_draw| < 0.08  (predictions/.../summary.md)
GATE_P_FIELD_MODAL = 0.85                       # adverse-corner field-deviation for the FIRE gate
DEFAULT_EPS_MIN = 0.02                          # effect-size floor: Delta P(top-3) >= +0.02 (HITL-set)
SIGMA_ABS_ANCHORS = (6.0, 8.0, 13.78, 19.5)     # secondary absolute sigma anchors (cross-check only)

# Precompute the LOCKED additive rubric as a lookup table -> fully vectorized, byte-identical to points().
_POINTS_TABLE = np.zeros((MAX_GOALS, MAX_GOALS, MAX_GOALS, MAX_GOALS), dtype=np.int8)
for _ph in range(MAX_GOALS):
    for _pa in range(MAX_GOALS):
        for _ah in range(MAX_GOALS):
            for _aa in range(MAX_GOALS):
                _POINTS_TABLE[_ph, _pa, _ah, _aa] = points((_ph, _pa), (_ah, _aa))


def is_coinflip(matrix: np.ndarray, threshold: float = COINFLIP_THRESHOLD) -> bool:
    """True iff this board is 'near-even': |P_top - P_draw| < threshold, P_top = max(P_home, P_away).

    Computed from the DC score matrix (reuses src.model.implied_1x2) BEFORE any prize sim, so the
    differentiable-board set is pre-registered from the odds (anti-selection-bias). Matches the published
    summary.md heuristic (threshold 0.08). dead-rubber (the other selection leg) is supplied as an ARGUMENT
    by the caller from the deterministic group table - NOT detected here (M5-independent build).
    """
    p = implied_1x2(matrix)
    p_top = max(p["home"], p["away"])
    return abs(p_top - p["draw"]) < threshold


def _cell(pick) -> int:
    return int(pick[0]) * MAX_GOALS + int(pick[1])


def _draw_results(boards, rng, n_sims):
    """Realized scoreline per board (CRN: shared across arms). Returns list of (r_home, r_away) int arrays."""
    out = []
    for b in boards:
        flat = np.asarray(b["matrix"], dtype=np.float64).flatten()
        s = flat.sum()
        if s <= 0:
            raise ValueError("board matrix has non-positive mass")
        flat = flat / s                                   # re-normalize guard (rng.choice needs sum==1)
        idx = rng.choice(flat.size, size=n_sims, p=flat)  # (n_sims,) flat cell index
        out.append((idx // MAX_GOALS, idx % MAX_GOALS))
    return out


def _plausible_nonmodal(matrix, modal_cell, floor):
    """Flat cell indices with P >= floor, excluding the modal cell (deviant opponents draw from these)."""
    flat = np.asarray(matrix, dtype=np.float64).flatten()
    pool = [c for c in range(flat.size) if flat[c] >= floor and c != modal_cell]
    return np.array(pool if pool else [modal_cell], dtype=np.int64)


def _validate(standings, us_id, boards, k):
    if us_id not in standings:
        raise ValueError(f"us_id {us_id!r} not in standings")
    if not all(isinstance(v, (int, float)) and v >= 0 for v in standings.values()):
        raise ValueError("standings values must be numeric and non-negative")
    if not (0 <= k <= len(boards)):
        raise ValueError(f"k must be in [0, {len(boards)}], got {k}")
    for b in boards:
        for key in ("matrix", "modal", "us_baseline", "decorrelating"):
            if key not in b:
                raise ValueError(f"board missing required key {key!r}")


def _arm_stats(rank):
    prize = np.where(rank == 1, PRIZES[1],
            np.where(rank == 2, PRIZES[2],
            np.where(rank == 3, PRIZES[3], 0.0)))
    return prize, {"E_prize": float(prize.mean()),
                   "P1": float((rank == 1).mean()),
                   "P2": float((rank == 2).mean()),
                   "P3": float((rank == 3).mean()),
                   "p_top3": float((rank <= 3).mean()),
                   "mean_rank": float(rank.mean())}


def expected_prizes_placement(standings, us_id, boards, k, *,
                              sigma_opp=None, n_sims: int = DEFAULT_N_SIMS,
                              seed: int = DEFAULT_SEED, p_field_modal: float = 1.0,
                              return_sim_vectors: bool = False) -> dict:
    """E[prize] for control (us_baseline everywhere) vs treatment (decorrelating on the first k boards).

    standings:     {player_id -> current points}; us identified by us_id. (Per-player panel latest col.)
    boards:        [{matrix:9x9, modal:(i,j), us_baseline:(i,j), decorrelating:(i,j)}] candidate boards.
    sigma_opp:     residual per-player base-noise std (PART-0 sigma(g2)). REQUIRED (no silent default - a
                   wrong sigma silently moves the verdict). p_field_modal<1 -> opponents deviate from modal.
    Returns {"control":{...}, "treatment":{...}, "delta_E_prize", "delta_p_top3"[, sim vectors]}.
    RECOMMENDATION ONLY - never a lock; default-OFF in the live path.
    """
    if sigma_opp is None:
        raise ValueError("sigma_opp is required (PART-0 measured sigma(g2)); pass it explicitly")
    _validate(standings, us_id, boards, k)
    rng = np.random.default_rng(seed)

    player_ids = sorted(standings.keys())                          # sorted (PYTHONHASHSEED-safe, L18)
    n_players = len(player_ids)
    us_col = player_ids.index(us_id)
    pts_vec = np.array([standings[p] for p in player_ids], dtype=np.float64)

    # (1) base noise for all players (one deterministic draw; columns = sorted player_ids)
    noise = rng.normal(0.0, sigma_opp, size=(n_sims, n_players))
    # (2) realized scorelines per board (shared across arms)
    results = _draw_results(boards, rng, n_sims)

    modal_cells = [_cell(b["modal"]) for b in boards]
    base_cells = [_cell(b["us_baseline"]) for b in boards]
    deco_cells = [_cell(b["decorrelating"]) for b in boards]

    # ---- US board points (int64; the ONLY thing that differs between arms) ----
    us_ctrl = np.zeros(n_sims, dtype=np.int64)
    us_trt = np.zeros(n_sims, dtype=np.int64)
    for b, (rh, ra) in enumerate(results):
        bh, ba = base_cells[b] // MAX_GOALS, base_cells[b] % MAX_GOALS
        base_pts = _POINTS_TABLE[bh, ba, rh, ra].astype(np.int64)
        us_ctrl += base_pts
        if b < k:
            dh, da = deco_cells[b] // MAX_GOALS, deco_cells[b] % MAX_GOALS
            us_trt += _POINTS_TABLE[dh, da, rh, ra].astype(np.int64)
        else:
            us_trt += base_pts                                     # identical -> k=0 => arms identical

    # ---- OPPONENT board points (shared across arms) ----
    opp_cols = [c for c in range(n_players) if c != us_col]
    opp_pts_base = pts_vec[opp_cols]                               # (N_opp,)
    opp_noise = noise[:, opp_cols]                                 # (n_sims, N_opp)
    N_opp = len(opp_cols)

    if p_field_modal >= 1.0:
        # all opponents play the field modal -> one shared modeled-points vector
        opp_modeled = np.zeros(n_sims, dtype=np.int64)
        for b, (rh, ra) in enumerate(results):
            mh, ma = modal_cells[b] // MAX_GOALS, modal_cells[b] % MAX_GOALS
            opp_modeled += _POINTS_TABLE[mh, ma, rh, ra].astype(np.int64)
        opp_total = opp_pts_base[None, :] + opp_noise + opp_modeled[:, None]
    else:
        # (3) a fraction (1 - p_field_modal) of opponents deviate per board to a uniform non-modal plausible
        #     pick -> erodes our differentiation edge (a rival can also catch the upset). Drawn AFTER the
        #     scorelines so noise+scorelines are identical to the p_field_modal=1 stream.
        opp_modeled = np.zeros((n_sims, N_opp), dtype=np.int64)
        for b, (rh, ra) in enumerate(results):
            pool = _plausible_nonmodal(boards[b]["matrix"], modal_cells[b], PLAUSIBILITY_FLOOR)
            deviate = rng.random((n_sims, N_opp)) >= p_field_modal
            dev_idx = pool[rng.integers(0, pool.size, size=(n_sims, N_opp))]
            cells = np.where(deviate, dev_idx, modal_cells[b])
            ph, pa = cells // MAX_GOALS, cells % MAX_GOALS
            opp_modeled += _POINTS_TABLE[ph, pa, rh[:, None], ra[:, None]].astype(np.int64)
        opp_total = opp_pts_base[None, :] + opp_noise + opp_modeled

    # ---- rank + prize, both arms (strict > -> ties favor us; measure-zero under continuous noise) ----
    us_base = pts_vec[us_col] + noise[:, us_col]
    rank_ctrl = 1 + (opp_total > (us_base + us_ctrl)[:, None]).sum(axis=1)
    rank_trt = 1 + (opp_total > (us_base + us_trt)[:, None]).sum(axis=1)
    prize_ctrl, ctrl = _arm_stats(rank_ctrl)
    prize_trt, trt = _arm_stats(rank_trt)

    res = {"control": ctrl, "treatment": trt,
           "delta_E_prize": trt["E_prize"] - ctrl["E_prize"],
           "delta_p_top3": trt["p_top3"] - ctrl["p_top3"],
           "k": k, "n_sims": n_sims, "sigma_opp": sigma_opp, "p_field_modal": p_field_modal}
    if return_sim_vectors:
        res["_sim_prize_ctrl"] = prize_ctrl
        res["_sim_prize_trt"] = prize_trt
    return res


def _bootstrap_ci_diff(prize_trt, prize_ctrl, *, n_bootstrap=5000, alpha=0.05, boot_seed=BOOT_SEED):
    """Percentile CI on the PAIRED per-sim prize difference (CRN -> tighter than unpaired). Uses
    RandomState(BOOT_SEED) to mirror pool/sigma_calibration.py's bootstrap convention."""
    d = np.asarray(prize_trt, float) - np.asarray(prize_ctrl, float)
    if np.allclose(d, 0.0):                                        # k=0 identity -> zero-variance
        return 0.0, 0.0, float(d.mean())
    n = d.size
    boot = np.random.RandomState(boot_seed)
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        means[i] = d[boot.randint(0, n, n)].mean()
    return (float(np.percentile(means, 100 * alpha / 2)),
            float(np.percentile(means, 100 * (1 - alpha / 2))),
            float(d.mean()))


def recommend_placement(standings, us_id, boards, *, sigma_opp=None,
                        n_sims: int = DEFAULT_N_SIMS, seed: int = DEFAULT_SEED,
                        n_bootstrap: int = 5000, alpha: float = 0.05,
                        eps_min: float = DEFAULT_EPS_MIN,
                        gate_p_field_modal: float = GATE_P_FIELD_MODAL,
                        k_fire: int | None = None) -> dict:
    """k-sweep (exploratory) + ADVERSE-CORNER fire gate. RECOMMENDATION ONLY; NOT fired in the build.

    HEADLINE = absolute P(top-3) per arm (a positive Delta E can be true-but-trivial, e.g. 0.2%->0.4%).
    FIRE GATE (for P4): k is PRE-REGISTERED = k_fire (default = differentiate on ALL candidate boards), NOT
    the argmax-k of the sweep (winner's-curse over nested correlated estimates). Fire iff, at the ADVERSE
    corner = min Delta E over the sigma grid {0.75s,s,1.25s} U {6,8,13.78,19.5} evaluated under
    p_field_modal=gate_p_field_modal (0.85): adverse CI_lo > 0 AND adverse Delta P(top-3) >= eps_min.
    The bootstrap CI is MC-error only (~1/sqrt(n_sims)); the sigma swing dominates -> gate on the corner.
    """
    if sigma_opp is None:
        raise ValueError("sigma_opp is required (PART-0 measured sigma(g2)); pass it explicitly")
    K = len(boards)
    if k_fire is None:
        k_fire = K                                                 # pre-registered: differentiate on all
    _validate(standings, us_id, boards, k_fire)

    # ---- HEADLINE: primary sigma, k_fire, contract base (p_field_modal=1.0) ----
    head = expected_prizes_placement(standings, us_id, boards, k_fire, sigma_opp=sigma_opp,
                                     n_sims=n_sims, seed=seed, p_field_modal=1.0)

    # ---- exploratory k-sweep (primary sigma, base field); paired bootstrap CI per k ----
    sweep = []
    for k in range(K + 1):
        r = expected_prizes_placement(standings, us_id, boards, k, sigma_opp=sigma_opp, n_sims=n_sims,
                                      seed=seed, p_field_modal=1.0, return_sim_vectors=True)
        lo, hi, mean = _bootstrap_ci_diff(r["_sim_prize_trt"], r["_sim_prize_ctrl"],
                                          n_bootstrap=n_bootstrap, alpha=alpha)
        sweep.append({"k": k, "delta_E_prize": r["delta_E_prize"], "ci_lo": lo, "ci_hi": hi,
                      "delta_p_top3": r["delta_p_top3"],
                      "E_prize_ctrl": r["control"]["E_prize"], "E_prize_trt": r["treatment"]["E_prize"]})
    argmax_k = max(sweep, key=lambda s: s["delta_E_prize"])["k"]   # EXPLORATORY only (not the gate)

    # ---- ADVERSE-CORNER fire gate at the pre-registered k_fire ----
    sigma_grid = sorted(set([0.75 * sigma_opp, sigma_opp, 1.25 * sigma_opp]) | set(SIGMA_ABS_ANCHORS))
    grid = []
    for s in sigma_grid:
        r = expected_prizes_placement(standings, us_id, boards, k_fire, sigma_opp=s, n_sims=n_sims,
                                      seed=seed, p_field_modal=gate_p_field_modal, return_sim_vectors=True)
        lo, hi, mean = _bootstrap_ci_diff(r["_sim_prize_trt"], r["_sim_prize_ctrl"],
                                          n_bootstrap=n_bootstrap, alpha=alpha)
        grid.append({"sigma": s, "delta_E_prize": r["delta_E_prize"], "ci_lo": lo, "ci_hi": hi,
                     "delta_p_top3": r["delta_p_top3"]})
    adverse = min(grid, key=lambda g: g["delta_E_prize"])          # worst sigma for the treatment
    fire = bool(adverse["ci_lo"] > 0.0 and adverse["delta_p_top3"] >= eps_min)

    return {"headline": {"k_fire": k_fire,
                         "p_top3_ctrl": head["control"]["p_top3"],
                         "p_top3_trt": head["treatment"]["p_top3"],
                         "delta_p_top3": head["delta_p_top3"],
                         "control": head["control"], "treatment": head["treatment"]},
            "sweep": sweep, "argmax_k_exploratory": argmax_k,
            "sigma_grid": grid, "adverse_corner": adverse,
            "eps_min": eps_min, "gate_p_field_modal": gate_p_field_modal,
            "fire": fire,
            "note": "RECOMMENDATION ONLY - NOT FIRED. Real MD3 run = P4 (Jun-24, separate GO)."}


# --------------------------------------------------------------------------------------------------
# SELFTEST = synthetic scenarios (engine logic, NOT a real pick). matrices are toy 9x9, mass on low scores.
# --------------------------------------------------------------------------------------------------
def _toy_matrix(home_win, draw, away_win):
    """A 9x9 toy score matrix concentrating 1X2 mass on (1,0)/(1,1)/(0,1). For selftest scenarios only."""
    m = np.zeros((MAX_GOALS, MAX_GOALS))
    m[1, 0] = home_win
    m[1, 1] = draw
    m[0, 1] = away_win
    return m / m.sum()


def _selftest(n_sims=DEFAULT_N_SIMS, seed=DEFAULT_SEED):
    SIGMA = 7.18                                          # PART-0 measured sigma(g2) (scenario input)
    # near-even board where the favorite NARROWLY wins the EV -> EV-argmax == field modal == 1-0 (we are
    # CORRELATED with the field by default). coinflip: |P_home 0.45 - P_draw 0.40| = 0.05 < 0.08.
    # decorrelating = 1-1 (the frequent draw the 1-0 field misses): -0.25/board EV but ~+54 relative-to-
    # field variance -> a near-pure decorrelation-variance add (helps trailing, hurts leading).
    nb = {"matrix": _toy_matrix(0.45, 0.40, 0.15), "modal": (1, 0), "us_baseline": (1, 0),
          "decorrelating": (1, 1)}
    boards = [dict(nb), dict(nb), dict(nb)]

    print("=" * 78)
    print(f"placement_mc SELFTEST  seed={seed} n_sims={n_sims} sigma_opp={SIGMA}  (3 near-even boards)")
    print(f"  is_coinflip(near-even board) = {is_coinflip(nb['matrix'])}  (expect True)")
    print("=" * 78)

    # (a) TRAILING: us below the podium cut but within an upset-swing -> variance helps (Delta E > 0)
    st_tr = {f"opp{i:02d}": p for i, p in enumerate([75, 72, 70, 68, 66, 64, 62, 60])}
    st_tr["us"] = 58
    r_tr = expected_prizes_placement(st_tr, "us", boards, k=3, sigma_opp=SIGMA, n_sims=n_sims, seed=seed)
    print(f"(a) TRAILING us=58 (cut~70): ctrl p_top3={r_tr['control']['p_top3']:.4f} "
          f"trt p_top3={r_tr['treatment']['p_top3']:.4f}  Delta E={r_tr['delta_E_prize']:+.5f}  "
          f"(expect Delta E > 0)")

    # (b) LEADING: us comfortably 1st (top prize, no upside above) -> variance regresses us off 1st +
    #     the EV sacrifice -> Delta E <= 0.
    st_ld = {f"opp{i:02d}": p for i, p in enumerate([80, 48, 47, 46, 45, 44, 43, 42])}
    st_ld["us"] = 92
    r_ld = expected_prizes_placement(st_ld, "us", boards, k=3, sigma_opp=SIGMA, n_sims=n_sims, seed=seed)
    print(f"(b) LEADING  us=92 (clear 1st): ctrl E[prize]={r_ld['control']['E_prize']:.4f} "
          f"trt E[prize]={r_ld['treatment']['E_prize']:.4f}  Delta E={r_ld['delta_E_prize']:+.5f}  "
          f"(expect Delta E <= 0)")

    # (c) k=0 identity: Delta E == 0.0 byte-exact
    r0 = expected_prizes_placement(st_tr, "us", boards, k=0, sigma_opp=SIGMA, n_sims=n_sims, seed=seed)
    print(f"(c) k=0 identity: Delta E = {r0['delta_E_prize']!r}  (expect exactly 0.0)")

    assert r_tr["delta_E_prize"] > 0, "(a) trailing: expected Delta E > 0"
    assert r_ld["delta_E_prize"] <= 0, "(b) leading: expected Delta E <= 0"
    assert r0["delta_E_prize"] == 0.0, "(c) k=0: expected exactly 0.0"
    print("SELFTEST: PASS  (a) trailing->+  (b) leading-><=0  (c) k=0->0.0 exact")
    print("=" * 78)
    return r_tr, r_ld, r0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _selftest()


if __name__ == "__main__":
    main()
