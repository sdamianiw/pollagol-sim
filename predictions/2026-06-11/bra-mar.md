====================================================================================
M8 run_matchday  DRY-RUN  -  Brazil vs Morocco
  fixture=f6c8748a16516e0998f95de14235432a  commence=2026-06-13T22:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=coolbet  books=['pinnacle', 'betfair_ex_eu', 'everygame', 'unibet_fr', 'coolbet', 'sport888', 'williamhill', 'unibet_nl', 'leovegas_se', 'unibet_se', 'betonlineag', 'pmu_fr', 'mybookieag', 'winamax_fr', 'winamax_de', 'betclic_fr', 'betsson', 'gtbets', 'tipico_de', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=coolbet, totals_book=coolbet)
  overround=1.0320  de-vigged 1X2={H:0.580 D:0.252 A:0.169}
  totals: line=2.5 (x.5 OK)  p_over=0.476  mu_eff=2.5794  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     1-0    2.933    0.1204
     2-0    2.811    0.1098
     2-1    2.780    0.0936
     3-1    2.535    0.0559
     3-0    2.534    0.0656
     3-2    2.338    0.0248
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   1-0   E[pts]=2.933  P=0.1204
  MODAL / CHALK (most likely):   1-0   P=0.1204
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
