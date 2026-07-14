# -*- coding: utf-8 -*-
"""JOINT worst-world stress harness (2026-07-14, ADVISORY; I-3 clean, imported by nothing).
Answers Sebas's premiaciones question DETERMINISTICALLY: in W* = {champion=FRANCE, MVP=Mbappe,
GK=Maignan, AST=Olise} with ALL those legs PAYING simultaneously (not expectation-weighted like
endgame_branches_sf.py), what is the exact locked-50 settlement per chaser, the required match-layer
margin, P(hold #1) under the FORCED world, and does tonight's EV pick (France 1-0) keep its logic?
Two Boot sub-cases (the 5th award, unspecified in W*): A = Mbappe wins the Boot (8==8 tie live; a
France-title run favors him) -> OUR Mbappe-scorer leg pays; B = Boot goes elsewhere (Messi).
Ownership = pool/locked_ownership_2026-06-28.md (OBSERVED). Gaps = 2026-07-12 board (VERIFIED).
Payout LOCK=10/leg. Seed-42 MC reuses the q=.25 mixture proxy of endgame_branches_sf.game_diff_dist;
tonight's game additionally CONDITIONED on a France win (W* requires it). B4 = run twice."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points, expected_points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-14T16-52-55Z.json"
FID_FE = "f9aa13a662d1658e5a02cfc06d6a2d73"   # France vs Spain SF1 (home=FRA)
FID_EA = "ced22494ae0bbb8cc4f7108bf6f493df"   # England vs Argentina SF2 (home=ENG)
GAPS = {"Greg": 28, "Gonzalo": 35, "felipe": 39, "Lucas": 39, "Rodrigo": 50}
LOCK = 10.0
SEED = 42
N_MC = 200_000
N_GAMES_AFTER_TONIGHT = 3   # SF2, 3rd place, final (tonight handled conditionally on FRA win)

# W* settlement, hand-derived from the ownership table (each entry = legs that PAY in W*):
#   us:      ESPx / Boot(A: Mbappe PAYS, B: x) / Bruno DEAD / Kane-MVP x (Mbappe) / Dibu x (Maignan)
#   Greg:    ESPx / Boot A pays (common w/ us) / Messi-AST x (Olise) / Yamal-MVP x / MAIGNAN PAYS
#   Lucas:   POR DEAD / Boot A pays / Bruno DEAD / MBAPPE-MVP PAYS / Costa DEAD
#   Gonzalo: FRA PAYS / Boot A pays / OLISE-AST PAYS / Yamal-MVP x / Alisson DEAD
#   felipe:  FRA PAYS / Kane-scorer x (both cases; a Kane-Boot world is NOT W*) / Bruno DEAD /
#            Yamal-MVP x / Dibu x (Maignan)
#   Rodrigo: FRA PAYS / Dembele x / Mbappe-AST x (Olise) / MBAPPE-MVP PAYS / MAIGNAN PAYS
SETTLE = {  # hits (count of paying legs) per player, per Boot case
    "A": {"us": 1, "Greg": 2, "Lucas": 2, "Gonzalo": 3, "felipe": 1, "Rodrigo": 3},
    "B": {"us": 0, "Greg": 1, "Lucas": 1, "Gonzalo": 2, "felipe": 1, "Rodrigo": 3},
}


def dist_for(fid):
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
    return ko_adjust(run_match(live)["matrix"])["dist_120"]


def cond_entry_ev(dist, entry, region):
    """E[points(entry)| region of 120' outcomes]: region in {'H','A','D'} (home win/away win/level)."""
    n = dist.shape[0]
    num = den = 0.0
    for a in range(n):
        for b in range(n):
            p = dist[a, b]
            if p <= 0:
                continue
            r = "H" if a > b else ("A" if a < b else "D")
            if r != region:
                continue
            num += p * points(entry, (a, b))
            den += p
    return num / den, den


def diff_dist(dist, ours, mix, cond=None):
    """(our - mixture-field) per-game swing distribution; optional conditioning region."""
    n = dist.shape[0]
    vals, ps = [], []
    for rv, w in mix.items():
        for a in range(n):
            for b in range(n):
                p = dist[a, b] * w
                if p <= 0:
                    continue
                r = "H" if a > b else ("A" if a < b else "D")
                if cond and r != cond:
                    continue
                vals.append(points(ours, (a, b)) - points(rv, (a, b)))
                ps.append(p)
    vals, ps = np.array(vals, float), np.array(ps, float)
    ps /= ps.sum()
    return vals, ps


# q=.25 mixtures (same ASSUMED weights as lead_max_sf.py / endgame_branches_sf.py)
MIX_FE = {(1, 0): 0.2625, (2, 1): 0.225, (2, 0): 0.1125, (1, 1): 0.15,
          (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
MIX_EA = {(1, 0): 0.30, (2, 1): 0.1875, (1, 1): 0.15, (2, 0): 0.1125,
          (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}


def main():
    dFE, dEA = dist_for(FID_FE), dist_for(FID_EA)
    assert abs(sum(MIX_FE.values()) - 1.0) < 1e-9 and abs(sum(MIX_EA.values()) - 1.0) < 1e-9

    print("W* = {champ FRA, MVP Mbappe, GK Maignan, AST Olise} -- ALL PAY (joint extreme, not expectation)")
    print("\nPART 1 -- deterministic locked-50 settlement (LOCK=10/leg) + required match-layer margin")
    for case in ("A", "B"):
        tag = "Boot=Mbappe (our leg PAYS)" if case == "A" else "Boot=other/Messi (our leg fails)"
        print(f"  case {case} [{tag}]:")
        us_pay = SETTLE[case]["us"] * LOCK
        for c, g in GAPS.items():
            delta = SETTLE[case][c] * LOCK - us_pay
            print(f"    {c:8s} settle={SETTLE[case][c]*LOCK:4.0f} vs us {us_pay:3.0f} -> delta {delta:+5.0f}"
                  f"  | gap +{g} -> chaser needs > {g - delta:+.0f} from the match layer to PASS us")
    worst = {c: max(SETTLE[k][c] * LOCK - SETTLE[k]["us"] * LOCK for k in ("A", "B")) for c in GAPS}
    binding = min(GAPS, key=lambda c: GAPS[c] - worst[c])
    print(f"  BINDING CHASER: {binding} (margin {GAPS[binding] - worst[binding]:+.0f} after worst-case settlement)")

    print("\nPART 2 -- does tonight's entry keep its logic INSIDE W*? (conditional harvest, deterministic)")
    print("  W* requires FRANCE TO WIN TONIGHT. E[our pts | 120' region] per candidate entry:")
    for entry in ((1, 0), (2, 1), (0, 1)):
        eh, ph = cond_entry_ev(dFE, entry, "H")
        ea, pa = cond_entry_ev(dFE, entry, "A")
        ed, pd_ = cond_entry_ev(dFE, entry, "D")
        uncond = expected_points(entry, dFE)
        print(f"    entry {entry[0]}-{entry[1]}: E|FRA-win={eh:.3f} (p={ph:.3f})  E|ESP-win={ea:.3f} (p={pa:.3f})"
              f"  E|level120={ed:.3f} (p={pd_:.3f})  E[uncond]={uncond:.3f}")
    print("  -> the argmax entry is ALSO the max-harvest entry in the France-win branch (the branch W*")
    print("     lives in); an 0-1 Spain entry harvests in the branch where the locked-50 already protects us.")

    print("\nPART 3 -- P(hold #1) with W* FORCED (settlement deterministic, match layer MC seed 42)")
    vFEc, pFEc = diff_dist(dFE, (1, 0), MIX_FE, cond="H")     # tonight conditioned on FRA win
    vEA, pEA = diff_dist(dEA, (1, 0), MIX_EA)                  # proxy for the 3 remaining games
    rng = np.random.default_rng(SEED)
    t = vFEc[rng.choice(len(vFEc), size=N_MC, p=pFEc)]
    rest = vEA[rng.choice(len(vEA), size=(N_MC, N_GAMES_AFTER_TONIGHT), p=pEA)].sum(axis=1)
    layer = t + rest
    print(f"  tonight|FRA-win swing: E={float((vFEc*pFEc).sum()):+.3f}   "
          f"rest-of-slate/game: E={float((vEA*pEA).sum()):+.3f}")
    for case in ("A", "B"):
        us_pay = SETTLE[case]["us"] * LOCK
        ok = np.ones(N_MC, bool)
        row = []
        for c, g in GAPS.items():
            delta = SETTLE[case][c] * LOCK - us_pay
            h = g + layer - delta > 0
            ok &= h
            row.append(f"{c}={float(h.mean()):.4f}")
        print(f"  case {case}: " + "  ".join(row) + f"   JOINT(all 5)={float(ok.mean()):.4f}")

    print("\nPART 4 -- projected FINAL standings under W* (expected, tonight|FRA-win + 3-game proxy)")
    e_t = float((vFEc * pFEc).sum())
    e_r = float((vEA * pEA).sum()) * N_GAMES_AFTER_TONIGHT
    for case in ("A", "B"):
        us_pay = SETTLE[case]["us"] * LOCK
        print(f"  case {case}: expected FINAL margin (us - chaser) =")
        for c, g in GAPS.items():
            delta = SETTLE[case][c] * LOCK - us_pay
            print(f"    {c:8s} {g + e_t + e_r - delta:+7.2f}")

    # hand-checks: two cells against the rubric
    c1 = points((1, 0), (2, 1)) - points((2, 1), (2, 1))
    c2 = points((1, 0), (1, 0)) - points((0, 1), (1, 0))
    print(f"\nHAND-CHECK cells: ours1-0 vs rival2-1 @2-1 diff={c1} (expect -5) | "
          f"ours1-0 vs rival0-1 @1-0 diff={c2} (expect +9)")
    assert c1 == -5 and c2 == 9


if __name__ == "__main__":
    main()
