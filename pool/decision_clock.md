# decision_clock.md — when to bind each variable (champion lock)

> **Purpose.** Separate what is built NOW and frozen (INVARIANT) from what is re-read LATE and bound at
> the snapshot (TIME-DEPENDENT). The engine (`pool/leverage.py` screen + `pool/pool_montecarlo.py` A2
> E[prize]) is invariant; the *inputs* late-bind. This is the schedule that turns "don't lock early" into
> a concrete, auditable procedure. Source paradigm: master plan §"PARADIGM SHIFT", confirmed 2026-06-02.

> 🛑 **HARD GATE.** This file schedules a RECOMMENDATION; it never authorizes a LOCK. Champion is OPEN
> (Brasil in pollaya = PLACEHOLDER). `ownership_source=prior` is `is_gated`. HITL: Sebas locks.

## INVARIANT vs TIME-DEPENDENT

| Variable | Class | Build / bind | Note |
|---|---|---|---|
| Scoring rubric / objective (E[points], E[prize]) | **INVARIANT** | built, unit-tested (`memory/rules.md`) | re-confirmed 2026-06-02; no optimizer change |
| Engine mechanics (de-vig, CRN Monte Carlo, argmax E[prize]) | **INVARIANT** | built (A1 + A2) | logic frozen; only inputs change |
| P_true **mechanism** (de-vig outright odds → P_true) | **INVARIANT** | built (`leverage.compute`) | how we map odds→prob is fixed |
| P_true **value** (the actual numbers) | **TIME-DEPENDENT** | **re-fetch fresh odds at the Jun-10 evening snapshot** | cached `data/outrights.json` is May-29 → **PB1/FM2** |
| N (total entrants) | **TIME-DEPENDENT** (top-line driver) | re-read at snapshot | 12 today → ~20–25 final → **PB2** |
| Observed ownership (locked opponents) | **TIME-DEPENDENT** | re-read at snapshot, self-excluded | low-n today = noise → **PB5** |
| Pending-opponent prior (sim input only) | **TIME-DEPENDENT** | re-read at snapshot | never used to choose my own pick |
| Decision-rule **structure** (argmax E[prize]) | **INVARIANT** | built | — |
| Decision-rule **N-calibration** (chalk↔contrarian regime) | **TIME-DEPENDENT** | bind at final N | don't freeze "N=12 chalk" → **PB3** |

## Pushback verdict — PB1–PB5 (baked into the table above)

- **PB1 — P_true value is TIME-DEPENDENT (FM2: stale-value-as-current).** Mechanism is built now; the
  *numbers* must come from FRESH odds at the Jun-10 evening snapshot. Never LOCK on the cached May-29 file.
- **PB2 — N is the top-line TIME-DEPENDENT driver (12 → ~20–25).** It scales every ownership denominator
  AND shifts the chalk/contrarian regime (§7c). Re-read at the snapshot; re-run the regime at the final N.
- **PB3 — decision-rule: structure INVARIANT / N-calibration TIME-DEPENDENT.** The argmax-E[prize] rule is
  fixed; its chalk-vs-contrarian tuning depends on final N and final ownership. Don't freeze today's regime.
- **PB4 — last-mover edge is HIGH value (softened; lock Jun-10 PM).** In a low-sophistication 12–25 pool
  most entrants lock early and visibly, so waiting captures the non-strategic majority's revealed ownership;
  residual uncertainty is only the 1–2 sharps who may also wait. **Softening (decision 2026-06-06):** we
  lock the EVENING of Jun-10 — one safe day before the Jun-11 first match — deliberately trading the last
  ~day of ownership-firming for execution safety. The hard backstop is tournament start (first match Jun-11),
  never raced; Jun-12 is VOID (see `tasks/lessons.md`).
- **PB5 — observed ownership at low n is NOISE** (n=2, n=1 after self-excluding Sebas → `{Uruguay:1.0}`).
  The Jun-9 rehearsal validates the PIPELINE, not a number; the number is only trusted near final N.

## Optimization rule
Late-bind the TIME-DEPENDENT inputs (fresh P_true, final N, final observed ownership) onto the prebuilt
INVARIANT engine, then take `argmax E[prize]` from `pool/pool_montecarlo.py`. The champion is **one ~10-pt
lever inside a ~300–500-pt competition** — size the effort accordingly; do not over-optimize one lever.
The last-mover edge is real but bounded; the Jun-10 PM lock wins the tie against squeezing the final sliver before the Jun-11 first match.

## Lock schedule
| When | Action | Binds |
|---|---|---|
| now → Jun 2 | build INVARIANT engine + observed ingestion (DONE: A1, ingest, A2) | invariants |
| Jun 2 | FIFA squads public → build P_true sources for the other 4 picks | (other picks) |
| **Jun 9** | **REHEARSAL** — full pipeline dry-run on then-current N/ownership (validates PIPELINE, PB5) | nothing |
| **Jun 10 (evening)** | **re-fetch FRESH odds → fresh P_true; re-read final N + observed ownership; run A2; RECOMMEND → HITL: Sebas reviews & LOCKS** | all TIME-DEPENDENT + the LOCK (human) |
| **Jun 11 (~13:00 CST / 21:00 CEST)** | **tournament start: first match = HARD constraint — NEVER race kickoff**; the Jun-10 PM lock exists so we never approach it | — |
| ~~Jun 12 02:00~~ | **VOID** — not the deadline (mis-recorded; binding constraint is tournament start Jun-11). See `tasks/lessons.md` | — |

*Kickoff time 13:00 CST = 21:00 CEST = 19:00 UTC — VERIFIED 2026-06-06 (FIFA + The Odds API commence_time `2026-06-11T19:00:00Z`).*

**Invariant of invariants:** no pick is LOCKED while `ownership_source = prior`; finalize only on measured
(`observed`/`polled`) ownership at near-final N, by Sebas. See `memory/rules.md`, `tasks/HANDOFF.md`.
