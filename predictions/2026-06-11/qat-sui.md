====================================================================================
M8 run_matchday  DRY-RUN  -  Qatar vs Switzerland
  fixture=26634922d3f78c146440816023e40de8  commence=2026-06-13T19:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=unibet_se  books=['unibet_se', 'leovegas_se', 'unibet_nl', 'pmu_fr', 'betonlineag', 'unibet_fr', 'williamhill', 'everygame', 'pinnacle', 'betfair_ex_eu', 'sport888', 'coolbet', 'mybookieag', 'winamax_fr', 'winamax_de', 'betclic_fr', 'betsson', 'gtbets', 'tipico_de', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=unibet_se, totals_book=unibet_se)
  overround=1.0222  de-vigged 1X2={H:0.054 D:0.130 A:0.815}
  totals: line=2.5 (x.5 OK)  p_over=0.588  mu_eff=3.0481  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     0-2    3.734    0.1460
     0-1    3.618    0.1159
     0-3    3.593    0.1224
     0-4    3.361    0.0782
     1-2    3.317    0.0781
     1-3    3.261    0.0654
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   0-2   E[pts]=3.734  P=0.1460
  MODAL / CHALK (most likely):   0-2   P=0.1460
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
