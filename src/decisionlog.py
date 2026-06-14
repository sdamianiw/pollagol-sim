"""M6 logging - per-match decision log (Track B).

Append one auditable row per recommended pick to predictions/decisions.csv. Every row MUST carry
reasoning + source + UTC date (provenance is non-negotiable). `played_unreviewed` is the filter the
companion predictions/review.ps1 uses to surface only matches that have a result but no review yet.
Stdlib only.
"""
from __future__ import annotations
import csv
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DECISIONS_PATH = os.path.join(ROOT, "predictions", "decisions.csv")
# Original 13 prediction-time columns (utc = kickoff UTC) ...
_BASE_FIELDS = ["utc", "fixture_id", "home", "away", "pick", "ev", "p_pick", "total_line",
                "context_flag", "source", "reasoning", "result", "reviewed"]
# ... + Phase-2 execution-discipline columns (APPENDED, additive; never renames an existing column).
# Forecast (backfilled from the snapshot replay; rubric-INDEPENDENT, odds-derived):
#   modal=B2 pick, favorite_pick=B1 pick, devig_*=de-vig MARKET 1X2 (input-cal),
#   m_*=PRE-context DC implied_1x2 (model-health forecast, F12).
# Scoring (written by src/decision_score when a result is recorded):
#   points_{actual,b1,b2} (corrected rubric), brier_model (PRIMARY, m_*), brier_market (secondary, devig_*).
# Dual-track (Track-B 2026-06-14; APPENDED, additive): entered_pick = the score the human actually typed into
#   pollaya (may diverge from `pick` = the model EV-argmax via a HITL override); pts_entered = its rubric
#   points. `pick`/`points_actual` STAY the MODEL track (never renamed). override = pts_entered - points_actual.
_PHASE2_FIELDS = ["modal", "favorite_pick", "devig_h", "devig_d", "devig_a", "m_h", "m_d", "m_a",
                  "points_actual", "points_b1", "points_b2", "brier_model", "brier_market",
                  "entered_pick", "pts_entered"]
FIELDS = _BASE_FIELDS + _PHASE2_FIELDS
_REQUIRED = ("source", "reasoning")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_decision(row: dict, path: str = DECISIONS_PATH) -> dict:
    """Append a decision row; writes the header if the file is new. Enforces provenance."""
    for req in _REQUIRED:
        if not row.get(req):
            raise ValueError(f"decision row requires non-empty {req!r} (provenance, no exceptions)")
    full = {k: "" for k in FIELDS}
    full.update({k: row.get(k, "") for k in FIELDS})
    if not full["utc"]:
        full["utc"] = _utc()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(full)
    return full


def read_decisions(path: str = DECISIONS_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def played_unreviewed(rows: list[dict]) -> list[dict]:
    """Matches with a result recorded but not yet reviewed (the review.ps1 filter)."""
    return [r for r in rows if r.get("result") and not r.get("reviewed")]


def _rewrite(rows: list[dict], path: str) -> None:
    """Rewrite the whole CSV under the current FIELDS (missing cols -> ''). The ONLY full-file writer."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def migrate_schema(path: str = DECISIONS_PATH) -> list[str]:
    """Idempotently widen the CSV header to the current FIELDS, preserving every existing value.

    Existing rows gain empty cells for the new columns; an already-migrated file is unchanged.
    Returns the header actually written.
    """
    rows = read_decisions(path)
    _rewrite(rows, path)
    return FIELDS


def update_decision(fixture_id: str, updates: dict, path: str = DECISIONS_PATH) -> dict:
    """Merge `updates` into the row matching `fixture_id` and rewrite the file in place.

    The single in-place writer (F7: keeps CSV quoting of the free-text `reasoning` field in Python,
    never PowerShell). Raises if the fixture is absent or matches more than one row. Does NOT touch
    any model parameter - this is a pure decisions.csv mutation (I3).
    """
    rows = read_decisions(path)
    hits = [r for r in rows if r.get("fixture_id") == fixture_id]
    if len(hits) != 1:
        raise ValueError(f"update_decision: fixture_id {fixture_id!r} matched {len(hits)} rows (need exactly 1)")
    bad = set(updates) - set(FIELDS)
    if bad:
        raise ValueError(f"update_decision: unknown column(s) {sorted(bad)}")
    hits[0].update({k: str(v) for k, v in updates.items()})
    _rewrite(rows, path)
    return hits[0]
