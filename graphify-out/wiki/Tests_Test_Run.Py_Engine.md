# Tests Test Run.Py Engine

> 113 nodes · cohesion 0.05

## Key Concepts

- **DataCatalog.default()** (63 connections) — `backtesting/catalog/catalog.py`
- **BacktestEngine.run()** (53 connections) — `backtesting/engine/core.py`
- **ParquetStore.write()** (40 connections) — `backtesting/data/store.py`
- **DataLoader.load()** (35 connections) — `backtesting/data/loader.py`
- **ParquetStore** (32 connections) — `backtesting/data/store.py`
- **BacktestRunner** (31 connections) — `backtesting/run.py`
- **BacktestRunner.run()** (23 connections) — `backtesting/run.py`
- **RunConfig** (22 connections) — `backtesting/run.py`
- **BacktestEngine** (20 connections) — `backtesting/engine/core.py`
- **CostModel** (18 connections) — `backtesting/execution/costs.py`
- **IngestJob** (17 connections) — `backtesting/ingest/pipeline.py`
- **DataLoader** (16 connections) — `backtesting/data/loader.py`
- **LoadRequest** (15 connections) — `backtesting/data/loader.py`
- **test_core.py** (15 connections) — `tests/engine/test_core.py`
- **DataCatalog** (14 connections) — `backtesting/catalog/catalog.py`
- **PositionPlan** (12 connections) — `backtesting/policy/base.py`
- **ValidationSession** (12 connections) — `backtesting/validation/session.py`
- **_load_default_frame()** (12 connections) — `backtesting/reporting/benchmarks.py`
- **BacktestResult** (11 connections) — `backtesting/engine/result.py`
- **IngestJob.run()** (9 connections) — `backtesting/ingest/pipeline.py`
- **test_runner_executes_strategy_plan_and_stores_position_plan()** (9 connections) — `tests/test_run.py`
- **test_runner_rejects_invalid_position_plan_before_engine_execution()** (9 connections) — `tests/test_run.py`
- **test_runner_uses_warmup_history_but_trims_persisted_outputs()** (9 connections) — `tests/test_run.py`
- **BacktestEngine._rebalance()** (8 connections) — `backtesting/engine/core.py`
- **default_repositories_for_universe()** (8 connections) — `backtesting/reporting/benchmarks.py`
- *... and 88 more nodes in this community*

## Relationships

- [[Raw Ksdq Csv]] (58 shared connections)
- [[Docs Superpowers Kosdaq150]] (56 shared connections)
- [[Docs Superpowers Plans]] (38 shared connections)
- [[Docs Superpowers Reporting]] (25 shared connections)
- [[Tests Dashboard Backend]] (21 shared connections)
- [[Tests Reporting Analytics]] (18 shared connections)
- [[Docs Superpowers Policy]] (15 shared connections)
- [[Docs Superpowers Strategy]] (10 shared connections)
- [[Backtesting Reporting Frontend]] (10 shared connections)
- [[Docs Superpowers Breakout]] (8 shared connections)
- [[Docs Superpowers Live]] (8 shared connections)
- [[Docs Superpowers Research]] (4 shared connections)

## Source Files

- `backtesting/catalog/catalog.py`
- `backtesting/catalog/groups.py`
- `backtesting/data/loader.py`
- `backtesting/data/store.py`
- `backtesting/engine/core.py`
- `backtesting/engine/result.py`
- `backtesting/execution/costs.py`
- `backtesting/ingest/io.py`
- `backtesting/ingest/normalize.py`
- `backtesting/ingest/pipeline.py`
- `backtesting/policy/base.py`
- `backtesting/reporting/benchmarks.py`
- `backtesting/run.py`
- `backtesting/validation/session.py`
- `tests/catalog/test_groups.py`
- `tests/data/test_loader.py`
- `tests/engine/test_core.py`
- `tests/execution/test_costs.py`
- `tests/ingest/test_pipeline.py`
- `tests/reporting/test_benchmarks.py`

## Audit Trail

- EXTRACTED: 173 (19%)
- INFERRED: 739 (81%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*