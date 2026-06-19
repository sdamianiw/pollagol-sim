# HANDOFF

> 🟢 **PRE-MD3 BUILD — player-panel + field-diff placement-MC (BUILD-BUT-WAIT, 2026-06-19/20, branch `rho-fit`, commit `5a69198` + remediation commit; engine FROZEN, 0 edits to the 6 frozen paths, NOTHING FIRED, suite 216 PASS; master untouched `05cde08`, NOT merged).** Plan `…\plans\pre-md3-build-contract-enumerated-marble.md`.
> **PART 0** — `standings/build_player_panel.py` → `standings/player_panel.csv` (27 players × 3 boards Jun-14/16/19; OCR NAMES validated vs `standings/<date>/standings.json` `points[]`: ordered match + monotonicity + roster constancy all PASS; S2/Jun-15 = phantom, dropped). Report `standings/player_panel_analysis.md`. **Skill: Spearman ρ(g1,g2)=−0.052 (n=27, ρ_crit≈±0.38, power~0.31) → CONSISTENT-WITH-LUCK, cannot exclude moderate skill; NOT no-skill-proven.** Leader Lucas LDC climbed rank 6→4→1 (luck). σ_opp = **σ(g2)=7.18** (σ(g1)=3.53 → variance RISING, may understate MD3); cross-check ≈ BASE_SIGMA 6.0.
> **PART 1** — NEW `pool/placement_mc.py` (single-entry Clair-Letscher field-diff E[prize]; imports A2 constants, never edits A2; reuses `src.optimizer.points` via 9⁴ int8 table; `is_coinflip` 0.08). 3 pick-roles (field-modal / EV-argmax `us_baseline` / decorrelating); CRN (sorted players, int64, renorm draws); locked picks cancel. `recommend_placement` = exploratory k-sweep + **ADVERSE-CORNER gate** (min ΔE over `{.75σ,σ,1.25σ}∪{6,8,13.78,19.5}` @ p_field_modal=0.85, CI_lo>0 AND Δp_top3≥ε_min), **P(top-3) per arm = HEADLINE**, WIRED-NOT-FIRED. `tests/test_placement_mc.py` 12 PASS — TDD (i)k=0→Δ==0.0 byte-exact (ii)trailing→>0 (iii)leading→≤0 (iv)determinism (v)single-entry (vi)orientation + **inverting-regime** + **bubble-consistency** + diagnostics.
> **CONDITIONALITY (P1 remediation):** trailing→ΔE>0 / leading→ΔE≤0 hold ONLY on LEVER-ACTIVE boards (`us_baseline == field modal`); if our EV pick already decorrelates from the field the property INVERTS (`board_lever_status()` flags `active`/`inverted-risk`; eligible iff active). **`ε_min` is HITL-SET at P4** (the 0.02 is a demo placeholder, surfaced via `eps_min_is_demo`). σ-grid top = 19.5 by default; `>19.5` OUT-OF-COVERAGE → set `sigma_top_extra=max(19.5, c·σ(MD3))` at P4 (rising variance). Tie-break = strict-`>` (ties→us = OPTIMISTIC; real pool tie-break ad-hoc per board footer).
> **🛑 NOT P4-READY until: (1) real MD3 boards + qualification (dead-rubber) states exist; (2) the decorrelating-pick SELECTION logic is built — P4 PREREQUISITE, deferred-as-argument here, must enforce `us_baseline==modal` eligibility; (3) Rama C (context.py M5/H4 fix) lands BEFORE any FIRE; (4) a fresh trailing-status read + a NEW Sebas GO.** Default-OFF: no live/cadence path imports placement_mc.
> **OPS:** the Jun-16 auto-HANDOFF write hit a claude.exe lock → this block was written manually; close any zombie CC/VS Code sessions and run `/doctor` before P4.
>
> ---
>
> 🟢 **RONDA-1 CATCH-UP + FINISH + MD2 SEED — CADENCE CONTRACT DONE (2026-06-16, branch `rho-fit`; engine FROZEN, live byte-identical, `rho_fit` OFF).**
> Data-ops only — **0 edits** to model/optimizer/strength/context/sigma/A2 (`git status` clean on all 6); I-3
> re-confirmed (backtest LEAKAGE=PASS). HITL respected (CC records, never enters pollaya). Plan:
> `…\plans\cadence-contract-bubbly-ripple.md`.
> **PART 0 — ingest/record (8 MD4/MD5 played games, dual-track):** GER-CUW 7-1, NED-JPN 2-2, CIV-ECU 1-0,
> SWE-TUN 5-1, ESP-CPV 0-0, BEL-EGY 1-1, KSA-URU 1-1, IRN-NZL 2-2. Entered = baseline for all except **NED-JPN
> entered 1-1 (override +4)**; **GER-CUW entered 3-0** (the Jun-14 4-0→3-0 revert held). **Cumulative n=16:
> Σus_model=28, Σus_entered=28, override=+0** = the observed pollaya board (us=28, rank 21/27) → **L25
> cross-check PASS**. **NED-JPN "fix" premise was FALSE** — its `result` was BLANK, never 1-1 (recorded 2-2;
> Gate-7 = the blank cell). **Standings S3 (Jun-16) ingested** (`standings/2026-06-16/standings.json`, board
> read off screenshots; us=28, rank 21/27, leader 44, podium_cut 42, gap_podium −14, override 0) →
> `standings_log.csv` = **2 rows (Jun-14+Jun-16) → F34 floor MET**. **S2/Jun-15 SKIPPED** (no board photos).
> review.ps1 → **0 played-unreviewed** (14 stamped). backtest re-run = deterministic reproduction: **HIGH-TOTAL
> PASS Δ+0.0809** [CI +0.0209,+0.1421], Brier 0.5792, exact-hit 0.1158, LEAKAGE=PASS, G-RHO2 still NO-PASS.
> **L29** (record the cross-checked final, not a remembered score; blank = safety net), **L30** (reconcile
> Σpts_entered vs the board; override=0 is a sum, not agreement), **L31** (4/4 MD5 draws → draw-lean
> counterfactual is variance not skill; I-NOTILT) logged.
> **PART 1 — cadence picks (Tue Jun-16 → Fri Jun-19 German, ONE API call):** fresh fetch
> `fetch_md1 --win-hi 2026-06-19T22:00:00Z` (quota **481→479**, ~2cr, snapshot `md1_2026-06-16T15-59-46Z.json`),
> 14 in-window. F27 diff: 8 existing (FRA-SEN→UZB-COL; fresh odds → **0 flips vs baseline**) + **5 NEW MD2
> BASELINES ADDED** (CZE-RSA 1-0, SUI-BIH 1-0, CAN-QAT 2-0, MEX-KOR 1-0, USA-AUS 1-0; `log_decision`+`backfill`,
> guards clean). **SCO-MAR EXCLUDED** (KO Jun-19 22:00Z = 00:00 CEST Saturday, past the Friday-German cutoff; in
> the snapshot, add on request). EV-argmax pass on all **13**: 0 coinflips, guards clean, ρ frozen −0.05
> (rho_fit OFF), context neutral. EV-vs-modal flip-watch: FRA-SEN, ARG-ALG, GHA-PAN, UZB-COL, MEX-KOR
> (lowest-conf = GHA-PAN, MEX-KOR, near-even). `decisions.csv` = **16 recorded + 13 pending = 29 rows**.
> **🛑 HITL STOP — 13 picks pending Sebas entry; nothing recorded for them.** Record post-match:
> `python -m src.decision_score record <fid> <H-A> --entered-pick <typed>`. **After the 8 Ronda-1 play+record →
> Ronda-1 = 24/24**; MD2 seeded through Fri Jun-19 German. Refresh K/L + MD2 before each 10-min-pre-KO deadline.
>
> ---
>
> 🟡 **L19 ρ-FIT BUILT + M7-VALIDATED — NO-PASS on the edge gate; kept BUILD≠FIRE (2026-06-14, branch `rho-fit` off master `05cde08`).**
> `fit_dc` (μ pinned from the totals price, solve `s←P_home` + `ρ←P_draw` by nested bisection, exactly identified;
> band-clamp [−0.20,+0.10]; gated `rho_fit`, **default-OFF → live path byte-identical**, suite **204/204**).
> Gate-7 RED→GREEN on KOR-CZE (pick 0-1→1-1, inversion cleared); G-RHO1 (same ρ live+backtest), G-RHO4 (OFF/ON
> test scoping), G-RHO5 (I3 grep-clean) all PASS.
> **M7 re-run verdict — G-RHO2 = NO-PASS:** outcome-hit-rate **0.5366→0.5336 (Δ −0.0030)** — the dominant 3-pt
> objective did NOT rise (neutral within noise). High-total edge +0.0809→+0.0779 (still PASS, narrower). exact-hit
> **+0.77pp** (0.1158→0.1235) and Brier 0.5792→0.5789 DO improve; favorite-inversion fixed; draw-rate 2.8%→9.0%
> (converges, no overshoot; empirical 25.3% — the rubric is structurally draw-averse). clamp 0.84%; LIVE board
> 0/16 picks changed. **L28** logged. **RECOMMENDATION: do NOT flip default-ON as an edge (there is none); keep
> gated OFF. The flip for the calibration/exact-hit/inversion-correctness value is Sebas's HITL call.** Committed
> on `rho-fit` (NOT merged). **Real top-3 torque now = field-DIFFERENTIATION only** (objective E[pts]→P(top-3));
> the per-match probability levers (dial L27, ρ-fit L28) are both E[pts]-inert.
> **FIELD-DIFF SPEC (post-MD3, build-ready) — SINGLE-ENTRY framing:** maximize P(top-3), NOT E[pts]
> (Clair-Letscher 2007, one bracket — `pool/` already maximizes E[prize]). On the *k* most near-even boards,
> deviate from the field's MODAL scoreline (chalk favorite-win) = CORRELATED upside, leapfrogs the whole field
> when right. Field = chalk PRIOR (per-match scorelines hidden). **Build = extend the existing
> `pool/pool_montecarlo.py` CRN E[prize] MC to per-match scorelines; compare {all-modal} vs {differentiate-on-k},
> pick the set maximizing P(top-3).** Do NOT implement Hunter-Vielma-Zaman's submodular portfolio algorithm —
> HVZ (2016) is a MULTI-entry (many-lineup) framework; we submit ONE entry, so it does not apply. HVZ/Metrick
> are the conceptual hook only (top-heavy payoff → field overbacks favorites → contrarian/correlated wins the
> upper tail). SELECTIVE + LATE (deviate only when `standings_log` shows you trailing — Dubins-Savage bold play /
> Brown-Harlow-Starks 1996: variance-seek when behind, in PLACEMENT space not self-SD).
> **BUILD ≠ FIRE — explicit windows (verified 2026-06-14: NEITHER built yet):**
> • **BUILD = ACCIONABLE PRE-MD3 (build-but-wait, needs its own GO).** Two pieces, both code-able + TDD-able NOW
>   with NO live data (scenario-band only, like the λ-dial was): (a) **H4/M5 re-anchor fix** — re-architect
>   `apply_context` to re-anchor μ PRE-DC (feed adjusted μ to `fit_dc`), Gate-7 RED first; today it is still the
>   post-DC tilt (`context.py:65-68`, warning lines 10-20). (b) **placement-MC machinery** — extend
>   `pool/pool_montecarlo.py` CRN to per-match scorelines, report a P(top-3) SCENARIO BAND for {all-modal} vs
>   {differentiate-on-k}. NEITHER exists (no `placement*.py`/`field*.py`; only the L27 λ-dial `variance_select.py`
>   is built — that is NOT field-diff).
> • **FIRE = POST-MD3 ONLY.** Activating a live differentiation pick needs ≥2-3 matchdays `standings_log` (the
>   trailing signal) + H4 fixed + an activation threshold. The BUILD does not wait for this; the FIRE does.
> RPS (Constantinou-Fenton 2012) = optional ordinal eval diagnostic,
> NEVER a gate (Wheatcroft 2021 contests it). DIBP (Karlis-Ntzoufras 2003) = the draws upgrade where ρ clamps
> (P_draw≳0.32); documented fallback only.
> **H4/M5 WATCH (pre-MD3):** context fix stays deferred (dormant under the live `neutral` flag) — but even
> `neutral` is NOT a perfect 1X2 identity: KOR-CZE draw 0.3107 (pre-M5) → 0.3009 (post-M5). Verify/close when
> H4 is fixed.
>
> ---
>
> 🟢 **TRACK-B DUAL-TRACK + MD1 CADENCE COMPLETE (2026-06-14, GATE 0–6, branch `track-b-dualtrack-md1-cadence`).**
> All on the FROZEN model — **0 edits** to model/optimizer/strength/context (`git diff --stat` clean). Suite
> **188/188** (172 + 16 new). Nothing entered/locked by CC.
> **DUAL-TRACK (additive schema 26→28: `entered_pick`,`pts_entered`):** recorded the 8 played MD1 games both
> ways. Anchor reconciles EXACTLY (auditor-verified, NOT massaged): **us_entered=15 · us_model=19 · B1=23 ·
> override=−4** (= real pollaya standing 15, rank 20/27, field median 19). Override damage is ONE fixture
> (HAI-SCO −5: entered 0-2, model 0-1 hit exact=9); USA-PAR +1; other 6 net 0. `summary` now labels us_entered
> (REAL) vs us_model (counterfactual) + the override line. **L26** logged.
> **CADENCE (F27 diff-driven · F29 conditional):** fresh fetch (`--win-hi 2026-06-18T03:00Z --expect 16`, quota
> 487→**481**, snapshot `md1_2026-06-14T12-14-52Z.json`) served all 16 unplayed → diffed ids vs decisions.csv →
> added the 8 Jun-16/17 rows on the frozen optimizer (guards clean ×8, determinism byte-identical, backfill
> idempotent). `decisions.csv` = **24 MD1 rows** (full MD1; IRN-NZL + UZB-COL present). F29 full-PASS branch.
> **STANDINGS:** new `decision_score standings <date>` (DETERMINISTIC stats, NO council) → `standings/standings_log.csv`
> first row (us=15, rank 20/27, median 19, mean 18.96, sd 5.69, z −0.70, pctl 0.30, leader 28, podium_cut 26,
> gap_median −4, gap_podium −11, override −4). Input `standings/2026-06-14/standings.json` (N=27).
> **🚨 TODAY's REVERT (Sebas types; CC never enters):** GER-CUW **4-0 → 3-0** (entered ≠ model EV-argmax; clear,
> high-confidence); NED-JPN **1-1 → 1-0** (judgment: 1-0 = EV-argmax, 1-1 = modal on a near-even board — keep 1-1
> only with a logged draw-thesis). CIV-ECU 0-1 / SWE-TUN 1-0 = model-aligned. Deadlines: GER-CUW 16:50Z,
> NED-JPN 19:50Z.
> **NEXT cadence (refresh before each 10-min-pre-KO deadline):** Jun-15 ESP-CPV 3-0 / BEL-EGY 1-0 / KSA-URU 0-1 /
> IRN-NZL 1-0; **Jun-16** FRA-SEN 1-0 / IRQ-NOR 0-2 / ARG-ALG 1-0¹ / AUT-JOR 2-0; **Jun-17** POR-COD 2-0 /
> ENG-CRO 1-0 / GHA-PAN 1-0¹ / UZB-COL 0-1¹ (¹ = EV≠modal flip-watch). Record results:
> `python -m src.decision_score record <fid> <H-A> --entered-pick <typed>`; cumulative via `… summary`; field via
> `… standings <date>`. **ANNEX V (build-but-wait): SKELETON DONE (commit `2ce2c8c`)** — λ-dial
> `src/variance_select.py` (pure selection layer, lam=0 ≡ optimizer, default-OFF `run_matchday` hook, 0 frozen
> edits) + `evals/variance_ev_cost.py`: REAL per-game EV-cost ≈ **+0.004–0.011 pts** (max 0.058, moves 5/16,
> saturates by lam=1) — ~40× SMALLER than the stylized −0.4 (the rubric CAPS achievable variance: the tilt only
> bumps a favorite win up one goal, e.g. 1-0→2-0). **RE-SCOPE (L27):** the deferred placement-MC must test
> **FIELD-DIFFERENTIATION** (deviate from the field's likely modal pick on near-even matches = correlated
> upside, beats the whole field at once when right), NOT the mean-variance dial (per-match SD is the WRONG
> proxy for P(top-3); the dial is low-torque/net-wash). DEFERRED post-MD3: placement-MC (field-diff) +
> eval-panel + activation gate (F35 H4-fixed; F34 ≥2–3 matchdays of standings_log).
> **NEXT ENGINEERING GO (await Sebas) = the real top-3 ROI:** the **L19 ρ-fit/H4/M7 engine bundle** (fixes
> draw-compression + favorite-inversion → raises outcome-hit-rate directly, the 3-pt component that dominates
> scoring; naturally aligns with the post-MD3 H4 activation window).
> 🟢 **MERGED to master** 2026-06-14 (commit `c6aaf6d`, F32 HITL exception = Sebas's explicit GO; post-merge
> verify: 196/196, frozen diff EMPTY). Branch `track-b-dualtrack-md1-cadence` retained.
> Output: `predictions/2026-06-14/summary.md`.
>
> ---
>
> 🔴→🟢 **F23 CORRECTION (2026-06-12, Sebas audit).** The weekend run below claimed "all 7 remaining MD1
> fixtures" — **FALSE.** The denominator is the FIFA calendar: **MD1 = 24 matches** (48 teams), so 2 played +
> 13 snapshot = 15 covered → **9 missing, not 7.** Root cause: the "4 Sunday vs 7 remaining?" scope question
> derived its denominator from a probe of the **same `/events` window being audited** (circular); compounded by
> CLAUDE.md's wrong "MD1 Jun 11–15" (real: Jun 11–18). The 9 missing (chronological MD1 #14–22):
> **IRN-NZL** Tue Jun-16 01:00Z · FRA-SEN Jun-16 19:00 · IRQ-NOR Jun-16 22:00 · ARG-ALG Jun-17 01:00 ·
> AUT-JOR Jun-17 04:00 · POR-COD Jun-17 17:00 · ENG-CRO Jun-17 20:00 · GHA-PAN Jun-17 23:00 · UZB-COL
> Jun-18 02:00. **IRN-NZL was the live risk** (deadline Mon-night 00:50Z, ~3h after KSA-URU) — now ADDED as
> BASELINE **1-0** (E=2.910, aligned; williamhill; snapshot `md1_2026-06-12T17-36-02Z.json`, quota 487→**483**).
> `decisions.csv` now **16 rows**; recorded n=2 (us=5/B1=8/B2=5) UNCHANGED. The other **8 (FRA-SEN→UZB-COL) are
> the Tue Jun-16+ cadence batch** (NOT this weekend; see Other open items). Fixes: CLAUDE.md §Data refresh-
> completeness rule (probe `/events` ~72h + diff vs decisions.csv; `--expect` from calendar not same-endpoint
> probe — F24) + MD1 date corrected + **L25** logged. (F25: CIV-ECU = priority flip-watch on cheap late
> re-check. F26: GER-CUW/ESP-CPV 3-0 are totals-line-sensitive — a totals move can legitimately flip 3-0↔2-0,
> odds-driven not a bug. Türkiye/Turkey pollaya-dropdown spelling still open for AUS-TUR Sat.)
>
> ---
>
> 🟢 **WEEKEND MATCHDAY CADENCE RUN DONE (2026-06-12).** Resumed the per-fixture refresh on the corrected
> optimizer (exact=3). (1) **Closed today's 2 picks** on fresh Jun-12 odds: **CAN-BIH 1-0** (E=2.953,
> aligned) and **USA-PAR 1-0** (E=2.678, EV-vs-modal gap persists) — both **STAND vs BASELINE, no change**;
> the only Jun-11 flip candidate (USA-PAR) did NOT flip. EDIT-only-on-change → no `decisions.csv` mutation
> for the unchanged picks. (2) **Closed the MD1 coverage gap:** `src/fetch_md1.py` window/count were
> hardcoded (`WIN_HI=2026-06-14T06:00Z`, expect 8), silently dropping later MD1 fixtures (this run added 7;
> the true gap was 9 — see F23 correction above). Added
> `--win-hi`/`--expect` + a pure `filter_window()` (TDD: `tests/test_fetch_md1.py`, defaults byte-identical;
> suite **172/172**, was 165 + 7). Fresh fetch `--win-hi 2026-06-15T23:00Z --expect 13` (quota 487→**485**,
> 2 cr) → snapshot `data/snapshots/md1_2026-06-12T17-10-37Z.json` (13 unplayed fixtures; MEX/KOR played &
> dropped). Added 7 BASELINE rows (GER-CUW 3-0, NED-JPN 1-0, CIV-ECU 0-1, SWE-TUN 1-0, ESP-CPV 3-0, BEL-EGY
> 1-0, KSA-URU 0-1) + backfilled forecast cols → `decisions.csv` **15 rows** (→**16** after F23 added IRN-NZL); recorded n=2 (us=5/B1=8/B2=5)
> UNCHANGED. All 13 guards clean (neutral×13, x.5×13, intra-book×13, L17 clean×13). **Flip-watch (EV≠modal):
> USA-PAR, NED-JPN, CIV-ECU.** Output `predictions/2026-06-12/summary.md`; refresh table below extended through
> Mon Jun-15. 🛑 Nothing entered/locked by CC. **NEXT: Sat ~18:00 UTC refresh** (QAT-SUI/BRA-MAR/HAI-SCO/AUS-TUR).
>
> ---
>
> 🟢 **TRACK-B OBJECTIVE-FUNCTION FIX + EXECUTION-DISCIPLINE LOOP DONE (2026-06-12).** Two gated phases,
> both auditor-checked.
> **PHASE 1 (GATE 1 PASS, commit `3778c4c`):** fixed a silent objective bug — optimizer paid EXACT-SCORE
> `+2` but pollaya pays `+3` (max/match 8→9). RED→GREEN minimal diff (`src/optimizer.py:23` 2→3 + 3 exact
> test assertions 8→9 + new GD-proof test; 3 non-exact locked tests stay 4/4/4). Backtest regenerated under
> exact=3 (det.): verdict STILL PASS, edge WIDENED (high-total Δ +0.0621→+0.0809), Brier 0.5792 unchanged.
> Forensics: 0/6 weekend flips, MEX-RSA argmax stays 1-0 (bug cost 0 realized points). **L23** logged.
> **PHASE 2 (GATE 2 — auditor verdict PENDING, commit `<this>`):** `src/decision_score.py` (new) +
> `decisionlog` schema (13→26 cols, `migrate_schema`/`update_decision`) + `review.ps1` 3-way + `-Mark`.
> Backfilled 8 fixtures (forecast cols) + recorded the 2 played: **MEX-RSA 2-0, KOR-CZE 2-1**. Cumulative
> n=2: **us=5, B1=8, B2=5** (us−B1=−3, us−B2=0), mean Brier **model=0.3828 (PRIMARY, F12 model-health)** /
> market=0.3817 (secondary input-cal; auditor's 0.3818 used 3dp inputs — 0.0001 reconciliation). Small-n
> caveat enforced. **I3 guardrail** in CLAUDE.md + grep-clean (no result→model path; F14 max-8 grep clean —
> `MAX_GOALS=8` is the goal grid, not the points ceiling). **L24** logged. Suite **165/165** (151 + 14 new).
> **NEXT: GATE 2 auditor verdict + Sebas GO. Then resume the MATCHDAY cadence below** (weekend BASELINE
> refreshes now run on the corrected optimizer; record results via `python -m src.decision_score record
> <fixture> <H-A>` as matches finish; `review.ps1 -Mark` to close them). Pending engine GO (post-MD, L19):
> ρ-fit + H4 + M7 re-run.
> **🟡 PRE-MD3 WATCH (auditor carry-forwards, GATE-2 PASS):** (F17) `brier_model` reads the PRE-context DC
> matrix, so it is BLIND to an H4/M5 corruption (lives only POST-context; dormant until ~MD3, Jun 24–27).
> Verified pre≠post even on MD1 (neutral = `var_x1.06`, NOT a no-op — corrects the auditor's F18 premise;
> MEX brier 0.1611 pre vs 0.1654 post). **Before MD3 / before H4 wakes: add a POST-context model-Brier**
> (pre+post) — the only metric that flags an H4 regression. Bundle with the L19 ρ-fit+H4 GO. (F18 doc fixed
> in `decision_score.py`; F19 I3 grep extended to `pool/` = clean.) (B1 draw-favoured case is DEFINED, not
> deferred — backs the win-favourite 1-0/0-1, never X; no MD1 fixture is draw-favoured.)
>
> ---
>
> 🟢 **TRACK-B MATCHDAY-1 RUN DONE (2026-06-11, P0–P6).** Repo now git-init'd (6 commits, `.env` ignored,
> frozen files byte-identical to baseline `5d2f645`). Suite **150/150** (145 + 5 L17-guard tests). Single
> fresh fetch (quota 489→487) → snapshot `data/snapshots/md1_2026-06-11T16-01-57Z.json` → 8 replays
> (determinism byte-identical, NEUTRAL×8, x.5×8, intra-book×8). **L17 favorite-inversion guard** added
> (output-layer, detection-only, `src/run_matchday.py`). New lessons **L20/L21/L22**.
> **ENTERED tonight (Sebas, manual):** MEX-RSA **1-0** (FINAL) · KOR-CZE **1-1** (FINAL, HITL override of
> as-built argmax 1-0 — gap 0.025<noise, inversion CLEARED on fresh odds). **BASELINE (NOT entered, refresh
> per fixture):** CAN-BIH 1-0, USA-PAR 1-0, QAT-SUI 0-2, BRA-MAR 1-0, HAI-SCO 0-1, AUS-TUR 0-1.
> **Refresh windows (contract §5, re-run `fetch_md1` + replay that day's fixtures, diff vs BASELINE, EDIT only on change):**
> Fri ~18:00 UTC → CAN-BIH (18:50), USA-PAR (00:50 Sat) — **DONE Jun-12: both 1-0 STAND** · Sat ~18:00 UTC →
> QAT-SUI (18:50, 0-2), BRA-MAR (21:50, 1-0), HAI-SCO (00:50 Sun, 0-1), AUS-TUR (03:50 Sun, 0-1) · **Sun ~15:00 UTC**
> → GER-CUW (16:50, 3-0), NED-JPN (19:50, 1-0¹), CIV-ECU (22:50, 0-1¹), SWE-TUN (01:50 Mon, 1-0) · **Mon ~14:00 UTC**
> → ESP-CPV (15:50, 3-0), BEL-EGY (18:50, 1-0), KSA-URU (21:50, 0-1), **IRN-NZL (Tue 00:50Z, 1-0 — F23 add;
> widen `--win-hi ≥ 2026-06-16T02:00Z`)**. ¹=flip-watch (EV≠modal; CIV-ECU = priority on a cheap late re-check, F25).
> Record: `predictions/decisions.csv` (**16 rows**, utc=KO) + `predictions/2026-06-1{1,2}/summary.md`. **Pending
> engine GO (post-MD, L19):** ρ-fit root fix + H4 + M7 re-run.

---

# HANDOFF — PODIUM LOCK RUN v3 COMPLETE (2026-06-10, decision-grade) → awaiting Sebas's manual lock

> ✅ **LOCK RUN DONE (Steps 0–8, GO#1 + GO#2 granted). RECOMMENDATION — NOT A LOCK.** Decision-grade run on
> FRESH odds (DraftKings, LM9 sportsbook basis) + EMBEDDED FINAL ownership (N_opp=24, Sebas's 18:35
> screenshots, exact §3-D4 match). Suite **145/145 GREEN**; A2 K=1 anchor byte-exact; **deterministic +
> PYTHONHASHSEED-invariant**; no-edit proof (A2/fit_lambdas/M7/H4 SHA256 unchanged vs
> `data/snapshots/lock_run_noedit_baseline_2026-06-10.json`). Spend ≈ 2 cr Odds-API (489 remaining).
>
> ## FINAL RECOMMENDATION (5 picks — Sebas types into pollaya, EXACT spelling; champion + 5 OPEN until he locks)
> | lever | pick (pollaya) | basis | currently on pollaya |
> |---|---|---|---|
> | **champion** | **España** (Spain) | chalk; England/Argentina contrarians REJECTED (flip ΔE<0 at every σ∈[2,20]) | Curazao → CHANGE |
> | **top_scorer** | **Kylian Mbappé** | chalk (fav +600; no scorer clears P>0.08) | Harry Kane → CHANGE |
> | **mvp** | **Harry Kane** | Kane=Yamal +800 single-book TIE; Kane 0-owned vs Yamal 9 → **engine ΔE(Kane−Yamal)=+0.0025 ±0.0005(2·SE), materially better** | Kylian Mbappé → CHANGE |
> | **best_gk** | **Emiliano Martínez** | chalk = leverage: fav +430 AND 0 opp owners | Emiliano Martínez → no change |
> | **assister** | **Bruno Fernandes** | K=4 chalk-manual (board flat, K-gate failed, no fabricated P_true FM3) | Bruno Fernandes → no change |
>
> **Verdict = ALL-CHALK + Kane(MVP).** Every contrarian was *identified* (England lev 3.17, Argentina 2.69,
> all clear the 0.08 gate) but *rejected on economics*: at calibrated σ≈14 a single 10-pt lever is swamped by
> the ±14 tournament-total noise, so higher win-prob (chalk) wins — flips are NEGATIVE at every σ (determinate,
> not σ-dependent). MVP=Kane chosen by Sebas (GO#2): the crowd over-piled on Yamal at IDENTICAL odds, leaving
> a 0-owned co-favourite as free leverage.
>
> ## HONEST CAVEAT (named, bounded, does NOT reverse — Sebas, GO#2)
> The engine treats levers as **independent**; in reality MVP↔champion **correlate** (Spain champion → a Spanish
> MVP, i.e. Yamal, is likelier). Yamal+Spain *concentrates* correlated upside; Kane+Spain *diversifies*. Net
> direction is **ambiguous and second-order** vs the first-order collision dominance (9 vs 0 owners) — and
> plausibly *reinforces* Kane, since the 9 Yamal-owners are largely the same worlds where Spain wins, so
> Yamal+Spain buys REDUNDANT collision (no separation) while Kane is a unique separator. Stylization is
> documented (`podium_montecarlo` docstring §2.6/PA7). Doesn't change the pick.
>
> ## 🔴 BINDING PRE-LOCK GATE (Sebas, GO#1 — the most important gate of the run)
> The 18:35 snapshot PRODUCES the recommendation but does NOT replace the final re-count. **Immediately before
> locking by hand, re-confirm: (1) N_opp still = 24, (2) nothing dramatic shifted.** NOTE: because the
> recommendation is ALL-CHALK (not a contrarian leverage play), it is ROBUST to ownership drift — the 0-owned
> England/Argentina condition is no longer load-bearing for THIS portfolio (the contrarians lose on economics
> regardless of ownership). Re-confirm N_opp mainly. HARD STOP: never race the Jun-11 19:00 UTC opener; if a
> Jun-11 AM re-run can't finish with buffer, the Jun-10 recommendation STANDS (re-run protocol §11, idempotent).
>
> ## Artifacts this run
> - Code (lock-run extensions, NOT frozen files): `pool/podium_montecarlo.py` (+`return_sim_vectors` SE_diff),
>   `pool/run_podium_draft.py` (`--lock-run`, σ-bracket matrix, 2·SE+A4+R9-lock+≤1-contrarian verdict layer),
>   `council/run_council.py` (`market_p_true(path=)`), `pool/fetch_outrights.py` (NEW; A1 probe + F2P1),
>   `pool/build_lock_props.py` (NEW; Jun-10 prop boards), `pool/ingest_ownership.py` (L18 determinism fix).
> - Data: `data/outrights_2026-06-10.json` (DraftKings primary, Betfair crosscheck), `data/props_*_2026-06-10.json`,
>   `data/snapshots/observed_ownership_2026-06-10.json` (N_opp=24), `data/snapshots/lock_run_noedit_baseline_2026-06-10.json`.
> - Lessons: **L18** (RNG-fed dict order must be sorted, not a bare set — PYTHONHASHSEED), **L19** (F2P1 =
>   most-complete *sportsbook* board; don't bake a favourite into the contract; 3-way verdict labels).
> - Re-run: `python pool/run_podium_draft.py --lock-run` (deterministic). Re-fetch fresh: `python pool/fetch_outrights.py`.
>
> 🛑 No pick LOCKED by CC. Sebas locks manually on pollaya before Jun-11 19:00 UTC.

---

# HANDOFF — resume point for next session (updated 2026-06-02, Steps 4–7 DONE)

> ✅ **PHASE COMPLETE (Steps 0–7).** A2 `pool/pool_montecarlo.py` built + verified (selftest GREEN:
> chalk→Fav, flip→Dark; deterministic; A1 T1–T7 still OK). `pool/decision_clock.md` written (INVARIANT/
> TIME-DEPENDENT + PB1–PB5 + lock schedule; grep tokens PASS). L5 logged in `tasks/lessons.md`.
> **▶ TRACK-B (2026-06-03): P0–P3 DONE.** Per-match EV engine, the ~88%-of-points lever (L6).
> **P3 M7 backtest = SUCCESS-PROOF: VERDICT = PASS (Gate-A).** `evals/backtest.py` +
> `evals/fetch_footballdata.py` + `tests/test_backtest.py` (full suite **69/69 GREEN**). EV vs B1 on
> football-data.co.uk top-5 EU × 5 seasons (8955 rows). HEADLINE (home-zeroed δ=0.30, OPENING, EX-COVID):
> **HIGH-TOTAL Δ=+0.0621 pts/match, 95% CI [+0.0139,+0.1115], n=3300 → PASS**; low-total NO-EDGE =
> MEASURED ~0, NOT an identity (3.4% diverge, EV→1-1; draw-modal n=0 is SILENT, not confirmatory);
> calibration beats uniform; PASS across all sensitivity rows; leakage PASS. Result =
> `evals/backtest_results.json`; plan = `…\plans\foamy-spinning-pebble.md`. Spec corrections this session
> (all FROZEN before reading, anti-FM1): M7-iii segmentation driver = TOTAL level only (away-fav gap-0);
> headline EX-COVID; δ = empirical home-goal-diff (not Elo); **M7 design v = μ_eff signal-recovery**
> (football-data pins line=2.5 → M3 was totals-blind; invert p_over→μ_eff in evals/ ONLY; L11).
> **P4b σ-calibration — DONE 2026-06-06** (`pool/sigma_calibration.py`, suite 95/95). σ_cal=13.78 (σ_lower
> 13.78 [CI 13.52,14.03]; σ_upper 24.93 [24.47,25.38]) derived from M7 variance as a RUNTIME value (model
> declared first in rules.md, anti-FM1). **Verdict = SIGMA_DEPENDENT_UNDER_LEVERAGE (L13):** the bracket
> clears the stylized ~σ7–8 flip (→ robust_chalk) BUT the real K=4 engine under starve stays contrarian_2 at
> BOTH σ endpoints → chalk-vs-contrarian DEFERS to OBSERVED Jun-10 ownership. A2 BASE_SIGMA=6.0 FROZEN
> (anchor PASS); σ_cal injected into `run_podium_draft.py` via `read_sigma_cal()`; M7 JSON sha-unchanged.
> **P4a μ_eff→src/ — DONE 2026-06-06** (suite 104/104). The ONE μ_eff model (`mu_from_pover`+`poisson_over_prob`)
> MOVED into `src/model.py`; `evals/backtest.py` re-imports it byte-identical (I4, no second model);
> `match_distribution` now consumes `p_over` (fed to the FROZEN `fit_lambdas` as the line, mirroring
> `fixture_eval`). totals-blind RED→GREEN; byte-equal on 3 fixtures; **M7 UNCHANGED** (deltas exact + JSON sha
> `8273f095…`); src/ offline-pure; A2/`pool/` + `fit_lambdas` untouched. The live WC engine now carries the
> totals-aware μ_eff edge M7 proved (completes L11's registered fix).
> **P4c DONE 2026-06-06 (suite 121/121):** **M8 `src/run_matchday.py`** orchestrator M1→M2→[x.5 guard]→
> M3(μ_eff)→M5→M4→summary; HITL STOP (--submit disabled); dry-run prints table+EV pick+EV-vs-modal gap
> +sources/flags+STOP; <60s/match (3.2s); offline-pure (no evals, test-asserted); snapshot-reproducible
> (byte-identical). Per-match argmax σ-INDEPENDENT. + `src/lines.is_half_line` + `src/probe_lines.py` (P4c-0)
> + `tests/test_run_matchday.py`. **H3 book-selection DONE 2026-06-06 (Option A, RB3-strict):** `parse_event`
> prefers ONE book with h2h + x.5 totals (intra-book μ_eff); else first-h2h book + totals-blind + HARD flag
> (`match['book_selection']`, never silent); NEVER cross-book (safety assertion). **Per-match coverage = 100%
> (72/72)** → totals-blind rarely fires; the prior NON_X5_PRESENT gate is RESOLVED. x.5 guard kept as
> defense-in-depth. **🛑 NEW OPEN ITEM — H4 (separate GO):** M5 `context.apply_context` adjusts POST-DC; the
> var-temper on a right-skewed matrix pushes the mean UP and overwhelms mu_factor → non-neutral flags
> MIS-DIRECT the mean (rotation +0.179, dead_rubber +0.131 move UP; neutral +0.069). Live default=neutral
> (tolerable); non-neutral flags NOT live-safe until M5 re-anchors μ PRE-DC (WARNING + pinned tests).
> F1 kickoff VERIFIED; F2 'contrarian'→'EV-vs-modal gap'. Gate-A ≠ Gate-B
> (L9): M7 PASS proves implementation + an in-distribution edge, NOT a WC edge (RB2) NOR DC-necessity.
> **PODIUM TEST RUN — DONE 2026-06-06 (suite 137/137):** observed-ownership rehearsal of the Jun-10 lock.
> `pool/ingest_ownership.py` Laplace floor (denom=N_opp, K_cand=top6∪observed, α=1; blanks→`_SENTINEL` so the
> dict sums to 1 — the joint MC re-normalizes internally, **L15**) + `load_observed_from_snapshot` (Sebas
> excluded; P2-b off-board→fold+log, not fabricate) + observed `[OBS]` block in `run_podium_draft.py` +
> `data/snapshots/observed_ownership_2026-06-06.json` (N=20→N_opp=19) + `tests/test_observed_ownership.py`
> (16 tests). **σ-verdict resolved-PRELIMINARY = STILL-SIGMA-DEPENDENT / INDETERMINATE:** at σ=13.78 Model A
> (blanks score 0) recommends a 1-lever contrarian (MVP Harry Kane) but Model B (blanks~P_true) → all-chalk;
> the **MVP lever FLIPS A↔B → INDETERMINATE, deferred to Jun-10** (Step-5b/FIX-1). Assister advisory-only
> (Bruno Fernandes most-owned, NO P_true, K=5 gate=Jun-10 probe). A2 BASE_SIGMA=6.0 byte-exact; σ/α untuned.
> ownership_source=observed but PRELIMINARY (n=4–7 deciders, selection-bias). NOT A LOCK.
> A3 council + other-4-picks (DoD-3) DEFERRED by point-value. The **Jun-10 evening** lock still stands
> (Jun-12 VOID). 🛑 No pick LOCKED;
> champion OPEN; A2 `pool_montecarlo.py` FROZEN.
> Re-verify anytime: `python pool/pool_montecarlo.py --selftest` · `python -m unittest discover -s tests`.

<details><summary>Original Step-4 resume spec (kept for audit — now satisfied)</summary>


> **Read this first, then `tasks/todo.md`, `CLAUDE.md`, `memory/rules.md`, `tasks/lessons.md`, and the
> plan `C:\Users\Sdami\.claude\plans\master-prompt-contract-lively-dusk.md` (§ "PARADIGM SHIFT → OBSERVED
> + A2 + DECISION CLOCK").** Everything below is deterministic — no thread is lost.

## 🛑 HARD GATES (do NOT violate)
- **NEVER LOCK any pick.** Champion is OPEN (Brazil in pollaya = PLACEHOLDER). The real decision run is the
  **Jun-10 EVENING lock** (one safe day before the Jun-11 first match; Jun-12 is VOID), on FRESH odds + FINAL
  observed ownership. HITL: recommend, Sebas locks.
- **`prior` is still `is_gated`.** Finalize only on measured (`observed`/`polled`) + HITL.
- **No bespoke ML; stdlib + (numpy optional); fixed seeds; provenance on every datum.**

## Paradigm shift (now FACT, pollaya screenshots 2026-05-30 / confirmed 2026-06-02)
- Premiation/locked picks (champion/scorer/assister/MVP/GK) ARE visible → `PICKS_VISIBLE=True`; `observed`
  ownership is REAL. Per-match scorelines HIDDEN → per-match ownership = prior only.
- **N = 12 today → TIME-DEPENDENT → ~20–25 final.** Lock **Jun-10 evening**; hard backstop = first match Jun-11 (Jun-12 VOID). Symmetry
  (opponents see your pick) → last-mover edge is HIGH in a low-sophistication pool (captures the
  non-strategic majority; residual uncertainty = the 1–2 sharps).
- Observed today: 2/12 locked (Pireli18→Uruguay; **Damiani=Sebas→Brasil = PLACEHOLDER**), 10 pending.
  **Self-exclude Sebas** from the field denominator → today's field = {Uruguay:1.0}, n=1 (noise; late-bind).
- Rubric re-confirmed (Image 3) — no optimizer change.

## ✅ DONE this phase (verified — re-confirm with the commands)
- **Step 0 docs reconcile** — `memory/rules.md` + `CLAUDE.md §7d`: PICKS_VISIBLE=True, N=12→20–25, lock
  Jun-10 evening (hard backstop = first match Jun-11; Jun-12 VOID), symmetry.
- **Step 1+2 — `PICKS_VISIBLE=True` flip (TDD)** in `pool/leverage.py`; rewrote T6 (observed runs w/
  override; w/o → ValueError) + added T7 (`is_gated`: prior→True, observed/polled→False) + `is_gated()`.
  Evidence-driven test rewrite, NOT FM1 (log as L5 in Step 7).
  - re-verify: `python -m unittest discover -s tests -v` → **T1–T7 OK**.
- **Step 3 — `pool/ingest_ownership.py`** (`load_observed(picks, n_total, exclude=None)`): ownership over
  LOCKED opponents only (self-excluded), + locked/pending counts + provenance.
  - re-verify: `python pool/ingest_ownership.py` → PASS (no-exclude: 2 locked/10 pending/sums to 1;
    exclude='b': {Uruguay:1.0}, 1 locked/10 pending).
- 3 plan nits folded (A2 bullet → observed-primary/N 12→20–25; PB4 softened; PB1 → "FM2:
  stale-value-as-current").

## ▶ RESUME HERE — PENDING (Steps 4–7), in order

### Step 4 — `pool/pool_montecarlo.py` (A2)  ⟵ START HERE
E[prize] per CHAMPION candidate; argmax = recommendation. Champion = one ~10-pt lever among ~300–500 pts.
**Design (build deterministically):**
- Model: player score = `base ~ Normal(0, BASE_SIGMA)` + `10 if their champion pick == true champion T*`.
  `T* ~ Categorical(P_true)`.
- **Common Random Numbers across candidates** (variance reduction → decisive argmax): per sim draw
  (T*, my base noise, each opponent's pick + noise) ONCE; evaluate every candidate on that same draw with
  `my_total = my_noise + (10 if cand==T* else 0)`. rank = 1 + #{opp_total > my_total}.
- `E[prize|cand] = mean( 0.6 if rank==1, 0.2 if ==2, 0.1 if ==3, else 0 )`. argmax over candidates.
- Opponents = `N_final − 1` (exclude self). LOCKED opponents ~ observed `ownership`; PENDING opponents ~
  `pending_prior` (default = ownership or chalk prior) — **SIMULATION ONLY, never to choose your own pick**.
- Params: `DEFAULT_SEED = 20260602` (fixed, documented — do NOT use Date/random-based seeds);
  `BASE_SIGMA ≈ 8–12` (stylized spread; DOCUMENT as a modeling assumption to calibrate from backtest
  variance later); `n_sims ≈ 30000`. Accept `ownership_source ∈ {observed, prior}`.
- **`--selftest` = TWO scenarios (FM1 guard; a single scenario is a latent gap).** Use SYNTHETIC clean
  P_true so the engine-logic test is unambiguous (NOT a real-data claim):
  - `P_true = {Fav:0.40, Mid:0.25, Dark:0.20, Rest:0.15}`; candidates `[Fav,Mid,Dark]`; `N_OPP = 11`.
  - **(a) chalk:** ownership ∝ P_true → **argmax == Fav** (favorite; efficient field → chalk at small N).
  - **(b) flip:** ownership `{Fav:0.60, Mid:0.33, Dark:0.02, Rest:0.05}` (chalk OVER-owned, Dark
    UNDER-owned) → **argmax == Dark** (contrarian pays when chalk is over-owned).
  - Print E[prize]/candidate + seed; assert both. **TUNE BASE_SIGMA empirically** so both pass decisively
    (lower sigma ⇒ champion lever more decisive ⇒ amplifies ownership effect; start ~8–10). If (b) doesn't
    flip, over-own chalk more / lower sigma.
- **Real-data caveat (write in the file):** with actual WC-2026 odds, Spain/France/England cluster near
  Brazil (≈11–15% vs 9.8%) → Brazil is NOT a clean contrarian; the synthetic selftest tests ENGINE LOGIC.
- Reuse `pool/leverage.py`: `compute`, `american_to_prob`, `devig`, `load_outrights` for real P_true.
- verify: `python pool/pool_montecarlo.py --selftest` → chalk→Fav AND flip→Dark, prints seed + E[prize].

### Step 5 — `pool/decision_clock.md`
The INVARIANT vs TIME-DEPENDENT table (with PB1–PB5 baked in), lock schedule, optimization rule. Content
is fully specified in the plan's PARADIGM-SHIFT §Step 5 + §"My pushback". Key reclassifications vs the
original order:
- **P_true:** mechanism INVARIANT / **value TIME-DEPENDENT** (re-fetch fresh odds at snapshot; FM2).
- **N:** top-line TIME-DEPENDENT driver (12→20–25): scales ownership denominators + shifts chalk/contrarian regime.
- **Decision-rule:** structure INVARIANT / **N-calibration TIME-DEPENDENT**.
- **Last-mover:** HIGH value (captures non-strategic majority); residual uncertainty = 1–2 sharps.
- Schedule: now→Jun2 build invariants + ingest; Jun2 squads (other-4 P_true); **Jun 9 REHEARSAL**;
  **Jun 10 evening lock**; first match Jun-11 = NEVER race (Jun-12 VOID).
- verify: Grep `INVARIANT|TIME-DEPENDENT|Jun 10|Jun 11` ≥1 each.

### Step 6 — Pushback gate
Already satisfied (PB1–PB5 in the plan + this handoff + decision_clock). Emit/keep the reasoned verdict.

### Step 7 — Log L5 + STOP
Append to `tasks/lessons.md`:
> **L5 — An empirically-verified assumption can be FALSIFIED by new platform evidence (caught 2026-06-02).**
> PICKS_VISIBLE flipped False→True via pollaya screenshots. Rewriting the encoding test (T6) to the NEW
> contract WITH the evidence cited = reconciliation, NOT FM1 test-gaming. Distinguish: editing a test
> because reality changed (legit) vs to dodge a real failure (banned). (FM-taxonomy: FM1 false-positive;
> FM2 stale-value-as-current.)

Then STOP — do not build A3 / Track B / lock anything without a new go.

</details>

## Other open items (not this phase)
- **🟡 NEXT CADENCE BATCH — MD1 #15–22 (Tue Jun-16 → Thu Jun-18), 8 fixtures still BASELINE-pending** (F23
  denominator): FRA-SEN (Jun-16 19:00), IRQ-NOR (Jun-16 22:00), ARG-ALG (Jun-17 01:00), AUT-JOR (Jun-17 04:00),
  POR-COD (Jun-17 17:00), ENG-CRO (Jun-17 20:00), GHA-PAN (Jun-17 23:00), UZB-COL (Jun-18 02:00). Run a Tue
  ~14:00 UTC cadence: `fetch_md1 --win-hi 2026-06-18T03:00:00Z --expect 22` (calendar-derived) → add the 8 +
  backfill → diff `/events` vs decisions.csv (CLAUDE.md §Data rule). After MD1#22, MD2 begins (Czech-RSA Jun-18
  16:00). This completes MD1 = 24.
- **A3** council (5 isolated Sonnet lenses + synthesis) — after A2. Can run now (Jun 2 squads out) but
  champion lens only needs odds; scorer/MVP/GK need the published squads.
- **Other 4 locked picks** (scorer/assister/MVP/GK) — squads published 2026-06-02; build their P_true source
  (player props / web) after A2.
- **Task #7** — Track-B per-match odds source still OPEN (paid API-Football | The Odds API |
  football-data.org | web fetch). API-Football FREE cannot serve WC-2026 (L3).
- `pool/poll_champion.md` — SUPERSEDED for champion (observed ≫ polled); keep as fallback only.

## File map (Track A / pool engine)
- `pool/leverage.py` — de-vig → P_true → leverage SCREEN; `compute()`, `is_gated()`, `PICKS_VISIBLE=True`.
- `pool/ingest_ownership.py` — observed picks → ownership (self-exclude) + pending. [Step 3 ✓]
- `pool/pool_montecarlo.py` — A2 E[prize] engine (CRN, seed 20260602, BASE_SIGMA 6.0, opponent groups,
  2-scenario selftest, gated demo). [Step 4 ✓]
- `pool/decision_clock.md` — INVARIANT/TIME-DEPENDENT map + PB1–PB5 + lock schedule. [Step 5 ✓]
- `pool/poll_champion.md` — superseded fallback.
- `data/outrights.json` — web-sourced WC-2026 outrights (FanDuel 48 + DraftKings 21, 2026-05-29). NOTE:
  cached; **re-fetch fresh at the Jun-10 snapshot** (FM2).
- `tests/test_leverage.py` — Gate-7 (T1–T7).
