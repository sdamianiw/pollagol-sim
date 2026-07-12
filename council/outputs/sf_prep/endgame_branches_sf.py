# -*- coding: utf-8 -*-
"""Endgame branch enumeration + P(hold #1) MC -- SF refresh (2026-07-12, ADVISORY; I-3 clean,
imported by nothing). Supersedes council/outputs/nor_eng_qf/endgame_branches.py (kept committed as-is):
  - QFs resolved (ENG, ARG through) -> chain is now SF1 x SF2 -> final. BOTH SF advancement probs come
    from the FROZEN engine FULL120 ko_adjust dists on REAL odds (md6 snapshot) -- the SF1 90'-devig
    APPROX and the ENG-ARG 0.50 ASSUMPTION are gone. Only the FINAL pairwise probs remain ASSUMED
    (labeled, swept +/-10pp).
  - GAPS refreshed from the 2026-07-12 board (377 vs 349/342/338/338/327).
  - AWARD conditionals refreshed from the sourced Jul-12 post-QF report (ESPN/Fox/FIFA/NBC, 2-source):
    Kane did NOT score (6; Bellingham braced -> 6 and is the surging England Ball narrative -> Kane MVP
    haircut); Mbappe 8 == Messi 8 Boot tie (Mbappe-boot legs up); Maignan 4 CS vs Simon 5; Olise 5 with
    every 4-assist chaser ELIMINATED -> his no-France floor rises. All still ASSUMED judgments -> swept.
Current gaps (board 2026-07-12, VERIFIED): Greg +28, Gonzalo +35, felipe +39, Lucas +39, Rodrigo +50.
Locked-50 ownership (pool/locked_ownership_2026-06-28.md, OBSERVED) unchanged; live legs:
  us 4 (ESP champ/Mbappe boot/Kane MVP/Dibu GK; Bruno DEAD) - Greg 5 - Gonzalo 4 - felipe 4 -
  Lucas 2 - Rodrigo 5 (all-France)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = "data/snapshots/md6_2026-07-12T12-14-09Z.json"
FID_FE = "f9aa13a662d1658e5a02cfc06d6a2d73"   # France vs Spain SF1 (home=FRA)
FID_EA = "ced22494ae0bbb8cc4f7108bf6f493df"   # England vs Argentina SF2 (home=ENG)

GAPS = {"Greg": 28, "Gonzalo": 35, "felipe": 39, "Lucas": 39, "Rodrigo": 50}
LOCK = 10.0
N_REMAINING_GAMES = 4   # SF1, SF2, 3rd-place, final (pool has scored every KO game so far)
SEED = 42
N_MC = 200_000

# ---- ASSUMED pairwise win probs for the FINAL only (P(row beats col), swept +/-10pp) ----
PAIR = {("FRA", "ENG"): 0.55, ("FRA", "ARG"): 0.55, ("ESP", "ENG"): 0.50, ("ESP", "ARG"): 0.50}

# ---- ASSUMED award-leg conditionals (P the leg PAYS given the champion branch); post-QF refresh ----
AWARD = {
    "kane_mvp_if_eng":    0.30,  # us; HAIRCUT from 0.55: Kane no-goal in QF, Bellingham brace -> 6==6,
                                 # Bellingham is the surging Ball narrative (Goal/Oddschecker) -- SWEPT
    "kane_mvp_else":      0.02,
    "mbappe_mvp_if_fra":  0.60,  # Lucas, Rodrigo -- Mbappe +125 Ball favorite (Fox Jul-11), 8 goals
    "mbappe_mvp_else":    0.05,
    "yamal_mvp_any":      0.02,  # Greg, Gonzalo, felipe -- still no post-QF Yamal surge (UNVERIFIED)
    "maignan_gk_if_fra":  0.65,  # Greg, Rodrigo -- Maignan 4 CS (was 3) vs Simon 5; FRA title flips it
    "maignan_gk_else":    0.05,
    "dibu_gk_if_arg":     0.45,  # us (felipe common-mode) -- HAIRCUT from 0.55: Dibu 2 CS vs Simon 5;
                                 # even an ARG title needs jury lean over the CS table -- SWEPT
    "dibu_gk_else":       0.03,
    "olise_ast_if_fra":   0.70,  # Gonzalo -- leader 5; every 4-assist chaser ELIMINATED
    "olise_ast_else":     0.50,  # RAISED from 0.35: best surviving rivals are at 3 (Mbappe/Saka/Gordon);
                                 # frozen-5 needs someone to find +2 in <=3 games -- SWEPT
    "kane_scorer_if_eng": 0.20,  # felipe -- HAIRCUT from 0.35: Kane 6 now chases an 8-8 tie, no QF goal
    "kane_scorer_else":   0.02,
    "dembele_scorer_any": 0.02,  # Rodrigo
    "messi_ast_any":      0.05,  # Greg (Messi PROBABLE 3 vs Olise 5)
    "mbappe_ast_if_fra":  0.10,  # Rodrigo (Olise leads by 2 on his own teammate)
    "mbappe_ast_else":    0.02,
}
# our Mbappe-BOOT differential vs felipe/Rodrigo (they don't hold Mbappe scorer): 8==8 tie with Messi
MBAPPE_BOOT = {"FRA": 0.45, "ESP": 0.35, "ENG": 0.30, "ARG": 0.25}   # ASSUMED, swept


def dist_for(fid):
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
    return ko_adjust(run_match(live)["matrix"])["dist_120"]


def adv_probs():
    """BOTH SFs from FROZEN FULL120 ko_adjust dists on real odds (VERIFIED; pens 50/50)."""
    out = {}
    for fid, hn, an in ((FID_FE, "FRA", "ESP"), (FID_EA, "ENG", "ARG")):
        d = dist_for(fid)
        ph = np.tril(d, -1).sum()   # home win (rows = home goals)
        pa = np.triu(d, 1).sum()
        pl = np.trace(d)
        out[hn] = float(ph + pl / 2)
        out[an] = float(pa + pl / 2)
    return out


def champion_probs(adv, pair):
    """Chain: {FRA|ESP} x {ENG|ARG} -> final. Final pairwise = PAIR (ASSUMED, swept)."""
    probs = {t: 0.0 for t in ("FRA", "ESP", "ENG", "ARG")}
    for t1, p1 in (("FRA", adv["FRA"]), ("ESP", adv["ESP"])):
        for t2, p2 in (("ENG", adv["ENG"]), ("ARG", adv["ARG"])):
            pb = p1 * p2
            pw = pair[(t1, t2)]
            probs[t1] += pb * pw
            probs[t2] += pb * (1 - pw)
    return probs


def locked50_delta(chaser, champ):
    """Expected locked-50 (chaser minus us) given the CHAMPION, differential legs only."""
    A = AWARD
    us = (LOCK if champ == "ESP" else 0.0) \
        + LOCK * (A["kane_mvp_if_eng"] if champ == "ENG" else A["kane_mvp_else"]) \
        + LOCK * (A["dibu_gk_if_arg"] if champ == "ARG" else A["dibu_gk_else"])
    # common-mode legs excluded from BOTH sides (Mbappe boot vs Greg/Lucas/Gonzalo; Bruno; Dibu-vs-felipe)
    if chaser == "Greg":
        them = (LOCK if champ == "ESP" else 0.0) + LOCK * A["yamal_mvp_any"] + LOCK * A["messi_ast_any"] \
            + LOCK * (A["maignan_gk_if_fra"] if champ == "FRA" else A["maignan_gk_else"])
        usx = us
    elif chaser == "Lucas":
        them = 0.0 + LOCK * (A["mbappe_mvp_if_fra"] if champ == "FRA" else A["mbappe_mvp_else"])
        usx = us
    elif chaser == "Gonzalo":
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["yamal_mvp_any"] \
            + LOCK * (A["olise_ast_if_fra"] if champ == "FRA" else A["olise_ast_else"])
        usx = us
    elif chaser == "felipe":
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["yamal_mvp_any"] \
            + LOCK * (A["kane_scorer_if_eng"] if champ == "ENG" else A["kane_scorer_else"])
        usx = us - LOCK * (A["dibu_gk_if_arg"] if champ == "ARG" else A["dibu_gk_else"]) \
            + LOCK * MBAPPE_BOOT[champ]
    else:  # Rodrigo
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["dembele_scorer_any"] \
            + LOCK * (A["mbappe_mvp_if_fra"] if champ == "FRA" else A["mbappe_mvp_else"]) \
            + LOCK * (A["mbappe_ast_if_fra"] if champ == "FRA" else A["mbappe_ast_else"]) \
            + LOCK * (A["maignan_gk_if_fra"] if champ == "FRA" else A["maignan_gk_else"])
        usx = us + LOCK * MBAPPE_BOOT[champ]
    return them - usx


def game_diff_dist():
    """Per-game (our-minus-one-chaser) swing distribution vs a chalk/contrarian mixture field,
    from SF2 ENG-ARG FULL120 dist with our 1-0 (proxy for the 4 remaining games, ASSUMED).
    Mixture = q=0.25 of lead_max_sf.py's CHALK_ENG/CONTRA_ARG (renormalized per side)."""
    d = dist_for(FID_EA)
    mix = {(1, 0): 0.30, (2, 1): 0.1875, (1, 1): 0.15, (2, 0): 0.1125,
           (0, 1): 0.1375, (1, 2): 0.075, (0, 2): 0.0375}
    vals, ps = [], []
    n = d.shape[0]
    for rv, w in mix.items():
        for a in range(n):
            for b in range(n):
                p = d[a, b] * w
                if p <= 0:
                    continue
                vals.append(points((1, 0), (a, b)) - points(rv, (a, b)))
                ps.append(p)
    vals, ps = np.array(vals, float), np.array(ps, float)
    ps /= ps.sum()
    return vals, ps


def main():
    adv = adv_probs()
    print("ADVANCEMENT (BOTH SFs = FULL120 on real odds, VERIFIED): "
          + "  ".join(f"{k}={v:.4f}" for k, v in adv.items()))
    champ = champion_probs(adv, PAIR)
    print("P(CHAMPION) (final pairwise ASSUMED): "
          + "  ".join(f"{k}={v:.3f}" for k, v in sorted(champ.items(), key=lambda x: -x[1])))
    print(f"  sum={sum(champ.values()):.6f} (must be 1)")

    print("\nBRANCH TABLE -- expected locked-50 delta (chaser MINUS us) by champion branch")
    print("champ   P(branch)  " + "  ".join(f"{c:>8s}" for c in GAPS))
    worst = {}
    for cb in ("FRA", "ESP", "ENG", "ARG"):
        row = [locked50_delta(c, cb) for c in GAPS]
        for c, d_ in zip(GAPS, row):
            worst.setdefault(c, []).append((cb, d_))
        print(f"  {cb}    {champ[cb]:.3f}     " + "  ".join(f"{d_:+8.2f}" for d_ in row))
    print("\nGap coverage check: chaser closes the CURRENT gap only if locked50-delta + match-layer > gap")
    for c, g in GAPS.items():
        w = max(worst[c], key=lambda x: x[1])
        print(f"  {c}: gap +{g}, worst branch {w[0]} delta {w[1]:+.2f} -> "
              f"needs {g - w[1]:+.2f} MORE from the match layer ({N_REMAINING_GAMES} games)")

    vals, ps = game_diff_dist()
    mu, sd = float((vals * ps).sum()), float(np.sqrt(((vals - (vals*ps).sum()) ** 2 * ps).sum()))
    print(f"\nMATCH-LAYER per-game swing vs mixture field: E={mu:+.3f} sd={sd:.3f} (proxy=SF2, ASSUMED)")

    rng = np.random.default_rng(SEED)
    print(f"\nP(HOLD #1 vs each chaser) x champion branch  (MC {N_MC}, seed {SEED}, {N_REMAINING_GAMES} games)")
    print("champ   " + "  ".join(f"{c:>8s}" for c in GAPS))
    idx = rng.choice(len(vals), size=(N_MC, N_REMAINING_GAMES), p=ps)
    layer = vals[idx].sum(axis=1)   # our-minus-chaser total (same draw per chaser: conservative common-shock)
    for cb in ("FRA", "ESP", "ENG", "ARG"):
        row = []
        for c, g in GAPS.items():
            hold = float(np.mean(g + layer - locked50_delta(c, cb) > 0))
            row.append(hold)
        print(f"  {cb}   " + "  ".join(f"{h:8.3f}" for h in row))
    print("\nOVERALL P(hold #1 vs ALL top-5) by branch (same MC draws, joint over chasers):")
    for cb in ("FRA", "ESP", "ENG", "ARG"):
        ok = np.ones(N_MC, bool)
        for c, g in GAPS.items():
            ok &= (g + layer - locked50_delta(c, cb) > 0)
        print(f"  {cb}: {float(ok.mean()):.3f}")

    print("\nSWEEPS (sensitive assumptions)")
    # each sweep prints the chaser x branch cells where its key actually fires
    for tag, k, lo, hi, cells in (
            ("olise_else", "olise_ast_else", 0.30, 0.70, (("Gonzalo", "ESP"), ("Gonzalo", "ENG"))),
            ("kane_mvp_if_eng", "kane_mvp_if_eng", 0.15, 0.45, (("Greg", "ENG"), ("felipe", "ENG"))),
            ("dibu_gk_if_arg", "dibu_gk_if_arg", 0.30, 0.60, (("Greg", "ARG"), ("felipe", "ARG")))):
        for v in (lo, hi):
            old = AWARD[k]; AWARD[k] = v
            vals_ = [(c, b, locked50_delta(c, b)) for c, b in cells]
            AWARD[k] = old
            print(f"  {tag}={v:.2f}: " + "  ".join(f"{c}-delta({b})={d_:+.2f}" for c, b, d_ in vals_))
    for tag, v in (("mbappe_boot_lo", -0.10), ("mbappe_boot_hi", +0.10)):
        old = dict(MBAPPE_BOOT); [MBAPPE_BOOT.__setitem__(k, min(max(x + v, 0.05), 0.95)) for k, x in old.items()]
        d_fel = locked50_delta("felipe", "FRA")
        MBAPPE_BOOT.update(old)
        print(f"  {tag}: felipe-delta(FRA-branch)={d_fel:+.2f}")
    for dp in (-0.10, +0.10):
        pair2 = {k: min(max(v + dp, 0.05), 0.95) for k, v in PAIR.items()}
        ch2 = champion_probs(adv, pair2)
        print(f"  PAIR{dp:+.2f}: " + "  ".join(f"P({t})={ch2[t]:.3f}" for t in ("FRA", "ESP", "ENG", "ARG")))


if __name__ == "__main__":
    main()
