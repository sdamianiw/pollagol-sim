# rules.md — locked rules (R5 mitigation: rubric is source-of-truth + unit-tested)

## Scoring rubric = objective function (additive across categories)
Optimize **E[points]**, never P(exact score).

| Category | Pts | Exact semantics |
|---|---|---|
| Exact score | 3 | home AND away goals both correct |
| Correct outcome (1 / X / 2) | 3 | correct win/draw/loss |
| Team goals | 1 **per team, max 2** | predicted goals for that team == actual goals for that team |
| Goal difference | 1 | predicted (home − away) margin == actual margin (any scoreline) |

Categories are **additive** (a perfect exact pick scores all of them).

### Locked unit tests (optimizer must reproduce EXACTLY)
| Actual | Predict | Exact | Outcome | Team goals | GD | **Total** |
|---|---|---|---|---|---|---|
| 1-0 | 1-0 | 3 | 3 | 1+1 | 1 | **9** |
| 1-0 | 2-1 | 0 | 3 | 0+0 | 1 | **4** |
| 1-0 | 3-2 | 0 | 3 | 0+0 | 1 | **4** |
| 2-2 | 1-1 | 0 | 3 | 0+0 | 1 | **4** |

Consequence: the EV-max scoreline gravitates to the **modal low-scoring favorite win** (1-0, 2-1), because
outcome (3) + GD (1) dominate and are winnable without the exact score. This is intended, and is the guard
against the "one factor → extreme scoreline" failure (R6): clamp + shrink + distributional output.

## Locked pre-tournament picks (50 pts; 10 each)
Champion · top scorer · top assister · MVP · best GK. Irreversible after tournament start. Decide via the
Chalk-vs-Contrarian engine (`pool/`) + council (`council/`). **HITL GATE: not finalizable while
`ownership_source = prior`.**

**Ownership visibility (pollaya) — CONFIRMED 2026-06-02 via screenshots (was `[PENDING]`, now FACT):**
**premiation/locked picks (champion/scorer/assister/MVP/GK) ARE visible** → `PICKS_VISIBLE=True` (in
`pool/leverage.py`); `observed` ownership is REAL (measured over opponents' locked picks). **Per-match
scorelines stay HIDDEN** → Track B/C ownership = prior only. HITL GATE persists: a pick on `prior` is
still gated (`is_gated`); `observed`/`polled` are measured (the LOCK itself remains a human action).
**Per-team ownership is NOT derivable from P_true** — prior covers the NAMED set only (see L4, L5).

**Pool params (2026-06-02):** N=12 entrants TODAY, **time-dependent → ~20–25 final** (scales every
ownership denominator AND shifts the chalk/contrarian regime, §7c). **Lock Jun-10 evening** (hard backstop
= first match Jun-11; Jun-12 02:00 = VOID, see `pool/decision_clock.md`) for all 5 locked picks. **Symmetry:** opponents see your pick too → last-mover dynamics (self-limiting; see
`pool/decision_clock.md`).

## Determinism / provenance
- Fixed seed for all Monte Carlo. Snapshot inputs to `data/snapshots/<fixture_id>_<UTC>.json`.
- Every datum: source + UTC + URL. Unconfirmed XI → `PROBABLE`. Critical inputs cross-checked ≥2 sources.

## Step-0 probe verdicts  (run 2026-05-30T15:09Z; snapshot `data/snapshots/probe_2026-05-30T15-09-50Z.json`)
- **API-Football FREE tier CANNOT serve WC-2026.** `fixtures?league=1&season=2026` →
  `errors.plan = "Free plans do not have access to this season, try from 2022 to 2024."` Plan=Free,
  `limit_day=100`. League-1 coverage: season 2022 fixtures=yes / **odds=NO**; season 2026 fixtures=NO /
  odds=NO. Source: `/status`, `/leagues?id=1`, `/fixtures` (api-sports.io, 2026-05-30).
- **Data layer re-planned:**
  - **Track A (outright/futures odds):** WEB FETCH (contract-sanctioned mandatory fallback) → de-vig →
    P_true. NOT API-Football. Provenance (source+URL+UTC) on every odds row.
  - **Track B (per-match odds, ~Jun 11):** API-Football free is out. Source DECISION PENDING — { paid
    API-Football | The Odds API free ~500/mo | football-data.org | per-matchday web fetch }. DC anchor
    likely The-Odds-API-totals or Elo-xG until resolved.
  - **Backtest B2:** WC-2022 odds are NOT on API-Football free either → external correct-score must come
    from elsewhere (e.g. football-data.co.uk archives) or B2 stays non-gating.
  - **Quota:** moot for free WC-2026 (no access). Cost model retained: 5 fixtures × 3 refreshes ≈ 32
    req/day — comfortable under any paid tier.

## Baseline definitions (backtest, evals/)
- **B1** = always predict 1-0 for the favorite.
- **B2** = EXTERNAL historical correct-score market modal score (WC-2022 / Euro-2024), if sourceable —
  independent of our DC model. **The DC-derived modal score is NEVER a baseline (circular — see
  tasks/lessons.md).**
- **Gate** = EV selector must beat B1 on points/match AND be calibrated (Brier/log-loss below threshold).

## Track-B odds source — VERDICT (DoD-2, decided 2026-06-02; probe `src/probe_oddssource.py`)
**CHOSEN PRIMARY = The Odds API** (`sport=soccer_fifa_world_cup`). Status = **LIVE-PROVEN** (2026-06-02:
`THE_ODDS_API_KEY` set → probe live call returned `events=72`, `markets=['h2h','h2h_lay','totals']`,
latency 1.28s). It is the sole candidate carrying **1X2 (h2h) + totals (over/under) for WC-2026** on a
free tier.

| candidate | 1X2 | totals | WC-2026 served | tier / cost | quota | verdict |
|---|---|---|---|---|---|---|
| **The Odds API** | YES | YES | YES (live: 72 events, sample 2026-06-14 NED-JPN) | Starter FREE (no card) / 20K $30·mo | 500 cr/mo; cost=markets×regions | **PRIMARY (LIVE-PROVEN 2026-06-02)** |
| API-Football | n/a free | n/a free | **NO on free** | free / paid Pro | 100 req/DAY | fallback (PAID only; free can't serve 2026) |
| football-data.org | NO (free) | NO (free) | fixtures only | free / odds add-on €15·mo | 10 req/min | **disqualified for odds**; OK as free fixtures/results companion |

**Why:** football-data.org free has **no odds** (odds = €15/mo add-on); API-Football **free cannot serve
season 2026** — LIVE re-confirmed 2026-06-02 (`results=0`, `errors.plan="Free plans do not have access to
this season, try from 2022 to 2024."`, latency 0.578s → network OK; corroborates the Step-0/L3 finding).
**Quota fit:** one `/odds` call returns ALL upcoming WC events; `markets=h2h,totals × regions=eu = 2
cr/call`; ~3 refreshes/match-day ≈ 6 cr/day → group stage worst case stays well under the **500 cr/mo**
free cap. **Latency:** single call < 1s → inside the 10-min pre-kickoff window. Request `oddsFormat=american`
so `pool/leverage.py: american_to_prob` applies directly (no second de-vig copy).

**Cross-check (R3) — LIVE PASS:** The Odds API returns multiple bookmakers per event natively → cross-check
= compare 2 bookmakers within one response (de-vigged favorite Δ < 3pp). **LIVE 2026-06-02:** Mexico v
South Africa, marathonbet vs pinnacle, fav=Mexico 0.668 vs 0.6678 → **Δ=0.02pp PASS** (reuses
`pool/leverage.py` de-vig). (Synthetic mechanism check also PASS, Δ=1.2pp.)

**RESOLVED 2026-06-02:** `THE_ODDS_API_KEY` set in `.env` (gitignored) → `python src/probe_oddssource.py`
→ The Odds API row = **PROVEN** (has_1x2=True, has_totals=True, wc2026_served=True, 72 live events).
**Paid 20K ($30/mo)** is the backstop ONLY if the free 500 cr/mo quota is blown — that spend needs a
separate Sebas GO (entertainment stakes). Re-probe nearer kickoff to confirm odds stay populated.

**Fallback chain:** The Odds API (free Starter) → API-Football **PAID** Pro (serves 2026 + odds; needs GO) →
Elo-xG model anchor (no market). football-data.org = free fixtures/results companion (no odds).
Provenance: the-odds-api.com/sports/fifa-world-cup-odds.html · the-odds-api.com (pricing) ·
football-data.org/coverage — all fetched 2026-06-02.

**Champion outrights (Track A) — LIVE source confirmed 2026-06-02.** Futures are a SEPARATE Odds-API sport
key: **`soccer_fifa_world_cup_winner`** + `markets=outrights` (match key `soccer_fifa_world_cup` rejects
`outrights` → HTTP 422 INVALID_MARKET_COMBO). Live call: 200, 0.41s, 54 teams, 2 books (betfair_ex_eu,
williamhill). Top: Spain +500, France +520, England +720, Brazil +950, Argentina +1000, Portugal +1050,
Germany +1650. **FM2 drift is REAL:** live (Jun-2) vs cached `data/outrights.json` (FanDuel, May-29) —
Brazil +950 vs +750, Germany +1650 vs +1300. ⇒ at the Jun-10 snapshot, re-fetch champion P_true from this
live key (2-book cross-check built in); do NOT lock on the cached May-29 file.

## F2 — Track-B M7 historical-odds gap (registered 2026-06-03)  [F2 = data-gap flag, NOT failure-mode FM2]
**F2** — Track-B M7 needs HISTORICAL pre-match odds as model input; The Odds API free has none ($30 paywall,
from 2020/2022). Mitigants un-chosen: OddsPapi free (claims historical odds) · football-data.org free
(historical RESULTS — grades picks, does NOT feed model odds) · one-month $30 Odds API window. Gates the
success-proof (M7).
**Context:** The Odds API is LIVE-PROVEN for FORWARD odds (DoD-2 verdict above) but its historical endpoint is
paywalled. OddsPapi's historical-odds claim is a CATALOG claim only — unverified for soccer/international (L7);
resolve in P1 via web pre-filter + 1-call live probe before any build depends on it. M7 leakage rule:
`odds_timestamp < kickoff` per fixture. Source: the-odds-api.com (historical-odds pricing), fetched 2026-06-03.

## P1 verdict — M7 historical-odds source (decided 2026-06-03; free, $0; HITL pre-confirm at P2 gate)
**CHOSEN = football-data.co.uk (free CSV)** for the OUT-OF-DOMAIN methodology backtest **+ free WC
FORWARD-test** for in-domain confirmation. No money spent (Sebas directive 2026-06-03: no paid window).
**M7 MODE = historical-OOD + forward-confirm.**

**Probe (L7 — live call, not a catalog claim):** `Invoke-WebRequest https://www.football-data.co.uk/mmz4281/2324/E0.csv`
→ **HTTP 200, 380 matches**. Each row carries, in ONE file: result join key (`Date,HomeTeam,AwayTeam,FTHG,
FTAG,FTR`), **1X2 pre-match odds** (`B365H/D/A`, Pinnacle `PSH/PSD/PSA`, market `Max/Avg`), **totals**
(`B365>2.5 / B365<2.5`, `P>2.5/<2.5`), **closing odds** (`…C…` cols), and **Asian-handicap** supremacy
(`AHh`). Sample: `E0,11/08/2023,…,Burnley,Man City,0,3,A,…,B365H=8,B365D=5.5,B365A=1.33,…,B365>2.5=1.67,
B365<2.5=2.2`. → 25 seasons × ~16 leagues = tens of thousands of matches, free, no key. Odds are **DECIMAL**
→ M2 needs a `decimal_to_prob = 1/odds` path alongside the live American path; each set de-vigged with its
OWN overround (single-book-set policy per set, RB3).

**Candidates rejected:**
- **OddsPapi** — marketing claims free-tier historical odds (1,372 tournaments) but coverage is
  domestic-league-centric; historical INTERNATIONAL/WC odds UNCONFIRMED; needs an account + a 250-req free
  cap. Catalog claim ≠ live availability (L7) → UNVERIFIED, not chosen. (Re-open only if Sebas wants a key.)
- **OddsPortal** — has in-domain WC/international historical 1X2 back ~30y, but web-only → requires a SCRAPE
  (fragile, ToS-gray, more code). Fails 80/20 simplicity.
- **football-data.org / Kaggle int'l-results** — RESULTS only, no odds → grade but cannot feed model de-vig.
- **$30 Odds API historical window** — EXCLUDED by Sebas (no spend).

**Leakage rule (RB1):** use pre-match (or closing) odds columns — both pre-kickoff (`odds_timestamp <
kickoff`); results (`FTHG/FTAG`) feed grading ONLY, never the model.
**M7 = TWO distinct gates — do NOT conflate (L9):**
- **Gate A — methodology validation (OOD, in-distribution, PRE-picks):** does the de-vig→DC→argmax
  pipeline run correctly and beat B1 *on football-data.co.uk*? High-n, tight CI, $0, before picks. Proves
  IMPLEMENTATION/plumbing — NOT the WC edge.
- **Gate B — WC success-proof TIER-1 (forward, POST-picks):** does the engine beat B1 *at the World Cup*?
  Only the free WC forward-test answers this; its verdict lands mid-tournament, AFTER picks (graded via M6
  `review.ps1`).
**Transfer is non-implicative in BOTH directions (RB2):** club ≠ WC (neutral venue, no true home, §5
dead-rubber/rotation/motivation asymmetry absent in league play). A club NO-EDGE does NOT imply a WC
NO-EDGE; a club edge does NOT imply a WC edge. Gate A validates implementation; it does not predict the WC
edge either way. Mitigation: run Gate A **home-zeroed (neutral-venue proxy) as the HEADLINE** — WC group =
neutral, so nullifying league home-advantage pushes more fixtures into away/close → more B1 divergence → it
is the WC-relevant test; home-advantage = secondary reference (C). **NO-EDGE remains a valid PROCESS-tier
result (L8); never tune to manufacture a win.**
**M7 design constraints (for P3):** (i) decimal odds carry vig → `decimal_to_prob = 1/odds` is
implied-WITH-overround; M2 MUST de-vig/normalize the decimal path identically (single-book-set policy,
RB3) — do NOT treat `1/odds` as a clean probability.
(ii) **Odds basis LOCKED 2026-06-03 (pre-result, anti-FM1): OPENING (`B365H/D/A`) is primary** — closest
analog to our real timing (we snapshot hours pre-kickoff, not at the close; neither opening nor closing of
football-data matches our live The-Odds-API pull exactly, opening is closest). **Closing (`B365CH…`) = a
robustness SENSITIVITY only, not a second attempt.** Changing opening↔closing AFTER reading the M7 number to
improve it = FM1 (spec-after-the-fact) — banned.
(iii) **SEGMENTED reporting is mandatory (L10), not aggregate-only. Divergence DRIVER = TOTAL level only
(CORRECTED 2026-06-03, Sebas).** B1 = "1-0 for the favorite" MIRRORS to the favorite's win on either side
— (1,0) if home is favored, (0,1) if away is favored — and the EV selector picks that SAME low-scoring
favorite win at low total. So **away-fav is gap-0, NOT a divergence segment**; favorite SIDE does not drive
divergence. (This corrects the earlier "(favorite SIDE × TOTAL level)" framing, which self-contradicted its
own verify line away-fav→0-1=B1.) Divergence is driven by the TOTAL: at high total the EV pick lifts to
2-1/1-2/2-2 while B1 stays 1-0. Segment by the DRIVER: **{low-total · any-favorite (≡B1, Δ≈0) · high-total
(the divergence segment)}**, where high-total = de-vigged P(over 2.5) ≥ 0.5. Report Δ(points/match)+CI **and
n PER SEGMENT** (ensure enough high-total fixtures — that is where any edge lives, D) alongside the
aggregate. The aggregate Δ is small BY CONSTRUCTION (gap-0 low-total dominates ~8.8k club matches) → read
the verdict on the HIGH-TOTAL segment; a small aggregate is expected, NOT failure (B). **Draw-modal
diagnostic (not a headline segment):** fixtures where P(draw) is the strict max can also diverge (EV→1-1 vs
B1→1-0) even at low total — report its count+Δ to EMPIRICALLY confirm "divergence ≈ high-total" rather than
assert it; surface it if non-negligible. In the WC (104 matches) the divergence segments are a minority →
wide CI even segmented → **NO-EDGE is the most honest likely result (L8), not a defect.** Verified
2026-06-03 (clear-fav→1-0=B1; away-fav→0-1=B1 [gap-0]; high-total→2-1=divergence).
(iv) **Same-book hygiene + μ source (root cause).** M3 anchors μ on the TOTALS LINE and supremacy s on the
1X2; when they disagree (e.g. 1X2→μ≈2.9 vs line=3.5) M3 FOLLOWS THE LINE — correct, totals is the direct μ
estimator. So the backtest MUST take 1X2 AND totals from the SAME book (B365H/D/A + B365>2.5/<2.5 together);
mixing books (e.g. B365-1X2 + Pinnacle-totals) fabricates artificial 1X2↔μ tension. LIMITATION (declared,
non-blocking): football-data gives only the single 2.5 O/U line, not a totals ladder → μ anchored on a
coarser signal than WC-live totals; a real ceiling on the OOD proof's fidelity.
(v) **μ_eff inversion — totals PRICE, not the pinned line (FROZEN 2026-06-03, BEFORE reading the number).**
The single-2.5-line limitation in (iv) is WORSE than "coarse": passing the literal line to M3 makes
`fit_lambdas` set μ≈2.51 for EVERY fixture (verified: 4 distinct μ over 380 EPL matches; de-vigged p_over
varies 0.42–0.79 but μ does NOT track it; the engine never picks 2-1). The total-goals signal lives in the
PRICE (`B365>2.5/<2.5`), not the line → discarding it makes the high-total segment a non-measurement.
**FIX (evals/ ONLY; src/ M3 stays FROZEN):** recover an effective total μ_eff by inverting the de-vigged
P(over 2.5) under a Poisson total-goals model — find μ s.t. P(T≥3)=p_over, T~Poisson(μ) (monotone →
bisection) — and feed μ_eff to the frozen `fit_lambdas` as the line (its standard 10% shrink still
applies). **Same book throughout** (B365 opening 1X2 + B365 opening over/under). **HARDENING — required
GREEN before the verdict is read:** (H3) post-fit μ must SPAN ≈[2.4,4.0] and track p_over (not
re-degenerate via the shrink), and the λ ceiling-clamp (LAMBDA_MAX=4.0) must not systematically bite
high-total fixtures; (H4) μ_eff carries TDD (hand-point + monotonicity + round-trip). The **LIVE WC path
shares this latent issue** (The-Odds-API totals price > line) → registered as a **P4 engine fix with its
own TDD**; do NOT un-freeze src/ for the OOD proof. This is a PRE-RESULT correctness fix (signal recovery),
NOT post-hoc tuning (L8): frozen before any number is read. Gate-A (this OOD proof) ≠ Gate-B (live WC) is
labeled in the report.
Sources: football-data.co.uk/notes.txt + /data.php (live 200, 2026-06-03); oddspapi.io/blog (claim);
oddsportal.com — all fetched 2026-06-03.

## PODIUM-1 — Track-A 5-pick reuse = JOINT K-lever model, NOT A2×5 (2026-06-04, auditor cross-check)
PODIUM-1 (2026-06-04, auditor cross-check): A2 `pool_montecarlo.py` is a generic single-lever categorical
E[prize] engine (champion = label from P_true; BASE_SIGMA = stand-in for all other points). The 4 awards
reuse its CRN/rank/prize logic via a NEW joint K-lever module `pool/podium_montecarlo.py` (A2 FROZEN,
reproduced byte-exact at K=1). Running A2 five times and summing/arg-maxing per-award is BANNED: E[prize] is
non-additive and misses joint separation (MASTER §7b portfolio rule). BASE_SIGMA in the joint model =
per-match spread only (5 levers now explicit); not decision-grade until Track-B P4 σ-calibration.
Thin-market policy (HITL 2026-06-04): top-assister, if no clean futures market (L7/PA4), is `[PENDIENTE]` +
defer-to-manual-chalk (Sebas's Jun-10 judgment, NOT auto-generated) and EXCLUDED from the joint engine; the
engine runs over champion+scorer+MVP+GK. Any OTHER award unexpectedly without a market → STOP + ask Sebas.

## PODIUM-2 — P1 per-award futures-source matrix (resolved 2026-06-04; re-fetch fresh Jun-10, FM2)
Live web probe (L7; Code re-fetched each stored board itself, not catalog claims). Champion already in
`data/outrights.json`. De-vig via `pool.leverage` (reproduced 2026-06-04); all three named sets normalize to
P_true = 1.0 (L4: P_true over NAMED candidates only, tail UNDEFINED — never generates a candidate).

| award | market? | primary book (board size) | crosscheck | favorite P_true | file |
|---|---|---|---|---|---|
| champion | YES | FanDuel via CBS (48) | DraftKings via Fox | Spain ~0.151 | `data/outrights.json` |
| top scorer | YES | FanDuel via FOX (19) | DraftKings via CBS (10) | Mbappe 0.169 | `data/props_top_scorer.json` |
| MVP / Golden Ball | YES | Bovada via TheSportsGeek (17) | DraftKings via CBS (5) | Yamal 0.130 | `data/props_mvp.json` |
| best GK / Golden Glove | YES | DraftKings via FOX+CBS (11) | BetOnline via VegasOdds (8, stale) | Martinez/Simon 0.137 | `data/props_best_gk.json` |
| top assister | **[PENDIENTE]** | — | — | — | none |

Named-coverage (raw implied sum, = vig net of truncated tail, NOT a clean overround): top_scorer 0.846 /
MVP 1.025 / GK 1.330. 2-book favorite cross-check PASS on all three (top scorer Mbappe +600 identical on
FanDuel & DraftKings; GK Martinez +450 DK / +400 BetOnline; both re-fetched by Code 2026-06-04).

**[PENDIENTE: props source for top-assister]** — CONSEQUENCE: no CLEAN single-book-set full board exists to
de-vig under RB3. The only complete US board (FOX "player to assist most goals", 12 names, Jun-2) carries NO
sportsbook attribution; named-book pricing exists only as scattered spot quotes (Messi 12/1 bet365; James
Rodriguez 100/1 William Hill); DraftKings & BetMGM confirmed NOT offering it; Oddschecker-UK has a page but is
403-blocked. Per the HITL thin-market policy (2026-06-04, PODIUM-1) + the **2026-06-05 refinement (lever deferred, NOT
conceded)**: top-assister is EXCLUDED from the joint engine NOW → it runs over **K=4 optimizable levers**
(champion + scorer + MVP + GK). The 10-pt lever is NOT given up over an incomplete classification: a
**FanDuel/Caesars (US-book) most-assists board probe is a MANDATORY item of the Jun-10 re-fetch**; if a clean
single-book-set board appears, the assister is **added as a 5th engine lever** (the K-lever engine supports one
more without rework). ONLY if the Jun-10 probe ALSO fails does it fall back to a manual chalk pick chosen by
Sebas at the lock (NOT auto-generated, FM3). The P3 council runs the assister **advisory-only** until/unless it
becomes an engine lever (G3). Do NOT fabricate an assister P_true (L7/PA4).
Sources fetched 2026-06-04: foxsports.com/.../golden-boot; cbssports.com/betting/news/world-cup-odds;
thesportsgeek.com/.../golden-ball; foxsports.com/.../golden-glove; vegasodds.com/.../best-goalkeeper;
foxsports.com/.../most-assists (unattributed) — 403 on oddschecker/draftkings/squawka (login/bot walls).

## PODIUM-3 — the chalk-vs-contrarian VERDICT is σ- and lever-count-dependent (demonstrated 2026-06-05)
The joint engine's QUALITATIVE recommendation (chalk vs contrarian), not just its absolute magnitudes, is
σ-dependent and diluted by the number of LIVE levers. Demonstrated via an `expected_prizes_joint` sweep
(P_true[Dark]=0.20, N_opp=11, n_sims=60000, seed=DEFAULT_SEED):
 (i) **Lever-count dilution:** with ONE live efficient second lever, flipping to an under-owned candidate is
     NET-NEGATIVE across the ENTIRE 10x→100x leverage range at σ=6 (gain −0.0015 at 10x ... −0.0004 at 100x)
     → engine correctly stays chalk. Under-ownership STRENGTH does NOT rescue a flip (the edge is capped by how
     often the contrarian wins; each extra 10-pt lever adds competing bonus mass). The K=1 flip (gain ~+0.010)
     only survives when the other levers are no-ops.
 (ii) **σ tipping point:** even ISOLATED (no competing lever), a 10x flip is 'flip' at σ≤6 but 'chalk' at σ≥8
     (tips ~σ7–8); A2 had noted a σ≥10 flip.
BASE_SIGMA=6.0 is a HAND-TUNED PLACEHOLDER, not decision-grade until Track-B P4 σ-calibration. **CONSEQUENCE
(extends PA3): re-running the joint engine on the CALIBRATED σ is MANDATORY before any lock.** The P4 draft's
qualitative direction (likely all-chalk at σ=6 with 4 live levers) may change post-calibration and must NOT be
read as final/directional. Repro: σ/ownership sweep over `pool.podium_montecarlo.expected_prizes_joint`
(numbers logged in tasks/lessons.md L12).

## P4b — σ-calibration model (DECLARED 2026-06-06 BEFORE any number is read; anti-FM1 / I2 / I3)
> This block is the FROZEN aggregation model. It is written FIRST; the computed σ values live in
> `memory/sigma_calibration.md` (written by `pool/sigma_calibration.py` AFTER this block exists). The
> compute step asserts the `SIGMA_CAL_MODEL: declared` sentinel below — refusing to run if the model was
> not logged first. The verdict is read AS-IS; **σ is NEVER tuned to move the verdict (I3 / FM-σ3).**

**What σ is.** In the A2/joint engines a player's score is `base ~ Normal(0, σ) + Σ_k 10·[pick_k==T*_k]`.
σ is the std of a player's **tournament-TOTAL** competition points (the non-locked-pick remainder), **NOT a
per-match std (I2 / FM2).** Per-match points come from the LOCKED additive rubric (exact +3, outcome +3,
per-team goal +1 each, goal-difference +1); the achievable per-match totals are **{0, 1, 3, 4, 9}** (5–8
unreachable: an exact score forces outcome+both-team-goals+GD = 9, and GD-match ⇒ outcome-match).
> **NOTE (2026-06-12, Track-B exact=2→3 correction, F9):** the stored `SIGMA_CAL`=13.7782 in
> `memory/sigma_calibration.md` was derived under the PRIOR exact=2 support {0, 1, 3, 4, 8}; it is a
> known-stale Track-A figure pending a separately-GO'd recalibration — OUT OF SCOPE for this Track-B
> objective fix (no σ recomputed here; the A2 pool/podium artifacts remain frozen on the old σ).

**Aggregation (iid-per-match).** `Var(total) = N · Var(per-match)` ⇒ **σ_total = √N · s_pm**, where
- **N** = matches an entrant scores = **DECLARED_N: 104** (WC-2026: 48 group + 46 knockout). Sensitivity
  N ∈ {48, 80, 104}.
- **s_pm** = std of per-fixture competition points from M7 = `std(ev_pts)` of
  `run_backtest(NONCOVID, delta=0.30, basis="opening")` (the headline basis). **Primary = `ev_pts`**
  (informed-entrant spread → the larger / conservative σ); `b1_pts.std()` is a chalk-pool cross-check.
- **CI** = percentile bootstrap of `std(ev_pts)`, `n_boot=5000`, `seed=20260603` (mirrors the M7 seed).

**Two bounds.**
- **σ_upper = √N · s_pm** — iid per-match; a STRUCTURAL MAXIMUM (real cross-match/cross-player correlation
  only shrinks it).
- **σ_lower = √(N · f_div · d) · s_pm** — differential-only: only matches where entrants diverge separate
  players in the ranking. **`f_div` AND `d` are DECLARED PROXIES, not measurements:**
  - **DECLARED_F_DIV: 0.611** (= high-total fraction 3300/5402 from M7) is a *proxy* for the fraction of
    picks that diverge between players — NOT the same object; carries the same proxy caveat as `d`.
  - **DECLARED_D: 0.50** (fraction of opponents diverging on a divergent match) is the **WEAKEST
    assumption** — per-match ownership is HIDDEN, so `d` is an agnostic prior. Sensitivity
    d ∈ {0.10, 0.25, 0.50, 0.75, 1.00}.
  CI on σ_lower propagated from the s_pm CI (f_div, d are fixed parameters).

**σ_cal (the injected runtime value).** = the **conservative σ_lower point estimate** (the
contrarian-favoring / lowest-defensible spread): if the real engine recommends chalk even there, chalk is
safe. Written to `memory/sigma_calibration.md` as `SIGMA_CAL:`; engines read it at call-time. **A2
`BASE_SIGMA=6.0` stays FROZEN (I1)** — σ_cal is a runtime kwarg only; the byte-exact T-anchor stays at 6.0.

**Verdict rule (read AS-IS; never tune σ — I3).** Compare the widest bracket
`[σ_lower CI-lo, σ_upper CI-hi]` to the documented isolated-lever flip at **~σ7–8** (PODIUM-3). The flip is
the **escalation TRIGGER only**, a DIFFERENT object from the real K=4 verdict — never report the stylized
threshold as the decision.
- Both bounds (incl. CI) above ~8 → ROBUST CHALK, STOP.  Both below ~7 → ROBUST FLIP.
- **Bracket straddles ~7–8 → escalate to the EXACT model under TWO ownerships** (no tuning): run the real
  K=4 `recommend_portfolio_joint` (market full-board P_true) at `sigma=σ_lower` AND `sigma=σ_upper`, under
  **(a) efficient-field** AND **(b) targeted-starve** ownership (`pool/run_podium_draft.py`). Reading chalk
  off (a) alone is quasi-tautological (leverage≈1 ⇒ chalk at any σ — the P4-audit confound); (b) supplies
  the real leverage the σ-flip bites on.
  - **Genuine `ROBUST_CHALK` requires chalk in ALL FOUR cells** (both ownerships × both σ-endpoints).
  - Else **`SIGMA_DEPENDENT_UNDER_LEVERAGE`** → the chalk-vs-contrarian decision **defers to the OBSERVED
    ownership at Jun-10** (a prior-gated dry-run cannot settle it).

**L9 caveat (logged before the verdict).** `s_pm` is EU-club-league data (football-data.co.uk); the WC is a
different domain (neutral venue, knockout, scoring-rate shifts). The calibrated σ is a **PROXY for the WC,
NOT a WC measurement.** σ_upper (iid, all 104) is a structural ceiling; σ_lower (divergent-only) is the
practically relevant floor for a low-sophistication pool.

**Machine-readable (parsed by `pool/sigma_calibration.py`):**
SIGMA_CAL_MODEL: declared
DECLARED_N: 104
DECLARED_F_DIV: 0.611
DECLARED_D: 0.50

## PODIUM TEST RUN — observed-ownership model (DECLARED 2026-06-06 BEFORE any number is read; anti-FM1 / I3)
> The Jun-6 PRELIMINARY rehearsal of the Jun-10 lock. This block is written FIRST; the ingestion code
> (`pool/ingest_ownership.py`) asserts the `OWNERSHIP_MODEL: declared` sentinel below and REFUSES to run
> if the model was not logged first. The smoothing constants (α, K_cand basis) are read AS-IS and are
> **NEVER tuned to move the chalk-vs-contrarian verdict (I3 / FM-σ).** NOT A LOCK.

**LM1 — Denominator = N_opp (NOT deciders-only).** Ownership shares use the FULL opponent count
`N_opp = 19` (roster 20 − Sebas, self-excluded) as the denominator, not the smaller `locked_count`.
A deciders-only denominator over-reacts at n=4–7 and is BANNED here. N_opp is time-dependent (entrants
may join by Jun-10) — asserted == 19 in code for this run.

**LM2 — Laplace (additive) smoothing floor.** `ownership[c] = (count_c + α) / (N_opp + α·K_cand)` for
each named candidate c. With **α = 1** and `K_cand = |named set|`, every named candidate (including those
with 0 observed picks, e.g. France for champion) gets a non-zero floor → **no infinite leverage** anywhere.

**K_cand basis (FIX-2) = (top-6 by P_true) ∪ (all observed-pick teams that resolve to a P_true board
key), per lever.** Every team that can receive ownership is a named candidate, so no observed decider
falls into the residual. Per-lever K_cand for this run: champion=7 (top-6 + Uruguay), top_scorer=7
(+Cristiano Ronaldo), mvp=7 (+Vitinha), best_gk=8 (+Diogo Costa, +Thibaut Courtois).

**LM3 — Blank/undecided = residual (never prior-filled).** Opponents not listed in pollaya are undecided;
their mass is `1 − Σ named_shares`, carried on the engine's `_SENTINEL` ("__unknown__") label so each
per-lever dict sums to exactly 1.0 (required: the joint MC and `_aggregate_ownership` both re-normalize
internally, so a sub-normalized dict would wrongly inflate named shares). `_SENTINEL` never matches a
winner → blank opponents contribute zero collision probability (win≈0).

**P2-b — observed pick without a market P_true.** An observed name that resolves to a real entity but is
NOT on the lever's P_true board is NOT fabricated and NOT hard-raised → it folds into `_SENTINEL`
(blank-equiv, win≈0) with an explicit log; only a malformed/unrecognizable token hard-raises (typo guard).
The assister has no P_true board → ADVISORY ONLY, never an engine lever (K=4); K=5 gate = Jun-10 probe.

**Step-5b — blank-resolution sensitivity (R9 / L13; read AS-IS, do NOT tune).** Run the K=4 MC under TWO
blank models: **(A) sentinel** — blanks score 0 (`_SENTINEL`); **(B) chalk-resolved** — the true-blank
mass is redistributed over the **named candidates' P_true, renormalized over the named set** (NOT the full
board), no blank `_SENTINEL`. If a lever's chalk-vs-contrarian argmax FLIPS between A and B, log it as
`INDETERMINATE-preliminary, deferred to Jun-10` (NOT "contrarian").

**α = 1, K_cand basis = top6∪observed (DECLARED, NOT TUNED).** Fixed at declaration time (I3 / FM-σ).

**Machine-readable (parsed by `pool/ingest_ownership.py`):**
OWNERSHIP_MODEL: declared
DECLARED_ALPHA: 1
DECLARED_KCAND: top6_union_observed

## LOCK RUN — decision-grade model (DECLARED 2026-06-10 BEFORE any number is read; anti-FM1 / I3)
> The Jun-10 PM decision-grade run (Step 0 of the LOCK RUN v3 contract). Written FIRST, before D1 fresh
> odds are fetched. Inherits the observed-ownership model above (OWNERSHIP_MODEL: declared, α=1,
> K_cand=top6∪observed) UNCHANGED; this block adds only the lock-specific, pre-declared constants. The σ
> bracket, n_sims, P_true gate, and §7b/A4 rules are FIXED here and **NEVER tuned to move the verdict
> (I3 / FM-σ).** A2 `pool/pool_montecarlo.py` BASE_SIGMA=6.0 stays FROZEN. RECOMMEND-NEVER-LOCK.

**N_opp = 24** (roster 25 − Sebas, self-excluded). Reconciled 19→24 vs the Jun-6 test run (entrants
joined; entry was OPEN). Time-dependent — asserted == 24 against `observed_ownership_2026-06-10.json` in
code; re-assert on a Jun-11 AM re-run.

**σ injection — bracket {6, 8, 13.78, 20}, primary 13.78 (calibrated `read_sigma_cal()` = 13.7782).**
σ is a RUNTIME kwarg into the FROZEN engine; BASE_SIGMA=6.0 (the byte-exact K=1 anchor) is never edited.
The verdict is read AS-IS across the whole bracket: a lever that flips chalk↔contrarian across σ OR across
blank-models A/B is **INDETERMINATE → chalk** (LM7 σ-ambiguity).

**n_sims = 120000 (PRE-DECLARED, PB2).** Fixed BEFORE any Δ is read so it cannot be raised after a
near-miss (that would be FM-σ tuning). At PRIZES∈{0,.1,.2,.6} the worst-case paired-CRN SE_diff bound is
√(2·0.36/120000) ≈ 0.0024 → the 2·SE_diff gate resolves flips ≥ ~1pp. The gate uses the EMPIRICAL paired
SE_diff (`std(prize_pf − prize_chalk)/√n` from the per-sim vectors), with the worst-case bound reported.

**P_true verdict gate = 0.08 (PB1).** The engine constant `MIN_PTRUE_FOR_CONTRARIAN = 0.05`
(`pool/leverage.py`) is UNTOUCHED; the 0.08 floor is enforced at the Step-7 verdict layer. A candidate
with 0.05 < P_true ≤ 0.08 is **reported-not-selected** (never gate-passed). Argentina is gate-fragile
(full-board de-vig ~0.071–0.095); it is reported with the EXACT full-board implied sum S_full and its
de-vigged P_true. England (~0.10) clears. P_true is de-vigged over a FULL board (≥40 teams, F2P1) —
a truncated-board normalization over-estimates P_true → a false gate PASS (FM1) and is BANNED.

**§7b portfolio rule + A4 (contrarian fires ONLY if ALL hold).** ≤ 1 contrarian lever (if the
unconstrained argmax is multi-contrarian, demote to the best ≤1-contrarian; a pairwise beating the best
single by > 2·SE_diff is SURFACED for HITL, never auto-selected). A flip fires iff: (i) P_true > 0.08;
(ii) ΔE_prize vs all-chalk > 2·SE_diff (empirical paired CRN); (iii) stable across the σ-bracket
{6,8,13.78,20}; (iv) stable across both blank-models A/B; (v) robust to ownership ±1 (R9-lock: one blank
moved onto the contrarian AND onto the chalk, both blank-models, verdict must persist). Else chalk.
The only live contrarian lever is **champion** (England/Argentina, 0-owned high-P_true).

**Machine-readable (LOCK RUN Step-0 sentinels; grep-verified):**
LOCK_RUN_MODEL: declared
N_OPP_LOCK: 24
N_SIMS_LOCK: 120000
PTRUE_GATE_LOCK: 0.08
SIGMA_BRACKET_LOCK: 6, 8, 13.78, 20
SIGMA_PRIMARY_LOCK: 13.78
BASE_SIGMA_FROZEN: 6.0
