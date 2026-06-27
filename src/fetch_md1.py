"""Matchday-1 enumeration + single fresh fetch (Track B, 2026-06-11).

ONE live call to The Odds API (soccer_fifa_world_cup, eu, h2h+totals, american) -> prints the quota
headers (x-requests-remaining/used, which ingest.fetch_live drops), lists every event, FILTERS to the
matchday-1 window [2026-06-11T00:00Z, 2026-06-14T06:00Z], and writes ONE multi-event snapshot
data/snapshots/md{N}_<UTC>.json (prefix from --md) for the per-fixture replay runs (P3). ~2 credits (h2h,totals x eu).

Reuses src.probe_oddssource._get/_load_dotenv and src.ingest.snapshot - no second HTTP/snapshot copy.
On a non-OK response it prints the failure and exits non-zero (P2 STOP; fall back per the contract §6).
"""
from __future__ import annotations
import argparse
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.probe_oddssource import _load_dotenv, _get
from src.ingest import snapshot, _utc_stamp, BASE, SPORT

WIN_LO = datetime(2026, 6, 11, 0, 0, tzinfo=timezone.utc)
WIN_HI = datetime(2026, 6, 14, 6, 0, tzinfo=timezone.utc)


def _commence(ev: dict) -> datetime:
    return datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))


def filter_window(events: list, win_lo: datetime = WIN_LO, win_hi: datetime = WIN_HI) -> list:
    """Pure, inclusive [win_lo, win_hi] filter sorted by commence_time. Defaults = the FROZEN MD1
    window (2026-06-11T00:00Z .. 2026-06-14T06:00Z) so the original 8-fixture replay is byte-identical;
    pass a wider win_hi to capture later MD1 fixtures (Sun Jun-14 / Mon Jun-15) that the API now serves."""
    return sorted([e for e in events if win_lo <= _commence(e) <= win_hi], key=_commence)


def _hdr(headers: dict, name: str):
    """Case-insensitive header lookup (server casing varies)."""
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v
    return None


def fetch_md1(fmt: str = "american", regions: str = "eu", markets: str = "h2h,totals",
              win_lo: datetime = WIN_LO, win_hi: datetime = WIN_HI, expect: int = 8,
              matchday: int = 1) -> int:
    _load_dotenv()
    key = os.environ.get("THE_ODDS_API_KEY") or os.environ.get("ODDS_API_KEY")
    if not key:
        print("🛑 no THE_ODDS_API_KEY in env/.env - cannot fetch. STOP.")
        return 1
    url = f"{BASE}/sports/{SPORT}/odds/?regions={regions}&markets={markets}&oddsFormat={fmt}&apiKey={key}"
    fetched_utc = _utc_stamp()
    r = _get(url)
    rem, used = _hdr(r.get("headers"), "x-requests-remaining"), _hdr(r.get("headers"), "x-requests-used")
    print("=" * 88)
    print(f"MD1 FETCH  {fetched_utc}  status={r.get('status')}  latency={r.get('latency_s')}s")
    print(f"  QUOTA: x-requests-remaining={rem}  x-requests-used={used}  (cost this call ~2 cr)")
    print("=" * 88)
    if not r.get("ok") or not isinstance(r.get("body"), list):
        print(f"🛑 fetch NOT ok (status={r.get('status')}, body={str(r.get('body'))[:200]}). "
              f"Fall back to a cached snapshot (contract §6). STOP.")
        return 1

    events = r["body"]
    print(f"events returned: {len(events)}")
    inwin = filter_window(events, win_lo, win_hi)
    print(f"events in window [{win_lo:%Y-%m-%dT%H:%MZ}, {win_hi:%Y-%m-%dT%H:%MZ}]: {len(inwin)}")
    print("-" * 88)
    for e in inwin:
        print(f"  {e['commence_time']}  {e['home_team']:<16} vs {e['away_team']:<20}  id={e['id']}")
    print("-" * 88)

    prov = {"source": "The Odds API", "sport": SPORT, "fmt": fmt, "regions": regions, "markets": markets,
            "fetched_utc": fetched_utc, "x_requests_remaining": rem, "x_requests_used": used,
            "window": [win_lo.isoformat(), win_hi.isoformat()], "n_events_total": len(events)}
    path = snapshot({"events": inwin, "provenance": prov}, f"md{matchday}")
    print(f"snapshot written: {path}")
    if len(inwin) != expect:
        print(f"⚠ EXPECTED {expect} MD1 fixtures, got {len(inwin)} -> STOP for HITL (do not guess). "
              f"Inspect the list above against the contract §3 table.")
        return 2
    print(f"OK: exactly {expect} MD1 fixtures captured.")
    return 0


def _parse_iso_utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="MD1 enumeration + single fresh fetch (Track B, HITL).")
    ap.add_argument("--win-lo", default=None,
                    help="lower window bound, ISO UTC (default 2026-06-11T00:00Z = the frozen MD1 window, "
                         "byte-identical replay). Set to the MD-N slate start to scope a later matchday, "
                         "e.g. 2026-06-24T03:00Z to exclude already-recorded MD-2 (L25 calendar-scoping).")
    ap.add_argument("--win-hi", default=None,
                    help="upper window bound, ISO UTC (default 2026-06-14T06:00Z = the frozen MD1 window). "
                         "Widen to capture later MD1 fixtures the API now serves, e.g. 2026-06-15T23:00Z.")
    ap.add_argument("--expect", type=int, default=8,
                    help="HITL count-guard: STOP (exit 2) unless exactly this many fixtures land in-window.")
    ap.add_argument("--md", type=int, required=True,
                    help="matchday number -> snapshot filename prefix md{N}_ (e.g. --md 3 -> md3_<UTC>.json).")
    a = ap.parse_args()
    win_lo = _parse_iso_utc(a.win_lo) if a.win_lo else WIN_LO
    win_hi = _parse_iso_utc(a.win_hi) if a.win_hi else WIN_HI
    sys.exit(fetch_md1(win_lo=win_lo, win_hi=win_hi, expect=a.expect, matchday=a.md))
