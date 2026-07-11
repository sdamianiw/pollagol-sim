# -*- coding: utf-8 -*-
"""NOR-ENG QF drift/face-off harness (2026-07-11, ADVISORY, imported by nothing; I-3 clean).
Pattern: council/outputs/esp_bel_qf/drift_esp_bel.py. CONTROL==LIVE gate before sweeps; B4 = run twice.
Race under audit: 1-2 (registered) vs 0-1 vs 0-2 (within-winner England) + Norway-side reachability."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import expected_points

FID = "e66e4478b739fa0657a7a11235e1fcee"
SNAP = "data/snapshots/md5_2026-07-11T19-03-03Z.json"
CANDS = [(1, 2), (0, 1), (0, 2), (2, 1), (1, 1), (2, 0), (1, 0)]


def synth(p_h, p_d, p_a, p_over, line=2.5):
    s = p_h + p_d + p_a
    p_h, p_d, p_a = p_h / s, p_d / s, p_a / s
    return {"id": FID, "home_team": "Norway", "away_team": "England",
            "commence_time": "2026-07-11T21:00:00Z",
            "bookmakers": [{"key": "synthetic", "title": "synthetic", "markets": [
                {"key": "h2h", "outcomes": [{"name": "Norway", "price": 1 / p_h},
                                            {"name": "England", "price": 1 / p_a},
                                            {"name": "Draw", "price": 1 / p_d}]},
                {"key": "totals", "outcomes": [{"name": "Over", "price": 1 / p_over, "point": line},
                                               {"name": "Under", "price": 1 / (1 - p_over), "point": line}]}]}]}


def ev(event, fmt):
    s = run_match(event, fmt=fmt)
    d = ko_adjust(s["matrix"])["dist_120"]
    evs = {c: expected_points(c, d) for c in CANDS}
    return s, evs, max(evs, key=evs.get), d


def main():
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID)
    sl, evl, al, dl = ev(live, "american")
    p = sl["strength"]["probs"]
    H, D, A = p["home"], p["draw"], p["away"]
    PO = sl["strength"]["p_over"]
    print(f"LIVE devig {H:.4f}/{D:.4f}/{A:.4f} p_over {PO:.4f} argmax={al} "
          f"1-2={evl[(1,2)]:.4f} 0-1={evl[(0,1)]:.4f} 0-2={evl[(0,2)]:.4f} 2-1nor={evl[(2,1)]:.4f}")
    sc, evc, ac, _ = ev(synth(H, D, A, PO), "decimal")
    dev = max(abs(evc[c] - evl[c]) for c in CANDS)
    print(f"CONTROL argmax={ac} max|dEV|={dev:.2e} -> {'PASS' if ac == al and dev < 1e-6 else 'FAIL'}")
    assert ac == al and dev < 1e-6

    grid = {"ENG-4pp": (H+.04, D, A-.04, PO), "ENG-2pp": (H+.02, D, A-.02, PO),
            "ENG+2pp": (H-.02, D, A+.02, PO), "ENG+4pp": (H-.04, D, A+.04, PO),
            "DRAW-2pp": (H*(1-(D-.02))/(H+A), D-.02, A*(1-(D-.02))/(H+A), PO),
            "DRAW+2pp": (H*(1-(D+.02))/(H+A), D+.02, A*(1-(D+.02))/(H+A), PO),
            "po-7pp": (H, D, A, PO-.07), "po-3.5": (H, D, A, PO-.035),
            "po+3.5": (H, D, A, PO+.035), "po+7pp": (H, D, A, PO+.07)}
    stable = 0
    for tag, (h, d_, a, po) in grid.items():
        _, evs, arg, _ = ev(synth(h, d_, a, po), "decimal")
        stable += (arg == al)
        print(f"  {tag:10s} argmax={arg}  gap(1-2 vs 0-1)={evs[(1,2)]-evs[(0,1)]:+.4f}")
    print(f"STABILITY: {stable}/{len(grid)} keep {al}")

    b = None  # scan DOWN: below which p_over does 0-1 take over from 1-2?
    for po in np.arange(0.40, 0.641, 0.01):
        _, evs, arg, _ = ev(synth(H, D, A, float(po)), "decimal")
        if arg == (1, 2) and b is None:
            b = float(po)
        print(f"  po={po:.2f} argmax={arg[0]}-{arg[1]} gap(1-2 vs 0-1)={evs[(1,2)]-evs[(0,1)]:+.4f}")
    if b is None:
        print("BOUNDARY: no flip in [0.40, 0.64]")
    elif abs(b - 0.40) < 1e-9:
        print("BOUNDARY: 1-2 already argmax at the scan floor -- true crossover <= 0.40 (unresolved)")
    else:
        print(f"BOUNDARY: 1-2 argmax from p_over >= {b:.2f}")

    # Norway-side reachability: how much would the market have to move toward Norway
    # before any NOR-win scoreline becomes argmax?
    hit = []
    for dn in np.arange(0.00, 0.211, 0.03):
        h, a = H + dn, A - dn
        if a <= 0.05:
            break
        _, evs, arg, _ = ev(synth(float(h), D, float(a), PO), "decimal")
        tag = f"NOR+{dn:.2f} (H={h:.2f}/A={a:.2f})"
        print(f"  {tag:26s} argmax={arg[0]}-{arg[1]}")
        if arg[0] > arg[1] and not hit:
            hit.append((float(h), float(a)))
    print(f"NOR-win argmax first at H={hit[0][0]:.2f}" if hit else "NOR-win argmax NOWHERE in scan (+21pp)")
    for c in [(1, 2), (0, 1), (0, 2), (2, 1)]:
        print(f"P(exact {c[0]}-{c[1]} @120') = {dl[c]:.4f}")


if __name__ == "__main__":
    main()
