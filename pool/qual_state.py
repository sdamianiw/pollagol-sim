"""qual_state.py - MD-3 qualification-state engine (READ-ONLY / BUILD-NOT-FIRE).

WHY: yesterday's MD-3 baselines show a correlated ANTI-DRAW bias - 9/18 boards have a draw modal yet
EV-argmax (§5 OFF, L17 draw-compression) keeps the draw on only 1. The single sanctioned MD-3 override is
a HITL draw-exception; it must fire only where a draw is STRUCTURALLY favoured, never on gut. This module
computes, per still-upcoming MD-3 fixture, a deterministic qualification-state tag from the results already
in predictions/decisions.csv, brute-forcing the remaining within-group outcome space, so the HITL can tell
"draw LIVE" from "trust EV-win".

THE REFRAME (the operative draw signal is MUTUAL-DRAW-SECURES, NOT strict dead-rubber):
  STRICT-DEAD-RUBBER (both guaranteed top-2 regardless of result) = the WEAKER, HIGH-VARIANCE case (teams
    rotate / play loose) -> NO draw lean.
  MUTUAL-DRAW-SECURES (a mutual draw guarantees both top-2; a loss risks 3rd) = the operative draw signal
    (the "convenient draw"). e.g. SUI-CAN (Group B = SUI 4 / CAN 4 / BIH 1 / QAT 1).

SIGNAL TAXONOMY:
  (A) Per-OUTCOME classifier - exhaustive (s,t), mutually exclusive (no implicit else, no UNCLASSIFIED).
      For team T over its 3 group-mates: s = #others with pts > pT ; t = #others with pts == pT.
        s >= 2            -> ELIMINATED       (this outcome)
        s + t <= 1        -> TOP2-GUARANTEED  (top-2 regardless of any GD/H2H tiebreak)
        else (s<=1, s+t>=2) -> TOP2-TIEBREAK  (2nd-vs-3rd hinges on tiebreak -> flagged, NOT resolved;
                                               v1 enumerates W/D/L only, never scorelines)
  (B) Per-TEAM state - from T's own-result partition (conservative: a tie for 2nd is NOT a guarantee).
      win_g/draw_g/loss_g = TOP2-GUARANTEED in ALL outcomes where T wins / draws / loses.
        not win_g                     -> ELIMINATED      (not even winning guarantees top-2)
        win_g and not draw_g          -> MUST-WIN        (only a win secures)
        win_g and draw_g and loss_g   -> SAFE-ANY        (guaranteed in every outcome incl. a loss)
        else                          -> DRAW-SUFFICIENT (a draw secures; a loss risks 3rd)
      draw_secures == state in {SAFE-ANY, DRAW-SUFFICIENT}.  (draw_g => win_g, so the four are exhaustive.)
      best_third_alive = T can finish >=3rd within-group in some outcome (s(T) <= 2). Cross-group best-third
        is OUT OF SCOPE -> 3RD-PENDING, never resolved here.
  (C) Fixture TAG (precedence top-down; per-team MUST-WIN is a TEAM state, WIN-REQUIRED is the FIXTURE tag -
      never conflated):
        1. 3RD-PENDING        either team ELIMINATED and best_third_alive (cross-group manual). DOMINATES.
        2. DECIDED            both ELIMINATED and neither best_third_alive (structurally unreachable in a
                              real 4-team group - kept for totality / branch coverage).
        3. STRICT-DEAD-RUBBER both SAFE-ANY (HIGH-VARIANCE, NOT a draw signal).
        4. MUTUAL-DRAW-SECURES both draw_secures (the draw signal).
        5. WIN-REQUIRED       some team draw_secures == False (no draw lean; trust EV-win).
  (D) DRAW-EXCEPTION LIVE = YES iff tag == MUTUAL-DRAW-SECURES AND market draw-price is thin (HITL
      threshold, NOT hardcoded). "LIVE" = strong HITL recommendation to consider the draw (toward FEWER
      goals), NEVER an auto-lock. Do NOT fire on STRICT-DEAD-RUBBER or any board with a WIN-REQUIRED team.

NOTE: STRICT-DEAD-RUBBER means neither team's QUALIFICATION (top-2) can change - NOT that neither team
cares (seeding is out of scope). MUTUAL-DRAW-SECURES is the draw signal, not it.

I3 (cardinal invariant) holds: this module READS results to compute standings (the permitted one-way
decisions.csv -> read-only scoring flow) and writes NO model parameter. It changes NO pick, edits NO frozen
file, only RECOMMENDS; the human types/locks (I-HITL). Determinism: pure integer combinatorics, no RNG.
"""
from __future__ import annotations

import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.decisionlog import read_decisions, DECISIONS_PATH  # noqa: E402  (read-only ingest)
from src.decision_score import parse_score                  # noqa: E402  (reuse, never reimplement)

RESULTS = ("H", "D", "A")                       # a game's result: home win / draw / away win
_STATE_ORDER = {"ELIMINATED": 0, "MUST-WIN": 1, "DRAW-SUFFICIENT": 2, "SAFE-ANY": 3}


# --- group structure (union-find over the fixture graph) -------------------------------------------
def build_groups(rows: list[dict]) -> dict[str, frozenset]:
    """Connected components of the (home,away) fixture graph. Returns {root: frozenset of 4 teams}.

    Edges use every row (played or not). Raises if any component is not exactly 4 (FM-guard)."""
    parent: dict[str, str] = {}

    def find(t: str) -> str:
        parent.setdefault(t, t)
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for r in rows:
        h, a = r.get("home"), r.get("away")
        if h and a:
            union(h, a)

    comps: dict[str, set] = {}
    for t in list(parent):
        comps.setdefault(find(t), set()).add(t)

    groups: dict[str, frozenset] = {}
    for root, members in comps.items():
        if len(members) != 4:
            raise ValueError(f"group component {sorted(members)} has {len(members)} != 4 members")
        groups[root] = frozenset(members)
    return groups


# --- group table (integrity-guarded) ---------------------------------------------------------------
def build_group_table(rows: list[dict], members: frozenset) -> dict[str, dict]:
    """Accumulate Pts/W/D/L/GF/GA/GD/n from PLAYED rows for the 4 `members`.

    Raises on an integrity violation (Σpts != 3·n_decisive + 2·n_draw, or ΣGF != ΣGA) - a recording
    error in decisions.csv (FM-recording-error)."""
    tbl = {tm: {"pts": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "n": 0} for tm in members}
    n_dec = n_draw = 0
    for r in rows:
        h, a = r.get("home"), r.get("away")
        if h not in members or a not in members:
            continue
        res = (r.get("result") or "").strip()
        if not res:
            continue
        hg, ag = parse_score(res)
        tbl[h]["gf"] += hg; tbl[h]["ga"] += ag; tbl[h]["n"] += 1
        tbl[a]["gf"] += ag; tbl[a]["ga"] += hg; tbl[a]["n"] += 1
        if hg > ag:
            tbl[h]["pts"] += 3; tbl[h]["w"] += 1; tbl[a]["l"] += 1; n_dec += 1
        elif ag > hg:
            tbl[a]["pts"] += 3; tbl[a]["w"] += 1; tbl[h]["l"] += 1; n_dec += 1
        else:
            tbl[h]["pts"] += 1; tbl[a]["pts"] += 1; tbl[h]["d"] += 1; tbl[a]["d"] += 1; n_draw += 1
    for tm in members:
        tbl[tm]["gd"] = tbl[tm]["gf"] - tbl[tm]["ga"]
    _integrity_check(tbl, members, n_dec, n_draw)
    return tbl


def _integrity_check(tbl: dict, members: frozenset, n_dec: int, n_draw: int) -> None:
    """Accumulation-regression guard (Σpts == 3·n_decisive + 2·n_draw, ΣGF == ΣGA). These hold
    structurally for a correct accumulation, so a raise means a build_group_table bug (or an injected
    inconsistency). The recorded-DATA guard is the external cross-check (computed != fetched -> STOP)."""
    sum_pts = sum(tbl[tm]["pts"] for tm in members)
    if sum_pts != 3 * n_dec + 2 * n_draw:
        raise ValueError(f"integrity Σpts={sum_pts} != 3·{n_dec}+2·{n_draw} for {sorted(members)}")
    sum_gf = sum(tbl[tm]["gf"] for tm in members)
    sum_ga = sum(tbl[tm]["ga"] for tm in members)
    if sum_gf != sum_ga:
        raise ValueError(f"integrity ΣGF={sum_gf} != ΣGA={sum_ga} for {sorted(members)}")


# --- remaining MD-3 pairs (synthesize J/K/L complements) ------------------------------------------
def find_md3_pairs(rows: list[dict], members: frozenset) -> list[dict]:
    """The 2 remaining MD-3 pairs for `members`: an empty-result row (baselined), or - for groups whose
    MD-3 row is not yet in the CSV (J/K/L) - the COMPLEMENT of the 4 played pairs, synthesized (home/away
    alphabetical, fixture_id/utc=None). Asserts exactly 2 and that they are disjoint."""
    mem = sorted(members)
    all_pairs = list(itertools.combinations(mem, 2))   # 6 sorted pairs
    played: set = set()
    row_by_pair: dict[tuple, dict] = {}
    for r in rows:
        h, a = r.get("home"), r.get("away")
        if h not in members or a not in members:
            continue
        key = tuple(sorted((h, a)))
        row_by_pair[key] = r
        if (r.get("result") or "").strip():
            played.add(key)

    remaining = [p for p in all_pairs if p not in played]
    if len(remaining) != 2:
        raise ValueError(f"group {mem}: {len(remaining)} remaining pairs (need 2): {remaining}")

    out = []
    for p in remaining:
        r = row_by_pair.get(p)
        if r is not None:                                   # baselined MD-3 row (empty result)
            out.append({"home": r["home"], "away": r["away"], "synthesized": False,
                        "fixture_id": (r.get("fixture_id") or None), "utc": (r.get("utc") or None)})
        else:                                               # not yet in the CSV -> synthesize
            out.append({"home": p[0], "away": p[1], "synthesized": True,
                        "fixture_id": None, "utc": None})

    g1, g2 = out
    if {g1["home"], g1["away"]} & {g2["home"], g2["away"]}:
        raise ValueError(f"group {mem}: remaining pairs not disjoint")
    return out


# --- the brute-force ------------------------------------------------------------------------------
def _classify(p_t: int, others: list[int]) -> str:
    """Exhaustive (s,t) per-outcome classifier. Returns ELIMINATED | TOP2-GUARANTEED | TOP2-TIEBREAK."""
    s = sum(1 for p in others if p > p_t)
    t = sum(1 for p in others if p == p_t)
    if s >= 2:
        return "ELIMINATED"
    if s + t <= 1:
        return "TOP2-GUARANTEED"
    return "TOP2-TIEBREAK"                                  # s<=1 and s+t>=2 (exhaustive remainder)


def _game_points(game: tuple, res: str) -> dict:
    h, a = game
    if res == "H":
        return {h: 3, a: 0}
    if res == "D":
        return {h: 1, a: 1}
    return {h: 0, a: 3}                                     # "A"


def _own_result(team: str, game: tuple, res: str) -> str:
    """T's own W/D/L given the game's H/D/A result (team must be in game)."""
    if res == "D":
        return "D"
    h, _ = game
    if team == h:
        return "W" if res == "H" else "L"
    return "W" if res == "A" else "L"


def qualification_states(table: dict, game1: tuple, game2: tuple) -> dict[str, dict]:
    """9-outcome (3x3) within-group brute-force over the two remaining MD-3 games. Per team returns its
    state + draw_secures/win_g/draw_g/loss_g/best_third_alive/tiebreak_sensitive/tiebreak_outcomes/game.
    Each team is routed to its game by MEMBERSHIP (not loop order - FM-team-dispatch)."""
    teams = list(game1) + list(game2)
    base = {tm: int(table[tm]["pts"]) for tm in teams}
    games = (game1, game2)

    outcomes = []                                          # (r1, r2, final_pts, per-team class)
    for r1 in RESULTS:
        for r2 in RESULTS:
            fp = dict(base)
            for g, r in ((game1, r1), (game2, r2)):
                for tm, pts in _game_points(g, r).items():
                    fp[tm] += pts
            cls = {tm: _classify(fp[tm], [fp[o] for o in teams if o != tm]) for tm in teams}
            outcomes.append((r1, r2, fp, cls))

    out: dict[str, dict] = {}
    for tm in teams:
        g_idx = 0 if tm in game1 else 1                    # membership routing
        my_game = games[g_idx]
        by_res = {"W": [], "D": [], "L": []}
        s_vals, tb_count = [], 0
        for (r1, r2, fp, cls) in outcomes:
            my_r = _own_result(tm, my_game, r1 if g_idx == 0 else r2)
            by_res[my_r].append(cls[tm])
            s_vals.append(sum(1 for o in teams if o != tm and fp[o] > fp[tm]))
            if cls[tm] == "TOP2-TIEBREAK":
                tb_count += 1

        def all_guar(lst):
            return all(c == "TOP2-GUARANTEED" for c in lst)

        win_g, draw_g, loss_g = all_guar(by_res["W"]), all_guar(by_res["D"]), all_guar(by_res["L"])
        if not win_g:
            state = "ELIMINATED"
        elif not draw_g:
            state = "MUST-WIN"
        elif loss_g:
            state = "SAFE-ANY"
        else:
            state = "DRAW-SUFFICIENT"

        def relaxed(lst):                                  # treat TIEBREAK as if GUARANTEED
            return all(c in ("TOP2-GUARANTEED", "TOP2-TIEBREAK") for c in lst)

        rw, rd, rl = relaxed(by_res["W"]), relaxed(by_res["D"]), relaxed(by_res["L"])
        if not rw:
            state2 = "ELIMINATED"
        elif not rd:
            state2 = "MUST-WIN"
        elif rl:
            state2 = "SAFE-ANY"
        else:
            state2 = "DRAW-SUFFICIENT"

        out[tm] = {
            "state": state,
            "draw_secures": state in ("SAFE-ANY", "DRAW-SUFFICIENT"),
            "win_g": win_g, "draw_g": draw_g, "loss_g": loss_g,
            "best_third_alive": any(s <= 2 for s in s_vals),
            "tiebreak_sensitive": _STATE_ORDER[state2] > _STATE_ORDER[state],
            "tiebreak_outcomes": tb_count,
            "game": tuple(my_game),
        }
    return out


# --- fixture tag (precedence) ---------------------------------------------------------------------
def fixture_tags(states: dict, game1: tuple, game2: tuple) -> list[dict]:
    """Apply the fixture-tag precedence to each of the two games. Pure function of `states`."""
    tags = []
    for g in (game1, game2):
        x, y = g
        sx, sy = states[x], states[y]
        elim_third = ((sx["state"] == "ELIMINATED" and sx["best_third_alive"]) or
                      (sy["state"] == "ELIMINATED" and sy["best_third_alive"]))
        both_dead = (sx["state"] == "ELIMINATED" and not sx["best_third_alive"] and
                     sy["state"] == "ELIMINATED" and not sy["best_third_alive"])
        if elim_third:
            tag = "3RD-PENDING"
        elif both_dead:                                    # before WIN-REQUIRED, else unreachable
            tag = "DECIDED"
        elif sx["state"] == "SAFE-ANY" and sy["state"] == "SAFE-ANY":
            tag = "STRICT-DEAD-RUBBER"
        elif sx["draw_secures"] and sy["draw_secures"]:
            tag = "MUTUAL-DRAW-SECURES"
        else:
            tag = "WIN-REQUIRED"
        detail = f"{x}: {sx['state']} · {y}: {sy['state']}"
        if tag == "3RD-PENDING":
            chasers = [t for t in (x, y) if states[t]["state"] == "ELIMINATED"
                       and states[t]["best_third_alive"]]
            detail += f"  [best-third-alive: {', '.join(chasers)} -> cross-group MANUAL]"
        elif tag == "WIN-REQUIRED":
            need = [t for t in (x, y) if not states[t]["draw_secures"]]
            detail += f"  [must win: {', '.join(need)} -> trust EV-win, no draw lean]"
        tags.append({
            "fixture": g,
            "tag": tag,
            "draw_secures_both": sx["draw_secures"] and sy["draw_secures"],
            "thresholds": {x: sx["state"], y: sy["state"]},
            "tiebreak_sensitive": {t: states[t]["tiebreak_sensitive"] for t in (x, y)},
            "detail": detail,
        })
    return tags


# --- composition ----------------------------------------------------------------------------------
def analyze_group(members: frozenset, rows: list[dict]) -> dict:
    table = build_group_table(rows, members)
    pairs = find_md3_pairs(rows, members)
    g1 = (pairs[0]["home"], pairs[0]["away"])
    g2 = (pairs[1]["home"], pairs[1]["away"])
    states = qualification_states(table, g1, g2)
    tags = fixture_tags(states, g1, g2)
    for tag, meta in zip(tags, pairs):                     # attach synth/id/utc (order-aligned)
        tag["synthesized"] = meta["synthesized"]
        tag["fixture_id"] = meta["fixture_id"]
        tag["utc"] = meta["utc"]
    return {"members": sorted(members), "table": table, "md3_pairs": pairs,
            "states": states, "tags": tags}


def analyze_all(rows: list[dict]) -> dict:
    """Analyze all 12 groups. Keyed by the sorted-members tuple (deterministic order)."""
    groups = build_groups(rows)
    result = {}
    for members in sorted(groups.values(), key=lambda m: tuple(sorted(m))):
        result[tuple(sorted(members))] = analyze_group(members, rows)
    return result


# --- merged HITL decision sheet -------------------------------------------------------------------
def _is_draw(score_str: str) -> bool:
    try:
        h, a = parse_score(score_str)
        return h == a
    except Exception:
        return False


def decision_sheet(rows: list[dict], analyses: dict | None = None) -> list[dict]:
    """Merge each upcoming MD-3 fixture's qual-tag with its EV-argmax baseline + market draw-price (read
    from the decisions.csv row: pick=EV-pick, modal, devig_d=de-vig market P(draw)). Synthesized J/K/L
    fixtures carry the tag but EV/price = pending-fetch. Sorted by utc (synthesized last)."""
    if analyses is None:
        analyses = analyze_all(rows)
    by_fid = {r.get("fixture_id"): r for r in rows if r.get("fixture_id")}
    sheet = []
    for grp in analyses.values():
        for tag in grp["tags"]:
            fid = tag.get("fixture_id")
            row = by_fid.get(fid) if fid else None
            home, away = tag["fixture"]
            ev_pick = (row or {}).get("pick") or "-"
            modal = (row or {}).get("modal") or "-"
            devig_d = (row or {}).get("devig_d") or ""
            try:
                price = round(float(devig_d), 3) if devig_d else None
            except Exception:
                price = None
            draw_modal = _is_draw(modal) if modal != "-" else None
            if tag["synthesized"] or row is None:
                live = "pending-fetch"
            elif tag["tag"] == "MUTUAL-DRAW-SECURES":
                price_s = f"{price:.3f}" if price is not None else "?"
                live = f"LIVE-ELIGIBLE (price={price_s}; HITL: fire iff <= thin-threshold)"
            else:
                live = f"no ({tag['tag']})"
            sheet.append({
                "utc": tag.get("utc") or "ZZZ-pending",
                "fixture": f"{home} v {away}",
                "tag": tag["tag"],
                "ev_pick": ev_pick, "modal": modal, "draw_price": price,
                "draw_modal": draw_modal, "draw_exception": live,
                "synthesized": tag["synthesized"], "detail": tag["detail"],
            })
    sheet.sort(key=lambda r: r["utc"])
    return sheet


# --- external cross-check (best-effort; UNVERIFIED graceful-degrade) -------------------------------
# Full-string <-> full-string name map (NEVER a 3-letter code: ARG = Argentina != Algeria, L34).
_FD_NAME_MAP = {
    "United States": "USA", "Korea Republic": "South Korea", "Congo DR": "DR Congo",
    "IR Iran": "Iran", "Côte d'Ivoire": "Ivory Coast", "Cabo Verde": "Cape Verde",
    "Türkiye": "Turkey", "Curacao": "Curaçao",
}


def external_crosscheck(tables: dict, timeout: int = 20) -> tuple[str, str]:
    """Best-effort verification vs football-data.org /v4/competitions/WC/standings. Returns
    (status, detail) where status in {PASS, MISMATCH, UNVERIFIED}. A MISMATCH means a decisions.csv
    recording error (STOP). Any fetch/parse failure -> UNVERIFIED (proceed on computed + invariants).
    I-NOFAB: NEVER overwrites a computed table with fetched data."""
    try:
        from src.probe_oddssource import _get, _load_dotenv
        _load_dotenv()
        token = os.environ.get("FOOTBALL_DATA_KEY") or os.environ.get("FD_API_KEY")
        headers = {"X-Auth-Token": token} if token else None
        r = _get("https://api.football-data.org/v4/competitions/WC/standings",
                 headers=headers, timeout=timeout)
        if not r.get("ok") or not isinstance(r.get("body"), dict):
            return "UNVERIFIED", f"fetch not ok (status={r.get('status')}; free-tier WC-2026 likely absent)"
        fetched = {}
        for grp in r["body"].get("standings", []):
            if grp.get("type") not in (None, "TOTAL"):
                continue
            for row in grp.get("table", []):
                name = (row.get("team") or {}).get("name", "")
                name = _FD_NAME_MAP.get(name, name)
                fetched[name] = int(row.get("points", -1))
        if not fetched:
            return "UNVERIFIED", "fetched standings empty / shape unexpected"
        mism = []
        for members in (tables if isinstance(tables, list) else [tables]):
            for tm, rec in members.items():
                if tm in fetched and fetched[tm] != rec["pts"]:
                    mism.append(f"{tm}: computed {rec['pts']} != fetched {fetched[tm]}")
        if mism:
            return "MISMATCH", "; ".join(mism)
        return "PASS", f"{len(fetched)} teams matched"
    except Exception as e:                                 # network down, import error, parse fail
        return "UNVERIFIED", f"{type(e).__name__}: {e}"


# --- selftest (constructed anchors; pytest holds the full suite) ----------------------------------
def _t(pts: dict) -> dict:
    return {tm: {"pts": p} for tm, p in pts.items()}


def _selftest():
    print("=" * 78)
    # (a) MUTUAL-DRAW-SECURES anchor: real Group B.
    gb = _t({"SUI": 4, "CAN": 4, "BIH": 1, "QAT": 1})
    st_b = qualification_states(gb, ("SUI", "CAN"), ("BIH", "QAT"))
    tg_b = {t["fixture"]: t for t in fixture_tags(st_b, ("SUI", "CAN"), ("BIH", "QAT"))}
    print(f"(a) SUI={st_b['SUI']['state']} CAN={st_b['CAN']['state']} -> "
          f"SUI-CAN={tg_b[('SUI','CAN')]['tag']}")
    assert st_b["SUI"]["state"] == "DRAW-SUFFICIENT" and st_b["CAN"]["state"] == "DRAW-SUFFICIENT"
    assert tg_b[("SUI", "CAN")]["tag"] == "MUTUAL-DRAW-SECURES"
    # (b) 3RD-PENDING anchor: BIH-QAT (both ELIMINATED + best-third-alive) - NOT MUST-WIN.
    print(f"(b) BIH={st_b['BIH']['state']} QAT={st_b['QAT']['state']} -> "
          f"BIH-QAT={tg_b[('BIH','QAT')]['tag']}")
    assert st_b["BIH"]["state"] == "ELIMINATED" and st_b["QAT"]["state"] == "ELIMINATED"
    assert st_b["BIH"]["best_third_alive"] and tg_b[("BIH", "QAT")]["tag"] == "3RD-PENDING"
    # (c) STRICT-DEAD-RUBBER anchor: constructed both-SAFE-ANY.
    gd = _t({"A": 6, "B": 6, "C": 0, "D": 0})
    st_d = qualification_states(gd, ("A", "B"), ("C", "D"))
    tg_d = {t["fixture"]: t for t in fixture_tags(st_d, ("A", "B"), ("C", "D"))}
    print(f"(c) A={st_d['A']['state']} B={st_d['B']['state']} -> A-B={tg_d[('A','B')]['tag']}")
    assert st_d["A"]["state"] == "SAFE-ANY" and st_d["B"]["state"] == "SAFE-ANY"
    assert tg_d[("A", "B")]["tag"] == "STRICT-DEAD-RUBBER"
    # (d) MUST-WIN/DRAW-SUFFICIENT threshold (pairing declared: game1=(Scotland,Brazil)).
    gc = _t({"Brazil": 4, "Morocco": 4, "Scotland": 3, "Haiti": 0})
    st_c = qualification_states(gc, ("Scotland", "Brazil"), ("Morocco", "Haiti"))
    print(f"(d) Scotland={st_c['Scotland']['state']} Brazil={st_c['Brazil']['state']}")
    assert st_c["Scotland"]["state"] == "MUST-WIN" and st_c["Brazil"]["state"] == "DRAW-SUFFICIENT"
    # (e) (s,t) classifier exhaustive: the reproduced UNCLASSIFIED leaks all -> TIEBREAK; full sweep ok.
    assert _classify(5, [5, 5, 3]) == "TOP2-TIEBREAK"          # (s=0,t=2)
    assert _classify(5, [5, 5, 5]) == "TOP2-TIEBREAK"          # (s=0,t=3)
    assert _classify(5, [7, 5, 5]) == "TOP2-TIEBREAK"          # (s=1,t=2)
    seen = set()
    for s in range(4):
        for t in range(4 - s):
            others = [10] * s + [5] * t + [0] * (3 - s - t)
            seen.add(_classify(5, others))
    assert seen <= {"ELIMINATED", "TOP2-GUARANTEED", "TOP2-TIEBREAK"}
    print("(e) (s,t) exhaustive: no UNCLASSIFIED across the full sweep")
    print("SELFTEST: PASS  (a) SUI-CAN->MDS  (b) BIH-QAT->3RD-PENDING  (c) constructed->STRICT  "
          "(d) SCO->MUST-WIN  (e) (s,t) exhaustive")
    print("=" * 78)


def _fmt_table(members_sorted, tbl) -> str:
    rank = sorted(members_sorted, key=lambda tm: (-tbl[tm]["pts"], -tbl[tm]["gd"], -tbl[tm]["gf"]))
    lines = [f"  {'team':<22} {'P':>2} {'W':>2} {'D':>2} {'L':>2} {'GF':>3} {'GA':>3} {'GD':>3}"]
    for tm in rank:
        r = tbl[tm]
        lines.append(f"  {tm:<22} {r['pts']:>2} {r['w']:>2} {r['d']:>2} {r['l']:>2} "
                     f"{r['gf']:>3} {r['ga']:>3} {r['gd']:>+3}")
    return "\n".join(lines)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    rows = read_decisions(DECISIONS_PATH)
    analyses = analyze_all(rows)
    analyses2 = analyze_all(rows)                          # determinism (B4)
    det = "PASS" if (str(analyses) == str(analyses2)) else "FAIL"

    print("=" * 78)
    print(f"MD-3 QUALIFICATION STATE  ·  {len(analyses)} groups  ·  determinism(B4)={det}")
    print("=" * 78)
    for members_t, grp in analyses.items():
        md3 = " + ".join(f"{p['home']}-{p['away']}{'*' if p['synthesized'] else ''}"
                         for p in grp["md3_pairs"])
        print(f"\nGROUP {{{', '.join(members_t)}}}   MD-3: {md3}   (*=synthesized, not yet in CSV)")
        print(_fmt_table(grp["members"], grp["table"]))
        for tm in sorted(grp["states"], key=lambda t: -grp["table"][t]["pts"]):
            s = grp["states"][tm]
            ts = " [tiebreak-sensitive]" if s["tiebreak_sensitive"] else ""
            print(f"    {tm:<22} {s['state']:<15} draw_secures={int(s['draw_secures'])} "
                  f"best_third_alive={int(s['best_third_alive'])} tb_outcomes={s['tiebreak_outcomes']}{ts}")
        for t in grp["tags"]:
            print(f"    -> {t['fixture'][0]}-{t['fixture'][1]:<18} {t['tag']:<20} {t['detail']}")

    print("\n" + "=" * 78)
    print("MERGED DECISION SHEET (HITL)  ·  DRAW-EXCEPTION LIVE only on MUTUAL-DRAW-SECURES + thin price")
    print("=" * 78)
    sheet = decision_sheet(rows, analyses)
    print(f"{'KO(UTC)':<20} {'fixture':<30} {'EVpick':>6} {'modal':>6} {'drawP':>6} {'tag':<20} draw-exception")
    print("-" * 110)
    for r in sheet:
        ko = "(pending)" if r["utc"].startswith("ZZZ") else r["utc"]
        dp = f"{r['draw_price']:.3f}" if r["draw_price"] is not None else "  -  "
        dm = "*" if r["draw_modal"] else " "
        print(f"{ko:<20} {r['fixture'][:30]:<30} {r['ev_pick']:>6} {r['modal']:>5}{dm} {dp:>6} "
              f"{r['tag']:<20} {r['draw_exception']}")
    print("-" * 110)

    # DEFER-6: enumerate the draw-modal boards -> draw-LIVE | trust-EV-win.
    dm_boards = [r for r in sheet if r["draw_modal"]]
    print(f"\nDRAW-MODAL BOARDS (modal is a draw): {len(dm_boards)} — anti-draw-bias disambiguation")
    for r in dm_boards:
        verdict = "draw-LIVE" if r["tag"] == "MUTUAL-DRAW-SECURES" else "trust-EV-win"
        print(f"    {r['fixture']:<30} tag={r['tag']:<20} -> {verdict}")

    status, detail = external_crosscheck([g["table"] for g in analyses.values()])
    print(f"\nEXTERNAL CROSS-CHECK (football-data.org, best-effort): {status} — {detail}")
    if status == "MISMATCH":
        print("  🛑 STOP: computed != fetched -> a decisions.csv recording error. Do NOT proceed.")
    elif status == "UNVERIFIED":
        print("  ⚠ UNVERIFIED — proceeding on computed tables + internal invariants (Σpts, ΣGF=ΣGA).")

    _selftest()


if __name__ == "__main__":
    main()
