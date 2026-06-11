====================================================================================
M8 run_matchday  DRY-RUN  -  USA vs Paraguay
  fixture=c12986f447a515fbe641addd786dbb24  commence=2026-06-13T01:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=williamhill  books=['pinnacle', 'betfair_ex_eu', 'everygame', 'coolbet', 'sport888', 'williamhill', 'unibet_nl', 'unibet_fr', 'leovegas_se', 'unibet_se', 'betonlineag', 'pmu_fr', 'mybookieag', 'winamax_fr', 'winamax_de', 'betclic_fr', 'betsson', 'gtbets', 'tipico_de', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=williamhill, totals_book=williamhill)
  overround=1.0763  de-vigged 1X2={H:0.476 D:0.286 A:0.238}
  totals: line=2.5 (x.5 OK)  p_over=0.406  mu_eff=2.3073  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     1-0    2.637    0.1246
     2-1    2.441    0.0872
     2-0    2.391    0.0937
     3-1    2.139    0.0428
     3-0    2.092    0.0460
     1-1    2.057    0.1269
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   1-0   E[pts]=2.637  P=0.1246
  MODAL / CHALK (most likely):   1-1   P=0.1269
  -> EV-vs-modal GAP: EV pick DIVERGES from the modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
