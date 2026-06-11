# pool/poll_champion.md — champion-ownership poll (Track A, §7b leverage denominator)

**Purpose.** Estimate `ownership_field` for the CHAMPION locked pick by polling the ~25 entrants. This is
the ONLY path to a *measured* leverage denominator: pollaya is assumed to expose no picks
(`PICKS_VISIBLE=False`, `[PENDING VERIFICATION]`), so `observed` is impossible. Feeds
`pool/leverage.py → compute(..., ownership_source="polled", ownership_override=<tally>)` and A2's R9 sweep.

**Scope.** Champion ONLY. The other 4 locked picks (top scorer / assister / MVP / GK) need the final
26-man squads (FIFA publishes **2026-06-02**) → poll those after Jun 2.

---

## The message (Spanish, casual — send to the pool group chat)

> Asunto: encuesta relámpago pa' la polla ⚽
>
> Oye [grupo], pregunta tonta pa' calentar motores del Mundial:
> 👉 ¿Quién creen que se lo gana? Tírenme UN candidato no más.
>
> (Es por hueveo / pa' picarnos, no hay premio por responder 😄)

**Why worded this way (design constraints baked in):**
- **Champion-only**, one tap to answer → maximizes response rate.
- **Casual / social** ("por hueveo"), NOT "para mi modelo" → avoids signaling that picks are being
  analyzed, which would distort answers.
- **Prediction-framed** ("¿quién creen que GANA?") NOT strategy-revealing ("¿qué vas a MARCAR?") → people
  share a belief, not their actual locked pick.

---

## ⚠ This is a NOISY PROXY — never finalize on it alone (§7d / R9)

A *prediction* ("who will win") is a biased proxy for *pick ownership* ("who you'll lock as champion"):
- **Chalk bias:** prediction answers cluster on the consensus favorite (Spain/France); some of those same
  people will actually LOCK a darkhorse for leverage. So the poll OVERSTATES favorite ownership.
- **Blind to the strategic / wildcard players** — exactly the ones who lock contrarian champions and who
  drive leverage. They may not reveal, or may answer chalk while picking contrarian.
- **Non-response bias:** ownership is estimated over RESPONDENTS only (likely < N=25). Non-responders'
  picks are unknown.

→ Treat the tally as an **estimate with wide error bars**. A2 keeps the **wide R9 sweep (Brazil 4%→25%)**,
NOT a point estimate. Triangulate with prior-year behaviour and public group banter. Consider a discreet,
pick-framed read from the 1–2 known wildcard players.

---

## Tally → ownership vector (mapping spec)

After collecting answers, record provenance (**date, N_respondents, raw tally**), then:
- `ownership[team] = votes[team] / N_respondents`
- teams with **0 votes → ownership 0** (do NOT fabricate a tail; unpicked = 0)
- the vector sums to 1 over respondents.

Feed it as the override:

```python
from pool.leverage import compute
tally = {"Spain": 9, "France": 6, "Brazil": 5, "Argentina": 4, "England": 1}   # example, N=25
N = sum(tally.values())
own = {k: v / N for k, v in tally.items()}
p_true, ownership, overround, rows, _ = compute(
    "data/outrights.json", ownership_source="polled", ownership_override=own)
# e.g. Brazil polled own = 20% -> leverage 0.098/0.20 = 0.49 -> NOT a contrarian candidate (chalk).
```

---

## Cadence + noise handling

1. **Poll now** for a first champion read.
2. **Re-poll ~Jun 8–10** — ownership intent drifts on GENUINELY NEW catalysts: fresh injuries/suspensions,
   a recovery setback, late form, eventually the knockout draw. **Already-absorbed news does NOT count.**
   E.g. Lamine Yamal's hamstring injury (2026-04-23, hamstring/biceps femoris; out for Barça's season but
   expected back for Spain's opener) is ALREADY reflected in the 2026-05-29 odds (Spain still +450
   favorite) → already in `P_true`; do NOT re-count it as a pending mover. (Sources: Sky Sports, CBS,
   2026-04-23.)
3. **Treat as noisy** → A2 sweeps Brazil 4%→25% rather than trusting a single snapshot.
4. **Triangulate** — prior-year pick behaviour, public group answers, the known wildcard players.

After **2026-06-02** squads publish: extend the poll to top scorer / assister / MVP / GK.
