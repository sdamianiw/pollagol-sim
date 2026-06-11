# Matchday-1 RECOMMENDATIONS — 2026-06-11 (Track B, DRY-RUN / HITL)

**Source:** The Odds API `soccer_fifa_world_cup`, eu, h2h+totals, american.
**Fetched:** 2026-06-11T16:01:55Z (single live call). **Quota:** 487 remaining / 13 used (2 cr spent).
**Snapshot (replayed for all 8):** `data/snapshots/md1_2026-06-11T16-01-57Z.json`.
**Engine:** M1→M2(de-vig)→x.5 guard→M3 Dixon-Coles(mu_eff, ρ=−0.05)→M5 context(neutral)→M4 argmax E[pts].
**STATUS: nothing submitted, nothing locked. Recommendation only — Sebas enters manually on pollaya.**

Per-match ownership is HIDDEN on pollaya → there is NO leverage-contrarian per-match; the "alt" column is
the modal (chalk) score, shown only where the EV pick diverges from it. Picks maximize E[competition points],
not P(exact score).

| # | fixture | KO (UTC) | de-vig H/D/A | **EV pick** | E[pts] | modal | alt(chalk) | guard | book | label |
|---|---------|----------|--------------|-------------|--------|-------|-----------|-------|------|-------|
| 1 | Mexico–South Africa      | 06-11 19:00 | .679/.213/.109 | **1-0** | 3.383 | 1-0 | — (aligned) | clean | coolbet     | FINAL-Jun11 |
| 2 | South Korea–Czech Rep.   | 06-12 02:00 | .366/.310/.324 | **1-0** | 2.174 | 1-1 | 1-1 | clean¹ | betonlineag | FINAL-Jun11 |
| 3 | Canada–Bosnia & Herz.    | 06-12 19:00 | .525/.277/.198 | **1-0** | 2.776 | 1-0 | — (aligned) | clean | unibet_nl   | BASELINE-Jun11 |
| 4 | USA–Paraguay             | 06-13 01:00 | .476/.286/.238 | **1-0** | 2.637 | 1-1 | 1-1 | clean | williamhill | BASELINE-Jun11 |
| 5 | Qatar–Switzerland        | 06-13 19:00 | .054/.130/.815 | **0-2** | 3.734 | 0-2 | — (aligned) | clean | unibet_se   | BASELINE-Jun11 |
| 6 | Brazil–Morocco           | 06-13 22:00 | .580/.252/.169 | **1-0** | 2.933 | 1-0 | — (aligned) | clean | coolbet     | BASELINE-Jun11 |
| 7 | Haiti–Scotland           | 06-14 01:00 | .165/.227/.608 | **0-1** | 2.964 | 0-1 | — (aligned) | clean | pinnacle    | BASELINE-Jun11 |
| 8 | Australia–Turkey         | 06-14 04:00 | .194/.252/.554 | **0-1** | 2.829 | 0-1 | — (aligned) | clean | coolbet     | BASELINE-Jun11 |

¹ **KOR-CZE / L17:** on the FRESH Jun-11 odds the inversion **DID NOT fire** (matrix favorite = market favorite =
South Korea, H 0.3659 vs A 0.3435). The Jun-9 knife-edge inversion (de-vig H 0.354 / A 0.335, +1.8pp Korea) was
resolved by the firmer fresh price (+4.2pp Korea). The interim (1,1) override was conditional on the inversion
PERSISTING on fresh odds — it does not, so the EV pick **1-0** stands and respects the market favorite. HITL
choice remains Sebas's: **1-0** (EV-max, Korea win) vs **1-1** (modal, P=0.137, the safer high-mass draw).

## Guards (asserted on all 8)
- **M5 context = `['neutral']` ×8** — all group openers, H4 dormant (no non-neutral flag is live-safe). PASS.
- **x.5 totals line = 2.5 (x.5 OK) ×8** — no `LineGuardStop`, no 2.5 coercion. PASS.
- **Book coverage (H3) = intra-book RB3-clean ×8** — h2h_book == totals_book on every fixture; no cross-book,
  no totals-blind fallback. PASS.
- **Determinism:** mex-rsa replayed from the snapshot → byte-identical (diff empty). PASS.
- **Inversion guard:** clean on 7/8; KOR-CZE inversion cleared on fresh odds (see ¹).

## Detail — first-time fixtures + L17 watch (KOR-CZE, HAI-SCO, AUS-TUR)

**KOR-CZE — South Korea vs Czech Republic** (betonlineag)
- de-vig 1X2: H=0.3659 D=0.3098 A=0.3243 · totals line 2.5, p_over=0.4202 · λ_home=1.2697 λ_away=1.2403
- matrix 1X2: H=0.3659 D=0.2906 A=0.3435 → **fav = home** (NO inversion; draw compresses 0.310→0.291, ~1.9pp, but Korea's 4.2pp h2h lead absorbs it)
- top-5: 1-1:0.1374, 1-0:0.1054, 0-1:0.1011, 0-0:0.0986, 2-1:0.0796 · EV pick **1-0** (E=2.174) vs modal **1-1**

**HAI-SCO — Haiti vs Scotland** (pinnacle) — first-time fixture
- de-vig 1X2: H=0.1648 D=0.2268 A=0.6083 · totals line 2.5, p_over=0.5046 · λ_home=0.7932 λ_away=1.7168
- matrix 1X2: H=0.1648 D=0.2351 A=0.6001 → **fav = away** (Scotland), no inversion
- top-5: 0-1:0.1199, 0-2:0.1147, 1-1:0.1119, 1-2:0.0976, 0-0:0.0737 · EV pick **0-1** (E=2.964) == modal

**AUS-TUR — Australia vs Turkey** (coolbet) — first-time fixture + L17 watch
- de-vig 1X2: H=0.1941 D=0.2520 A=0.5539 · totals line 2.5, p_over=0.4764 · λ_home=0.8734 λ_away=1.6366
- matrix 1X2: H=0.1941 D=0.2528 A=0.5531 → **fav = away** (Turkey), no inversion (margin wide enough)
- top-5: 0-1:0.1216, 1-1:0.1201, 0-2:0.1071, 1-2:0.0963, 0-0:0.0814 · EV pick **0-1** (E=2.829) == modal

## Entry order (by deadline, 10 min pre-KO)
1. **MEX-RSA** 1-0 — HARD 18:50 UTC today.  2. **KOR-CZE** 1-0 (or 1-1) — 01:50 UTC overnight.
3–8 are BASELINE — refresh on their own days (Fri ~18:00 UTC: CAN-BIH, USA-PAR; Sat ~18:00 UTC: QAT-SUI,
BRA-MAR, HAI-SCO, AUS-TUR) before each 10-min deadline.
