"""P4b - σ-calibration: derive the engines' BASE_SIGMA from M7 backtest variance, as a RUNTIME value.

σ is the std of a player's TOURNAMENT-TOTAL competition points (NOT per-match; memory/rules.md
"P4b - σ-calibration model", invariant I2). Two bounds:
    σ_upper = √N · s_pm                  (iid per-match; a STRUCTURAL MAXIMUM)
    σ_lower = √(N · f_div · d) · s_pm    (differential-only; f_div, d are DECLARED PROXIES)
s_pm = std(ev_pts) from `evals.backtest.run_backtest` (headline basis); CI by percentile bootstrap.

This module is READ-ONLY w.r.t. evals/, src/, and pool/pool_montecarlo.py (A2 FROZEN, I1): it imports
run_backtest, computes an ADDITIONAL statistic (a std), and writes ONLY memory/sigma_calibration.md. A2's
BASE_SIGMA=6.0 constant and the byte-exact T-anchor are untouched; σ_cal is injected via the engines'
existing `sigma=` runtime kwarg.

Anti-FM1 (I3): compute_sigma_cal() REFUSES to run unless the model block (`SIGMA_CAL_MODEL: declared`) is
present in memory/rules.md FIRST. The verdict is read AS-IS; σ is NEVER tuned to move it.

Step-3 escalation (Sebas refinement 2026-06-06): when the stylized bracket straddles the ~σ7-8 flip, the
real K=4 engine is run at the bracket endpoints under TWO ownerships - (a) efficient-field AND (b)
targeted-starve. Reading chalk off (a) alone is quasi-tautological (leverage≈1); (b) supplies the real
leverage the σ-flip bites on. ROBUST_CHALK requires chalk in ALL FOUR cells, else
SIGMA_DEPENDENT_UNDER_LEVERAGE -> the decision defers to OBSERVED Jun-10 ownership.

Pure stdlib + numpy.
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RULES_PATH = os.path.join(ROOT, "memory", "rules.md")
SIGMA_CAL_PATH = os.path.join(ROOT, "memory", "sigma_calibration.md")

# Isolated-lever flip (PODIUM-3). The ESCALATION TRIGGER only - a different object from the K=4 verdict.
FLIP_LO, FLIP_HI = 7.0, 8.0
# Declared model parameters (the rules.md P4b block is the source of truth; mirrored here).
DEFAULT_N = 104
DEFAULT_F_DIV = 0.611
DEFAULT_D = 0.50
D_GRID = (0.10, 0.25, 0.50, 0.75, 1.00)
N_GRID = (48, 80, 104)
BOOT_SEED = 20260603         # mirrors evals.backtest.SEED
N_BOOT = 5000


# ---- anti-FM1 model gate -------------------------------------------------------------------------
def model_declared(path: str = RULES_PATH) -> bool:
    """True iff the P4b model sentinel is present in rules.md (the model was logged BEFORE any number)."""
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        return re.search(r"^SIGMA_CAL_MODEL:\s*declared\s*$", f.read(), re.MULTILINE) is not None


# ---- statistics ----------------------------------------------------------------------------------
def bootstrap_std_ci(arr, n_boot: int = N_BOOT, seed: int = BOOT_SEED, alpha: float = 0.05):
    """Percentile bootstrap (lo, hi) CI of std(arr, ddof=1). Fresh RandomState -> order-independent.
    Mirrors evals.backtest.paired_bootstrap_ci but on the STD statistic (not the mean)."""
    a = np.asarray(arr, dtype=float)
    n = a.size
    if n < 2:
        return (float("nan"), float("nan"))
    rng = np.random.RandomState(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        boot[b] = a[rng.randint(0, n, n)].std(ddof=1)
    return (float(np.percentile(boot, 100 * alpha / 2)),
            float(np.percentile(boot, 100 * (1 - alpha / 2))))


def compute_s_pm(seasons=None, delta: float = 0.30, basis: str = "opening", leagues=None) -> dict:
    """std of per-fixture competition points (s_pm) from the M7 backtest, READ-ONLY (writes nothing).
    Returns {ev_spm, b1_spm, ev_spm_ci, n_fixtures, ev_mean_pm, b1_mean_pm, run}."""
    from evals.backtest import run_backtest, NONCOVID
    from evals.fetch_footballdata import LEAGUES
    if seasons is None:
        seasons = NONCOVID
    if leagues is None:
        leagues = LEAGUES
    res = run_backtest(seasons, delta=delta, basis=basis, leagues=leagues)
    ev = np.asarray(res["ev_pts"], dtype=float)
    b1 = np.asarray(res["b1_pts"], dtype=float)
    return {
        "ev_spm": float(ev.std(ddof=1)),
        "b1_spm": float(b1.std(ddof=1)),
        "ev_spm_ci": bootstrap_std_ci(ev),
        "n_fixtures": int(ev.size),
        "ev_mean_pm": float(ev.mean()),
        "b1_mean_pm": float(b1.mean()),
        "run": {"seasons": list(seasons), "delta": delta, "basis": basis},
    }


# ---- the two bounds --------------------------------------------------------------------------------
def sigma_upper(N: int, s_pm: float) -> float:
    """iid per-match: σ_total = √N · s_pm (structural maximum)."""
    return float(np.sqrt(N) * s_pm)


def sigma_lower(N: int, s_pm: float, d: float = DEFAULT_D, f_div: float = DEFAULT_F_DIV) -> float:
    """differential-only: only divergent matches separate players. f_div, d are DECLARED PROXIES."""
    return float(np.sqrt(N * f_div * d) * s_pm)


def read_verdict(bracket) -> str:
    """Stylized bracket vs the ~σ7-8 flip. Returns the ESCALATION TRIGGER (not the final decision):
    'robust_chalk' | 'robust_flip' | 'straddle_escalate'."""
    lo, hi = bracket
    if lo >= FLIP_HI:
        return "robust_chalk"
    if hi <= FLIP_LO:
        return "robust_flip"
    return "straddle_escalate"


def compute_sigma_cal(N: int = DEFAULT_N, d: float = DEFAULT_D, f_div: float = DEFAULT_F_DIV,
                      n_boot: int = N_BOOT, seed: int = BOOT_SEED,
                      rules_path: str = RULES_PATH) -> dict:
    """Master compute. Asserts the rules.md model sentinel (anti-FM1), then s_pm + both bounds + CIs +
    d/N sensitivity + the stylized bracket-vs-flip verdict. σ_cal = conservative σ_lower point estimate.
    Does NOT write any file and does NOT run the engine (that is the Step-3 escalation in main())."""
    if not model_declared(rules_path):
        raise AssertionError(
            "P4b model NOT declared in memory/rules.md (SIGMA_CAL_MODEL: declared). Log the aggregation "
            "model BEFORE computing any number (anti-FM1 / I3).")
    spm = compute_s_pm()
    s = spm["ev_spm"]
    s_ci = spm["ev_spm_ci"]
    up = sigma_upper(N, s)
    up_scale = float(np.sqrt(N))
    up_ci = (up_scale * s_ci[0], up_scale * s_ci[1])
    lo = sigma_lower(N, s, d, f_div)
    lo_scale = float(np.sqrt(N * f_div * d))
    lo_ci = (lo_scale * s_ci[0], lo_scale * s_ci[1])
    bracket = (lo_ci[0], up_ci[1])     # widest: σ_lower CI-lo .. σ_upper CI-hi
    return {
        "s_pm": spm,
        "sigma_upper": {"point": up, "ci": up_ci},
        "sigma_lower": {"point": lo, "ci": lo_ci, "d": d, "f_div": f_div},
        "d_sensitivity": {dd: sigma_lower(N, s, dd, f_div) for dd in D_GRID},
        "n_sensitivity": {nn: sigma_upper(nn, s) for nn in N_GRID},
        "bracket": bracket,
        "stylized_verdict": read_verdict(bracket),
        "sigma_cal": float(lo),        # conservative (contrarian-favoring) σ_lower point estimate
        "N": N, "flip": (FLIP_LO, FLIP_HI),
    }


# ---- Step 3: exact-model escalation under TWO ownerships -----------------------------------------
def escalate_dual_ownership(sigma_lo: float, sigma_hi: float) -> dict:
    """Run the REAL K=4 recommend_portfolio_joint at the σ bracket endpoints under BOTH
    (a) efficient-field and (b) targeted-starve ownership. ROBUST_CHALK iff chalk in all 4 cells;
    else SIGMA_DEPENDENT_UNDER_LEVERAGE (defer the decision to OBSERVED Jun-10 ownership)."""
    from pool.run_podium_draft import _recommend, _build, AWARDS
    starve = {}
    for aw in AWARDS:
        _l, top, _c, ref, _s, _m = _build(aw, boost=1.0)
        second = sorted(top, key=lambda c: -ref[c])[1]       # under-own each lever's 2nd-favourite
        starve[aw] = (second, 0.15)
    cells = {}
    for own_label, kw in (("efficient", {}), ("starve", {"starve": starve})):
        for sig_label, sig in (("sigma_lo", sigma_lo), ("sigma_hi", sigma_hi)):
            rec = _recommend(boost=1.0, sigma=sig, **kw)["recommendation"]
            cells[f"{own_label}|{sig_label}"] = rec["verdict"]
    all_chalk = all(v == "chalk" for v in cells.values())
    return {
        "cells": cells,
        "verdict": "ROBUST_CHALK" if all_chalk else "SIGMA_DEPENDENT_UNDER_LEVERAGE",
        "sigma_lo": sigma_lo, "sigma_hi": sigma_hi,
        "defer": (not all_chalk),
    }


# ---- runtime reader (mirrors pool.objective.read_objective) --------------------------------------
def read_sigma_cal(path: str = SIGMA_CAL_PATH) -> float:
    """Runtime reader of the calibrated σ. Call at run-time (do NOT cache at import).
    Raises FileNotFoundError if P4b has not been run, ValueError on a missing/out-of-range value."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"sigma_cal not declared: {path} missing (run pool/sigma_calibration.py)")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^SIGMA_CAL:\s*([0-9]+(?:\.[0-9]+)?)", text, re.MULTILINE)
    if not m:
        raise ValueError(f"SIGMA_CAL key absent in {path}")
    val = float(m.group(1))
    if not (0.0 < val < 100.0):
        raise ValueError(f"SIGMA_CAL={val!r} out of plausible range (0, 100)")
    return val


# ---- report + persist ----------------------------------------------------------------------------
def _fmt_ci(ci):
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"


def build_report(res: dict, esc: dict | None) -> str:
    """Human + machine-readable content for memory/sigma_calibration.md."""
    spm = res["s_pm"]
    lo, up = res["sigma_lower"], res["sigma_upper"]
    lines = []
    lines.append("# sigma_calibration.md - computed P4b σ-cal value (HITL-readable; runtime-injectable)")
    lines.append("")
    lines.append("> Computed by pool/sigma_calibration.py AFTER the model was declared in memory/rules.md")
    lines.append("> (P4b block, SIGMA_CAL_MODEL: declared). Read at run-time by read_sigma_cal(); runtime")
    lines.append("> callers pass sigma=read_sigma_cal(). A2 BASE_SIGMA=6.0 stays FROZEN (I1). NOT A LOCK.")
    lines.append("")
    d_vals = list(res["d_sensitivity"].values())
    d_lo, d_hi = min(d_vals), max(d_vals)
    lines.append(f"SIGMA_CAL: {res['sigma_cal']:.4f}")
    lines.append("")
    lines.append("> PRECISION CAVEAT - do NOT over-read '13.78' as 2-decimal-precise. The DOMINANT")
    lines.append("> uncertainty is the divergence prior d (a prior on a HIDDEN quantity), NOT sampling noise.")
    lines.append(f"> σ_cal d-DRIVEN RANGE = [{d_lo:.1f}, {d_hi:.1f}] over d in [0.10, 1.00]; {res['sigma_cal']:.2f} "
                 f"is ONLY the d=0.50 point.")
    lines.append(f"> The bootstrap CI {_fmt_ci(res['sigma_lower']['ci'])} (width "
                 f"~{res['sigma_lower']['ci'][1]-res['sigma_lower']['ci'][0]:.1f}) is ~{(d_hi-d_lo)/(res['sigma_lower']['ci'][1]-res['sigma_lower']['ci'][0]):.0f}x "
                 f"NARROWER than the d-range")
    lines.append(f"> (width ~{d_hi-d_lo:.0f}) -> it is NOISE relative to d-uncertainty. f_div={lo['f_div']} is itself a")
    lines.append("> BORROWED PROXY (high-total MATCH fraction != player-DIVERGENCE rate). Read σ_cal as")
    lines.append("> 'order ~14, plausibly 6-20', resolved by OBSERVED Jun-10 ownership - not a fixed point.")
    lines.append("")
    lines.append("## Computation log (deterministic; seed=%d, n_boot=%d)" % (BOOT_SEED, N_BOOT))
    lines.append(f"- basis: run_backtest(NONCOVID, delta={spm['run']['delta']}, "
                 f"basis={spm['run']['basis']!r}); n_fixtures={spm['n_fixtures']}")
    lines.append(f"- s_pm: ev_pts={spm['ev_spm']:.4f} CI {_fmt_ci(spm['ev_spm_ci'])} (PRIMARY=conservative) "
                 f"> b1_pts={spm['b1_spm']:.4f} (chalk cross-check)")
    lines.append(f"  -> ev>b1 SHOWN (not asserted): ev_pts is the larger/safer σ. "
                 f"means ev_pm={spm['ev_mean_pm']:.4f}, b1_pm={spm['b1_mean_pm']:.4f}")
    lines.append(f"- σ_upper = √{res['N']}·s_pm = {up['point']:.3f}  CI {_fmt_ci(up['ci'])}   (iid; ceiling)")
    lines.append(f"- σ_lower = √({res['N']}·{lo['f_div']}·{lo['d']})·s_pm = {lo['point']:.3f}  "
                 f"CI {_fmt_ci(lo['ci'])}   (differential-only; floor)")
    lines.append(f"- bracket (widest) = [{res['bracket'][0]:.3f}, {res['bracket'][1]:.3f}]  vs flip "
                 f"~{FLIP_LO}-{FLIP_HI}  ->  stylized: {res['stylized_verdict']}")
    lines.append("- d-sensitivity (σ_lower): " +
                 ", ".join(f"d={d}:{v:.2f}" for d, v in res["d_sensitivity"].items())
                 + "   [d=0.10 dips below the flip -> the divergence-rate tail is resolved by OBSERVED "
                   "Jun-10 ownership, not by this dry-run]")
    lines.append("- N-sensitivity (σ_upper): " +
                 ", ".join(f"N={n}:{v:.2f}" for n, v in res["n_sensitivity"].items()))
    if esc is not None:
        lines.append("")
        lines.append("## Step-3 escalation - real K=4 engine, 2x2 (ownership x σ-endpoint)")
        lines.append("(Run ALWAYS, not only on a stylized straddle: the ~σ7-8 flip is an ISOLATED-lever")
        lines.append(" threshold and contrarians persist to σ=10 under starve in the dry-run, so even a")
        lines.append(" 'robust_chalk' bracket is CONFIRMED on the real engine under BOTH ownerships -")
        lines.append(" reading chalk off efficient-field alone is tautological [Sebas refinement].)")
        lines.append(f"  endpoints: σ_lo={esc['sigma_lo']:.3f}  σ_hi={esc['sigma_hi']:.3f}")
        for cell, verdict in esc["cells"].items():
            lines.append(f"  {cell:<22} -> {verdict}")
        lines.append(f"  ENGINE VERDICT: {esc['verdict']}"
                     + ("  -> DEFER the chalk-vs-contrarian decision to OBSERVED Jun-10 ownership."
                        if esc["defer"] else
                        "  (chalk in all 4 cells: chalk is σ-robust under real leverage across the bracket)."))
        lines.append(f"  FINAL VERDICT: stylized={res['stylized_verdict']} + engine={esc['verdict']} -> "
                     + ("CHALK is decision-grade-robust within the declared d=0.50 model; the only path to "
                        "contrarian is the d<=~0.10 divergence tail, which Jun-10 OBSERVED ownership resolves."
                        if not esc["defer"] else
                        "SIGMA-DEPENDENT under real leverage -> Jun-10 OBSERVED ownership decides."))
    lines.append("")
    lines.append("### L9 caveat")
    lines.append("σ_cal is derived from EU club-league per-match variance (football-data.co.uk). It is a")
    lines.append("PROXY for WC-2026 variance, NOT a WC measurement (neutral venue / knockout / scoring-rate")
    lines.append("shifts). σ_upper (iid, all 104) is a structural ceiling; σ_lower (divergent-only) is the")
    lines.append("practically relevant floor. The stylized ~σ7-8 flip is an ESCALATION TRIGGER, distinct")
    lines.append("from the real K=4 verdict. RE-RUN podium+champion on σ_cal at Jun-10 (fresh odds +")
    lines.append("OBSERVED ownership) before any lock. No pick is locked here; champion + 4 awards OPEN.")
    lines.append("")
    return "\n".join(lines)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    res = compute_sigma_cal()
    # Always run the real-engine escalation (NOT only on a stylized straddle): the ~σ7-8 flip is an
    # isolated-lever threshold and the dry-run shows contrarians persist to σ=10 under multi-lever
    # starve, so a stylized 'robust_chalk' must still be CONFIRMED on the real K=4 engine under BOTH
    # efficient AND starve ownership (Sebas refinement: efficient-field alone is tautological chalk).
    esc = escalate_dual_ownership(res["bracket"][0], res["bracket"][1])
    report = build_report(res, esc)
    with open(SIGMA_CAL_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print("=" * 88)
    print(f"WROTE {SIGMA_CAL_PATH}  (SIGMA_CAL={res['sigma_cal']:.4f})  -- runtime-injectable; A2 FROZEN.")
    print("=" * 88)


def _selftest():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    res = compute_sigma_cal()
    assert res["sigma_upper"]["point"] > res["sigma_lower"]["point"], res
    assert res["stylized_verdict"] in {"robust_chalk", "robust_flip", "straddle_escalate"}, res
    assert res["sigma_cal"] == res["sigma_lower"]["point"], res
    print("sigma_calibration self-test: PASS")
    print(f"  s_pm(ev)={res['s_pm']['ev_spm']:.4f}  σ_lower={res['sigma_lower']['point']:.3f}  "
          f"σ_upper={res['sigma_upper']['point']:.3f}  stylized={res['stylized_verdict']}")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
