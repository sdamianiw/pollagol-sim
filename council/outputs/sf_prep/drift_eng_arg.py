# -*- coding: utf-8 -*-
"""ENG-ARG SF2 drift/face-off harness (2026-07-12, ADVISORY, imported by nothing; I-3 clean).
Pattern: council/outputs/nor_eng_qf/drift_nor_eng.py. CONTROL==LIVE gate before sweeps; B4 = run twice.
Race under audit: 1-0 (ENG, argmax) vs 0-1 (ARG -- the flip DIRECTION on a .373/.306 near-coin-flip)
+ 2-1 (totals-up shape). First baseline for this fixture (no prior snapshot contains it)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import expected_points

FID = "ced22494ae0bbb8cc4f7108bf6f493df"
SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-12T12-14-09Z.json"
CANDS = [(1, 0), (0, 1), (2, 1), (1, 2), (1, 1), (2, 0), (0, 2)]


def synth(p_h, p_d, p_a, p_over, line=2.5):
    s = p_h + p_d + p_a
    p_h, p_d, p_a = p_h / s, p_d / s, p_a / s
    return {"id": FID, "home_team": "England", "away_team": "Argentina",
            "commence_time": "2026-07-15T19:00:00Z",
            "bookmakers": [{"key": "synthetic", "title": "synthetic", "markets": [
                {"key": "h2h", "outcomes": [{"name": "England", "price": 1 / p_h},
                                            {"name": "Argentina", "price": 1 / p_a},
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
          f"1-0={evl[(1,0)]:.4f} 0-1={evl[(0,1)]:.4f} 2-1={evl[(2,1)]:.4f} 1-2={evl[(1,2)]:.4f}")
    sc, evc, ac, _ = ev(synth(H, D, A, PO), "decimal")
    dev = max(abs(evc[c] - evl[c]) for c in CANDS)
    print(f"CONTROL argmax={ac} max|dEV|={dev:.2e} -> {'PASS' if ac == al and dev < 1e-6 else 'FAIL'}")
    assert ac == al and dev < 1e-6

    # focal team ENGLAND is the HOME side here (template's focal was away) -> signs track H, not A
    grid = {"ENG-4pp": (H-.04, D, A+.04, PO), "ENG-2pp": (H-.02, D, A+.02, PO),
            "ENG+2pp": (H+.02, D, A-.02, PO), "ENG+4pp": (H+.04, D, A-.04, PO),
            "DRAW-2pp": (H*(1-(D-.02))/(H+A), D-.02, A*(1-(D-.02))/(H+A), PO),
            "DRAW+2pp": (H*(1-(D+.02))/(H+A), D+.02, A*(1-(D+.02))/(H+A), PO),
            "po-7pp": (H, D, A, PO-.07), "po-3.5": (H, D, A, PO-.035),
            "po+3.5": (H, D, A, PO+.035), "po+7pp": (H, D, A, PO+.07)}
    stable = 0
    for tag, (h, d_, a, po) in grid.items():
        _, evs, arg, _ = ev(synth(h, d_, a, po), "decimal")
        stable += (arg == al)
        print(f"  {tag:10s} argmax={arg}  gap(1-0 vs 0-1)={evs[(1,0)]-evs[(0,1)]:+.4f}")
    print(f"STABILITY: {stable}/{len(grid)} keep {al}")

    # THE winner-flip boundary: shift mass ENG -> ARG; at what split does 0-1 take over from 1-0?
    b = None
    for dn in np.arange(0.00, 0.151, 0.01):
        h, a = H - dn, A + dn
        _, evs, arg, _ = ev(synth(float(h), D, float(a), PO), "decimal")
        if arg[1] > arg[0] and b is None:
            b = (float(h), float(a))
        print(f"  ARG+{dn:.2f} (H={h:.2f}/A={a:.2f}) argmax={arg[0]}-{arg[1]} "
              f"gap(1-0 vs 0-1)={evs[(1,0)]-evs[(0,1)]:+.4f}")
    if b is None:
        print("BOUNDARY: no ARG-side argmax in scan (ARG +15pp)")
    elif abs(b[0] - H) < 1e-9:
        print("BOUNDARY: ARG-side already argmax at the live board (unresolved floor)")
    else:
        print(f"BOUNDARY: ARG-side (0-1) argmax from H<={b[0]:.2f}/A>={b[1]:.2f} devig")

    # Totals boundary: above which p_over does 2-1 overtake 1-0?
    b2 = None
    for po in np.arange(0.38, 0.621, 0.01):
        _, evs, arg, _ = ev(synth(H, D, A, float(po)), "decimal")
        if arg == (2, 1) and b2 is None:
            b2 = float(po)
        print(f"  po={po:.2f} argmax={arg[0]}-{arg[1]} gap(1-0 vs 2-1)={evs[(1,0)]-evs[(2,1)]:+.4f}")
    if b2 is None:
        print("BOUNDARY: 2-1 never argmax in [0.38, 0.62]")
    elif abs(b2 - 0.38) < 1e-9:
        print("BOUNDARY: 2-1 already argmax at the scan floor -- true crossover <= 0.38 (unresolved)")
    else:
        print(f"BOUNDARY: 2-1 argmax from p_over >= {b2:.2f}")
    for c in [(1, 0), (0, 1), (2, 1), (1, 2), (1, 1)]:
        print(f"P(exact {c[0]}-{c[1]} @120') = {dl[c]:.4f}")


if __name__ == "__main__":
    main()
