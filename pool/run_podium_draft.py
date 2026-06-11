"""P4 - pool/run_podium_draft.py : integrate market P_true + council overlay + (prior) ownership into the
JOINT engine -> a DRAFT per-pick E[prize] + chalk-vs-contrarian (§7b) recommendation over the K=4 engine levers.

PRIOR-GATED DRY-RUN (2026-06-05 GO): validates the end-to-end integrator + the R9 sensitivities (ownership +-1,
sigma sweep) and the §7b portfolio rule across K=4. It is NOT finalizable: there is NO observed ownership yet,
so ownership_source = 'prior' (is_gated). Every banner is DRAFT/GATED. No lock.

GUARDRAILS:
- Engine input = MARKET full-board P_true (one snapshot per the dry-run cache). FLAG 2/FM2: in the real Jun-10
  run, re-fetch ALL boards fresh and feed the SAME snapshot to engine + council (do NOT mix May-29 outrights
  with Jun-5 council). Here we use the cached files consistently and label them stale.
- Council is an OVERLAY (consensus + council-vs-market divergence + dissent), NOT the engine's probabilistic
  input (it covers only the top-6, no tail). FLAG 3: the §7b leverage (= P_true / OWNERSHIP) is DISTINCT from
  the council-vs-market divergence; they are printed separately and never conflated.
- sigma = BASE_SIGMA = 6.0 is a HAND-TUNED PLACEHOLDER. PODIUM-3: the qualitative chalk-vs-contrarian VERDICT
  is sigma-dependent -> NOT decision-grade until Track-B P4 sigma-calibration; mandatory engine re-run before lock.

Pure stdlib + numpy. Reuses pool.podium_montecarlo (engine), council.run_council (market de-vig + synthesis).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pool.podium_montecarlo import (  # noqa: E402
    recommend_portfolio_joint, CHAMP_BONUS, BASE_SIGMA, DEFAULT_SEED, DEFAULT_N_SIMS, _SENTINEL,
)
from pool.leverage import is_gated  # noqa: E402
from pool.sigma_calibration import read_sigma_cal  # noqa: E402
from pool.ingest_ownership import (  # noqa: E402
    load_observed_from_snapshot, laplace_ownership, laplace_ownership_with_residual,
    blanks_chalk_resolved, _assert_ownership_model_declared,
)
from council.run_council import market_p_true, synthesize, OUTPUTS_DIR  # noqa: E402

AWARDS = ["champion", "top_scorer", "mvp", "best_gk"]   # K=4 engine levers (assister deferred, K=5 if Jun-10 probe)

# σ injected at RUNTIME (Track-B P4b): the engine reads the CALIBRATED σ, not the hand-tuned BASE_SIGMA.
# Graceful fallback to BASE_SIGMA if P4b has not been run. A2 BASE_SIGMA=6.0 stays FROZEN (I1) - this is a
# call-time kwarg only. NOTE (P4b finding): chalk-vs-contrarian is SIGMA_DEPENDENT_UNDER_LEVERAGE
# (efficient->chalk at any σ; starve->contrarian across the whole σ bracket) -> the VERDICT defers to
# OBSERVED Jun-10 ownership; σ_cal alone does not settle it.
try:
    SIGMA_CAL = read_sigma_cal()
    SIGMA_SRC = "calibrated (memory/sigma_calibration.md)"
except (FileNotFoundError, ValueError):
    SIGMA_CAL = BASE_SIGMA
    SIGMA_SRC = "BASE_SIGMA placeholder (P4b σ-calibration not run)"
N_TOTAL = 22                                            # GO-note value; reconcile live N at Jun-10 (CLAUDE.md: 12->20-25)
N_OPP = N_TOTAL - 1                                     # self-excluded (Sebas)

# --- OBSERVED path (PODIUM TEST RUN 2026-06-06; model declared in memory/rules.md) ---
# These are SEPARATE from the prior dry-run constants above. The prior blocks keep N_OPP=21 (a frozen
# gated artifact, labeled "assumed"); the live observed run uses the reconciled N_opp=19 (roster 20 -
# Sebas), asserted against the snapshot. Time-dependent (entrants may join by Jun-10).
N_OPP_OBS = 19
ALPHA_OBS = 1.0                                         # Laplace alpha (DECLARED in rules.md; NOT tuned, I3)
OBS_SNAP_PATH = os.path.join(ROOT, "data", "snapshots", "observed_ownership_2026-06-06.json")

# --- LOCK RUN (Jun-10 PM): decision-grade. SEPARATE from the Jun-6 constants above (which stay frozen for
# the test-run + its tests). N_opp=24 (roster 25 - Sebas); n_sims pre-declared HIGH (PB2) so the 2*SE_diff
# gate resolves >=1pp flips; fresh DATED boards feed market_p_true via path=. RECOMMEND-NEVER-LOCK. ---
N_OPP_LOCK = 24                                         # roster 25 - Sebas; time-dependent for a Jun-11 re-run
LOCK_SNAP_PATH = os.path.join(ROOT, "data", "snapshots", "observed_ownership_2026-06-10.json")
LOCK_N_SIMS = 120_000                                   # PB2 pre-declared: worst-case paired SE_diff <= 0.0024
LOCK_PTRUE_GATE = 0.08                                  # PB1 verdict-layer gate (engine MIN_PTRUE 0.05 untouched)
LOCK_SIGMA_BRACKET = (6.0, 8.0, SIGMA_CAL, 20.0)        # {6, 8, 13.78(calibrated), 20}; primary = SIGMA_CAL
LOCK_DATA_PATHS = {
    "champion":   os.path.join(ROOT, "data", "outrights_2026-06-10.json"),
    "top_scorer": os.path.join(ROOT, "data", "props_top_scorer_2026-06-10.json"),
    "mvp":        os.path.join(ROOT, "data", "props_mvp_2026-06-10.json"),
    "best_gk":    os.path.join(ROOT, "data", "props_best_gk_2026-06-10.json"),
    "assister":   os.path.join(ROOT, "data", "props_assister_2026-06-10.json"),   # K=5 only (assister gate)
}


def _counts_from_shares(shares: dict, n: int) -> dict:
    """Largest-remainder integer allocation of n opponents across candidates (so +-1 sweeps are meaningful)."""
    raw = {k: shares[k] * n for k in shares}
    out = {k: int(raw[k]) for k in raw}
    rem = n - sum(out.values())
    for k in sorted(raw, key=lambda k: -(raw[k] - out[k]))[:rem]:
        out[k] += 1
    return {k: v for k, v in out.items() if v > 0}


def _build(award, boost=1.0):
    """Return (lever, top6, ownership_counts, market_ref_ptrue, ownership_share, meta) for an award.
    boost>1 over-owns the market favourite (illustrative casual-crowd skew)."""
    p_full, top, meta = market_p_true(award, top_n=6)
    lever = {"name": award, "p_true": p_full, "bonus": CHAMP_BONUS}          # winner drawn from FULL board
    s = sum(p_full[c] for c in top)
    ref = {c: p_full[c] / s for c in top}                                    # market P_true over the top-6
    own = dict(ref)
    if boost != 1.0:
        fav = max(own, key=own.get)
        own[fav] *= boost
        z = sum(own.values())
        own = {c: own[c] / z for c in own}
    counts = _counts_from_shares(own, N_OPP)
    share = {c: counts.get(c, 0) / N_OPP for c in top}
    return lever, top, counts, ref, share, meta


def _leverage(ref_ptrue, share):
    """§7b leverage = P_true / ownership (per candidate, same top-6 basis). inf if unowned."""
    return {c: (ref_ptrue[c] / share[c] if share.get(c, 0) > 0 else float("inf")) for c in ref_ptrue}


def _council_overlay(award):
    path = os.path.join(OUTPUTS_DIR, f"lenses_{award}.json")
    if not os.path.exists(path):
        return None
    snap = json.load(open(path, encoding="utf-8"))
    market, top, _ = market_p_true(award, top_n=6)
    return synthesize(award, market, snap.get("candidates", top), snap["lenses"])


def _recommend(boost=1.0, sigma=BASE_SIGMA, bump=None, starve=None):
    """Build all 4 levers and run the joint recommendation.
    bump=(award_idx, cand): move +1 opponent onto `cand` from the favourite (R9 +-1 sweep).
    starve={award: (cand, keep)}: under-own a credible candidate to `keep` of its fair share (crowd overlooks
    it), redistributing to the favourite -> identifies a real contrarian and exercises the §7b flip path."""
    levers, cands, groups_own = [], [], []
    for ai, aw in enumerate(AWARDS):
        lever, top, counts, ref, share, _ = _build(aw, boost=boost)
        if starve and aw in starve:
            c, keep = starve[aw]
            fav = max(counts, key=counts.get)
            if c in counts and c != fav:
                move = int(round(counts[c] * (1 - keep)))
                counts = dict(counts)
                counts[c] -= move
                counts[fav] = counts.get(fav, 0) + move
        if bump and bump[0] == ai:
            _, c = bump
            fav = max(counts, key=counts.get)
            if fav != c and counts.get(fav, 0) > 0:
                counts = dict(counts)
                counts[fav] -= 1
                counts[c] = counts.get(c, 0) + 1
        levers.append(lever)
        cands.append(top)
        groups_own.append(counts)
    groups = [(N_OPP, groups_own)]
    return recommend_portfolio_joint(levers, groups, cands, sigma=sigma, seed=DEFAULT_SEED)


def _build_observed_all(loaded, awards=None, n_opp_obs=N_OPP_OBS, alpha=ALPHA_OBS, data_paths=None):
    """Build the engine levers from observed ownership (Sebas-excluded snapshot, already resolved).
    Per lever: union candidate set (top-6 ∪ observed = FIX-2), Model-A ownership (Laplace + SENTINEL
    blanks), Model-B ownership (true-blank mass redistributed over named P_true, P2-a), and the §7b
    leverage over the top-6 (using Model-A ownership for display).

    Backward-compatible: `_build_observed_all(loaded)` == the Jun-6 K=4 build (awards=AWARDS, N_opp=19,
    undated boards). LOCK-RUN passes awards (K=4 or +assister), n_opp_obs=24, and data_paths (fresh dated
    boards) -> market_p_true reads the Jun-10 odds via path= (FM2)."""
    awards = awards if awards is not None else AWARDS
    data_paths = data_paths or {}
    builds = []
    for aw in awards:
        p_full, top, _meta = market_p_true(aw, top_n=6, path=data_paths.get(aw))
        lv = loaded["levers"][aw]
        rc = lv["resolved_counts"]
        named = sorted(set(top) | set(rc))                                   # K_cand = |union|
        own_a = laplace_ownership_with_residual(rc, n_opp_obs, alpha, named)
        named_shares = laplace_ownership(rc, n_opp_obs, alpha, named)
        denom = n_opp_obs + alpha * len(named)
        blank_mass = lv["blanks"] / denom                                    # true-blank portion
        offboard_mass = sum(lv["offboard_counts"].values()) / denom          # stays on SENTINEL (0 this run)
        own_b = blanks_chalk_resolved(named_shares, blank_mass, p_full)
        if offboard_mass > 0:
            own_b[_SENTINEL] = offboard_mass
        lever = {"name": aw, "p_true": p_full, "bonus": CHAMP_BONUS}
        leverage = {c: (p_full[c] / own_a[c] if own_a.get(c, 0) > 0 else float("inf")) for c in top}
        builds.append({"award": aw, "lever": lever, "top": top, "p_full": p_full, "named": named,
                       "own_a": own_a, "own_b": own_b, "leverage": leverage, "lv": lv})
    return builds


def _recommend_observed(builds, sigma, model="A", n_sims=DEFAULT_N_SIMS, n_opp=N_OPP_OBS,
                        return_sim_vectors=False):
    """Run the joint recommendation on observed ownership. model='A' (sentinel blanks) or 'B'
    (chalk-resolved blanks). Single opponent group of n_opp; each ownership dict sums to 1.
    Backward-compatible: `_recommend_observed(builds, sigma, model)` == the Jun-6 K=4 call (n_sims default,
    N_opp=19). LOCK-RUN passes n_sims=LOCK_N_SIMS, n_opp=24, return_sim_vectors=True (for SE_diff)."""
    levers = [b["lever"] for b in builds]
    cands = [b["top"] for b in builds]
    groups_own = [b["own_a" if model == "A" else "own_b"] for b in builds]
    groups = [(n_opp, groups_own)]
    return recommend_portfolio_joint(levers, groups, cands, n_sims=n_sims, sigma=sigma, seed=DEFAULT_SEED,
                                     return_sim_vectors=return_sim_vectors)


def _print_obs_block(sigma):
    """[OBS] block: PRELIMINARY observed-ownership recommendation + Step-5b blank sensitivity + assister
    advisory + resolved σ verdict. RECOMMENDATION ONLY - never a lock."""
    _assert_ownership_model_declared()                                       # anti-FM1: refuse without the model
    board_keys = {aw: set(market_p_true(aw, top_n=6)[0]) for aw in AWARDS}
    loaded = load_observed_from_snapshot(OBS_SNAP_PATH, board_keys=board_keys)
    assert loaded["n_opp"] == N_OPP_OBS, f"snapshot n_opp {loaded['n_opp']} != N_OPP_OBS {N_OPP_OBS}"
    builds = _build_observed_all(loaded)
    res_a = _recommend_observed(builds, sigma, model="A")
    res_b = _recommend_observed(builds, sigma, model="B")
    rec_a, rec_b = res_a["recommendation"], res_b["recommendation"]

    print("\n[OBS Jun-06 PRELIMINARY]  observed ownership (pollaya, Sebas excluded)  ownership_source=observed")
    print(f"  N_opp={N_OPP_OBS} (roster 20-Sebas; time-dependent)  alpha={ALPHA_OBS:g}  "
          f"K_cand=top6∪observed  sigma={sigma:.4f}  seed={DEFAULT_SEED}  model=A(sentinel)")
    print(f"  {'lever':<11}{'chalk':<16}{'best-contrarian':<16}{'own(bc)':>8}{'Ptrue(bc)':>10}"
          f"{'lev(bc)':>8}   {'chosen':<16}{'small-n':<10}")
    for ai, b in enumerate(builds):
        lvv = rec_a["lever_verdicts"][ai]
        chalk = lvv["chalk"]
        contras = [c for c in b["top"] if c != chalk]
        bc = max(contras, key=lambda c: b["leverage"][c])
        print(f"  {b['award']:<11}{chalk:<16}{bc:<16}{b['own_a'][bc]:>8.3f}{b['p_full'][bc]:>10.3f}"
              f"{b['leverage'][bc]:>8.2f}   {lvv['chosen']:<16}YES {b['lv']['deciders']}/{N_OPP_OBS}")
    print(f"  -> PORTFOLIO {rec_a['recommended']}  VERDICT={rec_a['verdict']}  "
          f"E_chalk={rec_a['e_prize_chalk']:.4f}  E_rec={rec_a['e_prize_recommended']:.4f}  "
          f"improvement={rec_a['improvement']:+.4f}")

    # ---- Step 5b: blank-resolution sensitivity (Model A vs B; per-lever flip -> INDETERMINATE) ----
    print("\n  [Step 5b - blank-resolution sensitivity (R9/L13; read AS-IS, NOT tuned)]")
    print(f"    A sentinel (blanks score 0):  verdict={rec_a['verdict']:<20} portfolio={rec_a['recommended']}")
    print(f"    B chalk-resolved (blanks~Ptrue over named): verdict={rec_b['verdict']:<20} portfolio={rec_b['recommended']}")
    any_flip = False
    for ai, b in enumerate(builds):
        va, vb = rec_a["lever_verdicts"][ai], rec_b["lever_verdicts"][ai]
        ca = "chalk" if va["chosen"] == va["chalk"] else "contrarian"
        cb = "chalk" if vb["chosen"] == vb["chalk"] else "contrarian"
        if ca != cb:
            any_flip = True
            print(f"    {b['award']:<11} A={ca:<10} B={cb:<10} -> INDETERMINATE-preliminary, deferred to Jun-10")
        else:
            print(f"    {b['award']:<11} A={ca:<10} B={cb:<10} -> stable")

    # ---- assister ADVISORY (observed ownership only; NO P_true; NOT in the MC) ----
    asn = loaded["levers"]["assister"]
    arc = asn["resolved_counts"]
    chalk_ass = max(arc, key=arc.get)
    print("\n  [assister ADVISORY - NOT an engine lever (K=4); observed ownership only]")
    print("    observed: " + ", ".join(f"{k} {v}" for k, v in arc.items())
          + f"  (deciders {asn['deciders']}/{N_OPP_OBS}, blanks {asn['blanks']})")
    print(f"    most-owned = {chalk_ass}; NO P_true market -> NO leverage (no fabrication, FM3); "
          f"K=5 gate = Jun-10 FanDuel/Caesars probe.")

    # ---- resolved σ verdict under OBSERVED leverage ----
    if rec_a["verdict"] == "chalk" and rec_b["verdict"] == "chalk" and not any_flip:
        sv = "CHALK (resolved: chalk under observed leverage at sigma=13.78, stable across blank models A/B)"
    elif any_flip:
        sv = "STILL-SIGMA-DEPENDENT / INDETERMINATE (a lever flips between blank models A/B) -> deferred to Jun-10"
    else:
        contra = [rec_a["lever_verdicts"][i]["lever"] for i in range(len(builds))
                  if rec_a["recommended"][i] != rec_a["chalk_portfolio"][i]]
        sv = f"CONTRARIAN on {contra} (observed leverage) - PRELIMINARY, confirm Jun-10"
    print(f"\n  GLOBAL σ-VERDICT (observed leverage, sigma={sigma:.2f}): {sv}")
    print("  PRELIMINARY - n=4-7 deciders/19, selection-bias (most entrants blank). NOT A LOCK. "
          "Decision-grade run = Jun-10 (fresh odds + final ownership + assister probe).")


# ==================================================================================================
# LOCK RUN (Jun-10 PM) - decision-grade. Steps 4-8 of the contract. RECOMMEND-NEVER-LOCK (Sebas locks).
# ==================================================================================================
def _paired_se(table, pf_a, pf_b):
    """Paired-CRN SE of the prize DIFFERENCE between two enumerated portfolios (requires
    return_sim_vectors). std(prize_a - prize_b, ddof=1)/sqrt(n). The CRN pairing makes this the right
    noise floor for a flip's materiality (PB2 / A4)."""
    d = table[pf_a]["_sim_prize"] - table[pf_b]["_sim_prize"]
    n = len(d)
    return float(np.std(d, ddof=1) / np.sqrt(n)) if n > 1 else float("nan")


def _compute_se_diff(table, chalk_pf):
    """Per-portfolio paired SE vs the all-chalk reference. The chalk row is 0 by construction."""
    return {pf: _paired_se(table, pf, chalk_pf) for pf in table}


def _single_flip_pf(chalk_pf, k, cand):
    return tuple(cand if i == k else chalk_pf[i] for i in range(len(chalk_pf)))


def _perturb_lever_build(b, candidate, n_opp, alpha):
    """A4/R9-lock: move ONE blank onto `candidate` on lever b (+-1 ownership) and rebuild own_a/own_b.
    blanks decrease by 1; the named count +1. Returns a rebuilt copy (originals untouched)."""
    rc = dict(b["lv"]["resolved_counts"])
    rc[candidate] = rc.get(candidate, 0) + 1
    blanks = max(0, b["lv"]["blanks"] - 1)
    top, p_full = b["top"], b["p_full"]
    named = sorted(set(top) | set(rc))
    own_a = laplace_ownership_with_residual(rc, n_opp, alpha, named)
    named_shares = laplace_ownership(rc, n_opp, alpha, named)
    denom = n_opp + alpha * len(named)
    own_b = blanks_chalk_resolved(named_shares, blanks / denom, p_full)
    off = sum(b["lv"]["offboard_counts"].values()) / denom
    if off > 0:
        own_b[_SENTINEL] = off
    nb = dict(b)
    nb["own_a"], nb["own_b"] = own_a, own_b
    nb["leverage"] = {c: (p_full[c] / own_a[c] if own_a.get(c, 0) > 0 else float("inf")) for c in top}
    return nb


def _r9_lock_holds(builds, k, contrarian, chalk, n_opp, alpha, sigma, n_sims):
    """A4 ownership +-1: lever k's contrarian must remain the recommended pick when one blank moves onto
    the contrarian (P+) AND onto the chalk (P-), under BOTH blank-models. False on any flip back to chalk."""
    for cand in (contrarian, chalk):
        pert = list(builds)
        pert[k] = _perturb_lever_build(builds[k], cand, n_opp, alpha)
        for model in ("A", "B"):
            rec = _recommend_observed(pert, sigma, model=model, n_sims=n_sims, n_opp=n_opp)["recommendation"]
            if rec["recommended"][k] != contrarian:
                return False
    return True


def _lock_stability_sweep(builds, n_opp, n_sims):
    """Run the σ-bracket x {A,B} sweep. Returns {(sigma, model): recommendation}. K=4 or K=5 per builds."""
    stab = {}
    for s in LOCK_SIGMA_BRACKET:
        for model in ("A", "B"):
            stab[(s, model)] = _recommend_observed(builds, s, model=model, n_sims=n_sims,
                                                   n_opp=n_opp)["recommendation"]
    return stab


def _lever_cell_is_contrarian(rec, k):
    """In recommendation `rec`, did the recommended portfolio pick lever k's contrarian (vs its chalk)?"""
    return rec["recommended"][k] != rec["chalk_portfolio"][k]


def _print_lock_run_block(sigma=None, awards=None, snap_path=LOCK_SNAP_PATH, n_opp=N_OPP_LOCK,
                          alpha=ALPHA_OBS, n_sims=LOCK_N_SIMS, data_paths=None, k_label=None):
    """LOCK RUN decision-grade recommendation (contract Steps 4-8). FRESH dated boards + EMBEDDED FINAL
    ownership (N_opp=24), σ-bracket {6,8,13.78,20}, dual blank-models, paired 2*SE_diff gate, A4 stability +
    R9-lock, §7b <=1-contrarian. RECOMMENDATION ONLY - Sebas locks manually on pollaya."""
    sigma = sigma if sigma is not None else SIGMA_CAL
    awards = awards if awards is not None else AWARDS
    data_paths = data_paths if data_paths is not None else LOCK_DATA_PATHS
    K = len(awards)
    k_label = k_label or f"K={K}"
    _assert_ownership_model_declared()                                       # anti-FM1

    # missing-fresh-board guard (Step 6 precondition: D1/D3 fetched). Friendly STOP, not a stack trace.
    missing = [aw for aw in awards if not os.path.exists(data_paths.get(aw, ""))]
    if missing:
        print(f"\n[LOCK RUN {k_label}]  BLOCKED: fresh dated boards missing for {missing}.")
        print("  Run Step 1 (champion fetch) + Step 3 (props) first; the lock block needs Jun-10 odds (FM2).")
        return None
    if not os.path.exists(snap_path):
        print(f"\n[LOCK RUN {k_label}]  BLOCKED: ownership snapshot {os.path.basename(snap_path)} missing "
              "(Step 4 writes it).")
        return None

    board_keys = {aw: set(market_p_true(aw, top_n=6, path=data_paths.get(aw))[0]) for aw in awards}
    loaded = load_observed_from_snapshot(snap_path, board_keys=board_keys)
    assert loaded["n_opp"] == n_opp, f"snapshot n_opp {loaded['n_opp']} != N_OPP_LOCK {n_opp}"
    builds = _build_observed_all(loaded, awards=awards, n_opp_obs=n_opp, alpha=alpha, data_paths=data_paths)

    print("\n" + "=" * 96)
    print(f"[LOCK RUN {k_label}]  ownership_source=observed (FINAL, Sebas excluded)  NOT A LOCK")
    print(f"  N_opp={n_opp} (roster 25-Sebas; time-dependent for a Jun-11 re-run)  alpha={alpha:g}  "
          f"K_cand=top6∪observed  n_sims={n_sims}  seed={DEFAULT_SEED}")
    print(f"  σ primary={sigma:.4f} (calibrated)  bracket={tuple(round(s,2) for s in LOCK_SIGMA_BRACKET)}  "
          f"P_true gate={LOCK_PTRUE_GATE:g} (verdict layer; engine MIN_PTRUE 0.05 untouched)")

    # --- primary cell (model A @ calibrated σ) WITH per-sim vectors -> SE_diff ---
    res_a = _recommend_observed(builds, sigma, model="A", n_sims=n_sims, n_opp=n_opp, return_sim_vectors=True)
    rec_a = res_a["recommendation"]
    table = res_a["portfolios"]
    chalk_pf = rec_a["chalk_portfolio"]
    se_diff = _compute_se_diff(table, chalk_pf)
    e_chalk = rec_a["e_prize_chalk"]
    worst_se = float(np.sqrt(2 * 0.36 / n_sims))                              # PB2 worst-case bound, reported

    # --- σ-bracket x {A,B} stability sweep ---
    stab = _lock_stability_sweep(builds, n_opp, n_sims)

    # --- per-lever verdict (JUDGMENT; no tuning) ---
    print(f"\n  per-lever verdict (primary cell model A @ σ={sigma:.2f}; SE_diff worst-case bound={worst_se:.4f})")
    print(f"  {'lever':<11}{'chalk':<16}{'best-contra':<16}{'own':>7}{'Ptrue':>8}{'lev':>7}"
          f"{'ΔE':>9}{'SEΔ':>8}{'2·SE':>8}  {'σ/blank':<9}{'R9':<4}VERDICT")
    final = list(chalk_pf)
    contrarian_levers = []
    band_notes = []
    for k, b in enumerate(builds):
        lvv = rec_a["lever_verdicts"][k]
        chalk_k = lvv["chalk"]
        contra_k = lvv["contrarian"]                                          # engine-identified (gate 0.05)
        # display best-leverage non-chalk candidate even when no engine contrarian
        non_chalk = [c for c in b["top"] if c != chalk_k]
        bc = max(non_chalk, key=lambda c: b["leverage"][c]) if non_chalk else chalk_k
        own_bc = b["own_a"].get(bc, 0.0)
        p_bc = b["p_full"].get(bc, 0.0)
        lev_bc = b["leverage"].get(bc, float("inf"))

        verdict, sb_tag, r9_tag = "STABLE-CHALK", "-", "-"
        if contra_k is not None:
            p_contra = b["p_full"].get(contra_k, 0.0)
            single_pf = _single_flip_pf(chalk_pf, k, contra_k)
            delta = table[single_pf]["E_prize"] - e_chalk if single_pf in table else 0.0
            se = se_diff.get(single_pf, float("nan"))
            # stability across the σ-bracket x both blank-models: does the recommended pf keep this lever
            # contrarian everywhere? (any disagreement -> INDETERMINATE, LM7)
            cells_contra = [_lever_cell_is_contrarian(stab[(s, m)], k)
                            for s in LOCK_SIGMA_BRACKET for m in ("A", "B")]
            sigma_blank_stable = all(cells_contra)
            sigma_blank_split = any(cells_contra) and not all(cells_contra)
            sb_tag = "stable" if sigma_blank_stable else ("split" if sigma_blank_split else "none")
            gate_08 = p_contra > LOCK_PTRUE_GATE                              # PB1
            signal_pos = delta > 2 * se                                      # flip materially BEATS chalk
            signal_neg = delta < -2 * se                                     # flip materially LOSES to chalk
            within_noise = not signal_pos and not signal_neg                 # |ΔE| <= 2*SE -> genuinely ambiguous
            if 0.05 < p_contra <= LOCK_PTRUE_GATE:
                band_notes.append(f"{b['award']}:{contra_k} P_true={p_contra:.3f} in 0.05-0.08 band "
                                  f"-> reported-not-selected (PB1)")
            if not gate_08:
                verdict = "STABLE-CHALK"                                     # contrarian fails the 0.08 gate
            elif signal_pos and sigma_blank_stable:
                r9_ok = _r9_lock_holds(builds, k, contra_k, chalk_k, n_opp, alpha, sigma, n_sims)
                r9_tag = "ok" if r9_ok else "fail"
                if r9_ok:
                    verdict = "STABLE-CONTRARIAN"
                    final[k] = contra_k
                    contrarian_levers.append((k, contra_k, delta, se))
                else:
                    verdict = "INDETERMINATE->chalk"                         # beats chalk but fragile to +-1 (R9)
            elif sigma_blank_split or within_noise or (signal_pos and not sigma_blank_stable):
                verdict = "INDETERMINATE->chalk"                             # ambiguous: within noise OR σ/blank split
            else:
                verdict = "STABLE-CHALK"                                     # flip determinately LOSES (signal_neg)
            print(f"  {b['award']:<11}{chalk_k:<16}{contra_k:<16}{own_bc:>7.3f}{p_contra:>8.3f}"
                  f"{lev_bc:>7.2f}{delta:>+9.4f}{se:>8.4f}{2*se:>8.4f}  {sb_tag:<9}{r9_tag:<4}{verdict}")
        else:
            print(f"  {b['award']:<11}{chalk_k:<16}{bc:<16}{own_bc:>7.3f}{p_bc:>8.3f}"
                  f"{lev_bc:>7.2f}{'-':>9}{'-':>8}{'-':>8}  {sb_tag:<9}{r9_tag:<4}{verdict}")

    # --- σ-bracket x {A,B} ΔE matrix (LM7 stability evidence): each lever's best-contra single-flip ΔE.
    #     NEGATIVE beyond 2·SE at EVERY σ = determinately chalk (flip loses); a sign change = σ-dependent. ---
    print(f"\n  [σ-bracket ΔE matrix]  single-flip ΔE±2·SE_diff per lever (NEG = chalk better; sign flip = σ-dep)")
    hdr = "  " + f"{'lever':<11}{'best-contra':<15}" + "".join(f"σ={s:<14.2f}" for s in LOCK_SIGMA_BRACKET)
    print(hdr)
    for k, b in enumerate(builds):
        contra_k = rec_a["lever_verdicts"][k]["contrarian"]
        if contra_k is None:
            print(f"  {b['award']:<11}{'(none>gate)':<15}" + "".join(f"{'—':<16}" for _ in LOCK_SIGMA_BRACKET))
            continue
        cells = []
        for s in LOCK_SIGMA_BRACKET:
            rr = _recommend_observed(builds, s, model="A", n_sims=n_sims, n_opp=n_opp,
                                     return_sim_vectors=True)
            tt, cc = rr["portfolios"], rr["recommendation"]["chalk_portfolio"]
            pf = _single_flip_pf(cc, k, contra_k)
            if pf in tt:
                dd = tt[pf]["E_prize"] - tt[cc]["E_prize"]
                cells.append(f"{dd:+.4f}±{2*_paired_se(tt, pf, cc):.4f}")
            else:
                cells.append("n/a")
        print(f"  {b['award']:<11}{contra_k:<15}" + "".join(f"{c:<16}" for c in cells))

    # --- P_true-tie surface (e.g. MVP Kane=Yamal +800): the chalk tie-break went to the LESS-owned
    #     candidate (correct for E[prize]) but it is single-book fragile -> SURFACE for HITL. ---
    for k, b in enumerate(builds):
        top = b["top"]
        if len(top) < 2:
            continue
        c0, c1 = top[0], top[1]
        if abs(b["p_full"][c0] - b["p_full"][c1]) < 1e-6:
            own0, own1 = b["own_a"].get(c0, 0.0), b["own_a"].get(c1, 0.0)
            less, more = (c0, c1) if own0 <= own1 else (c1, c0)
            print(f"\n  ⚠ P_true TIE ({b['award']}): {c0}={c1}={b['p_full'][c0]:.4f} (single-book). "
                  f"chalk tie-broke to the LESS-owned {less} (own {min(own0,own1):.3f}) over {more} "
                  f"(own {max(own0,own1):.3f}) -> correct for E[prize] IF the tie is real, but FRAGILE. "
                  f"Contract default = the cross-book/crowd favourite. SURFACE for HITL.")

    # --- §7b <=1-contrarian enforcement (A2-auditor) ---
    if len(contrarian_levers) > 1:
        best = max(contrarian_levers, key=lambda t: t[2])                    # keep the largest-ΔE flip
        demoted = [cl for cl in contrarian_levers if cl[0] != best[0]]
        for k, _c, _d, _s in demoted:
            final[k] = chalk_pf[k]
        print(f"\n  §7b DEMOTION: {len(contrarian_levers)} STABLE-CONTRARIAN levers > 1 allowed -> keep the "
              f"largest-ΔE flip (lever {best[0]} {best[1]}), demote {[d[1] for d in demoted]} to chalk.")
        contrarian_levers = [best]
    final = tuple(final)

    # --- pairwise-surfacing (A2-auditor): a double flip that beats the best single by >2*SE_diff is
    #     SURFACED for HITL, never auto-selected ---
    singles = {pf for pf in table if sum(1 for i in range(K) if pf[i] != chalk_pf[i]) == 1}
    doubles = {pf for pf in table if sum(1 for i in range(K) if pf[i] != chalk_pf[i]) == 2}
    best_single = max(singles, key=lambda pf: table[pf]["E_prize"], default=chalk_pf)
    if doubles:
        best_double = max(doubles, key=lambda pf: table[pf]["E_prize"])
        gain = table[best_double]["E_prize"] - table[best_single]["E_prize"]
        se_pd = _paired_se(table, best_double, best_single)
        if gain > 2 * se_pd:
            print(f"\n  ⚠ PAIRWISE SURFACED for HITL (NOT auto-selected): {best_double} beats best single "
                  f"{best_single} by ΔE={gain:+.4f} > 2·SE_diff={2*se_pd:.4f}. Sebas decides §7b.")

    # --- §7b portfolio check + recommendation ---
    n_contra = sum(1 for i in range(K) if final[i] != chalk_pf[i])
    e_final = table[final]["E_prize"] if final in table else None
    print(f"\n  RECOMMENDED PORTFOLIO ({k_label}): {final}")
    print(f"  §7b: {n_contra} contrarian lever(s) (<=1 enforced)  E_chalk={e_chalk:.4f}"
          + (f"  E_rec={e_final:.4f}  ΔE={e_final-e_chalk:+.4f}" if e_final is not None else ""))
    for note in band_notes:
        print(f"  band: {note}")

    return {"recommended": final, "chalk": chalk_pf, "builds": builds, "table": table,
            "se_diff": se_diff, "rec_a": rec_a, "stab": stab, "contrarian_levers": contrarian_levers,
            "awards": awards, "n_opp": n_opp}


def _pollaya_spelling(snap_path):
    """board-key -> exact pollaya spelling (for the manual TRANSCRIPTION BLOCK). Read from the snapshot's
    `pollaya_display` map (Step 4 must write it); board key returned verbatim + flagged if absent."""
    try:
        snap = json.load(open(snap_path, encoding="utf-8"))
    except Exception:
        return {}
    return snap.get("pollaya_display", {})


def _lock_run_main(awards_k4=None, snap_path=LOCK_SNAP_PATH, data_paths=None):
    """Orchestrate the decision-grade LOCK RUN: K=4 always; K=5 iff the assister dated board exists
    (Step-2 gate passed). Prints K-invariance, the §6 TRANSCRIPTION BLOCK, WATCH-ITEMS + NOT-A-LOCK banner.
    RECOMMENDATION ONLY - CC never locks."""
    awards_k4 = awards_k4 if awards_k4 is not None else AWARDS
    data_paths = data_paths if data_paths is not None else LOCK_DATA_PATHS
    print("=" * 96)
    print("PODIUM LOCK RUN (Jun-10 PM) - DECISION-GRADE  ownership_source=observed(FINAL)  🛑 NOT A LOCK")
    print(f"  fresh dated boards (FM2): {os.path.basename(data_paths['champion'])} + props_*_2026-06-10")
    print(f"  snapshot: {os.path.basename(snap_path)}  (N_opp={N_OPP_LOCK})   Sebas locks manually on pollaya.")
    print("=" * 96)

    out_k4 = _print_lock_run_block(awards=awards_k4, snap_path=snap_path, data_paths=data_paths, k_label="K=4")
    if out_k4 is None:
        print("\nLOCK RUN halted (precondition missing). Complete Steps 1/3/4 then re-run --lock-run.")
        return

    # K=5 iff the assister gate passed (Step 2 wrote the dated assister board).
    out_k5 = None
    if os.path.exists(data_paths.get("assister", "")):
        out_k5 = _print_lock_run_block(awards=list(awards_k4) + ["assister"], snap_path=snap_path,
                                       data_paths=data_paths, k_label="K=5")
        # K-invariance: the SHARED levers' chosen picks must not move between K=4 and K=5.
        print("\n  [K-invariance] shared-lever picks K=4 vs K=5:")
        for k, aw in enumerate(awards_k4):
            a, b = out_k4["recommended"][k], out_k5["recommended"][k]
            tag = "ok" if a == b else "⚠ MOVED"
            print(f"    {aw:<11} K4={a:<16} K5={b:<16} {tag}")
    else:
        print("\n  [K-gate] assister dated board absent -> K=4 (assister chalk-manual; no fabricated P_true, FM3).")

    chosen = out_k5 if out_k5 is not None else out_k4
    # --- TRANSCRIPTION BLOCK (manual lock; pollaya-exact spelling) ---
    disp = _pollaya_spelling(snap_path)
    print("\n  " + "-" * 60)
    print("  TRANSCRIPTION BLOCK  (Sebas types these into pollaya - EXACT spelling)")
    missing_disp = []
    for k, aw in enumerate(chosen["awards"]):
        pick = chosen["recommended"][k]
        spelled = disp.get(pick, pick)
        if pick not in disp:
            missing_disp.append(pick)
        print(f"    {aw:<11}: {spelled}")
    if missing_disp:
        print(f"    [!] no pollaya_display spelling in snapshot for {missing_disp} - VERIFY accents manually.")
    print("  " + "-" * 60)

    print("\n  WATCH-ITEMS: (1) champion England/Argentina (0-owned, lev 3.17/2.69) FAIL on E[prize]: the flip "
          "is NEGATIVE at every σ in [2,20] (10-pt lever swamped by σ≈14 base noise) -> STABLE-CHALK Spain; "
          "(2) MVP Kane=Yamal +800 single-book TIE -> engine picks the 0-owned Kane (E[prize]-max), contract "
          "default = Yamal (crowd/cross-book) - the ONE HITL call; (3) re-confirm 0-owned England/Argentina "
          "+ N_opp=24 immediately PRE-LOCK (binding GO#1 gate).")
    print("  CAVEATS: σ domain-gap (L9, club-league proxy); fresh-as-of D1 timestamp; blanks-as-undecided.")
    print("\n" + "=" * 96)
    print("RECOMMENDATION - SEBAS LOCKS MANUALLY - NOT A LOCK.  Champion + 5 picks OPEN until Sebas locks.")
    print("=" * 96)


def main():
    if "--lock-run" in sys.argv:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        _lock_run_main()
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 96)
    print("PODIUM P4 - DRAFT / GATED  (prior-gated dry-run)   ownership_source=prior  is_gated=%s" % is_gated("prior"))
    print(f"  N={N_TOTAL} (assumed; reconcile live N at Jun-10)  N_opp={N_OPP}  seed={DEFAULT_SEED}  "
          f"sigma={SIGMA_CAL:.4f} [{SIGMA_SRC}]")
    print("  P4b: chalk-vs-contrarian = SIGMA_DEPENDENT_UNDER_LEVERAGE (efficient->chalk; starve->contrarian "
          "across the σ bracket) -> VERDICT defers to OBSERVED Jun-10 ownership.")
    print("  snapshot (DRY-RUN cached/stale): outrights.json(as_of 2026-05-29) + props_*(2026-06-02). "
          "Jun-10 = ONE fresh re-fetch (FLAG2/FM2).")
    print("  engine input = MARKET full-board P_true; council = overlay only (FLAG3: divergence != §7b leverage).")
    print("=" * 96)

    # ---- BASE: efficient prior (ownership ~ market P_true) ----
    print("\n[BASE]  efficient prior  (ownership proportional to market P_true over the top-6)")
    res = _recommend(boost=1.0, sigma=SIGMA_CAL)
    rec = res["recommendation"]
    print(f"  {'lever':<11}{'chalk':<14}{'best-contrarian':<18}{'§7b lev':>8}   {'chosen':<14}")
    for ai, aw in enumerate(AWARDS):
        lever, top, counts, ref, share, _ = _build(aw, boost=1.0)
        lev = _leverage(ref, share)
        lv = rec["lever_verdicts"][ai]
        contras = [c for c in top if c != lv["chalk"]]
        bc = max(contras, key=lambda c: lev[c])
        print(f"  {aw:<11}{lv['chalk']:<14}{bc:<18}{lev[bc]:>8.2f}   {lv['chosen']:<14}")
    print(f"  -> PORTFOLIO {rec['recommended']}  VERDICT={rec['verdict']}  "
          f"E_chalk={rec['e_prize_chalk']:.4f}  E_rec={rec['e_prize_recommended']:.4f}  "
          f"improvement={rec['improvement']:+.4f}")
    print("  (efficient field -> leverage ~1 everywhere -> no contrarian -> all-chalk, as expected)")

    # ---- council overlay ----
    print("\n[COUNCIL OVERLAY]  (triangulation; engine uses MARKET P_true, not these)")
    for aw in AWARDS:
        syn = _council_overlay(aw)
        if not syn:
            print(f"  {aw:<11} (no council snapshot)")
            continue
        tag = " [CONTESTED]" if syn["contested"] else ""
        diss = ",".join(f"{d['lens']}->{d['top']}" for d in syn["dissent"]) or "none"
        print(f"  {aw:<11} median-leader={syn['consensus']:<14}{tag:<12} vote={syn['vote_verdict']:<11} "
              f"divergence={syn['leverage_council_vs_market']:.2f}x  dissent: {diss}")

    # ---- R9a: sigma sweep (PODIUM-3 sign-stability) ----
    print("\n[R9a sigma-sweep]  (efficient prior; PODIUM-3: the qualitative verdict is sigma-dependent)")
    for s in (4.0, 6.0, 8.0, 10.0, 12.0):
        r = _recommend(boost=1.0, sigma=s)["recommendation"]
        print(f"  sigma={s:>4.1f}  verdict={r['verdict']:<20} portfolio={r['recommended']}")

    # ---- R9b: ownership +-1 (thin integers at small N move leverage) ----
    print("\n[R9b ownership +-1]  (move 1 opponent onto each lever's top non-chalk candidate)")
    base_pf = res["recommendation"]["recommended"]
    for ai, aw in enumerate(AWARDS):
        lever, top, counts, ref, share, _ = _build(aw, boost=1.0)
        chalk = res["recommendation"]["lever_verdicts"][ai]["chalk"]
        bc = max([c for c in top if c != chalk], key=lambda c: _leverage(ref, share)[c])
        r = _recommend(boost=1.0, bump=(ai, bc), sigma=SIGMA_CAL)["recommendation"]
        flip = "FLIP" if r["recommended"] != base_pf else "stable"
        print(f"  {aw:<11} +1 -> {bc:<16} verdict={r['verdict']:<20} {flip}")

    # ---- STRESS: targeted-starve (crowd under-owns one credible candidate per lever) ----
    # Starve each lever's 2nd-favourite to 15% of fair share -> high §7b leverage -> contrarian IDENTIFIED,
    # so the flip-evaluation path + PODIUM-3 sigma-dependence are exercised in the integrated K=4 setting.
    starve = {}
    for aw in AWARDS:
        _l, top, _c, ref, _s, _m = _build(aw, boost=1.0)
        second = sorted(top, key=lambda c: -ref[c])[1]
        starve[aw] = (second, 0.15)
    print("\n[STRESS targeted-starve]  (each lever's 2nd-fav under-owned to 15% -> contrarian identified; GATED)")
    print("  starved (under-owned credible candidate) per lever: "
          + ", ".join(f"{aw}->{starve[aw][0]}" for aw in AWARDS))
    for s in (4.0, 6.0, 8.0, 10.0):
        r = _recommend(sigma=s, starve=starve)["recommendation"]
        ids = sum(1 for lv in r["lever_verdicts"] if lv["contrarian"] is not None)
        nc = sum(1 for i in range(4) if r["recommended"][i] != r["chalk_portfolio"][i])
        print(f"  sigma={s:>4.1f}  contrarians_identified={ids}/4  chosen_contrarian={nc}  "
              f"verdict={r['verdict']:<20} improvement={r['improvement']:+.4f}")
    print("  (PODIUM-3: if the flip fires at low sigma but not high, the qualitative verdict is sigma-dependent;")
    print("   if it stays chalk even with contrarians identified, the K=4 joint dilution suppresses it -- L12.)")

    # ---- OBS: PRELIMINARY observed-ownership run (PODIUM TEST RUN 2026-06-06) ----
    _print_obs_block(sigma=SIGMA_CAL)

    print("\n" + "=" * 96)
    print("🛑 DRAFT - NOT A LOCK.  [BASE]/[R9]/[STRESS] = prior-gated (is_gated); [OBS] = PRELIMINARY observed.")
    print("   This dry-run validates the pipeline + R9 sensitivities only. The finalizable run is the Jun-10")
    print("   EVENING lock on FRESH odds (one snapshot) + REAL observed ownership + sigma-calibrated engine")
    print("   (PODIUM-3). Hard constraint = tournament start: first match Jun-11 (~13:00 CST / 21:00 CEST) --")
    print("   never race kickoff; Jun-12 is VOID. Champion + 4 awards OPEN. Sebas locks, not this engine.")
    print("=" * 96)


if __name__ == "__main__":
    main()
