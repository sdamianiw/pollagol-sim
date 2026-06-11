"""DoD-2 - probe candidate per-match odds sources for WC-2026 1X2 + totals coverage.

Gate 7 (TDD): require_both() demands BOTH 1X2 (home/draw/away) AND totals (over/under); it FAILS on an
empty/placeholder response (proven in _selftest BEFORE any live call).

Candidates: The Odds API (soccer_fifa_world_cup) | API-Football (paid) | football-data.org.
Live-probes only sources with a key in env/.env; others report PENDIENTE + the exact missing key, plus the
DOCUMENTED web evidence (URL + UTC) so a documented-yes is never confused with a live-proven-yes.

'WC-2026 served' is BINDING = the 2026 competition endpoint returns >=1 WC-2026 fixture/event (NOT a
current-fixture proxy; a proxy only validates response SHAPE + latency -> FM2 guard).

Reuses pool/leverage.py american_to_prob + devig for the 2-source cross-check (R3, no second copy).
Stdlib only (urllib). Request odds in AMERICAN format so american_to_prob applies directly.
"""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from pool.leverage import american_to_prob, devig  # noqa: E402

H2H_KEYS = ("h2h", "match_winner", "1x2", "fulltime result", "match winner")
TOTALS_KEYS = ("totals", "over/under", "over_under", "goals over/under", "total goals")
DOC_UTC = "2026-06-02"   # UTC date the web evidence below was gathered


def require_both(markets: dict) -> None:
    """Gate-7 core: a usable per-match source MUST carry 1X2 AND totals."""
    assert markets.get("has_1x2") and markets.get("has_totals"), \
        f"source missing required markets (need 1X2 AND totals): {markets}"


def crosscheck_favorite(book_a: dict, book_b: dict) -> dict:
    """R3 2-source cross-check on ONE fixture's 1X2 (american odds {outcome: odds}).
    Reuses pool.leverage de-vig. Returns the favorite's de-vigged prob per book + delta (pp); PASS if <3pp."""
    pa, _ = devig({k: american_to_prob(v) for k, v in book_a.items()})
    pb, _ = devig({k: american_to_prob(v) for k, v in book_b.items()})
    fav = max(pa, key=pa.get)
    delta = abs(pa[fav] - pb.get(fav, 0.0)) * 100.0
    return {"favorite": fav, "book_a_prob": round(pa[fav], 4), "book_b_prob": round(pb.get(fav, 0.0), 4),
            "delta_pp": round(delta, 2), "pass": delta < 3.0}


def _live_crosscheck(events) -> dict | None:
    """R3 on REAL data: first event with >=2 bookmakers carrying h2h -> de-vigged favorite delta (pp)."""
    for ev in events or []:
        books = []
        for bk in ev.get("bookmakers", []):
            h2h = next((m for m in bk.get("markets", []) if m.get("key") == "h2h"), None)
            if h2h and len(h2h.get("outcomes", [])) >= 2:
                books.append((bk.get("key"), {o["name"]: o["price"] for o in h2h["outcomes"]}))
        if len(books) >= 2:
            (na, a), (nb, b) = books[0], books[1]
            cc = crosscheck_favorite(a, b)
            cc.update(event=f"{ev.get('home_team')} v {ev.get('away_team')}", book_a=na, book_b=nb)
            return cc
    return None


def _load_dotenv(path: str | None = None) -> None:
    path = path or os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get(url: str, headers: dict | None = None, timeout: int = 30) -> dict:
    t0 = time.monotonic()
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": True, "status": 200, "body": json.loads(r.read().decode()),
                    "headers": dict(r.headers), "latency_s": round(time.monotonic() - t0, 3)}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_raw": raw[:300]}
        return {"ok": False, "status": e.code, "body": body, "latency_s": round(time.monotonic() - t0, 3)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "status": None, "error": repr(e), "latency_s": round(time.monotonic() - t0, 3)}


def _markets_odds_api(events) -> dict:
    names = set()
    for ev in (events or []):
        for bk in ev.get("bookmakers", []):
            for m in bk.get("markets", []):
                names.add((m.get("key") or "").lower())
    return {"has_1x2": "h2h" in names, "has_totals": "totals" in names, "names": sorted(names)}


def _markets_api_football(body) -> dict:
    names = set()
    for item in (body.get("response") or []):
        for bk in item.get("bookmakers", []):
            for bet in bk.get("bets", []):
                names.add((bet.get("name") or "").lower())
    return {"has_1x2": any(any(k in n for k in H2H_KEYS) for n in names),
            "has_totals": any(any(k in n for k in TOTALS_KEYS) for n in names), "names": sorted(names)}


def probe_the_odds_api() -> dict:
    """The Odds API. Live only with THE_ODDS_API_KEY; else PENDIENTE + documented evidence."""
    _load_dotenv()
    key = os.environ.get("THE_ODDS_API_KEY") or os.environ.get("ODDS_API_KEY")
    base = "https://api.the-odds-api.com/v4"
    row = {"source": "The Odds API", "plan": "Starter FREE (500 cr/mo, no card) | 20K $30/mo",
           "quota": "500 cr/mo free; call cost = markets x regions (h2h,totals x eu = 2 cr/call)",
           "cost": "$0 free / $30 mo backstop",
           "url": f"{base}/sports/soccer_fifa_world_cup/odds/?regions=eu&markets=h2h,totals&oddsFormat=american&apiKey=***",
           "doc_url": "https://the-odds-api.com/sports/fifa-world-cup-odds.html", "doc_utc": DOC_UTC}
    if not key:
        row.update(status="PENDIENTE", wc2026_served="doc:YES (sample event 2026-06-14 NED-JPN)",
                   has_1x2="doc:YES", has_totals="doc:YES", latency_s=None,
                   note="no THE_ODDS_API_KEY; register free Starter (no card) -> set key -> re-run to flip PROVEN")
        return row
    sports = _get(f"{base}/sports/?apiKey={key}")
    listed = any(s.get("key") == "soccer_fifa_world_cup" for s in (sports.get("body") or [])
                 if isinstance(s, dict))
    odds = _get(f"{base}/sports/soccer_fifa_world_cup/odds/?regions=eu&markets=h2h,totals"
                f"&oddsFormat=american&apiKey={key}")
    events = odds.get("body") if odds.get("ok") else []
    n_events = len(events) if isinstance(events, list) else 0
    mk = _markets_odds_api(events if isinstance(events, list) else [])
    served = listed and n_events > 0
    if served and mk["has_1x2"] and mk["has_totals"]:
        status = "PROVEN"
    elif served and mk["has_1x2"]:
        status = "PARTIAL(no totals yet)"   # markets are doc-covered; totals often post closer to kickoff
    else:
        status = "FAIL"
    err = ""
    if not odds.get("ok"):
        b = odds.get("body") or {}
        err = f"  odds_http={odds.get('status')} {odds.get('error') or b.get('message') or b}"
    row.update(has_1x2=mk["has_1x2"], has_totals=mk["has_totals"], wc2026_served=served,
               latency_s=odds.get("latency_s"), status=status,
               note=f"sport listed={listed}; events={n_events}; markets={mk['names']}{err}",
               live_crosscheck=_live_crosscheck(events if isinstance(events, list) else []))
    return row


def probe_api_football() -> dict:
    _load_dotenv()
    key = os.environ.get("API_FOOTBALL_KEY")
    base = "https://v3.football.api-sports.io"
    row = {"source": "API-Football", "plan": "FREE (100/day, seasons 2022-2024 only) | paid serves 2026",
           "quota": "free 100 req/DAY; /odds returns all bookmakers/fixture = 1 req",
           "cost": "$0 free (no 2026) / paid ~Pro tier", "url": f"{base}/odds?league=1&season=2026&fixture=<id>",
           "doc_url": "memory/rules.md Step-0 probe (2026-05-30)", "doc_utc": DOC_UTC}
    if not key:
        row.update(status="PENDIENTE", has_1x2="?", has_totals="?", wc2026_served="?", latency_s=None,
                   note="no API_FOOTBALL_KEY")
        return row
    headers = {"x-apisports-key": key}
    fx = _get(f"{base}/fixtures?league=1&season=2026", headers)
    body = fx.get("body") or {}
    plan_err = (body.get("errors") or {})
    served = fx.get("ok") and int(body.get("results", 0) or 0) > 0
    mk = {"has_1x2": False, "has_totals": False, "names": []}
    if served and body.get("response"):
        fid = body["response"][0]["fixture"]["id"]
        odds = _get(f"{base}/odds?league=1&season=2026&fixture={fid}", headers)
        mk = _markets_api_football(odds.get("body") or {})
    row.update(has_1x2=mk["has_1x2"], has_totals=mk["has_totals"], wc2026_served=bool(served),
               latency_s=fx.get("latency_s"),
               status=("PROVEN" if (served and mk["has_1x2"] and mk["has_totals"]) else "FAIL"),
               note=f"results={body.get('results')}; plan_error={plan_err or 'none'}")
    return row


def probe_football_data() -> dict:
    """football-data.org. FREE tier has NO odds (odds is a paid EUR15/mo add-on) -> fails 1X2+totals."""
    return {"source": "football-data.org", "plan": "FREE (12 comps incl. WC, 10 req/min) | odds add-on EUR15/mo",
            "quota": "10 req/min free", "cost": "$0 free (NO odds) / EUR15 mo odds add-on",
            "url": "https://api.football-data.org/v4/competitions/WC/matches",
            "doc_url": "https://www.football-data.org/coverage", "doc_utc": DOC_UTC,
            "status": "FAIL(odds)", "has_1x2": "doc:NO(free)", "has_totals": "doc:NO(free)",
            "wc2026_served": "doc:YES(fixtures only)", "latency_s": None,
            "note": "good FREE fixtures/results source; odds NOT in free tier -> disqualified for per-match odds"}


def _selftest() -> None:
    # Gate 7: require_both must FAIL on an empty/placeholder source BEFORE any live call.
    failed = False
    try:
        require_both({"has_1x2": False, "has_totals": False})
    except AssertionError:
        failed = True
    assert failed, "require_both did not fail on empty source (Gate 7 broken)"
    print("Gate-7  require_both(empty)        -> AssertionError  PASS")
    require_both({"has_1x2": True, "has_totals": True})
    print("        require_both(1X2+totals)  -> ok              PASS")
    # cross-check mechanism on SYNTHETIC 2-bookmaker american 1X2 (modeled on The Odds API shape).
    a = {"France": -160, "Draw": 280, "Senegal": 420}
    b = {"France": -150, "Draw": 270, "Senegal": 410}
    cc = crosscheck_favorite(a, b)
    print(f"        crosscheck(synthetic)     -> fav={cc['favorite']} "
          f"{cc['book_a_prob']} vs {cc['book_b_prob']} delta={cc['delta_pp']}pp pass={cc['pass']}  PASS")
    assert cc["favorite"] == "France" and cc["pass"], cc


def _fmt(v):
    return str(v)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _load_dotenv()
    print("=" * 100)
    print(f"DoD-2  PER-MATCH ODDS SOURCE PROBE   (need: 1X2 + totals for WC-2026)   doc_utc={DOC_UTC}")
    print("=" * 100)
    _selftest()
    print("-" * 100)

    rows = [probe_the_odds_api(), probe_api_football(), probe_football_data()]
    hdr = f"{'source':<18}{'status':<12}{'1X2':<10}{'totals':<10}{'WC2026':<28}{'latency':<9}"
    print(hdr)
    print("-" * 100)
    for r in rows:
        print(f"{r['source']:<18}{str(r.get('status')):<12}{str(r.get('has_1x2')):<10}"
              f"{str(r.get('has_totals')):<10}{str(r.get('wc2026_served')):<28}{str(r.get('latency_s')):<9}")
        print(f"    plan : {r.get('plan')}")
        print(f"    quota: {r.get('quota')}   cost: {r.get('cost')}")
        print(f"    url  : {r.get('url')}")
        print(f"    doc  : {r.get('doc_url')}  ({r.get('doc_utc')})")
        print(f"    note : {r.get('note')}")
        print("-" * 100)

    proven = [r for r in rows if r.get("status") == "PROVEN"]
    partial = [r for r in rows if str(r.get("status")).startswith("PARTIAL")]
    doc_yes = [r for r in rows if r.get("status") == "PENDIENTE" and r.get("has_1x2") == "doc:YES"]
    print("VERDICT:")
    if proven:
        print(f"  LIVE-PROVEN (1X2+totals on WC-2026): {[r['source'] for r in proven]}")
    else:
        print("  LIVE-PROVEN: (none yet)")
    if partial:
        print(f"  LIVE-PARTIAL (served + 1X2, totals not posted yet): {[r['source'] for r in partial]} "
              f"-> re-probe nearer kickoff (~Jun 9-11) for totals")
    if doc_yes:
        print(f"  DOC-PROVEN / LIVE-PENDING: {[r['source'] for r in doc_yes]} "
              f"-> blocker = free key; what validates = register + set key + re-run this probe")
    live_cc = next((r.get("live_crosscheck") for r in rows if r.get("live_crosscheck")), None)
    if live_cc:
        print(f"  Cross-check (LIVE, real WC odds): {live_cc['event']} | {live_cc['book_a']} vs "
              f"{live_cc['book_b']} | fav={live_cc['favorite']} {live_cc['book_a_prob']} vs "
              f"{live_cc['book_b_prob']} delta={live_cc['delta_pp']}pp -> "
              f"{'PASS (<3pp)' if live_cc['pass'] else 'FLAG (>=3pp)'}")
    else:
        print("  Cross-check (live): PENDIENTE — no event with >=2 h2h bookmakers in this response.")
    print("=" * 100)


if __name__ == "__main__":
    main()
