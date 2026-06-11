====================================================================================
M8 run_matchday  DRY-RUN  -  Australia vs Turkey
  fixture=564084f52cc9f1abcc18187c168a7cdc  commence=2026-06-14T04:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=coolbet  books=['coolbet', 'betfair_ex_eu', 'everygame', 'betonlineag', 'pmu_fr', 'unibet_fr', 'leovegas_se', 'unibet_se', 'pinnacle', 'unibet_nl', 'sport888', 'williamhill', 'mybookieag', 'winamax_fr', 'betclic_fr', 'betsson', 'gtbets', 'nordicbet', 'onexbet', 'matchbook', 'betanysports', 'codere_it', 'winamax_de', 'tipico_de']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=coolbet, totals_book=coolbet)
  overround=1.0306  de-vigged 1X2={H:0.194 D:0.252 A:0.554}
  totals: line=2.5 (x.5 OK)  p_over=0.476  mu_eff=2.5794  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     0-1    2.829    0.1164
     1-2    2.699    0.0934
     0-2    2.688    0.1033
     1-3    2.442    0.0541
     0-3    2.410    0.0599
     2-3    2.263    0.0255
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   0-1   E[pts]=2.829  P=0.1164
  MODAL / CHALK (most likely):   0-1   P=0.1164
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
