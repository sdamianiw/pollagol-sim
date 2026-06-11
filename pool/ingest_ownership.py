"""Step 3 - observed champion-ownership ingestion (pollaya, PICKS_VISIBLE=True).

Turn the entrants' VISIBLE champion picks into an ownership vector + explicit pending tracking,
with self-exclusion (you are not your own opponent). Feeds A2 (pool_montecarlo) as
ownership_source="observed". Pure stdlib.

Ownership is over LOCKED OPPONENTS only:  ownership[team] = locked_for_team / locked_count.
Pending opponents (not yet locked) are the explicit uncertainty: pending_count, sampled in A2 from a
labeled swept prior - SIMULATION ONLY, never to choose your own pick. Provenance: source + UTC.

PODIUM TEST RUN (2026-06-06, observed-ownership model declared in memory/rules.md): the Laplace
smoothing floor below uses the FULL N_opp as denominator (LM1, NOT deciders-only), an additive
alpha over the named candidate set (LM2: K_cand = top-6 union observed), and carries the residual
blank mass on SENTINEL so each per-lever dict sums to 1 (LM3 - required because the joint MC and
_aggregate_ownership re-normalize internally). See pool/run_podium_draft.py for the observed path.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(ROOT, "memory", "rules.md")

# Must match pool.podium_montecarlo._SENTINEL (a lever's opponents with no scoring pick -> never matches
# a winner). Defined locally to avoid a circular import (pool_montecarlo imports load_observed from here).
SENTINEL = "__unknown__"


def load_observed(picks: dict, n_total: int, exclude: str | None = None,
                  as_of_utc: str | None = None, source: str = "pollaya screenshot") -> dict:
    """picks: {entrant_name: team or None}. exclude: your own entrant name (self-exclusion).

    n_total counts ALL entrants (incl. self). effective_total = n_total - 1 if excluding self.
    pending_count = effective_total - locked_count (entrants not in `picks` are pending too).
    """
    items = {k: v for k, v in picks.items() if k != exclude}
    locked = {k: v for k, v in items.items() if v is not None}
    counts: dict = {}
    for team in locked.values():
        counts[team] = counts.get(team, 0) + 1
    locked_count = len(locked)
    ownership = {t: c / locked_count for t, c in counts.items()} if locked_count else {}
    effective_total = n_total - (1 if exclude is not None else 0)
    pending_count = effective_total - locked_count
    return {
        "ownership": ownership,
        "raw_counts": dict(counts),          # {team: integer locked count} (Sebas excluded) - for Laplace
        "locked_count": locked_count,
        "pending_count": pending_count,
        "n_total": n_total,
        "effective_total": effective_total,
        "excluded": exclude,
        "as_of_utc": as_of_utc or datetime.now(timezone.utc).isoformat(),
        "source": source,
    }


def ownership_model_declared(path: str = RULES_PATH) -> bool:
    """True iff the `OWNERSHIP_MODEL: declared` sentinel is present in memory/rules.md (anti-FM1 / I3).
    Mirrors pool/sigma_calibration.py's `SIGMA_CAL_MODEL: declared` guard convention."""
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        return re.search(r"^OWNERSHIP_MODEL:\s*declared\s*$", f.read(), re.MULTILINE) is not None


def _assert_ownership_model_declared(path: str = RULES_PATH) -> None:
    if not ownership_model_declared(path):
        raise RuntimeError(
            "OWNERSHIP_MODEL: declared sentinel absent in memory/rules.md - log the LM1/LM2/LM3 "
            "observed-ownership model block BEFORE running the observed path (anti-FM1 / I3).")


def laplace_ownership(raw_counts: dict, n_opp: int, alpha: float = 1.0,
                      candidate_names=None) -> dict:
    """LM1/LM2 Laplace-smoothed ownership over the NAMED set, denominator = N_opp (NOT deciders-only).

    ownership[c] = (count_c + alpha) / (N_opp + alpha * K_cand),  K_cand = |named set|,
    named set = raw_counts keys UNION candidate_names (so 0-pick candidates still get a floor -> finite
    leverage). Returns named shares only (sums to < 1; the blank residual is added by the *_with_residual
    wrapper). alpha and the named set are DECLARED in memory/rules.md and NOT tuned (I3)."""
    assert n_opp >= 1, f"n_opp must be >= 1, got {n_opp}"
    # sorted() (NOT a bare set) so the dict key order is DETERMINISTIC across processes: the joint MC draws
    # opponent picks via rng.choice over list(own.keys()), so a hash-randomized set order (PYTHONHASHSEED)
    # would make the same fixed seed map probabilities to labels differently run-to-run -> MC jitter. Values
    # are order-independent, so this is byte-stable AND leaves every existing hand-check unchanged.
    named = sorted(set(raw_counts) | set(candidate_names or []))
    k_cand = len(named)
    denom = n_opp + alpha * k_cand
    return {c: (raw_counts.get(c, 0) + alpha) / denom for c in named}


def laplace_ownership_with_residual(raw_counts: dict, n_opp: int, alpha: float = 1.0,
                                    candidate_names=None) -> dict:
    """Model A: laplace_ownership + SENTINEL carrying the residual blank mass so the dict SUMS TO 1.0
    (required - the joint MC and _aggregate_ownership both re-normalize internally; a sub-normalized dict
    would wrongly inflate the named shares). Blank opponents pick SENTINEL -> never match a winner."""
    shares = laplace_ownership(raw_counts, n_opp, alpha, candidate_names)
    residual = 1.0 - sum(shares.values())
    assert residual >= -1e-9, (
        f"negative residual {residual}: sum(raw_counts)={sum(raw_counts.values())} > n_opp={n_opp}?")
    out = dict(shares)
    out[SENTINEL] = max(0.0, residual)
    return out


def blanks_chalk_resolved(named_shares: dict, blank_mass: float, p_true: dict) -> dict:
    """Model B (P2-a): redistribute the TRUE-blank mass over the NAMED candidates' P_true, renormalized
    over the named set (NOT the full board), added on top of the Laplace named_shares. No blank SENTINEL.

    Pass only the true-blank mass; any off-board-decider mass stays on SENTINEL (handled by the caller).
    Result sums to sum(named_shares) + blank_mass (== 1.0 when off-board mass is 0)."""
    named = list(named_shares)
    z = sum(p_true.get(c, 0.0) for c in named)
    if z <= 0:                                          # degenerate: no P_true over named -> uniform
        add = {c: blank_mass / len(named) for c in named}
    else:
        add = {c: blank_mass * p_true.get(c, 0.0) / z for c in named}
    return {c: named_shares[c] + add[c] for c in named}


def _expand_picks(raw_counts: dict, n_opp: int, excluded_entrant, excluded_pick) -> dict:
    """Rebuild a per-entrant picks dict from aggregated opponent counts (+ the excluded self pick) so
    load_observed's exclusion + counting are genuinely exercised. n_total = n_opp + 1 (incl. self)."""
    picks, i = {}, 0
    for team, c in raw_counts.items():
        for _ in range(int(c)):
            picks[f"opp_{i}"] = team
            i += 1
    for _ in range(n_opp - i):                          # remaining opponents = blank / undecided
        picks[f"opp_{i}"] = None
        i += 1
    if excluded_entrant is not None:
        picks[excluded_entrant] = excluded_pick         # self: counted, then excluded by load_observed
    return picks


def load_observed_from_snapshot(path: str, board_keys=None) -> dict:
    """Read the observed-ownership snapshot, run load_observed per lever (self EXCLUDED), and resolve each
    observed name against the lever's P_true board.

    board_keys: {lever: set(canonical board names)} for off-board detection (P2-b). A name that resolves
    to a real entity but is off-board is NOT fabricated and NOT raised -> folds into SENTINEL (blank-equiv,
    win~0) with a log; only a malformed/empty token raises (typo guard). Advisory levers (no P_true board,
    e.g. assister) pass through verbatim. Returns {"snapshot", "n_opp", "levers": {lever: {...}}}."""
    snap = json.load(open(path, encoding="utf-8"))
    n_opp = snap["n_opp"]
    n_total = snap.get("n_total", n_opp + 1)
    assert n_total - 1 == n_opp, f"snapshot inconsistent: n_total({n_total})-1 != n_opp({n_opp})"
    excl = snap.get("excluded_entrant")
    excl_picks = snap.get("excluded_picks", {})
    board_keys = board_keys or {}
    out = {}
    for lever, lv in snap["levers"].items():
        picks = _expand_picks(lv["raw_counts"], n_opp, excl, excl_picks.get(lever))
        lo = load_observed(picks, n_total=n_total, exclude=excl,
                           as_of_utc=snap.get("as_of_utc"),
                           source=snap.get("source", "pollaya screenshot"))
        counts = lo["raw_counts"]
        advisory = bool(lv.get("advisory", False))
        resolved, offboard = {}, {}
        if advisory or lever not in board_keys:
            resolved = dict(counts)                     # no P_true board to resolve against
        else:
            keys = board_keys[lever]
            for team, c in counts.items():
                if not isinstance(team, str) or not team.strip():
                    raise ValueError(f"{lever}: malformed observed token {team!r} (typo?) - fix snapshot")
                if team in keys:
                    resolved[team] = c
                else:
                    offboard[team] = c
                    print(f"  [P2-b] observed pick {team!r} ({lever}) without P_true market -> "
                          f"modeled as blank-equiv (win~0); folded into SENTINEL.")
        out[lever] = {
            "advisory": advisory,
            "resolved_counts": resolved,
            "offboard_counts": offboard,
            "deciders": lo["locked_count"],
            "blanks": lo["pending_count"],
            "n_opp": lo["effective_total"],
            "provenance": {k: lo[k] for k in ("as_of_utc", "source", "excluded")},
        }
    return {"snapshot": snap, "n_opp": n_opp, "levers": out}


def _selftest():
    # Order's synthetic: 2 locked / 10 pending / sums to 1 (no self-exclusion).
    r = load_observed({"a": "Uruguay", "b": "Brasil", "c": None}, 12)
    assert r["locked_count"] == 2 and r["pending_count"] == 10, r
    assert abs(sum(r["ownership"].values()) - 1.0) < 1e-9, r
    # Real today (Sebas='b'=Brasil placeholder, exclude self): field = {Uruguay:1.0}, locked 1, pending 10.
    r2 = load_observed({"a": "Uruguay", "b": "Brasil", "c": None}, 12, exclude="b")
    assert r2["ownership"] == {"Uruguay": 1.0} and r2["locked_count"] == 1 and r2["pending_count"] == 10, r2
    assert r2["raw_counts"] == {"Uruguay": 1}, r2

    # --- PODIUM TEST RUN: declared-model gate + Laplace floor (champion shape: 7 deciders / 12 blanks) ---
    assert ownership_model_declared(), "OWNERSHIP_MODEL: declared sentinel missing in memory/rules.md"
    champ_counts = {"Brazil": 2, "Portugal": 2, "Spain": 2, "Uruguay": 1}
    champ_named = ["Spain", "France", "England", "Brazil", "Argentina", "Portugal", "Uruguay"]  # K_cand=7
    own_a = laplace_ownership_with_residual(champ_counts, n_opp=19, alpha=1.0, candidate_names=champ_named)
    assert abs(own_a["Spain"] - 3 / 26) < 1e-12 and abs(own_a["France"] - 1 / 26) < 1e-12, own_a   # hand-check
    assert abs(sum(own_a.values()) - 1.0) < 1e-9, own_a                                            # sums to 1
    assert all(v > 0 for v in own_a.values()), own_a                                               # no inf leverage
    assert abs(own_a[SENTINEL] - 12 / 26) < 1e-12, own_a                                           # 12 blanks
    # Model B (P2-a): redistribute the blank mass over named P_true (renormalized over named) -> still sums to 1.
    named_b = laplace_ownership(champ_counts, n_opp=19, alpha=1.0, candidate_names=champ_named)
    p_true_demo = {c: 1.0 / len(champ_named) for c in champ_named}
    own_b = blanks_chalk_resolved(named_b, blank_mass=12 / 26, p_true=p_true_demo)
    assert SENTINEL not in own_b and abs(sum(own_b.values()) - 1.0) < 1e-9, own_b

    print("ingest_ownership self-test: PASS")
    print("  no-exclude:", r["ownership"], "locked", r["locked_count"], "pending", r["pending_count"])
    print("  self-exclude(b):", r2["ownership"], "locked", r2["locked_count"], "pending", r2["pending_count"])
    print(f"  Laplace floor (champion): Spain={own_a['Spain']:.4f}=3/26  France={own_a['France']:.4f}=1/26  "
          f"SENTINEL={own_a[SENTINEL]:.4f}=12/26  sum={sum(own_a.values()):.6f}")


if __name__ == "__main__":
    _selftest()
