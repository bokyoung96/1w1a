---
type: community
cohesion: 0.05
members: 80
---

# Tests Reporting Analytics

**Cohesion:** 0.05 - loosely connected
**Members:** 80 nodes

## Members
- [[BaseStrategy.zeros_like()]] - code - backtesting/strategy/base.py
- [[Breakout52WeekStaged]] - code - backtesting/strategies/breakout_staged.py
- [[Breakout52WeekStaged.build_plan()]] - code - backtesting/strategies/breakout_staged.py
- [[Breakout52WeekStaged.build_signal()]] - code - backtesting/strategies/breakout_staged.py
- [[Breakout52WeekStaged.datasets()]] - code - backtesting/strategies/breakout_staged.py
- [[IngestResult]] - code - backtesting/ingest/report.py
- [[IngestResult.from_frame()]] - code - backtesting/ingest/report.py
- [[IngestResult.to_dict()]] - code - backtesting/ingest/report.py
- [[IngestResult.write_json()]] - code - backtesting/ingest/report.py
- [[PerformanceSnapshotFactory._build_sectors()]] - code - backtesting/reporting/snapshots.py
- [[RankLongOnly]] - code - backtesting/strategy/cross.py
- [[RankLongOnly.target_weights()]] - code - backtesting/strategy/cross.py
- [[RankLongShort]] - code - backtesting/strategy/cross.py
- [[RankLongShort.target_weights()]] - code - backtesting/strategy/cross.py
- [[RegisteredStrategy.target_weights()]] - code - backtesting/strategies/base.py
- [[SavedRun]] - code - backtesting/reporting/models.py
- [[SectorRepository]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.__init__()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository._display_sector_label()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository._group_row_by_sector()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository._latest_aligned_weights()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository._normalize_symbol_key()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.default()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.display_symbol()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.from_frame()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.latest_sector_counts()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.latest_sector_row()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.latest_sector_weights()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.sector_contribution_timeseries()]] - code - backtesting/reporting/benchmarks.py
- [[SectorRepository.sector_weight_timeseries()]] - code - backtesting/reporting/benchmarks.py
- [[_asset_prices()]] - code - tests/reporting/test_snapshots.py
- [[_benchmark_prices()]] - code - tests/reporting/test_snapshots.py
- [[_expected_sortino()]] - code - tests/reporting/test_snapshots.py
- [[_load_display_name_maps()]] - code - backtesting/reporting/benchmarks.py
- [[_long_asset_prices()]] - code - tests/reporting/test_snapshots.py
- [[_long_benchmark_prices()]] - code - tests/reporting/test_snapshots.py
- [[_long_run()]] - code - tests/reporting/test_snapshots.py
- [[_long_sector_map()]] - code - tests/reporting/test_snapshots.py
- [[_sector_map()]] - code - tests/reporting/test_snapshots.py
- [[_toy_run()]] - code - tests/reporting/test_snapshots.py
- [[cross.py]] - code - backtesting/strategy/cross.py
- [[factor.py]] - code - backtesting/analytics/factor.py
- [[perf.py]] - code - backtesting/analytics/perf.py
- [[quantile_returns()]] - code - backtesting/analytics/factor.py
- [[rank_ic()]] - code - backtesting/analytics/factor.py
- [[report.py]] - code - backtesting/ingest/report.py
- [[series()]] - code - dashboard/frontend/src/components/App.test.tsx
- [[summarize_perf()]] - code - backtesting/analytics/perf.py
- [[test_benchmark_repository_load_returns_uses_kospi200_price_path()]] - code - tests/reporting/test_benchmarks.py
- [[test_cross.py]] - code - tests/strategy/test_cross.py
- [[test_cross_strategies_expose_cross_sectional_extension_point()]] - code - tests/strategy/test_cross.py
- [[test_factor.py]] - code - tests/analytics/test_factor.py
- [[test_load_display_name_maps_reads_sector_and_stock_sheets()]] - code - tests/reporting/test_benchmarks.py
- [[test_perf.py]] - code - tests/analytics/test_perf.py
- [[test_performance_snapshot_factory_applies_korean_sector_and_stock_display_names()]] - code - tests/reporting/test_snapshots.py
- [[test_performance_snapshot_factory_builds_analytics_snapshot()]] - code - tests/reporting/test_snapshots.py
- [[test_performance_snapshot_factory_derives_latest_holdings_when_optional_table_missing()]] - code - tests/reporting/test_snapshots.py
- [[test_performance_snapshot_factory_uses_fixed_252_day_rolling_window()]] - code - tests/reporting/test_snapshots.py
- [[test_quantile_returns_drops_duplicate_signals_without_error()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_returns_empty_frame_without_overlap()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_returns_empty_frame_without_shared_columns()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_uses_overlap_and_keeps_sparse_rows()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_returns_empty_series_without_overlap()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_returns_empty_series_without_shared_columns()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_uses_common_overlap_and_returns_nan_when_empty()]] - code - tests/analytics/test_factor.py
- [[test_rank_long_only_ignores_nan_names_when_selection_exceeds_valid_count()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_only_selects_top_names()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_only_validates_top_n()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_short_avoids_overlap_in_small_universe()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_short_balances_long_and_short_legs()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_short_ignores_nan_names_when_selection_exceeds_valid_count()]] - code - tests/strategy/test_cross.py
- [[test_rank_long_short_validates_leg_sizes()]] - code - tests/strategy/test_cross.py
- [[test_sector_contribution_timeseries_avoids_pct_change_future_warning()]] - code - tests/reporting/test_benchmarks.py
- [[test_sector_contribution_timeseries_matches_net_portfolio_return()]] - code - tests/reporting/test_benchmarks.py
- [[test_sector_repository_exposes_latest_row_and_counts_without_internal_access()]] - code - tests/reporting/test_benchmarks.py
- [[test_sector_repository_latest_sector_weights_maps_latest_date()]] - code - tests/reporting/test_benchmarks.py
- [[test_snapshots.py]] - code - tests/reporting/test_snapshots.py
- [[test_summarize_perf_handles_constant_returns()]] - code - tests/analytics/test_perf.py
- [[test_summarize_perf_marks_short_samples_undefined()]] - code - tests/analytics/test_perf.py
- [[test_summarize_perf_reports_core_metrics()]] - code - tests/analytics/test_perf.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Reporting_Analytics
SORT file.name ASC
```

## Connections to other communities
- 37 edges to [[_COMMUNITY_Backtesting Reporting Frontend]]
- 21 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 20 edges to [[_COMMUNITY_Docs Superpowers Policy]]
- 18 edges to [[_COMMUNITY_Tests Test Run.Py Engine]]
- 14 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 13 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 10 edges to [[_COMMUNITY_Backtesting Reporting Composers]]
- 9 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 8 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 7 edges to [[_COMMUNITY_Docs Superpowers Strategy]]
- 6 edges to [[_COMMUNITY_Docs Superpowers Kosdaq150]]
- 5 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 3 edges to [[_COMMUNITY_Docs Superpowers Research]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Analytics]]
- 1 edge to [[_COMMUNITY_Dashboard Frontend App]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Backtest]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Performance]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Live]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Reporting]]

## Top bridge nodes
- [[series()]] - degree 82, connects to 20 communities
- [[SavedRun]] - degree 14, connects to 7 communities
- [[test_performance_snapshot_factory_builds_analytics_snapshot()]] - degree 12, connects to 4 communities
- [[RegisteredStrategy.target_weights()]] - degree 11, connects to 4 communities
- [[test_performance_snapshot_factory_uses_fixed_252_day_rolling_window()]] - degree 11, connects to 4 communities