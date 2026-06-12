"""Phase 2 - execution-discipline loop (Track B). Score recorded picks; track us vs B1 vs B2.

Pipeline (ONE direction, I3): predictions/decisions.csv -> this module -> points/Brier. A result NEVER
flows back into a model parameter. We import the model engine ONLY to REPLAY a frozen snapshot's odds
(backfill the forecast columns); the engine never sees a result.

Scoring uses the SINGLE corrected rubric src.optimizer.points (exact=3). Two Brier conventions (F12):
  * brier_model  = PRE-context DC implied_1x2 (implied_1x2(match_distribution)) - the MODEL-HEALTH metric,
                   the thing L17 draw-compression degrades (same object the L17 guard reads). PRIMARY.
  * brier_market = de-vig MARKET 1X2 - INPUT-CALIBRATION reference (well-calibrated by construction;
                   NOT a model signal). SECONDARY.

CLI:
  python -m src.decision_score backfill --snapshot data/snapshots/md1_2026-06-11T16-01-57Z.json
  python -m src.decision_score record <fixture_id> <H-A>     # write a final score + score the row
  python -m src.decision_score mark   <fixture_id>            # stamp 'reviewed'
  python -m src.decision_score summary                         # cumulative us vs B1 vs B2 + Brier + caveat
Stdlib + numpy + the src engine.
"""
from __future__ import annotations
import argparse
import os
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
    """B1 baseline = back the 1X2 favorite to win 1-0 / 0-1. Never a draw; tie on win-prob -> home."""
    return (1, 0) if probs["home"] >= probs["away"] else (0, 1)


def brier(probs: dict, actual: str) -> float:
    """Multiclass Brier over the 1X2 classes vs the realized outcome (range [0, 2])."""
    return sum((probs[c] - (1.0 if c == actual else 0.0)) ** 2 for c in ("home", "draw", "away"))


def _probs(row: dict, prefix: str) -> dict:
    return {"home": float(row[f"{prefix}_h"]), "draw": float(row[f"{prefix}_d"]),
            "away": float(row[f"{prefix}_a"])}


def score_row(row: dict, actual: tuple[int, int]) -> dict:
    """Score one backfilled row against the actual result. Returns the 5 scoring fields.

    points_* via the corrected rubric (src.optimizer.points); brier_model from m_* (PRE-context DC),
    brier_market from devig_* (market). Pure: reads the row's stored forecast, never a model param.
    """
    cls = outcome_class(actual)
    return {
        "points_actual": points(parse_score(row["pick"]), actual),
        "points_b1": points(parse_score(row["favorite_pick"]), actual),
        "points_b2": points(parse_score(row["modal"]), actual),
        "brier_model": brier(_probs(row, "m"), cls),
        "brier_market": brier(_probs(row, "devig"), cls),
    }


def _played(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("result") and r.get("points_actual") not in (None, "")]


def cumulative(rows: list[dict]) -> dict:
    """Cumulative us vs B1 vs B2 + mean of both Brier conventions over scored rows."""
    pl = _played(rows)
    n = len(pl)
    us = sum(int(float(r["points_actual"])) for r in pl)
    b1 = sum(int(float(r["points_b1"])) for r in pl)
    b2 = sum(int(float(r["points_b2"])) for r in pl)
    mean = lambda key: (sum(float(r[key]) for r in pl) / n) if n else float("nan")
    return {"n": n, "us": us, "b1": b1, "b2": b2, "us_minus_b1": us - b1, "us_minus_b2": us - b2,
            "mean_brier_model": mean("brier_model"), "mean_brier_market": mean("brier_market")}


def summary_text(c: dict) -> str:
    """Render the cumulative tracker, both Brier conventions labeled, with the mandatory small-n caveat."""
    lines = [
        "CUMULATIVE (us = corrected-rubric EV pick | B1 = favorite 1-0/0-1 | B2 = model modal)",
        f"  n={c['n']}   Sigma us={c['us']}   Sigma B1={c['b1']}   Sigma B2={c['b2']}",
        f"  paired diffs:  us-B1 = {c['us_minus_b1']:+d}    us-B2 = {c['us_minus_b2']:+d}",
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
def record(fixture_id: str, score_str: str, path: str = dl.DECISIONS_PATH) -> dict:
    """Write a final score and score the row (points + both Briers). Requires the row to be backfilled."""
    actual = parse_score(score_str)
    row = next((r for r in dl.read_decisions(path) if r["fixture_id"] == fixture_id), None)
    if row is None:
        raise ValueError(f"record: fixture_id {fixture_id!r} not in {path}")
    if not (row.get("modal") and row.get("m_h")):
        raise ValueError(f"record: {fixture_id!r} not backfilled (run `backfill --snapshot ...` first)")
    s = score_row(row, actual)
    updates = {"result": score_str,
               "points_actual": str(s["points_actual"]), "points_b1": str(s["points_b1"]),
               "points_b2": str(s["points_b2"]),
               "brier_model": f"{s['brier_model']:.6f}", "brier_market": f"{s['brier_market']:.6f}"}
    dl.update_decision(fixture_id, updates, path)
    return {"fixture_id": fixture_id, "result": score_str, **s}


def mark(fixture_id: str, path: str = dl.DECISIONS_PATH) -> dict:
    """Stamp 'reviewed' for a fixture (the single Python writer the PowerShell review tool shells to)."""
    return dl.update_decision(fixture_id, {"reviewed": _utc()}, path)


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
    pr.add_argument("--path", default=dl.DECISIONS_PATH)
    pm = sub.add_parser("mark"); pm.add_argument("fixture"); pm.add_argument("--path", default=dl.DECISIONS_PATH)
    ps = sub.add_parser("summary"); ps.add_argument("--path", default=dl.DECISIONS_PATH)
    args = ap.parse_args(argv)

    if args.cmd == "backfill":
        filled = backfill(args.snapshot, args.path)
        print(f"backfilled {len(filled)} fixture(s); schema now {len(dl.FIELDS)} columns.")
        for f in filled:
            print(f"  {f['fixture_id']}  modal={f['modal']}  B1={f['favorite_pick']}  "
                  f"devig=({f['devig_h']},{f['devig_d']},{f['devig_a']})  m=({f['m_h']},{f['m_d']},{f['m_a']})")
    elif args.cmd == "record":
        r = record(args.fixture, args.score, args.path)
        print(f"recorded {args.fixture} = {r['result']}: points actual={r['points_actual']} "
              f"B1={r['points_b1']} B2={r['points_b2']}  "
              f"brier_model={r['brier_model']:.4f} brier_market={r['brier_market']:.4f}")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
