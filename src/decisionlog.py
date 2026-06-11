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
FIELDS = ["utc", "fixture_id", "home", "away", "pick", "ev", "p_pick", "total_line",
          "context_flag", "source", "reasoning", "result", "reviewed"]
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
