# Backtesting Reporting Snapshots

> 46 nodes · cohesion 0.08

## Key Concepts

- **PerformanceSnapshotFactory** (24 connections) — `backtesting/reporting/snapshots.py`
- **snapshots.py** (18 connections) — `backtesting/reporting/snapshots.py`
- **PerformanceSnapshot** (17 connections) — `backtesting/reporting/snapshots.py`
- **analytics.py** (12 connections) — `backtesting/reporting/analytics.py`
- **tables_single.py** (12 connections) — `backtesting/reporting/tables_single.py`
- **SavedRun** (9 connections) — `backtesting/reporting/models.py`
- **.build()** (9 connections) — `backtesting/reporting/snapshots.py`
- **.build()** (7 connections) — `backtesting/reporting/tables_single.py`
- **._build_exposure()** (6 connections) — `backtesting/reporting/snapshots.py`
- **_ordered_columns()** (5 connections) — `backtesting/reporting/tables_single.py`
- **._latest_holdings_relative_performance()** (4 connections) — `backtesting/reporting/snapshots.py`
- **TearsheetTableBuilder** (4 connections) — `backtesting/reporting/tables_single.py`
- **DrawdownStats** (3 connections) — `backtesting/reporting/analytics.py`
- **ExposureSnapshot** (3 connections) — `backtesting/reporting/analytics.py`
- **PerformanceMetrics** (3 connections) — `backtesting/reporting/analytics.py`
- **ResearchSnapshot** (3 connections) — `backtesting/reporting/analytics.py`
- **RollingMetrics** (3 connections) — `backtesting/reporting/analytics.py`
- **SectorSnapshot** (3 connections) — `backtesting/reporting/analytics.py`
- **._build_drawdowns()** (3 connections) — `backtesting/reporting/snapshots.py`
- **._build_metrics()** (3 connections) — `backtesting/reporting/snapshots.py`
- **._compute_latest_holdings_returns()** (3 connections) — `backtesting/reporting/snapshots.py`
- **build_drawdown_episodes_table()** (3 connections) — `backtesting/reporting/tables_single.py`
- **build_sector_weights_table()** (3 connections) — `backtesting/reporting/tables_single.py`
- **build_top_holdings_table()** (3 connections) — `backtesting/reporting/tables_single.py`
- **build_validation_appendix_table()** (3 connections) — `backtesting/reporting/tables_single.py`
- *... and 21 more nodes in this community*

## Relationships

- [[Backtesting Reporting Builder]] (11 shared connections)
- [[Backtesting Reporting Benchmarks]] (5 shared connections)
- [[Dashboard Backend Services]] (5 shared connections)
- [[Backtesting Reporting Figures]] (4 shared connections)
- [[Backtesting Reporting Plots]] (2 shared connections)
- [[Backtesting Reporting Composers]] (1 shared connections)

## Source Files

- `backtesting/reporting/analytics.py`
- `backtesting/reporting/models.py`
- `backtesting/reporting/snapshots.py`
- `backtesting/reporting/tables_single.py`

## Audit Trail

- EXTRACTED: 153 (76%)
- INFERRED: 49 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*