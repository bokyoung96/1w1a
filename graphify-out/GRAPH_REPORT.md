# Graph Report - /Users/bkchoi/Desktop/GitHub/1w1a  (2026-04-13)

## Corpus Check
- 242 files · ~92,309 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1885 nodes · 6106 edges · 41 communities detected
- Extraction: 30% EXTRACTED · 70% INFERRED · 0% AMBIGUOUS · INFERRED: 4245 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Raw Ksdq Csv|Raw Ksdq Csv]]
- [[_COMMUNITY_Backtesting Reporting Frontend|Backtesting Reporting Frontend]]
- [[_COMMUNITY_Docs Superpowers Policy|Docs Superpowers Policy]]
- [[_COMMUNITY_Tests Dashboard Backend|Tests Dashboard Backend]]
- [[_COMMUNITY_Tests Test Run.Py Engine|Tests Test Run.Py Engine]]
- [[_COMMUNITY_Docs Superpowers Plans|Docs Superpowers Plans]]
- [[_COMMUNITY_Docs Superpowers Kosdaq150|Docs Superpowers Kosdaq150]]
- [[_COMMUNITY_Tests Reporting Analytics|Tests Reporting Analytics]]
- [[_COMMUNITY_Backtesting Reporting Tests|Backtesting Reporting Tests]]
- [[_COMMUNITY_Dashboard Frontend App|Dashboard Frontend App]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Docs Superpowers Strategy|Docs Superpowers Strategy]]
- [[_COMMUNITY_Backtesting Reporting Composers|Backtesting Reporting Composers]]
- [[_COMMUNITY_Dashboard Backend Schemas|Dashboard Backend Schemas]]
- [[_COMMUNITY_Docs Superpowers Plans|Docs Superpowers Plans]]
- [[_COMMUNITY_Docs Superpowers Backtest|Docs Superpowers Backtest]]
- [[_COMMUNITY_Docs Superpowers Live|Docs Superpowers Live]]
- [[_COMMUNITY_Docs Superpowers Analytics|Docs Superpowers Analytics]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Docs Superpowers Research|Docs Superpowers Research]]
- [[_COMMUNITY_Docs Superpowers Performance|Docs Superpowers Performance]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Dashboard Frontend Src|Dashboard Frontend Src]]
- [[_COMMUNITY_Docs Superpowers Breakout|Docs Superpowers Breakout]]
- [[_COMMUNITY_Docs Superpowers Live|Docs Superpowers Live]]
- [[_COMMUNITY_Kis Tr Id Protocol|Kis Tr Id Protocol]]
- [[_COMMUNITY_Tests Reporting Test_Pdf|Tests Reporting Test_Pdf]]
- [[_COMMUNITY_Backtesting Universe.Py|Backtesting Universe.Py]]
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
3. `DataCatalog.get()` - 77 edges
4. `Shares Outstanding Outstanding` - 75 edges
5. `Equity Latest Quarter` - 66 edges
6. `Kosdaq Kosdaq Wics Sector Sector Large Cap Sector` - 65 edges
7. `DataCatalog.default()` - 63 edges
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
Cohesion: 0.03
Nodes (82): SymbolType, DerivMinute, Symbols, Kosdaq Ksdq150 Membership Flag, Kosdaq Kosdaq Adjusted Close, Kosdaq Kosdaq Adjusted High, Kosdaq Kosdaq Adjusted Low, Kosdaq Kosdaq Adjusted Open (+74 more)

### Community 1 - "Backtesting Reporting Frontend"
Cohesion: 0.02
Nodes (88): DrawdownStats, ExposureSnapshot, PerformanceMetrics, ResearchSnapshot, RollingMetrics, SectorSnapshot, PerformanceSnapshot, PerformanceSnapshotFactory (+80 more)

### Community 2 - "Docs Superpowers Policy"
Cohesion: 0.03
Nodes (124): ConstructionResult, LongOnlyTopN, LongShortTopBottom, SectorNeutralTopBottom, MarketData, PositionPolicy, PassThroughPolicy, BucketDefinition (+116 more)

### Community 3 - "Tests Dashboard Backend"
Cohesion: 0.04
Nodes (115): LaunchPlan, LaunchResolutionService, ResolvedRun, RunIndexService, KISAuth, FakeRunner, DataCatalog.get(), UniverseSpec.resolve_dataset() (+107 more)

### Community 4 - "Tests Test Run.Py Engine"
Cohesion: 0.05
Nodes (102): DataCatalog, DatasetGroups, DataLoader, LoadRequest, ParquetStore, BacktestEngine, BacktestResult, CostModel (+94 more)

### Community 5 - "Docs Superpowers Plans"
Cohesion: 0.03
Nodes (89): DatasetSpec, TradeCost, CustomSchedule, DailySchedule, MonthlySchedule, RebalanceSchedule, WeeklySchedule, SplitConfig (+81 more)

### Community 6 - "Docs Superpowers Kosdaq150"
Cohesion: 0.04
Nodes (80): DatasetGroup, DatasetId, BenchmarkConfig, StrategyPreset, WarmupConfig, BidAskListSpec, DerivMinuteSpec, 1w1a (+72 more)

### Community 7 - "Tests Reporting Analytics"
Cohesion: 0.05
Nodes (70): IngestResult, SectorRepository, SavedRun, Breakout52WeekStaged, RankLongOnly, RankLongShort, quantile_returns(), rank_ic() (+62 more)

### Community 8 - "Backtesting Reporting Tests"
Cohesion: 0.05
Nodes (65): ReportBuilder, ComparisonFigureBuilder, TearsheetFigureBuilder, ReportBundle, PlotExportError, PlotLibrary, ComposableStrategy, _FakeFactory (+57 more)

### Community 9 - "Dashboard Frontend App"
Cohesion: 0.03
Nodes (27): ReportArgumentParser, ReportCli, ReportKind, Options Close, Options Maturity, Options Oi, Options Spot Ticker, ReportArgumentParser.parse_args() (+19 more)

### Community 10 - "Docs Superpowers Reporting"
Cohesion: 0.06
Nodes (63): File Structure, Performance Reporting PDF Polish Implementation Plan, Placeholder Scan, Self-Review, Spec Coverage, Task 1: Add A PDF-First Render Context In The Composer, Task 2: Rebuild The Tearsheet Template Around Cover And Executive Spread, Task 3: Rebuild The Comparison Template With A Dense Executive Spread (+55 more)

### Community 11 - "Docs Superpowers Strategy"
Cohesion: 0.03
Nodes (59): BaseStrategy, CrossSectionalStrategy, TimeSeriesStrategy, ThresholdTrend, 1w1a Stock Backtesting Design, Analytics, API Shape, `BacktestEngine` (+51 more)

### Community 12 - "Backtesting Reporting Composers"
Cohesion: 0.07
Nodes (60): ComparisonComposer, ComparisonRenderContext, CoverContext, MetricStripItem, PageContext, SectionContext, TableContext, TearsheetComposer (+52 more)

### Community 13 - "Dashboard Backend Schemas"
Cohesion: 0.07
Nodes (55): BenchmarkModel, CategoryPointModel, CategorySeriesModel, DashboardContextModel, DashboardExposureModel, DashboardLaunchModel, DashboardMetricModel, DashboardPayloadModel (+47 more)

### Community 14 - "Docs Superpowers Plans"
Cohesion: 0.06
Nodes (46): DashboardBaseModel, DashboardLaunchConfig, File Structure, Live Dashboard Single-Command Launch Implementation Plan, Task 1: Add Launch Config Surface, Task 2: Resolve Saved Runs Against Desired Config, Task 3: Build Single-Command Launcher, Task 4: Expose Bootstrap State And Serve The SPA From FastAPI (+38 more)

### Community 15 - "Docs Superpowers Backtest"
Cohesion: 0.04
Nodes (48): 1w1a Backtest Reporting Design, Appendix, CLI Shape, Comparison report, Core Objects, Cover, Data Dependencies, Design Principles (+40 more)

### Community 16 - "Docs Superpowers Live"
Cohesion: 0.05
Nodes (43): Architecture, Backend, Backend API Shape, Backend Responsibility, Boundary Rule, Chosen Direction, Color, Components (+35 more)

### Community 17 - "Docs Superpowers Analytics"
Cohesion: 0.06
Nodes (38): Symbols, Dashboard Chart Followups Implementation Plan, Task 1: Red tests for the new chart shapes, Task 2: Implement the new chart transforms, Task 3: Verify and finish, tests/dashboard/test_run.py, 1. Payload Expansion, 2. Snapshot Calculations (+30 more)

### Community 18 - "Dashboard Frontend Src"
Cohesion: 0.06
Nodes (10): buildLineOption(), buildYearlyExcessOption(), distributionMidpoint(), equitySeries(), hasDistributionData(), hasSeriesData(), score(), sources() (+2 more)

### Community 19 - "Docs Superpowers Research"
Cohesion: 0.06
Nodes (33): Dashboard UX Followups Implementation Plan, Task 1: Remove the sector attribution warning at the source, Task 2: Make research figures clearer and resilient when data is sparse, Task 3: Add explicit sector filters for research charts, Task 4: Verify, commit, merge, and clean up, backtesting/run.py, dashboard/run.py, dashboard/strategies.py (+25 more)

### Community 20 - "Docs Superpowers Performance"
Cohesion: 0.06
Nodes (33): 1. Single-Run Tear Sheet, 2. Multi-Run Comparison Report, Analytics Requirements, Analytics Tests, Benchmark Policy, Builder Tests, Core Domain Objects, Data Sources (+25 more)

### Community 21 - "Docs Superpowers Reporting"
Cohesion: 0.08
Nodes (32): RunWriter, 1w1a Backtest Reporting Implementation Plan, Existing files to modify, File Map, New package files, New test files, Placeholder scan, Self-Review (+24 more)

### Community 22 - "Docs Superpowers Reporting"
Cohesion: 0.09
Nodes (25): BenchmarkRepository, BenchmarkSeries, Build Reports, Execution Handoff, Existing Files To Reuse Without Changing Responsibilities, File Structure, Modified Files, New Files (+17 more)

### Community 23 - "Dashboard Frontend Src"
Cohesion: 0.08
Nodes (2): candidate(), fetchSession()

### Community 24 - "Docs Superpowers Breakout"
Cohesion: 0.09
Nodes (22): 1. `breakout_52w_simple`, 2. `breakout_52w_staged`, 52-Week Breakout Strategies Design, Backtest And Output Requirements, Cleanup, Cleanup coverage, Git And Merge Requirements, Goal (+14 more)

### Community 25 - "Docs Superpowers Live"
Cohesion: 0.11
Nodes (17): Backend, Config Signature Shape, Data Flow, Default Strategy Set, Failure Handling, Frontend, Goal, Launcher (+9 more)

### Community 26 - "Kis Tr Id Protocol"
Cohesion: 0.2
Nodes (8): ResponseHeader, TRName, TRResponse, TRSpec, TRRegistry, TRResponse.from_http(), TRRegistry._coerce_name(), TRRegistry.get()

### Community 27 - "Tests Reporting Test_Pdf"
Cohesion: 0.33
Nodes (9): PdfRenderer, _FakeHtml, _FakeWeasyPrint, PdfRenderer.render_with_status(), _FakeHtml.write_pdf(), test_pdf_renderer_injects_print_layout_override_for_composed_reports(), test_pdf_renderer_keeps_html_when_pdf_export_fails(), test_pdf_renderer_writes_pdf_from_composed_report() (+1 more)

### Community 28 - "Backtesting Universe.Py"
Cohesion: 0.4
Nodes (3): UniverseRegistry, UniverseSpec, UniverseRegistry.default()

### Community 29 - "Raw Qw Bm.Xlsx"
Cohesion: 0.67
Nodes (2): Benchmark, qw_BM data shape

### Community 30 - "Raw Qw V.Csv"
Cohesion: 0.67
Nodes (2): Volume, qw_v data shape

### Community 31 - "Backtesting Policy Init__"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Backtesting Signals Init__"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Dashboard   Init  .Py"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Dashboard Backend Services"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Kis Tr Id Init__"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Tests Conftest.Py"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Dashboard Backend Requirements"
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

- **Why does `series()` connect `Tests Reporting Analytics` to `Raw Ksdq Csv`, `Backtesting Reporting Frontend`, `Docs Superpowers Policy`, `Tests Dashboard Backend`, `Tests Test Run.Py Engine`, `Docs Superpowers Plans`, `Docs Superpowers Kosdaq150`, `Backtesting Reporting Tests`, `Dashboard Frontend App`, `Docs Superpowers Reporting`, `Docs Superpowers Strategy`, `Backtesting Reporting Composers`, `Docs Superpowers Plans`, `Docs Superpowers Backtest`, `Docs Superpowers Live`, `Docs Superpowers Analytics`, `Docs Superpowers Research`, `Docs Superpowers Performance`, `Docs Superpowers Reporting`, `Docs Superpowers Reporting`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Equity Latest Quarter` connect `Backtesting Reporting Frontend` to `Raw Ksdq Csv`, `Tests Dashboard Backend`, `Tests Test Run.Py Engine`, `Docs Superpowers Plans`, `Docs Superpowers Kosdaq150`, `Tests Reporting Analytics`, `Backtesting Reporting Tests`, `Dashboard Frontend App`, `Docs Superpowers Reporting`, `Docs Superpowers Strategy`, `Backtesting Reporting Composers`, `Dashboard Backend Schemas`, `Docs Superpowers Plans`, `Docs Superpowers Backtest`, `Docs Superpowers Live`, `Dashboard Frontend Src`, `Docs Superpowers Performance`, `Docs Superpowers Reporting`, `Docs Superpowers Reporting`, `Dashboard Frontend Src`, `Tests Reporting Test_Pdf`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Foreign Ownership Ratio` connect `Backtesting Reporting Frontend` to `Raw Ksdq Csv`, `Docs Superpowers Policy`, `Tests Dashboard Backend`, `Docs Superpowers Plans`, `Docs Superpowers Kosdaq150`, `Tests Reporting Analytics`, `Dashboard Frontend App`, `Docs Superpowers Reporting`, `Docs Superpowers Strategy`, `Backtesting Reporting Composers`, `Dashboard Backend Schemas`, `Docs Superpowers Plans`, `Docs Superpowers Backtest`, `Docs Superpowers Live`, `Docs Superpowers Analytics`, `Dashboard Frontend Src`, `Docs Superpowers Research`, `Docs Superpowers Performance`, `Docs Superpowers Reporting`, `Dashboard Frontend Src`, `Docs Superpowers Breakout`, `Docs Superpowers Live`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `Mkt Typ` (e.g. with `factor.py` and `catalog.py`) actually correct?**
  _`Mkt Typ` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 81 inferred relationships involving `series()` (e.g. with `quantile_returns()` and `rank_ic()`) actually correct?**
  _`series()` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `DataCatalog.get()` (e.g. with `DataLoader.load()` and `IngestJob.run()`) actually correct?**
  _`DataCatalog.get()` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `Shares Outstanding Outstanding` (e.g. with `__init__.py` and `perf.py`) actually correct?**
  _`Shares Outstanding Outstanding` has 73 INFERRED edges - model-reasoned connections that need verification._