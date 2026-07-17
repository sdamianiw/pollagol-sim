# -*- coding: ascii -*-
"""GREG ENDGAME -- exact enumeration of the last two nodes (3rd-place Jul-18 + FINAL Jul-19), 2026-07-17.
ADVISORY; I-3 clean (reads snapshot odds only, imported by nothing). EXACT convolution, no Monte Carlo.

Model (successor of eng_arg_sf/greg_paths.py, which stays frozen as the SF2 audit artifact):
  gap = +24 (board 2026-07-17: us 386 / Greg 362). Two scored games remain.
  Game1 3rd-place France-England: PURE match layer vs Greg (his award legs don't touch it).
  Game2 FINAL Spain-Argentina: THE champion node -- result region sets champ in {ESP, ARG} directly
    (level after 120' -> pens, champ ~ PENS_ESP). Champion + Boot legs are COMMON-MODE with Greg
    (both hold Espana + Mbappe) -> delta 0 always, they drop out of the gap arithmetic entirely.
  Live differential award legs (delta = Greg-minus-us, LOCK=10):
    Greg: Messi-ASSISTER (+10, champ-conditioned), Yamal-MVP (+10), Maignan-GK (+10, ~dead)
    Us:   Dibu-GK (-10, pays ~only if ARG champ), Kane-MVP (-10, ~dead: England out of final)
  MVP and GK are CATEGORICALS (mutually exclusive within award); AST binary vs field.
  Greg passes strictly iff gap + M - dAW < 0, M = d1+d2 (our pts minus his); tie iff M == dAW - gap.
  Tie counted AS LOSS in headline numbers (conservative; in truth we hold the pleno tiebreak 18 vs
  his ~14-16) -- both printed.
ASSUMED inputs (labeled, swept): Greg side-probabilities Q3_ENG / QF_ARG (the free variables -- QF_ARG
  is THE read: his Espana champion lock vs his Argentina/Messi stake), within-side mixes, award
  conditionals re-grounded from Jul-16/17 market (Ball: Messi -750, Yamal +3000, Kane +4500; Glove:
  Simon presumptive if ESP; assists: Olise 5 vs Messi 4). Cross-validated by greg_endgame_mc.py
  (independent vectorized MC, seed 42) within 3xSE -- the L62 rule.
Usage: python council/outputs/endgame/greg_endgame.py [snapshot.json]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from collections import defaultdict
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md7_2026-07-17T10-48-15Z.json"
FID3 = "7a49e7985534a5ff3428740d0b630fd7"   # France (home) vs England, Jul-18 21:00Z
FIDF = "fb30113e43d113f1ace48b8563ba1ee9"   # Spain (home) vs Argentina, Jul-19 19:00Z
GAP = 24
LOCK = 10

OURS3 = [(2, 1), (1, 0), (2, 0), (1, 2), (0, 1)]
OURSF = [(1, 0), (2, 1), (2, 0), (0, 1), (1, 2), (0, 2), (1, 1), (0, 0)]  # draws included for
# candidate-set completeness (review finding: dist_120 keeps level mass; L54 says draws are
# EV-dominated but the P(hold) argmin must be free to disagree)

# Greg entry model (ASSUMED shapes, SF2-continuity; side-split = the swept free variable)
G3_FRA = {(2, 1): 0.35, (1, 0): 0.35, (2, 0): 0.30}
G3_ENG = {(1, 2): 0.40, (0, 1): 0.35, (0, 2): 0.25}
Q3_ENG = 0.30            # P(Greg goes England-side in the 3rd-place game); no stake -> mild contrarian
GF_ESP = {(1, 0): 0.40, (2, 1): 0.35, (2, 0): 0.25}
GF_ARG = {(0, 1): 0.35, (1, 2): 0.35, (0, 2): 0.15, (1, 1): 0.10, (2, 2): 0.05}
QF_ARG = 0.50            # P(Greg goes Argentina-side in the FINAL) -- THE read; full 0..1 sweep below

# Award conditionals by champion (ASSUMED, market-grounded Jul-16/17; swept)
YAMAL = {"ESP": 0.06, "ARG": 0.01}    # Ball +3000 ~.03 raw; bumped if ESP champ + big final
KANE = 0.01                            # Ball +4500, England out of final
MAIGNAN = 0.01                         # Glove w/ France out of final
MESSI = {"ESP": 0.25, "ARG": 0.40}    # top assister: 4 vs Olise 5, plays the final; title narrative
DIBU = {"ESP": 0.02, "ARG": 0.35}     # Glove: Simon presumptive if ESP champ
PENS_ESP = 0.50                        # champ | level after 120'


def dist_cells(fid):
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
    d = ko_adjust(run_match(live)["matrix"])["dist_120"]
    n = d.shape[0]
    return [((a, b), float(d[a, b])) for a in range(n) for b in range(n) if d[a, b] > 0]


def mix(side_a, side_b, q_b):
    """(1-q_b)*side_a + q_b*side_b, renormalized within each side."""
    za, zb = sum(side_a.values()), sum(side_b.values())
    g = {}
    for k, w in side_a.items():
        g[k] = g.get(k, 0.0) + (1 - q_b) * w / za
    for k, w in side_b.items():
        g[k] = g.get(k, 0.0) + q_b * w / zb
    return g


def diff_dist(cells, entry, gmix):
    """Exact dist of d = pts(entry,cell) - pts(g,cell) over cells x Greg mix."""
    out = defaultdict(float)
    for (a, b), pc in cells:
        for g, pg in gmix.items():
            out[points(entry, (a, b)) - points(g, (a, b))] += pc * pg
    return dict(out)


def diff_dist_by_region(cells, entry, gmix):
    """Same, but split by final region (home=Spain): ESP / ARG / LEV. Returns dict r -> (p_r, cond dist)."""
    acc = {"ESP": defaultdict(float), "ARG": defaultdict(float), "LEV": defaultdict(float)}
    pr = {"ESP": 0.0, "ARG": 0.0, "LEV": 0.0}
    for (a, b), pc in cells:
        r = "ESP" if a > b else ("ARG" if a < b else "LEV")
        pr[r] += pc
        for g, pg in gmix.items():
            acc[r][points(entry, (a, b)) - points(g, (a, b))] += pc * pg
    return {r: (pr[r], {v: p / pr[r] for v, p in acc[r].items()}) for r in acc if pr[r] > 0}


def award_paths(champ):
    """Exact (label, prob, dAW) enumeration for one realized champion. dAW = Greg-minus-us."""
    py, pk = YAMAL[champ], KANE
    mvp = [("YamalMVP", py, +LOCK), ("KaneMVP", pk, -LOCK), ("othMVP", 1 - py - pk, 0)]
    pd, pmg = DIBU[champ], MAIGNAN
    gk = [("DibuGK", pd, -LOCK), ("MaignanGK", pmg, +LOCK), ("othGK", 1 - pd - pmg, 0)]
    pm = MESSI[champ]
    ast = [("MessiAST", pm, +LOCK), ("othAST", 1 - pm, 0)]
    out = []
    for mn, mp, md in mvp:
        for gn, gp, gd in gk:
            for an, ap, ad in ast:
                p = mp * gp * ap
                if p > 0:
                    out.append((f"{champ}:{mn}|{gn}|{an}", p, md + gd + ad))
    return out


def award_paths_region(region):
    if region == "ESP":
        return award_paths("ESP")
    if region == "ARG":
        return award_paths("ARG")
    out = [(f"pens>{lbl}", PENS_ESP * p if c == "ESP" else (1 - PENS_ESP) * p, d)
           for c in ("ESP", "ARG") for lbl, p, d in award_paths(c)]
    # relabel keeps champ tag inside lbl; probabilities pre-scaled by the pens split
    return [(lbl, p, d) for lbl, p, d in out if p > 0]


def pass_tie_given_gap(regions, gap_now):
    """Given region-split d2 dists (from diff_dist_by_region) and the CURRENT gap (game1 resolved or
    hypothetical), return (P_pass, P_tie, paths). Path label carries region|award|threshold."""
    paths = []
    for r, (p_r, d2) in regions.items():
        for lbl, pa, daw in award_paths_region(r):
            thr = daw - gap_now - 1
            ppass = sum(p for v, p in d2.items() if v <= thr)
            ptie = sum(p for v, p in d2.items() if v == daw - gap_now)
            if ppass > 0 or ptie > 0:
                paths.append((f"{r}-reg|{lbl}|need d2<={thr}", p_r * pa * ppass, p_r * pa * ptie))
    return sum(p for _, p, _ in paths), sum(t for _, _, t in paths), paths


def joint(d1, regions, gap=None):
    """P(pass), P(tie) marginalizing game1: threshold shifts with realized d1."""
    gap = GAP if gap is None else gap
    tp = tt = 0.0
    for v1, p1 in d1.items():
        a, b, _ = pass_tie_given_gap(regions, gap + v1)
        tp += p1 * a
        tt += p1 * b
    return tp, tt


def main():
    global YAMAL, MESSI, DIBU, PENS_ESP
    cells3, cellsF = dist_cells(FID3), dist_cells(FIDF)
    for c in (cells3, cellsF):
        assert abs(sum(p for _, p in c) - 1.0) < 1e-9
    g3 = mix(G3_FRA, G3_ENG, Q3_ENG)
    gf = mix(GF_ESP, GF_ARG, QF_ARG)
    assert abs(sum(g3.values()) - 1.0) < 1e-9 and abs(sum(gf.values()) - 1.0) < 1e-9
    for r in ("ESP", "ARG"):
        s = sum(p for _, p, _ in award_paths(r))
        assert abs(s - 1.0) < 1e-9, (r, s)
    s_lev = sum(p for _, p, _ in award_paths_region("LEV"))
    assert abs(s_lev - 1.0) < 1e-9, ("LEV", s_lev)

    p3 = {"FRA": sum(p for (a, b), p in cells3 if a > b), "lev": sum(p for (a, b), p in cells3 if a == b),
          "ENG": sum(p for (a, b), p in cells3 if a < b)}
    pf = {"ESP": sum(p for (a, b), p in cellsF if a > b), "lev": sum(p for (a, b), p in cellsF if a == b),
          "ARG": sum(p for (a, b), p in cellsF if a < b)}
    print(f"GREG ENDGAME (exact, no MC)  snap={os.path.basename(SNAP)}  gap +{GAP}")
    print(f"  3rd-place 120' regions: FRA {p3['FRA']:.4f} / lev {p3['lev']:.4f} / ENG {p3['ENG']:.4f}")
    print(f"  FINAL     120' regions: ESP {pf['ESP']:.4f} / lev {pf['lev']:.4f} / ARG {pf['ARG']:.4f}")
    print(f"  Greg model: Q3_ENG={Q3_ENG}  QF_ARG={QF_ARG} (ASSUMED, swept)  awards: yamal {YAMAL}, "
          f"messi {MESSI}, dibu {DIBU}, kane {KANE}, maignan {MAIGNAN}, pens_esp {PENS_ESP}")

    # STRUCTURAL CHECK: no award delta -> Greg cannot pass (max match swing 18 < 24)
    regions_chk = diff_dist_by_region(cellsF, (1, 0), gf)
    d1_chk = diff_dist(cells3, (2, 1), g3)
    worst = min(d1_chk) + min(min(d2) for _, (_, d2) in regions_chk.items())
    assert worst >= -18 and -GAP < -18, f"structural: worst match swing {worst}"
    print(f"  STRUCTURAL: worst joint match swing = {worst} > -{GAP} -> awards are MANDATORY for Greg  OK")

    # ---------- [A] e2 (FINAL) decision table at gap +24, vs QF_ARG sweep -> crossover ----------
    print("\n=== [A] FINAL entry e2 at gap +24 (game1 net 0): P(Greg passes+ties) x QF_ARG ===")
    hdr = "  QF_ARG " + "".join(f"{f'{e[0]}-{e[1]}':>10s}" for e in OURSF) + "   best_e2"
    print(hdr)
    for q in [i / 10 for i in range(11)]:
        gfq = mix(GF_ESP, GF_ARG, q)
        row = []
        for e2 in OURSF:
            reg = diff_dist_by_region(cellsF, e2, gfq)
            a, b, _ = pass_tie_given_gap(reg, GAP)
            row.append(a + b)
        best = OURSF[row.index(min(row))]
        print(f"   {q:.1f}  " + "".join(f"{v*100:9.3f}%" for v in row) + f"   {best[0]}-{best[1]}")

    # ---------- [B] e1 (3rd place) table: static e2 representatives + sequential-optimal e2 ----------
    print("\n=== [B] 3RD-PLACE entry e1: P(pass+tie) with e2 fixed / with OPTIMAL e2 at realized gap ===")
    regs = {e2: diff_dist_by_region(cellsF, e2, gf) for e2 in OURSF}
    print("  e1     e2=1-0(chalk)  e2=0-1(cover)  e2=SEQ-OPTIMAL(policy)")
    for e1 in OURS3:
        d1 = diff_dist(cells3, e1, g3)
        stat = {}
        for e2 in ((1, 0), (0, 1)):
            a, b = joint(d1, regs[e2])
            stat[e2] = a + b
        seq = 0.0
        for v1, p1 in d1.items():
            best = min(sum(pass_tie_given_gap(regs[e2], GAP + v1)[:2]) for e2 in OURSF)
            seq += p1 * best
        print(f"  {e1[0]}-{e1[1]}     {stat[(1,0)]*100:8.3f}%      {stat[(0,1)]*100:8.3f}%        {seq*100:8.3f}%")

    # ---------- [C] GREG-NEEDS: our chalk (2-1, 1-0) vs his loss paths, named ----------
    print("\n=== [C] GREG-NEEDS MAP (our entries = chalk 2-1 then 1-0; Greg mix at defaults) ===")
    d1 = diff_dist(cells3, (2, 1), g3)
    reg10 = regs[(1, 0)]
    tp, tt = joint(d1, reg10)
    print(f"  P(Greg passes)={tp:.6f}  P(exact tie)={tt:.6f}  [P(hold strict)={1-tp-tt:.5f}]")
    agg = defaultdict(float)
    for v1, p1 in d1.items():
        _, _, paths = pass_tie_given_gap(reg10, GAP + v1)
        for lbl, p, _ in paths:
            agg[lbl.split("|need")[0]] += p1 * p
    print("  TOP LOSS PATHS (region|champ:MVP|GK|AST  --  prob, share):")
    for lbl, p in sorted(agg.items(), key=lambda x: -x[1])[:10]:
        if p > 0:
            print(f"    {lbl:46s} {p:.2e}  {p/tp*100:5.1f}%")

    # ---------- [D] ADVERSARIAL: Greg plays a PURE best-response (he can't see our entry) ----------
    print("\n=== [D] ADVERSARIAL Greg (pure entries, max over his (g1,g2)): our candidate pairs ===")
    gset3 = list(G3_FRA) + list(G3_ENG) + [(3, 1), (1, 3), (3, 0), (0, 3), (2, 2)]
    gsetF = list(GF_ESP) + list(GF_ARG) + [(3, 1), (1, 3), (0, 0)]   # long-shot gambles included
    print("  ours(e1,e2)      worst-case P(pass+tie)   Greg's best response (g1,g2)")
    results = {}
    for e1 in ((2, 1), (1, 0)):
        for e2 in ((1, 0), (0, 1), (1, 2)):
            wc, arg = 0.0, None
            for g1 in gset3:
                d1p = diff_dist(cells3, e1, {g1: 1.0})
                for g2 in gsetF:
                    regp = diff_dist_by_region(cellsF, e2, {g2: 1.0})
                    a, b = joint(d1p, regp)
                    if a + b > wc:
                        wc, arg = a + b, (g1, g2)
            results[(e1, e2)] = (wc, arg)
            print(f"  {e1[0]}-{e1[1]}, {e2[0]}-{e2[1]}        {wc*100:8.3f}%             "
                  f"g1={arg[0][0]}-{arg[0][1]} g2={arg[1][0]}-{arg[1][1]}")
    mm = min(results, key=lambda k: results[k][0])
    print(f"  MINIMAX pair: e1={mm[0][0]}-{mm[0][1]}, e2={mm[1][0]}-{mm[1][1]}  "
          f"worst-case {results[mm][0]*100:.3f}%")

    # ---------- [E] e2 lookup per REALIZED gap (the Jul-19 T-1h table) ----------
    print("\n=== [E] FINAL-node lookup: best e2 by realized gap (after 3rd place; Greg mix default) ===")
    print("  gap'   best_e2   P(pass+tie)    1-0 chalk     0-1 cover")
    for gp in (33, 30, 28, 26, 24, 22, 20, 18, 15):
        vals = {}
        for e2 in OURSF:
            a, b, _ = pass_tie_given_gap(regs[e2], gp)
            vals[e2] = a + b
        best = min(vals, key=vals.get)
        print(f"  +{gp:2d}    {best[0]}-{best[1]}    {vals[best]*100:8.3f}%    {vals[(1,0)]*100:8.3f}%     "
              f"{vals[(0,1)]*100:8.3f}%")

    # ---------- [F] SWEEPS: award params + pens, decision stability at QF_ARG=.5, gap 24 ----------
    print("\n=== [F] SWEEPS (best e2 at gap 24, QF_ARG=.5; flag if the argmin moves) ===")
    base = (dict(YAMAL), dict(MESSI), dict(DIBU), PENS_ESP)
    sweeps = [
        ("yamal_esp", [.03, .06, .12]), ("messi_arg", [.25, .40, .55]),
        ("messi_esp", [.10, .25, .40]), ("dibu_arg", [.20, .35, .45]), ("pens_esp", [.30, .50, .70]),
    ]
    gfq5 = mix(GF_ESP, GF_ARG, 0.5)
    regs5 = {e2: diff_dist_by_region(cellsF, e2, gfq5) for e2 in OURSF}   # award params don't touch these
    for name, vals in sweeps:
        row = []
        for v in vals:
            YAMAL, MESSI, DIBU, PENS_ESP = dict(base[0]), dict(base[1]), dict(base[2]), base[3]
            if name == "yamal_esp":
                YAMAL["ESP"] = v
            elif name == "messi_arg":
                MESSI["ARG"] = v
            elif name == "messi_esp":
                MESSI["ESP"] = v
            elif name == "dibu_arg":
                DIBU["ARG"] = v
            elif name == "pens_esp":
                PENS_ESP = v
            vals2 = {}
            for e2 in OURSF:
                a, b, _ = pass_tie_given_gap(regs5[e2], GAP)
                vals2[e2] = a + b
            best = min(vals2, key=vals2.get)
            row.append(f"{v}->{best[0]}-{best[1]} ({vals2[best]*100:.3f}%)")
        print(f"  {name:10s}: " + "   ".join(row))
    YAMAL, MESSI, DIBU, PENS_ESP = dict(base[0]), dict(base[1]), dict(base[2]), base[3]

    # hand-checks (rubric cells)
    assert points((1, 0), (0, 1)) == 0 and points((0, 1), (0, 1)) == 9
    assert points((2, 1), (1, 0)) == 4 and points((1, 2), (0, 1)) == 4 and points((2, 1), (3, 1)) == 4
    assert points((2, 1), (0, 1)) == 1 and points((1, 1), (2, 2)) == 4
    print("\nHAND-CHECKS PASS. All probabilities exact (convolution); MC cross-val = greg_endgame_mc.py.")


if __name__ == "__main__":
    main()
