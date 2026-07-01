# -*- coding: utf-8 -*-
"""ko_cadence - NON-FROZEN knockout-round cadence driver.

Formalizes the per-session scratchpad drivers (r32_flipcheck.py + bel_sen_driver.py) into ONE
deterministic, tested CLI so the KO cadence stops being re-typed each session. Reuses the FROZEN
engine (`run_matchday.run_match`, `optimizer`) and the non-frozen `ko_adjust` VERBATIM - it makes
no frozen edit, writes no model parameter, and reads NO match result (I-3 clean). It imports only
PUBLIC frozen symbols (`run_match`, `LineGuardStop`, `expected_points`, `ko_adjust`, `load_snapshot`);
the 6-line event selector is re-implemented locally so no private frozen symbol is coupled. Two caps:

  flipcheck : fresh 90' EV-argmax vs a baseline (a prior snapshot's argmax OR decisions.csv `pick`),
              with the runner-up gap and a HOLD/DEFER/FLIP verdict on the flip-floor band (L33). A
              fixture whose odds line is not x.5 is marked GUARD-STOP, not allowed to abort the batch.
  ko        : the FULL120 `ko_adjust` candidate table + f-band sweep + council-trigger (L53) for one
              knockout fixture (the pool scores 120', pens excluded - the raw 90' argmax the live
              cadence prints is NOT the KO-correct pick; run this for EVERY KO fixture, L57).

Advisory only: it surfaces the deterministic numbers; the human enters the pick (I-HITL). The LLM
council remains a separate, advisory step - this module produces its deterministic backbone.
"""
from __future__ import annotations
import argparse
import csv
import sys

from src.ingest import load_snapshot
from src.run_matchday import run_match, LineGuardStop
from src.optimizer import expected_points
from src.ko_adjust import ko_adjust

# Flip-floor discipline (L33) and council trigger (L53) - named + sourced, not magic numbers.
HOLD_FLOOR = 0.030      # gap < HOLD_FLOOR   -> sub-floor noise, HOLD the baseline
DEFER_CEIL = 0.040      # HOLD_FLOOR..DEFER_CEIL -> ambiguous, DEFER + re-check at T-1h
COUNCIL_EPS = 0.05      # best_decisive - best_draw <= COUNCIL_EPS -> draw live enough to convene
WEAK_FAV = 0.55         # max(devig_home, devig_away) < WEAK_FAV -> weak favourite / genuine near-even
F_BAND_DEFAULT = (0.25, 0.45, 0.65, 0.85, 1.0)   # cageyness grid -> penalty-rate f sweep (FULL120 only)

# Local score (de)serialisers: the codebase's formatters (`run_matchday._fmt_score`,
# `decision_score._fmt`) are PRIVATE, so there is no public helper to reuse; a shared module can't be
# introduced without editing frozen files. A local 2-line copy matches the existing per-module pattern.


def _score(s) -> str:
    return f"{int(s[0])}-{int(s[1])}"


def _parse_score(txt: str) -> tuple[int, int]:
    a, b = txt.strip().split("-")
    return (int(a), int(b))


def _select_event(data: dict, fixture_id: str) -> dict:
    """Local event selector (does not couple to run_matchday's private `_select_event`)."""
    for event in data.get("events", []):
        if event.get("id") == fixture_id:
            return event
    raise ValueError(f"fixture {fixture_id!r} not in payload ({len(data.get('events', []))} events)")


def _pred(cand) -> tuple | None:
    """Scoreline of a ko_adjust candidate row, or None (ko_adjust returns None when no draw/decisive
    cell clears the plausibility floor - e.g. draws on a heavy favourite after FULL120 depletion)."""
    return tuple(cand["pred"]) if cand is not None else None


def fixture_eval(event: dict) -> dict:
    """Compact FROZEN-engine read for one event (the 90' regulation layer). Pure; mutates nothing.
    May raise LineGuardStop (non-x.5 line) - batch callers catch it per fixture; single-fixture
    callers let it surface (loud + correct: that fixture cannot be scored)."""
    s = run_match(event)
    st, opt, matrix = s["strength"], s["opt"], s["matrix"]
    table = opt["table"]
    if not table:                                     # optimize() fell back to modal w/ empty table
        runup = {"pred": opt["pick"], "ev": opt["ev"]}
    else:
        runup = table[1] if len(table) > 1 else table[0]
    return {
        "fixture_id": s["match"]["fixture_id"],
        "home": s["match"]["home"], "away": s["match"]["away"],
        "devig": {k: float(st["probs"][k]) for k in ("home", "draw", "away")},
        "total_line": st["total_line"], "p_over": st["p_over"], "mu_eff": s["mu_eff"],
        "matrix": matrix,
        "argmax": tuple(opt["pick"]), "ev": float(opt["ev"]), "p_argmax": float(matrix[opt["pick"]]),
        "runup": tuple(runup["pred"]), "gap_runup": float(opt["ev"] - runup["ev"]),
        "modal": tuple(s["modal"]),
    }


def classify(gap_base: float) -> str:
    """Flip-floor verdict for a fresh argmax that DIFFERS from the baseline pick (L33)."""
    if gap_base < HOLD_FLOOR:
        return "HOLD"
    if gap_base <= DEFER_CEIL:
        return "DEFER"
    return "FLIP"


def _guard_stop_row(event: dict, baselines: dict) -> dict:
    fid = event.get("id")
    return {"fixture_id": fid, "home": event.get("home_team"), "away": event.get("away_team"),
            "devig": None, "argmax": None, "ev": None, "gap_runup": None, "modal": None,
            "baseline": baselines.get(fid), "ev_base": None, "gap_base": None, "verdict": "GUARD-STOP"}


def flip_check(snapshot_path: str, baselines: dict) -> list:
    """Per-fixture fresh 90' argmax vs a baseline pick.

    baselines: {fixture_id: (i, j)}. gap_base = EV(argmax) - EV(baseline) on the FRESH 90' matrix
    (>= 0 by construction). verdict = HOLD when argmax == baseline, else classify(gap_base); a fixture
    with no baseline is NO-BASELINE; a non-x.5-line fixture is GUARD-STOP (never aborts the batch).
    """
    data = load_snapshot(snapshot_path)
    rows = []
    for event in data.get("events", []):
        try:
            fx = fixture_eval(event)
        except LineGuardStop:
            rows.append(_guard_stop_row(event, baselines))
            continue
        base = baselines.get(fx["fixture_id"])
        if base is None:
            ev_base, gap_base, verdict = None, None, "NO-BASELINE"
        else:
            ev_base = expected_points(base, fx["matrix"])
            gap_base = fx["ev"] - ev_base
            verdict = "HOLD" if fx["argmax"] == base else classify(gap_base)
        rows.append({
            "fixture_id": fx["fixture_id"], "home": fx["home"], "away": fx["away"],
            "devig": fx["devig"], "argmax": fx["argmax"], "ev": fx["ev"],
            "gap_runup": fx["gap_runup"], "modal": fx["modal"],
            "baseline": base, "ev_base": ev_base, "gap_base": gap_base, "verdict": verdict,
        })
    return rows


def baselines_from_snapshot(prior_snapshot_path: str) -> dict:
    """Baseline map from a PRIOR snapshot's per-fixture argmax (KO fixtures not yet in decisions.csv).
    A non-x.5-line fixture is skipped (no baseline) rather than aborting the whole map."""
    data = load_snapshot(prior_snapshot_path)
    out = {}
    for event in data.get("events", []):
        try:
            out[event["id"]] = fixture_eval(event)["argmax"]
        except LineGuardStop:
            continue
    return out


def baselines_from_csv(csv_path: str, fixture_ids=None) -> dict:
    """Baseline map from decisions.csv `pick` (a FORECAST, not a result - I-3 clean). fixture_ids=None
    returns every logged pick; pass an iterable to filter."""
    want = set(fixture_ids) if fixture_ids is not None else None
    out = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fid = row.get("fixture_id")
            if row.get("pick") and (want is None or fid in want):
                out[fid] = _parse_score(row["pick"])
    return out


def council_trigger(fx: dict, ko: dict) -> dict:
    """Fire the LLM council only on a GENUINE near-even board (L53), never on a tag artifact.

    Fires iff (weak favourite AND EV-argmax diverges from the modal) OR (the FULL120 best-draw is
    within COUNCIL_EPS of best-decisive). The FULL120-argmax-vs-90'-argmax flip is reported as an
    informational `ko_flip` note (a heavy-favourite ET micro-flip is sub-floor, not a fire, L57).
    """
    reasons = []
    max_wp = max(fx["devig"]["home"], fx["devig"]["away"])
    if max_wp < WEAK_FAV and fx["argmax"] != fx["modal"]:
        reasons.append(f"weak-fav {max_wp:.3f}<{WEAK_FAV} AND EV-argmax {_score(fx['argmax'])} != modal {_score(fx['modal'])}")
    bd, bc = ko["best_draw"], ko["best_decisive"]
    if bd is not None and bc is not None:
        dgap = bc["ev"] - bd["ev"]
        if dgap <= COUNCIL_EPS:
            reasons.append(f"draw live: best_decisive - best_draw = {dgap:+.3f} <= {COUNCIL_EPS}")
    ko_flip = tuple(ko["ev_argmax"]) != fx["argmax"]
    return {
        "fires": bool(reasons), "reasons": reasons,
        "ko_flip": ko_flip,
        "ko_flip_note": (f"FULL120 argmax {_score(ko['ev_argmax'])} != 90' argmax {_score(fx['argmax'])}"
                         if ko_flip else None),
    }


def ko_candidates(snapshot_path: str, fixture_id: str, candidates=None,
                  cageyness: float = 0.65, ko_rule: str = "FULL120", f_band=None) -> dict:
    """Knockout analysis for one fixture under `ko_rule` (FULL120 = pool rule; REG90 = 90' sensitivity):
    candidate EVs (90' vs the KO-scored dist), an f-band penalty-rate sweep (FULL120 only), and the
    council-trigger. `candidates` defaults to the union of {90' argmax, modal, KO argmax, best_draw,
    best_decisive}; pass a list of (i, j) to score a specific set (e.g. the human's picks).
    """
    data = load_snapshot(snapshot_path)
    fx = fixture_eval(_select_event(data, fixture_id))
    M = fx["matrix"]
    r = ko_adjust(M, cageyness=cageyness, ko_rule=ko_rule)
    dist = r["dist_120"]

    if candidates is None:
        preds = [fx["argmax"], fx["modal"], tuple(r["ev_argmax"])]
        preds += [p for p in (_pred(r["best_draw"]), _pred(r["best_decisive"])) if p is not None]
        cands = sorted(set(preds))
    else:
        cands = [tuple(c) for c in candidates]
    cand_rows = [{"pred": c, "ev_90": expected_points(c, M), "ev_120": expected_points(c, dist)}
                 for c in cands]

    sweep = []
    if ko_rule == "FULL120":                          # the f-band is a FULL120-only penalty-rate tool
        band = f_band if f_band is not None else F_BAND_DEFAULT
        for cg in band:
            rr = ko_adjust(M, cageyness=cg, ko_rule="FULL120")
            bd, bc = rr["best_draw"], rr["best_decisive"]
            sweep.append({
                "cageyness": cg, "f_model": rr["f_model"], "argmax": tuple(rr["ev_argmax"]),
                "best_decisive": _pred(bc), "dec_ev": (bc["ev"] if bc else None),
                "best_draw": _pred(bd), "draw_ev": (bd["ev"] if bd else None),
            })

    return {
        "fixture_id": fx["fixture_id"], "home": fx["home"], "away": fx["away"], "ko_rule": ko_rule,
        "devig": fx["devig"], "total_line": fx["total_line"], "p_over": fx["p_over"], "mu_eff": fx["mu_eff"],
        "argmax_90": fx["argmax"], "ev_90": fx["ev"], "modal_90": fx["modal"],
        "ko_argmax": tuple(r["ev_argmax"]), "ko_argmax_pts": r["ev_argmax_pts"],
        "best_decisive": r["best_decisive"], "best_draw": r["best_draw"],
        "p_draw_90": r["p_draw_90"], "p_draw_scored": r["p_draw_scored"], "f_model": r["f_model"],
        "candidates": cand_rows, "f_band": sweep,
        "council": council_trigger(fx, r),
    }


# --------------------------------------------------------------------------------------------------
# CLI (dry-run / read-only). Prints tables; writes nothing. HITL enters the pick.
# --------------------------------------------------------------------------------------------------
def _print_flipcheck(rows: list) -> None:
    print(f"{'fixture':30} {'devig H/D/A':16} {'argmax':6} {'ev':7} {'gap_ru':7} "
          f"{'modal':6} {'base':6} {'gap_base':9} verdict")
    for r in rows:
        name = f"{(r['home'] or '?')[:14]}-{(r['away'] or '?')[:12]}"
        if r["verdict"] == "GUARD-STOP":
            print(f"{name:30} {'(non-x.5 line: not scored)':<58} GUARD-STOP")
            continue
        dv = r["devig"]
        base = _score(r["baseline"]) if r["baseline"] is not None else "--"
        gb = f"{r['gap_base']:+.4f}" if r["gap_base"] is not None else "--"
        print(f"{name:30} {dv['home']:.2f}/{dv['draw']:.2f}/{dv['away']:.2f}   "
              f"{_score(r['argmax']):6} {r['ev']:7.3f} {r['gap_runup']:7.4f} "
              f"{_score(r['modal']):6} {base:6} {gb:>9} {r['verdict']}")


def _cand_str(c) -> str:
    return f"{_score(c['pred'])} ({c['ev']:.4f})" if c is not None else "n/a"


def _print_ko(res: dict) -> None:
    dv = res["devig"]
    mu = f"{res['mu_eff']:.3f}" if res["mu_eff"] is not None else "--"
    pov = f"{res['p_over']:.3f}" if res["p_over"] is not None else "--"
    total = res["total_line"] if res["total_line"] is not None else "--"
    council = res["council"]
    flip = f"   [flipped from 90' {_score(res['argmax_90'])}]" if council["ko_flip"] else ""
    print(f"{res['home']} vs {res['away']}  ({res['fixture_id']})  ko_rule={res['ko_rule']}")
    print(f"  devig H/D/A = {dv['home']:.4f}/{dv['draw']:.4f}/{dv['away']:.4f}   "
          f"total={total} p_over={pov} mu_eff={mu}")
    print(f"  90' argmax={_score(res['argmax_90'])} (E={res['ev_90']:.4f})  modal={_score(res['modal_90'])}")
    print(f"  {res['ko_rule']} PICK (argmax)={_score(res['ko_argmax'])} (E={res['ko_argmax_pts']:.4f}){flip}")
    print(f"    best_decisive={_cand_str(res['best_decisive'])}  best_draw={_cand_str(res['best_draw'])}")
    print(f"  p_draw 90'={res['p_draw_90']:.4f} -> scored={res['p_draw_scored']:.4f}  f_model={res['f_model']:.4f}")
    print("  candidate E[pts]:   " + "  ".join(
        f"{_score(c['pred'])} 90={c['ev_90']:.3f}/ko={c['ev_120']:.3f}" for c in res["candidates"]))
    if res["f_band"]:
        print("  f-band (cagey/f/argmax/dec_ev/draw_ev):")
        for s in res["f_band"]:
            dec = f"{_score(s['best_decisive'])} {s['dec_ev']:.4f}" if s["best_decisive"] else "n/a"
            draw = f"{_score(s['best_draw'])} {s['draw_ev']:.4f}" if s["best_draw"] else "n/a"
            gap = (f"{s['dec_ev'] - s['draw_ev']:+.4f}"
                   if (s["dec_ev"] is not None and s["draw_ev"] is not None) else "n/a")
            print(f"    {s['cageyness']:.2f}  f={s['f_model']:.3f}  argmax={_score(s['argmax'])}  "
                  f"dec={dec}  draw={draw}  (dec-draw {gap})")
    print(f"  COUNCIL: {'FIRE' if council['fires'] else 'no-fire'}  reasons={council['reasons'] or '-'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KO-round cadence driver (read-only; HITL enters the pick).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    fc = sub.add_parser("flipcheck", help="fresh argmax vs baseline for every fixture in a snapshot")
    fc.add_argument("--snapshot", required=True)
    src = fc.add_mutually_exclusive_group()
    src.add_argument("--baseline-snapshot", help="prior snapshot -> per-fixture argmax baseline")
    src.add_argument("--baseline-csv", nargs="?", const="predictions/decisions.csv",
                     help="decisions.csv -> `pick` baseline (default path if flag given w/o value)")

    ko = sub.add_parser("ko", help="ko_adjust candidate table + council-trigger for one KO fixture")
    ko.add_argument("--snapshot", required=True)
    ko.add_argument("--fixture", required=True)
    ko.add_argument("--candidates", help="comma list e.g. '1-0,2-1,1-1,1-2' (default: derived set)")
    ko.add_argument("--cageyness", type=float, default=0.65)
    ko.add_argument("--ko-rule", default="FULL120", choices=["FULL120", "REG90"])

    args = ap.parse_args(argv)

    if args.cmd == "flipcheck":
        if args.baseline_snapshot:
            baselines = baselines_from_snapshot(args.baseline_snapshot)
        elif args.baseline_csv:
            baselines = baselines_from_csv(args.baseline_csv)
        else:                                        # no baseline -> fresh-scan (NO-BASELINE verdicts)
            baselines = {}
        _print_flipcheck(flip_check(args.snapshot, baselines))
        return 0

    if args.cmd == "ko":
        cands = [_parse_score(c) for c in args.candidates.split(",")] if args.candidates else None
        _print_ko(ko_candidates(args.snapshot, args.fixture, candidates=cands,
                                cageyness=args.cageyness, ko_rule=args.ko_rule))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
