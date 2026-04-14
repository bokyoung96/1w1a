# Backtesting Run.Py Universe

> 32 nodes · cohesion 0.12

## Key Concepts

- **run.py** (13 connections) — `backtesting/run.py`
- **.run()** (12 connections) — `backtesting/run.py`
- **BacktestRunner** (11 connections) — `backtesting/run.py`
- **run.py** (8 connections) — `dashboard/run.py`
- **main()** (7 connections) — `dashboard/run.py`
- **RunReport** (7 connections) — `backtesting/run.py`
- **UniverseSpec** (7 connections) — `backtesting/universe.py`
- **RunConfig** (6 connections) — `backtesting/run.py`
- **UniverseRegistry** (6 connections) — `backtesting/universe.py`
- **universe.py** (5 connections) — `backtesting/universe.py`
- **build_frontend()** (5 connections) — `dashboard/run.py`
- **launch_dashboard()** (4 connections) — `dashboard/run.py`
- **build_parser()** (3 connections) — `dashboard/run.py`
- **._ensure_parquet()** (2 connections) — `backtesting/run.py`
- **._resolve_dataset_ids()** (2 connections) — `backtesting/run.py`
- **._resolve_universe_spec()** (2 connections) — `backtesting/run.py`
- **_build_run_config()** (2 connections) — `dashboard/run.py`
- **_install_frontend_dependencies()** (2 connections) — `dashboard/run.py`
- **_needs_npm_install()** (2 connections) — `dashboard/run.py`
- **_resolve_effective_config()** (2 connections) — `backtesting/run.py`
- **_resolve_load_start()** (2 connections) — `backtesting/run.py`
- **_resolve_npm_command()** (2 connections) — `dashboard/run.py`
- **_schedule()** (2 connections) — `backtesting/run.py`
- **_trim_plan_to_display_range()** (2 connections) — `backtesting/run.py`
- **_trim_result_to_display_range()** (2 connections) — `backtesting/run.py`
- *... and 7 more nodes in this community*

## Relationships

- [[Backtesting Strategies Construction]] (4 shared connections)
- [[Backtesting Strategy Catalog]] (3 shared connections)
- [[Backtesting Reporting Writer]] (1 shared connections)
- [[Dashboard Backend Services]] (1 shared connections)

## Source Files

- `backtesting/__init__.py`
- `backtesting/run.py`
- `backtesting/universe.py`
- `dashboard/run.py`

## Audit Trail

- EXTRACTED: 109 (84%)
- INFERRED: 20 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*