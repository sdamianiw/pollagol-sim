"""ANNEX V (skeleton) - per-game EV-cost of the lambda variance-dial, measured on the REAL DC matrices.

Replaces the auditor's stylized per-game -0.4 with the ACTUAL E[pts] sacrificed per fixture across a lambda
sweep, using run_matchday's POST-context matrix (the exact object the live EV-optimizer picks from). It is
DETERMINISTIC and read-only on a snapshot, and FIRES NOTHING (no pick is entered). The deferred placement-MC
weighs these costs against the P(top-3) gain; that, the H1-H4 tests and the activation gate are post-MD3
(F35 H4-fixed, F34 >=2-3 matchdays of standings_log).

Run:  python -m evals.variance_ev_cost [snapshot.json]   (default = the Jun-14 MD1 snapshot)
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.ingest import load_snapshot
from src.run_matchday import run_match, LineGuardStop
from src import variance_select as vs
from src.optimizer import optimize, expected_points

LAMS = [0.5, 1.0, 2.0]
DEFAULT_SNAP = os.path.join(ROOT, "data", "snapshots", "md1_2026-06-14T12-14-52Z.json")


def fixture_rows(snap: dict) -> list[dict]:
    rows = []
    for ev in snap.get("events", []):
        try:
            summ = run_match(ev)
        except LineGuardStop:
            continue                                            # non-x.5 -> skip (the live guard's domain)
        adj = summ["matrix"]
        ev_pick = optimize(adj)["pick"]
        ev_ev = expected_points(ev_pick, adj)
        row = {"fixture": f"{ev['home_team']} v {ev['away_team']}", "ev_pick": ev_pick, "ev_ev": ev_ev,
               "lams": {}}
        for lam in LAMS:
            sel = vs.select(adj, lam)
            row["lams"][lam] = {"pick": sel["pick"], "cost": ev_ev - sel["ev"], "moved": sel["pick"] != ev_pick}
        rows.append(row)
    return rows


def _fmt(p):
    return f"{p[0]}-{p[1]}"


def main() -> int:
    snap_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SNAP
    rows = fixture_rows(load_snapshot(snap_path))
    print("=" * 100)
    print(f"ANNEX V - per-game EV-cost of the variance dial (real matrices)   snapshot={os.path.basename(snap_path)}")
    print(f"  cost = E[pts](EV-argmax) - E[pts](variance pick) >= 0   (lambda sweep {LAMS})")
    print("=" * 100)
    hdr = f"  {'fixture':<26} {'EV pick':>8}" + "".join(f"  | l={l:<4} pick  cost" for l in LAMS)
    print(hdr)
    print("-" * 100)
    agg = {l: [] for l in LAMS}
    moved = {l: 0 for l in LAMS}
    for r in rows:
        line = f"  {r['fixture']:<26} {_fmt(r['ev_pick']):>8}"
        for l in LAMS:
            c = r["lams"][l]
            agg[l].append(c["cost"])
            moved[l] += 1 if c["moved"] else 0
            flag = "*" if c["moved"] else " "
            line += f"  | {_fmt(c['pick']):>5}{flag} {c['cost']:>5.3f}"
        print(line)
    print("-" * 100)
    print(f"  fixtures: {len(rows)}   (* = dial moved off the EV-argmax)")
    for l in LAMS:
        mean = sum(agg[l]) / len(agg[l]) if agg[l] else 0.0
        mx = max(agg[l]) if agg[l] else 0.0
        print(f"  lambda={l}:  mean EV-cost/game = {mean:+.4f} pts   max = {mx:.4f}   moved {moved[l]}/{len(rows)}")
    print("=" * 100)
    print("NOTE: cost only; the P(top-3) GAIN is the deferred placement-MC (post-MD3). BUILD != FIRE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
