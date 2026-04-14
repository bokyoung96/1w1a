# Graph Report - /Users/bkchoi/Desktop/GitHub/1w1a  (2026-04-14)

## Corpus Check
- 125 files · ~217,981 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 705 nodes · 1371 edges · 46 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 282 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Signals & Policies|Signals & Policies]]
- [[_COMMUNITY_Engine & Catalog|Engine & Catalog]]
- [[_COMMUNITY_Report Builder|Report Builder]]
- [[_COMMUNITY_Payload Schemas|Payload Schemas]]
- [[_COMMUNITY_Snapshots & Analytics|Snapshots & Analytics]]
- [[_COMMUNITY_Run Artifacts|Run Artifacts]]
- [[_COMMUNITY_Run Resolution|Run Resolution]]
- [[_COMMUNITY_HTML Composers|HTML Composers]]
- [[_COMMUNITY_Launch Entrypoints|Launch Entrypoints]]
- [[_COMMUNITY_Data Loading|Data Loading]]
- [[_COMMUNITY_Frontend API|Frontend API]]
- [[_COMMUNITY_Benchmarks|Benchmarks]]
- [[_COMMUNITY_Plots & Tables|Plots & Tables]]
- [[_COMMUNITY_Figure Builders|Figure Builders]]
- [[_COMMUNITY_Frontend Tests|Frontend Tests]]
- [[_COMMUNITY_Validation|Validation]]
- [[_COMMUNITY_Run Writer|Run Writer]]
- [[_COMMUNITY_Serializers|Serializers]]
- [[_COMMUNITY_Research Detail|Research Detail]]
- [[_COMMUNITY_Root Paths|Root Paths]]
- [[_COMMUNITY_Performance Strip|Performance Strip]]
- [[_COMMUNITY_Dashboard App|Dashboard App]]
- [[_COMMUNITY_Factor Analytics|Factor Analytics]]
- [[_COMMUNITY_Backend API|Backend API]]
- [[_COMMUNITY_Research Workspace|Research Workspace]]
- [[_COMMUNITY_Exposure Band|Exposure Band]]
- [[_COMMUNITY_Format Helpers|Format Helpers]]
- [[_COMMUNITY_App Factory|App Factory]]
- [[_COMMUNITY_Shared Types|Shared Types]]
- [[_COMMUNITY_Run Selector|Run Selector]]
- [[_COMMUNITY_Top Rail|Top Rail]]
- [[_COMMUNITY_Error State|Error State]]
- [[_COMMUNITY_Diagnostic Strip|Diagnostic Strip]]
- [[_COMMUNITY_Empty State|Empty State]]
- [[_COMMUNITY_Selector Tests|Selector Tests]]
- [[_COMMUNITY_Run Entry|Run Entry]]
- [[_COMMUNITY_Report Entry|Report Entry]]
- [[_COMMUNITY_Dashboard Init|Dashboard Init]]
- [[_COMMUNITY_Vite Types|Vite Types]]
- [[_COMMUNITY_Vite JS Config|Vite JS Config]]
- [[_COMMUNITY_Vite TS Config|Vite TS Config]]
- [[_COMMUNITY_Frontend Bootstrap|Frontend Bootstrap]]
- [[_COMMUNITY_Test Setup|Test Setup]]
- [[_COMMUNITY_Frontend Types|Frontend Types]]
- [[_COMMUNITY_Backend Init|Backend Init]]
- [[_COMMUNITY_Services Init|Services Init]]

## God Nodes (most connected - your core abstractions)
1. `Public strategy exports.` - 41 edges
2. `DashboardPayloadService` - 27 edges
3. `DashboardBaseModel` - 25 edges
4. `PerformanceSnapshotFactory` - 24 edges
5. `ReportBuilder` - 23 edges
6. `DataCatalog` - 20 edges
7. `asRecord()` - 20 edges
8. `PerformanceSnapshot` - 17 edges
9. `BenchmarkConfig` - 17 edges
10. `SignalBundle` - 17 edges

## Surprising Connections (you probably didn't know these)
- `QW Benchmark Time Series` --conceptually_related_to--> `Performance Snapshot Factory`  [INFERRED]
  raw/qw_BM.xlsx → backtesting/reporting/snapshots.py
- `Korean Sector Map` --conceptually_related_to--> `Performance Snapshot Factory`  [INFERRED]
  raw/map.xlsx → backtesting/reporting/snapshots.py
- `BenchmarkConfig` --conceptually_related_to--> `KOSPI 200`  [INFERRED]
  backtesting/reporting/models.py → raw/qw_BM.xlsx
- `BenchmarkConfig` --references--> `QW Benchmark Time Series`  [EXTRACTED]
  backtesting/reporting/models.py → raw/qw_BM.xlsx
- `Public strategy exports.` --uses--> `SplitConfig`  [INFERRED]
  backtesting/strategy/__init__.py → backtesting/validation/split.py

## Hyperedges (group relationships)
- **Saved Run Lifecycle** — backtest_runner, run_writer, run_reader, run_index_service, dashboard_payload_service, results_backtests_root [INFERRED 0.92]
- **Dashboard Launch Pipeline** — dashboard_launcher_main, launch_resolution_service, backtest_runner, dashboard_backend_app [INFERRED 0.90]
- **Reference Data Stack** — sector_map_document, qw_bm_document, benchmark_config, performance_snapshot_factory [INFERRED 0.85]

## Communities

### Community 0 - "Signals & Policies"
Cohesion: 0.05
Nodes (32): ABC, build_signal(), ConstructionResult, PositionPlan, PositionPolicy, RegisteredStrategy, SignalBundle, _Breakout52WeekConstructionRule (+24 more)

### Community 1 - "Engine & Catalog"
Cohesion: 0.05
Nodes (30): BaseStrategy, CrossSectionalStrategy, TimeSeriesStrategy, DataCatalog, default(), _spec(), BacktestEngine, _normalize_quantity() (+22 more)

### Community 2 - "Report Builder"
Cohesion: 0.08
Nodes (26): _build_notes(), ReportBuilder, _write_legacy_table(), _write_tables(), main(), ReportArgumentParser, ReportCli, _validate_report_args() (+18 more)

### Community 3 - "Payload Schemas"
Cohesion: 0.1
Nodes (35): BaseModel, DashboardPayloadService, _serialize_benchmark(), _serialize_launch(), _serialize_launch_benchmark_context(), _serialize_metrics(), _serialize_research(), _serialize_rolling_correlation() (+27 more)

### Community 4 - "Snapshots & Analytics"
Cohesion: 0.09
Nodes (24): build_monthly_heatmap(), DrawdownStats, ExposureSnapshot, monthly_return_series(), PerformanceMetrics, ResearchSnapshot, RollingMetrics, SectorSnapshot (+16 more)

### Community 5 - "Run Artifacts"
Cohesion: 0.09
Nodes (42): Backtest Runner, Backtesting Reporting Main, Backtesting Run Main, BenchmarkConfig, 52W Breakout Strategy, Simple, 52W Breakout Strategy, Staged, Breakout 52W Simple Run (daily, close; CAGR -1.47%, MDD -51.66%), Breakout 52W Simple Run (daily, close; CAGR -1.47%, MDD -51.66%) (+34 more)

### Community 6 - "Run Resolution"
Cohesion: 0.11
Nodes (26): _archive_run_dir(), _build_saved_signature(), _build_signature(), _is_usable_saved_run(), LaunchPlan, LaunchResolutionService, _normalize_universe_id(), _normalize_use_k200() (+18 more)

### Community 7 - "HTML Composers"
Cohesion: 0.15
Nodes (26): _comparison_metric_strip(), ComparisonComposer, ComparisonRenderContext, CoverContext, _format_metric_value(), _format_table_cell(), _format_value(), _is_internal_column() (+18 more)

### Community 8 - "Launch Entrypoints"
Cohesion: 0.12
Nodes (20): BacktestRunner, build_frontend(), build_parser(), _build_run_config(), _install_frontend_dependencies(), launch_dashboard(), main(), _needs_npm_install() (+12 more)

### Community 9 - "Data Loading"
Cohesion: 0.09
Nodes (6): DataLoader, LoadRequest, MarketData, IngestJob, IngestResult, ParquetStore

### Community 10 - "Frontend API"
Cohesion: 0.24
Nodes (24): asNumber(), asRecord(), asString(), fetchDashboard(), fetchSession(), normalizeBenchmarkOption(), normalizeCategoryPoint(), normalizeCategorySeries() (+16 more)

### Community 11 - "Benchmarks"
Cohesion: 0.15
Nodes (10): BenchmarkRepository, BenchmarkSeries, default(), default_repositories_for_universe(), from_frame(), _load_default_frame(), _load_display_name_maps(), _normalize_symbol_key() (+2 more)

### Community 12 - "Plots & Tables"
Cohesion: 0.15
Nodes (12): _line_trace(), _monthly_heatmap_trace(), _monthly_returns(), PlotExportError, PlotLibrary, _vertical_spacing(), RuntimeError, build_latest_qty_table() (+4 more)

### Community 13 - "Figure Builders"
Cohesion: 0.16
Nodes (8): ComparisonFigureBuilder, _largest_holding(), _line(), _line(), _monthly_returns(), TearsheetFigureBuilder, _top_holdings(), write_figure_asset()

### Community 14 - "Frontend Tests"
Cohesion: 0.12
Nodes (0): 

### Community 15 - "Validation"
Cohesion: 0.21
Nodes (7): _covers_index(), _has_sparse_row(), _unique_sorted(), ValidationSession, split_frame(), SplitConfig, SplitResult

### Community 16 - "Run Writer"
Cohesion: 0.33
Nodes (8): _bucket_ledger(), _drawdown(), _latest_qty(), _latest_weights(), _monthly_returns(), _plot_series(), RunWriter, _write_json()

### Community 17 - "Serializers"
Cohesion: 0.35
Nodes (10): sanitize_finite_number(), serialize_category_series(), serialize_distribution(), serialize_drawdown_episodes(), serialize_heatmap(), serialize_latest_holdings(), serialize_latest_holdings_performance(), serialize_named_series() (+2 more)

### Community 18 - "Research Detail"
Cohesion: 0.36
Nodes (8): computeValueDiffs(), flattenEpisodes(), formatMetricNumber(), formatMetricPercent(), formatNumberValue(), formatRewardRisk(), ResearchDetailPanel(), visibleRunIds()

### Community 19 - "Root Paths"
Cohesion: 0.25
Nodes (1): RootPaths

### Community 20 - "Performance Strip"
Cohesion: 0.29
Nodes (2): buildCostSummary(), formatCostValue()

### Community 21 - "Dashboard App"
Cohesion: 0.52
Nodes (5): normalizeDashboardSelection(), orderSelectedRunIds(), resolveInitialRunIds(), uniqueRunIds(), uniqueRunOptions()

### Community 22 - "Factor Analytics"
Cohesion: 0.33
Nodes (0): 

### Community 23 - "Backend API"
Cohesion: 0.4
Nodes (2): get_run_index_service(), list_runs()

### Community 24 - "Research Workspace"
Cohesion: 0.5
Nodes (2): formatPercentValue(), ResearchFigure()

### Community 25 - "Exposure Band"
Cohesion: 0.67
Nodes (0): 

### Community 26 - "Format Helpers"
Cohesion: 0.67
Nodes (0): 

### Community 27 - "App Factory"
Cohesion: 1.0
Nodes (2): create_app(), get_frontend_dist_dir()

### Community 28 - "Shared Types"
Cohesion: 1.0
Nodes (1): Core shared type definitions for the backtesting package.

### Community 29 - "Run Selector"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Top Rail"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Error State"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Diagnostic Strip"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Empty State"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Selector Tests"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Run Entry"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Report Entry"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Dashboard Init"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Vite Types"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Vite JS Config"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Vite TS Config"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Frontend Bootstrap"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Test Setup"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Frontend Types"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Backend Init"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Services Init"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **6 isolated node(s):** `RootPaths`, `Core shared type definitions for the backtesting package.`, `run.py Entry Point`, `report.py Entry Point`, `Korean Sector Map` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Shared Types`** (2 nodes): `types.py`, `Core shared type definitions for the backtesting package.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Run Selector`** (2 nodes): `RunSelector.tsx`, `RunSelector()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Top Rail`** (2 nodes): `TopRail.tsx`, `TopRail()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Error State`** (2 nodes): `ErrorState()`, `ErrorState.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Diagnostic Strip`** (2 nodes): `DiagnosticStrip()`, `DiagnosticStrip.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Empty State`** (2 nodes): `EmptyState()`, `EmptyState.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Selector Tests`** (2 nodes): `RunSelector.test.tsx`, `selectorScope()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Run Entry`** (1 nodes): `run.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Report Entry`** (1 nodes): `report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Init`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite Types`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite JS Config`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite TS Config`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Frontend Bootstrap`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Test Setup`** (1 nodes): `setup.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Frontend Types`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Init`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Services Init`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Public strategy exports.` connect `Engine & Catalog` to `Signals & Policies`, `Factor Analytics`, `Validation`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Why does `DataCatalog` connect `Engine & Catalog` to `Launch Entrypoints`, `Data Loading`, `Benchmarks`?**
  _High betweenness centrality (0.215) - this node is a cross-community bridge._
- **Why does `DashboardPayloadService` connect `Payload Schemas` to `Launch Entrypoints`, `Report Builder`, `Snapshots & Analytics`, `Run Resolution`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Public strategy exports.` (e.g. with `SignalBundle` and `MomentumSignalProducer`) actually correct?**
  _`Public strategy exports.` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `DashboardPayloadService` (e.g. with `BenchmarkConfig` and `SavedRun`) actually correct?**
  _`DashboardPayloadService` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PerformanceSnapshotFactory` (e.g. with `DrawdownStats` and `ExposureSnapshot`) actually correct?**
  _`PerformanceSnapshotFactory` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ReportBuilder` (e.g. with `BenchmarkRepository` and `SectorRepository`) actually correct?**
  _`ReportBuilder` has 16 INFERRED edges - model-reasoned connections that need verification._