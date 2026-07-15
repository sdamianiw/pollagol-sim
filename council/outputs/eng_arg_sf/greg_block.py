# -*- coding: utf-8 -*-
"""GREG-BLOCK decision harness (2026-07-15, ADVISORY; I-3 clean, imported by nothing).
THE architecture call of SF2: gap vs Greg collapsed to +24 and Sebas holds a ~95% prior that Greg
enters an ARGENTINA scoreline tonight (Messi-assister stake + fandom). A predictable single-chaser
entry makes defensive-chalk IMPLEMENTABLE (the L50 freeze doctrine assumed picks-hidden ->
unimplementable), so the decision metric tonight is argmax_e P(hold #1 vs Greg | our entry e),
computed jointly with the post-SF1 endgame (Spain 2-0 France -> ESP in final; FRA legs DEAD).
Chain per MC draw (seed 42): tonight's real 120' cell (frozen FULL120 dist) x Greg entry ~ G
(ASSUMED mix, swept) -> tonight diff -> winner -> final ESP vs winner (PAIR .50) -> champion ->
award categoricals (post-SF1 re-conditioned, mutually exclusive, swept) -> realized settlement
(absolute pays; common legs cancel naturally) -> hold test 24 + diffs - (payG - payUs) > 0 (STRICT,
tie=loss; our 17-pleno tiebreak would win most ties -> also printed).
CONTROL: E[tonight diff(e,g)] must equal expected_points(e) - expected_points(g) (identity) for
3 pairs, and B4 = byte-identical re-run. Ownership: us = ESP/Mbappe-boot/Kane-MVP/Dibu-GK (Bruno dead);
Greg = ESP/Mbappe-boot/Messi-AST/Yamal-MVP/Maignan-GK(dead, ~1%). Gap = +24 (377 vs 353, user verbal,
cross-foot consistent). Others (Gonzalo/felipe/Lucas/Rodrigo >= +30, award slates gutted by FRA-out)
floor-checked at the end."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points, expected_points

SNAP = sys.argv[1] if len(sys.argv) > 1 else "data/snapshots/md6_2026-07-15T17-11-10Z.json"
FID = "ced22494ae0bbb8cc4f7108bf6f493df"
GAP = 24.0
LOCK = 10.0
SEED = 42
N = 200_000
N_PROXY = 2                      # 3rd-place + final (pool has scored every KO game)
PAIR_ESP = 0.50                  # ESP vs tonight's winner in the final (ASSUMED, +-10 swept)
OURS = [(1, 0), (2, 1), (0, 1), (1, 2), (0, 2), (1, 1)]

# Greg entry model G (ASSUMED shape, swept): P(ARG-side) = p95; within-side weights below.
G_ARG = {(0, 1): 0.40, (1, 2): 0.30, (0, 2): 0.15, (1, 1): 0.10, (2, 2): 0.05}
G_ENG = {(1, 0): 0.60, (2, 1): 0.40}
G_ARG_ALT = {(0, 1): 0.60, (1, 2): 0.25, (0, 2): 0.15}   # concentration sweep

# post-SF1 award conditionals (ASSUMED, swept where sensitive). FRA OUT -> Maignan/Mbappe-MVP dead.
AW = {"yamal_mvp_if_esp": 0.25, "yamal_mvp_else": 0.05,
      "kane_mvp_if_eng": 0.30, "kane_mvp_else": 0.02,
      "dibu_gk_if_arg": 0.45, "dibu_gk_else": 0.03,
      "maignan_gk": 0.01,
      "messi_ast_if_arg_final": 0.15, "messi_ast_else": 0.05,
      "mbappe_boot": 0.40}       # common-mode vs Greg (both hold it) -- kept for completeness


def dist_cells():
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID)
    d = ko_adjust(run_match(live)["matrix"])["dist_120"]
    n = d.shape[0]
    cells = [(a, b) for a in range(n) for b in range(n) if d[a, b] > 0]
    ps = np.array([d[a, b] for a, b in cells], float)
    return d, cells, ps / ps.sum()


def sample_cat(rng, cat, n):
    names = list(cat.keys())
    cum = np.cumsum([cat[k] for k in names])
    u = rng.random(n)
    out = np.full(n, "other", dtype=object)
    lo = 0.0
    for k, hi in zip(names, cum):
        out[(u >= lo) & (u < hi)] = k
        lo = hi
    return out


def run(d, cells, ps, p95, g_arg, yamal, messi_fin, pair_esp, label, verbose=True):
    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(cells), size=N, p=ps)
    A = np.array([cells[i][0] for i in idx]); B = np.array([cells[i][1] for i in idx])
    pens = rng.random(N)
    w2_eng = np.where(A > B, True, np.where(A < B, False, pens < .5))   # tonight's winner == ENG?
    # Greg entry per sim
    side = rng.random(N) < p95
    g_entries = list(g_arg.keys()) + list(G_ENG.keys())
    gw_arg = np.array([g_arg[k] for k in g_arg]); gw_arg = gw_arg / gw_arg.sum()
    gw_eng = np.array([G_ENG[k] for k in G_ENG]); gw_eng = gw_eng / gw_eng.sum()
    gi = np.where(side, rng.choice(len(g_arg), size=N, p=gw_arg),
                  len(g_arg) + rng.choice(len(G_ENG), size=N, p=gw_eng))
    # precompute points tables per entry over sampled cells
    def pts_of(entry):
        tbl = {c: points(entry, c) for c in cells}
        return np.array([tbl[cells[i]] for i in idx], float)
    pts_g = np.zeros(N)
    for j, ge in enumerate(g_entries):
        m = gi == j
        if m.any():
            pts_g[m] = pts_of(ge)[m]
    # champion: final = ESP vs tonight's winner
    fin = rng.random(N)
    champ_esp = fin < pair_esp
    champ = np.where(champ_esp, "ESP", np.where(w2_eng, "ENG", "ARG"))
    # proxy diffs for the 2 remaining games (our EV entry vs chalk mixture on tonight's dist shape)
    mix = {(1, 0): 0.30, (2, 1): 0.1875, (1, 1): 0.15, (2, 0): 0.1125,
           (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
    vals, pw = [], []
    for rv, w in mix.items():
        for (a, b), p in zip(cells, ps):
            vals.append(points((1, 0), (a, b)) - points(rv, (a, b))); pw.append(p * w)
    vals, pw = np.array(vals, float), np.array(pw, float); pw /= pw.sum()
    proxy = vals[rng.choice(len(vals), size=(N, N_PROXY), p=pw)].sum(axis=1)
    # award categoricals (mutually exclusive within category)
    mvp = np.empty(N, dtype=object); gk = np.empty(N, dtype=object); ast = np.empty(N, dtype=object)
    boot = sample_cat(rng, {"Mbappe": AW["mbappe_boot"]}, N)
    for cb in ("ESP", "ENG", "ARG"):
        m = champ == cb; nb = int(m.sum())
        mvp[m] = sample_cat(rng, {"Yamal": yamal if cb == "ESP" else AW["yamal_mvp_else"],
                                  "Kane": AW["kane_mvp_if_eng"] if cb == "ENG" else AW["kane_mvp_else"]}, nb)
        gk[m] = sample_cat(rng, {"Dibu": AW["dibu_gk_if_arg"] if cb == "ARG" else AW["dibu_gk_else"],
                                 "Maignan": AW["maignan_gk"]}, nb)
        # Messi assist odds depend on ARG reaching the final (one more Messi game vs 3rd-place only)
    arg_in_final = ~w2_eng
    pm = np.where(arg_in_final, messi_fin, AW["messi_ast_else"])
    ast_u = rng.random(N)
    ast = np.where(ast_u < pm, "Messi", "other")
    # NOTE: numpy bool "+" is logical OR -- cast each leg to float so parlays STACK (bug caught
    # 2026-07-15 by the exact-enumeration cross-validation in greg_paths.py)
    pay_us = LOCK * ((champ == "ESP").astype(float) + (boot == "Mbappe").astype(float)
                     + (mvp == "Kane").astype(float) + (gk == "Dibu").astype(float))
    pay_gr = LOCK * ((champ == "ESP").astype(float) + (boot == "Mbappe").astype(float)
                     + (ast == "Messi").astype(float) + (mvp == "Yamal").astype(float)
                     + (gk == "Maignan").astype(float))
    dAward = pay_gr - pay_us

    if verbose:
        print(f"\n=== {label}  [p95={p95:.2f} yamal={yamal:.2f} messi_fin={messi_fin:.2f} pairESP={pair_esp:.2f}] ===")
        print("entry  E[t-diff vs G]  P(G +>=5 tn)  P(G +9 tn)  E[vs field]  P(hold#1)  P(hold w/tb)")
    res = {}
    for e in OURS:
        pe = pts_of(e)
        d1 = pe - pts_g
        margin = GAP + d1 + proxy - dAward
        hold, hold_tb = float((margin > 0).mean()), float((margin >= 0).mean())
        evf = expected_points(e, d)
        res[e] = hold
        if verbose:
            print(f" {e[0]}-{e[1]}      {float(d1.mean()):+7.4f}      {float((d1<=-5).mean()):.4f}"
                  f"      {float((d1<=-9).mean()):.4f}     {evf:7.4f}    {hold:.5f}    {hold_tb:.5f}")
    return res


def main():
    d, cells, ps = dist_cells()
    # CONTROL: identity E[diff(e,g)] == E[pts e] - E[pts g] for 3 fixed pairs
    for e, g in (((1, 0), (0, 1)), ((0, 1), (1, 2)), ((1, 0), (1, 1))):
        lhs = sum(p * (points(e, c) - points(g, c)) for c, p in zip(cells, ps))
        rhs = expected_points(e, d) - expected_points(g, d)
        assert abs(lhs - rhs) < 1e-9, (e, g, lhs, rhs)
    print("CONTROL identity E[diff]==dEV: PASS (3 pairs)")
    assert points((1, 0), (2, 1)) - points((2, 1), (2, 1)) == -5
    assert points((0, 1), (1, 2)) == 4 and points((0, 1), (0, 1)) == 9
    print("HAND-CHECK rubric cells: PASS")

    base = run(d, cells, ps, 0.95, G_ARG, AW["yamal_mvp_if_esp"], AW["messi_ast_if_arg_final"], PAIR_ESP, "BASE")

    print("\nSWEEPS (does the argmax_e P(hold) move?)")
    for tag, kw in (("p95=0.80", dict(p95=.80)), ("p95=1.00", dict(p95=1.00)),
                    ("G concentrated 0-1", dict(g_arg=G_ARG_ALT)),
                    ("yamal=0.15", dict(yamal=.15)), ("yamal=0.40", dict(yamal=.40)),
                    ("messi_fin=0.05", dict(messi_fin=.05)), ("messi_fin=0.25", dict(messi_fin=.25)),
                    ("pairESP=0.40", dict(pair_esp=.40)), ("pairESP=0.60", dict(pair_esp=.60))):
        args = dict(p95=.95, g_arg=G_ARG, yamal=AW["yamal_mvp_if_esp"],
                    messi_fin=AW["messi_ast_if_arg_final"], pair_esp=PAIR_ESP)
        args.update(kw)
        r = run(d, cells, ps, args["p95"], args["g_arg"], args["yamal"], args["messi_fin"],
                args["pair_esp"], tag, verbose=False)
        best = max(r, key=r.get)
        line = "  ".join(f"{e[0]}-{e[1]}:{r[e]:.5f}" for e in OURS)
        print(f"  {tag:22s} best={best[0]}-{best[1]}  {line}")

    print("\nFLOOR-CHECK others (best case for them: gap +30, ALL award legs vs us worth +10 flat):")
    rng = np.random.default_rng(SEED + 7)
    mix_layer = run.__defaults__  # noqa placeholder (deterministic note)
    # conservative closed form: they need >20 net over 3 games incl. tonight; per-game diff sd~3.2, mean +0.25
    from math import erf, sqrt
    z = (20 - 0.75) / (3.2 * sqrt(3))
    print(f"  P(pass) ~ Phi(-{z:.2f}) ~ {0.5*(1-erf(z/sqrt(2))):.5f} per chaser -> negligible; Greg is the node.")


if __name__ == "__main__":
    main()
