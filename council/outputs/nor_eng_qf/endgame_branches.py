# -*- coding: utf-8 -*-
"""Endgame branch enumeration + P(hold #1) MC (2026-07-11, ADVISORY; I-3 clean, imported by nothing).
Extends council/outputs/fra_mar_qf/locked50_scenarios.md from 3 chasers to the CURRENT top-5 and makes
it numeric. Two layers:
  (1) DETERMINISTIC branch table: 6 champion branches x 5 chasers -> expected locked-50 delta
      (chaser minus us) + tonight-relevant advancement math. Champion-chain probabilities: tonight's
      two games from the FROZEN engine dists (VERIFIED); SF2/final pairwise win probs ASSUMED (labeled,
      swept +/-10pp). Award-leg conditionals ASSUMED (labeled, swept on the two sensitive ones).
  (2) SEEDED MC (numpy, seed=42): per-game match-layer swing vs a chalk/contrarian field mixture
      (exact per-game diff distribution from tonight's NOR-ENG dist reused as proxy for future games,
      ASSUMED) + locked-50 branch delta -> P(chaser closes the gap) per champion branch.
Current gaps (board 2026-07-11, VERIFIED): Greg +29, Lucas +30, Gonzalo +36, felipe +37, Rodrigo +39.
Locked-50 ownership (pool/locked_ownership_2026-06-28.md, OBSERVED):
  us:     ESP champ / Mbappe scorer / Bruno assist / KANE MVP / Dibu GK
  Greg:   ESP champ / Mbappe / Messi assist / Yamal MVP / Maignan GK
  Lucas:  POR champ(DEAD) / Mbappe / Bruno assist / MBAPPE MVP / D.Costa(DEAD)
  Gonzalo: FRA champ / Mbappe / OLISE assist (leader 5) / Yamal MVP / Alisson(DEAD)
  felipe: FRA champ / KANE scorer / Bruno assist / Yamal MVP / Dibu GK
  Rodrigo: FRA champ / Dembele scorer / Mbappe assist / MBAPPE MVP / Maignan GK
Common-mode legs cancel in GAP terms (Mbappe scorer us==Greg==Lucas==Gonzalo; Bruno us==Lucas==felipe;
Dibu us==felipe). Only DIFFERENTIAL legs enter the deltas below."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np
from src.ingest import load_snapshot
from src.run_matchday import run_match
from src.ko_adjust import ko_adjust
from src.optimizer import points

SNAP = "data/snapshots/md5_2026-07-11T19-03-03Z.json"
FID_NE = "e66e4478b739fa0657a7a11235e1fcee"
FID_AS = "200d9cd5eda092c7eb778cc104cd2fd2"
FID_FE = "f9aa13a662d1658e5a02cfc06d6a2d73"   # France vs Spain SF1 (home=FRA)

GAPS = {"Greg": 29, "Lucas": 30, "Gonzalo": 36, "felipe": 37, "Rodrigo": 39}
LOCK = 10.0
N_REMAINING_GAMES = 6   # NOR-ENG, ARG-SUI, SF1, SF2, 3rd-place, final (ASSUMED pool scores all KO games
                        # incl. 3rd place -- it has scored every KO game so far; if 3rd place is absent
                        # the match-layer term only shrinks, which HELPS us hold)
SEED = 42
N_MC = 200_000

# ---- ASSUMED pairwise win probs (P(row beats col), swept +/-10pp) for games with no odds yet ----
PAIR = {("ENG", "ARG"): 0.50, ("ENG", "SUI"): 0.65, ("NOR", "ARG"): 0.40, ("NOR", "SUI"): 0.55,
        ("FRA", "ENG"): 0.55, ("FRA", "ARG"): 0.55, ("FRA", "NOR"): 0.60, ("FRA", "SUI"): 0.70,
        ("ESP", "ENG"): 0.50, ("ESP", "ARG"): 0.50, ("ESP", "NOR"): 0.60, ("ESP", "SUI"): 0.70}

# ---- ASSUMED award-leg conditionals (probability the leg PAYS given the champion branch) ----
# sensitive ones swept in the sweep section
AWARD = {
    "kane_mvp_if_eng":    0.55,  # us; Kane carrying England to title -> strong Ball case (he's #4 now)
    "kane_mvp_else":      0.02,
    "mbappe_mvp_if_fra":  0.50,  # Lucas, Rodrigo
    "mbappe_mvp_else":    0.05,
    "yamal_mvp_any":      0.02,  # Greg, Gonzalo, felipe -- Yamal out of Ball top-10 (verified Jul-9)
    "maignan_gk_if_fra":  0.60,  # Greg, Rodrigo -- Simon 5 CS is the Glove leader, but FRA title flips it
    "maignan_gk_else":    0.05,
    "dibu_gk_if_arg":     0.55,  # us (felipe common-mode)
    "dibu_gk_else":       0.03,
    "olise_ast_if_fra":   0.65,  # Gonzalo -- current leader 5
    "olise_ast_else":     0.35,  # frozen-not-dead if FRA exits (Diaz 4 can pass) -- SWEPT
    "kane_scorer_if_eng": 0.35,  # felipe -- Kane 6 vs Messi 8 / Mbappe 7; needs a scoring title run
    "kane_scorer_else":   0.03,
    "dembele_scorer_any": 0.02,  # Rodrigo
    "messi_ast_any":      0.05,  # Greg (~dead per Jul-9 table)
    "mbappe_ast_if_fra":  0.15,  # Rodrigo (Olise leads)
    "mbappe_ast_else":    0.03,
}


def adv_probs():
    """Tonight's QF advancement = FULL120 ko_adjust dists (VERIFIED); SF1 = APPROX (raw 90' devig +
    level->pens 50/50 -- ko_adjust NOT applied, mild undercount of the level-at-120 path)."""
    out = {}
    for fid, hn, an in ((FID_NE, "NOR", "ENG"), (FID_AS, "ARG", "SUI")):
        live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == fid)
        d = ko_adjust(run_match(live)["matrix"])["dist_120"]
        ph = np.tril(d, -1).sum()   # home win (rows=home goals) -- verified vs B0 print
        pa = np.triu(d, 1).sum()
        pl = np.trace(d)
        out[an] = float(pa + pl / 2)
        out[hn] = float(ph + pl / 2)
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID_FE)
    s = run_match(live)["strength"]["probs"]
    out["FRA"] = s["home"] + s["draw"] / 2
    out["ESP"] = s["away"] + s["draw"] / 2
    return out


def champion_probs(adv, pair):
    """Chain: {ENG|NOR} x {ARG|SUI} x {FRA|ESP} -> final -> champion. SF2 winner meets SF1 winner."""
    probs = {t: 0.0 for t in ("FRA", "ESP", "ENG", "NOR", "ARG", "SUI")}
    for t3, p3 in (("ENG", adv["ENG"]), ("NOR", adv["NOR"])):
        for t4, p4 in (("ARG", adv["ARG"]), ("SUI", adv["SUI"])):
            for t1, p1 in (("FRA", adv["FRA"]), ("ESP", adv["ESP"])):
                pb = p3 * p4 * p1
                w34 = pair[(t3, t4)]
                for tf2, pf2 in ((t3, w34), (t4, 1 - w34)):
                    pw1 = pair[(t1, tf2)]
                    probs[t1] += pb * pf2 * pw1
                    probs[tf2] += pb * pf2 * (1 - pw1)
    return probs


def locked50_delta(chaser, champ):
    """Expected locked-50 (chaser minus us) given the CHAMPION, differential legs only."""
    A = AWARD
    us = (LOCK if champ == "ESP" else 0.0) \
        + LOCK * (A["kane_mvp_if_eng"] if champ == "ENG" else A["kane_mvp_else"]) \
        + LOCK * (A["dibu_gk_if_arg"] if champ == "ARG" else A["dibu_gk_else"])
    # NOTE common-mode legs excluded from BOTH sides (Mbappe scorer, Bruno, and Dibu-vs-felipe handled below)
    if chaser == "Greg":
        them = (LOCK if champ == "ESP" else 0.0) + LOCK * A["yamal_mvp_any"] + LOCK * A["messi_ast_any"] \
            + LOCK * (A["maignan_gk_if_fra"] if champ == "FRA" else A["maignan_gk_else"])
        usx = us  # Mbappe scorer common; Bruno-vs-Messi differential kept (Bruno dead = 0 for us)
    elif chaser == "Lucas":
        them = 0.0 + LOCK * (A["mbappe_mvp_if_fra"] if champ == "FRA" else A["mbappe_mvp_else"])
        usx = us  # champ POR dead, GK dead; Mbappe scorer + Bruno common-mode
    elif chaser == "Gonzalo":
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["yamal_mvp_any"] \
            + LOCK * (A["olise_ast_if_fra"] if champ == "FRA" else A["olise_ast_else"])
        usx = us  # Mbappe scorer common; Alisson dead; our Bruno dead = 0 anyway
    elif chaser == "felipe":
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["yamal_mvp_any"] \
            + LOCK * (A["kane_scorer_if_eng"] if champ == "ENG" else A["kane_scorer_else"])
        # Dibu GK is common-mode with felipe -> remove it from our side; felipe does NOT hold
        # Mbappe scorer -> our Mbappe-boot leg IS differential here, add it.
        mb = 0.30 if champ == "FRA" else 0.15   # ASSUMED P(Mbappe wins Boot | branch): 7 vs Messi 8
        usx = us - LOCK * (A["dibu_gk_if_arg"] if champ == "ARG" else A["dibu_gk_else"]) + LOCK * mb
    else:  # Rodrigo
        them = (LOCK if champ == "FRA" else 0.0) + LOCK * A["dembele_scorer_any"] \
            + LOCK * (A["mbappe_mvp_if_fra"] if champ == "FRA" else A["mbappe_mvp_else"]) \
            + LOCK * (A["mbappe_ast_if_fra"] if champ == "FRA" else A["mbappe_ast_else"]) \
            + LOCK * (A["maignan_gk_if_fra"] if champ == "FRA" else A["maignan_gk_else"])
        mb = 0.30 if champ == "FRA" else 0.15   # our Mbappe-scorer differential vs Rodrigo's Dembele
        usx = us + LOCK * mb
    return them - usx


def game_diff_dist():
    """Per-game (our-minus-one-chaser) swing distribution for a chalk/contrarian mixture field,
    from tonight's NOR-ENG FULL120 dist with our 1-2 (proxy for future games, ASSUMED)."""
    live = next(e for e in load_snapshot(SNAP)["events"] if e["id"] == FID_NE)
    d = ko_adjust(run_match(live)["matrix"])["dist_120"]
    # ASSUMED: exactly the q=0.25 chalk/contrarian mixture of lead_max_scenarios.py
    # (CHALK_ENG x 0.75 + CONTRA_NOR x 0.25, renormalized per side)
    mix = {(1, 2): 0.30, (0, 1): 0.225, (0, 2): 0.15, (1, 1): 0.075, (2, 1): 0.15, (1, 0): 0.0625, (2, 2): 0.0375}
    vals, ps = [], []
    n = d.shape[0]
    for rv, w in mix.items():
        for a in range(n):
            for b in range(n):
                p = d[a, b] * w
                if p <= 0:
                    continue
                vals.append(points((1, 2), (a, b)) - points(rv, (a, b)))
                ps.append(p)
    vals, ps = np.array(vals, float), np.array(ps, float)
    ps /= ps.sum()
    return vals, ps


def main():
    adv = adv_probs()
    print("ADVANCEMENT (QF=FULL120 VERIFIED; SF1=90'-devig APPROX): "
          + "  ".join(f"{k}={v:.3f}" for k, v in adv.items()))
    champ = champion_probs(adv, PAIR)
    print("P(CHAMPION) (chain, SF2/final pairwise ASSUMED): "
          + "  ".join(f"{k}={v:.3f}" for k, v in sorted(champ.items(), key=lambda x: -x[1])))
    print(f"  sum={sum(champ.values()):.6f} (must be 1)")

    print("\nBRANCH TABLE -- expected locked-50 delta (chaser MINUS us) by champion branch")
    print("champ   P(branch)  " + "  ".join(f"{c:>8s}" for c in GAPS))
    worst = {}
    for cb in ("FRA", "ESP", "ENG", "ARG", "NOR", "SUI"):
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
    print(f"\nMATCH-LAYER per-game swing vs mixture field: E={mu:+.3f} sd={sd:.3f} (proxy=tonight, ASSUMED)")

    rng = np.random.default_rng(SEED)
    print(f"\nP(HOLD #1 vs each chaser) x champion branch  (MC {N_MC}, seed {SEED}, {N_REMAINING_GAMES} games)")
    print("champ   " + "  ".join(f"{c:>8s}" for c in GAPS))
    idx = rng.choice(len(vals), size=(N_MC, N_REMAINING_GAMES), p=ps)
    layer = vals[idx].sum(axis=1)          # our-minus-chaser match-layer total (same draw reused per chaser: conservative common-shock)
    for cb in ("FRA", "ESP", "ENG", "ARG", "NOR", "SUI"):
        row = []
        for c, g in GAPS.items():
            hold = float(np.mean(g + layer - locked50_delta(c, cb) > 0))
            row.append(hold)
        print(f"  {cb}   " + "  ".join(f"{h:8.3f}" for h in row))
    print("\nOVERALL P(hold #1 vs ALL top-5) by branch (same MC draws, joint over chasers):")
    for cb in ("FRA", "ESP", "ENG", "ARG", "NOR", "SUI"):
        ok = np.ones(N_MC, bool)
        for c, g in GAPS.items():
            ok &= (g + layer - locked50_delta(c, cb) > 0)
        print(f"  {cb}: {float(ok.mean()):.3f}")

    print("\nSWEEPS (sensitive assumptions)")
    for tag, k, lo, hi in (("olise_else", "olise_ast_else", 0.15, 0.55),
                           ("kane_mvp_if_eng", "kane_mvp_if_eng", 0.35, 0.75)):
        for v in (lo, hi):
            old = AWARD[k]; AWARD[k] = v
            d_gon = locked50_delta("Gonzalo", "ESP")
            d_greg = locked50_delta("Greg", "ENG")
            AWARD[k] = old
            print(f"  {tag}={v:.2f}: Gonzalo-delta(ESP-branch)={d_gon:+.2f}  Greg-delta(ENG-branch)={d_greg:+.2f}")
    for dp in (-0.10, +0.10):
        pair2 = {k: min(max(v + dp, 0.05), 0.95) for k, v in PAIR.items()}
        ch2 = champion_probs(adv, pair2)
        print(f"  PAIR{dp:+.2f}: P(FRA)={ch2['FRA']:.3f} P(ESP)={ch2['ESP']:.3f} P(ENG)={ch2['ENG']:.3f} P(ARG)={ch2['ARG']:.3f}")


if __name__ == "__main__":
    main()
