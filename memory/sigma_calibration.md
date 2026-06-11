# sigma_calibration.md - computed P4b σ-cal value (HITL-readable; runtime-injectable)

> Computed by pool/sigma_calibration.py AFTER the model was declared in memory/rules.md
> (P4b block, SIGMA_CAL_MODEL: declared). Read at run-time by read_sigma_cal(); runtime
> callers pass sigma=read_sigma_cal(). A2 BASE_SIGMA=6.0 stays FROZEN (I1). NOT A LOCK.

SIGMA_CAL: 13.7782

> PRECISION CAVEAT - do NOT over-read '13.78' as 2-decimal-precise. The DOMINANT
> uncertainty is the divergence prior d (a prior on a HIDDEN quantity), NOT sampling noise.
> σ_cal d-DRIVEN RANGE = [6.2, 19.5] over d in [0.10, 1.00]; 13.78 is ONLY the d=0.50 point.
> The bootstrap CI [13.523, 14.029] (width ~0.5) is ~26x NARROWER than the d-range
> (width ~13) -> it is NOISE relative to d-uncertainty. f_div=0.611 is itself a
> BORROWED PROXY (high-total MATCH fraction != player-DIVERGENCE rate). Read σ_cal as
> 'order ~14, plausibly 6-20', resolved by OBSERVED Jun-10 ownership - not a fixed point.

## Computation log (deterministic; seed=20260603, n_boot=5000)
- basis: run_backtest(NONCOVID, delta=0.3, basis='opening'); n_fixtures=5402
- s_pm: ev_pts=2.4444 CI [2.399, 2.489] (PRIMARY=conservative) > b1_pts=2.3993 (chalk cross-check)
  -> ev>b1 SHOWN (not asserted): ev_pts is the larger/safer σ. means ev_pm=2.7105, b1_pm=2.6751
- σ_upper = √104·s_pm = 24.928  CI [24.466, 25.382]   (iid; ceiling)
- σ_lower = √(104·0.611·0.5)·s_pm = 13.778  CI [13.523, 14.029]   (differential-only; floor)
- bracket (widest) = [13.523, 25.382]  vs flip ~7.0-8.0  ->  stylized: robust_chalk
- d-sensitivity (σ_lower): d=0.1:6.16, d=0.25:9.74, d=0.5:13.78, d=0.75:16.87, d=1.0:19.49   [d=0.10 dips below the flip -> the divergence-rate tail is resolved by OBSERVED Jun-10 ownership, not by this dry-run]
- N-sensitivity (σ_upper): N=48:16.94, N=80:21.86, N=104:24.93

## Step-3 escalation - real K=4 engine, 2x2 (ownership x σ-endpoint)
(Run ALWAYS, not only on a stylized straddle: the ~σ7-8 flip is an ISOLATED-lever
 threshold and contrarians persist to σ=10 under starve in the dry-run, so even a
 'robust_chalk' bracket is CONFIRMED on the real engine under BOTH ownerships -
 reading chalk off efficient-field alone is tautological [Sebas refinement].)
  endpoints: σ_lo=13.523  σ_hi=25.382
  efficient|sigma_lo     -> chalk
  efficient|sigma_hi     -> chalk
  starve|sigma_lo        -> contrarian_2_levers
  starve|sigma_hi        -> contrarian_2_levers
  ENGINE VERDICT: SIGMA_DEPENDENT_UNDER_LEVERAGE  -> DEFER the chalk-vs-contrarian decision to OBSERVED Jun-10 ownership.
  FINAL VERDICT: stylized=robust_chalk + engine=SIGMA_DEPENDENT_UNDER_LEVERAGE -> SIGMA-DEPENDENT under real leverage -> Jun-10 OBSERVED ownership decides.

### L9 caveat
σ_cal is derived from EU club-league per-match variance (football-data.co.uk). It is a
PROXY for WC-2026 variance, NOT a WC measurement (neutral venue / knockout / scoring-rate
shifts). σ_upper (iid, all 104) is a structural ceiling; σ_lower (divergent-only) is the
practically relevant floor. The stylized ~σ7-8 flip is an ESCALATION TRIGGER, distinct
from the real K=4 verdict. RE-RUN podium+champion on σ_cal at Jun-10 (fresh odds +
OBSERVED ownership) before any lock. No pick is locked here; champion + 4 awards OPEN.
