# Tests Reporting Analytics

> 80 nodes · cohesion 0.05

## Key Concepts

- **series()** (82 connections) — `dashboard/frontend/src/components/App.test.tsx`
- **test_snapshots.py** (27 connections) — `tests/reporting/test_snapshots.py`
- **SectorRepository** (15 connections) — `backtesting/reporting/benchmarks.py`
- **SavedRun** (14 connections) — `backtesting/reporting/models.py`
- **IngestResult.from_frame()** (14 connections) — `backtesting/ingest/report.py`
- **test_factor.py** (12 connections) — `tests/analytics/test_factor.py`
- **test_cross.py** (12 connections) — `tests/strategy/test_cross.py`
- **test_performance_snapshot_factory_builds_analytics_snapshot()** (12 connections) — `tests/reporting/test_snapshots.py`
- **RegisteredStrategy.target_weights()** (11 connections) — `backtesting/strategies/base.py`
- **test_performance_snapshot_factory_applies_korean_sector_and_stock_display_names()** (11 connections) — `tests/reporting/test_snapshots.py`
- **test_performance_snapshot_factory_uses_fixed_252_day_rolling_window()** (11 connections) — `tests/reporting/test_snapshots.py`
- **IngestResult.to_dict()** (10 connections) — `backtesting/ingest/report.py`
- **RankLongOnly** (9 connections) — `backtesting/strategy/cross.py`
- **RankLongShort** (9 connections) — `backtesting/strategy/cross.py`
- **test_performance_snapshot_factory_derives_latest_holdings_when_optional_table_missing()** (9 connections) — `tests/reporting/test_snapshots.py`
- **SectorRepository.sector_contribution_timeseries()** (8 connections) — `backtesting/reporting/benchmarks.py`
- **quantile_returns()** (7 connections) — `backtesting/analytics/factor.py`
- **summarize_perf()** (7 connections) — `backtesting/analytics/perf.py`
- **IngestResult** (6 connections) — `backtesting/ingest/report.py`
- **cross.py** (6 connections) — `backtesting/strategy/cross.py`
- **rank_ic()** (6 connections) — `backtesting/analytics/factor.py`
- **_toy_run()** (6 connections) — `tests/reporting/test_snapshots.py`
- **test_perf.py** (5 connections) — `tests/analytics/test_perf.py`
- **_load_display_name_maps()** (5 connections) — `backtesting/reporting/benchmarks.py`
- **SectorRepository._group_row_by_sector()** (5 connections) — `backtesting/reporting/benchmarks.py`
- *... and 55 more nodes in this community*

## Relationships

- [[Backtesting Reporting Frontend]] (37 shared connections)
- [[Raw Ksdq Csv]] (21 shared connections)
- [[Docs Superpowers Policy]] (20 shared connections)
- [[Docs Superpowers Plans]] (18 shared connections)
- [[Tests Test Run.Py Engine]] (18 shared connections)
- [[Docs Superpowers Reporting]] (14 shared connections)
- [[Backtesting Reporting Tests]] (14 shared connections)
- [[Backtesting Reporting Composers]] (10 shared connections)
- [[Tests Dashboard Backend]] (8 shared connections)
- [[Docs Superpowers Strategy]] (7 shared connections)
- [[Docs Superpowers Kosdaq150]] (6 shared connections)
- [[Docs Superpowers Research]] (3 shared connections)

## Source Files

- `backtesting/analytics/factor.py`
- `backtesting/analytics/perf.py`
- `backtesting/ingest/report.py`
- `backtesting/reporting/benchmarks.py`
- `backtesting/reporting/models.py`
- `backtesting/reporting/snapshots.py`
- `backtesting/strategies/base.py`
- `backtesting/strategies/breakout_staged.py`
- `backtesting/strategy/base.py`
- `backtesting/strategy/cross.py`
- `dashboard/frontend/src/components/App.test.tsx`
- `tests/analytics/test_factor.py`
- `tests/analytics/test_perf.py`
- `tests/reporting/test_benchmarks.py`
- `tests/reporting/test_snapshots.py`
- `tests/strategy/test_cross.py`

## Audit Trail

- EXTRACTED: 144 (29%)
- INFERRED: 358 (71%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*