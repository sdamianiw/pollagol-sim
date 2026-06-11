# lessons.md — corrections → rules (self-improvement loop)

Format: **Pattern** (what went wrong / was caught) → **Rule** (how to prevent recurrence).

## L1 — Quota units (caught 2026-05-30)
**Pattern:** Risk of treating the API-Football free limit as per-hour when it is **100 requests / DAY**;
underestimating consumption hides a crunch-time outage (R4).
**Rule:** State rate limits in explicit units. The Step-0 probe MUST measure and print
`requests_consumed` for a full cycle and project a 5-fixture peak day vs 100/day; if > 100, cache +
web-fallback is **mandatory, not optional**.

## L2 — A baseline drawn from the model under test is not a baseline (caught 2026-05-30)
**Pattern:** Defining B2 = the DC model's own modal score makes "EV selector beats B2" a trivial PASS —
the EV selector optimizes the very metric the modal score ignores, on the same distribution. Circular
self-grading is a false positive (FM1).
**Rule:** Backtest baselines must be **external/independent** of the model under test. Real gate =
**beat B1 (always 1-0 favorite) + calibration (Brier/log-loss)**. Use B2 only if sourced from an
**external** correct-score market, with its source documented. Never grade a model against itself.

## L3 — A "primary" data source unverified end-to-end is a liability (caught 2026-05-30)
**Pattern:** The contract's default primary source (API-Football free tier) was assumed to serve WC-2026.
The Step-0 probe proved it CANNOT: free plans are restricted to seasons 2022–2024, and World-Cup odds are
not covered on free at all. Building Track B on it would have failed at crunch time.
**Rule:** Probe the exact endpoint + season + plan on the REAL key BEFORE committing a data source. Treat
vendor marketing ("all endpoints on free") as unconfirmed until a live call returns non-empty for YOUR
plan and season. Keep the web-fetch fallback first-class, not an afterthought.

## L4 — Per-team ownership is not derivable from P_true (caught 2026-05-30)
**Pattern:** A1's contrarian screen modelled tail ownership as `own ∝ P_true^γ`, so leverage =
`K·P_true^(1−γ)` — the within-tail ranking AND the candidate set were a pure function of the free knob γ
(Germany/Portugal order inverts across γ=1; Portugal drops out of the candidate set at γ=3). A knob that
GENERATES the very candidates it should only stress-test is an artifact (FM1/FM2). It also self-
contradicted: γ>1 ("famous teams over-picked") yet flagged Germany (4× champion) as under-owned.
**Rule:** Per-team ownership is NOT a function of P_true. Under `ownership_source=prior`, emit leverage for
the NAMED set only; the tail = UNDEFINED until polled/observed. A sensitivity knob must never select
candidates. Never mark a module done while its load-bearing input (here: ownership) is unverified (Gate 9/FM4).

## L5 — An empirically-verified assumption can be FALSIFIED by new platform evidence (caught 2026-06-02)
**Pattern:** `PICKS_VISIBLE` was treated as `False` (a screened, evidence-backed assumption that pollaya
exposed no participant picks). New pollaya screenshots (2026-05-30, confirmed 2026-06-02) FALSIFIED it:
premiation/locked picks ARE visible → `observed` ownership is real. The encoding test T6 had asserted the
OLD contract (observed → `NotImplementedError`); it had to be rewritten to the NEW contract (observed runs
with an override; without → `ValueError`), and T7 (`is_gated`) added.
**Rule:** Editing a test because **reality changed**, with the new evidence cited (source + UTC + URL), is
**reconciliation — legitimate**. Editing a test to **dodge a real failure** is FM1 test-gaming — **banned**.
The distinguishing question: did the spec/world change (reconcile, and log it here), or did the code fail
the unchanged spec (fix the code, never the test)? FM-taxonomy: **FM1** = false-positive (grade a model
against itself / loosen a test to pass); **FM2** = stale-value-as-current (lock on a cached number when the
live value moved — e.g. re-fetch fresh odds at the Jun-10 snapshot, never the May-29 cache).

## L6 — Allocate build effort by point-value, not by salience (caught 2026-06-03)
**Pattern:** The 5 locked picks are salient (visible, "decisive", sequenced FIRST) but worth ~50 pts total
(champion ~10). The per-match scorelines are ~88% of the competition's points (~350 of ~400). Continuing to
pour hours into the champion lever — a ~10-pt lever inside a ~300–500-pt competition — while the per-match
engine stays unbuilt is misallocation: optimizing the visible small lever over the dominant one.
**Rule:** Allocate effort by **point-value**. Track-B (per-match EV engine) ≈ 88% of points → it is the
priority; do not divert to DoD-3 (other-4-picks) or over-tune the champion. Re-derive "what matters" from the
rubric's point totals, not from what feels decisive. (This is why the 2026-06-03 GO builds Track-B ahead of DoD-3.)

## L7 — A catalog/marketing claim ≠ live availability for YOUR (sport × market × history) (caught 2026-06-03)
**Pattern:** A source's catalog/marketing page may advertise a market ("historical odds", "all sports") that
is not actually served for the exact (sport × market × history-window) on YOUR plan. Generalizes L3 (API-Football's
"all endpoints on free") to ANY source's claim — e.g. OddsPapi advertising historical soccer odds, unverified
for international/major-tournament fixtures. Treating the claim as fact would gate the M7 success-proof on vapor.
**Rule:** A catalog/marketing claim is UNCONFIRMED until a live call returns the exact (sport × market ×
history-window) you need for your plan. Do a web pre-filter (cite source+date), THEN a 1-call live probe with a
captured HTTP status + sample row, BEFORE committing the source. Never let a marketing claim gate a downstream build.

## L8 — NO-EDGE is a valid measured outcome, not a failure to engineer around (caught 2026-06-03)
**Pattern:** The success-proof (M7 backtest, EV selector vs B1) has three honest verdicts: PASS, NO-EDGE, FAIL.
The temptation is to treat anything but PASS as failure and post-hoc tune the model until it "beats B1" — which
games the proxy (the model is then fit to the test; FM1-adjacent / Stuart-Russell: optimizing the measure until
it stops measuring).
**Rule:** Success is the **PROCESS tier** — a clean, reproducible engine that EITHER beats B1 with calibration
OR honestly reports "no measured edge vs B1". **Freeze the model spec before reading M7**; report the number
as-is (n + CI); never tune to manufacture a win. A measured NO-EDGE is a legitimate success of the process, not
a defect to engineer away.

## L9 — A methodology/plumbing verdict is NOT the target-domain success-proof (caught 2026-06-03)
**Pattern:** In the M7 source comparison I labeled the out-of-domain (club-league) backtest as delivering a
"success-proof verdict before picks". That collapses two distinct claims: **(A)** a methodology/implementation
gate — does the de-vig→DC→argmax pipeline run correctly and beat B1 *in-distribution* (high-n, $0, pre-picks) —
and **(B)** the TIER-1 success-proof — does the engine beat B1 *at the World Cup*. An OOD backtest validates (A)
only. The steelman "if it can't win on 10k club matches it won't on 104 WC" is invalid in BOTH directions: WC
has §5 effects (dead-rubber, rotation, motivation asymmetry) absent in league play, so a club NO-EDGE does not
imply a WC NO-EDGE, nor does a club edge imply a WC edge. (Caught by Sebas as a table↔caveat inconsistency —
the prose caveat was right; the comparison table overclaimed. FM1-lite: a tidy table manufacturing a stronger
claim than the evidence supports.)
**Rule:** Label every gate by exactly what it proves and in which distribution. A backtest on a different
domain (or a forward-test) is a methodology-validation gate, never the target-domain success-proof. Keep the
in-distribution implementation check and the out-of-distribution / forward edge-proof as SEPARATE,
separately-labeled verdicts; never let a comparison table collapse them.

## L10 — Necessary ≠ sufficient: harden the gate, segment the metric, smoke the hard case (caught 2026-06-03)
**Pattern:** Three related ways a green verdict can still measure the wrong thing (caught by Sebas before P3):
**(A)** the M4 optimizer gate had only the 4 locked unit-test cases — a buggy/overfit `points()` could pass
exactly those and fail elsewhere (necessary, not sufficient). **(B)** the M7 backtest was specced as an
AGGREGATE points/match vs B1 — but the engine provably EQUALS B1 on clear favorites (both pick fav-1-0,
gap=0), so the edge (if any) lives only in high-total / draw-or-away-likely matches; averaging ~70 gap-0
fixtures with a few decisive ones dilutes a real edge to NO-EDGE (Goodhart). **(C)** the e2e smoke covered
only the easy case (clear favorite → 1-0), leaving "is it just a 1-0 machine?" unobserved.
**Rule:** A gate of K hand-picked cases is necessary, not sufficient — add adversarial/edge cases beyond the
spec's own examples (did so: 6 extra `points()` cases + 2 divergence guards). Report metrics SEGMENTED by the
regime where behaviour differs (clear-fav · close · high-total · draw-likely), each with its own CI, never
aggregate-only. Always smoke the HARD case — where the system SHOULD diverge from the baseline — not just the
easy one. Related anti-FM1: lock a spec choice (e.g. opening vs closing odds) BEFORE reading the metric it
feeds; changing it afterward to improve the number is spec-after-the-fact.

## L11 — A green pipeline can silently DISCARD its load-bearing signal (caught 2026-06-03, in P3)
**Pattern:** Every M1–M7 test was GREEN and the e2e ran, but the M7 backtest was about to report NO-EDGE for
a MECHANICAL reason: M3 `fit_lambdas` anchors μ on the totals LINE, and football-data pins that line at 2.5,
so μ≈2.51 for EVERY fixture (4 distinct μ over 380 EPL matches; the engine never picked 2-1). The total-goals
SIGNAL lives in the over/under PRICE (`B365>2.5/<2.5`), which the model discarded — so the "high-total"
segment was a non-measurement. The unit tests passed because none of them asserted that μ TRACKS the totals
input across fixtures; the symptom surfaced only via the divergence smoke test (`test_high_total_diverges`
went RED) + a per-fixture diagnostic (count distinct μ; corr(μ, p_over)). Twin lesson on classification:
the FIX (invert p_over→μ_eff, feed the frozen `fit_lambdas`) was registered + FROZEN in rules.md (M7 design
v) BEFORE the number was read → a PRE-RESULT correctness fix (signal recovery), NOT post-hoc tuning (L8/FM1).
**Rule:** For any model, add a test that the OUTPUT tracks each load-bearing INPUT across the data range
(here: distinct-μ count + corr(μ, p_over) ≳ 0.9 + μ spans [2.4,4.0]) — not just that a single fixture is
sane. When a data source degrades an input (single pinned line vs a price), RECOVER the signal in the
backtest layer and HARDEN it (range + monotonicity + round-trip + clamp-not-biting) BEFORE reading the
metric; freeze the recovery in the spec so it cannot be mistaken for tuning. A pipeline being GREEN proves
plumbing, not that the signal flows. And: a latent input-handling bug found in a backtest is usually latent
in the LIVE path too — register the live fix (here: port μ_eff into `src/` M2/M3, P4) so Gate-A ≠ Gate-B
doesn't hide it (L9).

## L12 — The contrarian edge is σ- and lever-count-fragile; K=1 intuition does NOT transfer to K>1 (caught 2026-06-05, P2; demonstrated)
**Pattern:** The A2 (K=1) result "under-owned Dark beats chalk Fav by ~+0.010" was assumed to hold in the
joint engine, so T-flip-one AND the podium selftest expected a lone flip to win even with a LIVE efficient
second lever. MEASURED (σ=6, N_opp=11, P_true[Dark]=0.20, n=60000): with ONE live efficient lever the flip
gain is NEGATIVE across the WHOLE under-ownership range — −0.0015 at 10x leverage down to only −0.0004 at 100x
— i.e. extreme under-ownership does NOT rescue it (the edge is capped because the contrarian pays only the
~20% it wins, while every extra live 10-pt lever adds competing bonus mass). My initial "weak-vs-strong"
hypothesis was WRONG: under-ownership strength is not the axis. The governing params are {P_true,
ownership→leverage, σ, N_opp, #live levers}. And the QUALITATIVE verdict is σ-dependent: even ISOLATED (no-op
lever) the 10x flip is 'flip' at σ≤6 but 'chalk' at σ≥8 (tips ~σ7–8). This is correct §7b behavior surfacing
numerically, not a bug.
**Rule:** Reason about chalk-vs-contrarian on the JOINT total; E[prize] is non-additive (PODIUM-1). The
chalk-vs-contrarian VERDICT (not just magnitudes) is σ-dependent and NOT decision-grade until Track-B P4
σ-calibration → re-run the engine on the calibrated σ before any lock (PODIUM-3). To UNIT-TEST a single-lever
flip mechanism, ISOLATE it with a no-op lever (the only regime where a flip is decisive at the placeholder
σ=6); to test "don't over-gamble," use multiple LIVE levers and assert the RULE, not a fixed outcome. Never
port a K=1 contrarian magnitude into a K>1 assertion.

## L13 — A robustness check under the EFFICIENT prior is tautological; σ-calibration does NOT settle the verdict (caught 2026-06-06, P4b; Sebas refinement)
**Pattern:** P4b calibrated σ from M7 variance: σ_lower=13.8 (CI [13.5,14.0]), σ_upper=24.9 (CI [24.5,25.4]);
the widest bracket [13.5, 25.4] clears the stylized isolated-lever flip (~σ7–8) → a naïve read = "robust
chalk, STOP". The planned escalation would have CONFIRMED this by running the real K=4 engine at the bracket
endpoints under the EFFICIENT-field ownership — but efficient ownership ⇒ §7b leverage≈1 ⇒ chalk is
quasi-tautological at ANY σ, so "robust chalk" would have CONFLATED chalk-by-prior with chalk-by-high-σ
(over-reading the conclusion as more decisive than it is). Running the real engine under BOTH (a) efficient
AND (b) targeted-starve (the high-leverage stress) revealed the truth: efficient→chalk at σ_lo AND σ_hi, but
**starve→contrarian_2_levers at BOTH σ_lo=13.5 AND σ_hi=25.4** — contrarians persist far above the
isolated-lever flip. So σ-calibration does NOT settle chalk-vs-contrarian; the verdict is
**SIGMA_DEPENDENT_UNDER_LEVERAGE** and hinges on the ownership LEVERAGE regime, which only OBSERVED Jun-10
ownership reveals. The stylized ~σ7–8 flip (isolated lever) is a DIFFERENT object from the K=4 verdict (L12).
**Rule:** Never read a robustness/sign-stability verdict off a scenario where the answer is structurally
forced (efficient ownership → leverage≈1 → chalk regardless of the variable under test). Test sign-stability
under the regime where the lever actually BITES (here: real/stressed leverage), and require the robust
verdict to hold across BOTH the forced and the biting scenario — else the verdict is regime-dependent and
must DEFER to the measured input (observed ownership), not be declared from a dry-run. Twin caveat (σ as
proxy, "L9-style"): σ_cal is from EU club-league per-match variance — a PROXY for WC-2026 (neutral venue,
knockout, scoring-rate shifts), not a WC measurement; σ_upper (iid, all 104) is a structural ceiling, σ_lower
(divergent-only, with f_div AND d as declared proxies) the practical floor. Inject σ_cal as a RUNTIME value;
keep A2 BASE_SIGMA=6.0 FROZEN (the byte-exact anchor). RE-RUN podium+champion on σ_cal + observed ownership
at Jun-10 before any lock.

## L14 — A previously-sourced operating constant can be VOID; reconcile the convention repo-wide, don't leave a split (caught 2026-06-06, Sebas)
**Pattern:** The locked-pick "deadline 2026-06-12 02:00" was recorded across `CLAUDE.md §7d`, `memory/rules.md`,
`memory/predictions.md`, HANDOFF, todo, `decision_clock.md` and two print banners — but the BINDING constraint
is tournament start (first match Jun-11, ~13:00 CST / 21:00 CEST / 19:00 UTC); Jun-12 02:00 is VOID
(mis-recorded / not the operative deadline). The repo was ALSO internally split (some docs said "Jun-11 late
lock", others "Jun-10 LATE"). **Decision (Sebas 2026-06-06):** canonical = LOCK **Jun-10 EVENING** (one safe
day before kickoff), hard backstop = first match Jun-11 (never raced). This consciously trades ~a day of
last-mover ownership-firming for execution safety (PB4). **Rule:** when an operating constant changes or is
falsified, sweep EVERY occurrence (code banners + all docs) in ONE pass and leave a breadcrumb — a
half-applied reconcile (banner fixed but docs stale, or two camps coexisting) is worse than the original
because it reads as "decided" while still ambiguous. Cross-check the new datum at its source before the
irreversible step (here: the Jun-11 kickoff time was VERIFIED 2026-06-06 — FIFA + The Odds API commence_time `2026-06-11T19:00:00Z`).

## L15 — A consumer that re-normalizes silently turns "blank mass" into inflated named shares; carry it on a non-matching sentinel (caught 2026-06-06, observed-ownership test run)
**Pattern:** The observed-ownership model (memory/rules.md) puts each named candidate's share over the FULL
N_opp with a Laplace floor, leaving the undecided/blank opponents as a RESIDUAL (`1 − Σ named < 1`). But
both `expected_prizes_joint` and `_aggregate_ownership` (`pool/podium_montecarlo.py`) re-normalize every
ownership dict (`probs = probs / probs.sum()`) before sampling/leverage. Feeding a sub-normalized dict would
have SILENTLY re-scaled the named shares up — collapsing the blank mass onto the candidates, deflating every
leverage, and biasing the verdict toward chalk — with no error raised. **Rule:** before handing an ownership
(or any probability) vector to a component that normalizes internally, make it sum to 1 YOURSELF, modelling
the missing mass EXPLICITLY — here on the engine's `_SENTINEL` ("__unknown__"), which never equals a drawn
winner, so blank opponents contribute zero collision probability (the correct semantics) instead of being
redistributed onto real candidates. Keep the sentinel constant single-sourced (ingest `SENTINEL` == engine
`_SENTINEL`, asserted in a test) so the convention can't split (L14).
**Corollary (blank-resolution is a free parameter at small-n; FIX-1/Step-5b):** how you resolve blanks IS a
modelling choice — (A) score 0 (sentinel) vs (B) sample from P_true. At n=4–7 deciders/19 the two disagree:
Model A flagged a 1-lever MVP contrarian (Harry Kane) that Model B erased to all-chalk. When the chalk-vs-
contrarian argmax FLIPS between A and B, the lever is `INDETERMINATE-preliminary` and DEFERS to the measured
input (Jun-10 final ownership) — never reported as a contrarian pick (same defer-to-measurement discipline as
L13, applied to the blank model rather than σ).

## L16 — spec ≠ as-built (logged v9 handoff; backfilled to lessons.md 2026-06-09)
**Pattern:** MASTER §6/§11 specify `run_matchday.py <date>` (multi-fixture); M8 was actually built
single-fixture (`--snapshot|--live --fixture`, one match per call). The auditor asserted "run = 1 day" from the
spec without reading the code → corrected.
**Rule:** any claim about a BUILT module's interface must read the code, not the contract that commissioned it.

## L17 — Favorite-inversion in near-even / high-draw fixtures: a 1-constraint DC fit under-produces draws and flips the matrix favorite (caught 2026-06-09, Jun-9 dry-run audit)
**Pattern:** The 1-constraint Dixon-Coles fit (`fit_lambdas`/`_solve_s`: supremacy `s ← market P_home`, μ pinned
by the totals price, ρ fixed at −0.05) SUB-PRODUCES draws (~2–3pp deficit; independently measured −0.024 to
−0.033). The missing draw mass leaks onto the AWAY side → the matrix-implied favorite INVERTS vs the market →
M4 EV-argmax then recommends a scoreline that CONTRADICTS the market favorite (violates the §2.2 outcome
backbone). MEASURED on KOR-CZE (Jun-9 cache replay): market H/D/A = 0.354/0.311/0.335 (Korea fav) vs matrix
0.358/0.278/0.364 (Czech fav) → pick **0-1 for a market Korea-favorite**. Knife-edge (P(0-1) .0961 vs P(1-0)
.0951) but substantive. Decisive favorites are NOT affected (USA-PAR: market == matrix == home-fav, supremacy
+0.45 = clean). Process tier: catching this in a DRY-RUN is success (L8); the RUN itself = PASS.
**Detection:** `matrix_favorite != market_favorite` OR `|P_home − P_away| < ε` (near-even).
**Interim (zero code, HITL):** manual override to the MODAL score (do NOT abstain) — it is the EV-argmax under
the market-draw distribution and respects the (barely-ahead) market favorite via the high-mass draw.
matchday-1 KOR-CZE: baseline (0,1) → override (1,1).
**Root fix (auditor-validated):** ρ-fit — KEEP μ from the totals price, solve `s ← P_home` AND `ρ ← P_draw`
(ρ is literally the Dixon-Coles draw knob). SUPERIOR to the (μ,s)-fit, which is REJECTED: it fixes the favorite
but deforms μ 2.44 → 2.12 (drift −0.32), discarding the totals signal and biasing every goal-count low. The
ρ-fit requires RE-RUNNING the M7 backtest (the historical Δ was measured under the old fit).

## L18 — A dict whose key order feeds an RNG draw must be DETERMINISTICALLY ordered, never a bare `set` (caught 2026-06-10, lock-run determinism gate)
**Pattern:** `pool/ingest_ownership.laplace_ownership` built ownership as `{c: ... for c in set(raw)|set(named)}`.
Set iteration over STRINGS is randomized per process by `PYTHONHASHSEED`, so the dict key order varied run-to-run.
The joint MC draws opponent picks via `rng.choice(len(labels), p=probs)` over `list(own.keys())` — a different
key order maps the SAME fixed seed's draws to different LABELS → statistically-equivalent but byte-different MC
results (ΔE jittered ±0.0002 ≈ 1·SE across runs). Same `seed=20260602`, different output. The byte-exact A2
anchor did NOT catch it (it's a WITHIN-process equality, so both sides share whatever order that run drew).
**Why it hid:** the Jun-6 test run shared the latent bug but its verdict (chalk) was robust to ±SE jitter, so it
never surfaced — only the decision-grade 2·SE gate (which reads ΔE at the 4th decimal) exposed it.
**Detection:** diff TWO full runs (`diff lr1 lr2`), and run under `PYTHONHASHSEED=1` vs `PYTHONHASHSEED=999` — a
truly deterministic pipeline is byte-identical across both.
**Rule:** any collection whose iteration order reaches an RNG (label arrays, sampling order, dict fed to
`np.random.choice`) MUST be `sorted()` or otherwise fixed at construction. A fixed numpy seed is necessary but
NOT sufficient for determinism — the data structures feeding it must have stable order too. Values that are
order-independent (Laplace shares) make this a zero-risk, test-preserving fix.

## L19 — F2P1 "most-complete board" must be qualified by book TYPE; never bake a specific favourite into the contract (caught 2026-06-10, lock run GO#1)
**Pattern A (de-vig basis):** F2P1 selects the LARGEST WC-winner board as the de-vig divisor. The largest live
board was **Betfair (an exchange, 54 teams, overround 1.05)** — but LM9 bars an exchange from the divisor. Size
alone picked the wrong basis; the largest SPORTSBOOK board (DraftKings, 48, overround 1.19) is the LM9-correct
one. The gate verdict was invariant (Argentina cleared 0.08 on both: 0.0826 vs 0.0841), but the principle stands.
**Pattern B (assumed chalk):** the contract hardcoded "MVP chalk = Yamal." Fresh Jun-10 odds tied **Kane = Yamal
at +800** → the engine's chalk (max P_true, tie → less-owned) became Kane (0-owned) over Yamal (9-owned), a
+0.0025 E[prize] edge. A contract assumption about WHICH option is favourite can be FALSIFIED by the fresh fetch.
**Pattern C (verdict labelling):** a flip with ΔE < −2·SE is DETERMINATELY chalk (loses on economics), NOT
"indeterminate." Conflating "flip loses beyond noise" with "within noise" overstates ambiguity to the HITL.
**Rule:** (A) F2P1 = most-complete *sportsbook* board (exchanges are cross-check only, LM9). (B) Let the engine
derive chalk from FRESH P_true; don't pre-name the favourite in the contract. (C) Label verdicts three-way:
STABLE-CONTRARIAN (ΔE>2·SE + stable + R9) | INDETERMINATE (|ΔE|≤2·SE or σ/blank split) | STABLE-CHALK (ΔE<−2·SE).
**Rule:** `fit_lambdas`/`optimizer` are FROZEN → any near-even guard or ρ-fit is a SEPARATE GO with a Gate-7 RED
test FIRST, bundled with H4 into ONE post-lock engine-maintenance GO. Never let Track-B remediation compete
with the irreversible Jun-10 PM podium lock (the absolute priority).

## L20 — Plan→execute handoff: ground EVERY contract constant in as-built code; never trust a planned path/number/threshold (caught 2026-06-11, matchday-1 GO P0)
**Pattern:** The matchday-1 contract (planned by one model, executed by another) baked constants that the
as-built code contradicted: (a) "load the Jun-9 KOR-CZE snapshot" — no per-fixture snapshots existed (the raw
events lived inside `probe_lines_2026-06-06…json`); (b) "append L18/L19" — both numbers were ALREADY taken, and
the proposed "PYTHONHASHSEED" lesson was VERBATIM the existing L18 (a blind append would have collided/duplicated);
(c) "confirm cache dedupe" — `ingest.fetch_live` has NO cache (every `--live` is a fresh hit); (d) "write
`predictions/<date>/`" and "`review.sh`" — neither writer/script exists (`run_matchday` prints to stdout;
reviewer is `predictions/review.ps1`). Each was caught by reading the code BEFORE building, then corrected in the
plan as an explicit push-back (and the inversion was reproduced to 4 decimals on the real Jun-6 data first).
**Rule:** generalises L16 across a model/agent handoff — the executor must VERIFY every contract constant
(file path, lesson number, interface, threshold, "it caches/writes/exists") against the repo before acting on it.
Treat a planning contract as a *hypothesis about the code*, never as ground truth. A planned constant that the
code contradicts is a push-back to surface, not an instruction to follow. (Sibling of L18's lesson: a fixed seed/
contract is necessary but not sufficient — the substrate it runs on must actually match.)

## L21 — An external-audit gate has integrity only if the executor waits for the auditor's ACTUAL verdict, not an anticipated/self-supplied "GO" (caught 2026-06-11, matchday-1 P4 gate)
**Pattern:** the matchday-1 contract pre-declared "Plan APPROVED by Sebas (GO) + audited by claude.ai" and the
P5 step keyed off an "Auditor GO". The risk the auditor flagged: if the executor accepts a "GO" that the
gate-REQUESTER (Sebas) can author before the external reviewer (claude.ai) has actually run, the audit gate is
theater — the very independent check it exists to provide is bypassed. (This run did stop correctly at P4 and
waited for the real verdict, which then returned findings F1–F6; the lesson hardens the rule against the near-miss.)
**Rule:** at a HITL/external-audit gate, distinguish two distinct authorities: (a) the principal's instruction
to proceed (Sebas — legitimate, HITL) and (b) the external reviewer's VERDICT (claude.ai — must be the
reviewer's own emitted output, with its findings, not a relayed/anticipated label). Do not advance past an
external-review gate on (a) standing in for (b). When a "GO" arrives, confirm its provenance: whose verdict is
this, and has the reviewer actually run? Name what you are waiting for and stop until it exists.

## L22 — Per-fixture λ must be fit to mu_eff (price), not the totals line (re-confirmed 2026-06-11, F1 byte-check)
**Pattern:** a transparency dump (and the auditor's independent repro) computed λ via `fit_lambdas(probs,
total_line=2.5)` (fit mu≈2.51) while the LIVE `match_distribution` fits to `mu_eff = mu_from_pover(p_over, line)`
(KOR-CZE: 2.3614, fit mu 2.385). Same HOME (the fit pins P_home exactly) but draw/away drift ~0.8–1.1pp →
`match_distribution != score_matrix(fit_lambdas(probs, line))`. The matrix/EV/modal were always from the
correct path (unchanged), but the *displayed* λ were inconsistent with the matrix. This is L11 recurring at
the reporting layer. **Detection/Rule:** any λ or matrix repro MUST go through `mu_eff` when `p_over` is present;
assert `np.array_equal(match_distribution(st), score_matrix(lh, la, RHO))` before publishing λ. The over/under
PRICE carries the goal signal, never the (often pinned) line (L11).
