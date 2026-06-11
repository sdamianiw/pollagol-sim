====================================================================================
M8 run_matchday  DRY-RUN  -  Haiti vs Scotland
  fixture=5ae41a06735c926eeb7f74006933adce  commence=2026-06-14T01:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=pinnacle  books=['pinnacle', 'betfair_ex_eu', 'everygame', 'coolbet', 'sport888', 'williamhill', 'unibet_nl', 'unibet_fr', 'leovegas_se', 'unibet_se', 'betonlineag', 'pmu_fr', 'mybookieag', 'winamax_fr', 'winamax_de', 'betclic_fr', 'betsson', 'gtbets', 'tipico_de', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=pinnacle, totals_book=pinnacle)
  overround=1.0372  de-vigged 1X2={H:0.165 D:0.227 A:0.608}
  totals: line=2.5 (x.5 OK)  p_over=0.505  mu_eff=2.6927  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     0-1    2.964    0.1147
     0-2    2.875    0.1100
     1-2    2.841    0.0946
     1-3    2.617    0.0594
     0-3    2.614    0.0691
     2-3    2.409    0.0265
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   0-1   E[pts]=2.964  P=0.1147
  MODAL / CHALK (most likely):   0-1   P=0.1147
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
