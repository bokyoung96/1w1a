# 1w1a Stock Backtesting Design

## Goal

Build a stock-only backtesting stack for `1w1a` that:

- audits and standardizes `raw/` market and factor data
- converts raw files to parquet while preserving original stems
- separates KIS broker code into `kis/`
- adds an object-oriented `backtesting/` package for research, simulation, analytics, and validation
- supports today's main use case: daily-bar cross-sectional rebalancing
- stays extensible for time-series strategies, custom schedules, and future validation workflows

This stack is library-first and optimized for interactive window workflows.

## Scope

### In scope

- Stock data only for phase 1
- `raw -> parquet` ingestion with schema normalization and data validation reports
- Cross-sectional backtesting as the primary engine
- Time-series strategy extension points
- Long-only and long-short support
- External universe injection
- External benchmark injection
- IS/OOS split evaluation
- Bias-focused validation session after backtest
- Qlib-style performance and factor analytics

### Out of scope for phase 1

- Options backtesting
- Live trading integration inside the backtesting engine
- Full CLI-first workflow
- Full borrow inventory modeling

## Design Principles

- Keep names short, concrete, and readable.
- Prefer simple object boundaries over clever abstractions.
- Put raw data, broker code, and research code in separate layers.
- Use vectorized math where it materially improves speed.
- Keep stateful execution logic explicit when realism matters.
- Make all research-critical assumptions configurable and visible.
- Avoid naive forward-filling of low-frequency data.

## Target Layout

```text
1w1a/
  raw/
  parquet/
  kis/
  backtesting/
    catalog/
    ingest/
    data/
    strategy/
    execution/
    engine/
    analytics/
    validation/
  docs/
    superpowers/
      specs/
  root.py
```

## Layered Architecture

### `raw/`

Source CSV/XLSX files stay unchanged. This directory remains the single raw-data source of truth.

### `parquet/`

Standardized parquet outputs preserve the original stem:

- `raw/qw_adj_c.csv -> parquet/qw_adj_c.parquet`
- `raw/qw_mktcap.csv -> parquet/qw_mktcap.parquet`

The code should never invent unrelated file names for these core datasets.

### `kis/`

All non-raw existing code should move under `kis/`, including config, auth, request helpers, and future broker-facing utilities. `root.py` remains available for interactive window import bootstrap.

### `backtesting/`

This package owns research and simulation only. It must not depend on live trading behavior.

## Core Types

### `DatasetId`

An `Enum` whose values map 1:1 to the original raw stems, such as:

- `qw_adj_c`
- `qw_adj_o`
- `qw_adj_h`
- `qw_adj_l`
- `qw_v`
- `qw_mktcap`
- `qw_k200_yn`

This keeps file identity explicit and avoids stringly typed loader code.

### `DatasetSpec`

A `dataclass` that defines one dataset:

- `id`
- `stem`
- `freq`
- `kind`
- `fill`
- `validity`
- `lag`
- `dtype`
- `axis`

This is the contract between ingestion, loading, and validation.

### `DataCatalog`

Central registry for every dataset. It answers:

- how the file is loaded
- whether it is daily or low-frequency
- how it should be aligned
- whether lag is required
- how validity windows work

## Ingestion

### Goal

Convert raw files into analysis-ready parquet with auditability.

### Components

- `IngestRequest`
- `IngestResult`
- `ParquetStore`
- `IngestReport`

### Responsibilities

- read CSV/XLSX from `raw/`
- normalize date index and symbol axis
- sort and standardize dtypes
- write parquet outputs
- generate validation summaries

### Validation report contents

- row and column counts
- date range
- duplicate checks
- missing-value summary
- dtype summary
- shape summary
- axis consistency findings

## Frequency and Fill Rules

Daily data stays daily.

Low-frequency data may be expanded to daily, but never through naive unlimited forward-fill.

Each dataset must declare a validity rule. Example:

- if a value exists in March and May but not April, April stays missing unless the dataset policy explicitly says the March value is still valid in April

This avoids silent contamination from stale observations.

Each dataset may also declare a lag rule so that fundamentals and similar fields can become usable only after a configured delay. This is required to reduce look-ahead bias.

## Data Access

### `LoadRequest`

A `dataclass` describing what to load:

- datasets
- date range
- universe
- benchmark
- price mode
- alignment options

### `MarketData`

A typed bundle used by strategies and the engine. It may contain:

- open, high, low, close
- adjusted prices
- volume
- market cap
- universe masks
- factor inputs
- benchmark series

## Strategy Model

### Primary mode

Phase 1 is optimized for daily-bar cross-sectional rebalancing.

### Extension mode

The architecture must also allow time-series strategies.

### Strategy interfaces

- `BaseStrategy`
- `CrossSectionalStrategy`
- `TimeSeriesStrategy`

The final strategy output should normalize to target weights or target quantities so the engine can stay generic.

### Supported portfolio styles

- long-only
- long-short

Shorting should support both:

- a simplified research mode
- an extension path for borrow constraints and borrow costs

## Scheduling and Execution

### Rebalance schedule

Support:

- daily
- weekly
- monthly
- custom schedule injection

Custom schedules are the extension point for split execution or staged trading.

### Fill rules

Support both:

- signal at `t`, fill at `t+1` open
- signal at `t`, fill at `t` close

Default behavior should be the more realistic `t+1` open model.

### Cost model

Expose user-configurable:

- trading cost
- sell tax
- slippage
- borrow cost

These should live in a dedicated execution config object.

### Quantity model

Portfolio accounting should use `price * quantity`, not only abstract weights.

Support:

- integer quantity
- fractional quantity

Default should allow fractional quantity for research flexibility.

### Trading filters

Even when the user injects a universe, the engine must auto-filter names that are not tradable at that timestamp, including suspensions or other execution-blocked states when detectable from the available data rules.

## Engine

### `BacktestEngine`

The engine should:

- convert targets into orders
- update holdings and cash
- apply execution assumptions
- apply costs and taxes
- calculate equity and returns

It should remain as vectorized as practical without hiding state transitions that affect realism.

Long-running steps should optionally show progress via `tqdm`.

## Analytics

Performance reporting should include a general layer and a factor-research layer.

### General metrics

- cumulative return
- CAGR
- MDD
- Sharpe
- turnover
- monthly return table
- trade log
- contribution breakdown

### Benchmark-aware metrics

- excess return
- benchmark-relative curve
- with-cost and without-cost comparisons

### Factor analytics

- quantile analysis
- bucket analysis
- IC
- rank IC
- long-short spread

The style should be close to Qlib's research outputs where practical, but implemented in a form that matches `1w1a` data and architecture.

## Validation

### `ValidationSession`

Backtest results and validation results are separate outputs.

Validation is responsible for checking bias and robustness, including:

- look-ahead risk
- survivorship assumptions
- stale-value propagation
- sparse coverage
- excessive turnover
- suspicious data alignment
- missing lag settings on lag-sensitive datasets

This session should emit a validation report that can be reviewed independently of strategy return.

## IS/OOS Evaluation

### `SplitConfig`

Support:

- IS
- OOS
- later extension to walk-forward and train/valid/test

### Outputs

The split workflow should make it easy to compare:

- IS performance
- OOS performance
- metric deltas
- stability degradation

This should exist as a separate analysis utility, not as hidden engine behavior.

## API Shape

The package should be library-first:

```python
from backtesting.engine import BacktestEngine
from backtesting.strategy import CrossSectionalStrategy
```

Interactive window usage is a first-class target. `root.py` should continue to support clean imports from the repo root.

A thin CLI may be added later, but it is not the primary interface for phase 1.

## Naming Guidance

- Prefer short names with clear roles.
- Avoid inflated names like `ComprehensivePortfolioBacktestingExecutionConfiguration`.
- Favor names like `MarketData`, `LoadRequest`, `CostModel`, `SplitConfig`, `BacktestResult`.
- Keep one responsibility per class where possible.

## Reference Patterns

The design should borrow ideas, not structure blindly, from several repository styles:

- vectorized research-first engines such as `vectorbt`, `moonshot`, and `bt`
- event-driven OOP engines such as `QSTrader` and `backtrader`
- layered quant platforms such as `Qlib`

The chosen direction is a hybrid:

- parquet-backed data layer
- vectorized cross-sectional core
- explicit OOP strategy, execution, analytics, and validation layers

## Phase 1 Deliverables

- `kis/` package containing current non-raw broker code
- `backtesting/` package skeleton and core interfaces
- raw-to-parquet ingestion pipeline
- dataset catalog with policy metadata
- stock-only cross-sectional engine
- time-series strategy extension points
- general analytics
- factor analytics
- validation session
- IS/OOS split analysis helpers
- interactive-window-friendly import path support

## Success Criteria

- Raw stock datasets can be converted to parquet with validation reports.
- Parquet datasets can be loaded through typed requests and dataset metadata.
- A stock cross-sectional strategy can run end-to-end with realistic execution settings.
- Long-only and long-short both work.
- Universe and benchmark can be injected externally.
- Low-frequency data expansion does not silently fill invalid gaps.
- Validation and IS/OOS workflows can be run separately from the main backtest.
- The codebase stays object-oriented, readable, and compact in naming.
