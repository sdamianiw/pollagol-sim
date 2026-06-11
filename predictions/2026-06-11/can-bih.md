====================================================================================
M8 run_matchday  DRY-RUN  -  Canada vs Bosnia & Herzegovina
  fixture=d1f4f946c70a0b4e81f5d43e9d32361c  commence=2026-06-12T19:00:00Z  fmt=american
------------------------------------------------------------------------------------
SOURCES / FLAGS:
  M2 source=market  primary_book=unibet_nl  books=['unibet_nl', 'unibet_se', 'leovegas_se', 'coolbet', 'betfair_ex_eu', 'everygame', 'pinnacle', 'betonlineag', 'pmu_fr', 'unibet_fr', 'sport888', 'williamhill', 'mybookieag', 'winamax_fr', 'betclic_fr', 'betsson', 'gtbets', 'nordicbet', 'codere_it', 'onexbet', 'tipico_de', 'matchbook', 'betanysports', 'winamax_de']
  book-selection: intra-book x.5 totals (RB3-clean mu_eff)  (h2h_book=unibet_nl, totals_book=unibet_nl)
  overround=1.0311  de-vigged 1X2={H:0.525 D:0.277 A:0.198}
  totals: line=2.5 (x.5 OK)  p_over=0.441  mu_eff=2.4429  [M3 totals-aware]
  M5 context: neutral venue (WC group) -> mild extra uncertainty  (flags=['neutral'], source=WC group stage = neutral venue (memory/rules.md §5; documented), mu_x1.0, var_x1.06)
  inversion-guard: clean (matrix favorite == market favorite)
  snapshot (reproducible): data/snapshots/md1_2026-06-11T16-01-57Z.json
------------------------------------------------------------------------------------
E[points] TABLE (top, plausibility-floored):
   score   E[pts]  P(score)
     1-0    2.776    0.1224
     2-1    2.607    0.0912
     2-0    2.590    0.1014
     3-1    2.329    0.0494
     3-0    2.298    0.0549
     3-2    2.163    0.0231
------------------------------------------------------------------------------------
  EV PICK (argmax E[pts]) :   1-0   E[pts]=2.776  P=0.1224
  MODAL / CHALK (most likely):   1-0   P=0.1224
  -> ALIGNED: EV pick == modal score  (per-match ownership hidden -> not leverage-contrarian)
====================================================================================
🛑 HITL STOP - dry-run only. Review above; nothing submitted, nothing locked.
   M6 decision-logging is post-lock and NOT invoked here. --submit is disabled by design.
====================================================================================
