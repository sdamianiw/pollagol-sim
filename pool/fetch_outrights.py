"""pool/fetch_outrights.py - LOCK-RUN D1: fetch WC-2026 CHAMPION (winner) outrights from The Odds API.

Writes data/outrights_<YYYY-MM-DD>.json in the existing outrights schema (primary/crosscheck/format=
american/odds) so pool.leverage / council.market_p_true consume it unchanged. RECOMMEND-NEVER-LOCK pipeline.

Why a NEW file (not src/ingest.py): src/ingest.py is the Track-B per-match h2h/totals path (sport key
soccer_fifa_world_cup, event-shaped output). This is the FUTURES winner market (sport key
soccer_fifa_world_cup_winner, market key 'outrights', team-name outcomes) feeding the pool podium engine -
a different endpoint and a different output schema. Reuses src.probe_oddssource._load_dotenv/_get (the
proven HTTP + .env loader, no second copy) and pool.leverage.american_to_prob (no second de-vig).

GATES (contract A1 + F2P1 + LM9):
  A1  : probe /v4/sports FIRST (0 cr); soccer_fifa_world_cup_winner must be LISTED + the odds board
        non-empty, else STOP (FM2/LM6) - never compute on the stale May-29 board, never hit a paid API.
  F2P1: the PRIMARY (de-vig divisor) book MUST carry a FULL board (>= MIN_BOARD teams). A de-vig over a
        truncated board over-estimates tail-adjacent P_true -> a false 0.08-gate PASS (FM1). No book
        >= MIN_BOARD -> STOP.
  LM9 : ONE book is the de-vig basis; the crosscheck book is ordering/sanity only, NEVER mixed into the
        divisor. Overround S_full (sum of raw implied over the FULL primary board) is printed before de-vig.

Spend: 1 odds call (regions us,eu = 2 cr). Cap <= 10 cr. Stdlib + numpy-free (uses pool.leverage only).
Offline `--selftest` exercises the PARSE/SELECT/overround logic on a synthetic response (no credits).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.probe_oddssource import _load_dotenv, _get   # noqa: E402  (proven HTTP + .env loader)
from pool.leverage import american_to_prob            # noqa: E402  (no second de-vig)

BASE = "https://api.the-odds-api.com/v4"
SPORT = "soccer_fifa_world_cup_winner"
MIN_BOARD = 40                                          # F2P1: primary board must be >= this many teams
OWNED_CHAMPION_TEAMS = ["Spain", "France", "Portugal", "Brazil", "Uruguay", "Netherlands"]  # must resolve

# The Odds API name -> our board key (data/outrights.json convention). Passthrough for anything not listed.
CANON = {
    "United States": "USA", "USA": "USA",
    "Czech Republic": "Czechia", "Czechia": "Czechia",
    "South Korea": "South Korea", "Korea Republic": "South Korea",
    "Turkey": "Turkiye", "Turkiye": "Turkiye", "Türkiye": "Turkiye",
    "Ivory Coast": "Ivory Coast", "Cote d'Ivoire": "Ivory Coast",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Netherlands": "Netherlands", "Holland": "Netherlands",
}


def _canon(name: str) -> str:
    return CANON.get(name, name)


def parse_outrights(events) -> dict:
    """events (The Odds API /odds response for an outrights sport) -> {book_title: {team: american_price}}.
    Outcomes come from each bookmaker's market with key 'outrights'. Names canonicalized to board keys."""
    boards: dict = {}
    for ev in events or []:
        for bk in ev.get("bookmakers", []):
            title = bk.get("title") or bk.get("key") or "unknown"
            board = boards.setdefault(title, {})
            for m in bk.get("markets", []):
                if (m.get("key") or "").lower() != "outrights":
                    continue
                for o in m.get("outcomes", []):
                    nm = o.get("name")
                    pr = o.get("price")
                    if isinstance(nm, str) and nm.strip() and pr is not None:
                        board[_canon(nm)] = int(pr)
    return {t: b for t, b in boards.items() if b}       # drop empty books


def select_books(boards: dict, min_board: int = MIN_BOARD):
    """F2P1: primary = the LARGEST board and it MUST be >= min_board (else None -> caller STOPs).
    crosscheck = the next-largest (may be smaller; ordering/sanity only, LM9). Returns
    (primary_title, primary_board, cross_title_or_None, cross_board_or_None)."""
    ranked = sorted(boards.items(), key=lambda kv: -len(kv[1]))
    if not ranked or len(ranked[0][1]) < min_board:
        return None, None, None, None
    p_title, p_board = ranked[0]
    c_title, c_board = (ranked[1] if len(ranked) > 1 else (None, None))
    return p_title, p_board, c_title, c_board


def overround(board: dict) -> float:
    """S_full = sum of RAW implied probs over the FULL board (book vig net of any truncated tail; LM9)."""
    return sum(american_to_prob(v) for v in board.values())


def _devig_top(board: dict, names):
    """De-vig over the full board, return P_true for the requested names (P_true | winner is a board team)."""
    s = overround(board)
    return {n: (american_to_prob(board[n]) / s if n in board else None) for n in names}


def _spain_france_ordering(board: dict) -> str:
    sp, fr = board.get("Spain"), board.get("France")
    if sp is None or fr is None:
        return "Spain/France: one or both absent from fresh board"
    psp, pfr = american_to_prob(sp), american_to_prob(fr)
    lead = "Spain" if psp >= pfr else "France"
    return (f"fresh: Spain {sp:+d} (impl {psp:.4f}) vs France {fr:+d} (impl {pfr:.4f}) -> {lead} favored "
            f"[May-29 was Spain +450 vs France +480 -> Spain favored]")


def fetch_outrights(date_label: str | None = None, regions: str = "us,eu",
                    odds_format: str = "american", out_dir: str | None = None) -> dict:
    """Live A1 probe -> odds fetch -> parse -> F2P1 select -> write dated json. Returns the written payload.
    Raises RuntimeError on any gate failure (no key / sport not listed / empty board / no board >= MIN_BOARD /
    an owned champion team unresolved) - the caller STOPs and does NOT compute on stale odds."""
    _load_dotenv()
    key = os.environ.get("THE_ODDS_API_KEY") or os.environ.get("ODDS_API_KEY")
    if not key:
        raise RuntimeError("no THE_ODDS_API_KEY in env/.env - cannot fetch fresh outrights (FM2). STOP.")
    date_label = date_label or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = out_dir or os.path.join(ROOT, "data")

    # --- A1: probe /v4/sports FIRST (0 cr) ---
    sports = _get(f"{BASE}/sports/?apiKey={key}")
    listed = any(isinstance(s, dict) and s.get("key") == SPORT for s in (sports.get("body") or []))
    print(f"[A1] /v4/sports  http={sports.get('status')}  {SPORT} listed={listed}  "
          f"latency={sports.get('latency_s')}s")
    if not listed:
        raise RuntimeError(f"A1 FAIL: {SPORT} not listed on this plan -> STOP (no stale, no paid API).")

    # --- odds call (2 cr: regions us,eu) ---
    url = f"{BASE}/sports/{SPORT}/odds/?regions={regions}&oddsFormat={odds_format}&apiKey={key}"
    resp = _get(url)
    rem = (resp.get("headers") or {}).get("x-requests-remaining")
    used = (resp.get("headers") or {}).get("x-requests-used")
    print(f"[D1] /odds outrights  http={resp.get('status')}  latency={resp.get('latency_s')}s  "
          f"x-requests-remaining={rem}  x-requests-used={used}")
    if not resp.get("ok"):
        raise RuntimeError(f"D1 FAIL: odds http={resp.get('status')} {resp.get('body')} -> STOP.")
    events = resp.get("body") or []
    boards = parse_outrights(events if isinstance(events, list) else [])
    print(f"[D1] books parsed: " + ", ".join(f"{t}({len(b)})" for t, b in
                                              sorted(boards.items(), key=lambda kv: -len(kv[1]))) or "(none)")
    if not boards:
        raise RuntimeError("D1 FAIL: empty outright board (no 'outrights' outcomes) -> STOP (FM2/LM6).")

    p_title, p_board, c_title, c_board = select_books(boards, MIN_BOARD)
    if p_board is None:
        sizes = {t: len(b) for t, b in boards.items()}
        raise RuntimeError(f"F2P1 FAIL: no book has a full board >= {MIN_BOARD} teams (sizes={sizes}) -> "
                           f"STOP (a truncated de-vig over-estimates P_true -> false 0.08 gate PASS, FM1).")

    # F2P1: every OWNED champion team must resolve on the PRIMARY board.
    unresolved = [t for t in OWNED_CHAMPION_TEAMS if t not in p_board]
    if unresolved:
        raise RuntimeError(f"F2P1 FAIL: owned champion team(s) {unresolved} not on primary board "
                           f"{p_title} (canon map gap?) -> STOP.")

    s_full = overround(p_board)
    p_owned = _devig_top(p_board, OWNED_CHAMPION_TEAMS)
    p_gate = _devig_top(p_board, ["England", "Argentina"])
    print(f"[D1] PRIMARY={p_title} ({len(p_board)} teams)  overround S_full={s_full:.4f}  "
          f"CROSSCHECK={c_title}({len(c_board) if c_board else 0})")
    print(f"[D1] {_spain_france_ordering(p_board)}")
    print("[D1] de-vigged P_true (FULL-board basis): "
          + ", ".join(f"{t}={p_owned[t]:.4f}" for t in OWNED_CHAMPION_TEAMS))
    for t in ("England", "Argentina"):
        v = p_gate[t]
        band = ("MOOT (>0.08)" if v and v > 0.08 else
                "BAND 0.05-0.08 -> reported-not-selected (PB1)" if v and v > 0.05 else "FAILS gate (<0.05)")
        print(f"[D1] gate {t}: P_true={v:.4f}  -> {band}" if v is not None else f"[D1] gate {t}: absent")

    payload = {
        "as_of": date_label,
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
        "note": (f"WC-2026 champion outrights, LIVE The Odds API ({SPORT}, market=outrights, regions="
                 f"{regions}). American. Primary={p_title} (full board, de-vig basis, F2P1>={MIN_BOARD}); "
                 f"crosscheck={c_title} (ordering/sanity only, NEVER the divisor, LM9). overround S_full "
                 f"printed. RECOMMEND-NEVER-LOCK."),
        "overround_primary": round(s_full, 6),
        "x_requests_remaining": rem,
        "primary": {"source": f"{p_title} (The Odds API)", "url": url.replace(key, "***"),
                    "format": "american", "odds": p_board},
        "crosscheck": ({"source": f"{c_title} (The Odds API)", "url": url.replace(key, "***"),
                        "format": "american", "odds": c_board} if c_board else {}),
    }
    out_path = os.path.join(out_dir, f"outrights_{date_label}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[D1] WROTE {out_path}  (primary {len(p_board)} teams, overround {s_full:.4f})")
    return payload


# --------------------------------------------------------------------------------------------------
def _selftest():
    """Offline: parse/select/overround on a SYNTHETIC Odds-API outrights response (no credits, no key)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    big = {"Spain": 450, "France": 480, "England": 650, "Brazil": 750, "Argentina": 900, "Portugal": 950,
           "Germany": 1300, "Netherlands": 1700, "Uruguay": 6000}
    big.update({f"Team{i}": 50000 for i in range(40)})              # pad to a full (>=40) board
    synth = [{"bookmakers": [
        {"key": "fanduel", "title": "FanDuel",
         "markets": [{"key": "outrights", "outcomes": [{"name": n, "price": p} for n, p in big.items()]}]},
        {"key": "betmgm", "title": "BetMGM",
         "markets": [{"key": "outrights", "outcomes": [{"name": n, "price": p} for n, p in
                                                       list(big.items())[:8]]}]},   # truncated (8) -> not primary
    ]}]
    boards = parse_outrights(synth)
    assert set(boards) == {"FanDuel", "BetMGM"}, boards
    p_title, p_board, c_title, c_board = select_books(boards, MIN_BOARD)
    assert p_title == "FanDuel" and len(p_board) >= MIN_BOARD, (p_title, len(p_board))   # F2P1: full board wins
    assert c_title == "BetMGM", c_title
    # truncated-only response -> select STOPs (None)
    trunc = parse_outrights([{"bookmakers": [
        {"key": "x", "title": "X", "markets": [{"key": "outrights",
         "outcomes": [{"name": n, "price": p} for n, p in list(big.items())[:8]]}]}]}])
    assert select_books(trunc, MIN_BOARD)[1] is None, "F2P1 must STOP when no board >= MIN_BOARD"
    # canonicalization
    assert _canon("United States") == "USA" and _canon("Czech Republic") == "Czechia"
    # de-vig sanity: full-board P_true sums to ~1 over the board; owned teams all resolve
    s = overround(p_board)
    pt = {t: american_to_prob(p_board[t]) / s for t in OWNED_CHAMPION_TEAMS}
    assert all(t in p_board for t in OWNED_CHAMPION_TEAMS), "owned team unresolved on synthetic board"
    assert 0.999 < sum(american_to_prob(v) / s for v in p_board.values()) < 1.001
    print("fetch_outrights self-test: PASS")
    print(f"  primary={p_title}({len(p_board)})  crosscheck={c_title}({len(c_board)})  S_full={s:.4f}")
    print(f"  de-vig: Spain={pt['Spain']:.4f} France={pt['France']:.4f} "
          f"(synthetic; real numbers come from the LIVE Step-1 fetch)")


def main():
    if "--selftest" in sys.argv:
        _selftest()
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fetch_outrights()


if __name__ == "__main__":
    main()
