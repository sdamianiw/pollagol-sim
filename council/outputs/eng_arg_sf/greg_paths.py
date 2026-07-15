# -*- coding: utf-8 -*-
"""GREG LOSS-PATH EXHAUSTIVE ENUMERATION -- 'every universe where Greg wins' (2026-07-15, ADVISORY;
I-3 clean, imported by nothing). EXACT computation, no Monte Carlo: full convolution over
  tonight's 120' cell (frozen FULL120 dist) x Greg's entry (mix G) -> conditional d1 | result-region
  x 2 proxy games (exact convolution) x champion chain | region x award categoricals | champion
  -> P(Greg passes) decomposed into NAMED PATHS, for our entry e in {1-0 ENG, 0-1 ARG, 2-1}.
CROSS-VALIDATION (meta-check): totals must reproduce greg_block.py's MC loss rates (1-P(hold):
1-0 -> ~0.00055, 0-1 -> ~0.00016) within ~2 MC SE (~1.2e-4). If they don't, one harness is broken.
GAP SWEEP: recompute at gap {24, 20, 15, 10, 5} -> the 'when to play the man' crossover doctrine.
Same ASSUMED inputs as greg_block.py (Greg mix p95=.95, award conditionals, PAIR_ESP .50), labeled."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from collections import defaultdict
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-15T17-11-10Z.json"
FID = "ced22494ae0bbb8cc4f7108bf6f493df"
GAP = 24
LOCK = 10
P95 = 0.95
G_ARG = {(0, 1): 0.40, (1, 2): 0.30, (0, 2): 0.15, (1, 1): 0.10, (2, 2): 0.05}
G_ENG = {(1, 0): 0.60, (2, 1): 0.40}
PAIR_ESP = 0.50
AW = {"yamal_mvp_if_esp": 0.25, "yamal_mvp_else": 0.05,
      "kane_mvp_if_eng": 0.30, "kane_mvp_else": 0.02,
      "dibu_gk_if_arg": 0.45, "dibu_gk_else": 0.03,
      "maignan_gk": 0.01,
      "messi_ast_if_arg_final": 0.15, "messi_ast_else": 0.05}
MIX_CHALK = {(1, 0): 0.30, (2, 1): 0.1875, (1, 1): 0.15, (2, 0): 0.1125,
             (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
OURS = [(1, 0), (0, 1), (2, 1)]


def dist_cells():
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID)
    d = ko_adjust(run_match(live)["matrix"])["dist_120"]
    n = d.shape[0]
    return [((a, b), float(d[a, b])) for a in range(n) for b in range(n) if d[a, b] > 0]


def greg_mix():
    g = {}
    za = sum(G_ARG.values()); ze = sum(G_ENG.values())
    for k, w in G_ARG.items():
        g[k] = g.get(k, 0.0) + P95 * w / za
    for k, w in G_ENG.items():
        g[k] = g.get(k, 0.0) + (1 - P95) * w / ze
    return g


def convolve(d1, d2):
    out = defaultdict(float)
    for v1, p1 in d1.items():
        for v2, p2 in d2.items():
            out[v1 + v2] += p1 * p2
    return dict(out)


def award_paths(region):
    """Exact enumeration of (champion, MVP, GK, AST) given tonight's result region.
    Returns list of (label, prob, dAward = Greg-minus-us award delta). Common legs excluded."""
    # champion given region
    if region == "ENG":
        champs = [("ESP", PAIR_ESP), ("ENG", 1 - PAIR_ESP)]
        arg_final = False
    elif region == "ARG":
        champs = [("ESP", PAIR_ESP), ("ARG", 1 - PAIR_ESP)]
        arg_final = True
    else:  # level -> pens 50/50 then final
        champs = [("ESP", PAIR_ESP), ("ENG", (1 - PAIR_ESP) / 2), ("ARG", (1 - PAIR_ESP) / 2)]
        arg_final = None  # 50/50 -> handled below via averaging messi prob
    out = []
    for champ, pc in champs:
        yam = AW["yamal_mvp_if_esp"] if champ == "ESP" else AW["yamal_mvp_else"]
        kan = AW["kane_mvp_if_eng"] if champ == "ENG" else AW["kane_mvp_else"]
        mvp_opts = [("Yamal", yam, +LOCK), ("Kane", kan, -LOCK), ("othMVP", 1 - yam - kan, 0)]
        dib = AW["dibu_gk_if_arg"] if champ == "ARG" else AW["dibu_gk_else"]
        gk_opts = [("Dibu", dib, -LOCK), ("Maignan", AW["maignan_gk"], +LOCK),
                   ("othGK", 1 - dib - AW["maignan_gk"], 0)]
        if arg_final is None:
            pm = 0.5 * AW["messi_ast_if_arg_final"] + 0.5 * AW["messi_ast_else"]
        else:
            pm = AW["messi_ast_if_arg_final"] if arg_final else AW["messi_ast_else"]
        ast_opts = [("MessiAST", pm, +LOCK), ("othAST", 1 - pm, 0)]
        for mn, mp, md in mvp_opts:
            for gn, gp, gd in gk_opts:
                for an, ap, ad in ast_opts:
                    p = pc * mp * gp * ap
                    if p <= 0:
                        continue
                    out.append((f"{champ}|{mn}|{gn}|{an}", p, md + gd + ad))
    return out


def analyze(entry, cells, gmix, proxy2, gap, verbose=True):
    # conditional d1 distributions per region + region probs
    d1 = {"ENG": defaultdict(float), "ARG": defaultdict(float), "LEV": defaultdict(float)}
    pr = {"ENG": 0.0, "ARG": 0.0, "LEV": 0.0}
    for (a, b), pc in cells:
        r = "ENG" if a > b else ("ARG" if a < b else "LEV")
        pr[r] += pc
        for g, pg in gmix.items():
            d1[r][points(entry, (a, b)) - points(g, (a, b))] += pc * pg
    paths = []
    for r in ("ENG", "ARG", "LEV"):
        dcond = {v: p / pr[r] for v, p in d1[r].items()}
        m = convolve(dcond, proxy2)   # match-layer total given region
        for label, pa, daw in award_paths(r):
            # Greg passes strictly if gap + M - daw < 0 -> M <= daw - gap - 1 (integer support)
            thr = daw - gap - 1
            ppass = sum(p for v, p in m.items() if v <= thr)
            ptie = sum(p for v, p in m.items() if v == daw - gap)
            if ppass > 0 or ptie > 0:
                paths.append((f"{r}-win|{label}|need M<={thr}", pr[r] * pa * ppass,
                              pr[r] * pa * ptie))
    tot = sum(p for _, p, _ in paths)
    tie = sum(t for _, _, t in paths)
    if verbose:
        print(f"\nENTRY {entry[0]}-{entry[1]} @ gap +{gap}:  P(Greg PASSES)={tot:.6f}"
              f"  P(exact tie)={tie:.6f}  [P(hold strict)={1-tot-tie:.5f}]")
        print("  TOP LOSS PATHS (universe | prob | share):")
        for lbl, p, _ in sorted(paths, key=lambda x: -x[1])[:8]:
            if p > 0:
                print(f"    {lbl:58s} {p:.2e}  {p/tot*100:5.1f}%")
    return tot, tie


def main():
    cells = dist_cells()
    s = sum(p for _, p in cells)
    assert abs(s - 1.0) < 1e-9
    gmix = greg_mix()
    assert abs(sum(gmix.values()) - 1.0) < 1e-9
    # exact proxy diff dist (our 1-0 vs chalk mixture), convolved for 2 future games
    prox = defaultdict(float)
    zm = sum(MIX_CHALK.values())
    for rv, w in MIX_CHALK.items():
        for (a, b), pc in cells:
            prox[points((1, 0), (a, b)) - points(rv, (a, b))] += pc * w / zm
    proxy2 = convolve(dict(prox), dict(prox))
    print("EXACT ENUMERATION -- every (tonight-result x champion x MVP x GK x AST x match-swing) branch")
    print(f"region probs: ENG-win {sum(p for (a,b),p in cells if a>b):.4f} / "
          f"ARG-win {sum(p for (a,b),p in cells if a<b):.4f} / level {sum(p for (a,b),p in cells if a==b):.4f}")

    print("\n=== CROSS-VALIDATION vs greg_block MC (must match within ~1.2e-4) ===")
    for e, mc in (((1, 0), 0.00055), ((0, 1), 0.00016)):
        tot, tie = analyze(e, cells, gmix, proxy2, GAP, verbose=False)
        ok = abs((tot + tie) - mc) < 1.2e-4
        print(f"  entry {e[0]}-{e[1]}: exact P(no-hold)={tot+tie:.5f} vs MC {mc:.5f} -> {'PASS' if ok else 'FAIL'}")

    for e in OURS:
        analyze(e, cells, gmix, proxy2, GAP)

    print("\n=== GAP SWEEP -- 'when to play the man' (P(Greg passes+ties), EV-pick 1-0 vs cover 0-1) ===")
    print("  gap   1-0 ENG      0-1 ARG      cover buys (bp)   verdict")
    for g in (24, 20, 15, 10, 5):
        t1, x1 = analyze((1, 0), cells, gmix, proxy2, g, verbose=False)
        t0, x0 = analyze((0, 1), cells, gmix, proxy2, g, verbose=False)
        a, b = t1 + x1, t0 + x0
        bp = (a - b) * 1e4
        v = "COVER" if bp >= 50 else ("consider" if bp >= 20 else "EV-pick")
        print(f"  +{g:2d}   {a:.5f}      {b:.5f}      {bp:7.1f}          {v}")

    # hand-checks
    assert points((1, 0), (0, 1)) == 0 and points((0, 1), (0, 1)) == 9
    assert points((0, 1), (1, 2)) == 4
    print("\nHAND-CHECKS PASS. All probabilities exact (convolution), no MC in this harness.")


if __name__ == "__main__":
    main()
