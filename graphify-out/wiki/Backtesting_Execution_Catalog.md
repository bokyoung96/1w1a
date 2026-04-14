# Backtesting Execution Catalog

> 63 nodes · cohesion 0.06

## Key Concepts

- **Public strategy exports.** (41 connections) — `backtesting/strategy/__init__.py`
- **DataCatalog** (20 connections) — `backtesting/catalog/catalog.py`
- **BacktestEngine** (8 connections) — `backtesting/engine/core.py`
- **RebalanceSchedule** (8 connections) — `backtesting/execution/schedule.py`
- **DatasetGroup** (7 connections) — `backtesting/catalog/enums.py`
- **DatasetId** (7 connections) — `backtesting/catalog/enums.py`
- **catalog.py** (7 connections) — `backtesting/catalog/catalog.py`
- **enums.py** (7 connections) — `backtesting/catalog/enums.py`
- **schedule.py** (6 connections) — `backtesting/execution/schedule.py`
- **DatasetGroups** (6 connections) — `backtesting/catalog/groups.py`
- **Enum** (5 connections)
- **__init__.py** (5 connections) — `backtesting/catalog/__init__.py`
- **core.py** (5 connections) — `backtesting/engine/core.py`
- **session.py** (5 connections) — `backtesting/validation/session.py`
- **DatasetSpec** (5 connections) — `backtesting/catalog/specs.py`
- **._rebalance()** (4 connections) — `backtesting/engine/core.py`
- **.run()** (4 connections) — `backtesting/engine/core.py`
- **CostModel** (4 connections) — `backtesting/execution/costs.py`
- **groups.py** (4 connections) — `backtesting/catalog/groups.py`
- **specs.py** (4 connections) — `backtesting/catalog/specs.py`
- **costs.py** (4 connections) — `backtesting/execution/costs.py`
- **__init__.py** (4 connections) — `backtesting/execution/__init__.py`
- **__init__.py** (4 connections) — `backtesting/validation/__init__.py`
- **split.py** (4 connections) — `backtesting/validation/split.py`
- **CustomSchedule** (4 connections) — `backtesting/execution/schedule.py`
- *... and 38 more nodes in this community*

## Relationships

- [[Backtesting Strategies Construction]] (12 shared connections)
- [[Backtesting Strategy Base]] (7 shared connections)
- [[Backtesting Data Ingest]] (4 shared connections)
- [[Backtesting Run.Py Universe]] (3 shared connections)
- [[Backtesting Reporting Benchmarks]] (3 shared connections)
- [[Backtesting Reporting Builder]] (3 shared connections)
- [[Backtesting Analytics Factor]] (1 shared connections)

## Source Files

- `backtesting/catalog/__init__.py`
- `backtesting/catalog/catalog.py`
- `backtesting/catalog/enums.py`
- `backtesting/catalog/groups.py`
- `backtesting/catalog/specs.py`
- `backtesting/engine/__init__.py`
- `backtesting/engine/core.py`
- `backtesting/engine/result.py`
- `backtesting/execution/__init__.py`
- `backtesting/execution/costs.py`
- `backtesting/execution/fill.py`
- `backtesting/execution/schedule.py`
- `backtesting/strategy/__init__.py`
- `backtesting/validation/__init__.py`
- `backtesting/validation/portfolio.py`
- `backtesting/validation/session.py`
- `backtesting/validation/split.py`

## Audit Trail

- EXTRACTED: 182 (69%)
- INFERRED: 81 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*