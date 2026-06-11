"""A3 council - council/run_council.py : 5-lens triangulation over the 4 ENGINE locked picks.

MASTER §7a: 5 ISOLATED lenses (1 Market/de-vig . 2 Form/quality . 3 Tactical/lineup . 4 Base-rate/historical
. 5 Contrarian/game-theory) form their views INDEPENDENTLY (independent-then-aggregate, NOT debate -> R7).
The lens RESEARCH is gathered by the orchestrator via the Agent tool (isolated contexts, web search, no API
key) and SNAPSHOTTED, dated + sourced, to council/outputs/lenses_<award>.json. THIS module is the
DETERMINISTIC synthesis over those snapshots: per award it prints median + spread + dissent + a
council-vs-market leverage note, and emits a council-informed P_true for the engine (P4).

Determinism = reproducible PIPELINE: the agent outputs are timestamped snapshots; the synthesis math here is
deterministic and unit-tested (_selftest). RESEARCH ONLY: the lenses inform; they NEVER produce a forecast
number that bypasses the engine. The engine (pool/podium_montecarlo.py) + observed ownership (P4) decides.
RECOMMEND, NEVER LOCK. top-assister is DEFERRED to the Jun-11 pass (2026-06-05 scope) -> not run here.

CONSENSUS RULE (declared, explicit): `consensus` = the MEDIAN-LEADER (argmax of per-candidate median across
lenses). The VOTE signal is reported SEPARATELY as `vote_verdict` (majority = a candidate is the top pick of
> n/2 lenses; plurality = a unique top vote-getter with <= n/2; no-majority = a TIE for top). A pick is
flagged `contested` when there is no vote majority OR the median-leader differs from the plurality. A tie is
NEVER collapsed to a single winner silently.

DIVERGENCE vs §7b LEVERAGE (do NOT conflate): `leverage_council_vs_market` = council_median / market (both on
the reference-candidate basis) is a council-vs-MARKET DIVERGENCE signal only. It is NOT the §7b decision
leverage (= P_true / OWNERSHIP), which governs the chalk-vs-contrarian flip and is computed at P4.

Pure stdlib + numpy. Awards reuse pool.leverage de-vig (single book-set, RB3).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pool.leverage import american_to_prob, devig  # noqa: E402

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# The 4 ENGINE picks (assister deferred to Jun-11). Each maps to its market odds file (primary book-set).
AWARDS = {
    "champion":   {"file": "data/outrights.json", "kind": "team"},
    "top_scorer": {"file": "data/props_top_scorer.json", "kind": "player"},
    "mvp":        {"file": "data/props_mvp.json", "kind": "player"},
    "best_gk":    {"file": "data/props_best_gk.json", "kind": "player"},
}

# 5 isolated lenses (key + display name + the independent angle each must take).
LENSES = [
    {"key": "market",     "name": "Market / de-vig",        "angle": "de-vig the futures board(s); the market consensus is the prior"},
    {"key": "form",       "name": "Form / quality",          "angle": "recent club+international form, goals/assists/clean-sheet rate, role security"},
    {"key": "tactical",   "name": "Tactical / lineup",       "angle": "starting role, set-piece/penalty duty, team style, fixture path / expected minutes"},
    {"key": "baserate",   "name": "Base-rate / historical",  "angle": "historical WC base rates for the award (who tends to win it, from which teams/positions)"},
    {"key": "contrarian", "name": "Contrarian / game-theory","angle": "where is the crowd over/under-betting; uniqueness value, NOT just the favourite"},
]
LENS_KEYS = [le["key"] for le in LENSES]


def market_p_true(award: str, top_n: int = 6, path: str | None = None):
    """De-vig an award's PRIMARY board -> named-normalized P_true (L4: tail excluded). Returns
    (p_true:{name:prob} over ALL named, top:[name...] top_n by prob, meta:{source,as_of,coverage}).

    path: override the board file (lock-run dated snapshots, e.g. data/outrights_2026-06-10.json). When
    None (default) the undated AWARDS[award]["file"] is used -> existing behavior is byte-for-byte preserved."""
    path = path if path is not None else os.path.join(ROOT, AWARDS[award]["file"])
    data = json.load(open(path, encoding="utf-8"))
    odds = data["primary"]["odds"]
    implied = {k: american_to_prob(v) for k, v in odds.items()}
    coverage = sum(implied.values())          # vig net of truncated tail (see PODIUM-2); NOT a clean overround
    p_true, _ = devig(implied)                # proportional normalize over named set -> sum 1 (L4)
    top = sorted(p_true, key=lambda c: -p_true[c])[:top_n]
    meta = {"source": data["primary"]["source"], "as_of": data["primary"].get("as_of", data.get("as_of")),
            "named_coverage": round(coverage, 4)}
    return p_true, top, meta


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def _normalize(d):
    tot = sum(d.values())
    return {k: v / tot for k, v in d.items()} if tot > 0 else dict(d)


def synthesize(award: str, market: dict, candidates: list, lens_rows: list) -> dict:
    """Aggregate the 5 lenses for one award. lens_rows = [{lens, probs:{cand:prob}, top, rationale, sources}].

    Each lens's probs are normalized over the reference `candidates` (named-only, like `market`) so council
    and market are apples-to-apples. Per candidate: median + (min,max) spread across lenses. consensus =
    highest median. dissent = lenses whose top pick != consensus. leverage = council_median / market (the
    council-vs-MARKET divergence; the ownership leverage comes at P4)."""
    norm = {}
    for row in lens_rows:
        sub = {c: float(row["probs"].get(c, 0.0)) for c in candidates}
        norm[row["lens"]] = _normalize(sub)

    per_cand = {c: [norm[le][c] for le in norm] for c in candidates}
    med = {c: _median(per_cand[c]) for c in candidates}
    spread = {c: (min(per_cand[c]), max(per_cand[c])) for c in candidates}
    consensus = max(candidates, key=lambda c: med[c])   # median-leader; declared tiebreak = highest median

    votes = {}
    for row in lens_rows:
        votes[row["top"]] = votes.get(row["top"], 0) + 1
    dissent = [{"lens": row["lens"], "top": row["top"]} for row in lens_rows if row["top"] != consensus]

    # Vote signal (explicit — never force a tie to one label). majority = top pick of > n/2 lenses;
    # plurality = unique top vote-getter with <= n/2; no-majority = a tie for top.
    n = len(lens_rows)
    max_votes = max(votes.values()) if votes else 0
    plurality = sorted([c for c, v in votes.items() if v == max_votes])
    if max_votes > n / 2:
        vote_verdict = "majority"
    elif len(plurality) > 1:
        vote_verdict = "no-majority"
    else:
        vote_verdict = "plurality"
    contested = (vote_verdict != "majority") or (consensus not in plurality)

    council_p_true = _normalize(med)          # council-informed P_true over the reference set (feeds P4)
    # APPLES-TO-APPLES: the council median is normalized over the 6 reference candidates, so the market must
    # be too. Comparing to the FULL-board P_true (champion=48 teams, scorer=19 names) would inflate leverage
    # uniformly (a pure renormalization artifact, not real divergence).
    market_ref = _normalize({c: market.get(c, 0.0) for c in candidates})   # market on the SAME 6-cand basis
    mkt_c = market_ref.get(consensus, 0.0)
    leverage = (med[consensus] / mkt_c) if mkt_c > 0 else float("inf")

    return {
        "award": award, "candidates": candidates,
        "consensus": consensus,
        "median": med, "spread": spread,
        "votes": votes, "dissent": dissent,
        "plurality": plurality, "vote_verdict": vote_verdict, "contested": contested,
        "council_p_true": council_p_true,
        "market_ref": market_ref,                                    # market renormalized over the 6 (comparable)
        "market_full": {c: market.get(c, 0.0) for c in candidates},  # full-board P_true (tail incl.) = engine input
        "leverage_council_vs_market": leverage,                      # DIVERGENCE signal, NOT §7b ownership leverage
        "n_lenses": len(lens_rows),
    }


def print_report(syn: dict, meta: dict):
    a = syn["award"]
    print("=" * 84)
    print(f"COUNCIL SYNTHESIS - {a}   (market: {meta['source']}, as_of {meta['as_of']}, "
          f"named-coverage {meta['named_coverage']})   [{syn['n_lenses']} lenses]")
    print("-" * 84)
    print(f"  (mkt(ref) = market de-vig renormalized over these 6, comparable to council med; "
          f"full-board P_true noted below)")
    print(f"{'candidate':<20}{'mkt(ref)':>9}{'council med':>13}{'spread (min-max)':>22}")
    for c in sorted(syn["candidates"], key=lambda x: -syn["median"][x]):
        lo, hi = syn["spread"][c]
        print(f"{c:<20}{syn['market_ref'][c]:>9.3f}{syn['median'][c]:>13.3f}{f'{lo:.3f}-{hi:.3f}':>22}")
    print("-" * 84)
    cons = syn["consensus"]
    tag = "  [CONTESTED]" if syn["contested"] else ""
    print(f"MEDIAN-LEADER: {cons}{tag}   full-board market P_true({cons})={syn['market_full'][cons]:.3f}")
    vv = syn["vote_verdict"]
    extra = f" (top tie among {syn['plurality']})" if vv == "no-majority" else ""
    print(f"  votes={syn['votes']}  ->  {vv.upper()}{extra}")
    print(f"  council-vs-market DIVERGENCE (ref-basis; NOT the §7b P_true/ownership leverage) = "
          f"{syn['leverage_council_vs_market']:.2f}x "
          f"({'council > market' if syn['leverage_council_vs_market'] > 1 else 'council <= market'})")
    if syn["dissent"]:
        diss = ", ".join(f"{d['lens']}->{d['top']}" for d in syn["dissent"])
        print(f"DISSENT ({len(syn['dissent'])}/{syn['n_lenses']}): {diss}")
    else:
        print("DISSENT: none (all lenses agree on the consensus pick)")
    print("🛑 DRAFT / GATED - council triangulation only, NOT a lock. Engine + ownership (P4) decides.")
    print("=" * 84)


def load_and_run(top_n: int = 6):
    """Load council/outputs/lenses_<award>.json snapshots and print the synthesis per engine award."""
    any_loaded = False
    for award in AWARDS:
        path = os.path.join(OUTPUTS_DIR, f"lenses_{award}.json")
        if not os.path.exists(path):
            print(f"[skip] {award}: no lens snapshot at {path} (run the Agent-tool lenses first)")
            continue
        any_loaded = True
        snap = json.load(open(path, encoding="utf-8"))
        market, top, meta = market_p_true(award, top_n=top_n)
        candidates = snap.get("candidates", top)
        syn = synthesize(award, market, candidates, snap["lenses"])
        print_report(syn, meta)
    if not any_loaded:
        print("No lens snapshots found. Gather the 5 lenses via the Agent tool -> "
              "council/outputs/lenses_<award>.json, then re-run.")


# --------------------------------------------------------------------------------------------------
# SELFTEST: deterministic synthesis math on synthetic lens rows (median / spread / dissent / leverage).
# --------------------------------------------------------------------------------------------------
def _selftest():
    cands = ["A", "B", "C"]
    market = {"A": 0.50, "B": 0.30, "C": 0.20}
    # 4 lenses back A, 1 dissents to B. Median should pick A; dissent lists the B lens.
    rows = [
        {"lens": "market",     "probs": {"A": 0.50, "B": 0.30, "C": 0.20}, "top": "A", "rationale": "x", "sources": []},
        {"lens": "form",       "probs": {"A": 0.60, "B": 0.25, "C": 0.15}, "top": "A", "rationale": "x", "sources": []},
        {"lens": "tactical",   "probs": {"A": 0.55, "B": 0.30, "C": 0.15}, "top": "A", "rationale": "x", "sources": []},
        {"lens": "baserate",   "probs": {"A": 0.45, "B": 0.35, "C": 0.20}, "top": "A", "rationale": "x", "sources": []},
        {"lens": "contrarian", "probs": {"A": 0.20, "B": 0.55, "C": 0.25}, "top": "B", "rationale": "x", "sources": []},
    ]
    syn = synthesize("test", market, cands, rows)
    print("council SELFTEST")
    print(f"  consensus={syn['consensus']} (expect A)  votes={syn['votes']}")
    print(f"  median A={syn['median']['A']:.3f}  spread A={syn['spread']['A']}")
    print(f"  dissent={syn['dissent']}")
    print(f"  council_p_true sums to {sum(syn['council_p_true'].values()):.6f}")
    print(f"  leverage council/market (A) = {syn['leverage_council_vs_market']:.3f}")
    assert syn["consensus"] == "A", syn["consensus"]
    assert syn["votes"] == {"A": 4, "B": 1}, syn["votes"]
    assert len(syn["dissent"]) == 1 and syn["dissent"][0]["lens"] == "contrarian", syn["dissent"]
    assert abs(syn["median"]["A"] - 0.50) < 1e-9, syn["median"]["A"]      # median of {.50,.60,.55,.45,.20}=.50
    assert abs(sum(syn["council_p_true"].values()) - 1.0) < 1e-9
    # all-agree case -> no dissent
    rows2 = [dict(r, top="A", probs={"A": 0.6, "B": 0.3, "C": 0.1}) for r in rows]
    syn2 = synthesize("test2", market, cands, rows2)
    assert syn2["dissent"] == [], syn2["dissent"]
    print("SELFTEST: PASS  (consensus, vote tally, dissent detection, median, normalized council P_true)")
    return syn


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--selftest" in sys.argv:
        _selftest()
    elif "--candidates" in sys.argv:
        for award in AWARDS:
            _p, top, meta = market_p_true(award)
            print(f"{award:<12} top-6 = {top}   (src {meta['source'].split(' (')[0]})")
    else:
        load_and_run()


if __name__ == "__main__":
    main()
