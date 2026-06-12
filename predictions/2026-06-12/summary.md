# Weekend MATCHDAY refresh — 2026-06-12 (Track B, DRY-RUN / HITL)

**Source:** The Odds API `soccer_fifa_world_cup`, eu, h2h+totals, american.
**Fetched:** 2026-06-12T17:10:35Z (single live call). **Quota:** 485 remaining / 15 used (2 cr spent).
**Snapshot (replayed for all 13):** `data/snapshots/md1_2026-06-12T17-10-37Z.json`.
**Engine:** M1→M2(de-vig)→x.5 guard→M3 Dixon-Coles(mu_eff)→M5 context(neutral)→M4 argmax E[pts] — **corrected optimizer (exact-score=3, commit 3778c4c).**
**STATUS: nothing submitted, nothing locked. Recommendation only — Sebas enters manually on pollaya.**

Two things this run did: (1) **closed today's 2 picks** on fresh odds (contract §5 refresh: fetch → replay
→ diff vs BASELINE → EDIT only on change), and (2) **added later MD1 fixtures** that the old
`WIN_HI=2026-06-14T06:00Z` window silently dropped. The played MEX-RSA (2-0) and KOR-CZE (2-1) are recorded
and no longer in the API event list.

> **🔴 F23 CORRECTION (Sebas audit, same day).** This run first added **7** fixtures and called the gap closed —
> WRONG. The denominator is the **FIFA calendar: MD1 = 24 matches**, so 2 played + 13 = 15 covered → **9 missing,
> not 7** (the "7 vs 4" scope question was derived from the same windowed `/events` probe under audit — circular).
> **#14 IRN-NZL (Tue Jun-16 01:00Z, deadline Mon-night 00:50Z) was the live risk → now ADDED below as BASELINE
> 1-0** (E=2.910, aligned, williamhill, snapshot `md1_2026-06-12T17-36-02Z.json`). The other 8 (MD1 #15–22,
> FRA-SEN→UZB-COL, Tue Jun-16 19:00 → Thu Jun-18 02:00) are the **next cadence batch**, not this weekend. Fix
> rules in CLAUDE.md §Data + lesson L25.

## A. TODAY's 2 picks — CLOSED (refreshed on Jun-12 odds)

| fixture | KO (UTC) | deadline | de-vig H/D/A (Jun-12) | **EV pick** | E[pts] | modal | BASELINE | verdict |
|---|---|---|---|---|---|---|---|---|
| Canada–Bosnia & Herz. | 06-12 19:00 | **18:50 UTC today** | .529/.273/.198 | **1-0** | 2.953 | 1-0 | 1-0 | **STANDS — no change** |
| USA–Paraguay | 06-13 01:00 | 00:50 UTC Sat | .455/.287/.259 | **1-0** | 2.678 | 1-1 | 1-0 | **STANDS — no change** |

- **CAN-BIH:** aligned (EV==modal), guard clean. Fresh de-vig firmed Canada slightly (.525→.529); pick stable.
- **USA-PAR (the only Jun-11 flip candidate):** USA softened .476→.455 but the EV argmax **stays 1-0**; the
  EV-vs-modal gap (1-0 vs modal 1-1) **persists**. The flip did NOT trigger. Pick stands.
- Per "EDIT only on change," neither `decisions.csv` row was mutated (picks unchanged; Jun-11 forecast cols stand).

## B. NEW MD1 fixtures — BASELINE added (refresh before each deadline)

7 added in the first pass + **IRN-NZL added in the F23 correction** (last row). Total tracked = 16 rows.

| fixture | KO (UTC) | deadline | de-vig H/D/A | **EV pick** | E[pts] | modal | line | book | flip-watch |
|---|---|---|---|---|---|---|---|---|---|
| Germany–Curaçao | 06-14 17:00 | 16:50 UTC Sun | .918/.061/.022 | **3-0** | 4.072 | 3-0 | 4.5 | coolbet | totals-sensitive² |
| Netherlands–Japan | 06-14 20:00 | 19:50 UTC Sun | .484/.264/.252 | **1-0** | 2.634 | 1-1 | 2.5 | pinnacle | **EV≠modal** |
| Ivory Coast–Ecuador | 06-14 23:00 | 22:50 UTC Sun | .280/.319/.402 | **0-1** | 2.598 | 1-1 | 2.5 | williamhill | **EV≠modal (priority³)** |
| Sweden–Tunisia | 06-15 02:00 | 01:50 UTC Mon | .512/.277/.211 | **1-0** | 2.891 | 1-0 | 2.5 | unibet_nl | — (aligned) |
| Spain–Cape Verde | 06-15 16:00 | 15:50 UTC Mon | .885/.082/.034 | **3-0** | 4.087 | 3-0 | 3.5 | pinnacle | totals-sensitive² |
| Belgium–Egypt | 06-15 19:00 | 18:50 UTC Mon | .601/.236/.164 | **1-0** | 3.123 | 1-0 | 2.5 | pinnacle | — (aligned) |
| Saudi Arabia–Uruguay | 06-15 22:00 | 21:50 UTC Mon | .118/.214/.669 | **0-1** | 3.412 | 0-1 | 2.5 | pinnacle | — (aligned) |
| **Iran–New Zealand (F23)** | 06-16 01:00 | 00:50 UTC Tue | .518/.266/.215 | **1-0** | 2.910 | 1-0 | 2.5 | williamhill | — (aligned) |

These are **BASELINE** (not entered). Refresh each on its own day before the 10-min deadline; EDIT only on change.
² **F26:** GER-CUW / ESP-CPV 3-0 sit on a high totals line (4.5 / 3.5); a totals move on the Sun/Mon refresh can
legitimately flip the argmax 3-0↔2-0 — that is **odds-driven, not a bug** (p_pick is above the R6 floor, guards clean).
³ **F25:** asymmetric staleness on overnight refreshes; if a cheap late re-check is available, prioritize the
flip-watch fixtures — **CIV-ECU first**.

## Guards (asserted on all 14 = 13 + IRN-NZL)
- **M5 context = `['neutral']` ×14** — all group-stage matches, H4 dormant. PASS.
- **x.5 totals line ×14** — every fixture priced on a half-line (4.5 / 3.5 / 2.5); no `LineGuardStop`, no 2.5 coercion. PASS.
- **Book coverage (H3) = intra-book RB3-clean ×14** — h2h_book == totals_book on every fixture; no cross-book, no totals-blind fallback. PASS.
- **Inversion guard (L17): clean ×14** — matrix favorite == market favorite on every fixture.
- **Determinism:** the per-match pipeline is closed-form (no RNG); same snapshot → byte-identical replay.

## EV-vs-modal divergence — the only fresh-odds flip candidates (F13 watch)
Three fixtures whose EV pick diverges from the model modal (per-match ownership is HIDDEN → not leverage-contrarian,
just where fresh odds could move the argmax): **USA-PAR** (1-0 vs 1-1), **NED-JPN** (1-0 vs 1-1), **CIV-ECU** (0-1 vs 1-1).
Watch these on their refresh. The other 12 are aligned/robust.

## Refresh schedule (10-min pre-KO deadlines)
- **Fri (today) — DONE:** CAN-BIH (18:50), USA-PAR (00:50 Sat). Both 1-0, stand.
- **Sat ~18:00 UTC** → QAT-SUI (18:50, 0-2), BRA-MAR (21:50, 1-0), HAI-SCO (00:50 Sun, 0-1), AUS-TUR (03:50 Sun, 0-1 — *check Türkiye/Turkey spelling in the pollaya dropdown*).
- **Sun ~15:00 UTC** → GER-CUW (16:50, 3-0), NED-JPN (19:50, 1-0¹), CIV-ECU (22:50, 0-1¹), SWE-TUN (01:50 Mon, 1-0).
- **Mon ~14:00 UTC** → ESP-CPV (15:50, 3-0), BEL-EGY (18:50, 1-0), KSA-URU (21:50, 0-1), **IRN-NZL (00:50 Tue, 1-0 — F23; widen `--win-hi ≥ 2026-06-16T02:00Z`)**.
- **Tue ~14:00 UTC (next batch, NOT this weekend)** → MD1 #15–22: FRA-SEN, IRQ-NOR, ARG-ALG, AUT-JOR, POR-COD, ENG-CRO, GHA-PAN, UZB-COL (`--win-hi 2026-06-18T03:00Z --expect 22`).

¹ flip-watch (EV≠modal).

**Every refresh (CLAUDE.md §Data, post-F23):** probe `/events` next ~72h and diff ids vs `decisions.csv` before fetching; set `--expect` from the FIFA calendar (MD1=24), not a same-endpoint probe.

Record results as matches finish: `python -m src.decision_score record <fixture_id> <H-A>` then `pwsh predictions/review.ps1 -Mark`.
