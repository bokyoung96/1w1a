# Tests Test Run.Py Engine

> 98 nodes · cohesion 0.06

## Key Concepts

- **BacktestEngine.run()** (53 connections) — `backtesting/engine/core.py`
- **test_run.py** (51 connections) — `tests/test_run.py`
- **ParquetStore.write()** (40 connections) — `backtesting/data/store.py`
- **DataLoader.load()** (35 connections) — `backtesting/data/loader.py`
- **ParquetStore** (32 connections) — `backtesting/data/store.py`
- **BacktestRunner** (31 connections) — `backtesting/run.py`
- **main()** (26 connections) — `backtesting/run.py`
- **BacktestRunner.run()** (23 connections) — `backtesting/run.py`
- **RunConfig** (22 connections) — `backtesting/run.py`
- **BacktestEngine** (20 connections) — `backtesting/engine/core.py`
- **CostModel.calc()** (20 connections) — `backtesting/execution/costs.py`
- **CostModel** (18 connections) — `backtesting/execution/costs.py`
- **DataLoader** (16 connections) — `backtesting/data/loader.py`
- **LoadRequest** (15 connections) — `backtesting/data/loader.py`
- **test_core.py** (15 connections) — `tests/engine/test_core.py`
- **PositionPlan** (12 connections) — `backtesting/policy/base.py`
- **ValidationSession** (12 connections) — `backtesting/validation/session.py`
- **BacktestResult** (11 connections) — `backtesting/engine/result.py`
- **IngestJob.run()** (9 connections) — `backtesting/ingest/pipeline.py`
- **test_runner_executes_strategy_plan_and_stores_position_plan()** (9 connections) — `tests/test_run.py`
- **test_runner_rejects_invalid_position_plan_before_engine_execution()** (9 connections) — `tests/test_run.py`
- **test_runner_uses_warmup_history_but_trims_persisted_outputs()** (9 connections) — `tests/test_run.py`
- **BacktestEngine._rebalance()** (8 connections) — `backtesting/engine/core.py`
- **test_loader_expands_month_only_data_without_crossing_missing_months()** (8 connections) — `tests/data/test_loader.py`
- **test_loader_returns_market_data()** (8 connections) — `tests/data/test_loader.py`
- *... and 73 more nodes in this community*

## Relationships

- [[Raw Ksdq Csv]] (106 shared connections)
- [[Docs Superpowers Reporting]] (70 shared connections)
- [[Docs Superpowers Plans]] (25 shared connections)
- [[Backtesting Reporting Frontend]] (19 shared connections)
- [[Backtesting Reporting Tests]] (14 shared connections)
- [[Backtesting Strategies Tests]] (14 shared connections)
- [[Docs Superpowers Strategy]] (13 shared connections)
- [[Tests Reporting Analytics]] (13 shared connections)
- [[Tests Dashboard Backend]] (12 shared connections)
- [[Docs Superpowers Portfolio]] (4 shared connections)
- [[Tests Reporting Test_Builder]] (1 shared connections)

## Source Files

- `backtesting/data/loader.py`
- `backtesting/data/store.py`
- `backtesting/engine/core.py`
- `backtesting/engine/result.py`
- `backtesting/execution/costs.py`
- `backtesting/ingest/io.py`
- `backtesting/ingest/normalize.py`
- `backtesting/ingest/pipeline.py`
- `backtesting/policy/base.py`
- `backtesting/run.py`
- `backtesting/validation/session.py`
- `run.py`
- `tests/data/test_loader.py`
- `tests/engine/test_core.py`
- `tests/execution/test_costs.py`
- `tests/reporting/test_reader.py`
- `tests/test_report_cli.py`
- `tests/test_run.py`
- `tests/validation/test_session.py`

## Audit Trail

- EXTRACTED: 177 (21%)
- INFERRED: 652 (79%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*