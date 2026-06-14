"""Phase 2 - execution-discipline loop (Track B). Score recorded picks; track us vs B1 vs B2.

Pipeline (ONE direction, I3): predictions/decisions.csv -> this module -> points/Brier. A result NEVER
flows back into a model parameter. We import the model engine ONLY to REPLAY a frozen snapshot's odds
(backfill the forecast columns); the engine never sees a result.

Scoring uses the SINGLE corrected rubric src.optimizer.points (exact=3). Two Brier conventions (F12):
  * brier_model  = PRE-context DC implied_1x2 (implied_1x2(match_distribution)) - the MODEL-HEALTH metric,
                   the thing L17 draw-compression degrades (same object the L17 guard reads). PRIMARY.
  * brier_market = de-vig MARKET 1X2 - INPUT-CALIBRATION reference (well-calibrated by construction;
                   NOT a model signal). SECONDARY.
Why store BOTH: the DC fit and the market disagree on the outcome split (the F12 gap; MEX dD/dA~0.0043,
KOR~0.0192) - that disagreement is the model signal, and brier_market alone (near-tautological) would miss it.

PRE- vs POST-context (correcting an auditor F18 premise): brier_model reads the PRE-context DC matrix on
purpose - it isolates the DC fit / L17 and matches the L17 guard's object. Note neutral context is NOT a
no-op (CONTEXT_RULES['neutral'] = var_factor 1.06), so the PRE-context DC matrix already differs from the
POST-context COMMITTED forecast even on MD1 (MEX brier 0.1611 pre vs 0.1654 post; KOR 0.6045 vs 0.5986).
brier_model therefore tracks the DC FIT, not the committed forecast. LIMITATION (F17, registered pre-MD3):
this is BLIND to an apply_context/M5 corruption (H4, dormant until ~MD3) because that lives only in the
POST-context matrix. Before H4 wakes, add a POST-context model-Brier (or track pre+post) - it is the only
metric that would flag an H4 regression.

CLI:
  python -m src.decision_score backfill --snapshot data/snapshots/md1_2026-06-11T16-01-57Z.json
  python -m src.decision_score record <fixture_id> <H-A>     # write a final score + score the row
  python -m src.decision_score mark   <fixture_id>            # stamp 'reviewed'
  python -m src.decision_score summary                         # cumulative us vs B1 vs B2 + Brier + caveat
Stdlib + numpy + the src engine.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import statistics
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import decisionlog as dl
from src.optimizer import points
from src.model import match_distribution, implied_1x2

# ~280 = matches needed for a ±0.05 pts/match paired-SE to clear 0 at the observed spread (registered caveat).
N_SIGNAL = 280
CAVEAT = (f"n={{n}}; statistical signal requires ~{N_SIGNAL} matches - do NOT act on this "
          f"(register everything, compare everything, act on nothing result-driven; I3).")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- pure helpers -----------------------------------------------------------------------------
def parse_score(s: str) -> tuple[int, int]:
    h, a = str(s).strip().split("-")
    return int(h), int(a)


def outcome_class(score: tuple[int, int]) -> str:
    h, a = score
    return "home" if h > a else "away" if a > h else "draw"


def favorite_pick(probs: dict) -> tuple[int, int]:
    """B1 baseline = back the higher-win-prob side to win 1-0 / 0-1 (mirrors evals/backtest.py b1_pick).

    NEVER a draw - even on a DRAW-FAVOURED fixture (X is the modal 1X2 outcome) B1 still picks the more
    likely WINNER's 1-0/0-1 (this is the deliberate definition: B1 is the chalk 'favourite wins by one'
    rule, not 'predict the modal outcome' - that's B2/modal). None of the 8 MD1 fixtures is draw-favoured,
    so this branch is untested live; the behaviour is defined, not deferred. Tie on win-prob -> home.
    """
    return (1, 0) if probs["home"] >= probs["away"] else (0, 1)


def brier(probs: dict, actual: str) -> float:
    """Multiclass Brier over the 1X2 classes vs the realized outcome (range [0, 2])."""
    return sum((probs[c] - (1.0 if c == actual else 0.0)) ** 2 for c in ("home", "draw", "away"))


def is_model_high_confidence(probs: dict, entropy_threshold: float = 0.85) -> bool:
    """Advisory predicate (NON-blocking, informational; GATE 5 / I3): True when the model has a clear
    favorite = LOW 1X2 entropy. `probs` = {home, draw, away}. Max entropy for 3 classes = log2(3) ~ 1.585
    bits; the 0.85-bit default fires roughly when one outcome carries > ~0.70. Pure predicate over stored
    de-vig/matrix probabilities - never reads or writes a model parameter. Surfacing it means 'override only
    with a logged reason' (it would have flagged the GER-CUW 4-0 / HAI-SCO 0-2 overrides); ADVISORY, never a
    hard block."""
    import math
    ps = [p for p in (probs.get("home", 0.0), probs.get("draw", 0.0), probs.get("away", 0.0)) if p > 0]
    h = -sum(p * math.log2(p) for p in ps)
    return h < entropy_threshold


def _probs(row: dict, prefix: str) -> dict:
    return {"home": float(row[f"{prefix}_h"]), "draw": float(row[f"{prefix}_d"]),
            "away": float(row[f"{prefix}_a"])}


def score_row(row: dict, actual: tuple[int, int],
              entered_pick: tuple[int, int] | None = None) -> dict:
    """Score one backfilled row against the actual result. Returns the 5 scoring fields (+ `pts_entered`
    iff an entered_pick is supplied).

    points_* via the corrected rubric (src.optimizer.points); brier_model from m_* (PRE-context DC),
    brier_market from devig_* (market). Pure: reads the row's stored forecast, never a model param.
    DUAL-TRACK: `points_actual` is the MODEL track (scores row["pick"] = the EV-argmax). When `entered_pick`
    (what the human typed into pollaya) is given, ALSO score it -> `pts_entered`. The kw-only `None` default
    keeps every existing caller's 5-key contract byte-identical.
    """
    cls = outcome_class(actual)
    out = {
        "points_actual": points(parse_score(row["pick"]), actual),
        "points_b1": points(parse_score(row["favorite_pick"]), actual),
        "points_b2": points(parse_score(row["modal"]), actual),
        "brier_model": brier(_probs(row, "m"), cls),
        "brier_market": brier(_probs(row, "devig"), cls),
    }
    if entered_pick is not None:
        out["pts_entered"] = points(entered_pick, actual)
    return out


def _played(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("result") and r.get("points_actual") not in (None, "")]


def cumulative(rows: list[dict]) -> dict:
    """Cumulative us_model vs B1 vs B2 + mean Brier (both conventions) + the DUAL-TRACK override.

    `us` (= Sigma points_actual) is the MODEL track (the EV-argmax counterfactual). DUAL-TRACK (F28/F36):
    over rows that ALSO carry an entered_pick, `us_entered` = Sigma pts_entered = the REAL pollaya standing,
    and `override_value` = us_entered - us_model_dual (entered minus model; < 0 = overrides cost points).
    NOTE (F36 name-fragility): `points_actual` IS the model track's points only because `pick` = the model
    EV-argmax; if `pick` ever stops being the model pick this identity breaks - the override_value test is the
    backstop. I3: this READS results + picks and returns numbers; it never writes a model parameter.
    """
    pl = _played(rows)
    n = len(pl)
    us = sum(int(float(r["points_actual"])) for r in pl)
    b1 = sum(int(float(r["points_b1"])) for r in pl)
    b2 = sum(int(float(r["points_b2"])) for r in pl)
    mean = lambda key: (sum(float(r[key]) for r in pl) / n) if n else float("nan")
    dual = [r for r in pl if r.get("pts_entered") not in (None, "")]
    n_dual = len(dual)
    us_entered = sum(int(float(r["pts_entered"])) for r in dual) if n_dual else None
    override_value = (us_entered - sum(int(float(r["points_actual"])) for r in dual)) if n_dual else None
    return {"n": n, "us": us, "b1": b1, "b2": b2, "us_minus_b1": us - b1, "us_minus_b2": us - b2,
            "mean_brier_model": mean("brier_model"), "mean_brier_market": mean("brier_market"),
            "n_dual": n_dual, "us_entered": us_entered, "override_value": override_value}


def summary_text(c: dict) -> str:
    """Render the cumulative tracker, both Brier conventions labeled, with the mandatory small-n caveat.

    F36 labels: `us_model` = the model EV-argmax track (= Sigma points_actual); `us_entered` = what we
    actually typed into pollaya = the REAL standing. The OVERRIDE line shows entered - model (the realized
    cost of HITL overrides), I3-informational only - never a model signal.
    """
    lines = [
        "CUMULATIVE  (us_model = model EV-argmax counterfactual | us_entered = typed into pollaya = the REAL "
        "standing | B1 = favorite 1-0/0-1 | B2 = model modal)",
        f"  n={c['n']}   Sigma us_model={c['us']}   Sigma B1={c['b1']}   Sigma B2={c['b2']}",
    ]
    if c.get("override_value") is not None:
        lines.append(f"  Sigma us_entered={c['us_entered']}   (REAL standing over n_dual={c['n_dual']} "
                     f"fixtures carrying an entered pick)")
        lines.append(f"  OVERRIDE: us_entered - us_model = {c['override_value']:+d} pts  (entered minus model "
                     f"over the dual rows; < 0 = overrides cost points; I3 informational only, NOT a model signal)")
    lines += [
        f"  paired diffs:  us_model-B1 = {c['us_minus_b1']:+d}    us_model-B2 = {c['us_minus_b2']:+d}",
        f"  mean Brier (PRIMARY, model-health = PRE-context DC, the metric L17 degrades) = {c['mean_brier_model']:.4f}",
        f"  mean Brier (secondary, input-calibration = de-vig market; ~good by construction, NOT a model signal) "
        f"= {c['mean_brier_market']:.4f}",
        "  " + CAVEAT.format(n=c["n"]),
    ]
    return "\n".join(lines)


# --- snapshot backfill (forecast columns; rubric-INDEPENDENT) ----------------------------------
def _fmt(score: tuple[int, int]) -> str:
    return f"{score[0]}-{score[1]}"


def backfill(snapshot_path: str, path: str = dl.DECISIONS_PATH) -> list[dict]:
    """Migrate the schema, then fill the forecast columns for any row missing them via a deterministic
    snapshot replay (run_match consumes ONLY odds - never a result). Idempotent. Returns filled fixtures.

    Forecast cols: modal (B2), favorite_pick (B1), devig_* (market 1X2), m_* (PRE-context DC implied_1x2).
    """
    from src.run_matchday import run_match, _select_event
    from src.ingest import load_snapshot
    dl.migrate_schema(path)
    snap = load_snapshot(snapshot_path)
    filled = []
    for row in dl.read_decisions(path):
        fid = row["fixture_id"]
        if row.get("modal") and row.get("m_h"):            # already backfilled -> idempotent skip
            continue
        summ = run_match(_select_event(snap, fid))
        dv = summ["strength"]["probs"]                      # de-vig market 1X2
        m = implied_1x2(match_distribution(summ["strength"]))  # PRE-context DC implied_1x2 (F12, model-health)
        updates = {
            "modal": _fmt(summ["modal"]),
            "favorite_pick": _fmt(favorite_pick(dv)),
            "devig_h": f"{dv['home']:.6f}", "devig_d": f"{dv['draw']:.6f}", "devig_a": f"{dv['away']:.6f}",
            "m_h": f"{m['home']:.6f}", "m_d": f"{m['draw']:.6f}", "m_a": f"{m['away']:.6f}",
        }
        dl.update_decision(fid, updates, path)
        filled.append({"fixture_id": fid, **updates})
    return filled


# --- result entry + scoring -------------------------------------------------------------------
def record(fixture_id: str, score_str: str, entered_pick: str | None = None,
           path: str = dl.DECISIONS_PATH) -> dict:
    """Write a final score and score the row (points + both Briers). Requires the row to be backfilled.

    DUAL-TRACK: `entered_pick` (optional, e.g. "0-2") = the score the human actually typed into pollaya; it is
    scored into `pts_entered` while the MODEL track (`pick`/`points_actual`) is untouched. RETCON GUARD:
    refuse to overwrite an already-set `entered_pick` (never mutate a played fixture's entered_pick).
    """
    actual = parse_score(score_str)
    row = next((r for r in dl.read_decisions(path) if r["fixture_id"] == fixture_id), None)
    if row is None:
        raise ValueError(f"record: fixture_id {fixture_id!r} not in {path}")
    if not (row.get("modal") and row.get("m_h")):
        raise ValueError(f"record: {fixture_id!r} not backfilled (run `backfill --snapshot ...` first)")
    if entered_pick is not None and row.get("entered_pick"):
        raise ValueError(f"record: {fixture_id!r} already has entered_pick={row['entered_pick']!r} - refusing "
                         f"to overwrite (retcon guard; never mutate a played fixture's entered_pick)")
    ep = parse_score(entered_pick) if entered_pick else None
    s = score_row(row, actual, entered_pick=ep)
    updates = {"result": score_str,
               "points_actual": str(s["points_actual"]), "points_b1": str(s["points_b1"]),
               "points_b2": str(s["points_b2"]),
               "brier_model": f"{s['brier_model']:.6f}", "brier_market": f"{s['brier_market']:.6f}"}
    if entered_pick is not None:
        updates["entered_pick"] = entered_pick
        updates["pts_entered"] = str(s["pts_entered"])
    dl.update_decision(fixture_id, updates, path)
    return {"fixture_id": fixture_id, "result": score_str, "entered_pick": entered_pick, **s}


def mark(fixture_id: str, path: str = dl.DECISIONS_PATH) -> dict:
    """Stamp 'reviewed' for a fixture (the single Python writer the PowerShell review tool shells to)."""
    return dl.update_decision(fixture_id, {"reviewed": _utc()}, path)


# --- standings ingest (Track-B 2026-06-14; DETERMINISTIC field stats only - NO council, NO Monte Carlo) ---
STANDINGS_LOG_PATH = os.path.join(ROOT, "standings", "standings_log.csv")
STANDINGS_LOG_FIELDS = ["date", "n", "our_pts", "rank", "median", "mean", "sd", "our_z", "our_pctl",
                        "leader", "podium_cut", "gap_median", "gap_podium", "override_value"]


def standings_stats(data: dict, override_value=None) -> dict:
    """Pure deterministic field statistics from a standings JSON dict (stdlib `statistics` only).

    data = {date, n, points:[...full field incl. us...], our_points, our_rank, source}. Returns a row
    matching STANDINGS_LOG_FIELDS. `override_value` (int|None) is threaded in from cumulative() - this
    function never reads results or a model parameter (I3). No RNG, no council: a field eval, not a forecast.
    """
    pts = [float(x) for x in data["points"]]
    n = int(data["n"])
    our = float(data["our_points"])
    mean_pts = statistics.mean(pts)
    sd = statistics.stdev(pts) if len(pts) > 1 else 0.0
    median = statistics.median(pts)
    podium_cut = sorted(pts, reverse=True)[min(2, len(pts) - 1)]
    return {
        "date": data["date"], "n": n, "our_pts": int(our), "rank": int(data["our_rank"]),
        "median": round(median, 2), "mean": round(mean_pts, 4), "sd": round(sd, 4),
        "our_z": round((our - mean_pts) / sd, 4) if sd > 0 else "",
        "our_pctl": round(sum(1 for p in pts if p <= our) / n, 4),
        "leader": int(max(pts)), "podium_cut": int(podium_cut),
        "gap_median": int(our - median), "gap_podium": int(our - podium_cut),
        "override_value": "" if override_value is None else str(override_value),
    }


def ingest_standings(date_str: str, decisions_path: str = dl.DECISIONS_PATH,
                     log_path: str = STANDINGS_LOG_PATH, standings_root: str | None = None) -> dict:
    """Read standings/<date>/standings.json, compute deterministic stats (override_value pulled from
    cumulative(decisions.csv)), and append one row to standings_log.csv. Returns the stats row."""
    root = standings_root or os.path.join(ROOT, "standings")
    json_path = os.path.join(root, date_str, "standings.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"ingest_standings: {json_path} not found "
                                f"(create it from the standings screenshots first)")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    ov = cumulative(dl.read_decisions(decisions_path)).get("override_value")
    stats = standings_stats(data, ov)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    new = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=STANDINGS_LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(stats)
    return stats


# --- CLI --------------------------------------------------------------------------------------
def _divergences(rows: list[dict]) -> list[str]:
    """Rows where the EV pick != model modal: the ONLY fresh-odds flip candidates (F13 watch)."""
    out = []
    for r in rows:
        if r.get("modal") and r.get("pick") and r["pick"] != r["modal"]:
            out.append(f"{r['home']} vs {r['away']}: EV pick {r['pick']} != modal {r['modal']}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase-2 execution-discipline loop (score + track; HITL).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pb = sub.add_parser("backfill"); pb.add_argument("--snapshot", required=True)
    pb.add_argument("--path", default=dl.DECISIONS_PATH)
    pr = sub.add_parser("record"); pr.add_argument("fixture"); pr.add_argument("score")
    pr.add_argument("--entered-pick", dest="entered_pick", default=None,
                    help="the score the human actually typed into pollaya, e.g. 0-2 (optional; dual-track)")
    pr.add_argument("--path", default=dl.DECISIONS_PATH)
    pm = sub.add_parser("mark"); pm.add_argument("fixture"); pm.add_argument("--path", default=dl.DECISIONS_PATH)
    ps = sub.add_parser("summary"); ps.add_argument("--path", default=dl.DECISIONS_PATH)
    pst = sub.add_parser("standings")
    pst.add_argument("date", help="YYYY-MM-DD (matches standings/<date>/standings.json)")
    pst.add_argument("--path", default=dl.DECISIONS_PATH)
    pst.add_argument("--log-path", default=STANDINGS_LOG_PATH)
    args = ap.parse_args(argv)

    if args.cmd == "backfill":
        filled = backfill(args.snapshot, args.path)
        print(f"backfilled {len(filled)} fixture(s); schema now {len(dl.FIELDS)} columns.")
        for f in filled:
            print(f"  {f['fixture_id']}  modal={f['modal']}  B1={f['favorite_pick']}  "
                  f"devig=({f['devig_h']},{f['devig_d']},{f['devig_a']})  m=({f['m_h']},{f['m_d']},{f['m_a']})")
    elif args.cmd == "record":
        r = record(args.fixture, args.score, entered_pick=args.entered_pick, path=args.path)
        ep = (f"  entered={r['entered_pick']} pts_entered={r['pts_entered']} "
              f"(override {r['pts_entered'] - r['points_actual']:+d})") if r.get("pts_entered") is not None else ""
        print(f"recorded {args.fixture} = {r['result']}: points actual={r['points_actual']} "
              f"B1={r['points_b1']} B2={r['points_b2']}  "
              f"brier_model={r['brier_model']:.4f} brier_market={r['brier_market']:.4f}{ep}")
    elif args.cmd == "mark":
        mark(args.fixture, args.path)
        print(f"marked {args.fixture} reviewed.")
    elif args.cmd == "summary":
        rows = dl.read_decisions(args.path)
        print(summary_text(cumulative(rows)))
        div = _divergences(rows)
        if div:
            print("  EV-vs-modal divergence (the only fresh-odds flip candidates, F13):")
            for d in div:
                print(f"    - {d}")
    elif args.cmd == "standings":
        s = ingest_standings(args.date, decisions_path=args.path, log_path=args.log_path)
        print(f"standings {s['date']}: us={s['our_pts']} rank={s['rank']}/{s['n']}  median={s['median']} "
              f"mean={s['mean']} sd={s['sd']}  z={s['our_z']} pctl={s['our_pctl']}  leader={s['leader']} "
              f"podium_cut={s['podium_cut']}  gap_median={s['gap_median']:+d} gap_podium={s['gap_podium']:+d}  "
              f"override_value={s['override_value'] or 'n/a'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
