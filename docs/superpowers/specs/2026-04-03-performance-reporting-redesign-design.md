# Performance Reporting Redesign Design

**Date:** 2026-04-03
**Status:** Proposed
**Scope:** `backtesting.reporting` PDF-first redesign for single-run tear sheets and multi-run comparison reports

## Goal

Replace the current flat HTML-to-PDF export with a PDF-first reporting system that:

- produces a polished single-run institutional tear sheet
- produces a research-style multi-run comparison report
- uses `qw_BM` with `KOSPI200` as the default benchmark
- adds benchmark-aware performance analytics, rolling statistics, holdings breadth, and WICS sector analysis
- fits into the existing object-oriented reporting package without turning the module into a script pile

## Why The Current Output Fails

The current report output is functional but not credible as an investment report.

- The PDF is derived from a generic HTML page instead of being designed as an actual document.
- Plots are rendered as a loose list instead of a narrative built from page-level subplot compositions.
- Benchmark context is missing from both metrics and visuals.
- The summary table exposes raw floats and long run ids instead of readable investment statistics.
- The document lacks rolling diagnostics, holdings breadth, sector analysis, and drawdown episode detail.
- HTML and PDF share the same weak structure, so both outputs inherit the same layout problems.

The redesign must treat PDF quality as the primary standard and HTML as a secondary output.

## External Reference Direction

The target style will borrow from three established tearsheet patterns:

- QuantConnect LEAN: rolling Sharpe and rolling beta panels, benchmark overlays, crisis/focus plot mentality
- QSTrader: tight risk/performance subplot composition with rolling diagnostics directly under the equity view
- QuantStats-style tearsheets: benchmark-relative metrics, monthly heatmaps, return distribution and drawdown summaries

The redesign should not copy any one source exactly. It should combine their strengths into a cleaner Korean equity workflow that matches the repo’s data model.

## Product Shape

The reporting system will support two distinct PDF products built on top of one shared analytics engine.

### 1. Single-Run Tear Sheet

Audience: PM, researcher, allocator

Intent:

- understand one strategy deeply
- compare it against `KOSPI200`
- see performance, risk, exposures, and current holdings in one document

Tone:

- institutional
- concise
- graph-first
- first page should answer most portfolio-review questions

### 2. Multi-Run Comparison Report

Audience: researcher, PM, strategy reviewer

Intent:

- compare multiple strategies on a common benchmark and time range
- identify performance and risk differences quickly
- inspect cross-strategy exposures and positioning differences

Tone:

- research-style
- comparative
- more tables and ranked views than the single-run tear sheet

## Benchmark Policy

Default benchmark is `KOSPI200` sourced from `qw_BM`.

Design requirements:

- benchmark selection must be explicit and encapsulated
- the reporting layer should not hardcode spreadsheet cell positions inside rendering code
- the benchmark selector must resolve a human-facing name and an internal code from the benchmark dataset
- single-run and multi-run reports must both use the same benchmark selection logic

Initial default:

- benchmark dataset: `qw_BM`
- benchmark series: `IKS200 / 코스피 200`

Future-safe requirement:

- the design should allow additional benchmark selectors later without rewriting the reporting engine

## Data Sources

Existing sources already available in the repo:

- run bundle series: equity, returns, turnover, monthly returns
- run bundle positions: weights, qty, latest weights, latest qty
- raw/parquet benchmark source: `qw_BM`
- raw/parquet sector source: `qw_wics_sec_big`
- optional validation artifacts: `validation.json`, `split.json`, `factor.json`

Additional reporting data must be derived from these assets instead of introducing a separate reporting-only datastore.

## Object-Oriented Architecture

The redesign will keep the current reporting package structure but insert a proper analytics layer between file reading and rendering.

### Core Domain Objects

#### `BenchmarkSpec`

Responsibility:

- describe which benchmark to load
- carry user-facing label and internal source identifier

Examples:

- `BenchmarkSpec.default_kospi200()`
- `BenchmarkSpec(code="IKS200", name="KOSPI200")`

#### `BenchmarkSeries`

Responsibility:

- hold aligned benchmark price/equity/return views
- provide benchmark-relative calculations to higher objects

#### `PerformanceMetrics`

Responsibility:

- calculate headline metrics for one strategy versus one benchmark

Metrics to include:

- cumulative return
- CAGR
- annual volatility
- Sharpe
- Sortino
- Calmar
- max drawdown
- final equity
- avg turnover
- alpha
- beta
- tracking error
- information ratio
- upside/downside capture if feasible from aligned daily return series

#### `RollingMetrics`

Responsibility:

- hold rolling series used by charts and appendix tables

Metrics to include:

- rolling Sharpe
- rolling beta
- rolling annual volatility
- rolling excess return

Window defaults:

- daily data, 252-trading-day window

#### `DrawdownStats`

Responsibility:

- hold underwater series and episode summaries

Metrics to include:

- underwater series
- worst drawdown episodes
- drawdown start/trough/recovery dates
- drawdown duration and recovery days

#### `ExposureSnapshot`

Responsibility:

- represent current and historical positioning shape

Fields to include:

- holdings count time series
- gross and net exposure if derivable from weights
- latest top holdings
- latest top sectors
- sector breadth
- sector concentration proxy

#### `SectorSnapshot`

Responsibility:

- map holdings/weights through `qw_wics_sec_big`
- produce sector weights and counts through time

Outputs:

- latest weighted sector exposure
- latest equal-count sector exposure
- sector concentration time series
- sector breadth time series

#### `PerformanceSnapshot`

Responsibility:

- aggregate all analytics for one run
- act as the single input object for single-run rendering

Contains:

- run metadata
- strategy series
- benchmark series
- `PerformanceMetrics`
- `RollingMetrics`
- `DrawdownStats`
- `ExposureSnapshot`
- `SectorSnapshot`

#### `ComparisonSnapshot`

Responsibility:

- aggregate multiple `PerformanceSnapshot` objects for comparison rendering
- produce ranked summary tables and common-axis aligned series

## Rendering Architecture

The rendering stack should remain layered and narrow in responsibility.

### Figure Builders

#### `TearsheetFigureBuilder`

Responsibility:

- create page-level subplot figures for a single strategy

Required figure groups:

- performance page
- rolling diagnostics page
- distribution and calendar page
- holdings and sector page

#### `ComparisonFigureBuilder`

Responsibility:

- create page-level subplot figures for multiple strategies on common scales

Required figure groups:

- performance comparison page
- rolling comparison page
- exposure comparison page
- appendix mini-panels

### Table Builders

#### `TearsheetTableBuilder`

Responsibility:

- build human-readable, formatted single-run tables

Tables:

- performance summary
- drawdown episodes
- top holdings
- sector weights
- validation appendix

#### `ComparisonTableBuilder`

Responsibility:

- build cross-strategy tables

Tables:

- ranked summary metrics
- benchmark-relative metrics
- latest holdings count and turnover comparison
- sector comparison summary

### Document Composers

#### `TearsheetComposer`

Responsibility:

- assemble single-run context for HTML/PDF templates

#### `ComparisonComposer`

Responsibility:

- assemble multi-run context for HTML/PDF templates

### Renderers

Keep:

- `HtmlRenderer`
- `PdfRenderer`

Change:

- renderers should become thin output layers receiving pre-built context and asset paths
- HTML should no longer decide report semantics
- PDF quality drives page composition and visual hierarchy

## PDF Page Layouts

### Single-Run Tear Sheet Layout

#### Page 1: Executive Performance

- report title, strategy label, period, benchmark label
- metric cards:
  - CAGR
  - Sharpe
  - Sortino
  - Calmar
  - MDD
  - Volatility
  - Alpha
  - Beta
- main subplot block:
  - cumulative return/equity vs `KOSPI200`
  - drawdown or underwater directly below it

Intent:

- first page should answer “did it outperform, at what cost, and how painful was the ride?”

#### Page 2: Rolling Diagnostics

- rolling Sharpe
- rolling beta
- rolling annualized volatility
- holdings count time series

Intent:

- show whether quality and market sensitivity were stable through time

#### Page 3: Return Shape

- monthly return heatmap
- return distribution
- yearly returns vs benchmark
- turnover time series if space allows

Intent:

- show seasonal shape, skew, and year-by-year behavior

#### Page 4: Holdings And Sector Structure

- top holdings table
- top sector weights
- sector breadth over time
- sector concentration or sector mix subplot

Intent:

- show where the strategy is taking risk now and structurally

#### Page 5+: Appendix

- worst drawdown episodes
- latest quantities / weights
- validation notes
- split/factor appendix when present

### Multi-Run Comparison Layout

#### Page 1: Executive Comparison

- compared strategies and benchmark
- ranked metric table
- summary callouts by metric leadership

#### Page 2: Performance Comparison

- cumulative return vs `KOSPI200`
- comparative drawdown

#### Page 3: Rolling Comparison

- rolling Sharpe by strategy
- rolling beta by strategy
- rolling vol or rolling excess return

#### Page 4: Exposure Comparison

- holdings count time series
- turnover comparison
- sector exposure comparison

#### Page 5+: Per-Run Appendix

- mini summary tables
- latest holdings and sector tables per strategy

## Visual Direction

The redesign must look intentional and contemporary, not like a default notebook export.

Visual rules:

- PDF-first layout with strong hierarchy and whitespace
- cards and sections should feel editorial, not dashboard-y
- readable numeric formatting with percentages, decimals, and thousands separators
- subplot grouping should tell a story instead of dumping charts
- benchmark should appear as a clear reference line or comparison trace
- legends and titles should be concise
- use a restrained institutional palette with one accent color and one benchmark color
- sector visuals should favor clarity over novelty

What to avoid:

- raw dataframe dumps as core content
- long run ids as display labels
- giant tables with no ranking or formatting
- one-plot-per-file mentality in the final PDF
- iframe-led report structure

## Analytics Requirements

### Must-Have Metrics

- cumulative return
- CAGR
- annualized volatility
- Sharpe
- Sortino
- Calmar
- max drawdown
- final equity
- average turnover
- beta vs benchmark
- alpha vs benchmark
- information ratio

### Must-Have Charts

- cumulative return/equity vs benchmark
- drawdown paired with return/equity in subplot form
- underwater curve
- rolling Sharpe
- rolling beta
- return distribution
- monthly heatmap
- yearly return comparison
- holdings count time series
- top holdings
- sector analysis using `qw_wics_sec_big`

### Nice-To-Have If Cheap

- rolling excess return
- rolling volatility
- drawdown episode table with sparkline-like formatting
- sector concentration metric such as Herfindahl-style proxy

## Repo Integration Plan

Likely file additions:

- `backtesting/reporting/analytics.py`
- `backtesting/reporting/benchmarks.py`
- `backtesting/reporting/snapshots.py`
- `backtesting/reporting/figures.py`
- `backtesting/reporting/comparison_figures.py`
- `backtesting/reporting/tables_single.py`
- `backtesting/reporting/tables_comparison.py`
- new or revised templates under `backtesting/reporting/templates/`

Likely file modifications:

- `backtesting/reporting/models.py`
- `backtesting/reporting/reader.py`
- `backtesting/reporting/builder.py`
- `backtesting/reporting/html.py`
- `backtesting/reporting/pdf.py`
- `backtesting/reporting/__init__.py`
- `backtesting/reporting/cli.py`
- `tests/reporting/*`

Boundary rule:

- analytics objects compute
- builders orchestrate
- figure builders draw
- composers format context
- renderers write files

## Testing Strategy

Testing must protect both analytics correctness and output structure.

### Analytics Tests

- benchmark selector resolves `KOSPI200`
- rolling Sharpe and beta calculations align on daily windows
- drawdown episode extraction is correct
- holdings count and sector aggregation are correct on toy inputs
- benchmark-relative metrics handle missing dates safely

### Builder Tests

- single-run bundle includes expected figures and tables
- comparison bundle includes expected cross-strategy assets
- labels are human-readable and formatted

### Renderer Tests

- HTML and PDF context render without missing keys
- PNG-first plots are preferred when export succeeds
- PDF still builds when optional appendix blocks are absent

### Regression Tests

- single-run report from a toy run produces the expected assets
- multi-run report from two toy runs produces the expected assets

## Non-Goals

- interactive browser dashboard redesign
- adding live benchmark download logic
- replacing the backtest engine
- adding commentary text generation or LLM-authored narrative inside the PDF

## Risks

- benchmark extraction from `qw_BM` must be handled carefully because the source is Excel-based and should not leak spreadsheet-specific parsing assumptions into rendering code
- plot export relies on `kaleido` and a working headless Chrome path
- adding too many metrics can create a crowded PDF if formatting discipline is weak
- sector analysis can become noisy unless grouped and ranked carefully

## Success Criteria

The redesign is successful if:

- a single-run PDF looks like a real tear sheet instead of an HTML printout
- a multi-run PDF makes cross-strategy ranking obvious within the first two pages
- `KOSPI200` benchmark context is present in both metrics and charts
- rolling risk diagnostics, drawdown analysis, holdings breadth, and WICS sector analysis are all present
- the code remains object-oriented, testable, and consistent with the existing `backtesting.reporting` package
