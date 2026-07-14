# -*- coding: utf-8 -*-
"""SF1+SF2 joint lead-maximization harness (2026-07-12, ADVISORY; I-3 clean, imported by nothing).
Pattern: council/outputs/nor_eng_qf/lead_max_scenarios.py re-pointed at the two semifinals.
CONTROL regression = recompute the committed NOR-ENG headline pair (1-2 vs 0-1 = +0.1084 in
lead_max_scenarios_run_2026-07-11.txt) from its committed snapshot -- hard assert to 4dp.
Exact enumeration over frozen FULL120 distributions -- no MC, no randomness, B4 = run twice.
Field-entry mixtures are ASSUMED (per-match picks hidden); q swept. SF2 note: a Chilean pool plus the
Messi narrative can put the MAJORITY of the field on Argentina -- q swept to 0.75 there."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-12T12-14-09Z.json"
FID_FE = "f9aa13a662d1658e5a02cfc06d6a2d73"   # France vs Spain (home=FRA)
FID_EA = "ced22494ae0bbb8cc4f7108bf6f493df"   # England vs Argentina (home=ENG)

OURS_FE = [(1, 0), (2, 1), (0, 1)]
RIVAL_FE = [(1, 0), (2, 1), (1, 1), (0, 1), (1, 2), (2, 0)]
OURS_EA = [(1, 0), (0, 1), (2, 1)]
RIVAL_EA = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (0, 2)]

CHALK_FRA = {(1, 0): 0.35, (2, 1): 0.30, (2, 0): 0.15, (1, 1): 0.20}   # 1-1 kept: casual draw entries exist
CONTRA_ESP = {(0, 1): 0.55, (1, 2): 0.30, (0, 2): 0.15}
CHALK_ENG = {(1, 0): 0.40, (2, 1): 0.25, (1, 1): 0.20, (2, 0): 0.15}
CONTRA_ARG = {(0, 1): 0.55, (1, 2): 0.30, (0, 2): 0.15}


def dist_for(snap, fid):
    live = next(e for e in load_snapshot(snap)["events"] if e["id"] == fid)
    return ko_adjust(run_match(live)["matrix"])["dist_120"]


def pair_metrics(dist, ours, rv):
    n = dist.shape[0]
    e = g = l = l5 = 0.0
    worst = 99
    for a in range(n):
        for b in range(n):
            p = dist[a, b]
            if p <= 0:
                continue
            d = points(ours, (a, b)) - points(rv, (a, b))
            e += p * d
            g += p * (d > 0)
            l += p * (d < 0)
            l5 += p * (d <= -5)
            worst = min(worst, d)
    return e, g, l, l5, worst


def control_nor_eng():
    """CONTROL: the committed lead_max_scenarios_run_2026-07-11.txt prints '1-2 vs 0-1 : +0.1084'."""
    d = dist_for("data/snapshots/md5_2026-07-11T19-03-03Z.json", "e66e4478b739fa0657a7a11235e1fcee")
    e, *_ = pair_metrics(d, (1, 2), (0, 1))
    print(f"CONTROL NOR-ENG (1-2 vs 0-1) = {e:+.4f} (committed +0.1084) -> "
          f"{'PASS' if abs(e - 0.1084) < 5e-4 else 'FAIL'}")
    assert abs(e - 0.1084) < 5e-4


def single_game(tag, dist, ours_list, rival_list):
    print(f"\nBUCKET A1 -- {tag}: our-pick vs rival-pick")
    print("our vs rival : E[diff]  P(gain)  P(lose)  P(lose>=5)  worst")
    for ours in ours_list:
        for rv in rival_list:
            e, g, l, l5, worst = pair_metrics(dist, ours, rv)
            print(f"  {ours[0]}-{ours[1]} vs {rv[0]}-{rv[1]} : {e:+.4f}   {g:.3f}    {l:.3f}    {l5:.3f}      {worst:+d}")


def mixture(tag, dist, ours_list, chalk, contra, qs):
    print(f"\nBUCKET A2 -- {tag} vs FIELD MIXTURE, contrarian fraction q swept")
    for q in qs:
        mix = {}
        for k, w in chalk.items():
            mix[k] = mix.get(k, 0.0) + (1 - q) * w / sum(chalk.values())
        for k, w in contra.items():
            mix[k] = mix.get(k, 0.0) + q * w / sum(contra.values())
        row = []
        for ours in ours_list:
            e_mix = sum(w * pair_metrics(dist, ours, rv)[0] for rv, w in mix.items())
            row.append(f"{ours[0]}-{ours[1]}: {e_mix:+.4f}")
        print(f"  q={q:.2f}  E[our-field]  " + "   ".join(row))


def main():
    control_nor_eng()
    dFE = dist_for(SNAP, FID_FE)
    dEA = dist_for(SNAP, FID_EA)

    single_game("FRA-ESP SF1", dFE, OURS_FE, RIVAL_FE)
    mixture("FRA-ESP SF1", dFE, OURS_FE, CHALK_FRA, CONTRA_ESP, (0.0, 0.25, 0.50))
    single_game("ENG-ARG SF2", dEA, OURS_EA, RIVAL_EA)
    mixture("ENG-ARG SF2", dEA, OURS_EA, CHALK_ENG, CONTRA_ARG, (0.0, 0.25, 0.50, 0.75))

    print("\nBUCKET A3 -- JOINT two-game grid (SF1 x SF2), ours = (1-0, 1-0) [today's FULL120 argmaxes]")
    print("vs rival pair : E[2-game diff]  P(net lose)  P(net lose>=6)  worst")
    n1, n2 = dFE.shape[0], dEA.shape[0]
    for rvFE in [(1, 0), (2, 1), (1, 1), (0, 1)]:
        for rvEA in [(1, 0), (0, 1), (1, 1)]:
            e = pl = pl6 = 0.0
            worst = 99
            for a in range(n1):
                for b in range(n1):
                    p1 = dFE[a, b]
                    if p1 <= 0:
                        continue
                    d1 = points((1, 0), (a, b)) - points(rvFE, (a, b))
                    for c in range(n2):
                        for d_ in range(n2):
                            p2 = dEA[c, d_]
                            if p2 <= 0:
                                continue
                            d2 = points((1, 0), (c, d_)) - points(rvEA, (c, d_))
                            p = p1 * p2
                            t = d1 + d2
                            e += p * t
                            pl += p * (t < 0)
                            pl6 += p * (t <= -6)
                            worst = min(worst, t)
            print(f"  FE {rvFE[0]}-{rvFE[1]} + EA {rvEA[0]}-{rvEA[1]} : {e:+.4f}    {pl:.3f}      {pl6:.3f}       {worst:+d}")

    print("\nBUCKET B0 -- advancement probabilities from the frozen FULL120 dists (pens split 50/50)")
    for name, dist, hn, an in (("FRA-ESP", dFE, "France", "Spain"), ("ENG-ARG", dEA, "England", "Argentina")):
        ph = pa = pd_ = 0.0
        n = dist.shape[0]
        for a in range(n):
            for b in range(n):
                p = dist[a, b]
                if a > b:
                    ph += p
                elif a < b:
                    pa += p
                else:
                    pd_ += p
        print(f"  {name}: P({hn} win120)={ph:.4f} P({an} win120)={pa:.4f} P(level@120->pens)={pd_:.4f}"
              f"  -> P(adv {hn})={ph + pd_ / 2:.4f}")


if __name__ == "__main__":
    main()
