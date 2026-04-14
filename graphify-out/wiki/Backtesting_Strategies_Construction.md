# Backtesting Strategies Construction

> 88 nodes · cohesion 0.05

## Key Concepts

- **SignalBundle** (17 connections) — `backtesting/signals/base.py`
- **PositionPlan** (16 connections) — `backtesting/policy/base.py`
- **ComposableStrategy** (16 connections) — `backtesting/strategies/composable.py`
- **ConstructionResult** (15 connections) — `backtesting/construction/base.py`
- **PassThroughPolicy** (14 connections) — `backtesting/policy/pass_through.py`
- **RegisteredStrategy** (13 connections) — `backtesting/strategies/base.py`
- **PositionPolicy** (12 connections) — `backtesting/policy/base.py`
- **ConstructionRule** (9 connections) — `backtesting/strategies/composable.py`
- **SignalProducer** (9 connections) — `backtesting/strategies/composable.py`
- **registry.py** (9 connections) — `backtesting/strategies/registry.py`
- **LongOnlyTopN** (9 connections) — `backtesting/construction/long_only.py`
- **base.py** (8 connections) — `backtesting/policy/base.py`
- **base.py** (8 connections) — `backtesting/strategies/base.py`
- **composable.py** (8 connections) — `backtesting/strategies/composable.py`
- **_Breakout52WeekConstructionRule** (7 connections) — `backtesting/strategies/breakout_simple.py`
- **Breakout52WeekSignalProducer** (7 connections) — `backtesting/strategies/breakout_simple.py`
- **Breakout52WeekSimple** (7 connections) — `backtesting/strategies/breakout_simple.py`
- **breakout_simple.py** (7 connections) — `backtesting/strategies/breakout_simple.py`
- **Breakout52WeekStaged** (6 connections) — `backtesting/strategies/breakout_staged.py`
- **__init__.py** (6 connections) — `backtesting/strategies/__init__.py`
- **LongShortTopBottom** (6 connections) — `backtesting/construction/long_short.py`
- **MomentumTopN** (6 connections) — `backtesting/strategies/momentum.py`
- **OpFwdYieldTopN** (6 connections) — `backtesting/strategies/op_fwd.py`
- **SectorNeutralTopBottom** (6 connections) — `backtesting/construction/sector_neutral.py`
- **BudgetPreservingStagedPolicy** (6 connections) — `backtesting/policy/staged.py`
- *... and 63 more nodes in this community*

## Relationships

- [[Backtesting Execution Catalog]] (12 shared connections)
- [[Backtesting Strategy Base]] (5 shared connections)
- [[Backtesting Run.Py Universe]] (4 shared connections)

## Source Files

- `backtesting/construction/__init__.py`
- `backtesting/construction/base.py`
- `backtesting/construction/long_only.py`
- `backtesting/construction/long_short.py`
- `backtesting/construction/sector_neutral.py`
- `backtesting/policy/__init__.py`
- `backtesting/policy/base.py`
- `backtesting/policy/pass_through.py`
- `backtesting/policy/staged.py`
- `backtesting/signals/__init__.py`
- `backtesting/signals/base.py`
- `backtesting/signals/momentum.py`
- `backtesting/signals/op_fwd.py`
- `backtesting/strategies/__init__.py`
- `backtesting/strategies/base.py`
- `backtesting/strategies/breakout_simple.py`
- `backtesting/strategies/breakout_staged.py`
- `backtesting/strategies/composable.py`
- `backtesting/strategies/momentum.py`
- `backtesting/strategies/op_fwd.py`

## Audit Trail

- EXTRACTED: 238 (63%)
- INFERRED: 141 (37%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*