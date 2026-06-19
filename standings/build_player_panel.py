"""PART 0 — build standings/player_panel.csv from the 3 real boards + skill-persistence analysis.

Reproducible, deterministic. Encodes the OCR'd board NAMES (the json has only anonymous points[]),
then VALIDATES them against the authoritative json point-arrays before writing anything.

OCR source (read 2026-06-19/20 via the Read image tool):
  Jun-14: standings/standings 14-06-26/  (3 PNGs, ranks 1-27)
  Jun-16: standings/standings 16-06-26/  (2 PNGs, ranks 1-27)
  Jun-19: standings/stadings 19-06-26/   (2 PNGs, ranks 1-27)  [dir typo "stadings" is real]

I-NOFAB: any integrity violation raises -> halt the panel, never fabricate. The json points[] arrays
are ground truth; the PNG only adds the NAMES. No model parameter is written from any of this (I-3).
"""
from __future__ import annotations
import csv
import json
import os
import sys
import unicodedata

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAND = os.path.join(ROOT, "standings")

# --- OCR'd boards: ordered (rank 1..27) lists of (name, points). NAMES from the PNGs. -------------
BOARD_06_14 = [
    ("Julio Rojas", 28), ("Germanator", 27), ("GonzaloVillagran", 26), ("felipe vergara", 26),
    ("Cristian Espinoza Barria", 26), ("Lucas LDC", 25), ("Gonzalo Rodríguez", 24),
    ("Juan Pablo Lobos", 24), ("Rodrigo MZ", 24), ("Nacho hurtado", 22), ("Greg Langer", 21),
    ("José Miguel", 20), ("Pireli18", 19), ("SEBASTIAN MERA", 19), ("Ignacio Martínez", 17),
    ("Javier Andres Roco Jorquera", 17), ("Santiago Luco", 17), ("Sergio Giglio", 16),
    ("Rodrigo Tamayo", 16), ("Sebastián Damiani", 15), ("Fernando Veliz Alvarado", 15),
    ("marcelo novoa", 13), ("Fran Segovia", 12), ("Matías Jorge Villagrán Salas", 12),
    ("Andrés Arciniegas", 11), ("Diego Vergara", 11), ("Fer Meyer Fer Meyer", 9),
]
BOARD_06_16 = [
    ("felipe vergara", 44), ("Rodrigo MZ", 44), ("Julio Rojas", 42), ("Lucas LDC", 42),
    ("Germanator", 39), ("Cristian Espinoza Barria", 37), ("José Miguel", 37), ("Nacho hurtado", 36),
    ("GonzaloVillagran", 36), ("Juan Pablo Lobos", 36), ("marcelo novoa", 36),
    ("Gonzalo Rodríguez", 35), ("Fernando Veliz Alvarado", 33), ("Greg Langer", 32),
    ("Santiago Luco", 32), ("SEBASTIAN MERA", 32), ("Ignacio Martínez", 32),
    ("Javier Andres Roco Jorquera", 30), ("Pireli18", 29), ("Rodrigo Tamayo", 29),
    ("Sebastián Damiani", 28), ("Sergio Giglio", 26), ("Matías Jorge Villagrán Salas", 24),
    ("Diego Vergara", 21), ("Fran Segovia", 21), ("Andrés Arciniegas", 20), ("Fer Meyer Fer Meyer", 20),
]
BOARD_06_19 = [
    ("Lucas LDC", 91), ("Rodrigo MZ", 87), ("José Miguel", 84), ("GonzaloVillagran", 79),
    ("Fernando Veliz Alvarado", 79), ("Greg Langer", 77), ("marcelo novoa", 76),
    ("Juan Pablo Lobos", 76), ("Julio Rojas", 76), ("felipe vergara", 75), ("Andrés Arciniegas", 71),
    ("Ignacio Martínez", 71), ("Cristian Espinoza Barria", 70), ("Sergio Giglio", 69),
    ("Gonzalo Rodríguez", 69), ("Rodrigo Tamayo", 68), ("Germanator", 68), ("Nacho hurtado", 66),
    ("Diego Vergara", 66), ("SEBASTIAN MERA", 65), ("Sebastián Damiani", 65), ("Pireli18", 64),
    ("Santiago Luco", 63), ("Fer Meyer Fer Meyer", 62), ("Javier Andres Roco Jorquera", 58),
    ("Fran Segovia", 55), ("Matías Jorge Villagrán Salas", 46),
]
BOARDS = {"2026-06-14": BOARD_06_14, "2026-06-16": BOARD_06_16, "2026-06-19": BOARD_06_19}
DATES = ["2026-06-14", "2026-06-16", "2026-06-19"]
US = "Sebastián Damiani"
# alias map for OCR variants across boards (none needed - names are UI-consistent; kept for audit).
ALIAS = {}


def _canon(name: str) -> str:
    return ALIAS.get(name, name)


def _slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "_".join(s.lower().split())


def _load_json_points(date: str) -> list:
    with open(os.path.join(STAND, date, "standings.json"), encoding="utf-8") as f:
        return json.load(f)


def build():
    # ---- integrity check (a): ORDERED match, board pts position-by-position == json points[] ----
    for date in DATES:
        meta = _load_json_points(date)
        board_pts = [p for _, p in BOARDS[date]]
        if board_pts != list(meta["points"]):
            raise SystemExit(f"OCR-INTEGRITY FAIL (ordered match) {date}:\n"
                             f"  board={board_pts}\n  json ={meta['points']}")
        # us row in the board must match json our_points / our_rank
        us_rank = [i + 1 for i, (n, _) in enumerate(BOARDS[date]) if _canon(n) == US]
        if len(us_rank) != 1:
            raise SystemExit(f"OCR-INTEGRITY FAIL: '{US}' not uniquely on {date} board")
        r = us_rank[0]
        if BOARDS[date][r - 1][1] != meta["our_points"] or r != meta["our_rank"]:
            raise SystemExit(f"OCR-INTEGRITY FAIL (us) {date}: board r{r}={BOARDS[date][r-1][1]} "
                             f"vs json rank {meta['our_rank']} pts {meta['our_points']}")
    print("OCR-integrity (a) ordered match vs all 3 json arrays + us row: PASS")

    # ---- integrity check (c): roster constancy - identical 27 canonical names across boards ----
    rosters = {date: {_canon(n) for n, _ in BOARDS[date]} for date in DATES}
    base = rosters[DATES[0]]
    for date in DATES:
        if len(BOARDS[date]) != 27:
            raise SystemExit(f"OCR-INTEGRITY FAIL: {date} has {len(BOARDS[date])} rows, expected 27")
        if len(rosters[date]) != 27:
            raise SystemExit(f"OCR-INTEGRITY FAIL: {date} has duplicate names: "
                             f"{[n for n,_ in BOARDS[date]]}")
        if rosters[date] != base:
            raise SystemExit(f"OCR-INTEGRITY FAIL (roster constancy) {date} != {DATES[0]}:\n"
                             f"  only in {date}: {rosters[date]-base}\n  only in {DATES[0]}: {base-rosters[date]}")
    print(f"OCR-integrity (c) roster constancy: PASS  (identical {len(base)} players across 3 boards)")

    # ---- assemble per-player panel ----
    panel = {}  # canon name -> {date: (pts, rank)}
    for date in DATES:
        for rank, (name, pts) in enumerate(BOARDS[date], start=1):
            panel.setdefault(_canon(name), {})[date] = (pts, rank)

    # ---- integrity check (b): per-player monotonicity pts_14<=pts_16<=pts_19, g1>=0, g2>=0 ----
    for name, rec in panel.items():
        p14, p16, p19 = rec["2026-06-14"][0], rec["2026-06-16"][0], rec["2026-06-19"][0]
        if not (p14 <= p16 <= p19):
            raise SystemExit(f"OCR-INTEGRITY FAIL (monotonicity) {name}: {p14}->{p16}->{p19}")
    print("OCR-integrity (b) per-player monotonicity (g1>=0, g2>=0): PASS")

    # ---- write player_panel.csv ----
    out = os.path.join(STAND, "player_panel.csv")
    rows = sorted(panel.items(), key=lambda kv: -kv[1]["2026-06-19"][0])  # by latest pts desc
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["player_id", "name",
                    "pts_2026-06-14", "rank_2026-06-14",
                    "pts_2026-06-16", "rank_2026-06-16",
                    "pts_2026-06-19", "rank_2026-06-19"])
        for name, rec in rows:
            w.writerow([_slug(name), name,
                        rec["2026-06-14"][0], rec["2026-06-14"][1],
                        rec["2026-06-16"][0], rec["2026-06-16"][1],
                        rec["2026-06-19"][0], rec["2026-06-19"][1]])
    print(f"wrote {out}  ({len(rows)} players)")
    return panel


def _spearman(x, y):
    """Spearman rho = Pearson on ranks (average ranks for ties). numpy-only, no scipy dep."""
    def rankdata(a):
        a = np.asarray(a, float)
        order = a.argsort()
        ranks = np.empty(len(a), float)
        ranks[order] = np.arange(1, len(a) + 1)
        # average ties
        _, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
        sums = np.zeros(len(counts))
        np.add.at(sums, inv, ranks)
        return (sums / counts)[inv]
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def analyse(panel):
    names = list(panel.keys())
    p14 = np.array([panel[n]["2026-06-14"][0] for n in names], float)
    p16 = np.array([panel[n]["2026-06-16"][0] for n in names], float)
    p19 = np.array([panel[n]["2026-06-19"][0] for n in names], float)
    r14 = np.array([panel[n]["2026-06-14"][1] for n in names], float)
    r16 = np.array([panel[n]["2026-06-16"][1] for n in names], float)
    r19 = np.array([panel[n]["2026-06-19"][1] for n in names], float)
    g1 = p16 - p14   # Jun14 -> Jun16
    g2 = p19 - p16   # Jun16 -> Jun19
    n = len(names)

    rho = _spearman(g1, g2)
    # n=27 inference: two-sided 5% critical rho ~ t-approx; power at true rho=0.3 ~0.31 (pre-declared).
    rho_crit = 0.38
    rank_ac_14_16 = _spearman(r14, r16)
    rank_ac_16_19 = _spearman(r16, r19)

    print("\n" + "=" * 78)
    print("PART 0c/0d — SKILL-PERSISTENCE  (n=27 players, 2 gain-periods; 3 boards, S2/Jun-15 PHANTOM)")
    print("=" * 78)
    print(f"per-period gains: g1 = pts_16 - pts_14   g2 = pts_19 - pts_16")
    print(f"  g1: mean={g1.mean():.2f}  sd(sigma_g1)={g1.std(ddof=1):.3f}  min={g1.min():.0f} max={g1.max():.0f}")
    print(f"  g2: mean={g2.mean():.2f}  sd(sigma_g2)={g2.std(ddof=1):.3f}  min={g2.min():.0f} max={g2.max():.0f}")
    print("-" * 78)
    print(f"PRIMARY  Spearman rho(g1,g2) = {rho:+.3f}   (n={n}; |rho_crit| ~ {rho_crit:.2f} at 5% two-sided;")
    print(f"         power at true rho=0.3 ~ 0.31 -> LOW power)")
    verdict = ("CONSISTENT-WITH-LUCK; cannot exclude moderate skill (|rho| <~ 0.4)"
               if abs(rho) < rho_crit else
               "rho exceeds the n=27 5% critical value -> evidence of gain-persistence (skill)")
    print(f"         VERDICT: {verdict}")
    print("-" * 78)
    print(f"SECONDARY (descriptive, STICKY/OVERSTATED - NOT the verdict):")
    print(f"  cumulative-rank autocorr  rho(rank14,rank16)={rank_ac_14_16:+.3f}  "
          f"rho(rank16,rank19)={rank_ac_16_19:+.3f}")
    print(f"  -> points never decrease => cumulative ranks are sticky BY CONSTRUCTION; overstates skill.")
    print("-" * 78)
    # leader persistence
    leader_19 = min(panel, key=lambda nm: panel[nm]["2026-06-19"][1])
    lr14, lr16, lr19 = (panel[leader_19]["2026-06-14"][1], panel[leader_19]["2026-06-16"][1],
                        panel[leader_19]["2026-06-19"][1])
    print(f"leader persistence: Jun-19 leader = {leader_19} (91 pts) had rank {lr14}->{lr16}->{lr19} "
          f"(Jun-14/16/19)")
    print(f"  -> climbed from rank {lr14} (mid-pack) => luck signature, not a sustained top seat.")
    print("-" * 78)
    us_g1 = panel[US]["2026-06-16"][0] - panel[US]["2026-06-14"][0]
    us_g2 = panel[US]["2026-06-19"][0] - panel[US]["2026-06-16"][0]
    print(f"us ({US}): pts 15->28->65  rank 20->21->21  | gains g1={us_g1} g2={us_g2}")
    print("=" * 78)
    print("OPPONENT-VARIANCE PARAMS for PART 1 (placement_mc sigma_opp):")
    print(f"  per-period mean gain mu:  g1={g1.mean():.2f}  g2={g2.mean():.2f}")
    print(f"  cross-player gain sigma:  sigma(g1)={g1.std(ddof=1):.3f}  sigma(g2)={g2.std(ddof=1):.3f}"
          f"   <- sigma_opp PRIMARY = sigma(g2)")
    print(f"  gain-autocorr rho(g1,g2): {rho:+.3f}")
    print(f"  cross-check: sigma(g2) ~ BASE_SIGMA=6.0 ?  {g2.std(ddof=1):.2f} vs 6.0")
    print("-" * 78)
    ahead = (p19 > panel[US]["2026-06-19"][0]).sum()
    print(f"BEATABLE? {ahead} players are strictly ahead of us at Jun-19. Low rho({rho:+.3f}) => per-period")
    print("  gains look luck-like (iid) => the lead is NOT a skill wall; differentiation variance is the")
    print("  lever (firmed up post-MD2; n=27, 2 periods => first estimate only).")
    print("=" * 78)
    return dict(rho_g1g2=rho, sigma_g1=g1.std(ddof=1), sigma_g2=g2.std(ddof=1),
                mu_g1=g1.mean(), mu_g2=g2.mean())


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    panel = build()
    analyse(panel)
