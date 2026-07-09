# -*- coding: utf-8 -*-
"""FRA-MAR QF drift/face-off harness (2026-07-09, scratchpad, ADVISORY — no repo write, I-3 clean).

Rebuilds the documented pattern (drift_arg_sui.py / hedge_por_esp.py, prior sessions): synthetic
single-book vig-free events at EXACT devig targets -> frozen run_match -> ko_adjust FULL120 -> argmax +
1-0 vs 2-1 face-off gap. CONTROL (targets == live devig/p_over) must reproduce the live argmax/EV
before any sweep is read (B4: run twice, byte-identical stdout).

Sweeps: fav-axis ±4pp (H±d, A∓d, D fixed) · draw ±2pp (D±d, H/A pro-rata) · p_over ±7pp ·
p_over fine-scan for the 1-0 <-> 2-1 flip boundary · joint stress corner.
"""
import io
import sys
import numpy as np

sys.path.insert(0, r"C:\Users\Sdami\Projects\Pollagol SIM")
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import expected_points

SNAP = r"C:\Users\Sdami\Projects\Pollagol SIM\data\snapshots\md5_2026-07-09T17-23-16Z.json"
FID = "b6e926d7f026782b9cab2fa02b823d92"
CANDS = [(1, 0), (2, 0), (2, 1), (3, 1), (1, 1), (0, 1)]


def synth_event(p_h, p_d, p_a, p_over, line=2.5):
    """Single vig-free book at exact target probabilities (decimal odds = 1/p)."""
    s = p_h + p_d + p_a
    p_h, p_d, p_a = p_h / s, p_d / s, p_a / s          # renorm guard (sweeps keep sum=1 anyway)
    return {
        "id": FID, "home_team": "France", "away_team": "Morocco",
        "commence_time": "2026-07-09T20:00:00Z",
        "bookmakers": [{
            "key": "synthetic", "title": "synthetic",
            "markets": [
                {"key": "h2h", "outcomes": [
                    {"name": "France", "price": 1.0 / p_h},
                    {"name": "Morocco", "price": 1.0 / p_a},
                    {"name": "Draw", "price": 1.0 / p_d},
                ]},
                {"key": "totals", "outcomes": [
                    {"name": "Over", "price": 1.0 / p_over, "point": line},
                    {"name": "Under", "price": 1.0 / (1.0 - p_over), "point": line},
                ]},
            ],
        }],
    }


def ko_eval(event, fmt):
    s = run_match(event, fmt=fmt)
    ko = ko_adjust(s["matrix"])                         # FULL120 default
    dist = ko["dist_120"]
    evs = {c: expected_points(c, dist) for c in CANDS}
    argmax = max(evs, key=evs.get)
    return s, ko, evs, argmax


def fmt_row(tag, evs, argmax):
    gap = evs[(1, 0)] - evs[(2, 1)]
    tops = "  ".join(f"{a}-{b}={evs[(a,b)]:.4f}" for a, b in CANDS[:4])
    return (f"{tag:34s} argmax={argmax[0]}-{argmax[1]}  gap(1-0 vs 2-1)={gap:+.4f}  {tops}")


def main():
    out = io.StringIO()
    live_event = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID)
    s_live, ko_live, evs_live, arg_live = ko_eval(live_event, "american")
    pv = s_live["strength"]["probs"]
    H, D, A = pv["home"], pv["draw"], pv["away"]
    PO = s_live["strength"]["p_over"]
    print(f"LIVE  devig H/D/A={H:.4f}/{D:.4f}/{A:.4f}  p_over={PO:.4f}", file=out)
    print(fmt_row("LIVE (25-book snapshot)", evs_live, arg_live), file=out)

    s_c, ko_c, evs_c, arg_c = ko_eval(synth_event(H, D, A, PO), "decimal")
    dev_max = max(abs(evs_c[c] - evs_live[c]) for c in CANDS)
    ctrl = "PASS" if (arg_c == arg_live and dev_max < 1e-6) else "FAIL"
    print(fmt_row("CONTROL (synth @ live targets)", evs_c, arg_c), file=out)
    print(f"CONTROL==LIVE: {ctrl}  (max |dEV| = {dev_max:.2e})", file=out)
    if ctrl == "FAIL":
        print(out.getvalue())
        sys.exit("CONTROL FAILED - sweeps not trustworthy")

    n_stable, n_tot = 0, 0
    print("\n-- fav-axis sweep (FRA +/-4pp, mass vs MAR, draw fixed)", file=out)
    for d in (-0.04, -0.02, 0.02, 0.04):
        _, _, evs, arg = ko_eval(synth_event(H + d, D, A - d, PO), "decimal")
        n_tot += 1; n_stable += (arg == arg_live)
        print(fmt_row(f"  FRA{d:+.2f}", evs, arg), file=out)

    print("-- draw sweep (+/-2pp, H/A pro-rata)", file=out)
    for d in (-0.02, 0.02):
        k = (1.0 - (D + d)) / (H + A)
        _, _, evs, arg = ko_eval(synth_event(H * k, D + d, A * k, PO), "decimal")
        n_tot += 1; n_stable += (arg == arg_live)
        print(fmt_row(f"  DRAW{d:+.2f}", evs, arg), file=out)

    print("-- p_over sweep (+/-7pp)", file=out)
    for d in (-0.07, -0.035, 0.035, 0.07):
        _, _, evs, arg = ko_eval(synth_event(H, D, A, PO + d), "decimal")
        n_tot += 1; n_stable += (arg == arg_live)
        print(fmt_row(f"  p_over{d:+.3f} ({PO+d:.3f})", evs, arg), file=out)

    print(f"\nDRIFT STABILITY: {n_stable}/{n_tot} grid points keep argmax "
          f"{arg_live[0]}-{arg_live[1]}", file=out)

    print("\n-- p_over fine-scan for the 1-0 <-> 2-1 flip boundary (live devig held)", file=out)
    boundary = None
    for po in np.arange(0.40, 0.701, 0.01):
        _, _, evs, arg = ko_eval(synth_event(H, D, A, float(po)), "decimal")
        flag = " <-- FLIP" if arg != arg_live and boundary is None else ""
        if arg != arg_live and boundary is None:
            boundary = float(po)
        print(f"  p_over={po:.2f}  argmax={arg[0]}-{arg[1]}  gap={evs[(1,0)]-evs[(2,1)]:+.4f}{flag}",
              file=out)
    print(f"FLIP BOUNDARY: p_over >= {boundary:.2f}" if boundary is not None
          else "FLIP BOUNDARY: none in [0.40, 0.70]", file=out)

    print("\n-- joint stress corner (FRA-4pp AND p_over+7pp, the 2-1-friendliest reachable world)",
          file=out)
    _, _, evs, arg = ko_eval(synth_event(H - 0.04, D, A + 0.04, PO + 0.07), "decimal")
    print(fmt_row("  FRA-0.04 & p_over+0.07", evs, arg), file=out)

    print(out.getvalue())


if __name__ == "__main__":
    main()
