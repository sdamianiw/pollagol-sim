"""M1 ingest - per-match odds ingestion + provenance + snapshot + web fallback (Track B).

Live source = The Odds API (american, soccer_fifa_world_cup). Reuses src/probe_oddssource helpers
(_load_dotenv, _get, crosscheck_favorite) - no second copy. Snapshots the RAW event payload to
data/snapshots/<fixture_id>_<UTC>.json for deterministic replay; the FALLBACK payload is snapshotted
too (PM5). Stdlib only.
"""
from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.probe_oddssource import _load_dotenv, _get, crosscheck_favorite
from src.lines import is_half_line

BASE = "https://api.the-odds-api.com/v4"
SPORT = "soccer_fifa_world_cup"
SNAP_DIR = os.path.join(ROOT, "data", "snapshots")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _market(bk: dict, key: str):
    return next((m for m in bk.get("markets", []) if m.get("key") == key), None)


def _totals_of(bk: dict):
    """Extract {over, under, line} from a book's totals market, or None if absent/incomplete."""
    tm = _market(bk, "totals")
    if not (tm and tm.get("outcomes")):
        return None
    over = next((o for o in tm["outcomes"] if o["name"].lower() == "over"), None)
    under = next((o for o in tm["outcomes"] if o["name"].lower() == "under"), None)
    if over and under:
        return {"over": over["price"], "under": under["price"], "line": over.get("point")}
    return None


def parse_event(event: dict, fmt: str = "american") -> dict:
    """The Odds API event -> our match dict.

    Book-selection (RB3-clean, H3/P4c): prefer a SINGLE book carrying BOTH h2h AND an x.5 (half) totals line,
    and take 1X2 AND totals from that one book -> the totals PRICE feeds mu_eff against the SAME book's 1X2
    (no cross-book 'fabricated 1X2<->mu tension', RB3). If no book has h2h + x.5 totals, take 1X2 from the
    first h2h book and go totals-blind (HARD-flagged 'mu_eff unavailable', never silent); NEVER mix books
    (cross_book is a safety assertion that must never fire). x.5-only because poisson_over_prob/mu_from_pover
    handle only half-lines (H1). The selection is surfaced in match['book_selection']."""
    home, away = event["home_team"], event["away_team"]
    with_h2h = [bk for bk in event.get("bookmakers", []) if _market(bk, "h2h")]
    if not with_h2h:
        raise ValueError(f"event {event.get('id')} has no h2h market")

    primary, totals = None, None
    for bk in with_h2h:                                   # prefer ONE book with h2h + x.5 totals (RB3-clean)
        t = _totals_of(bk)
        if t and is_half_line(t.get("line")):
            primary, totals = bk, t
            break
    if primary is None:                                   # fallback A: first h2h book, totals-blind (no mu_eff)
        primary = with_h2h[0]

    h2h = {o["name"]: o["price"] for o in _market(primary, "h2h")["outcomes"]}
    odds_1x2 = {"home": h2h[home], "away": h2h[away], "draw": h2h.get("Draw", h2h.get("draw"))}
    h2h_book = primary.get("key")
    totals_book = h2h_book if totals is not None else None
    # SAFETY ASSERTION (must NEVER fire): policy A never cross-books, never feeds a non-x.5 line to mu_eff.
    if totals is not None and (totals_book != h2h_book or not is_half_line(totals.get("line"))):
        raise ValueError(f"BUG: parse_event produced cross-book/non-x.5 totals (h2h={h2h_book}, "
                         f"totals_book={totals_book}, line={totals.get('line')}) - RB3/x.5 invariant violated")
    book_selection = {
        "h2h_book": h2h_book, "totals_book": totals_book, "cross_book": False,
        "totals_blind": totals is None, "x5_line": totals.get("line") if totals else None,
        "text": ("intra-book x.5 totals (RB3-clean mu_eff)" if totals is not None
                 else "mu_eff unavailable -> totals-blind fallback (no book has h2h + x.5 totals)"),
    }
    return {"fixture_id": event.get("id"), "home": home, "away": away,
            "commence_time": event.get("commence_time"), "odds_1x2": odds_1x2, "totals": totals,
            "fmt": fmt, "primary_book": h2h_book, "book_selection": book_selection,
            "books": [bk.get("key") for bk in event.get("bookmakers", [])]}


def crosscheck_event(event: dict) -> dict | None:
    """R3: de-vigged favorite delta between the first two books carrying h2h (>=2 outcomes)."""
    books = []
    for bk in event.get("bookmakers", []):
        m = _market(bk, "h2h")
        if m and len(m.get("outcomes", [])) >= 2:
            books.append((bk.get("key"), {o["name"]: o["price"] for o in m["outcomes"]}))
    if len(books) < 2:
        return None
    (na, a), (nb, b) = books[0], books[1]
    cc = crosscheck_favorite(a, b)
    cc.update(book_a=na, book_b=nb)
    return cc


def snapshot(payload, fixture_id: str, snap_dir: str = SNAP_DIR) -> str:
    """Write payload to data/snapshots/<fixture_id>_<UTC>.json (sorted keys -> deterministic content)."""
    os.makedirs(snap_dir, exist_ok=True)
    path = os.path.join(snap_dir, f"{fixture_id}_{_utc_stamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def load_snapshot(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ingest_event(event: dict, fmt: str = "american", snap_dir: str = SNAP_DIR) -> dict:
    """Parse + cross-check + snapshot one event. {match, crosscheck, provenance, snapshot_path}."""
    match = parse_event(event, fmt)
    provenance = {"source": "The Odds API", "sport": SPORT, "fmt": fmt,
                  "fetched_utc": _utc_stamp(), "books": match["books"]}
    path = snapshot({"event": event, "provenance": provenance}, match["fixture_id"], snap_dir)
    return {"match": match, "crosscheck": crosscheck_event(event),
            "provenance": provenance, "snapshot_path": path}


def fetch_live(fmt: str = "american", regions: str = "eu", markets: str = "h2h,totals") -> dict:
    """Live fetch (consumes quota). On failure ok=False -> caller MUST fall back to a cached snapshot
    (mandatory web fallback). Returns {ok, status, events, provenance}."""
    _load_dotenv()
    key = os.environ.get("THE_ODDS_API_KEY") or os.environ.get("ODDS_API_KEY")
    prov = {"source": "The Odds API", "sport": SPORT, "fmt": fmt, "regions": regions,
            "markets": markets, "fetched_utc": _utc_stamp()}
    if not key:
        return {"ok": False, "status": None, "events": [], "error": "no THE_ODDS_API_KEY", "provenance": prov}
    url = f"{BASE}/sports/{SPORT}/odds/?regions={regions}&markets={markets}&oddsFormat={fmt}&apiKey={key}"
    r = _get(url)
    events = r.get("body") if (r.get("ok") and isinstance(r.get("body"), list)) else []
    prov["latency_s"] = r.get("latency_s")
    return {"ok": bool(r.get("ok")), "status": r.get("status"), "events": events, "provenance": prov}
