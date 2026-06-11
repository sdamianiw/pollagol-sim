"""P3 / M7 - football-data.co.uk historical-odds fetcher (Track B backtest input).

Downloads top-5 EU league season CSVs to data/footballdata/<season>_<league>.csv (cached: skips
files already present). Each CSV carries, in ONE file, the result join key + B365 opening 1X2 +
B365 totals (2.5 line) + closing odds (memory/rules.md P1 verdict). DECIMAL odds.

Provenance (no invented facts): every file logged with url + fetched-UTC + HTTP status + row count +
sha256 to data/footballdata/provenance.json. URL live-verified 2026-06-03 (HTTP 200, 380 rows).

Stdlib only. Run: `python evals/fetch_footballdata.py` (add --force to re-download).
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "footballdata")
PROV_PATH = os.path.join(DATA_DIR, "provenance.json")
BASE = "https://www.football-data.co.uk/mmz4281"

# top-5 EU leagues; 5 seasons. COVID seasons flagged (crowd-less -> abnormal home advantage).
LEAGUES = ["E0", "SP1", "I1", "D1", "F1"]
SEASONS = ["1920", "2021", "2122", "2223", "2324"]
COVID_SEASONS = {"1920", "2021"}
_UA = "Mozilla/5.0 (compatible; PollagolBacktest/1.0; +https://www.football-data.co.uk)"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def url_for(season: str, league: str) -> str:
    return f"{BASE}/{season}/{league}.csv"


def cache_path(season: str, league: str) -> str:
    return os.path.join(DATA_DIR, f"{season}_{league}.csv")


def _count_rows(raw: bytes) -> int:
    """Data rows (excludes the header). football-data CSVs are latin-1 with possible blank tails."""
    text = raw.decode("latin-1")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return max(len(lines) - 1, 0)


def _download(url: str) -> tuple[int, bytes]:
    req = Request(url, headers={"User-Agent": _UA})
    with urlopen(req, timeout=60) as r:                      # noqa: S310 (trusted host)
        return r.status, r.read()


def fetch_all(force: bool = False, seasons=SEASONS, leagues=LEAGUES) -> dict:
    """Download (or reuse cached) every season×league CSV. Returns the provenance dict."""
    os.makedirs(DATA_DIR, exist_ok=True)
    records = []
    for season in seasons:
        for league in leagues:
            url, path = url_for(season, league), cache_path(season, league)
            cached = os.path.exists(path) and not force
            if cached:
                with open(path, "rb") as f:
                    raw = f.read()
                status = 200
            else:
                status, raw = _download(url)
                if status != 200 or not raw:
                    records.append({"season": season, "league": league, "url": url,
                                    "status": status, "rows": 0, "ok": False, "path": None,
                                    "fetched_utc": _utc()})
                    print(f"  FAIL {season} {league}: HTTP {status}")
                    continue
                with open(path, "wb") as f:
                    f.write(raw)
            rows = _count_rows(raw)
            records.append({"season": season, "league": league, "url": url, "status": status,
                            "rows": rows, "ok": True, "path": path, "cached": cached,
                            "covid": season in COVID_SEASONS, "fetched_utc": _utc(),
                            "sha256": hashlib.sha256(raw).hexdigest()})
            print(f"  {'cache' if cached else 'DL   '} {season} {league}: {rows} rows")
    prov = {"source": "football-data.co.uk", "base": BASE, "generated_utc": _utc(),
            "covid_seasons": sorted(COVID_SEASONS), "files": records,
            "total_rows": sum(r["rows"] for r in records if r["ok"]),
            "n_files_ok": sum(1 for r in records if r["ok"])}
    with open(PROV_PATH, "w", encoding="utf-8") as f:
        json.dump(prov, f, ensure_ascii=False, indent=2, sort_keys=True)
    return prov


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    force = "--force" in sys.argv
    print(f"Fetching football-data.co.uk -> {DATA_DIR} (force={force})")
    prov = fetch_all(force=force)
    print("-" * 60)
    print(f"OK files: {prov['n_files_ok']}/{len(prov['files'])}   total data rows: {prov['total_rows']}")
    print(f"provenance: {PROV_PATH}")
    return 0 if prov["n_files_ok"] == len(prov["files"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
