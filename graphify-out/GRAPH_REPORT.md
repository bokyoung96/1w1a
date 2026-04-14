# Graph Report - /Users/bkchoi/Desktop/GitHub/1w1a  (2026-04-14)

## Corpus Check
- 129 files · ~247,783 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 731 nodes · 1406 edges · 47 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Backtesting Strategies Construction|Backtesting Strategies Construction]]
- [[_COMMUNITY_Backtesting Strategy Catalog|Backtesting Strategy Catalog]]
- [[_COMMUNITY_Dashboard Backend Services|Dashboard Backend Services]]
- [[_COMMUNITY_Results Backtests Plots|Results Backtests Plots]]
- [[_COMMUNITY_Backtesting Reporting Builder|Backtesting Reporting Builder]]
- [[_COMMUNITY_Backtesting Reporting Snapshots|Backtesting Reporting Snapshots]]
- [[_COMMUNITY_Backtesting Reporting Composers|Backtesting Reporting Composers]]
- [[_COMMUNITY_Backtesting Run.Py Universe|Backtesting Run.Py Universe]]
- [[_COMMUNITY_Backtesting Reporting Benchmarks|Backtesting Reporting Benchmarks]]
- [[_COMMUNITY_Backtesting Data Ingest|Backtesting Data Ingest]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Backtesting Reporting Plots|Backtesting Reporting Plots]]
- [[_COMMUNITY_Backtesting Reporting Figures|Backtesting Reporting Figures]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Backtesting Reporting Writer|Backtesting Reporting Writer]]
- [[_COMMUNITY_Dashboard Backend Serializers|Dashboard Backend Serializers]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Backend Services|Dashboard Backend Services]]
- [[_COMMUNITY_Root.Py|Root.Py]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend App|Dashboard Frontend App]]
- [[_COMMUNITY_Backtesting Analytics Factor|Backtesting Analytics Factor]]
- [[_COMMUNITY_Backtesting Validation Session|Backtesting Validation Session]]
- [[_COMMUNITY_Dashboard Backend Api|Dashboard Backend Api]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Backend Main|Dashboard Backend Main]]
- [[_COMMUNITY_Raw Map Ticker Name Index|Raw Map Ticker Name Index.Md]]
- [[_COMMUNITY_Backtesting Types.Py|Backtesting Types.Py]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Run.Py|Run.Py]]
- [[_COMMUNITY_Report.Py|Report.Py]]
- [[_COMMUNITY_Dashboard   Init  .Py|Dashboard   Init  .Py]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Dashboard Backend Init__|Dashboard Backend Init__]]
- [[_COMMUNITY_Dashboard Backend Services|Dashboard Backend Services]]

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
10. `SectorRepository` - 17 edges

## Surprising Connections (you probably didn't know these)
- `BenchmarkConfig` --conceptually_related_to--> `KOSPI 200`  [INFERRED]
  backtesting/reporting/models.py → raw/qw_BM.xlsx
- `default_repositories_for_universe()` --conceptually_related_to--> `KOSDAQ GICS Sector Mapping`  [INFERRED]
  backtesting/reporting/benchmarks.py → raw/snp_ksdq_gics_sector_latest.md
- `Performance Snapshot Factory` --references--> `QW Benchmark Time Series`  [EXTRACTED]
  backtesting/reporting/snapshots.py → raw/qw_BM.xlsx
- `Performance Snapshot Factory` --conceptually_related_to--> `Korean Sector Map`  [INFERRED]
  backtesting/reporting/snapshots.py → raw/map.xlsx
- `BenchmarkConfig` --references--> `QW Benchmark Time Series`  [EXTRACTED]
  backtesting/reporting/models.py → raw/qw_BM.xlsx

## Hyperedges (group relationships)
- **Saved Run Lifecycle** — backtest_runner, run_writer, run_reader, run_index_service, dashboard_payload_service, results_backtests_root [INFERRED 0.92]
- **Dashboard Launch Pipeline** — dashboard_launcher_main, launch_resolution_service, backtest_runner, dashboard_backend_app [INFERRED 0.90]
- **Reference Data Stack** — sector_map_document, qw_bm_document, benchmark_config, performance_snapshot_factory [INFERRED 0.85]
- **Sector Lookup Bundle** — sector_map_document, raw_map_sector_codes_doc, sector_code_lookup_index, sector_code_mapping_concept [INFERRED 0.93]
- **Ticker Lookup Bundle** — raw_ticker_name_index_doc, ticker_code_name_index, ticker_code_name_mapping_concept [INFERRED 0.93]
- **Benchmark and Snapshot Bundle** — qw_bm_document, benchmark_config, performance_snapshot_factory [INFERRED 0.90]
- **KOSDAQ GICS Lookup Bundle** — raw_gics_sector_big_document, raw_gics_sector_latest_doc, raw_gics_sector_membership_doc, raw_gics_sector_pivot_dataset, gics_sector_mapping_concept, benchmarks_default_repositories_for_universe [INFERRED 0.93]

## Communities

### Community 0 - "Backtesting Strategies Construction"
Cohesion: 0.05
Nodes (32): ABC, build_signal(), ConstructionResult, PositionPlan, PositionPolicy, RegisteredStrategy, SignalBundle, _Breakout52WeekConstructionRule (+24 more)

### Community 1 - "Backtesting Strategy Catalog"
Cohesion: 0.05
Nodes (33): BaseStrategy, CrossSectionalStrategy, TimeSeriesStrategy, DataCatalog, default(), _spec(), BacktestEngine, _normalize_quantity() (+25 more)

### Community 2 - "Dashboard Backend Services"
Cohesion: 0.06
Nodes (54): BaseModel, DashboardPayloadService, _serialize_benchmark(), _serialize_launch(), _serialize_launch_benchmark_context(), _serialize_metrics(), _serialize_research(), _serialize_rolling_correlation() (+46 more)

### Community 3 - "Results Backtests Plots"
Cohesion: 0.06
Nodes (57): Backtest Runner, Backtesting Reporting Main, Backtesting Run Main, BenchmarkConfig, 52W Breakout Strategy, Simple, 52W Breakout Strategy, Staged, Breakout 52W Simple Run (daily, close; CAGR -1.47%, MDD -51.66%), Breakout 52W Simple Drawdown Curve (+49 more)

### Community 4 - "Backtesting Reporting Builder"
Cohesion: 0.09
Nodes (24): _build_notes(), ReportBuilder, _write_legacy_table(), _write_tables(), main(), ReportArgumentParser, ReportCli, _validate_report_args() (+16 more)

### Community 5 - "Backtesting Reporting Snapshots"
Cohesion: 0.08
Nodes (26): build_monthly_heatmap(), DrawdownStats, ExposureSnapshot, monthly_return_series(), PerformanceMetrics, ResearchSnapshot, RollingMetrics, SectorSnapshot (+18 more)

### Community 6 - "Backtesting Reporting Composers"
Cohesion: 0.15
Nodes (26): _comparison_metric_strip(), ComparisonComposer, ComparisonRenderContext, CoverContext, _format_metric_value(), _format_table_cell(), _format_value(), _is_internal_column() (+18 more)

### Community 7 - "Backtesting Run.Py Universe"
Cohesion: 0.12
Nodes (20): BacktestRunner, build_frontend(), build_parser(), _build_run_config(), _install_frontend_dependencies(), launch_dashboard(), main(), _needs_npm_install() (+12 more)

### Community 8 - "Backtesting Reporting Benchmarks"
Cohesion: 0.11
Nodes (17): BenchmarkRepository, BenchmarkSeries, default(), default_repositories_for_universe(), from_frame(), _load_default_frame(), _load_display_name_maps(), _normalize_symbol_key() (+9 more)

### Community 9 - "Backtesting Data Ingest"
Cohesion: 0.09
Nodes (6): DataLoader, LoadRequest, MarketData, IngestJob, IngestResult, ParquetStore

### Community 10 - "Dashboard Frontend Src"
Cohesion: 0.24
Nodes (24): asNumber(), asRecord(), asString(), fetchDashboard(), fetchSession(), normalizeBenchmarkOption(), normalizeCategoryPoint(), normalizeCategorySeries() (+16 more)

### Community 11 - "Backtesting Reporting Plots"
Cohesion: 0.15
Nodes (12): _line_trace(), _monthly_heatmap_trace(), _monthly_returns(), PlotExportError, PlotLibrary, _vertical_spacing(), RuntimeError, build_latest_qty_table() (+4 more)

### Community 12 - "Backtesting Reporting Figures"
Cohesion: 0.16
Nodes (8): ComparisonFigureBuilder, _largest_holding(), _line(), _line(), _monthly_returns(), TearsheetFigureBuilder, _top_holdings(), write_figure_asset()

### Community 13 - "Dashboard Frontend Src"
Cohesion: 0.12
Nodes (0): 

### Community 14 - "Backtesting Reporting Writer"
Cohesion: 0.33
Nodes (8): _bucket_ledger(), _drawdown(), _latest_qty(), _latest_weights(), _monthly_returns(), _plot_series(), RunWriter, _write_json()

### Community 15 - "Dashboard Backend Serializers"
Cohesion: 0.35
Nodes (10): sanitize_finite_number(), serialize_category_series(), serialize_distribution(), serialize_drawdown_episodes(), serialize_heatmap(), serialize_latest_holdings(), serialize_latest_holdings_performance(), serialize_named_series() (+2 more)

### Community 16 - "Dashboard Frontend Src"
Cohesion: 0.36
Nodes (8): computeValueDiffs(), flattenEpisodes(), formatMetricNumber(), formatMetricPercent(), formatNumberValue(), formatRewardRisk(), ResearchDetailPanel(), visibleRunIds()

### Community 17 - "Dashboard Backend Services"
Cohesion: 0.36
Nodes (7): _config_signature(), _is_usable_run_dir(), _load_run_option(), _normalize_universe_id(), _normalize_value(), _parse_run_timestamp(), _sort_key()

### Community 18 - "Root.Py"
Cohesion: 0.25
Nodes (1): RootPaths

### Community 19 - "Dashboard Frontend Src"
Cohesion: 0.29
Nodes (2): buildCostSummary(), formatCostValue()

### Community 20 - "Dashboard Frontend App"
Cohesion: 0.52
Nodes (5): normalizeDashboardSelection(), orderSelectedRunIds(), resolveInitialRunIds(), uniqueRunIds(), uniqueRunOptions()

### Community 21 - "Backtesting Analytics Factor"
Cohesion: 0.33
Nodes (0): 

### Community 22 - "Backtesting Validation Session"
Cohesion: 0.53
Nodes (4): _covers_index(), _has_sparse_row(), _unique_sorted(), ValidationSession

### Community 23 - "Dashboard Backend Api"
Cohesion: 0.4
Nodes (2): get_run_index_service(), list_runs()

### Community 24 - "Dashboard Frontend Src"
Cohesion: 0.5
Nodes (2): formatPercentValue(), ResearchFigure()

### Community 25 - "Dashboard Frontend Src"
Cohesion: 0.67
Nodes (0): 

### Community 26 - "Dashboard Frontend Src"
Cohesion: 0.67
Nodes (0): 

### Community 27 - "Dashboard Backend Main"
Cohesion: 1.0
Nodes (2): create_app(), get_frontend_dist_dir()

### Community 28 - "Raw Map Ticker Name Index.Md"
Cohesion: 1.0
Nodes (3): Ticker/Code/Name Index Document, Ticker-Code-Name Index, Ticker/Code-to-Name Mapping

### Community 29 - "Backtesting Types.Py"
Cohesion: 1.0
Nodes (1): Core shared type definitions for the backtesting package.

### Community 30 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Run.Py"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Report.Py"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Dashboard   Init  .Py"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Dashboard Frontend Src"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Dashboard Backend Init__"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Dashboard Backend Services"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **17 isolated node(s):** `RootPaths`, `Core shared type definitions for the backtesting package.`, `run.py Entry Point`, `report.py Entry Point`, `KOSPI 200` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Backtesting Types.Py`** (2 nodes): `types.py`, `Core shared type definitions for the backtesting package.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `RunSelector.tsx`, `RunSelector()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `TopRail.tsx`, `TopRail()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `ErrorState()`, `ErrorState.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `DiagnosticStrip()`, `DiagnosticStrip.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `EmptyState()`, `EmptyState.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (2 nodes): `RunSelector.test.tsx`, `selectorScope()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Run.Py`** (1 nodes): `run.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Report.Py`** (1 nodes): `report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard   Init  .Py`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (1 nodes): `setup.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Src`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Backend Init__`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Backend Services`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DataCatalog` connect `Backtesting Strategy Catalog` to `Backtesting Reporting Benchmarks`, `Backtesting Data Ingest`, `Backtesting Run.Py Universe`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `Public strategy exports.` connect `Backtesting Strategy Catalog` to `Backtesting Strategies Construction`, `Backtesting Analytics Factor`, `Backtesting Validation Session`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `DashboardPayloadService` connect `Dashboard Backend Services` to `Backtesting Reporting Builder`, `Backtesting Reporting Snapshots`, `Backtesting Run.Py Universe`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Public strategy exports.` (e.g. with `SignalBundle` and `MomentumSignalProducer`) actually correct?**
  _`Public strategy exports.` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `DashboardPayloadService` (e.g. with `UniverseRegistry` and `PerformanceSnapshot`) actually correct?**
  _`DashboardPayloadService` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PerformanceSnapshotFactory` (e.g. with `DrawdownStats` and `ExposureSnapshot`) actually correct?**
  _`PerformanceSnapshotFactory` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ReportBuilder` (e.g. with `PerformanceSnapshotFactory` and `SavedRun`) actually correct?**
  _`ReportBuilder` has 16 INFERRED edges - model-reasoned connections that need verification._