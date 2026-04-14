# Engine & Catalog

> 71 nodes · cohesion 0.05

## Key Concepts

- **Public strategy exports.** (41 connections) — `backtesting/strategy/__init__.py`
- **DataCatalog** (20 connections) — `backtesting/catalog/catalog.py`
- **base.py** (9 connections) — `backtesting/strategy/base.py`
- **BacktestEngine** (8 connections) — `backtesting/engine/core.py`
- **RebalanceSchedule** (8 connections) — `backtesting/execution/schedule.py`
- **RankLongOnly** (7 connections) — `backtesting/strategy/cross.py`
- **DatasetGroup** (7 connections) — `backtesting/catalog/enums.py`
- **DatasetId** (7 connections) — `backtesting/catalog/enums.py`
- **catalog.py** (7 connections) — `backtesting/catalog/catalog.py`
- **enums.py** (7 connections) — `backtesting/catalog/enums.py`
- **BaseStrategy** (6 connections) — `backtesting/strategy/base.py`
- **RankLongShort** (6 connections) — `backtesting/strategy/cross.py`
- **schedule.py** (6 connections) — `backtesting/execution/schedule.py`
- **DatasetGroups** (6 connections) — `backtesting/catalog/groups.py`
- **CrossSectionalStrategy** (5 connections) — `backtesting/strategy/base.py`
- **Enum** (5 connections)
- **__init__.py** (5 connections) — `backtesting/catalog/__init__.py`
- **core.py** (5 connections) — `backtesting/engine/core.py`
- **DatasetSpec** (5 connections) — `backtesting/catalog/specs.py`
- **ThresholdTrend** (5 connections) — `backtesting/strategy/timeseries.py`
- **TimeSeriesStrategy** (4 connections) — `backtesting/strategy/base.py`
- **._rebalance()** (4 connections) — `backtesting/engine/core.py`
- **.run()** (4 connections) — `backtesting/engine/core.py`
- **CostModel** (4 connections) — `backtesting/execution/costs.py`
- **groups.py** (4 connections) — `backtesting/catalog/groups.py`
- *... and 46 more nodes in this community*

## Relationships

- No strong cross-community connections detected

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
- `backtesting/policy/__init__.py`
- `backtesting/strategy/__init__.py`
- `backtesting/strategy/base.py`
- `backtesting/strategy/cross.py`
- `backtesting/strategy/timeseries.py`

## Audit Trail

- EXTRACTED: 202 (69%)
- INFERRED: 91 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*