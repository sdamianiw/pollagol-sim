# -*- coding: ascii -*-
"""GREG TWO-FRONT -- his seed-2 defense vs #1 hunt, 2026-07-17 (ADVISORY; I-3 clean, imported by nothing).
Question (Sebas): does Greg 'risk it' (England gamble / off-market final) to chase our +24, and what does
that cost him against HIS chasers (felipe 342 / Gonzalo 342 / Lucas 339 / Rodrigo 327)? Prize 60/20/10.

Model: joint MC (seed 42, N=1M, vectorized, every boolean .astype(float) -- L62) over the top-6 players:
  match layer (both games, frozen FULL120 dists) x entries (ours FIXED chalk; GREG = the STRATEGY variable;
  chasers = chalk-heavy mixes, ASSUMED+swept) x award categoricals (champ / boot / MVP / GK / AST from the
  REAL 2026-06-28 ownership slates -- pool/locked_ownership_2026-06-28.md -- with champion-conditional
  levels re-grounded from the Jul-16/17 market).
Slate cancellation structure this encodes (the analytical point):
  - Yamal-MVP: GREG+Gonzalo+felipe all hold it -> cancels on his SEED-2 front, only works vs US.
  - AST is the two-front pivot: Messi -> Greg +10 vs everyone; OLISE -> Gonzalo +10 vs Greg.
  - Dibu-GK (us + felipe): fires iff ARG champ -> an Argentina title hurts Greg on BOTH fronts.
  - Boot: Mbappe common to us/Greg/Gonzalo/Lucas but NOT felipe(Kane)/Rodrigo(Dembele).
Cutoff: players ranked 7+ (Jose Miguel 323 = -39 vs Greg) need >39 net vs Greg (match max 18 + no
  realistic award net > 20) -> excluded, documented.
Cross-validation (L62 rule): the pairwise marginal P(Greg passes us | pure strategy) from THIS sim must
  match greg_endgame.py's EXACT convolution within 3xSE.
Usage: python council/outputs/endgame/greg_two_front.py [snapshot.json]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import greg_endgame as GE
from greg_endgame_mc import np_score, sample_cells

SEED = 42
N = 1_000_000
POINTS = {"us": 386, "greg": 362, "gonzalo": 342, "felipe": 342, "lucas": 339, "rodrigo": 327}
PRIZE = {1: 0.60, 2: 0.20, 3: 0.10}          # pot shares (pot = 27 x 30k = 810k CLP)
LOCK = 10

# match entries: ours fixed; chaser mixes ASSUMED chalk-heavy (labeled, swept via CONTRARIAN_TILT)
US = ((2, 1), (1, 0))
CHASER_G1 = {(2, 1): 0.28, (1, 0): 0.28, (2, 0): 0.14, (1, 1): 0.10, (1, 2): 0.12, (0, 1): 0.08}
CHASER_G2 = {(1, 0): 0.30, (2, 1): 0.18, (1, 1): 0.14, (0, 1): 0.16, (1, 2): 0.12, (2, 0): 0.10}
STRATEGIES = [                                 # the GREG decision variable
    ("S1  chalk-chalk 2-1/1-0", (2, 1), (1, 0)),
    ("S1b chalk 1-0/1-0", (1, 0), (1, 0)),
    ("S2  ESP-diff  2-1/2-1", (2, 1), (2, 1)),
    ("S3  ENG-gamble 1-2/1-0", (1, 2), (1, 0)),
    ("S4  double    1-2/2-1", (1, 2), (2, 1)),
    ("S5  ARG-fandom 2-1/0-1", (2, 1), (0, 1)),
    ("S6  ENG+ARG   1-2/0-1", (1, 2), (0, 1)),
]

# award categoricals (champion-conditional; market-grounded Jul-16/17, ASSUMED+swept)
P_BOOT = {"MBAPPE": 0.40, "KANE": 0.02, "DEMBELE": 0.005}   # remainder ~.575 = Messi/other (no top-6 holder)
P_MVP = {"YAMAL_ESP": 0.06, "YAMAL_ARG": 0.01, "KANE": 0.01, "MBAPPE": 0.02}
P_GK = {"DIBU_ESP": 0.02, "DIBU_ARG": 0.35, "MAIGNAN": 0.01}
P_AST = {"MESSI_ESP": 0.25, "MESSI_ARG": 0.40, "MBAPPE": 0.02, "OTHER": 0.05}  # OLISE = remainder
PENS_ESP = GE.PENS_ESP


def sample_mix(rng, mixd, n):
    ks = list(mixd)
    w = np.array([mixd[k] for k in ks], dtype=float)
    idx = rng.choice(len(ks), size=n, p=w / w.sum())
    arr = np.array(ks, dtype=float)
    return arr[idx, 0], arr[idx, 1]


def run(quiet=False, greg_wins_chaser_ties=False, contrarian_tilt=0.0, p_olise_shift=0.0):
    """One full joint sim. Returns {strategy: (P1, P2, P3, Ppass_us, Eprize)} for Greg.
    greg_wins_chaser_ties: tie convention vs chasers (unknown pleno counts) -- run both.
    contrarian_tilt: extra weight chasers put on away-side entries (sweep).
    p_olise_shift: additive shift on P(Olise AST) via the OTHER/MESSI remainder (sweep)."""
    rng = np.random.default_rng(SEED)
    cells3, cellsF = GE.dist_cells(GE.FID3), GE.dist_cells(GE.FIDF)
    c3h, c3a = sample_cells(rng, cells3, N)
    cfh, cfa = sample_cells(rng, cellsF, N)

    g1mix, g2mix = dict(CHASER_G1), dict(CHASER_G2)
    if contrarian_tilt:
        for k in g1mix:
            if k[1] > k[0]:
                g1mix[k] += contrarian_tilt / 2
        for k in g2mix:
            if k[1] > k[0]:
                g2mix[k] += contrarian_tilt / 2
    chasers = {}
    for name in ("gonzalo", "felipe", "lucas", "rodrigo"):
        e1h, e1a = sample_mix(rng, g1mix, N)
        e2h, e2a = sample_mix(rng, g2mix, N)
        chasers[name] = (np_score(e1h, e1a, c3h, c3a), np_score(e2h, e2a, cfh, cfa))

    u_pens, u_boot, u_mvp, u_gk, u_ast = (rng.random(N) for _ in range(5))
    esp = (cfh > cfa) | ((cfh == cfa) & (u_pens < PENS_ESP))            # champion
    champ_pay = {"us": esp.astype(float) * LOCK, "greg": esp.astype(float) * LOCK}

    boot_mba = (u_boot < P_BOOT["MBAPPE"]).astype(float)
    boot_kane = ((u_boot >= P_BOOT["MBAPPE"]) & (u_boot < P_BOOT["MBAPPE"] + P_BOOT["KANE"])).astype(float)
    boot_dem = ((u_boot >= P_BOOT["MBAPPE"] + P_BOOT["KANE"])
                & (u_boot < P_BOOT["MBAPPE"] + P_BOOT["KANE"] + P_BOOT["DEMBELE"])).astype(float)

    y_p = np.where(esp, P_MVP["YAMAL_ESP"], P_MVP["YAMAL_ARG"])
    mvp_yam = (u_mvp < y_p).astype(float)
    mvp_kane = ((u_mvp >= y_p) & (u_mvp < y_p + P_MVP["KANE"])).astype(float)
    mvp_mba = ((u_mvp >= y_p + P_MVP["KANE"]) & (u_mvp < y_p + P_MVP["KANE"] + P_MVP["MBAPPE"])).astype(float)

    d_p = np.where(esp, P_GK["DIBU_ESP"], P_GK["DIBU_ARG"])
    gk_dibu = (u_gk < d_p).astype(float)
    gk_mai = ((u_gk >= d_p) & (u_gk < d_p + P_GK["MAIGNAN"])).astype(float)

    m_p = np.where(esp, P_AST["MESSI_ESP"], P_AST["MESSI_ARG"])          # Messi level fixed by champ
    ast_messi = (u_ast < m_p).astype(float)
    ast_mba = ((u_ast >= m_p) & (u_ast < m_p + P_AST["MBAPPE"])).astype(float)
    # p_olise_shift moves Olise mass by shifting the OTHER bucket the opposite way:
    # olise_shift = -0.10 -> OTHER +0.10 -> P(Olise) -10pp (V1 audit caught the inverted sign).
    oth_hi = m_p + P_AST["MBAPPE"] + np.maximum(P_AST["OTHER"] - p_olise_shift, 0.0)
    ast_olise = (u_ast >= oth_hi).astype(float)                          # remainder = Olise

    # award totals per player (from the REAL slates; dead legs contribute 0 by construction)
    awards = {
        "us": champ_pay["us"] + LOCK * (boot_mba + mvp_kane + gk_dibu),
        "greg": champ_pay["greg"] + LOCK * (boot_mba + mvp_yam + gk_mai + ast_messi),
        "gonzalo": LOCK * (boot_mba + mvp_yam + ast_olise),
        "felipe": LOCK * (boot_kane + mvp_yam + gk_dibu),
        "lucas": LOCK * (boot_mba + mvp_mba),
        "rodrigo": LOCK * (boot_dem + mvp_mba + gk_mai + ast_mba),
    }

    us_match = np_score(np.float64(US[0][0]), np.float64(US[0][1]), c3h, c3a) \
        + np_score(np.float64(US[1][0]), np.float64(US[1][1]), cfh, cfa)
    finals = {n: POINTS[n] + chasers[n][0] + chasers[n][1] + awards[n]
              for n in ("gonzalo", "felipe", "lucas", "rodrigo")}
    finals["us"] = POINTS["us"] + us_match + awards["us"]

    out = {}
    for label, g1, g2 in STRATEGIES:
        greg_match = np_score(np.float64(g1[0]), np.float64(g1[1]), c3h, c3a) \
            + np_score(np.float64(g2[0]), np.float64(g2[1]), cfh, cfa)
        greg_total = POINTS["greg"] + greg_match + awards["greg"]
        # rank vs us: we hold the pleno tiebreak (18 vs ~15) -> tie goes to US always.
        beats_us = (greg_total > finals["us"]).astype(float)
        # rank vs chasers: pleno counts unknown -> convention parameter.
        if greg_wins_chaser_ties:
            above = sum((finals[n] > greg_total).astype(float) for n in ("gonzalo", "felipe", "lucas", "rodrigo"))
        else:
            above = sum((finals[n] >= greg_total).astype(float) for n in ("gonzalo", "felipe", "lucas", "rodrigo"))
        rank = 1.0 + (1.0 - beats_us) + above                            # 1 + players strictly above Greg
        p1 = float((rank == 1).astype(float).mean())
        p2 = float((rank == 2).astype(float).mean())
        p3 = float((rank == 3).astype(float).mean())
        ep = PRIZE[1] * p1 + PRIZE[2] * p2 + PRIZE[3] * p3
        out[label] = (p1, p2, p3, float(beats_us.mean()), ep)
        if not quiet:
            print(f"  {label:24s} P1={p1*100:6.3f}%  P2={p2*100:6.2f}%  P3={p3*100:6.2f}%  "
                  f"E[prize-share]={ep:.4f}  (passes us: {float(beats_us.mean())*100:5.3f}%)")
    return out


def main():
    print(f"GREG TWO-FRONT (MC N={N:,} seed={SEED})  boards: greg 362 | chasers 342/342/339/327 | us 386")
    print(f"  chaser mixes ASSUMED chalk-heavy; awards: boot {P_BOOT} mvp {P_MVP} gk {P_GK} ast {P_AST}")
    print("\n=== [1] Greg strategy table (chaser ties count AGAINST Greg -- conservative for his seed-2) ===")
    base = run()

    print("\n=== [2] tie convention flipped (Greg WINS chaser ties) ===")
    run(greg_wins_chaser_ties=True)

    print("\n=== [3] chasers +10pp contrarian tilt ===")
    run(contrarian_tilt=0.10)

    print("\n=== [4] Olise-AST stress: P(Olise) shifted -10pp (transferred to 'other') ===")
    run(p_olise_shift=-0.10)

    # ---- L62 cross-validation: pairwise P(Greg passes us) vs the EXACT convolution ----
    print("\n=== [5] CROSS-VAL: pairwise P(passes us) vs greg_endgame EXACT (pure entries, 3xSE gate) ===")
    cells3, cellsF = GE.dist_cells(GE.FID3), GE.dist_cells(GE.FIDF)
    ok_all = True
    for label, g1, g2 in (STRATEGIES[0], STRATEGIES[4], STRATEGIES[6]):
        exd1 = GE.diff_dist(cells3, US[0], {g1: 1.0})
        exreg = GE.diff_dist_by_region(cellsF, US[1], {g2: 1.0})
        a, _b = GE.joint(exd1, exreg)          # strict pass (ties -> us, matches beats_us strict)
        mc = base[label][3]
        se3 = 3.0 * (a * (1 - a) / N) ** 0.5
        ok = abs(mc - a) < max(se3, 2e-5)
        ok_all &= ok
        print(f"  {label:24s} MC={mc:.6f}  exact={a:.6f}  |d|={abs(mc-a):.6f}  3SE={se3:.6f}  "
              f"{'PASS' if ok else 'FAIL'}")
    # hand-checks
    assert abs(sum(PRIZE.values()) - 0.9) < 1e-12
    r = np.random.default_rng(0)
    sp = r.integers(0, 4, size=(100, 4)).astype(float)
    from src.optimizer import points as pref
    ref = np.array([pref((int(x[0]), int(x[1])), (int(x[2]), int(x[3]))) for x in sp])
    assert np.array_equal(ref.astype(float), np_score(sp[:, 0], sp[:, 1], sp[:, 2], sp[:, 3]))
    print("\nHAND-CHECKS PASS (rubric 100/100, prize shares).",
          "CROSS-VAL:", "ALL PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
