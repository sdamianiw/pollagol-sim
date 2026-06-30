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

## L23 — Validate every objective-function constant against the platform config before trusting a pick; a perfectly-optimized WRONG objective is silent (caught 2026-06-12, Track-B exact=2→3)
**Pattern:** the per-match optimizer's `points()` rubric encoded the EXACT-SCORE category as `+2` (max/match 8),
but the pollaya pool config pays `+3` (max/match 9). The optimizer was working flawlessly — argmax E[points],
145+ green tests, a passing M7 backtest — yet maximizing the wrong objective. It produced no error, no warning,
no visible anomaly: every pick "looked right" because the bug lived in the constant the whole apparatus trusts.
The danger is exactly that silence — a mis-specified objective doesn't crash, it quietly biases every downstream
decision and then corrupts any diagnosis that reasons from those decisions. Forensics under the corrected rubric
showed the blast radius was small *this time* (0/6 weekend picks flipped; MEX-RSA stayed argmax 1-0, E=3.530 vs
2-0 E=3.458 — the bug cost nothing on the one locked entry), and the backtest edge over B1 actually *widened*
(high-total Δ +0.0621→+0.0809) — but "small impact" was only knowable *after* the fix, and the next mis-encoded
constant may not be benign. Collateral: the Track-A σ-calibration (`SIGMA_CAL`=13.7782) was derived under the old
support {0,1,3,4,8}; flagged stale (F9), recalibration is a separate Track-A GO (out of scope here).
**Rule:** every constant that DEFINES the objective (scoring weights, payout multipliers, max-per-unit) must be
cross-checked against the authoritative platform/config source — not just unit-tested for internal consistency.
A locked test that asserts the WRONG number (here, `== 8`) is a green light on a broken gauge: it proves the code
matches the test, never that the test matches reality. Re-derive the objective from the source of truth (the
pollaya rubric), not from the codebase's own restatement of it. When you DO correct an objective constant, treat
every artifact that consumed it (backtest verdict, prior picks, σ/calibration) as suspect until re-run or
explicitly scoped out — a fix to the objective invalidates the diagnostics built on the old one. (Supersedes the
auditor's retracted L23; sibling of L20 — constants are hypotheses, here verified against the platform, not the repo.)

## L24 — The autonomy worth automating is EXECUTION DISCIPLINE, not model adaptation (caught 2026-06-12, Track-B Phase 2)
**Pattern:** the instinct after each match is to "learn" — tune ρ/σ/λ toward what just happened. That is the
cardinal error (I3): with n=2 (or n=20) the per-match points signal is pure noise (a ±0.05 pts/match paired-SE
needs ~280 matches to clear 0), so a model that mutates after each game is fitting noise and silently corrupts
the very diagnostics you'd use to notice. The execution-discipline loop (`src/decision_score.py`) instead
registers EVERYTHING (forecast + result), compares EVERYTHING (us vs B1=favorite, vs B2=modal, two Brier
conventions), and acts on NOTHING result-driven: results flow ONE way — decisions.csv → scoring → display —
never back into a model constant. The Brier we track for model-health is the matrix-implied (PRE-context DC)
convention, not de-vig-market (market is well-calibrated by construction → near-tautological, blind to the L17
draw-compression we actually want to catch — auditor F12). Backfilled n=2: us=5, B1=8, B2=5 (we trail the
naive favorite-1-0 baseline by 3 over two games — exactly the kind of small-n result you must NOT act on).
**Rule:** automate the discipline (never miss a fixture, never mis-enter, always rubric-optimal, always logged
+ compared), NOT the model. No result→model path, ever (grep-guarded; CLAUDE.md I3). Present every cumulative
diff with n + the ~280-match caveat; a model change is a separate Gate-7-RED-first GO from a mechanical cause,
never an inference from live scores. Track model-health with the metric that degrades when the model drifts
(matrix-implied Brier), not the one that looks good no matter what (market Brier).

## L25 — A completeness claim needs an INDEPENDENT denominator; never the same source/window under audit (caught 2026-06-12, Track-B weekend run)
**Pattern:** the Jun-12 run claimed to "close the MD1 coverage gap," widened `fetch_md1`'s window, and asked
the HITL "add the 4 Sunday games or all 7 remaining?" — then added "all 7" and declared the gap closed. But
"7 remaining" was derived from a probe of the **same `/events` endpoint within the same window being
audited** → circular. The real denominator is the **FIFA calendar: MD1 = 24 matches (48 teams)**; we had
covered 15 (2 played + 13), so **9** were missing, not 7. The dropped fixtures included **IRN-NZL (Tue Jun-16
01:00Z, deadline Mon-night 00:50Z)** — a live mis-entry risk and the *exact* silent-drop the run said it was
fixing. The scope question itself propagated the false premise (the HITL can't catch a denominator error you
fed them). Compounding root cause: CLAUDE.md said "MD1 Jun 11–15" (wrong; MD1 runs Jun 11–18), reinforcing the
"Sunday+Monday is the tail" mental model. **Rule:** a completeness/exhaustiveness claim ("all remaining", "the
full set", "nothing left") MUST be checked against a denominator from a DIFFERENT source than the one you are
enumerating — here the FIFA match calendar (24 R1 matches), never the odds API's windowed return. Operationally
(now HARD in CLAUDE.md §Data): every refresh, probe `/events` next ~72h and **diff ids vs decisions.csv**; set
`--expect` from the calendar count, not a same-endpoint probe (a guard fed the probe's number only proves
fetch==probe, not fetch==calendar — F24). Sibling of L3 (free tier can't serve WC odds — verify the source
actually covers the need), L7, and L23 (a silently-wrong constant passes every test that doesn't independently
pin the truth). When you say "complete," name the denominator and where it came from.

## L26 — Instrument the override; treat its SIGN as execution-discipline, NEVER a model signal (caught 2026-06-14, Track-B dual-track)
**Pattern:** the human's HITL overrides of the model's EV-argmax pick, scored against results, NET **−4 pts**
over the 8 played MD1 games (us_entered 15 vs us_model 19) — concentrated almost entirely in ONE fixture
(**HAI-SCO −5**: entered 0-2, but the model's 0-1 hit the exact score for 9), partially offset by USA-PAR +1;
the other 6 net 0. The instinct to "improve" on the model by typing a flashier / higher-scoring line (4-0 over
the model's 3-0; 0-2 over 0-1; 1-1-the-modal over the EV-argmax 1-0) systematically bleeds E[points], because
the optimizer ALREADY maximizes exactly that objective — an override is a bet that you out-predict a calibrated
argmax. The seductive next trap is to "learn" from the −4 and tune the model: that is the I3 cardinal error
(n=8 is pure noise; ~280 matches to clear a ±0.05 pts/match paired-SE). A second trap is the LABEL — the
cumulative summary historically called the MODEL track "us", so "us" silently meant the counterfactual (19),
not our actual 15-pt standing (F36). **Rule:** make the override VISIBLE and scored
(`override_value = us_entered − us_model`, now in `cumulative`/`summary_text`; dual-track schema cols
`entered_pick`/`pts_entered`, additive), and label **`us_entered` (real)** vs **`us_model` (counterfactual)**
unambiguously. Use the sign ONLY as execution feedback — default to the model pick, override ONLY with a logged
§5 thesis (the soft `is_model_high_confidence` advisory flags clear-favorite fixtures where an override is most
expensive, e.g. GER-CUW). NEVER feed override_value — or any result — back into a model parameter (I3).
Sibling of L24 (automate the discipline, not the model).

## L27 — The variance λ-dial is LOW-TORQUE under the exact=3 rubric; it optimizes the WRONG proxy for P(top-3) (caught 2026-06-14, ANNEX V skeleton)
**Pattern:** the placement-bet instinct (MAX P(top-3); 60/20/10 pays nothing below 3rd) suggested a per-match
mean-variance dial — argmax `E[pts] + λ·SD[pts]` — to "buy upside variance" when trailing. Built and measured on
the REAL matrices, it is nearly INERT: under exact=3, E[pts] and SD[pts] are POSITIVELY correlated (the same
modal-favorite pick that maximizes E[pts] also carries the most spread), so the dial is frozen on all but
coin-flip matches, and even there trades only ~0.10 EV for ~0.07 SD. The auditor's stylized −0.4 per-game cost
was WRONG (real ≈ +0.004–0.011, max 0.058; moves 5/16 fixtures, saturates by λ=1) — but the implied P(top-3)
BENEFIT is equally illusory (≈ net wash; P(top3) ~3.2% essentially unchanged). Root cause: the dial optimizes
per-MATCH SD, the WRONG proxy for tournament P(top-3). **Rule:** a null placement result from the dial means
"WRONG LEVER", not "variance is useless." The real top-3 levers are **(a) outcome hit-rate** — the 3-pt outcome
component dominates the rubric, so the L19 ρ-fit/H4 bundle (fix draw-compression + favorite-inversion) raises
E[pts] AND P(top-3) directly; and **(b) field-DIFFERENTIATION** — deviating from the field's likely modal pick
on near-even matches buys CORRELATED upside (you beat the WHOLE field at once when right), which a self-only SD
dial structurally cannot. The deferred placement-MC must therefore test FIELD-DIFFERENTIATION, NOT the
mean-variance dial. Sibling of L26 (instrument, don't tune) and the L9 proxy caveat (per-match SD ≠ tournament
placement). BUILD≠FIRE still holds — the skeleton fires nothing.

## L28 — ρ-fit (L19) CLEARS favorite-inversion + improves calibration/exact-hit, but is E[pts]/outcome-NEUTRAL: the draw-compression "bug" is real at the PROBABILITY layer, ~inert at the DECISION layer (caught 2026-06-14, M7 re-run, branch `rho-fit`)
**Pattern:** the L17/L19 thesis was "fit ρ to the market P_draw → restore the ~2–3pp draw deficit → fix
favorite-inversion → RAISE outcome-hit-rate (the dominant 3-pt component) → raise E[pts] AND P(top-3)." Built
(`fit_dc`: μ pinned from the totals price, solve `s←P_home` + `ρ←P_draw` by nested bisection, exactly identified;
band-clamp [−0.20,+0.10]; gated `rho_fit`, default-OFF → live byte-identical) and TDD-validated (Gate-7 RED→GREEN
on KOR-CZE: pick 0-1→1-1, inversion cleared; G-RHO1 same ρ in live+backtest; G-RHO4 OFF/ON test scoping; G-RHO5
I3-clean). The **M7 re-run (frozen ρ → fitted ρ, club leagues n=8945) REFUTES the edge half of the thesis:**
- outcome-hit-rate **0.5366 → 0.5336 (Δ −0.0030)** — the stated objective went slightly DOWN (within noise →
  NEUTRAL, NOT the predicted lift) → **G-RHO2 NO-PASS**.
- high-total E[pts] edge **+0.0809 → +0.0779** (still PASS, marginally narrower); exact-hit **0.1158 → 0.1235
  (+0.77pp)** and Brier **0.5792 → 0.5789** both IMPROVE; favorite-inversion artifact fixed.
- EV draw-rate **2.8% → 9.0%** (empirical 25.3%): converges, NO overshoot — but stays far below empirical because
  the **rubric's EV-argmax is structurally draw-averse**: under exact=3/outcome=3/GD=1, a 1-0 favorite pick banks
  outcome+GD+team-goals more reliably than a 1-1 even when the draw is well-calibrated. clamp-rate 0.84%; LIVE
  board 2026-06-14 = **0/16 picks changed** (no inverted near-even fixture pending).
**Root cause / rule:** calibrating P_draw does NOT make the EV-optimal pick choose more draws — the decision layer
(argmax E[pts]) is robust/saturated to moderate probability shifts, exactly as the variance λ-dial was (L27). **Two
distinct per-match levers (variance dial L27, ρ-fit L28) both target real defects and both fail to move
E[pts]/P(top-3) → the binding constraint is the OBJECTIVE, not the probabilities.** The only remaining torque is
changing the objective E[pts]→P(top-3) via **field-DIFFERENTIATION** (correlated contrarian vs the field), the
deferred post-MD3 lever. ρ-fit's real (smaller) value = calibration (Brier↓) + exact-hit (+0.77pp = real points
under exact=3) + inversion-correctness (never recommend a market-contradicting pick; ends the manual-override
burden, e.g. KOR-CZE/NED-JPN). **BUILD≠FIRE holds: kept default-OFF; the flip to live is Sebas's GO, justified —
if at all — by the calibration/correctness value, NOT by an E[pts] edge (there is none).** Sibling of L27 (right
defect, wrong objective) and L26 (instrument, don't tune).
**Auditor-reproduced** (independent 2000-board sim, same rubric): outcome-hit 0.5477→0.5428, exact-hit
0.1203→0.1240, draw-rate 2.2%→9.4% — same direction, NOT a scoring bug. Subset mechanism: pick-changed subset
(12%) outcome-hit DROPS −0.040 (E[pts] flat); **inverting subset (1.3%) outcome-hit DROPS −0.012 because ρ-fit
swaps the inverted-AWAY pick (the 2nd-likeliest outcome) for the DRAW (the LEAST-likely outcome)** — so "fixing
the inversion" SUBTRACTS points at the decision layer (a stronger keep-OFF reason than the flat aggregate).
**META-LESSON (L27+L28):** two per-match PROBABILITY levers both target real defects and are both E[pts]-inert ⇒
**the binding constraint is the OBJECTIVE (E[pts], single-entry, this rubric), NOT the probabilities.** The only
remaining top-3 torque is the objective swap E[pts]→P(top-3) via **field-DIFFERENTIATION** (post-MD3; SINGLE-entry
framing per Clair-Letscher, NOT HVZ's multi-entry submodular portfolio). Disposition: ρ-fit KEPT GATED OFF
(parked, validated knowledge); `rho-fit` branch unmerged; engine stays frozen on master.

## L29 — A recorded RESULT must be the cross-checked final score, never a remembered/expected one; the BLANK cell is the safety net (caught 2026-06-16, MD4/MD5 ingest)
**Pattern:** the cadence contract's PART-0a asserted NED-JPN was logged as 1-1 and needed "fixing" to 2-2
(actual: van Dijk 50', Summerville 64' / Nakamura 57', Kamada 88'). In fact `decisions.csv` had NED-JPN
`result` **BLANK** — nothing was ever mis-recorded; the "1-1" lived only in a stale mental model / an earlier
plan note. The system caught it pre-write. Had the row been pre-seeded with the remembered 1-1, the retcon
would have stood silently (record overwrites a blank result; `entered_pick` is retcon-locked once set).
**Rule:** only ever `record` a result that is the cross-checked final score (≥2 sources), and treat a BLANK
result cell as the correct default — never pre-seed a row with an anticipated score. A planned/expected value
is not a result; the gap between "what I think happened" and "the confirmed scoreline" is exactly where
grounding errors enter. Sibling of L25 (independent denominator) applied at the result layer.

## L30 — Reconcile Σpts_entered against the observed standings board before trusting a batch of recorded results; "override = 0" is a sum, not an agreement (caught 2026-06-16, MD4/MD5 ingest)
**Pattern:** after recording the 8 MD4/MD5 results, the dual-track cumulative read **Σus_entered = 28** over
n=16 — EXACTLY the observed pollaya board (us=28, rank 21/27). That equality is an INDEPENDENT check that
every (result, entered_pick) pair was entered correctly: the model and entry tracks are both derived inside
the tool, but the board is an OUTSIDE measurement. The cumulative override settled to **+0** (rows 1–8 = −4
[HAI −5 + USA +1], plus NED +4 over MD4/MD5) — a coincidental wash, not a target. **Rule:** when bulk-recording
played fixtures, reconcile Σpts_entered vs the latest standings board (the L25 independent denominator) before
trusting the batch; a mismatch means a wrong result or wrong entered_pick, caught while still fixable. Use the
override SIGN only as execution feedback (L26), never a model signal (I3) — and never read "override = 0" as
"model and I agree": it is a sum that can hide offsetting ±.

## L31 — All four MD5 games drew; the draw-lean counterfactual scored huge but it is variance (azar), not skill — do NOT tilt the live picks (caught 2026-06-16, MD5 review)
**Pattern:** MD5 finished ESP-CPV 0-0, BEL-EGY 1-1, KSA-URU 1-1, IRN-NZL 2-2 — **4/4 draws**. A draw-leaning
slate would have banked a large counterfactual (~+26 across the wave) vs the chalk favorite-by-one picks (~+3);
the instinct after a draw cluster is to start picking draws. But the rubric's EV-argmax is structurally
draw-averse for a reason (L28: a 1-0 favorite banks outcome+GD+team-goals more reliably than a 1-1 even when
the draw is well-calibrated), and a 4-draw cluster is a small-n variance excursion (azar) compressing f_skill
over a 4-game window — NOT a calibration failure or a skill signal. **Rule:** never convert a realized variance
cluster into a model/objective change (I-NOTILT, I3). P_draw is reported as CONTEXT, never added to the pick.
The legitimate response to "my picks under-weight draws" is the post-MD3 field-DIFFERENTIATION lever on
near-even matches (correlated contrarian, L27/L28), evaluated on calibrated probabilities over the full slate —
NOT a reactive draw-lean. Sibling of L28 (right defect, wrong layer) and the I-NOTILT cadence invariant.

## L32 — Deviating from EV-argmax to a gut scoreline on low-confidence near-even games strictly lowers E[pts] and never gains (caught 2026-06-19, Ronda-1/MD2 ingest)
> _The -9 override tally cited below is SUPERSEDED -> canonical running ledger: tasks/override_ledger.md (total -3 / tilt-only -4 as of 2026-06-21)._
**Pattern:** Over the 12 Jun-16→18 fixtures Sebas deviated from the EV-argmax pick on 9, and the realized
override came to **−9 pts** (Σus_entered=65 vs Σus_model=74) — almost exactly the gap between his real rank
(21/27) and where strict EV-discipline would have placed him. The cost concentrated where the EV pick hit the
exact score and the gut pick did not: **GHA-PAN** (EV 1-0 == actual 1-0 = 9 pts; entered 1-1 = 1; −8) and
**MEX-KOR** (EV 1-0 == actual 1-0 = 9; entered 2-1 = 4; −5). A by-one EV pick weakly dominates a gut 2-1 —
equal when the favorite wins by 2, strictly better when by 1 — so a gut scoreline can only match or lose vs the
EV pick, never beat it in expectation. The empirical "the favorite keeps winning 1-0" is the model being
*correct*, NOT a separate pattern to chase. **Rule:** enter the EV-argmax pick verbatim; entry-discipline =
model-discipline. The only thing that may flip a recommendation off fresh EV is DATA INVALIDITY (illiquid /
single-book odds), never a preferred scoreline. Extends L28/L31 and the I-NOTILT cadence invariant down to the
human entry layer.


## L33 — A flip's EV-gap must be compared to the noise-floor band EDGES; a near-lock "hold" is anti-churn / finalize-at-lock, NOT "noise" (caught 2026-06-20, Sat-Sun cadence flip-check, audit N3)
**Pattern:** On the Jun-20 fresh-odds cross-check NED-SWE flipped 1-0→2-1 with EV-gap **0.0410** and it was
labeled "at/under the ~0.03–0.04 noise floor → noise → hold." But **0.0410 > 0.040 (the band ceiling)**: by
the project's own KOR-CZE rule that is SIGNAL, so the engine's current pick IS 2-1. It was conflated with
GER-CIV (**0.0301**, at the floor → genuinely sub-threshold). Under EV-argmax PURE (I-NOTILT) there is no
"holding the old argmax" — the live pick is always the fresh argmax; the legitimate reason to keep the baseline
~9 h before a lock is **anti-churn / finalize-at-the-10-min-pre-KO lock** (totals wiggle intra-window), NOT
"the gap is noise." Mislabeling a timing-hold as a noise-hold causes a WRONG action AT the lock: holding 1-0
even if 2-1 still leads ≥0.04 = anti-EV inertia. (Also: GER-CIV's line moved 2.5→3.5 but it was the SAME book
`pmu_fr` relisting, and μ_eff stayed ~3.1 — the engine normalized it; the "book-swap artifact" hypothesis was
wrong, the flip is just a near-tie tipping by 0.030.)
**Rule:** (1) State the noise floor as a band [floor≈0.030, ceiling≈0.040] and compare the gap to the relevant
EDGE: gap>ceiling = signal, gap<floor = noise, between = ambiguous — never collapse to "at the floor." (2) Near
a lock, frame a non-switch as "defer-and-recheck, finalize at 10-min-pre-KO," and PRE-COMMIT the switch rule
("if the fresh argmax still leads ≥ceiling at the lock → SWITCH"). (3) A totals-driven flip with unchanged
favorite/outcome is still a real EV move; distinguish a within-same-book market move (μ_eff shifts) from an x.5
line relisting the engine already normalizes (μ_eff stable). (4) Process: a threshold-read / HOLD-vs-SWITCH
verdict is a JUDGMENT task — do NOT run it under a self-certifying `/goal` loop (it can rationalize "Goal
achieved"); present the per-fixture EV-gaps and STOP, leaving the umbral cut to HITL. Extends L32/I-NOTILT to
the refresh/flip layer.


## L34 — Resolve fixture identity from decisions.csv's full team strings, NEVER a relayed 3-letter code (caught 2026-06-21, MD-2 reconcile; Sebas correction)
**Pattern:** An inherited contract line instructed "resolve RCH-RSA as CHILE (not Czechia)". RCH in this sim =
**Czech Republic** (`decisions.csv` row 26 home="Czech Republic"); Chile never qualified. The relayed pollaya
3-letter code was ambiguous AND wrong, and contradicted the CSV's own team name — accepting it (even under an
autonomy grant) would have mismatched the fixture_id. The same board showed "CRS" = South Korea (row 29), not
Costa Rica: pollaya display codes are NOT 1:1 with FIFA codes in this sim. The error was caught pre-write only
because Sebas intervened; #3 (no invented facts / cross-check) and #7 (push-back) should have flagged the
code-vs-CSV contradiction first.
**Rule:** Match every fixture to its `decisions.csv` row by the CSV home/away **full strings** + kickoff UTC +
score triangulation — never by a relayed/screenshot 3-letter code. If any instruction's code contradicts the
CSV name, STOP and PUSH-BACK before any write, autonomy grant notwithstanding. Codes are display-only. Extends
CLAUDE.md #3/#7 down to the fixture-resolution layer.

## L35 — An EV-UPDATE classification must be GROUNDED by re-deriving the pre-lock snapshot argmax; a TILT that HIT on variance is still a TILT (caught 2026-06-23, MD-2 reconcile, audit F-ARG/F2)
**Pattern:** the Jun-23 reconcile classified two Jun-22 entry deviations (entered ≠ baseline `pick`): FRA-IRQ
3-0 (vs base 2-0) = **EV-UPDATE** and ARG-AUT 2-0 (vs base 1-0) = **TILT**. The first was grounded — re-deriving
the frozen engine on the pre-lock snapshot `md1_2026-06-22T16-57-21Z.json` showed FRA-IRQ argmax flipped to 3-0
(gap +0.047 > 0.040 = SIGNAL), so the entry FOLLOWED the engine = a disciplined fresh-argmax switch. The second
was initially only ASSERTED ("entered the modal, no engine flip"); the audit (F-ARG) correctly demanded the same
re-derivation. Re-running ARG-AUT on the same snapshot: argmax stayed **1-0** (= baseline, NO flip), modal 2-0,
and EV(entered 2-0)=3.277 was **−0.042 BELOW** EV(argmax 1-0)=3.319 — a discretionary move *away* from the
EV-optimal pick. Both ARG-AUT and FRA-IRQ HIT exact (9 pts each, +5 override), so by realized points they look
identical — but FRA-IRQ earned its EV-UPDATE label and ARG-AUT did not. The TILT/EV-UPDATE split is what sets
the L32 tilt-only metric (here: TILT → tilt-only 0; had ARG-AUT been mislabeled EV-UPDATE → −5), so the
classification is load-bearing, not cosmetic.
**Rule:** classify an `entered != pick` deviation as EV-UPDATE **only if** the pre-lock snapshot's frozen-engine
argmax == the entered pick (i.e. the human followed a real fresh-argmax flip, gap > noise ceiling); otherwise it
is TILT-OVERRIDE — including when it HIT. A variance hit never promotes a discretionary pick to EV-UPDATE (L8
symmetry: a winning override carries the same bias risk as a losing one; outcome ≠ process). Ground BOTH sides of
the split by re-derivation from the artifact (I-NOFAB), never by narrative assertion — the same rigor on the
TILT call as on the EV-UPDATE call. Sibling of L32 (entry-discipline = model-discipline) and L28/L31 (don't
convert realized variance into a label/objective change).

> (L36 override-decomp · L37 draw-bar · L38 token≠repo remain reserved candidates per the Jun-26 contract;
> canonicalize when written. L39–L42 below are the MD-3 day-3 batch, 2026-06-26.)

## L39 — The rubric is empirically exact=3 (max 9); a DOC that says exact=2 is the silent corruptor — fix the doc, never the engine (confirmed 2026-06-26, MD-3 day-3 TA8)
**Pattern:** the Jun-26 contract's TA8 ordered a sync of `MASTER_PROMPT_CONTRACT…§2` from a stale exact=2/max-8
to exact=3. Forensics: that file is not in-repo, and the in-repo rubric (`memory/rules.md:8,18`) was ALREADY
exact=3/max-9 with correct unit tests — nothing to fix. The proof is the reconciliation itself: prior 168 + this
batch's 24 = **192 == board ONLY under exact=3**; under exact=2 the six fixtures sum to 22 → 190 ≠ 192, falsifying
exact=2. The engine (`src/optimizer.py:17`) has been correct; the risk was a governing doc drifting out of sync.
**Rule:** the engine is the source of truth for the rubric — verify docs against it, never the reverse (I-3 /
FROZEN). When a contract says "fix the rubric doc", first confirm WHICH artifact is stale; if engine and in-repo
rules already agree, the task is verify-only + cite the empirical reconciliation, and an external template is the
human's to update (outside the repo write-set). An objective-function doc contradicting the engine is the
silent-corruptor; catch it at plan-preflight.

## L40 — A lock that drifts off the T-1h argmax is TILT even when it nets zero; net-0 does not launder the count (confirmed 2026-06-26, MD-3 day-2 JAP-SUE/TUN-NED)
**Pattern:** two day-2 locks diverged from their EV-baselines — JAP-SUE entered 2-1 (base 1-0), TUN-NED entered
0-3 (base 0-2). Re-running the frozen engine on the T-1h lock snapshot `md1_2026-06-25T22-07-56Z` showed the
argmax HELD at the baselines (1-0, 0-2) → the entries were flicker-takes off the EV-optimal pick = TILT-OVERRIDE.
Both scored identically to the baseline (1 and 4) → net-0 points, so by realized points they vanish — but the
tilt PATTERN is real and the COUNT must increment (L35: process ≠ outcome).
**Rule:** at lock, if |EV-gap| < the 0.040 floor the disciplined pick is the BASELINE, not the flicker (L33).
When a lock diverged anyway, classify it by re-deriving the lock-time argmax (L35) and increment the tilt count
even on net-0 — net-0 is luck, not discipline. The only sanctioned systematic override is the gated field-diff,
never a gut flicker (L32). Sibling of L32/L33/L35.

## L41 — "Grid-invariant" ≠ "upset-safe": a perturbation grid tests market MOVEMENT, not the irreducible tail (confirmed 2026-06-26, Turkey-USA 3-2)
**Pattern:** the Group-D blind-lock panel called Turkey-USA "USA-win invariant across the perturbation grid /
robust" — and it was, to market drift. Actual: Turkey 3-2 (home upset). The grid perturbed de-vig 1X2 / totals
mass and re-ran the engine; it never modeled the rotation/upset tail (USA 3RD-PENDING/safe → rotation risk,
flagged as unhedgeable). The blind-lock priced that tail acceptable and PAR-AUS's pleno (9) more than offset the
1-pt TUR-USA miss → Group D net **+10**.
**Rule:** don't over-claim "invariant/robust" from a grid sweep — say "robust to the modeled market movement" and
keep the separately-flagged upset/rotation tail visible in the recommendation. A grid that holds is necessary,
not sufficient; the tail is real and is absorbed by the portfolio (other picks' plenos), not eliminated by the grid.

## L42 — Chalk closes gaps near the podium; a variance/field-diff lever is net-negative E[prize] there → keep placement_mc PARKED (confirmed 2026-06-26, gap −9 → −4)
**Pattern:** the podium gap closed −9 → −4 over MD-3 day-1→day-3 with `placement_mc` PARKED (zero field-diff
flips) — pure chalk EV-picks landing plenos (PAR-AUS, CUW-CIV). At gap −4 with a full late wave ahead and a
compressed top (1st→5th = 8 pts), a field-differentiation/variance lever is NET-NEGATIVE E[prize]: variance could
as easily drop us to 4th/5th ($0) as lift us to 3rd.
**Rule:** near the podium with chalk already closing the gap, chalk-protect dominates — `placement_mc` stays
PARKED (portfolio BUILD, not FIRE). Re-evaluate a variance lever ONLY if we fall well below the cut at a
max-parity dead-rubber, where added variance is the only positive-EV move. Sibling of L28 (the binding constraint
is the objective; differentiation is for when you're BEHIND, not protecting a near-podium).

## L43 — qual_state MUTUAL-DRAW-SECURES must split TRUE-MUTUAL from ONE-SIDED-SECURES; a SAFE-ANY team has no draw incentive (caught 2026-06-26, Colombia-Portugal best-third cross-check)
**Pattern:** the tag MUTUAL-DRAW-SECURES (precedence 4) fires when BOTH teams have `draw_secures=True` (state in
{SAFE-ANY, DRAW-SUFFICIENT}) — but that conflates two incentive-distinct cases. **TRUE-MUTUAL** = both
DRAW-SUFFICIENT: both NEED ≥ a draw (a loss risks 3rd) → both fear losing → a mutual draw is a genuine
non-aggression equilibrium (SUI-CAN, PAR-AUS). **ONE-SIDED-SECURES** = one SAFE-ANY + one DRAW-SUFFICIENT: a
draw mathematically secures both, but the SAFE-ANY team is through even on a loss → free to rotate / chase the
top seed / indifferent → the draw is NOT a mutual pact (Colombia-Portugal Jun-27: COL SAFE-ANY 6 pts, POR
DRAW-SUFFICIENT). The DRAW-EXCEPTION signal is materially WEAKER in the one-sided case, yet v1 tags both
identically — and the engine already flagged Col-Por LIVE-ELIGIBLE on price alone, which over-states it.
**Rule:** before firing a DRAW-EXCEPTION on a MUTUAL-DRAW-SECURES board, manually check TRUE-MUTUAL (both
DRAW-SUFFICIENT) vs ONE-SIDED-SECURES (one SAFE-ANY); only TRUE-MUTUAL is a strong draw signal. **ENHANCEMENT
(PARKED, own GO — like the cross-group best-third manual step; qual_state is non-frozen but untouched here
beyond a docstring note):** sub-classify the tag into {TRUE-MUTUAL, ONE-SIDED-SECURES} from the already-computed
per-team states (both DRAW-SUFFICIENT vs one SAFE-ANY) — no new data needed. Sibling of the Paraguay-Australia
best-third mis-tag finding; complements L40/L33 (don't fire a weak signal as if it were strong).

## L44 — A council/subagent's quantitative E[pts] claim must be adjudicated by the frozen engine, never adopted on its hand-estimate (caught 2026-06-26, Phase B H/G coinflip council)
**Pattern:** the H/G close-call council (4 lenses on Cape Verde-SA + Egypt-Iran) had its rubric-floor lens vote
GO-DRAW on Egypt-Iran with a quantitative claim — `1-1 EV 3.14 > 1-0 EV 2.58` — and claim Cape Verde-SA's `0-1`
carries a 33% zero-floor vs 1-1's 20%. Both were hand-rolled from *estimated* scoreline masses. The frozen
engine (Dixon-Coles → `expected_points` over the full joint distribution) refuted both: Egypt-Iran `1-0=2.473 >
1-1=2.365` (the dissent inverted the ranking — 1-1 is NOT the E[pts]-max), and Cape Verde-SA `0-1` has the BEST
floor (P0 0.277 vs 1-1 0.280), not the worst (the agent forgot partial credit on near-scorelines, e.g. 0-1 scores
+1 on 2-1). Adopting the subagent's GO-DRAW would have overridden the engine's argmax on an arithmetic error.
**Rule:** a council/subagent is an ADVISORY judgment layer (incentives, market-read, adversarial refutation,
floor intuition) — it does NOT recompute E[points]. Any quantitative claim it makes (an EV value, a scoreline
mass, a zero-floor) must be re-derived from the frozen engine before it can move a pick; if the engine disagrees,
the engine wins. The council's value is hypotheses + perspective, not arithmetic — **confirm deterministically.**
Direct corollary of R7 (deterministic stats decisions stay single-pass/engine) + L35 (ground claims by
re-derivation, never narrative); complements [[subagent-strategy]] (subagents for research/judgment, never for the
deterministic forecast/stats decision).

## L45 - Reconcile the batch sum to the independent standings delta BEFORE writing; the I-NOFAB confirm-gate is load-bearing, not ceremony (caught 2026-06-27, MD-3 day-4 paren near-miss)
**Pattern:** the day-4 auditor's first screenshot decode mis-read 4 of 6 `(actual)` parens as == the pick, nearly
logging 5 false plenos (+49 vs the true +25). It was caught ONLY by reconciling the batch sum (Sigma pts_entered)
against the independent standings delta (board 217 - prior 192 = 25). The CONFIRM-GATE (re-read each paren
independently) + this arithmetic cross-check are the controls that catch a transcription error before it corrupts
an immutable row (record's retcon-guard forbids a second attempt). When the screenshot is NOT in-repo (as here),
the reconcile + explicit HITL "confirmado" IS the I-NOFAB gate - there is no OCR fallback.
**Rule:** never write a transcribed result batch until (a) the human has confirmed the re-read table verbatim AND
(b) Sigma(entered points) == the independent standings delta. A batch sum that does not match the board delta is a
STOP (FM-paren), not a number to be reconciled away. Extends [[always-use-task-manager-and-gates]]; complements
L34 (full-string resolution).

## L46 - A winning override is still an override; the gain is variance, not edge (confirmed 2026-06-27, Cape Verde-Saudi)
**Pattern:** Cape Verde-Saudi was locked at the MODAL 1-1 over the EV-argmax 1-0 (a sub-floor-margin near-coinflip)
and gained +3 because the game drew (4 vs 1). By L8 symmetry this winning override carries the SAME bias risk as a
losing one - it is the mirror of PAN-CRO -5 / ARG-AUT +5. The +3 must NOT be read as evidence that overrides work.
**Rule:** classify and log a winning override identically to a losing one - TILT-OVERRIDE, tilt-count increments,
the points delta goes to the tilt-only tally. Do NOT relabel it skill, and do not let the +3 launder the no-tilt
rule. (Mitigant: on a true coinflip EV ~= modal within the floor -> expected cost ~0 -> low-stakes, still logged.)
Direct application of L8/L32 symmetry.

## L47 - IN the podium -> chalk-protect; field-diff CLOSED (confirmed 2026-06-27, rank 2 gap_podium +1; extends L42)
**Pattern:** we crossed INTO the podium this MD (rank 2/27, gap_podium +1) on chalk EV + variance, placement_mc
still PARKED. Top-4 are within 4 pts and only 6 games remain -> the outcome is now Tier-3 luck-dominated.
Introducing discretionary variance now (field-diff, draw-exceptions, modal hedges) RISKS the podium we earned;
with the top-heavy 60/20/10 payout, dropping to 4th = $0 is the dominant risk, which dwarfs the upside of chasing 1st.
**Rule:** when IN the podium with few games left, run pure chalk EV on every remaining fixture - do NOT
differentiate, do NOT chase 1st with variance, do NOT fire draw-exceptions. Strengthens L42 (near-podium -> chalk
closes gaps): now that we are IN it the lever is not just net-negative, it is podium-threatening. placement_mc stays PARKED.

## L48 - An EV-UPDATE flip can be booked two ways (absorb-into-pick = override 0, vs count-the-gap = override +N); choose by engine-verified argmax + human intent, apply consistently (caught 2026-06-27, Norway-France vs the FRA-IRQ precedent)
**Pattern:** Norway-France's recorded `pick` was the stale Jun-24 baseline 0-1, but the engine's argmax on the
final pre-KO snapshot (`md1_2026-06-26T18-17-02Z`) was 1-2 (E[pts]=3.045, verified) - a genuine flip-switch, and
Sebas entered the flipped 1-2. Two bookings give different totals: (A) ABSORB - update `pick` 0-1->1-2 to the
verified argmax, entered==pick, override 0, cumulative +1; (B) COUNT - keep `pick` at baseline 0-1, entered 1-2
differs, override +1 EV-UPDATE, cumulative +2. The Jun-23 FRA-IRQ EV-UPDATE was booked (B) (pick stayed 2-0, +5
counted); NOR-FRA was booked (A) per Sebas's explicit directive + engine verification. Same phenomenon, opposite
accounting - a latent inconsistency.
**Rule:** an EV-UPDATE is ABSORBED (update `pick` to the engine's verified final pre-KO argmax -> override 0) iff
(i) the engine's argmax verifiably flipped on the pre-KO snapshot AND (ii) the human entered that flipped argmax;
otherwise it is COUNTED (pick stays at baseline, override = the gap, labeled EV-UPDATE not tilt). The number is
engine-adjudicated either way (L44). OPEN: the FRA-IRQ row was booked the other way and is NOT re-opened here -
pick ONE convention and reconcile retroactively before end-of-tournament scoring. Builds on L35 + L44.

## L49 - Bind every fixture by full team string + fixture_id, never by 3-letter code or internal/contract group letter (caught 2026-06-28, the Argentina-group mislabel)
**Pattern:** in the final MD-3 cadence I labeled groups by the CONTRACT's arbitrary letters (it called
Croatia-Ghana "Group J") instead of the official pollaya/FIFA source. On a "fetch groups J-K" ping I then
fetched the already-kicked-off Croatia-Ghana group as "J" - the DEAD, unlockable group - instead of the real
upcoming ARGENTINA group (Algeria-Austria + Jordan-Argentina, KO 02:00Z). The pollaya app compounds the trap:
Algeria AND Argentina are BOTH coded "ARG" (distinguished only by flag - green-crescent vs light-blue-sun) and
Austria is "ATR". A 3-letter code is NOT a unique key; an internal/contract group letter is an arbitrary label
that can silently disagree with the official source and route a pick to the wrong (or already-played) fixture.
**Rule:** never identify a fixture by a 3-letter code or an internal/contract group letter. Bind every pick by
FULL team string + fixture_id + flag, cross-checked against the official app / FIFA schedule, BEFORE any fetch /
present / lock. Deterministic procedure: map the official-source slate -> predictions/decisions.csv rows by full
home/away string + fixture_id (those strings are unambiguous; the codes are not); resolve any code collision by
flag. Drop internal group letters from cadence presentations - name the teams. Extends L34 (full-string
resolution); the ARG=Algeria/Argentina, ATR=Austria collision is the canonical instance. See memory
[[bind-fixtures-full-string]].

## L50 - LEADING (rank 1) -> chalk-protect MAXIMAL (group stage closed 2026-06-28; us=245 rank 1/27, +4 over a 3-way tie)
**Pattern:** the group stage closed with us in FIRST (245, gap_2nd +4 over a 3-team tie at 241). From the front, the
60/20/10 payout is maximally asymmetric: any discretionary variance is pure downside (a flip that misses can only drop
us off the lead; a flip that hits barely extends an already-winning margin). The contract's earlier "field-DIFFERENTIATE
for top-3" reflex (Clair-Letscher single-entry) is now actively WRONG - we ARE the field's ceiling.
**Rule:** while leading, match the field's EV-argmax picks; the only remaining swing is Tier-3 pleno luck we accept. The
ONLY acceptable override is rule-confirmed + model-grounded (e.g. a verified EV-UPDATE flip-switch), NEVER gut. Escalates
L47 (IN-podium -> chalk-protect) one notch: podium = protect; rank-1 = protect MAXIMAL. Carries into every KO round.

## L51 - The dead-rubber draw edge is GROUP-STAGE-ONLY; a winning override is NOT vindication (closed 2026-06-28)
**Pattern:** the +7 this batch came from two DRAW-EXCEPTION overrides that WON - Colombia-Portugal (entered 1-1 vs EV 0-1,
0-0) +3 and Algeria-Austria (entered 1-1 vs EV 0-1, 3-3) +4. The read was CORRECT: the frozen engine under-prices the
mutual-draw incentive in a dead rubber (both teams already through / both content with a point), a real blind spot.
**Rule:** BUT (a) per L46/L8 a winning override carries the SAME bias risk as a losing one - book it as VARIANCE, not
skill; it does NOT launder the no-tilt rule; and (b) the edge is DEAD-RUBBER-SPECIFIC and VANISHES in the knockouts (no
dead rubbers - both teams play to advance). The draw-override reflex STOPS at the group stage. PARKED enhancement (like
best-third): encode the dead-rubber-draw uplift as a `qual_state`-driven §5 context modifier so the insight is
systematic/auditable (not gut) for portfolio value + future tournaments. NOT for this KO bracket.

## L52 - The KO draw-rule (90' vs 120'+pens) is a LOAD-BEARING config, not a guess (flagged 2026-06-28, pre-R32)
**Pattern:** the frozen engine emits a 90'-regulation scoreline distribution. In the knockouts a "draw" pick's value
depends entirely on whether the pool scores the 90' result (REG90) or the full 120'+penalties result (FULL120) - the two
rules INVERT the KO draw EV (under FULL120 most 90' draws resolve in ET, so the engine's draw mass overstates the scored
draw mass). The rule is pool-specific and lives in the pollaya in-app KO config - it is NOT web-resolvable.
**Rule:** parameterize it (a `KO_SCORING` flag + a `ko_adjust(dist, rule)` POST-PROCESS wrapper - NEVER a frozen-engine
edit) and GATE draw-picks on it. While UNCONFIRMED, run DRAW-SUPPRESSION: decisive picks are rule-robust (a decisive 90'
pick that holds scores the same under both rules; a 90' draw your team wins in ET scores BETTER under FULL120), draw-picks
are rule-sensitive (win only under REG90) -> as the LEADER (L50) take the rule-robust line, never lock a draw-argmax until
the rule is confirmed. Resolve `KO_SCORING` before the first draw-relevant KO lock.

## L53 - R32 cadence: fire the council on a GENUINE near-even board, not on a 0.55 tag-artifact (2026-06-29)
**Pattern:** the read-only CLEAR/TIGHT map tags TIGHT when max(pH,pA) < 0.55. On Jun-29 that flagged Brazil-Japan
(de-vig Brazil 0.529) and earlier SA-Canada (0.53) as TIGHT - but both are directionally CLEAR ~2.7x favorites whose
EV-argmax == modal and whose pick is decisive + KO-rule-robust. Firing a 5-agent council on a 0.53-vs-0.55 threshold
artifact is wasted motion (and, while LEADING/chalk-protect, the council cannot move the EV-argmax pick anyway, L50).
**Rule:** the council trigger is a GENUINE near-even board, not the tag alone - diagnose by (a) EV-argmax DIVERGES from
modal AND (b) weak favorite / live draw (Netherlands-Morocco: NL 0.416 / draw 0.308 / EV 1-0 vs modal 1-1). Fire it as
LATE as the HITL can actually attend: the freshness ideal (T-1h, fresh odds+lineups, L33) is BOUNDED by human
availability - if Sebas can't reach T-1h (NED-MAR KO 01:00Z = 03:00 German, no T-1h ping), pick the LATEST feasible
window (~T-5/6h, when he's still awake) over firing 8h early or missing it entirely. NED-MAR is the user-MANDATED
council exemplar: the single most penalty-likely R32 tie (very similar/contested sides), where FULL120 scoring makes the
90' draw mass (0.308) most misleading vs the still-level-after-120' SCORED-draw mass - a 90' draw won in ET is NOT a
scored draw. Cadence proof: 1 fetch (15/15, quota 435, B4 byte-identical), 0/15 flips vs Jun-28 baseline, 0 draw-picks;
wrote 3 today/tonight baseline rows (BRA-JPN 1-0, GER-PAR 2-0, NED-MAR 1-0); SA-Canada recorded 0-1/0-1 = +9 (us_entered
245->254); frozen diff empty; /code-review N/A (data-ops, no code diff).

## L54 - The FULL120 KO rule makes the DRAW worse, not better: `ko_adjust` built; NED-MAR deep council = HOLD 1-0 (2026-06-29)
**Pattern:** built `src/ko_adjust.py` (the long-deferred L52 wrapper; non-frozen, standalone, reuses frozen
`optimizer.expected_points`+`model.implied_1x2`, 9 TDD, suite 251, frozen diff empty) to answer the toughest R32 call
(Netherlands-Morocco, the most penalty-likely tie). It transforms the 90' matrix -> FULL120 scored dist: off-diagonal
(decided-at-90') invariant, only the diagonal (level-at-90') redistributes through an ET Poisson model; a==b stays level
= scored draw (pens excluded). The counter-intuitive result, proven across the WHOLE penalty-rate band: **the draw is
NEVER EV-justified, under ANY rule.** best-decisive (1-0) beats best-draw (1-1) by +0.62..+1.75 across f in [0.30,0.83],
and STILL by +0.247 at f=1.0 (= REG90, the draw-MAXIMAL bound) -> the gap is SMALLEST when draws are maximally favored
and only WIDENS as ET resolves them. Intuition trap busted: Sebas (rightly) worried the 90' draw mass (0.31) was being
undervalued; FULL120 makes it WORSE because a 1-1 won in ET becomes a 2-1 (not a scored draw), cratering the 1-1 pick
while 0-0->1-0 ET resolution reinforces 1-0.
**Rule:** (a) the council is ADVISORY (L44) - the EV math lives in the deterministic engine, NEVER a lens; the
adversarial's strongest case (2-1 "better-calibrated") was REFUTED by re-deriving vs ko_adjust (1-0 2.746 > 2-1 2.680 AND
higher P) - exactly the L44 discipline. (b) a 5-lens panel (market/form-tactical/historian/contrarian/adversarial) +
deep-research historian (f=0.70 [.50-.83] from WC KO 1982-2022, BTTS 75% Qatar-confirmed) gave the draw its BEST
empirical shot and it still lost = rigorous rejection, not a reflex. (c) pre-register a NUMERIC decision rule
(best_draw_ev >= best_decisive_ev - eps across the f-band) so the loop verifies on a number, not vibes - this is what let
the panel converge (contested=FALSE) without endless debate. (d) /code-review caught 2 real bugs in the new module
(grid-edge clamp creating a FALSE diagonal = miscounted decisive-as-draw; best_draw/decisive None-vs-valid
inconsistency) - both fixed + regression-tested; pushed back on 2 (symmetric mu_et override + unconditional-lambda ET =
documented stylizations absorbed by cageyness calibration). DELIVERED: HOLD NED-MAR 1-0 (engine EV-argmax; chalk-protect
L50-aligned; pick UNCHANGED from baseline, council CONFIRMS). `ko_adjust` now reusable for Belgium-Senegal + every later
KO round. Artifact `council/outputs/ned_mar_r32/verdict.md`.

## L55 - A sound EV decision that loses to variance is still sound; EV-argmax != modal, vividly (2026-06-30)
**Pattern:** NED-MAR R32 = the deep council REJECTED the draw on EV (1-0 argmax, draw dominated at EVERY f; L54).
Actual = **1-1** (Morocco advanced on pens; FULL120 pens-excluded -> scored DRAW). The model MODAL was 1-1 -> it
scored **9** (exact); the EV-argmax 1-0 scored **1**; Sebas's entered 2-1 (his HITL deviation toward the adversarial's
#2) also scored **1**. So in hindsight the modal nailed it and BOTH decisive picks missed. Same day GER-PAR also
ended 1-1 (Paraguay upset on pens), our 2-0 = 0. Two favorites eliminated, two scored-draws, one wild day.
**Rule:** do NOT outcome-bias. (a) The scored-draw was a ~0.14-0.22 tail; it landing does NOT make the EV pick wrong
- EV-argmax maximizes EXPECTED points, not realized, and over n it wins (M7 backtest). Concluding "we should have
drawn" from the 1-1-scored-9 is exactly the I3 / results-driven error the project bans (n=76 << 280). (b) It IS a
vivid demonstration that **EV-argmax != modal on draw-prone KO boards** (L27/L28 meta-lesson: the binding constraint
is the OBJECTIVE; on a high-draw board the modal and the EV-argmax genuinely diverge - here by 8 realized pts). The
ko_adjust verdict (hold decisive) was epistemically correct; the build's value stands. (c) **Chalk-protect HELD:**
despite two favorites dying we stayed RANK 1 at 264 (+4 over Lucas LDC 260; gaps +4/+9/+14 PRESERVED) because the draws
hurt the whole field symmetrically - precisely why the leader takes EV/chalk and lets variance wash out (L50). (d)
Sebas's 2-1 over the rec'd 1-0 = a TILT (override 0 here, cost nothing; book as variance per L32/L35, NOT validated;
BRA-JAP 2-1 was the other tilt, +5, a lucky PLENO). NEXT-round discipline UNCHANGED: enter the EV-argmax, accept
modal/draw variance, never chase the draw because one hit.

## Code-review gate log (one-line cadence; lighter than the L# blocks — see CLAUDE.md → Review Gate)
- 2026-06-25 · installed the `/code-review` gate (doc-ops: CLAUDE.md Review Gate block + plan-preflight Phase E) · Redundancy-criterion: rejected 6 already-present/conflicting concepts (simplicity/TDD/plan-default/writing-skills/self-improvement = already have; subagent-driven = R7 boundary; git-worktrees = single-canonical decisions.csv L2) · R7 boundary drawn (code-review = code-quality ≠ deterministic-stats decisions; aligned with Sebas's "use subagents liberally" note) · gate result = DOGFOODED on its own diff (10 angles × 3 reviewers) → caught a real mis-reference: "extends FM3" corrected to "extends #7 Sparring/PUSH-BACK" (FM3 = anti-fabrication, not critique-integrity) → **gate has teeth on first use**.
- 2026-06-29 · `/code-review` on the NEW `src/ko_adjust.py` diff (212 lines; 2 finder agents = correctness + reuse/conventions) · result = **2 real bugs caught + fixed** (grid-edge `min(k+a,n-1)` clamp created a FALSE diagonal → a≠b ET overflow miscounted decisive-as-scored-draw, fixed to drop-overflow+renormalize + regression test #9; `best_draw`/`best_decisive` None-while-`ev_argmax`-valid inconsistency → unified on one `_candidate_table` scan with modal fallback) + 2 cleanups adopted (reuse `model.implied_1x2`; single scan removes the double O(n⁴)) · **2 findings pushed back with reasoning** (symmetric `mu_et` override = by-design convenience, live `cageyness` path is asymmetric-correct; unconditional-λ ET = stylization absorbed by cageyness→empirical-f calibration) — documented, not changed · I3/frozen CLEAN (ko_adjust imports only, mutates no frozen file, reads no result) · suite 250→251 green.
