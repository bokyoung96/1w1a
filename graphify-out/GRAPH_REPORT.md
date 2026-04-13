# Graph Report - /Users/bkchoi/Desktop/GitHub/1w1a  (2026-04-13)

## Corpus Check
- 242 files · ~92,248 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1884 nodes · 6102 edges · 25 communities detected
- Extraction: 30% EXTRACTED · 70% INFERRED · 0% AMBIGUOUS · INFERRED: 4243 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Docs Superpowers Reporting|Docs Superpowers Reporting]]
- [[_COMMUNITY_Backtesting Reporting Frontend|Backtesting Reporting Frontend]]
- [[_COMMUNITY_Raw Ksdq Csv|Raw Ksdq Csv]]
- [[_COMMUNITY_Tests Dashboard Backend|Tests Dashboard Backend]]
- [[_COMMUNITY_Backtesting Reporting Tests|Backtesting Reporting Tests]]
- [[_COMMUNITY_Backtesting Strategies Tests|Backtesting Strategies Tests]]
- [[_COMMUNITY_Docs Superpowers Plans|Docs Superpowers Plans]]
- [[_COMMUNITY_Tests Test Run.Py Engine|Tests Test Run.Py Engine]]
- [[_COMMUNITY_Docs Superpowers Portfolio|Docs Superpowers Portfolio]]
- [[_COMMUNITY_Docs Superpowers Strategy|Docs Superpowers Strategy]]
- [[_COMMUNITY_Tests Reporting Analytics|Tests Reporting Analytics]]
- [[_COMMUNITY_Tests Reporting Test_Builder|Tests Reporting Test_Builder]]
- [[_COMMUNITY_Dashboard Frontend App|Dashboard Frontend App]]
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
4. `Shares Outstanding Outstanding` - 75 edges
5. `Equity Latest Quarter` - 66 edges
6. `Kosdaq Kosdaq Wics Sector Sector Large Cap Sector` - 65 edges
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

### Community 0 - "Docs Superpowers Reporting"
Cohesion: 0.01
Nodes (409): BenchmarkRepository, RunReader, LaunchPlan, Symbols, RateLimiter, TimeTools, BidAskList, BidAskListSpec (+401 more)

### Community 1 - "Backtesting Reporting Frontend"
Cohesion: 0.02
Nodes (164): DrawdownStats, ExposureSnapshot, PerformanceMetrics, ResearchSnapshot, RollingMetrics, SectorSnapshot, ComparisonFigureBuilder, TearsheetFigureBuilder (+156 more)

### Community 2 - "Raw Ksdq Csv"
Cohesion: 0.03
Nodes (130): DataCatalog, DatasetGroup, DatasetId, DatasetGroups, DatasetSpec, IngestJob, UniverseRegistry, UniverseSpec (+122 more)

### Community 3 - "Tests Dashboard Backend"
Cohesion: 0.04
Nodes (114): RunOptionModel, RunSummaryModel, LaunchResolutionService, ResolvedRun, RunIndexService, DashboardLaunchConfig, GlobalRunConfig, StrategyPreset (+106 more)

### Community 4 - "Backtesting Reporting Tests"
Cohesion: 0.04
Nodes (117): IngestResult, BenchmarkSeries, ReportArgumentParser, ReportCli, ComparisonComposer, ComparisonRenderContext, CoverContext, MetricStripItem (+109 more)

### Community 5 - "Backtesting Strategies Tests"
Cohesion: 0.04
Nodes (82): ConstructionResult, LongOnlyTopN, LongShortTopBottom, SectorNeutralTopBottom, MarketData, PositionPolicy, PassThroughPolicy, BucketDefinition (+74 more)

### Community 6 - "Docs Superpowers Plans"
Cohesion: 0.03
Nodes (90): TradeCost, CustomSchedule, DailySchedule, MonthlySchedule, RebalanceSchedule, WeeklySchedule, SplitConfig, SplitResult (+82 more)

### Community 7 - "Tests Test Run.Py Engine"
Cohesion: 0.06
Nodes (82): DataLoader, LoadRequest, ParquetStore, BacktestEngine, BacktestResult, CostModel, PositionPlan, BacktestRunner (+74 more)

### Community 8 - "Docs Superpowers Portfolio"
Cohesion: 0.02
Nodes (63): ConstructionRule, SignalProducer, ResponseHeader, TRName, TRResponse, TRSpec, TRRegistry, 1w1a Portfolio Construction And Staged Policy Design (+55 more)

### Community 9 - "Docs Superpowers Strategy"
Cohesion: 0.03
Nodes (67): RunWriter, BaseStrategy, CrossSectionalStrategy, TimeSeriesStrategy, ThresholdTrend, 1w1a Stock Backtesting Design, Analytics, API Shape (+59 more)

### Community 10 - "Tests Reporting Analytics"
Cohesion: 0.06
Nodes (62): SectorRepository, Breakout52WeekStaged, RankLongOnly, RankLongShort, quantile_returns(), rank_ic(), summarize_perf(), IngestResult.from_frame() (+54 more)

### Community 11 - "Tests Reporting Test_Builder"
Cohesion: 0.06
Nodes (51): ReportBuilder, SavedRun, PlotExportError, PlotLibrary, _FakeComparisonFigureBuilder, _FakeComparisonTableBuilder, _FakeFactory, _FakeTearsheetFigureBuilder (+43 more)

### Community 12 - "Dashboard Frontend App"
Cohesion: 0.03
Nodes (16): Options Close, Options Maturity, Options Oi, Options Spot Ticker, availableRunIds(), createDashboard(), exposureBand(), findChartOption() (+8 more)

### Community 13 - "Raw Qw Bm.Xlsx"
Cohesion: 0.67
Nodes (2): Benchmark, qw_BM data shape

### Community 14 - "Raw Qw V.Csv"
Cohesion: 0.67
Nodes (2): Volume, qw_v data shape

### Community 15 - "Backtesting Policy Init__"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Backtesting Signals Init__"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Dashboard   Init  .Py"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Dashboard Backend Services"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Dashboard Frontend Vite"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Kis Tr Id Init__"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Tests Conftest.Py"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Dashboard Backend Requirements"
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

- **Why does `series()` connect `Tests Reporting Analytics` to `Docs Superpowers Reporting`, `Backtesting Reporting Frontend`, `Raw Ksdq Csv`, `Tests Dashboard Backend`, `Backtesting Reporting Tests`, `Backtesting Strategies Tests`, `Docs Superpowers Plans`, `Tests Test Run.Py Engine`, `Docs Superpowers Portfolio`, `Docs Superpowers Strategy`, `Tests Reporting Test_Builder`, `Dashboard Frontend App`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Equity Latest Quarter` connect `Backtesting Reporting Frontend` to `Docs Superpowers Reporting`, `Raw Ksdq Csv`, `Tests Dashboard Backend`, `Backtesting Reporting Tests`, `Docs Superpowers Plans`, `Tests Test Run.Py Engine`, `Docs Superpowers Portfolio`, `Docs Superpowers Strategy`, `Tests Reporting Analytics`, `Tests Reporting Test_Builder`, `Dashboard Frontend App`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Foreign Ownership Ratio` connect `Backtesting Reporting Frontend` to `Docs Superpowers Reporting`, `Raw Ksdq Csv`, `Tests Dashboard Backend`, `Backtesting Reporting Tests`, `Docs Superpowers Plans`, `Tests Test Run.Py Engine`, `Docs Superpowers Portfolio`, `Docs Superpowers Strategy`, `Tests Reporting Analytics`, `Dashboard Frontend App`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `Mkt Typ` (e.g. with `factor.py` and `catalog.py`) actually correct?**
  _`Mkt Typ` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 81 inferred relationships involving `series()` (e.g. with `quantile_returns()` and `rank_ic()`) actually correct?**
  _`series()` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `DataCatalog.get()` (e.g. with `DataLoader.load()` and `IngestJob.run()`) actually correct?**
  _`DataCatalog.get()` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `Shares Outstanding Outstanding` (e.g. with `__init__.py` and `perf.py`) actually correct?**
  _`Shares Outstanding Outstanding` has 73 INFERRED edges - model-reasoned connections that need verification._