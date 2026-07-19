# -*- coding: ascii -*-
"""FINAL NODE -- Jul-19 binding T-1h computation. Game1 (3rd place FRA 4-6 ENG) is RESOLVED:
both we and Greg scored 0 on it (board-confirmed), so the realized gap is +24 and the decision
collapses to the final-only lookup the greg_endgame harness pre-computed as section [E].
This driver reuses greg_endgame.py functions verbatim (no logic re-implementation) on the FRESH
final-only snapshot. ADVISORY; I-3 clean. Usage: python final_node.py <snapshot.json> [gap]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import greg_endgame as GE

GAP_REALIZED = int(sys.argv[2]) if len(sys.argv) > 2 else 24


def table(cellsF, qs, gap):
    print(f"\n[A] FINAL-ONLY e2 table @ realized gap +{gap}  (P(Greg passes)+P(tie), strict: tie=loss)")
    hdr = "e2      " + "".join(f"  q={q:.2f}   " for q in qs)
    print(hdr)
    best = {}
    for e2 in GE.OURSF:
        row = f"{e2[0]}-{e2[1]}    "
        for q in qs:
            gmix = GE.mix(GE.GF_ESP, GE.GF_ARG, q)
            regions = GE.diff_dist_by_region(cellsF, e2, gmix)
            a, b, _ = GE.pass_tie_given_gap(regions, gap)
            row += f"  {100*(a+b):7.4f}%"
            best.setdefault(q, []).append((a + b, e2))
        print(row)
    print("argmin(P pass+tie) per q: " + "  ".join(
        f"q={q:.2f}:{min(v)[1][0]}-{min(v)[1][1]}({100*min(v)[0]:.4f}%)" for q, v in best.items()))
    return best


def main():
    cellsF = GE.dist_cells(GE.FIDF)
    print(f"snapshot={GE.SNAP}  gap_realized=+{GAP_REALIZED}  LOCK={GE.LOCK}")
    print(f"defaults: QF_ARG={GE.QF_ARG}  YAMAL={GE.YAMAL}  MESSI={GE.MESSI}  DIBU={GE.DIBU}  PENS_ESP={GE.PENS_ESP}")

    qs = [0.0, 0.25, 0.50, 0.75, 0.90, 1.00]
    table(cellsF, qs, GAP_REALIZED)

    # [B] cover delta at the realized gap: EV-argmax 1-0 vs cover 0-1, default q
    for tag, e2 in (("EV-argmax 1-0", (1, 0)), ("cover 0-1", (0, 1))):
        gmix = GE.mix(GE.GF_ESP, GE.GF_ARG, GE.QF_ARG)
        regions = GE.diff_dist_by_region(cellsF, e2, gmix)
        a, b, paths = GE.pass_tie_given_gap(regions, GAP_REALIZED)
        print(f"\n[B] {tag}: P(pass)={100*a:.4f}%  P(tie)={100*b:.4f}%  "
              f"P(hold strict)={100*(1-a-b):.4f}%  (tie=win: {100*(1-a):.4f}%)")
        for lbl, pp, pt in sorted(paths, key=lambda x: -(x[1] + x[2]))[:4]:
            print(f"    {lbl}  pass={100*pp:.5f}%  tie={100*pt:.5f}%")

    # [C] stressed award sweeps (worst plausible for us), e2 = 1-0 vs 0-1
    print("\n[C] stressed award sweeps @ q=QF_ARG, gap +%d  (P pass+tie, e2=1-0 | e2=0-1)" % GAP_REALIZED)
    sweeps = [
        ("default", {}),
        ("messi_arg .60", {"MESSI": {"ESP": GE.MESSI["ESP"], "ARG": 0.60}}),
        ("messi both +.15", {"MESSI": {"ESP": 0.40, "ARG": 0.55}}),
        ("yamal_esp .15", {"YAMAL": {"ESP": 0.15, "ARG": GE.YAMAL["ARG"]}}),
        ("dibu_arg .20 (Simon-null)", {"DIBU": {"ESP": GE.DIBU["ESP"], "ARG": 0.20}}),
        ("pens_esp .30", {"PENS_ESP": 0.30}),
        ("joint worst (messi.60+yamal.15+dibu.20)",
         {"MESSI": {"ESP": 0.40, "ARG": 0.60}, "YAMAL": {"ESP": 0.15, "ARG": 0.05},
          "DIBU": {"ESP": GE.DIBU["ESP"], "ARG": 0.20}}),
    ]
    saved = {k: getattr(GE, k) for k in ("YAMAL", "MESSI", "DIBU", "PENS_ESP")}
    for tag, over in sweeps:
        for k, v in over.items():
            setattr(GE, k, v)
        out = []
        for e2 in ((1, 0), (0, 1)):
            gmix = GE.mix(GE.GF_ESP, GE.GF_ARG, GE.QF_ARG)
            regions = GE.diff_dist_by_region(cellsF, e2, gmix)
            a, b, _ = GE.pass_tie_given_gap(regions, GAP_REALIZED)
            out.append(a + b)
        for k, v in saved.items():
            setattr(GE, k, v)
        print(f"  {tag:42s}  1-0: {100*out[0]:7.4f}%   0-1: {100*out[1]:7.4f}%   "
              f"cover buys {100*(out[0]-out[1]):+7.4f}pp")


if __name__ == "__main__":
    main()
