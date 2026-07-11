# -*- coding: utf-8 -*-
"""NOR-ENG + ARG-SUI joint lead-maximization harness (2026-07-11, ADVISORY; I-3 clean, imported by nothing).
Pattern: council/outputs/esp_bel_qf/lead_protect_esp_bel.py extended to (a) a rival-entry MIXTURE with a
contrarian fraction q (trailing chasers variance-hunt; picks are HIDDEN so rivals cannot react to ours),
(b) the joint two-fixture product grid (NOR-ENG x ARG-SUI), (c) CONTROL regression = the ESP-BEL single-
fixture table reproduced from its committed snapshot (must match the committed verdict numbers).
Objective per Sebas: MAXIMIZE THE LEAD (+29/+30 over Greg/Lucas, 60/20/10, tiebreak = most plenos).
Exact enumeration over frozen FULL120 distributions -- no MC, no randomness, B4 = run twice."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = "data/snapshots/md5_2026-07-11T19-03-03Z.json"
FID_NE = "e66e4478b739fa0657a7a11235e1fcee"   # Norway vs England (home=NOR)
FID_AS = "200d9cd5eda092c7eb778cc104cd2fd2"   # Argentina vs Switzerland (home=ARG)

OURS_NE = [(1, 2), (0, 1), (0, 2), (2, 1)]     # candidates for tonight (2-1 = Norway-side test)
RIVAL_NE = [(1, 2), (0, 1), (0, 2), (1, 1), (2, 1), (1, 0), (2, 2)]
OUR_AS = (1, 0)
RIVAL_AS = [(1, 0), (2, 0), (2, 1), (1, 1), (0, 1)]

# Field-entry model for NOR-ENG (ASSUMED weights -- per-match picks hidden; anchored on "mostly-chalk
# field" from CLAUDE.md + the modal-heavy entries observed on past boards). ENG-side chalk vs NOR-side
# contrarian mass q is swept; within each side, weights renormalize.
CHALK_ENG = {(1, 2): 0.40, (0, 1): 0.30, (0, 2): 0.20, (1, 1): 0.10}   # 1-1 kept: casual draw entries exist
CONTRA_NOR = {(2, 1): 0.60, (1, 0): 0.25, (2, 2): 0.15}


def dist_for(fid):
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
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


def control_esp_bel():
    """CONTROL regression: reproduce the committed ESP-BEL table (same snapshot, same pairs)."""
    live = next(e for e in load_snapshot("data/snapshots/md5_2026-07-10T17-34-17Z.json")["events"]
                if e["id"] == "fca257de4583bd4bc592e8b2a8f24ad7")
    dist = ko_adjust(run_match(live)["matrix"])["dist_120"]
    print("CONTROL (ESP-BEL committed harness, first row must equal the committed output):")
    for ours in [(1, 0), (2, 1)]:
        for rv in [(1, 0), (2, 0), (2, 1), (3, 1), (1, 1), (0, 1)]:
            e, g, l, l5, worst = pair_metrics(dist, ours, rv)
            print(f"  {ours[0]}-{ours[1]} vs {rv[0]}-{rv[1]} : {e:+.4f}   {g:.3f}    {l:.3f}    {l5:.3f}      {worst:+d}")


def main():
    control_esp_bel()
    dNE = dist_for(FID_NE)
    dAS = dist_for(FID_AS)

    print("\nBUCKET A1 -- NOR-ENG single game: our-pick vs rival-pick")
    print("our vs rival : E[diff]  P(gain)  P(lose)  P(lose>=5)  worst")
    for ours in OURS_NE:
        for rv in RIVAL_NE:
            e, g, l, l5, worst = pair_metrics(dNE, ours, rv)
            print(f"  {ours[0]}-{ours[1]} vs {rv[0]}-{rv[1]} : {e:+.4f}   {g:.3f}    {l:.3f}    {l5:.3f}      {worst:+d}")

    print("\nBUCKET A2 -- NOR-ENG vs FIELD MIXTURE, contrarian fraction q (NOR-side mass) swept")
    print("q = P(a given chaser enters a Norway-side scoreline); entries within each side renormalized")
    for q in (0.0, 0.25, 0.50):
        mix = {}
        for k, w in CHALK_ENG.items():
            mix[k] = mix.get(k, 0.0) + (1 - q) * w / sum(CHALK_ENG.values())
        for k, w in CONTRA_NOR.items():
            mix[k] = mix.get(k, 0.0) + q * w / sum(CONTRA_NOR.values())
        row = []
        for ours in OURS_NE:
            e_mix = sum(w * pair_metrics(dNE, ours, rv)[0] for rv, w in mix.items())
            row.append(f"{ours[0]}-{ours[1]}: {e_mix:+.4f}")
        print(f"  q={q:.2f}  E[our-field]  " + "   ".join(row))

    print("\nBUCKET A3 -- JOINT two-game grid (NOR-ENG x ARG-SUI), ours = (1-2, 1-0) [registered]")
    print("vs rival pair : E[2-game diff]  P(net lose)  P(net lose>=6)  worst")
    n1, n2 = dNE.shape[0], dAS.shape[0]
    for rvNE in [(1, 2), (0, 1), (1, 1), (2, 1)]:
        for rvAS in [(1, 0), (2, 1), (1, 1)]:
            e = pl = pl6 = 0.0
            worst = 99
            for a in range(n1):
                for b in range(n1):
                    p1 = dNE[a, b]
                    if p1 <= 0:
                        continue
                    d1 = points((1, 2), (a, b)) - points(rvNE, (a, b))
                    for c in range(n2):
                        for d_ in range(n2):
                            p2 = dAS[c, d_]
                            if p2 <= 0:
                                continue
                            d2 = points(OUR_AS, (c, d_)) - points(rvAS, (c, d_))
                            p = p1 * p2
                            t = d1 + d2
                            e += p * t
                            pl += p * (t < 0)
                            pl6 += p * (t <= -6)
                            worst = min(worst, t)
            print(f"  NE {rvNE[0]}-{rvNE[1]} + AS {rvAS[0]}-{rvAS[1]} : {e:+.4f}    {pl:.3f}      {pl6:.3f}       {worst:+d}")

    print("\nBUCKET B0 -- advancement probabilities from the frozen FULL120 dists (pens split 50/50)")
    for name, dist, hn, an in (("NOR-ENG", dNE, "Norway", "England"), ("ARG-SUI", dAS, "Argentina", "Switzerland")):
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
              f"  -> P(adv {an})={pa + pd_ / 2:.4f}")


if __name__ == "__main__":
    main()
