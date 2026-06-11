====================================================================================
M8 run_matchday  DRY-RUN  -  Mexico vs South Africa
  fixture=80d82d1113934bfbea4ce8daf37a2433  commence=2026-06-11T19:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=coolbet  books=['pinnacle', 'betfair_ex_eu', 'everygame', 'unibet_fr', 'coolbet', 'sport888', 'williamhill', 'unibet_nl', 'leovegas_se', 'unibet_se', 'betonlineag', 'pmu_fr', 'mybookieag', 'winamax_fr', 'betclic_fr', 'betsson', 'gtbets', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it', 'winamax_de', 'tipico_de']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=coolbet, totals_book=coolbet)
  overround=1.0227  de-vigged 1X2={H:0.679 D:0.213 A:0.109}
  totals: line=2.5 (x.5 OK)  p_over=0.448  mu_eff=2.4670  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     1-0    3.383    0.1461
     2-0    3.315    0.1422
     2-1    3.041    0.0871
     3-0    3.036    0.0918
     3-1    2.841    0.0562
     4-0    2.790    0.0451
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   1-0   E[pts]=3.383  P=0.1461
  MODAL / CHALK (most likely):   1-0   P=0.1461
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
