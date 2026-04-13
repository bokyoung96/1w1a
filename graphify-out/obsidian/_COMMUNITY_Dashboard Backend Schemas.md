---
type: community
cohesion: 0.07
members: 60
---

# Dashboard Backend Schemas

**Cohesion:** 0.07 - loosely connected
**Members:** 60 nodes

## Members
- [[BenchmarkModel]] - code - dashboard/backend/schemas.py
- [[CategoryPointModel]] - code - dashboard/backend/schemas.py
- [[CategorySeriesModel]] - code - dashboard/backend/schemas.py
- [[DashboardContextModel]] - code - dashboard/backend/schemas.py
- [[DashboardExposureModel]] - code - dashboard/backend/schemas.py
- [[DashboardLaunchModel]] - code - dashboard/backend/schemas.py
- [[DashboardMetricModel]] - code - dashboard/backend/schemas.py
- [[DashboardPayloadModel]] - code - dashboard/backend/schemas.py
- [[DashboardPayloadService]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._read_run()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._resolve_benchmark()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_benchmark()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_context()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_launch()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_launch_benchmark_context()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_metrics()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_research()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_rolling_correlation()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_rolling_series()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._serialize_series()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService._snapshot_factory_for_run()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPayloadService.build()]] - code - dashboard/backend/services/dashboard_payload.py
- [[DashboardPerformanceModel]] - code - dashboard/backend/schemas.py
- [[DashboardResearchModel]] - code - dashboard/backend/schemas.py
- [[DashboardRollingModel]] - code - dashboard/backend/schemas.py
- [[DistributionBinModel]] - code - dashboard/backend/schemas.py
- [[DrawdownEpisodeModel]] - code - dashboard/backend/schemas.py
- [[HeatmapCellModel]] - code - dashboard/backend/schemas.py
- [[HoldingModel]] - code - dashboard/backend/schemas.py
- [[HoldingPerformanceModel]] - code - dashboard/backend/schemas.py
- [[LaunchBenchmarkContextModel]] - code - dashboard/backend/schemas.py
- [[LaunchStrategyBenchmarkModel]] - code - dashboard/backend/schemas.py
- [[NamedSeriesModel]] - code - dashboard/backend/schemas.py
- [[ResearchFocusModel]] - code - dashboard/backend/schemas.py
- [[RollingSeriesModel]] - code - dashboard/backend/schemas.py
- [[RunIndexService._is_usable_run_dir()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._load_run_option()]] - code - dashboard/backend/services/run_index.py
- [[RunOptionModel]] - code - dashboard/backend/schemas.py
- [[RunSummaryModel]] - code - dashboard/backend/schemas.py
- [[SessionBootstrapModel]] - code - dashboard/backend/schemas.py
- [[ValuePointModel]] - code - dashboard/backend/schemas.py
- [[_latest_abs_value()]] - code - dashboard/backend/serializers.py
- [[_to_camel()]] - code - dashboard/backend/schemas.py
- [[enabled_strategy_presets()]] - code - dashboard/strategies.py
- [[sanitize_finite_number()]] - code - dashboard/backend/serializers.py
- [[schemas.py]] - code - dashboard/backend/schemas.py
- [[serialize_category_series()]] - code - dashboard/backend/serializers.py
- [[serialize_distribution()]] - code - dashboard/backend/serializers.py
- [[serialize_drawdown_episodes()]] - code - dashboard/backend/serializers.py
- [[serialize_heatmap()]] - code - dashboard/backend/serializers.py
- [[serialize_latest_holdings()]] - code - dashboard/backend/serializers.py
- [[serialize_latest_holdings_performance()]] - code - dashboard/backend/serializers.py
- [[serialize_named_series()]] - code - dashboard/backend/serializers.py
- [[serialize_named_values()]] - code - dashboard/backend/serializers.py
- [[serialize_value_points()]] - code - dashboard/backend/serializers.py
- [[serializers.py]] - code - dashboard/backend/serializers.py
- [[test_default_launch_config_enables_both_default_strategies()]] - code - tests/dashboard/test_strategies.py
- [[test_default_launch_config_strategy_params_are_read_only()]] - code - tests/dashboard/test_strategies.py
- [[test_enabled_strategy_presets_filters_disabled_entries()]] - code - tests/dashboard/test_strategies.py
- [[test_strategies.py]] - code - tests/dashboard/test_strategies.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Dashboard_Backend_Schemas
SORT file.name ASC
```

## Connections to other communities
- 26 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 19 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 15 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 10 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 2 edges to [[_COMMUNITY_Tests Test Run.Py Engine]]
- 2 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 1 edge to [[_COMMUNITY_Backtesting Reporting Tests]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Kosdaq150]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Reporting]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Analytics]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Policy]]

## Top bridge nodes
- [[DashboardPayloadService]] - degree 18, connects to 4 communities
- [[DashboardPayloadService._resolve_benchmark()]] - degree 6, connects to 4 communities
- [[DashboardPayloadService._snapshot_factory_for_run()]] - degree 5, connects to 3 communities
- [[enabled_strategy_presets()]] - degree 5, connects to 3 communities
- [[schemas.py]] - degree 38, connects to 2 communities