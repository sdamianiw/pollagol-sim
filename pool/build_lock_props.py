"""build_lock_props.py - LOCK-RUN Step 3: write the fresh Jun-10 prop boards (scorer/MVP/GK) as dated JSON.

Provenance (web-fetched 2026-06-10, decision-grade lock run; sources + dates below). Player names are
ASCII-normalized to the board-key convention used by the observed-ownership snapshot (so observed picks
resolve). RB3: ONE book per award is the de-vig basis (full board as the book presented it; a truncated
board over-states P_true -> FM1). De-vig + top-6 happen at engine time in council.market_p_true; this file
only stores the raw American board. The ASSISTER board is FLAT (K=4 gate fail) -> NOT written, NOT an engine
lever (FM3: no fabricated P_true). Re-runnable; writes data/props_<award>_2026-06-10.json. NOT A LOCK.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from pool.leverage import american_to_prob  # noqa: E402

DATE = "2026-06-10"

# --- Golden Boot / top scorer: DraftKings, updated 2026-06-08 11:06 EST (153-player full board) ---
SCORER = {
    "Kylian Mbappe": 600, "Harry Kane": 700, "Erling Haaland": 1400, "Mikel Oyarzabal": 1400,
    "Lionel Messi": 1600, "Cristiano Ronaldo": 2000, "Lamine Yamal": 2200, "Ousmane Dembele": 2500,
    "Raphinha": 2800, "Julian Alvarez": 3000, "Vinicius Junior": 3000, "Kai Havertz": 3000,
    "Lautaro Martinez": 3500, "Cody Gakpo": 4000, "Romelu Lukaku": 4000, "Mikel Merino": 4000,
    "Donyell Malen": 5000, "Jean-Philippe Mateta": 5000, "Ferran Torres": 5000, "Bukayo Saka": 5000,
    "Igor Thiago": 5000, "Michael Olise": 5000, "Endrick": 5000, "Deniz Undav": 5000,
    "Memphis Depay": 5000, "Luis Diaz": 5000, "Desire Doue": 5000, "Matheus Cunha": 5000,
    "Luis Javier Suarez": 5000, "Morgan Rogers": 6500, "Santiago Gimenez": 6500, "Darwin Nunez": 6500,
    "Eberechi Eze": 6500, "Jude Bellingham": 6500, "Alexander Isak": 6500, "Goncalo Ramos": 6500,
    "Jamal Musiala": 6500, "Leandro Trossard": 6500, "Marcus Rashford": 6500, "Ollie Watkins": 6500,
    "Florian Wirtz": 6500, "Neymar": 6500, "Enner Valencia": 6500, "Bruno Fernandes": 6500,
    "Nick Woltemade": 6500, "Alexander Sorloth": 6500, "Dani Olmo": 6500, "Folarin Balogun": 8000,
    "Kevin De Bruyne": 8000, "Christian Pulisic": 8000, "Anthony Gordon": 8000, "Rafael Leao": 8000,
    "Jeremy Doku": 8000, "Sadio Mane": 8000, "Marcus Thuram": 8000, "Brian Brobbey": 8000,
    "Leroy Sane": 8000, "Viktor Gyokeres": 8000, "Raul Jimenez": 8000, "Mohamed Salah": 8000,
    "Joao Felix": 8000, "Ayase Ueda": 8000, "Omar Marmoush": 10000, "Mohammed Kudus": 10000,
    "Charles De Ketelaere": 10000, "Nicolas Jackson": 10000, "Rayan Cherki": 10000, "Jonathan David": 10000,
    "Breel Embolo": 10000, "Christoph Baumgartner": 10000, "Ayoub El Kaabi": 10000, "Rayan": 10000,
    "Pedro Neto": 10000, "Haji Wright": 10000, "Nico Williams": 10000, "Ante Budimir": 10000,
    "Ricardo Pepi": 10000, "Son Heung-min": 10000, "Federico Valverde": 10000, "Bradley Barcola": 10000,
    "Gabriel Martinelli": 10000, "Ismaila Sarr": 15000, "Arda Guler": 15000, "Noa Lang": 15000,
    "Edin Dzeko": 15000, "Ivan Toney": 15000, "Kang-In Lee": 15000, "Kerem Akturkoglu": 15000,
    "Ange-Yoan Bonny": 15000, "Enzo Fernandez": 15000, "Promise David": 15000, "Kenan Yildiz": 15000,
    "Patrik Schick": 15000, "Jorgen Strand Larsen": 15000, "Riyad Mahrez": 15000, "Armando Gonzalez": 15000,
    "Julian Quinones": 15000, "Sepe Elye Wahi": 15000, "James Rodriguez": 15000, "Scott McTominay": 15000,
    "Brahim Diaz": 15000, "Andrej Kramaric": 15000, "Jhon Arias": 15000, "Giorgian De Arrascaeta": 20000,
    "Lucas Paqueta": 20000, "Che Adams": 20000, "Ermedin Demirovic": 20000, "Inaki Williams": 20000,
    "Chris Wood": 20000, "Amad Diallo": 20000, "Alphonso Davies": 20000, "Yan Diomande": 20000,
    "Mohamed El Amine Amoura": 20000, "Nicolas Pepe": 20000, "Cyle Larin": 20000, "Benjamin Nygren": 20000,
    "Noah Okafor": 20000, "Casemiro": 20000, "Amine Gouiri": 20000, "Martin Odegaard": 20000,
    "Daizen Maeda": 20000, "Mohamed Toure": 20000, "Crysencio Summerville": 20000, "Lawrence Shankland": 20000,
    "Denzel Dumfries": 20000, "Federico Vinas": 20000, "Yoane Wissa": 25000, "Pedri": 25000,
    "Anthony Elanga": 25000, "Giovanni Reyna": 25000, "Oscar Bobb": 25000, "Dan Ndoye": 25000,
    "Moussa Tamari": 25000, "Zeki Amdouni": 25000, "Fabian Ruiz": 25000, "Julio Enciso": 25000,
    "Eldor Shomurodov": 25000, "Achraf Hakimi": 25000, "Takefusa Kubo": 25000, "Cedric Bakambu": 25000,
    "Ismael Saibari": 25000, "Granit Xhaka": 25000, "Marcel Sabitzer": 25000, "Brenden Aaronson": 50000,
    "Tomas Soucek": 50000, "Ismael Diaz": 50000, "Lyle Foster": 50000, "Tete Yengi": 50000,
    "Lucas Bergvall": 50000, "John McGinn": 50000, "Wilson Isidor": 50000, "Nestory Irankunda": 50000,
    "Sergino Dest": 100000,
}
SCORER_META = {"source": "DraftKings Sportsbook (via RotoWire)", "as_of": "2026-06-08",
               "url": "https://www.rotowire.com/soccer/article/2026-world-cup-golden-boot-odds-full-player-list-mbappe-kane-haaland-108917"}

# --- Golden Ball / MVP: DraftKings, updated 2026-06-10 (~6h before fetch). Book's contender board (11). ---
MVP = {
    "Harry Kane": 800, "Lamine Yamal": 800, "Michael Olise": 900, "Kylian Mbappe": 900,
    "Lionel Messi": 1200, "Pedri": 1400, "Vinicius Junior": 1600, "Bruno Fernandes": 1800,
    "Declan Rice": 2000, "Raphinha": 2000, "Vitinha": 2000,
}
MVP_META = {"source": "DraftKings Sportsbook (via Sports Illustrated)", "as_of": "2026-06-10",
            "url": "https://www.si.com/soccer/2026-world-cup-golden-ball-winner-odds-predictions-yamal-messi"}

# --- Golden Glove / best GK: FanDuel, updated 2026-06-10. Book's contender board (9). ---
GK = {
    "Emiliano Martinez": 430, "Unai Simon": 500, "Alisson": 600, "Mike Maignan": 650,
    "Jordan Pickford": 750, "Ederson": 850, "David Raya": 850, "Diogo Costa": 1100, "Manuel Neuer": 1800,
}
GK_META = {"source": "FanDuel Sportsbook (via FOX Sports)", "as_of": "2026-06-10",
           "url": "https://www.foxsports.com/stories/soccer/2026-world-cup-golden-glove-odds-emiliano-martinez-favored-repeat"}

BOARDS = {"top_scorer": (SCORER, SCORER_META), "mvp": (MVP, MVP_META), "best_gk": (GK, GK_META)}


def _write(award, odds, meta):
    s_full = sum(american_to_prob(v) for v in odds.values())
    pt = {k: american_to_prob(v) / s_full for k, v in odds.items()}
    top6 = sorted(pt, key=lambda c: -pt[c])[:6]
    payload = {
        "award": award, "as_of": meta["as_of"], "fetched_utc": DATE + "T00:00:00Z",
        "note": (f"WC-2026 {award} futures, web-fetched {DATE} for the decision-grade lock run. American. "
                 f"Primary={meta['source']} (single-book de-vig basis, RB3; {len(odds)} names as the book "
                 f"presented them). Names ASCII-normalized to board keys. De-vig + top-6 at engine time "
                 f"(council.market_p_true). STALE by kickoff -> this IS the Jun-10 refresh (FM2). NOT A LOCK."),
        "overround_primary": round(s_full, 6),
        "primary": {"source": meta["source"], "url": meta["url"], "as_of": meta["as_of"],
                    "format": "american", "odds": odds},
        "crosscheck": {},
    }
    out = os.path.join(ROOT, "data", f"props_{award}_{DATE}.json")
    json.dump(payload, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"WROTE {os.path.basename(out)}  ({len(odds)} names, S_full={s_full:.4f})  "
          f"top6: " + ", ".join(f"{c}={pt[c]:.4f}" for c in top6))
    return pt


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for award, (odds, meta) in BOARDS.items():
        _write(award, odds, meta)
    print("\nASSISTER: K=4 gate FAIL (board flat: FanDuel co-favs Bruno/Olise +1100 ~8.3% raw, truncated "
          "10-name board -> honest P_true <=0.08; no under-owned candidate clears P_true>0.08 & leverage>1.5)."
          "\n  -> assister NOT written, NOT an engine lever (FM3). Chalk-manual = Bruno Fernandes (most-owned).")


if __name__ == "__main__":
    main()
