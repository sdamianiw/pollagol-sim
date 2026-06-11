# objective.md — declared objective + hour budget (DoD-1; HITL decision 2026-06-02)

> Machine-readable invariant that governs how every remaining build-hour is prioritized. Decided by
> **Sebas** (Code presents + records, never chooses). Read by `pool/objective.py: read_objective()`.

OBJECTIVE: HYBRID
HOUR_CAP_HOURS: 6
DECIDED_UTC: 2026-06-02

## Rationale (2026-06-02)
**HYBRID** = build enough to compete decently AND to learn (modeling, EV, calibration, sparring). The
money-EV ranking does NOT solely govern: build a defensible 5-pick + scorelines + insight, without
over-optimizing one ~10-pt lever (champion) inside a ~300–500-pt competition.

**Honest money framing (why a bounded 6h cap, not unbounded):** N≈22 final, entry $30.000 CLP → pot ≈
$660.000 CLP; 1st = 60% ≈ $396.000 CLP (~US$415). Random baseline P(1st) ≈ 1/22 ≈ 4.5%. In a mostly-chalk
pool the full apparatus realistically lifts P(1st) by ≈ **+1.5–3.5 pp** (most of the outcome is variance —
one upset round sinks you). So the money-EV of the *entire* build ≈ **$6.000–12.000 CLP (~US$6–13)** —
dozens of build-hours pay single-digit USD/hour if money is the only goal. The apparatus mostly pays in
**learning/sparring** value → HYBRID with a bounded cap.

## Enforcement — STOP by HITL convention (NOT auto-enforced)
`HOUR_CAP_HOURS` is a **soft STOP by convention**: when ~6 h of remaining-build effort is reached, Code
STOPS and asks for a new GO before continuing. Passing the cap requires explicit Sebas approval. This
module does not track time automatically — it records the governing number so every session sees it.
Independently, **each DoD needs its own GO**.

## Priority consequence (HYBRID, cap 6 h)
DoD-1 (this) → DoD-2 (Track-B odds source) → **DoD-4 (engine hygiene; HARD-DEP before DoD-3)** → DoD-3
(other 4 locked picks; blocked on Jun-2 squads + a player-prop source). Champion stays **OPEN**; nothing
to lock. See the approved plan + `tasks/HANDOFF.md`.
