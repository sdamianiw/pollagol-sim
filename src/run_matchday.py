"""M8 run_matchday - per-match orchestrator (Track B, P4c).

Wires the LIVE per-match engine end-to-end: M1 ingest -> M2 strength -> M3 Dixon-Coles (mu_eff) ->
M5 context -> M4 argmax E[points] -> human summary. DRY-RUN ONLY: prints the scoreline table, the EV pick,
the modal (chalk) score it diverges from (the "EV-vs-modal gap"; not leverage, per-match ownership is
hidden), the sources/flags, then STOPs. NEVER submits,
NEVER locks - HITL (--submit is intentionally disabled).

x.5 GUARD (H1 / P4c): poisson_over_prob/mu_from_pover (src/model.py, FROZEN) are correct ONLY for
half-lines (x.5). The LIVE WC board carries integer/quarter lines too (src/probe_lines.py verdict
NON_X5_PRESENT, 2026-06-06). On a non-x.5 totals PRICE this STOPs the match (never coerces to 2.5) and
surfaces the Sebas decision: restrict to x.5, or add an independent push/split oracle.

OFFLINE PURITY: imports only src/ (M1-M5; pool/ de-vig via M2) - NEVER evals/ (M7, the backtest).
SNAPSHOT-REPRODUCIBLE: --snapshot replays a saved event; the per-match pipeline is deterministic (no RNG)
-> same snapshot => byte-identical summary. <60s/match by construction (one API call + closed-form DC).
Stdlib + numpy.
"""
from __future__ import annotations
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np

# Windows consoles default to cp1252; force utf-8 so the STOP banner (unicode) never crashes a run.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from src.ingest import fetch_live, parse_event, snapshot, load_snapshot
from src.strength import match_strength
from src.model import match_distribution, implied_1x2, mu_from_pover, TOTAL_LINE
from src.context import apply_context
from src.optimizer import optimize
from src.variance_select import select as select_variance   # ANNEX V dial (default OFF; BUILD != FIRE)
from src.lines import is_half_line

DEFAULT_CONTEXT = "neutral"   # WC group = neutral venue (CONTEXT_RULES; documented §5 assumption, SOURCED)
DEFAULT_CONTEXT_SOURCE = "WC group stage = neutral venue (memory/rules.md §5; documented)"


class LineGuardStop(Exception):
    """Raised when a non-x.5 totals line would feed the FROZEN mu_eff path (H1) - STOP, never coerce."""


def guard_total_line(strength: dict, fixture_id: str) -> None:
    """x.5 guard: STOP if the totals PRICE is present on a non-half-line. NEVER coerces to 2.5."""
    p_over, line = strength.get("p_over"), strength.get("total_line")
    if p_over is not None and not is_half_line(line):
        raise LineGuardStop(
            f"match {fixture_id}: totals line {line} is NON-x.5 -> mu_from_pover/poisson_over_prob collapse "
            f"it via floor(line)+1 and ignore push/split (H1). STOP - no 2.5 coercion. Sebas decides: "
            f"(a) restrict the mu_eff path to x.5 only, or (b) add an independent push/split oracle "
            f"(see src/probe_lines.py: live board is NON_X5_PRESENT)."
        )


def guard_favorite_inversion(strength: dict, matrix: np.ndarray, fixture_id: str) -> dict:
    """L17 output-layer guard: flag when the DC matrix-implied favorite disagrees with the de-vigged
    h2h MARKET favorite. On near-even/high-draw fixtures the 1-constraint fit under-produces draws and
    leaks the missing mass onto the away side, inverting the margin (measured on KOR-CZE, 2026-06-09).
    DETECTION ONLY: returns a status dict, NEVER mutates the pick, NEVER raises (anti-tuning - Sebas
    decides). Compares the PRE-context matrix (the DC output L17 indicts, not the M5-adjusted one). A
    non-market (Elo) source has no h2h favorite to compare -> fired=False. The ρ-fit ROOT fix is a
    separate post-lock GO (L19); this guard only surfaces the disagreement to the HITL."""
    if strength.get("source") != "market":
        return {"fired": False, "reason": "non-market source (no h2h favorite to compare)"}
    dv = strength["probs"]
    im = implied_1x2(matrix)
    dv_fav = "home" if dv["home"] > dv["away"] else "away"
    matrix_fav = "home" if im["home"] > im["away"] else "away"
    return {"fired": dv_fav != matrix_fav, "dv_fav": dv_fav, "matrix_fav": matrix_fav,
            "dv_home": round(dv["home"], 5), "dv_away": round(dv["away"], 5),
            "matrix_home": round(im["home"], 5), "matrix_away": round(im["away"], 5)}


def _modal(matrix: np.ndarray) -> tuple[int, int]:
    idx = np.unravel_index(int(np.argmax(matrix)), matrix.shape)
    return int(idx[0]), int(idx[1])


def run_match(event: dict, fmt: str = "american", context_flags=DEFAULT_CONTEXT,
              context_source: str = DEFAULT_CONTEXT_SOURCE, variance_lam: float = 0.0) -> dict:
    """One match through M1(parse) -> M2 -> [x.5 guard] -> M3(mu_eff) -> M5 context -> M4 argmax.

    Returns a summary dict. Raises LineGuardStop on a non-x.5 totals line (H1).
    Data-flow note: M5 (context) adjusts the DISTRIBUTION before M4 (argmax) - the working e2e order
    M3->M5->M4, not the literal 'M4->M5' shorthand in the contract.
    ANNEX V (BUILD != FIRE): `variance_lam` defaults to 0.0 -> the pure E[pts] argmax (byte-identical); a
    > 0 lambda swaps in the variance/P(top-3) mean-variance dial (src/variance_select). Firing is gated by
    the deferred activation gate (post-MD3), never by this call alone.
    """
    match = parse_event(event, fmt)
    strength = match_strength(match)
    guard_total_line(strength, match["fixture_id"])                 # x.5 guard BEFORE the mu_eff path
    matrix = match_distribution(strength)                           # M3 (mu_eff recovered inside if p_over)
    inv_guard = guard_favorite_inversion(strength, matrix, match["fixture_id"])   # L17 detection (PRE-context)
    adj, context_flag = apply_context(matrix, context_flags, source=context_source)   # M5 before M4
    # M4 selection. DEFAULT (variance_lam=0.0) = argmax E[points] (byte-identical, the live path). ANNEX V:
    # a > 0 lambda swaps in the variance/P(top-3) mean-variance dial - BUILD-NOT-FIRE, gated post-MD3.
    opt = select_variance(adj, variance_lam) if variance_lam else optimize(adj)   # M4 argmax E[points]
    mu_eff = (mu_from_pover(strength["p_over"], strength["total_line"] or TOTAL_LINE)
              if strength["p_over"] is not None else None)
    return {"match": match, "strength": strength, "mu_eff": mu_eff, "context_flag": context_flag,
            "matrix": adj, "opt": opt, "modal": _modal(adj), "inversion_guard": inv_guard}


def _fmt_score(s) -> str:
    return f"{s[0]}-{s[1]}"


def print_summary(summary: dict, snapshot_path: str | None = None) -> None:
    m, st, opt = summary["match"], summary["strength"], summary["opt"]
    adj, pick, modal = summary["matrix"], opt["pick"], summary["modal"]
    pick_p, modal_p = float(adj[pick]), float(adj[modal])
    divergent = pick != modal

    print("=" * 84)
    print(f"M8 run_matchday  DRY-RUN  -  {m['home']} vs {m['away']}")
    print(f"  fixture={m['fixture_id']}  commence={m.get('commence_time')}  fmt={m['fmt']}")
    # --- sources / flags ---
    print("-" * 84)
    print("SOURCES / FLAGS:")
    print(f"  M2 source={st['source']}  primary_book={m.get('primary_book')}  books={m.get('books')}")
    bs = m.get("book_selection")
    if bs:
        print(f"  book-selection: {bs['text']}  (h2h_book={bs['h2h_book']}, totals_book={bs['totals_book']})")
    if st.get("overround") is not None:
        print(f"  overround={st['overround']:.4f}  de-vigged 1X2="
              f"{{H:{st['probs']['home']:.3f} D:{st['probs']['draw']:.3f} A:{st['probs']['away']:.3f}}}")
    if st.get("p_over") is not None:
        print(f"  totals: line={st['total_line']} (x.5 OK)  p_over={st['p_over']:.3f}  "
              f"mu_eff={summary['mu_eff']:.4f}  [M3 totals-aware]")
    else:
        print("  totals: none -> M3 nested-solve (no mu_eff); totals signal unavailable")
    cf = summary["context_flag"]
    print(f"  M5 context: {cf['text']}  (flags={cf['flags']}, source={cf['source']}, "
          f"mu_x{cf['mu_factor']}, var_x{cf['variance_factor']})")
    ig = summary.get("inversion_guard", {})
    if ig.get("fired"):
        fav_team = {"home": m["home"], "away": m["away"]}
        print(f"  ⚠ FAVORITE-INVERSION (L17): matrix favors {fav_team[ig['matrix_fav']]} "
              f"(H={ig['matrix_home']:.4f} A={ig['matrix_away']:.4f}), market favors {fav_team[ig['dv_fav']]} "
              f"(H={ig['dv_home']:.4f} A={ig['dv_away']:.4f}) -> HITL override required; "
              f"modal alt: {_fmt_score(modal)}")
    elif ig:
        print("  inversion-guard: clean (matrix favorite == market favorite)")
    if snapshot_path:
        print(f"  snapshot (reproducible): {snapshot_path}")
    # --- scoreline table (top EV) ---
    print("-" * 84)
    print("E[points] TABLE (top, plausibility-floored):")
    print(f"  {'score':>6} {'E[pts]':>8} {'P(score)':>9}")
    for row in opt["table"][:6]:
        print(f"  {_fmt_score(row['pred']):>6} {row['ev']:>8.3f} {row['p']:>9.4f}")
    # --- pick vs chalk (the EV-vs-modal gap) ---
    print("-" * 84)
    print(f"  EV PICK (argmax E[pts]) : {_fmt_score(pick):>5}   E[pts]={opt['ev']:.3f}  P={pick_p:.4f}")
    print(f"  MODAL / CHALK (most likely): {_fmt_score(modal):>5}   P={modal_p:.4f}")
    gap = "EV-vs-modal GAP: EV pick DIVERGES from the modal score" if divergent else "ALIGNED: EV pick == modal score"
    print(f"  -> {gap}  (per-match ownership hidden -> not leverage-contrarian)")
    # --- HITL STOP ---
    print("=" * 84)
    print("🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.")
    print("   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.")
    print("=" * 84)


def _select_event(data_or_res: dict, fixture: str | None) -> dict:
    """Accept an ingest_event snapshot ({'event':...}) or a multi-event payload ({'events':[...]})."""
    if "event" in data_or_res and isinstance(data_or_res["event"], dict):
        return data_or_res["event"]
    events = data_or_res.get("events") or []
    if not events:
        raise ValueError("no event(s) found in payload")
    if fixture:
        ev = next((e for e in events if e.get("id") == fixture), None)
        if ev is None:
            raise ValueError(f"fixture {fixture!r} not in payload ({len(events)} events)")
        return ev
    return events[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="M8 per-match orchestrator (DRY-RUN, HITL).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--snapshot", help="replay a saved snapshot JSON (deterministic)")
    src.add_argument("--live", action="store_true", help="live fetch from The Odds API (consumes quota)")
    ap.add_argument("--fixture", help="event id to select (multi-event payloads); default = first")
    ap.add_argument("--fmt", default="american", help="odds format (american|decimal)")
    ap.add_argument("--context", default=DEFAULT_CONTEXT, help="M5 context flag (default: neutral)")
    ap.add_argument("--submit", action="store_true", help="(disabled by design - HITL only)")
    args = ap.parse_args(argv)

    if args.submit:
        print("🛑 --submit is disabled by design (HITL). Nothing was submitted or locked.")
        return 2

    snap_path = None
    if args.snapshot:
        payload = load_snapshot(args.snapshot)
        event = _select_event(payload, args.fixture)
        snap_path = args.snapshot
    else:
        res = fetch_live(markets="h2h,totals")
        if not res["ok"]:
            print(f"🛑 live fetch failed (status={res['status']}, {res.get('error')}). "
                  f"Fall back to --snapshot <cached>. Nothing locked.")
            return 1
        event = _select_event(res, args.fixture)
        snap_path = snapshot({"event": event, "provenance": res["provenance"]}, event.get("id", "live"))

    try:
        summary = run_match(event, fmt=args.fmt, context_flags=args.context)
    except LineGuardStop as e:
        print("=" * 84)
        print("🛑 x.5 GUARD STOP - match not scored (no silent 2.5 coercion).")
        print(f"   {e}")
        print("=" * 84)
        return 0
    print_summary(summary, snapshot_path=snap_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
