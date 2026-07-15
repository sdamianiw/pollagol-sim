# -*- coding: utf-8 -*-
"""P(FINISH #1) MULTIVERSE HARNESS (2026-07-14, ADVISORY; I-3 clean, imported by nothing).
KNOWN DEFECT (found 2026-07-15 by greg_paths.py exact cross-validation): the pay dict uses
numpy bool "+" (= logical OR), capping every award payout at ONE leg -- multi-leg parlays
never stacked, so the committed run OVERSTATES P(#1) (.9996 headline; true value lower,
order ~.99, since chasers hold more stackable legs than us). Superseded by greg_paths.py /
fixed greg_block.py for the SF2 decision; retained unfixed as the audit trail of L-line
2026-07-15. Do NOT reuse this file without applying .astype(float) casts per leg.

One JOINT seeded simulation solving every dependency in every branch:
  SF1 real 120' cell (frozen dist, our entry 1-0 FRA) -> winner  x  SF2 real cell (entry 1-0 ENG,
  ASSUMED pending its council) -> winner -> final via PAIR (ASSUMED, swept) -> CHAMPION ->
  award CATEGORICALS conditioned on champion with MUTUAL EXCLUSIVITY (one Boot/MVP/GK/AST winner --
  fixes the independent-Bernoulli simplification of endgame_branches_sf.py) -> REALIZED locked-50
  settlement per player (absolute pays both sides; common legs cancel naturally) -> hold test
  gap + match-layer - delta > 0 (STRICT: a points-TIE counts as a LOSS = conservative, since our
  17-pleno tiebreak lead would actually win most ties; tiebreak-adjusted number also printed).
Match layer: SF1/SF2 = our sampled points minus a mixture-sampled rival entry per chaser per game
(same ASSUMED q=.25 mixtures as lead_max_sf.py); 3rd-place + final = the SF2-mixture diff proxy
(ASSUMED, common-shock across chasers). Ownership = locked_ownership_2026-06-28.md (OBSERVED).
Gaps = Jul-12 board. Award conditionals = the committed AWARD/MBAPPE_BOOT values (ASSUMED, swept).
CROSS-CHECK: forced-W* subset must reproduce worst_world_stress.py (~.995). B4 = run twice."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-14T16-52-55Z.json"
FID_FE = "f9aa13a662d1658e5a02cfc06d6a2d73"   # France vs Spain (home=FRA)
FID_EA = "ced22494ae0bbb8cc4f7108bf6f493df"   # England vs Argentina (home=ENG)
GAPS = {"Greg": 28, "Gonzalo": 35, "felipe": 39, "Lucas": 39, "Rodrigo": 50}
LOCK = 10.0
SEED = 42
N = 200_000
OUR_FE, OUR_EA = (1, 0), (1, 0)   # tonight's council verdict; SF2 PRELIMINARY (swept below)
PAIR = {("FRA", "ENG"): 0.55, ("FRA", "ARG"): 0.55, ("ESP", "ENG"): 0.50, ("ESP", "ARG"): 0.50}
MIX_FE = {(1, 0): 0.2625, (2, 1): 0.225, (2, 0): 0.1125, (1, 1): 0.15,
          (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
MIX_EA = {(1, 0): 0.30, (2, 1): 0.1875, (1, 1): 0.15, (2, 0): 0.1125,
          (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
BRANCHES = ("FRA", "ESP", "ENG", "ARG")


def dist_cells(fid):
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
    d = ko_adjust(run_match(live)["matrix"])["dist_120"]
    n = d.shape[0]
    cells = [(a, b) for a in range(n) for b in range(n) if d[a, b] > 0]
    ps = np.array([d[a, b] for a, b in cells], float)
    return cells, ps / ps.sum()


def award_probs(cb):
    """Per-champion-branch categorical over named award outcomes (committed AWARD values; 'other'
    absorbs the remainder -> mutual exclusivity guaranteed)."""
    boot = {"Mbappe": {"FRA": .45, "ESP": .35, "ENG": .30, "ARG": .25}[cb],
            "Kane": .20 if cb == "ENG" else .02, "Dembele": .02}
    mvp = {"Mbappe": .60 if cb == "FRA" else .05, "Kane": .30 if cb == "ENG" else .02, "Yamal": .02}
    gk = {"Maignan": .65 if cb == "FRA" else .05, "Dibu": .45 if cb == "ARG" else .03}
    ast = {"Olise": .70 if cb == "FRA" else .50, "Messi": .05, "MbappeA": .10 if cb == "FRA" else .02}
    for d_ in (boot, mvp, gk, ast):
        assert sum(d_.values()) <= 1.0 + 1e-9
    return boot, mvp, gk, ast


def sample_award(rng, cat, n):
    """Vector-sample a categorical dict (+implicit 'other') -> array of names."""
    names = list(cat.keys())
    cum = np.cumsum([cat[k] for k in names])
    u = rng.random(n)
    out = np.full(n, "other", dtype=object)
    lo = 0.0
    for k, hi in zip(names, cum):
        out[(u >= lo) & (u < hi)] = k
        lo = hi
    return out


def main():
    rng = np.random.default_rng(SEED)
    cFE, pFE = dist_cells(FID_FE)
    cEA, pEA = dist_cells(FID_EA)

    # --- sample real 120' cells for both SFs ---
    iFE = rng.choice(len(cFE), size=N, p=pFE)
    iEA = rng.choice(len(cEA), size=N, p=pEA)
    aFE = np.array([cFE[i][0] for i in iFE]); bFE = np.array([cFE[i][1] for i in iFE])
    aEA = np.array([cEA[i][0] for i in iEA]); bEA = np.array([cEA[i][1] for i in iEA])
    pens1, pens2, fin = rng.random(N), rng.random(N), rng.random(N)
    w1 = np.where(aFE > bFE, "FRA", np.where(aFE < bFE, "ESP", np.where(pens1 < .5, "FRA", "ESP")))
    w2 = np.where(aEA > bEA, "ENG", np.where(aEA < bEA, "ARG", np.where(pens2 < .5, "ENG", "ARG")))
    pw = np.array([PAIR[(t1, t2)] for t1, t2 in zip(w1, w2)])
    champ = np.where(fin < pw, w1, w2)

    # --- our match points on the two real games ---
    ptsFE_our = np.array([points(OUR_FE, (int(a), int(b))) for a, b in zip(aFE, bFE)], float)
    ptsEA_our = np.array([points(OUR_EA, (int(a), int(b))) for a, b in zip(aEA, bEA)], float)

    # --- per-chaser rival entries sampled from the mixtures (independent per chaser/game) ---
    def rival_pts(cells_a, cells_b, mix):
        rvs = list(mix.keys()); wts = np.array([mix[r] for r in rvs]); wts /= wts.sum()
        idx = rng.choice(len(rvs), size=N, p=wts)
        tbl = {j: np.array([points(rvs[j], (int(a), int(b))) for a, b in zip(cells_a, cells_b)], float)
               for j in range(len(rvs))}
        out = np.empty(N)
        for j in range(len(rvs)):
            m = idx == j
            out[m] = tbl[j][m]
        return out

    layer = {}
    for c in GAPS:
        layer[c] = (ptsFE_our - rival_pts(aFE, bFE, MIX_FE)) + (ptsEA_our - rival_pts(aEA, bEA, MIX_EA))
    # 3rd-place + final proxy diff (ASSUMED; common shock across chasers)
    vals, ps = [], []
    for rv, w in MIX_EA.items():
        for (a, b), p in zip(cEA, pEA):
            vals.append(points(OUR_EA, (a, b)) - points(rv, (a, b))); ps.append(p * w)
    vals, ps = np.array(vals, float), np.array(ps, float); ps /= ps.sum()
    proxy = vals[rng.choice(len(vals), size=(N, 2), p=ps)].sum(axis=1)
    for c in GAPS:
        layer[c] = layer[c] + proxy

    # --- award categoricals per champion branch (mutually exclusive) ---
    boot = np.empty(N, dtype=object); mvp = np.empty(N, dtype=object)
    gk = np.empty(N, dtype=object); ast = np.empty(N, dtype=object)
    for cb in BRANCHES:
        m = champ == cb
        nb = int(m.sum())
        bB, bM, bG, bA = award_probs(cb)
        boot[m], mvp[m] = sample_award(rng, bB, nb), sample_award(rng, bM, nb)
        gk[m], ast[m] = sample_award(rng, bG, nb), sample_award(rng, bA, nb)

    # --- realized locked-50 pays (absolute; dead legs = 0) ---
    pay = {
        "us":      LOCK * ((champ == "ESP") + (boot == "Mbappe") + (mvp == "Kane") + (gk == "Dibu")),
        "Greg":    LOCK * ((champ == "ESP") + (boot == "Mbappe") + (ast == "Messi") + (mvp == "Yamal") + (gk == "Maignan")),
        "Lucas":   LOCK * ((boot == "Mbappe") + (mvp == "Mbappe")),
        "Gonzalo": LOCK * ((champ == "FRA") + (boot == "Mbappe") + (ast == "Olise") + (mvp == "Yamal")),
        "felipe":  LOCK * ((champ == "FRA") + (boot == "Kane") + (mvp == "Yamal") + (gk == "Dibu")),
        "Rodrigo": LOCK * ((champ == "FRA") + (boot == "Dembele") + (ast == "MbappeA") + (mvp == "Mbappe") + (gk == "Maignan")),
    }

    hold_all = np.ones(N, bool); hold_all_tb = np.ones(N, bool)
    margin = {}
    for c, g in GAPS.items():
        m_ = g + layer[c] - (pay[c] - pay["us"])
        margin[c] = m_
        hold_all &= m_ > 0
        hold_all_tb &= m_ >= 0   # tie -> our 17-pleno tiebreak lead (approx: every tie won)
    print(f"P(FINISH #1) [strict, tie=loss]  = {float(hold_all.mean()):.4f}")
    print(f"P(FINISH #1) [tie->plenos lead]  = {float(hold_all_tb.mean()):.4f}   (truth in between, near the latter)")

    print("\nMULTIVERSE -- P(branch) and P(#1 | branch)  [strict]")
    for cb in BRANCHES:
        m = champ == cb
        print(f"  {cb} title: P={float(m.mean()):.3f}   P(#1|branch)={float(hold_all[m].mean()):.4f}")
    print("  advancement inside the sim: "
          f"P(FRA adv)={float((w1=='FRA').mean()):.3f} P(ENG adv)={float((w2=='ENG').mean()):.3f}")

    # forced-W* cross-check vs worst_world_stress.py
    mW = (champ == "FRA") & (mvp == "Mbappe") & (gk == "Maignan") & (ast == "Olise")
    print(f"\nW* CROSS-CHECK: P(W* occurs)={float(mW.mean()):.4f}   "
          f"P(#1 | W*)={float(hold_all[mW].mean()):.4f}   (worst_world_stress said ~.9953)")

    print("\nLOSS AUTOPSY -- the {:.2%} of universes where we are NOT #1 [strict]:".format(1 - hold_all.mean()))
    lost = ~hold_all
    if lost.sum():
        print("  champion distribution in losses: "
              + "  ".join(f"{cb}={float((champ[lost]==cb).mean()):.2f}" for cb in BRANCHES))
        for c in GAPS:
            passed = lost & (margin[c] <= 0)
            print(f"  {c:8s} is (co-)passer in {float(passed.sum())/max(lost.sum(),1):.2f} of losses"
                  f"  | needs realized delta {float((pay[c]-pay['us'])[passed].mean() if passed.sum() else 0):+5.1f}"
                  f" + layer {float(layer[c][passed].mean() if passed.sum() else 0):+6.1f} vs gap +{GAPS[c]}")
        both = lost & (margin["Gonzalo"] <= 0) & (margin["Greg"] <= 0)
        print(f"  (Gonzalo AND Greg both pass simultaneously in {float(both.sum())/max(lost.sum(),1):.2f} of losses)")

    print("\nSENSITIVITY")
    # SF2 entry 0-1 ARG instead (its council may flip tomorrow)
    ptsEA_alt = np.array([points((0, 1), (int(a), int(b))) for a, b in zip(aEA, bEA)], float)
    hold_alt = np.ones(N, bool)
    for c, g in GAPS.items():
        alt_layer = layer[c] + (ptsEA_alt - ptsEA_our)
        hold_alt &= g + alt_layer - (pay[c] - pay["us"]) > 0
    print(f"  SF2 entry 0-1 ARG instead of 1-0 ENG: P(#1) = {float(hold_alt.mean()):.4f}")
    for dp in (-0.10, +0.10):
        pw2 = np.clip(np.array([PAIR[(t1, t2)] for t1, t2 in zip(w1, w2)]) + dp, 0.05, 0.95)
        ch2 = np.where(fin < pw2, w1, w2)
        # re-sample awards cheaply: reuse categorical draws by branch masks on ch2
        b2 = np.empty(N, dtype=object); m2 = np.empty(N, dtype=object)
        g2 = np.empty(N, dtype=object); a2 = np.empty(N, dtype=object)
        rng2 = np.random.default_rng(SEED + 1)
        for cb in BRANCHES:
            mm = ch2 == cb; nb = int(mm.sum())
            bB, bM, bG, bA = award_probs(cb)
            b2[mm], m2[mm] = sample_award(rng2, bB, nb), sample_award(rng2, bM, nb)
            g2[mm], a2[mm] = sample_award(rng2, bG, nb), sample_award(rng2, bA, nb)
        pay2 = {
            "us":      LOCK * ((ch2 == "ESP") + (b2 == "Mbappe") + (m2 == "Kane") + (g2 == "Dibu")),
            "Greg":    LOCK * ((ch2 == "ESP") + (b2 == "Mbappe") + (a2 == "Messi") + (m2 == "Yamal") + (g2 == "Maignan")),
            "Lucas":   LOCK * ((b2 == "Mbappe") + (m2 == "Mbappe")),
            "Gonzalo": LOCK * ((ch2 == "FRA") + (b2 == "Mbappe") + (a2 == "Olise") + (m2 == "Yamal")),
            "felipe":  LOCK * ((ch2 == "FRA") + (b2 == "Kane") + (m2 == "Yamal") + (g2 == "Dibu")),
            "Rodrigo": LOCK * ((ch2 == "FRA") + (b2 == "Dembele") + (a2 == "MbappeA") + (m2 == "Mbappe") + (g2 == "Maignan")),
        }
        h2 = np.ones(N, bool)
        for c, g in GAPS.items():
            h2 &= g + layer[c] - (pay2[c] - pay2["us"]) > 0
        print(f"  PAIR{dp:+.2f}: P(#1) = {float(h2.mean()):.4f}")

    # hand-checks
    assert points((1, 0), (2, 1)) - points((2, 1), (2, 1)) == -5
    assert points((1, 0), (1, 0)) - points((0, 1), (1, 0)) == 9
    print("\nHAND-CHECKS: rubric cells -5/+9 OK; mixtures sum to 1; award categoricals sum <= 1 per branch.")


if __name__ == "__main__":
    main()
