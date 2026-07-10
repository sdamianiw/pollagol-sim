# -*- coding: utf-8 -*-
"""ESP-BEL lead-protection harness (2026-07-10, ADVISORY; I-3 clean, imported by nothing).
Objective per Sebas: WE CANNOT LOSE THE LEAD (+24/+25/+31, 60/20/10 payout) -> for each of OUR
candidates {1-0, 2-1} x each plausible RIVAL entry, enumerate the EXACT per-game point-differential
distribution over the frozen FULL120 score distribution (81 cells — exact enumeration, no MC needed).
Metrics: E[our-their], P(we gain), P(they gain), P(they gain >=5 = pleno-vs-nonpleno swing), worst case.
Rival picks are PRIORS (per-match picks hidden on pollaya)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

FID = "fca257de4583bd4bc592e8b2a8f24ad7"
SNAP = "data/snapshots/md5_2026-07-10T17-34-17Z.json"
OURS = [(1, 0), (2, 1)]
RIVAL = [(1, 0), (2, 0), (2, 1), (3, 1), (1, 1), (0, 1)]


def main():
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID)
    s = run_match(live)
    dist = ko_adjust(s["matrix"])["dist_120"]
    n = dist.shape[0]
    print("our-pick vs rival-pick : E[diff]  P(gain)  P(lose)  P(lose>=5)  worst")
    for ours in OURS:
        for rv in RIVAL:
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
            print(f"  {ours[0]}-{ours[1]} vs {rv[0]}-{rv[1]} : {e:+.4f}   {g:.3f}    {l:.3f}    {l5:.3f}      {worst:+d}")


if __name__ == "__main__":
    main()
