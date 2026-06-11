====================================================================================
M8 run_matchday  DRY-RUN  -  South Korea vs Czech Republic
  fixture=384cbb5d76b535896a24fe65f93cfac8  commence=2026-06-12T02:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=betonlineag  books=['coolbet', 'betfair_ex_eu', 'everygame', 'pinnacle', 'betonlineag', 'pmu_fr', 'leovegas_se', 'unibet_se', 'unibet_fr', 'unibet_nl', 'sport888', 'williamhill', 'mybookieag', 'winamax_fr', 'betclic_fr', 'betsson', 'gtbets', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it', 'winamax_de', 'tipico_de']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=betonlineag, totals_book=betonlineag)
  overround=1.0313  de-vigged 1X2={H:0.366 D:0.310 A:0.324}
  totals: line=2.5 (x.5 OK)  p_over=0.420  mu_eff=2.3614  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     1-0    2.174    0.1019
     1-1    2.101    0.1310
     0-1    2.082    0.0981
     2-1    2.043    0.0782
     1-2    1.955    0.0754
     0-0    1.923    0.0957
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   1-0   E[pts]=2.174  P=0.1019
  MODAL / CHALK (most likely):   1-1   P=0.1310
  -> EV-vs-modal GAP: EV pick DIVERGES from the modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
