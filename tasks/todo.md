# todo.md — build order + status

Mirrors the approved plan. Each module: goal → minimal impl → run + show output → log. Verify before next.

> ▶ **RESUME (2026-06-03): see `tasks/HANDOFF.md`. TRACK-B GO ACTIVE** — build the per-match EV engine
> (Track B P0–P4 below), the ~88%-of-points lever (L6), ahead of DoD-3. **P0–P2 DONE** (engine M1–M6,
> 45/45 GREEN); **NEXT = P3 GO** (M7 backtest = Gate-A methodology proof on football-data.co.uk). A3 /
> other-4-picks (DoD-3) DEFERRED. Track-A pool
> phase DONE through Step 7. HARD GATE: never LOCK; champion is OPEN; A2 `pool_montecarlo.py` FROZEN.
>
> ▶ **NEW GO (2026-06-04): TRACK-A PODIUM (5 locked picks; lock Jun-10 evening, Jun-12 VOID).** Squads public (FIFA
> 2026-06-02) unblocked it. **P0 DONE; NEXT = P1 GO.** Joint K-lever engine `pool/podium_montecarlo.py`
> (A2 frozen, byte-exact at K=1; A2×5 BANNED — PODIUM-1). **P0–P4 DONE (P4 = prior-gated dry-run, 2026-06-05);
> NEXT = the Jun-10 EVENING real run (fresh odds + observed ownership + σ-calibrated engine).** Plan:
> `C:\Users\Sdami\.claude\plans\track-a-podium-execution-virtual-starfish.md`. See "Track A — PODIUM (P0–P4)" below.

## ✅ RESOLVED — pollaya pick visibility (2026-06-02)
- [x] **Premiation/locked picks ARE visible** (screenshots) → `PICKS_VISIBLE=True`; `observed` ownership
      is REAL. Per-match scorelines HIDDEN → prior only. HITL GATE persists (`is_gated('prior')`); never
      LOCK without measured ownership + Sebas. N=12→20–25; lock Jun-10 evening (hard backstop first match Jun-11; Jun-12 VOID).
- [x] **API-Football key** provided (in .env, gitignored). Probe ran 2026-05-30.

## Step 0 — scaffold + coverage/quota probe
- [x] Create file tree.
- [x] CLAUDE.md, memory/ (rules/user/preferences/predictions), tasks/ (todo/lessons). Rubric locked + unit-tested.
- [x] `src/probe.py` ran 2026-05-30. **FINDING: API-Football FREE tier cannot serve season 2026**
      (errors.plan; free = seasons 2022-2024 only; no WC odds even for 2022). Verdict → memory/rules.md + L3.
      → Track A odds via WEB FETCH; Track B odds source PENDING (task #7).

## Track A — locked picks (FIRST; run council after Jun 2, finalize ~Jun 10)
- [x] **A1** `pool/leverage.py` — de-vig + screen FIXED & verified (Gate-7 GREEN; named-only ownership,
      tail UNDEFINED, candidate⊆named={Brazil} w/ 6.5% break-even; L4). **UPDATED 2026-06-02:
      PICKS_VISIBLE=True, observed unblocked, `is_gated` added (T6/T7 GREEN).** Pick NOT final — champion OPEN.
- [x] **A2** `pool/pool_montecarlo.py` — E[prize] per champion candidate; argmax; CRN + fixed seed
      (DEFAULT_SEED=20260602, BASE_SIGMA=6.0). Ownership = OBSERVED primary; opponent GROUPS
      (locked~observed, pending~prior). **2-scenario selftest GREEN** (chalk→Fav gap +0.0116; flip→Dark
      gap +0.0104; determinism: byte-identical re-runs). Gated real-data demo prints DRAFT banner (no
      lock). `decision_clock.md` (Step 5, INVARIANT/TIME-DEPENDENT + PB1–PB5 + lock schedule) + L5
      (Step 7) done. **DONE 2026-06-02.**
- [ ] **A3** `council/` 5 isolated lenses + `synthesis.py` (median/spread/dissent/leverage). Feeds A2.
      HITL: recommend; Sebas decides. GATE on ownership_source.

## Track B — per-match EV engine (P0–P4) — GO 2026-06-03 (supersedes the old M1–M8 bullet)
> ▶ Build the ~88%-of-points engine (L6) ahead of DoD-3. Each phase: GOAL → TDD impl → reproduced
> command + PASS/FAIL → STOP for the next GO. Champion stays OPEN; A2 `pool_montecarlo.py` FROZEN.
> Plan: `C:\Users\Sdami\.claude\plans\track-b-execution-contract-validated-wand.md`.

### P0 — F2 registration (executable now)
- [x] Append the F2 line (historical-odds gap) to `memory/rules.md` with source+date+context.
      Verify: `Select-String "F2" memory/rules.md` returns the line → PASS. **DONE 2026-06-03.**

### P1 — M7 historical-odds SOURCE resolution — DONE 2026-06-03 (free, $0)
- [x] Web pre-filter (L7): OddsPapi = unverified domestic-centric catalog claim (rejected); OddsPortal =
      in-domain but scrape (rejected); football-data.org/Kaggle = results-only (rejected).
- [x] Live 1-call probe: `football-data.co.uk/mmz4281/2324/E0.csv` → **HTTP 200, 380 matches**; one row =
      1X2 + totals + closing odds + result join key (Burnley 0-3 Man City sample).
- [x] M7 MODE = **historical-OOD + forward-confirm** (Sebas: no spend). football-data.co.uk OOD methodology
      backtest (decimal odds → `decimal_to_prob`) + free WC forward-test via M6 `review.ps1`.
- [x] Verdict in `memory/rules.md` ("P1 verdict — M7 historical-odds source") = source + mode + leakage
      rule (`odds_timestamp < kickoff`) + transfer caveat. **STOP for P2 GO.**

### P2 — Build M1–M6 — DONE 2026-06-03 (TDD RED→GREEN; 45/45 suite GREEN, no regression; e2e smoke OK)
- [x] **M1** `src/ingest.py` — parse The-Odds-API event + provenance + snapshot + web fallback
      (cached-snapshot replay via `load_snapshot`; live-fail→cached wiring in M8); reuses
      `_load_dotenv`/`_get`/`crosscheck_favorite`. Verify: snapshot reproduces identically; 2-source
      cross-check (NED-JPN Δ1.2pp PASS). (`tests/test_ingest.py`, 4)
- [x] **M2** `src/strength.py` — de-vig 1X2 (single book-set) + `decimal_to_prob` that STILL de-vigs
      (L9) + Elo fallback. Verify: normalizes to 1; overround re-derived (1.0709 on probe row); Elo
      fires. (`tests/test_strength.py`, 9)
- [x] **M3** `src/model.py` — Dixon-Coles; λ split + clamp/shrink; totals-present 1-D solve, absent
      nested solve. Verify: dist sums to 1; fit round-trips; ρ-sensitivity reported. (`tests/test_model.py`, 6)
- [x] **M4** `src/optimizer.py` — argmax E[points] + plausibility floor. Verify: **4 locked unit tests
      EXACT** (8/4/4/4); argmax; floor active. (`tests/test_optimizer.py`, 7)
- [x] **M5** `src/context.py` — dead-rubber/rotation/high-stakes/neutral flags. Verify: sourced
      `context_flag`; adjusts BOTH mean and variance. (`tests/test_context.py`, 6)
- [x] **M6** `src/decisionlog.py` → `predictions/decisions.csv` + `predictions/review.ps1`. Verify: every
      row sourced+dated (provenance enforced); review filter = played-and-unreviewed. (`tests/test_decisionlog.py`, 3)
- e2e smoke (M1→M2→M3→M5→M4): NED-JPN → **1-0**; divergence verified (away-fav→0-1, high-total→2-1) →
  NOT a 1-0 machine (now regression-guarded). 48/48 GREEN. **STOP for P3 GO.**

### P3 — M7 backtest = SUCCESS-PROOF — DONE 2026-06-03 · VERDICT = **PASS** (high-total segment)
- [x] `evals/backtest.py` (+ `evals/fetch_footballdata.py`, `tests/test_backtest.py` 21 tests) →
      EV selector vs **B1** on football-data.co.uk top-5 EU × **5 seasons** (8955 rows). **Reproduce:**
      `python evals/backtest.py` → `evals/backtest_results.json`.
      **HEADLINE (home-zeroed δ=0.30, OPENING odds, EX-COVID 2122/2223/2324, n=5402):**
      **HIGH-TOTAL Δ=+0.0621 pts/match, 95% CI [+0.0139, +0.1115], n=3300 → PASS.**
      low-total Δ=−0.0067 [−0.039,+0.027] → NO-EDGE — a MEASURED near-zero net, NOT an identity (the
      non-zero-width CI proves it): 71/2102 (3.4%) low-total fixtures diverge — EV→1-1 (68) / 0-0 (3)
      in balanced games vs B1's fav 1-0/0-1 (reproduced 2026-06-04, command+output). aggregate Δ=+0.0354
      [+0.0024,+0.0681] → PASS. **draw-modal diagnostic n=0 is SILENT, NOT confirmatory** — outcome-
      strict-max draw needs μ<~1.885 but the μ_eff floor ~1.8 + low-μ matches carry a favorite → it
      ~never fires and misses the EV→1-1 picks. Calibration (δ=0, all-5, n=8945): Brier 0.579
      (< uniform 0.667), log-loss 0.974 (< ln3 1.099), exact-hit 0.114. PASS holds across ALL
      sensitivity rows (closing +0.069; δ=0 +0.076; data-derived δ=0.276 +0.080; δ=0.311 ex-COVID +0.062).
      **SCOPE (L9/L10):** PASS = market-totals-aware (μ_eff) > totals-BLIND B1, IN-DOMAIN — it does NOT
      imply a WC edge NOR that the DC model is necessary (a simpler totals-aware rule might capture much).
- [x] Leakage check (PM1) = **PASS** — football-data has NO per-row odds timestamp → structural guard
      (`assert_no_leakage`: model input carries only odds, never FT*) + source-semantics (B365 opening is
      pre-kickoff by construction). DC-modal NOT a baseline (FM1/L2). **No post-hoc tuning (L8).**
- [x] SEGMENT driver = **TOTAL level only** (rules.md iii corrected 2026-06-03: B1 mirrors the favorite
      side → away-fav is gap-0). Verdict read on HIGH-TOTAL. **Same-book** B365 throughout.
- [x] **μ_eff signal-recovery (rules.md v, FROZEN before reading):** football-data pins the line at 2.5,
      so M3 set μ≈2.51 for EVERY fixture (totals-blind) → invert p_over→μ_eff (Poisson) in evals/ ONLY.
      Hardened H1–H6 GREEN (μ span [2.38,4.04], corr(μ,p_over)=0.996, 0 clamp-bites, 69/69 suite).
- [x] **Gate A (OOD methodology, pre-picks) ≠ Gate B (WC forward, post-picks) — L9.** This PASS proves
      IMPLEMENTATION + an in-distribution edge; it does NOT imply a WC edge (transfer non-implicative, RB2).
      STOP for P4 GO.

### P4 — σ-calibration + M8 orchestrator (gated; defers to Jun 9–10 rehearsal if 6h cap hit)
- [ ] **CONSTRAINT (frozen 2026-06-03):** `M8 src/run_matchday.py` BLOCKED until M1–M7 GREEN (P3
      verified). **M7 = PASS (2026-06-03) → M8 wraps the DC engine** (not B1). (Had M7 been FAIL, M8 would
      wrap B1.)
- [x] **P4a — μ_eff PORTED to the LIVE engine — DONE 2026-06-06.** The ONE μ_eff model
      (`poisson_over_prob`+`mu_from_pover`, FROZEN spec) **moved into `src/model.py`** (+ `TOTAL_LINE`);
      `evals/backtest.py` re-imports it (byte-identical → I4 one model, no duplicate). `match_distribution`
      now consumes `p_over` (mu_eff = mu_from_pover(p_over, line); fed to the **FROZEN `fit_lambdas`** as the
      line) — mirrors `evals.fixture_eval`. TDD: totals-blind `test_mu_tracks_pover_at_fixed_line` RED→GREEN
      (E[tot] 2.51@0.45 vs 2.51@0.75 pre-port → lifts post-port); byte-equal to evals μ_eff on 3 fixtures +
      shared model object; hardening (hand-point/monotonic/roundtrip/poisson-inc/**corr≥0.9+span**/clamp).
      **M7 UNCHANGED (cross-phase gate):** run_backtest deltas == stored (agg 0.035357, hi 0.062121, exact)
      + `backtest_results.json` sha `8273f095…` unchanged. **src/ offline-pure** (no `evals` import).
      **fit_lambdas FROZEN; A2/`pool/` untouched.** Suite **104/104** (95+9). Completes L11's registered fix.
- [x] **P4b σ-calibration — DONE 2026-06-06.** `pool/sigma_calibration.py` (+ `tests/` 14 GREEN, suite
      95/95) derives σ from M7 variance as a RUNTIME value; model declared FIRST in `memory/rules.md`
      (anti-FM1 sentinel). **s_pm: ev_pts=2.444 [CI 2.40,2.49] (PRIMARY, conservative) > b1_pts=2.399 (chalk
      cross-check, shown not asserted); σ_lower=13.78 [13.52,14.03]; σ_upper=24.93 [24.47,25.38]; bracket
      [13.52,25.38] clears the ~σ7–8 flip → stylized robust_chalk.** **PRECISION (FIX-2):** the real σ_cal
      uncertainty is the d-DRIVEN RANGE **[6.2, 19.5]** over d∈[0.10,1.00]; **13.78 is only the d=0.50 point**
      and the bootstrap CI [13.52,14.03] is ~26× narrower than the d-range → NOISE vs d-uncertainty (f_div=0.611
      is itself a borrowed proxy: high-total match fraction ≠ player-divergence rate). Read σ_cal as ~14,
      plausibly 6–20. BUT the Step-3
      dual-ownership escalation (Sebas refinement, L13) shows the real K=4 verdict is
      **SIGMA_DEPENDENT_UNDER_LEVERAGE**: efficient→chalk at both σ endpoints, **starve→contrarian_2 at BOTH
      σ_lo=13.52 AND σ_hi=25.38** (contrarians persist far above the isolated-lever flip). → σ-calibration
      does NOT settle chalk-vs-contrarian; it **DEFERS to OBSERVED Jun-10 ownership**. σ_cal=13.78 written to
      `memory/sigma_calibration.md`, injected as runtime kwarg into `pool/run_podium_draft.py`
      (`read_sigma_cal()`); **A2 BASE_SIGMA=6.0 FROZEN, byte-exact anchor PASS**. M7 `backtest_results.json`
      sha-unchanged. Repro: `python pool/sigma_calibration.py`. **Jun-10: re-run podium+champion on σ_cal +
      fresh odds + observed ownership before any lock.**
- [x] **M8 DONE 2026-06-06 (suite 121/121)** `src/run_matchday.py` — M1→M2→[x.5 guard]→M3(μ_eff)→M5→M4→
      summary; HITL STOP (--submit disabled); offline (no evals, test-asserted); <60s/match (3.2s); dry-run
      prints table+EV pick+EV-vs-modal gap+sources/flags+STOP; snapshot-reproducible byte-identical. + `src/lines.py`
      + `src/probe_lines.py` (P4c-0) + `tests/test_run_matchday.py`. **H3 book-selection DONE (Option A):**
      `parse_event` prefers a book with h2h + x.5 totals (intra-book μ_eff, RB3-clean); else totals-blind + HARD
      flag; never cross-book. **Per-match coverage 100% (72/72)** → NON_X5 gate RESOLVED. **🛑 NEW: H4 (separate
      GO)** — M5 context post-DC mis-directs the mean for non-neutral flags (neutral tolerable; pinned + WARNING).
      STOP: HITL, no submit, no lock.

## Track A — PODIUM engine (P0–P4) — GO 2026-06-04 (completes the 5 locked picks)
> ▶ Joint K-lever E[prize] over the 5 picks (champion + 4 awards). A2 `pool_montecarlo.py` FROZEN +
> reproduced byte-exact at K=1. A2×5/sum-argmax BANNED (PODIUM-1; E[prize] non-additive). RECOMMEND, NEVER
> LOCK. Each phase: GOAL → impl → reproduced command + PASS/FAIL → STOP for the next GO.
> Plan: `C:\Users\Sdami\.claude\plans\track-a-podium-execution-virtual-starfish.md`.

### P0 — register PODIUM-1 finding — DONE 2026-06-04
- [x] Append PODIUM-1 (joint-reuse decision + thin-market policy) to `memory/rules.md` with source+date.
      Verify: `Select-String -Path memory\rules.md -Pattern "PODIUM-1"` returns the line → PASS.

### P1 — per-award P_true source resolution — DONE 2026-06-04 (matrix in rules.md PODIUM-2)
- [x] Code re-fetched each board itself (L7 live probe). **3 clean markets** →
      `data/props_{top_scorer,mvp,best_gk}.json` (mirror outrights shape, raw American odds + provenance).
      De-vig (`pool.leverage`) reproduced: named-coverage 0.846/1.025/1.330, all P_true→1.0 (L4). 2-book
      favorite cross-check PASS (top scorer Mbappe +600 FanDuel≡DraftKings). **top-assister = `[PENDIENTE]`**
      (no clean single-book-set board; DK/BetMGM don't offer it) → EXCLUDED now, engine runs **K=4** levers
      (champion+scorer+MVP+GK). **Lever NOT conceded (2026-06-05): mandatory FanDuel/Caesars assists probe at
      the Jun-10 re-fetch → add 5th lever if a clean board appears; manual chalk only if that ALSO fails.**
      Council runs the assister advisory-only until/unless it becomes a lever (G3).

### P2 — build `pool/podium_montecarlo.py` (joint K-lever) — DONE 2026-06-05
- [x] `expected_prizes_joint` + `expected_prizes_k1` shim + `recommend_portfolio_joint` (§7b NUMERICAL;
      bounded enum = all-chalk + single-flips + pairwise). A2 constants IMPORTED (not redefined); RNG draw
      order collapses to A2's at K=1 (groups-outer, one shared noise/group, skip-before-draw, natural dtype).
      **8/8 GREEN** (`tests/test_podium_montecarlo.py`): **T-anchor byte-exact at K=1 vs A2 — no skip, numpy
      1.26.4 confirmed** (real-champion single-group + synthetic two-group); T-chalk; T-flip-one; T-portfolio-
      rule; T-L4; T-perm-invariance (G1); no-edit-proof; numpy pin+guard (G2). A2 selftest still PASS; **full
      suite 77 passed (69→77, no regression)**; A2 unedited (only podium_montecarlo.py + test added).
      Repro: `python pool/podium_montecarlo.py` (byte-exact K=1=True) · `python -m pytest tests/`.
      **Finding (L12):** a lone contrarian flip's edge is diluted to ~0 by other LIVE levers → engine
      correctly stays chalk (§7b emerges numerically); K=1 intuition does NOT transfer to K>1.

### P3 — A3 council over the 4 ENGINE picks — DONE 2026-06-05
- [x] `council/run_council.py` (deterministic synthesis: median/spread/dissent/leverage; `--selftest`) + 5
      ISOLATED lens-agents (1 agent per lens covering all 4 picks = lens-isolation preserved at 5 invocations,
      R7) → `council/outputs/lenses_<award>.json` (dated+sourced snapshots). `tests/test_council.py` 2 GREEN;
      **full suite 79 passed**. Consensus (DRAFT/GATED): **champion=Spain** (4/5; contrarian→England),
      **top_scorer=Mbappe** (4/5; contrarian→Oyarzabal), **MVP=Mbappe but CONTESTED** (2-2-1: market+form→Yamal,
      tactical+baserate→Mbappe, contrarian→Olise; council 1.56x>market on Mbappe), **best_gk=Martinez** (3/5;
      form+contrarian→Simon). Top-assister council DEFERRED to Jun-10 (G3). **Fix (verification):** leverage
      now ref-basis (apples-to-apples), not full-board (was a 1.7-2.7x renormalization artifact) — regression-
      tested. Repro: `python council/run_council.py`. NOTE: council = triangulation only; engine+ownership (P4)
      decides; council P_true covers top-6 (no tail) so P4's engine input is the MARKET full-board P_true.

### P4 — integrate → DRAFT per-pick E[prize] + leverage — DONE 2026-06-05 (PRIOR-GATED DRY-RUN)
- [x] `pool/run_podium_draft.py` — integrates MARKET full-board P_true → joint engine (K=4) + council overlay +
      (prior) ownership; reproduced output snapshot `predictions/podium_draft_2026-06-05.txt`. Guardrails honored:
      (FLAG2/FM2) one cached snapshot, stale-labeled; (FLAG3) §7b leverage(P_true/ownership) printed separate from
      council-vs-market divergence; engine input = market full-board, council = overlay only.
      **BASE (efficient prior):** all-chalk **(Spain, Mbappe, Yamal, Martinez)**, E_chalk=0.0499, no contrarian
      (leverage ~1.08–1.25 < 1.5). **R9a σ-sweep 4–12:** verdict=chalk at every σ (stable). **R9b ownership±1:**
      stable on all 4 levers. **§7b path verified via targeted-starve stress:** 4 contrarians identified → engine
      picks **2** (not 4) = the "don't over-gamble" rule; improvement σ-decays +0.032→+0.011 (4→10) = PODIUM-3
      σ-dependence in the integrated path. **Council overlay:** champion=Spain(maj), scorer=Mbappe(maj),
      **MVP=NO-MAJORITY (engine-chalk Yamal vs council-median Mbappe, CONTESTED)**, GK=Martinez(maj).
      Every banner DRAFT/GATED (`is_gated(prior)=True`); suite **81/81 GREEN**.
- [x] **PODIUM TEST RUN — observed-ownership rehearsal — DONE 2026-06-06 (suite 137/137):** `[OBS]` block in
      `pool/run_podium_draft.py` over REAL observed ownership (5 pollaya screenshots, Sebas excluded → N_opp=19).
      Model declared first in `memory/rules.md` (LM1 denom=N_opp; LM2 Laplace α=1, K_cand=top6∪observed; LM3
      blanks→`_SENTINEL`, sums to 1; L15). `pool/ingest_ownership.py` += `laplace_ownership[_with_residual]`,
      `blanks_chalk_resolved`, `load_observed_from_snapshot` (P2-b off-board→fold+log) +
      `data/snapshots/observed_ownership_2026-06-06.json` + `tests/test_observed_ownership.py` (16 tests).
      **Result (σ=13.78, PRELIMINARY):** Model A (blanks→0) → contrarian_1 (MVP Harry Kane); Model B
      (blanks~P_true) → all-chalk; **MVP FLIPS A↔B → INDETERMINATE, deferred to Jun-10** (Step-5b/FIX-1). Global
      σ-verdict = STILL-SIGMA-DEPENDENT. Assister advisory-only (Bruno Fernandes, no P_true, K=5 gate). A2 6.0
      byte-exact; σ/α untuned. NOT A LOCK.
- [ ] **Jun-10 EVENING real run (HITL, NOT done — needs the day):** ONE fresh odds snapshot (FM2) + REAL observed
      ownership (`load_observed`, exclude Sebas) + reconcile live N (12→20–25 vs 22) + σ-calibrated engine
      (PODIUM-3, post-Track-B-P4) + MANDATORY FanDuel/Caesars assists probe (→ K=5 if clean). Then Sebas LOCKS
      (lock Jun-10 evening; hard backstop = first match Jun-11, Jun-12 VOID). No lock before this.
