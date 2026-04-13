# Graph Report - /Users/bkchoi/Desktop/GitHub/1w1a  (2026-04-13)

## Corpus Check
- 242 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1881 nodes · 6088 edges · 44 communities detected
- Extraction: 31% EXTRACTED · 69% INFERRED · 0% AMBIGUOUS · INFERRED: 4231 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Raw Ksdq Csv|Raw Ksdq Csv]]
- [[_COMMUNITY_Docs Superpowers Policy|Docs Superpowers Policy]]
- [[_COMMUNITY_Backtesting Reporting Tests|Backtesting Reporting Tests]]
- [[_COMMUNITY_Tests Test Run.Py Engine|Tests Test Run.Py Engine]]
- [[_COMMUNITY_Tests Dashboard Backend|Tests Dashboard Backend]]
- [[_COMMUNITY_Backtesting Reporting Tests|Backtesting Reporting Tests]]
- [[_COMMUNITY_Docs Superpowers Strategy|Docs Superpowers Strategy]]
- [[_COMMUNITY_Docs Superpowers Plans|Docs Superpowers Plans]]
- [[_COMMUNITY_Docs Superpowers Plans|Docs Superpowers Plans]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Dashboard Backend Schemas|Dashboard Backend Schemas]]
- [[_COMMUNITY_Dashboard Frontend App|Dashboard Frontend App]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Backtesting Reporting Composers|Backtesting Reporting Composers]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Docs Superpowers Analytics|Docs Superpowers Analytics]]
- [[_COMMUNITY_Docs Superpowers Kosdaq150|Docs Superpowers Kosdaq150]]
- [[_COMMUNITY_Docs Superpowers Live|Docs Superpowers Live]]
- [[_COMMUNITY_Tests Dashboard Test_Run|Tests Dashboard Test_Run]]
- [[_COMMUNITY_Docs Superpowers Research|Docs Superpowers Research]]
- [[_COMMUNITY_Docs Superpowers Performance|Docs Superpowers Performance]]
- [[_COMMUNITY_Docs Superpowers Breakout|Docs Superpowers Breakout]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Backtesting Reporting Tables_Single|Backtesting Reporting Tables_Single]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Tests Validation Test_Split|Tests Validation Test_Split]]
- [[_COMMUNITY_Tests Analytics Test_Factor|Tests Analytics Test_Factor]]
- [[_COMMUNITY_Kis Tools.Py Tr_Id|Kis Tools.Py Tr_Id]]
- [[_COMMUNITY_Backtesting Universe.Py|Backtesting Universe.Py]]
- [[_COMMUNITY_Kis Tools.Py|Kis Tools.Py]]
- [[_COMMUNITY_Raw Qw Bm.Xlsx|Raw Qw Bm.Xlsx]]
- [[_COMMUNITY_Raw Qw V.Csv|Raw Qw V.Csv]]
- [[_COMMUNITY_Backtesting Policy Init__|Backtesting Policy Init__]]
- [[_COMMUNITY_Backtesting Signals Init__|Backtesting Signals Init__]]
- [[_COMMUNITY_Dashboard   Init  .Py|Dashboard   Init  .Py]]
- [[_COMMUNITY_Dashboard Backend Services|Dashboard Backend Services]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Dashboard Frontend Vite|Dashboard Frontend Vite]]
- [[_COMMUNITY_Kis Tr Id Init__|Kis Tr Id Init__]]
- [[_COMMUNITY_Tests Conftest.Py|Tests Conftest.Py]]
- [[_COMMUNITY_Dashboard Backend Requirements|Dashboard Backend Requirements]]

## God Nodes (most connected - your core abstractions)
1. `Mkt Typ` - 87 edges
2. `series()` - 82 edges
3. `DataCatalog.get()` - 76 edges
4. `Shares Outstanding Outstanding` - 74 edges
5. `Equity Latest Quarter` - 66 edges
6. `Kosdaq Kosdaq Wics Sector Sector Large Cap Sector` - 64 edges
7. `DataCatalog.default()` - 62 edges
8. `Wics Sector Sector Large Cap Sector` - 61 edges
9. `BacktestEngine.run()` - 53 edges
10. `Foreign Ownership Ratio` - 52 edges

## Surprising Connections (you probably didn't know these)
- `summarize_perf()` --calls--> `Options Div`  [INFERRED]
  backtesting/analytics/perf.py → raw/options/qw_div.csv
- `BacktestEngine._rebalance()` --calls--> `Options Div`  [INFERRED]
  backtesting/engine/core.py → raw/options/qw_div.csv
- `SectorRepository.__init__()` --calls--> `Map`  [INFERRED]
  backtesting/reporting/benchmarks.py → raw/map.xlsx
- `SectorRepository.sector_contribution_timeseries()` --calls--> `Options Div`  [INFERRED]
  backtesting/reporting/benchmarks.py → raw/options/qw_div.csv
- `ReportBuilder.build_legacy()` --calls--> `Equity Latest Quarter`  [INFERRED]
  backtesting/reporting/builder.py → raw/qw_equity_lfq0.csv

## Hyperedges (group relationships)
- **Ksdq data family** — dataset_raw_ksdq_qw_ksdq150_yn_csv, dataset_raw_ksdq_qw_ksdq_adj_c_csv, dataset_raw_ksdq_qw_ksdq_adj_h_csv, dataset_raw_ksdq_qw_ksdq_adj_l_csv, dataset_raw_ksdq_qw_ksdq_adj_o_csv, dataset_raw_ksdq_qw_ksdq_mkcap_csv, dataset_raw_ksdq_qw_ksdq_mktcap_flt_csv, dataset_raw_ksdq_qw_ksdq_v_csv, dataset_raw_ksdq_qw_ksdq_wics_sec_big_csv [INFERRED 0.80]
- **Options data family** — dataset_raw_options_qw_c_csv, dataset_raw_options_qw_div_csv, dataset_raw_options_qw_implied_vol_csv, dataset_raw_options_qw_maturity_csv, dataset_raw_options_qw_oi_csv, dataset_raw_options_qw_spot_ticker_csv, dataset_raw_options_qw_strike_price_csv [INFERRED 0.80]
- **Implementation planning corpus** — file_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_1w1a_backtest_reporting_implementation_plan, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_file_map, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_existing_files_to_modify, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_new_package_files, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_new_test_files, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_1_add_typed_report_models_and_run_reader, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_2_build_summary_table_helpers, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_3_add_plotly_figure_builders, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_4_assemble_report_bundles, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_5_render_html_reports, doc_docs_superpowers_plans_2026_04_03_backtest_reporting_implementation_md_task_6_add_pdf_export_with_html_fallback [INFERRED 0.80]
- **Design spec corpus** — file_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_1w1a_backtest_reporting_design, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_goal, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_why_this_layer_exists, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_scope, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_in_scope, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_out_of_scope_for_phase_1, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_reference_patterns, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_design_principles, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_output_model, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_run_bundle, doc_docs_superpowers_specs_2026_04_03_backtest_reporting_design_md_report_bundle [INFERRED 0.80]

## Communities

### Community 0 - "Raw Ksdq Csv"
Cohesion: 0.02
Nodes (106): GlobalRunConfig, SymbolType, BidAskList, DerivMinute, TRSpec, _FakeComparisonFigureBuilder, _FakeComparisonTableBuilder, _FakeTearsheetFigureBuilder (+98 more)

### Community 1 - "Docs Superpowers Policy"
Cohesion: 0.02
Nodes (137): ConstructionResult, LongOnlyTopN, LongShortTopBottom, SectorNeutralTopBottom, MarketData, PositionPolicy, PassThroughPolicy, BucketDefinition (+129 more)

### Community 2 - "Backtesting Reporting Tests"
Cohesion: 0.03
Nodes (109): CustomSchedule, DailySchedule, MonthlySchedule, RebalanceSchedule, WeeklySchedule, IngestResult, DrawdownStats, ExposureSnapshot (+101 more)

### Community 3 - "Tests Test Run.Py Engine"
Cohesion: 0.05
Nodes (107): DataCatalog, DatasetGroups, DataLoader, LoadRequest, ParquetStore, BacktestEngine, BacktestResult, CostModel (+99 more)

### Community 4 - "Tests Dashboard Backend"
Cohesion: 0.05
Nodes (100): LaunchResolutionService, RunIndexService, KISAuth, KISConfig, ResponseHeader, TRResponse, TRClient, DataCatalog.get() (+92 more)

### Community 5 - "Backtesting Reporting Tests"
Cohesion: 0.05
Nodes (70): ReportBuilder, ComparisonFigureBuilder, TearsheetFigureBuilder, PlotExportError, PlotLibrary, RunWriter, _FakeFactory, LongOnlyTopN.build() (+62 more)

### Community 6 - "Docs Superpowers Strategy"
Cohesion: 0.03
Nodes (73): BaseStrategy, CrossSectionalStrategy, TimeSeriesStrategy, RankLongOnly, RankLongShort, ThresholdTrend, 1w1a Stock Backtesting Design, Analytics (+65 more)

### Community 7 - "Docs Superpowers Plans"
Cohesion: 0.04
Nodes (71): DatasetId, DatasetSpec, BidAskListSpec, DerivMinuteSpec, RootPaths, 1w1a Stock Backtesting Implementation Plan, Existing files to modify, Existing files to move into `kis/` (+63 more)

### Community 8 - "Docs Superpowers Plans"
Cohesion: 0.05
Nodes (63): DashboardBaseModel, LaunchPlan, ResolvedRun, DashboardLaunchConfig, StrategyPreset, WarmupConfig, File Structure, Live Dashboard Single-Command Launch Implementation Plan (+55 more)

### Community 9 - "Docs Superpowers Reporting"
Cohesion: 0.03
Nodes (66): PdfRenderer, RunReader, _FakeHtml, _FakeWeasyPrint, 1w1a Backtest Reporting Design, Appendix, CLI Shape, Comparison report (+58 more)

### Community 10 - "Dashboard Backend Schemas"
Cohesion: 0.07
Nodes (55): BenchmarkModel, CategoryPointModel, CategorySeriesModel, DashboardContextModel, DashboardExposureModel, DashboardLaunchModel, DashboardMetricModel, DashboardPayloadModel (+47 more)

### Community 11 - "Dashboard Frontend App"
Cohesion: 0.04
Nodes (14): Options Close, Options Maturity, Options Oi, availableRunIds(), createDashboard(), exposureBand(), findChartOption(), promise() (+6 more)

### Community 12 - "Docs Superpowers Reporting"
Cohesion: 0.05
Nodes (52): File Structure, Performance Reporting PDF Polish Implementation Plan, Placeholder Scan, Self-Review, Spec Coverage, Task 1: Add A PDF-First Render Context In The Composer, Task 2: Rebuild The Tearsheet Template Around Cover And Executive Spread, Task 3: Rebuild The Comparison Template With A Dense Executive Spread (+44 more)

### Community 13 - "Backtesting Reporting Composers"
Cohesion: 0.08
Nodes (53): ComparisonComposer, ComparisonRenderContext, CoverContext, MetricStripItem, PageContext, SectionContext, TableContext, TearsheetComposer (+45 more)

### Community 14 - "Dashboard Frontend Src"
Cohesion: 0.04
Nodes (12): formatRewardRisk(), buildLineOption(), buildYearlyExcessOption(), distributionMidpoint(), equitySeries(), hasDistributionData(), hasSeriesData(), score() (+4 more)

### Community 15 - "Docs Superpowers Analytics"
Cohesion: 0.06
Nodes (46): Dashboard Chart Followups Implementation Plan, Task 1: Red tests for the new chart shapes, Task 2: Implement the new chart transforms, Task 3: Verify and finish, tests/dashboard/test_run.py, 1. Payload Expansion, 2. Snapshot Calculations, 3. Frontend Layout (+38 more)

### Community 16 - "Docs Superpowers Kosdaq150"
Cohesion: 0.05
Nodes (46): DatasetGroup, 1w1a, Backend, Config Signature Shape, Data Flow, Default Strategy Set, Failure Handling, Frontend (+38 more)

### Community 17 - "Docs Superpowers Live"
Cohesion: 0.05
Nodes (43): Architecture, Backend, Backend API Shape, Backend Responsibility, Boundary Rule, Chosen Direction, Color, Components (+35 more)

### Community 18 - "Tests Dashboard Test_Run"
Cohesion: 0.1
Nodes (29): ReportArgumentParser, ReportCli, ReportKind, FakeRunner, ReportArgumentParser.parse_args(), ReportCli.parser(), ReportCli.run(), _validate_report_args() (+21 more)

### Community 19 - "Docs Superpowers Research"
Cohesion: 0.06
Nodes (33): PerformanceSnapshot, Dashboard UX Followups Implementation Plan, Task 1: Remove the sector attribution warning at the source, Task 2: Make research figures clearer and resilient when data is sparse, Task 3: Add explicit sector filters for research charts, Task 4: Verify, commit, merge, and clean up, backtesting/run.py, dashboard/run.py (+25 more)

### Community 20 - "Docs Superpowers Performance"
Cohesion: 0.06
Nodes (33): 1. Single-Run Tear Sheet, 2. Multi-Run Comparison Report, Analytics Requirements, Analytics Tests, Benchmark Policy, Builder Tests, Core Domain Objects, Data Sources (+25 more)

### Community 21 - "Docs Superpowers Breakout"
Cohesion: 0.08
Nodes (25): TradeCost, 1. `breakout_52w_simple`, 2. `breakout_52w_staged`, 52-Week Breakout Strategies Design, Backtest And Output Requirements, Cleanup, Cleanup coverage, Git And Merge Requirements (+17 more)

### Community 22 - "Docs Superpowers Reporting"
Cohesion: 0.09
Nodes (24): 1w1a Backtest Reporting Implementation Plan, Existing files to modify, File Map, New package files, New test files, Placeholder scan, Self-Review, Spec coverage (+16 more)

### Community 23 - "Dashboard Frontend Src"
Cohesion: 0.08
Nodes (2): candidate(), fetchSession()

### Community 24 - "Docs Superpowers Reporting"
Cohesion: 0.1
Nodes (19): BenchmarkConfig, Build Reports, Execution Handoff, Existing Files To Reuse Without Changing Responsibilities, File Structure, Modified Files, New Files, Performance Reporting Redesign Implementation Plan (+11 more)

### Community 25 - "Backtesting Reporting Tables_Single"
Cohesion: 0.2
Nodes (16): ComparisonTableBuilder, TearsheetTableBuilder, build_benchmark_relative_table(), build_holdings_turnover_table(), build_ranked_summary_table(), build_sector_comparison_table(), ComparisonTableBuilder.build(), _ordered_columns() (+8 more)

### Community 26 - "Dashboard Frontend Src"
Cohesion: 0.12
Nodes (5): benchmarkSeries(), chartOption(), focusLabel(), normalizeFocusLabel(), summarySeries()

### Community 27 - "Tests Validation Test_Split"
Cohesion: 0.34
Nodes (12): SplitConfig, SplitResult, split_frame(), test_split_frame_rejects_invalid_is_window(), test_split_frame_rejects_invalid_oos_window(), test_split_frame_rejects_is_window_without_overlap(), test_split_frame_rejects_oos_window_without_overlap(), test_split_frame_rejects_partial_is_window_overlap() (+4 more)

### Community 28 - "Tests Analytics Test_Factor"
Cohesion: 0.31
Nodes (9): quantile_returns(), rank_ic(), test_quantile_returns_drops_duplicate_signals_without_error(), test_quantile_returns_returns_empty_frame_without_overlap(), test_quantile_returns_returns_empty_frame_without_shared_columns(), test_quantile_returns_uses_overlap_and_keeps_sparse_rows(), test_rank_ic_returns_empty_series_without_overlap(), test_rank_ic_returns_empty_series_without_shared_columns() (+1 more)

### Community 29 - "Kis Tools.Py Tr_Id"
Cohesion: 0.32
Nodes (7): DataTools, RateLimiter, TRBatchClient, DataTools.to_frame(), main(), TRBatchClient.call_batch(), TRBatchClient._chunked()

### Community 30 - "Backtesting Universe.Py"
Cohesion: 0.4
Nodes (3): UniverseRegistry, UniverseSpec, UniverseRegistry.default()

### Community 31 - "Kis Tools.Py"
Cohesion: 0.5
Nodes (5): TimeTools, TimeTools.adjust_futures_timestamp(), TimeTools.kst_hhmmss(), TimeTools.now_kst(), TimeTools.select_completed_futures_candle()

### Community 32 - "Raw Qw Bm.Xlsx"
Cohesion: 0.67
Nodes (2): Benchmark, qw_BM data shape

### Community 33 - "Raw Qw V.Csv"
Cohesion: 0.67
Nodes (2): Volume, qw_v data shape

### Community 34 - "Backtesting Policy Init__"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Backtesting Signals Init__"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Dashboard   Init  .Py"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Dashboard Backend Services"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Kis Tr Id Init__"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Tests Conftest.Py"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Dashboard Backend Requirements"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **529 isolated node(s):** `SymbolType`, `Quick Start`, `The parquet directory must already be populated by the ingest step`, `before calling `loader.load(...)`.`, `Manual Validation` (+524 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Backtesting Policy Init__`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backtesting Signals Init__`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard   Init  .Py`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Backend Services`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Frontend Vite`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kis Tr Id Init__`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tests Conftest.Py`** (1 nodes): `conftest.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Backend Requirements`** (1 nodes): `requirements.txt`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `series()` connect `Backtesting Reporting Tests` to `Raw Ksdq Csv`, `Docs Superpowers Policy`, `Tests Test Run.Py Engine`, `Tests Dashboard Backend`, `Backtesting Reporting Tests`, `Docs Superpowers Strategy`, `Docs Superpowers Plans`, `Docs Superpowers Plans`, `Docs Superpowers Reporting`, `Dashboard Frontend App`, `Backtesting Reporting Composers`, `Docs Superpowers Analytics`, `Docs Superpowers Live`, `Docs Superpowers Research`, `Docs Superpowers Performance`, `Docs Superpowers Reporting`, `Docs Superpowers Reporting`, `Tests Analytics Test_Factor`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Equity Latest Quarter` connect `Raw Ksdq Csv` to `Tests Test Run.Py Engine`, `Tests Dashboard Backend`, `Backtesting Reporting Tests`, `Docs Superpowers Strategy`, `Docs Superpowers Plans`, `Docs Superpowers Plans`, `Docs Superpowers Reporting`, `Dashboard Backend Schemas`, `Dashboard Frontend App`, `Docs Superpowers Reporting`, `Backtesting Reporting Composers`, `Dashboard Frontend Src`, `Docs Superpowers Live`, `Docs Superpowers Performance`, `Docs Superpowers Reporting`, `Dashboard Frontend Src`, `Docs Superpowers Reporting`, `Backtesting Reporting Tables_Single`, `Dashboard Frontend Src`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Foreign Ownership Ratio` connect `Raw Ksdq Csv` to `Docs Superpowers Policy`, `Tests Dashboard Backend`, `Docs Superpowers Strategy`, `Docs Superpowers Plans`, `Docs Superpowers Plans`, `Docs Superpowers Reporting`, `Dashboard Backend Schemas`, `Dashboard Frontend App`, `Docs Superpowers Reporting`, `Backtesting Reporting Composers`, `Dashboard Frontend Src`, `Docs Superpowers Analytics`, `Docs Superpowers Kosdaq150`, `Docs Superpowers Live`, `Docs Superpowers Research`, `Docs Superpowers Performance`, `Docs Superpowers Breakout`, `Dashboard Frontend Src`, `Docs Superpowers Reporting`, `Backtesting Reporting Tables_Single`, `Dashboard Frontend Src`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `Mkt Typ` (e.g. with `factor.py` and `catalog.py`) actually correct?**
  _`Mkt Typ` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 81 inferred relationships involving `series()` (e.g. with `quantile_returns()` and `rank_ic()`) actually correct?**
  _`series()` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `DataCatalog.get()` (e.g. with `DataLoader.load()` and `IngestJob.run()`) actually correct?**
  _`DataCatalog.get()` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `Shares Outstanding Outstanding` (e.g. with `__init__.py` and `perf.py`) actually correct?**
  _`Shares Outstanding Outstanding` has 72 INFERRED edges - model-reasoned connections that need verification._