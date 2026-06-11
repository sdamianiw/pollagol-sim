"""P4c-0 line-distribution probe (Track B).

ONE live read-only call to The Odds API for the WC group stage; logs the real distribution of over/under
TOTAL lines and snapshots the raw payload to data/snapshots/ as an artifact. Answers the P4c precondition:
are the live lines all x.5 - the only lines poisson_over_prob/mu_from_pover handle correctly (H1)?
  ALL_X5          -> precondition satisfied.
  NON_X5_PRESENT  -> STOP + Sebas decides (restrict to x.5 | independent push/split oracle).
  NO_TOTALS_YET   -> totals not posted (common before ~Jun 9-11) -> re-probe nearer kickoff.
NON-BLOCKING under Option 3: the run_matchday x.5 guard enforces the invariant at runtime regardless.
Reuses src/ingest fetch+snapshot (no second copy); stdlib only.
"""
from __future__ import annotations
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from collections import Counter

from src.ingest import fetch_live, snapshot, load_snapshot, _market, _totals_of
from src.lines import is_half_line


def line_distribution(events: list) -> dict:
    """Pure: events -> {n_events, n_with_totals, n_quotes, dist (line->count), non_x5, verdict}.
    Counts every totals 'point' across ALL bookmakers of ALL events (one quote per book pricing totals)."""
    counts: Counter = Counter()
    n_with_totals = 0
    for ev in events:
        ev_has = False
        for bk in ev.get("bookmakers", []):
            tm = _market(bk, "totals")
            if not tm:
                continue
            for o in tm.get("outcomes", []):
                pt = o.get("point")
                if pt is not None:
                    counts[float(pt)] += 1
                    ev_has = True
        if ev_has:
            n_with_totals += 1
    non_x5 = sorted(l for l in counts if not is_half_line(l))
    n_quotes = sum(counts.values())
    verdict = "NO_TOTALS_YET" if n_quotes == 0 else ("NON_X5_PRESENT" if non_x5 else "ALL_X5")
    return {"n_events": len(events), "n_with_totals": n_with_totals, "n_quotes": n_quotes,
            "dist": {str(k): v for k, v in sorted(counts.items())}, "non_x5": non_x5, "verdict": verdict}


def match_coverage(events: list) -> dict:
    """Per-MATCH mu_eff availability (the OPERATIONAL metric for book-selection policy A, NOT the quote-level
    x.5 share): fraction of events with >=1 book carrying BOTH h2h AND an x.5 totals line. Uses the SAME
    `_totals_of` + `is_half_line` as parse_event's selection -> the count it reports is exactly what the
    engine will recover."""
    usable = 0
    for ev in events:
        for bk in ev.get("bookmakers", []):
            if _market(bk, "h2h"):
                t = _totals_of(bk)
                if t and is_half_line(t.get("line")):
                    usable += 1
                    break
    n = len(events)
    return {"n_events": n, "n_mu_eff_usable": usable, "fraction": round(usable / n, 4) if n else 0.0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P4c line-distribution + per-match coverage probe.")
    ap.add_argument("--snapshot", help="replay a saved probe snapshot (no live call / no quota burned)")
    args = ap.parse_args(argv)

    if args.snapshot:
        payload = load_snapshot(args.snapshot)
        events = payload.get("events", [])
        prov = payload.get("provenance", {})
        ok, status, src_label = True, "replay", "snapshot"
    else:
        res = fetch_live(markets="h2h,totals")
        events = res.get("events", [])
        prov = res["provenance"]
        ok, status, src_label = res["ok"], res["status"], "live"

    dist = line_distribution(events)
    cov = match_coverage(events)
    line_artifact = (args.snapshot if args.snapshot
                     else snapshot({"events": events, "provenance": prov, "distribution": dist,
                                    "coverage": cov}, "probe_lines"))
    cov_artifact = snapshot({"provenance": prov, "coverage": cov, "distribution": dist}, "probe_coverage")

    print("=" * 78)
    print("P4c LINE-DISTRIBUTION + COVERAGE PROBE - The Odds API soccer_fifa_world_cup (h2h,totals)")
    print(f"  ok={ok} status={status} source={src_label} fetched_utc={prov.get('fetched_utc')}")
    if not ok:
        print("  fetch FAILED. No quota spent on parse; re-run when reachable.")
    print(f"  events={dist['n_events']}  events_with_totals={dist['n_with_totals']}"
          f"  total_line_quotes={dist['n_quotes']}")
    print("  line distribution (line -> count across all books):")
    if dist["dist"]:
        for line, c in dist["dist"].items():
            tag = "x.5" if is_half_line(float(line)) else "NON-x.5"
            print(f"    {float(line):>5.2f}  x{c:<5} [{tag}]")
    else:
        print("    (none - totals not posted yet)")
    print(f"  non_x5 lines: {dist['non_x5'] or 'none'}")
    print("-" * 78)
    print("PER-MATCH mu_eff COVERAGE (book-selection A: >=1 book with h2h + x.5 totals):")
    print(f"  usable = {cov['n_mu_eff_usable']}/{cov['n_events']} = {cov['fraction'] * 100:.1f}% of matches")
    print(f"  artifacts: {line_artifact}  +  {cov_artifact}")
    print("-" * 78)
    v = dist["verdict"]
    if v == "ALL_X5":
        print("LINE VERDICT = ALL_X5 -> every live line is x.5.")
    elif v == "NON_X5_PRESENT":
        print("LINE VERDICT = NON_X5_PRESENT -> book-selection (A) prefers an x.5 book per match; non-x.5-only")
        print("  matches fall to totals-blind (hard-flagged). The run_matchday x.5 guard is defense-in-depth.")
    else:
        print("LINE VERDICT = NO_TOTALS_YET -> totals not posted; re-probe nearer kickoff.")
    cf = cov["fraction"]
    if cov["n_events"]:
        gate = ("HIGH -> policy A is cheap (most matches keep mu_eff)." if cf >= 0.8 else
                ("MODERATE." if cf >= 0.5 else
                 "LOW -> seek another totals source (SEPARATE GO); do NOT switch to cross-book B."))
        print(f"COVERAGE GATE: {cf * 100:.1f}% -> {gate}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
