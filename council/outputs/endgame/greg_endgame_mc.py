# -*- coding: ascii -*-
"""GREG ENDGAME MC -- independent vectorized cross-validation of greg_endgame.py (the L62 rule:
a decision-critical computation gets an INDEPENDENT whole-output re-derivation). Seed 42, N=2M.
Re-implements the rubric in numpy (every boolean leg .astype(float) -- L62) and spot-checks it
against src.optimizer.points; then estimates P(Greg passes/ties) by simulation and gates each
cell against the exact convolution within 3xSE.
Usage: python council/outputs/endgame/greg_endgame_mc.py [snapshot.json]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.optimizer import points as points_ref

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import greg_endgame as GE

SEED = 42
N = 2_000_000


def np_score(ph, pa, ah, aa):
    """Pool rubric, vectorized; every indicator cast per leg (L62)."""
    ph, pa = np.asarray(ph), np.asarray(pa)
    ah, aa = np.asarray(ah), np.asarray(aa)
    out = 3.0 * (np.sign(ph - pa) == np.sign(ah - aa)).astype(float)
    out += (ph == ah).astype(float)
    out += (pa == aa).astype(float)
    out += ((ph - pa) == (ah - aa)).astype(float)
    out += 3.0 * ((ph == ah) & (pa == aa)).astype(float)
    return out


def sample_entries(rng, mixd, n):
    ks = list(mixd)
    idx = rng.choice(len(ks), size=n, p=np.array([mixd[k] for k in ks]) / sum(mixd.values()))
    arr = np.array(ks)
    return arr[idx, 0], arr[idx, 1]


def sample_cells(rng, cells, n):
    p = np.array([p for _, p in cells])
    idx = rng.choice(len(cells), size=n, p=p / p.sum())
    arr = np.array([c for c, _ in cells])
    return arr[idx, 0], arr[idx, 1]


def main():
    rng = np.random.default_rng(SEED)
    cells3, cellsF = GE.dist_cells(GE.FID3), GE.dist_cells(GE.FIDF)

    # [1] rubric spot-check: numpy vs src.optimizer.points on 400 random pick/actual pairs
    sp = rng.integers(0, 5, size=(400, 4))
    ref = np.array([points_ref((int(r[0]), int(r[1])), (int(r[2]), int(r[3]))) for r in sp])
    got = np_score(sp[:, 0], sp[:, 1], sp[:, 2], sp[:, 3])
    assert np.array_equal(ref.astype(float), got), "rubric mismatch vs optimizer.points"
    print("rubric spot-check vs src.optimizer.points: 400/400 identical  OK")

    g3 = GE.mix(GE.G3_FRA, GE.G3_ENG, GE.Q3_ENG)
    gf = GE.mix(GE.GF_ESP, GE.GF_ARG, GE.QF_ARG)

    # samples shared across compared cells (common random numbers)
    c3h, c3a = sample_cells(rng, cells3, N)
    cfh, cfa = sample_cells(rng, cellsF, N)
    g1h, g1a = sample_entries(rng, g3, N)
    g2h, g2a = sample_entries(rng, gf, N)
    u_pens, u_mvp, u_gk, u_ast = rng.random(N), rng.random(N), rng.random(N), rng.random(N)

    esp = (cfh > cfa) | ((cfh == cfa) & (u_pens < GE.PENS_ESP))   # champion = ESP else ARG
    y_p = np.where(esp, GE.YAMAL["ESP"], GE.YAMAL["ARG"])
    m_p = np.where(esp, GE.MESSI["ESP"], GE.MESSI["ARG"])
    d_p = np.where(esp, GE.DIBU["ESP"], GE.DIBU["ARG"])
    yamal = (u_mvp < y_p).astype(float)
    kane = ((u_mvp >= y_p) & (u_mvp < y_p + GE.KANE)).astype(float)
    dibu = (u_gk < d_p).astype(float)
    maignan = ((u_gk >= d_p) & (u_gk < d_p + GE.MAIGNAN)).astype(float)
    messi = (u_ast < m_p).astype(float)
    daw = GE.LOCK * (yamal - kane + maignan - dibu + messi)

    dg1 = np_score(g1h, g1a, c3h, c3a)
    dg2 = np_score(g2h, g2a, cfh, cfa)

    print(f"\nMC N={N:,} seed={SEED}  (defaults Q3_ENG={GE.Q3_ENG} QF_ARG={GE.QF_ARG})")
    print("cell                              MC pass+tie    exact       |d|      3xSE     gate")
    ok_all = True
    # [2] joint cells (e1, e2)
    for e1, e2 in (((2, 1), (1, 0)), ((2, 1), (0, 1)), ((1, 0), (1, 0))):
        d1 = np_score(*np.broadcast_arrays(np.float64(e1[0]), np.float64(e1[1]), c3h, c3a)) - dg1
        d2 = np_score(*np.broadcast_arrays(np.float64(e2[0]), np.float64(e2[1]), cfh, cfa)) - dg2
        m = GE.GAP + d1 + d2 - daw
        est = float(((m < 0) | (m == 0)).astype(float).mean())
        exd1 = GE.diff_dist(cells3, e1, g3)
        exreg = GE.diff_dist_by_region(cellsF, e2, gf)
        a, b = GE.joint(exd1, exreg)
        ex = a + b
        se3 = 3.0 * (ex * (1 - ex) / N) ** 0.5
        ok = abs(est - ex) < max(se3, 1e-6)
        ok_all &= ok
        print(f"joint e1={e1[0]}-{e1[1]} e2={e2[0]}-{e2[1]}              {est:.6f}    {ex:.6f}  "
              f"{abs(est-ex):.6f}  {se3:.6f}  {'PASS' if ok else 'FAIL'}")
    # [3] final-only cells at gap 24 (no game1)
    for e2 in ((1, 0), (0, 1)):
        d2 = np_score(*np.broadcast_arrays(np.float64(e2[0]), np.float64(e2[1]), cfh, cfa)) - dg2
        m = GE.GAP + d2 - daw
        est = float(((m < 0) | (m == 0)).astype(float).mean())
        exreg = GE.diff_dist_by_region(cellsF, e2, gf)
        a, b, _ = GE.pass_tie_given_gap(exreg, GE.GAP)
        ex = a + b
        se3 = 3.0 * (ex * (1 - ex) / N) ** 0.5
        ok = abs(est - ex) < max(se3, 1e-6)
        ok_all &= ok
        print(f"final-only e2={e2[0]}-{e2[1]} @ gap 24           {est:.6f}    {ex:.6f}  "
              f"{abs(est-ex):.6f}  {se3:.6f}  {'PASS' if ok else 'FAIL'}")
    print("\nCROSS-VALIDATION:", "ALL PASS" if ok_all else "FAIL -- investigate before trusting either")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
