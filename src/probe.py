"""Step-0 coverage + quota probe for API-Football (WC-2026, league=1 season=2026).

Answers two blocking questions before any engine is built:
  1. Which markets/endpoints exist on the FREE tier?  -> decides the odds path.
  2. How many requests does one matchday cost vs the 100/DAY cap?  -> decides whether
     the cache + web-fallback path is MANDATORY (P0-a / lesson L1).

Read-only. Stdlib only (urllib) so it runs with zero installed deps.

Auth (set ONE; read from env, never hardcoded):
  - Direct api-sports.io :  set env  API_FOOTBALL_KEY   (header x-apisports-key)
  - RapidAPI            :  set env  RAPIDAPI_KEY        (host api-football-v1.p.rapidapi.com)
  Keys may also live in a local, gitignored .env file (KEY=value lines). A real env
  var always wins — .env never overrides one already set.

Run:   python src/probe.py
Output: prints a verdict block + writes data/snapshots/probe_<UTC>.json.
It does NOT edit memory/rules.md — the verdict is reviewed (HITL) then pasted in.
"""
from __future__ import annotations
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

LEAGUE, SEASON = 1, 2026

# --- matchday cost model (explicit + auditable; P0-a) ----------------------------
# One /odds and one /fixtures/lineups call each return ALL bookmakers / both XIs for a
# fixture, so they cost 1 request per fixture. /injuries is league-wide => 1 shared/day.
PEAK_FIXTURES = 5          # a busy group-stage day
REFRESHES     = 3          # initial pass + 2 refreshes as lineups/odds firm up near kickoff
DAILY_LIMIT_DEFAULT = 100  # free tier; confirmed from response headers at runtime

MARKET_KEYS = {
    "match_winner":  ("match winner", "1x2", "fulltime result"),
    "over_under":    ("over/under", "goals over/under", "total goals"),
    "correct_score": ("exact score", "correct score"),
}


def _load_dotenv(path=".env"):
    """Populate env from a local .env (gitignored), without overriding real env vars."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _auth():
    _load_dotenv()
    k = os.environ.get("API_FOOTBALL_KEY")
    if k:
        return "https://v3.football.api-sports.io", {"x-apisports-key": k}
    k = os.environ.get("RAPIDAPI_KEY")
    if k:
        return ("https://api-football-v1.p.rapidapi.com/v3",
                {"x-rapidapi-key": k, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"})
    sys.exit("No key found. Set API_FOOTBALL_KEY (api-sports.io) or RAPIDAPI_KEY (RapidAPI).")


class Client:
    def __init__(self):
        self.base, self.headers = _auth()
        self.count = 0
        self.daily_limit = None
        self.daily_remaining = None

    def get(self, endpoint, **params):
        self.count += 1
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.base}/{endpoint}" + (f"?{qs}" if qs else "")
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                h = r.headers
                lim = h.get("x-ratelimit-requests-limit")
                rem = h.get("x-ratelimit-requests-remaining")
                if lim is not None:
                    self.daily_limit = int(lim)
                if rem is not None:
                    self.daily_remaining = int(rem)
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"_http_error": e.code, "_body": e.read().decode(errors="replace")}
        except Exception as e:  # noqa: BLE001
            return {"_error": repr(e)}


def _ok(resp):
    return isinstance(resp, dict) and "_http_error" not in resp and "_error" not in resp \
        and int(resp.get("results", 0) or 0) > 0


def detect_markets(odds_resp):
    found = {k: False for k in MARKET_KEYS}
    names = set()
    for item in (odds_resp.get("response") or []):
        for bk in item.get("bookmakers", []):
            for bet in bk.get("bets", []):
                names.add((bet.get("name") or "").lower())
    for low in names:
        for key, kws in MARKET_KEYS.items():
            if any(kw in low for kw in kws):
                found[key] = True
    return found, sorted(names)


def main():
    c = Client()
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    snap = {"utc": utc, "league": LEAGUE, "season": SEASON, "endpoints": {}}

    fixtures = c.get("fixtures", league=LEAGUE, season=SEASON)
    n_fix = int(fixtures.get("results", 0) or 0)
    snap["endpoints"]["fixtures"] = {"ok": _ok(fixtures), "count": n_fix}

    fixture_id = None
    if fixtures.get("response"):
        fixture_id = fixtures["response"][0]["fixture"]["id"]

    odds = c.get("odds", league=LEAGUE, season=SEASON, fixture=fixture_id) if fixture_id else {}
    markets, market_names = detect_markets(odds) if odds else ({k: False for k in MARKET_KEYS}, [])
    snap["endpoints"]["odds"] = {"ok": _ok(odds), "markets": markets, "names": market_names}

    lineups = c.get("fixtures/lineups", fixture=fixture_id) if fixture_id else {}
    snap["endpoints"]["lineups"] = {"ok": _ok(lineups)}
    injuries = c.get("injuries", league=LEAGUE, season=SEASON)
    snap["endpoints"]["injuries"] = {"ok": _ok(injuries)}
    topscorers = c.get("players/topscorers", league=LEAGUE, season=SEASON)
    snap["endpoints"]["topscorers"] = {"ok": _ok(topscorers)}

    # --- quota projection (P0-a) -------------------------------------------------
    limit = c.daily_limit or DAILY_LIMIT_DEFAULT
    per_day = (1 + 1) + PEAK_FIXTURES * (1 + 1) * REFRESHES  # fixtures+injuries once, (lineups+odds)/fixture/refresh
    mandatory_cache = per_day > limit
    snap["quota"] = {
        "daily_limit": limit, "daily_remaining": c.daily_remaining,
        "probe_requests_used": c.count,
        "projected_peak_day": per_day,
        "model": f"(fixtures+injuries=2) + {PEAK_FIXTURES} fixtures x (lineups+odds=2) x {REFRESHES} refreshes",
        "cache_web_fallback_mandatory": mandatory_cache,
    }

    # --- odds-path decision ------------------------------------------------------
    if markets["over_under"]:
        odds_path = "1X2+totals (API-Football)"
    elif _ok(odds):
        odds_path = "API-Football has odds but NO totals -> add The Odds API (totals only); else Elo-xG"
    else:
        odds_path = "no usable odds on free tier -> The Odds API (totals) or Elo-xG fallback"
    snap["odds_path"] = odds_path

    out = os.path.join("data", "snapshots", f"probe_{utc}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2)

    # --- human verdict (paste into memory/rules.md after review) -----------------
    print("=" * 72)
    print(f"STEP-0 PROBE  ({utc})   snapshot -> {out}")
    print("=" * 72)
    print(f"fixtures league=1 season=2026 : ok={_ok(fixtures)}  count={n_fix}")
    print(f"odds endpoint                 : ok={_ok(odds)}  markets={markets}")
    print(f"  bet names seen              : {market_names or '(none)'}")
    print(f"lineups / injuries / topscr   : {_ok(lineups)} / {_ok(injuries)} / {_ok(topscorers)}")
    print("-" * 72)
    print(f"QUOTA  daily_limit={limit}  remaining={c.daily_remaining}  probe_used={c.count}")
    print(f"  projected peak day ({PEAK_FIXTURES} fixtures x {REFRESHES} refreshes) = {per_day} req")
    print(f"  cache + web-fallback MANDATORY? -> {mandatory_cache}")
    print("-" * 72)
    print(f"ODDS PATH -> {odds_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
