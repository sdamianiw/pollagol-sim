"""A1 - leverage SCREEN for the locked CHAMPION pick (Chalk-vs-Contrarian, step 1).

de-vig outright odds -> P_true ; leverage = P_true / ownership, EMITTED ONLY where ownership
is defensible. Per-team ownership is NOT derivable from P_true (see tasks/lessons.md L4), so:
  - prior ownership exists for the §7b NAMED set only; the tail's leverage is UNDEFINED (None).
  - contrarian candidates are therefore a subset of the named set.
Data: data/outrights.json (web-sourced; API-Football free tier cannot serve WC-2026, memory/rules.md).
Pure stdlib.

ownership_source (observed | polled | prior). DEFAULT = prior.
PICKS_VISIBLE = True (pollaya screenshots, confirmed 2026-06-02: premiation picks ARE visible) =>
`observed` ownership is REAL (measured over opponents' locked picks). HITL GATE: a pick on `prior` is
still gated (is_gated); `observed`/`polled` are measured (the LOCK itself is a human action).
This module SCREENS; A2 (pool_montecarlo) makes the E[prize] decision.
"""
from __future__ import annotations
import json
import sys

MIN_PTRUE_FOR_CONTRARIAN = 0.05   # "non-tiny P_true" gate (§7b decision rule)
LEVERAGE_THRESHOLD = 1.5          # contrarian-lever gate (§7b)

# Pollaya screenshots (2026-05-30, confirmed 2026-06-02): premiation picks ARE visible -> observed is REAL.
PICKS_VISIBLE = True

# §7b chalk-prior ownership for the KNOWN named set (sums to 0.90; the remaining 0.10 of the
# field's ownership mass is genuinely UNKNOWN until polled - we do NOT fabricate a tail split).
OWNERSHIP_PRIOR_NAMED = {
    "Spain": 0.38, "France": 0.32, "England": 0.08, "Brazil": 0.06, "Argentina": 0.06,
}


def is_gated(ownership_source: str) -> bool:
    """A pick built on this ownership source may NOT be finalized without HITL.
    prior = unmeasured chalk default -> gated. observed/polled = MEASURED -> not gated
    (the LOCK itself is still a human action)."""
    return ownership_source == "prior"


def american_to_prob(odds: float) -> float:
    """American moneyline -> raw (vig-inclusive) implied probability."""
    o = float(odds)
    return 100.0 / (o + 100.0) if o > 0 else (-o) / ((-o) + 100.0)


def devig(implied: dict) -> tuple[dict, float]:
    """Proportional (multiplicative) de-vig: normalize raw implied probs to sum 1.

    Returns (p_true, overround) where overround = sum of raw implied probs.
    """
    total = sum(implied.values())
    return {k: v / total for k, v in implied.items()}, total


def ownership_prior(p_true: dict) -> dict:
    """Prior ownership for the NAMED set only (§7b). No tail distribution: per-team ownership
    is not a function of P_true, so the tail is left UNKNOWN (absent => leverage None)."""
    return {t: OWNERSHIP_PRIOR_NAMED[t] for t in OWNERSHIP_PRIOR_NAMED if t in p_true}


def leverage_table(p_true: dict, ownership: dict) -> list[dict]:
    """One row per team. leverage = p_true/own ONLY where ownership is real; else None.
    A contrarian candidate (real leverage > 1.5 and non-tiny P_true) carries its prior-inversion
    break-even note."""
    rows = []
    for t, p in p_true.items():
        own = ownership.get(t)
        lev = (p / own) if (own is not None and own > 0) else None
        candidate = lev is not None and lev > LEVERAGE_THRESHOLD and p >= MIN_PTRUE_FOR_CONTRARIAN
        note = None
        if candidate:
            breakeven = p / LEVERAGE_THRESHOLD
            note = (f"leverage {lev:.2f} conditional on prior own={own:.1%}; inverts to <=1.5 (chalk) "
                    f"if true own >= {breakeven:.1%} -> POLL before A2")
        rows.append({"team": t, "p_true": p, "ownership": own, "leverage": lev,
                     "contrarian_candidate": candidate, "note": note})
    # highest leverage first; UNDEFINED (None) leverage sorts last.
    rows.sort(key=lambda r: (r["leverage"] is None, -(r["leverage"] if r["leverage"] is not None else 0.0)))
    return rows


def load_outrights(path="data/outrights.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute(path="data/outrights.json", ownership_source="prior", ownership_override=None, gamma=2.0):
    """Returns (p_true, ownership, overround, rows, data).

    gamma is accepted but INERT (regression guard; it MUST NOT influence candidate selection -
    see A1 REMEDIATION H1). The real A2/R9 sweep variable is the named ownership vector.
    """
    data = load_outrights(path)
    book = data["primary"]
    implied = {t: american_to_prob(o) for t, o in book["odds"].items()}
    p_true, overround = devig(implied)

    if ownership_source == "prior":
        ownership = ownership_prior(p_true)
    elif ownership_source == "observed":
        if not PICKS_VISIBLE:
            raise NotImplementedError(
                "observed ownership unavailable: pollaya exposes no participant picks "
                "[PENDING VERIFICATION]; use polled or prior")
        if ownership_override is None:
            raise ValueError("observed ownership requires ownership_override")
        ownership = ownership_override
    elif ownership_source == "polled":
        if ownership_override is None:
            raise ValueError("polled ownership requires ownership_override (the polled pick shares)")
        ownership = ownership_override
    else:
        raise ValueError(f"unknown ownership_source: {ownership_source}")

    return p_true, ownership, overround, leverage_table(p_true, ownership), data


def _selftest():
    assert abs(american_to_prob(100) - 0.5) < 1e-12
    assert abs(american_to_prob(-200) - 2 / 3) < 1e-12
    pt, tot = devig({"A": 0.6, "B": 0.6})           # overround 1.2 -> {0.5, 0.5}
    assert abs(tot - 1.2) < 1e-12
    assert abs(pt["A"] - 0.5) < 1e-12 and abs(sum(pt.values()) - 1.0) < 1e-12
    assert abs(leverage_table({"X": 0.10}, {"X": 0.06})[0]["leverage"] - 0.10 / 0.06) < 1e-12
    assert leverage_table({"Y": 0.10}, {})[0]["leverage"] is None    # no ownership -> UNDEFINED
    print("self-test: PASS")


def _fmt_lev(lev):
    return "UNDEFINED" if lev is None else f"{lev:.2f}"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _selftest()

    p_true, ownership, overround, rows, data = compute(ownership_source="prior")
    assert abs(sum(p_true.values()) - 1.0) < 1e-9, "P_true must sum to 1"

    print("=" * 80)
    print(f"A1 LEVERAGE SCREEN (CHAMPION)   ownership_source = prior   PICKS_VISIBLE = {PICKS_VISIBLE}")
    print(f"primary odds: {data['primary']['source']}  as_of {data.get('as_of')}  "
          f"overround={overround:.3f}  field={len(p_true)} teams")
    print("=" * 80)
    print(f"DECISION RULE [ownership_source=prior, PICKS_VISIBLE={PICKS_VISIBLE}]:")
    print("  Champion pick DEFAULTS CHALK-LEANING (small-pool §7c + no measured leverage denominator).")
    print("  A contrarian champion is justified ONLY IF: POLLED ownership in hand")
    print("  AND leverage > 1.5 AND A2 Monte Carlo E[prize] > chalk.")
    print("  Until polled: chalk champion, separate via per-match EV (Track B). FINALIZATION GATED.")
    print("-" * 80)

    credible = [r for r in rows if r["p_true"] >= MIN_PTRUE_FOR_CONTRARIAN]
    print(f"credible champions (P_true >= {MIN_PTRUE_FOR_CONTRARIAN:.0%}):")
    print(f"{'team':<14}{'P_true':>9}{'own':>11}{'leverage':>11}   status")
    for r in credible:
        if r["ownership"] is None:
            own_s, status = "UNKNOWN", "needs polled ownership"
        elif r["contrarian_candidate"]:
            own_s, status = f"{r['ownership']*100:.2f}%", "<= CONDITIONAL contrarian candidate"
        elif r["leverage"] is not None and r["leverage"] < 1:
            own_s, status = f"{r['ownership']*100:.2f}%", "chalk (over-owned)"
        else:
            own_s, status = f"{r['ownership']*100:.2f}%", ""
        print(f"{r['team']:<14}{r['p_true']*100:>8.2f}%{own_s:>11}{_fmt_lev(r['leverage']):>11}   {status}")
    n_tail = len(rows) - len(credible)
    print(f"... {n_tail} tail teams (P_true < {MIN_PTRUE_FOR_CONTRARIAN:.0%}): leverage UNDEFINED "
          f"(no defensible ownership; un-pickable darkhorses).")

    # candidate notes (break-even) ------------------------------------------------------
    cands = [r for r in rows if r["contrarian_candidate"]]
    print("-" * 80)
    print(f"contrarian candidates (named set only): {[r['team'] for r in cands] or '(none)'}")
    for r in cands:
        print(f"  {r['team']}: {r['note']}")

    # HAND-CHECK with the REAL de-vig number (plumbing, not a placeholder) ---------------
    o_spain = data["primary"]["odds"]["Spain"]
    implied_spain = american_to_prob(o_spain)
    hand = implied_spain / overround
    print("-" * 80)
    print(f"HAND-CHECK Spain: implied 100/({o_spain}+100)={implied_spain:.4f}; "
          f"P_true={implied_spain:.4f}/{overround:.3f}={hand:.4f}  == pipeline {p_true['Spain']:.4f} "
          f"-> {abs(hand - p_true['Spain']) < 1e-12}")

    # CROSS-CHECK favorites vs 2nd source (>=2 sources on critical inputs) ---------------
    cc = data.get("crosscheck", {})
    if cc:
        print("-" * 80)
        print(f"CROSS-CHECK favorites  {data['primary']['source']}  vs  {cc['source']}  ({data.get('as_of')})")
        for t in ["Spain", "France", "England", "Brazil", "Argentina", "Portugal", "Germany"]:
            a, b = data["primary"]["odds"].get(t), cc["odds"].get(t)
            print(f"  {t:<10} {'+%d' % a if a else '-':>8}  vs  {'+%d' % b if b else '-':>8}")

    print("-" * 80)
    print("GATE: ownership_source=prior -> DRAFT only. POLL the field (champion now; rest after Jun-2")
    print("      squads) -> ownership_source=polled, then A2 decides via E[prize] + R9 sweep. FINALIZATION GATED.")
    print("=" * 80)


if __name__ == "__main__":
    main()
