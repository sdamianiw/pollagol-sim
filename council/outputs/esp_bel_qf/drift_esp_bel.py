# -*- coding: utf-8 -*-
"""ESP-BEL QF drift/face-off harness (2026-07-10, ADVISORY, imported by nothing; I-3 clean).
Pattern: council/outputs/fra_mar_qf/drift_fra_mar.py. CONTROL==LIVE gate before sweeps; B4 = run twice."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import expected_points

FID = "fca257de4583bd4bc592e8b2a8f24ad7"
SNAP = "data/snapshots/md5_2026-07-10T17-34-17Z.json"
CANDS = [(1, 0), (2, 0), (2, 1), (3, 1), (1, 1), (0, 1)]


def synth(p_h, p_d, p_a, p_over, line=2.5):
    s = p_h + p_d + p_a
    p_h, p_d, p_a = p_h / s, p_d / s, p_a / s
    return {"id": FID, "home_team": "Spain", "away_team": "Belgium",
            "commence_time": "2026-07-10T19:00:00Z",
            "bookmakers": [{"key": "synthetic", "title": "synthetic", "markets": [
                {"key": "h2h", "outcomes": [{"name": "Spain", "price": 1 / p_h},
                                            {"name": "Belgium", "price": 1 / p_a},
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
          f"1-0={evl[(1,0)]:.4f} 2-1={evl[(2,1)]:.4f} 2-0={evl[(2,0)]:.4f}")
    sc, evc, ac, _ = ev(synth(H, D, A, PO), "decimal")
    dev = max(abs(evc[c] - evl[c]) for c in CANDS)
    print(f"CONTROL argmax={ac} max|dEV|={dev:.2e} -> {'PASS' if ac == al and dev < 1e-6 else 'FAIL'}")
    assert ac == al and dev < 1e-6

    grid = {"ESP-4pp": (H-.04, D, A+.04, PO), "ESP-2pp": (H-.02, D, A+.02, PO),
            "ESP+2pp": (H+.02, D, A-.02, PO), "ESP+4pp": (H+.04, D, A-.04, PO),
            "DRAW-2pp": (H*(1-(D-.02))/(H+A), D-.02, A*(1-(D-.02))/(H+A), PO),
            "DRAW+2pp": (H*(1-(D+.02))/(H+A), D+.02, A*(1-(D+.02))/(H+A), PO),
            "po-7pp": (H, D, A, PO-.07), "po-3.5": (H, D, A, PO-.035),
            "po+3.5": (H, D, A, PO+.035), "po+7pp": (H, D, A, PO+.07)}
    stable = 0
    for tag, (h, d_, a, po) in grid.items():
        _, evs, arg, _ = ev(synth(h, d_, a, po), "decimal")
        stable += (arg == al)
        print(f"  {tag:10s} argmax={arg}  gap(2-1 vs 1-0)={evs[(2,1)]-evs[(1,0)]:+.4f}")
    print(f"STABILITY: {stable}/{len(grid)} keep {al}")

    b = None
    for po in np.arange(0.44, 0.641, 0.01):
        _, evs, arg, _ = ev(synth(H, D, A, float(po)), "decimal")
        if arg == (2, 1) and b is None:
            b = float(po)
        print(f"  po={po:.2f} argmax={arg[0]}-{arg[1]} gap={evs[(2,1)]-evs[(1,0)]:+.4f}")
    print(f"BOUNDARY: 2-1 argmax from p_over >= {b:.2f}" if b is not None
          else "BOUNDARY: no flip in [0.44, 0.64]")

    hit = [(h, po) for po in np.arange(0.44, 0.701, 0.02) for h in np.arange(0.55, 0.701, 0.03)
           if 1-h-D > 0.03 and ev(synth(float(h), D, float(1-h-D), float(po)), "decimal")[2] == (2, 0)]
    print("2-0 argmax NOWHERE in scan" if not hit else f"2-0 wins at {hit}")
    for c in [(1, 0), (2, 1), (2, 0)]:
        print(f"P(exact {c[0]}-{c[1]} @120') = {dl[c]:.4f}")


if __name__ == "__main__":
    main()
