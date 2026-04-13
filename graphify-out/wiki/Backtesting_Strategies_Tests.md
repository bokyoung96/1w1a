# Backtesting Strategies Tests

> 112 nodes · cohesion 0.04

## Key Concepts

- **MarketData** (23 connections) — `backtesting/data/loader.py`
- **test_registry.py** (20 connections) — `tests/strategies/test_registry.py`
- **SignalBundle** (18 connections) — `backtesting/signals/base.py`
- **base.py** (18 connections) — `backtesting/policy/base.py`
- **PositionPolicy.apply()** (18 connections) — `backtesting/policy/base.py`
- **TRRegistry.all()** (17 connections) — `kis/tr_id/register.py`
- **test_staged.py** (15 connections) — `tests/policy/test_staged.py`
- **RegisteredStrategy.build_plan()** (15 connections) — `backtesting/strategies/base.py`
- **ConstructionResult** (14 connections) — `backtesting/construction/base.py`
- **__init__.py** (14 connections) — `backtesting/data/__init__.py`
- **BudgetPreservingStagedPolicy** (13 connections) — `backtesting/policy/staged.py`
- **composable.py** (13 connections) — `backtesting/strategies/composable.py`
- **base.py** (11 connections) — `backtesting/construction/base.py`
- **base.py** (11 connections) — `backtesting/strategies/base.py`
- **test_rules.py** (11 connections) — `tests/construction/test_rules.py`
- **build_strategy()** (11 connections) — `backtesting/strategies/registry.py`
- **pass_through.py** (10 connections) — `backtesting/policy/pass_through.py`
- **registry.py** (10 connections) — `backtesting/strategies/registry.py`
- **validate_position_plan()** (10 connections) — `backtesting/validation/portfolio.py`
- **test_staged_policy_never_exceeds_base_budget_when_all_rules_fire_each_bar()** (10 connections) — `tests/policy/test_staged.py`
- **test_staged_policy_releases_budget_over_multiple_buckets_and_handles_signed_base_weights()** (10 connections) — `tests/policy/test_staged.py`
- **StagedRuleSet** (9 connections) — `backtesting/policy/staged.py`
- **base.py** (9 connections) — `backtesting/signals/base.py`
- **test_staged_policy_clears_active_buckets_when_base_weight_is_zero()** (9 connections) — `tests/policy/test_staged.py`
- **test_staged_policy_resets_progress_on_sign_flip()** (9 connections) — `tests/policy/test_staged.py`
- *... and 87 more nodes in this community*

## Relationships

- [[Raw Ksdq Csv]] (56 shared connections)
- [[Tests Reporting Analytics]] (18 shared connections)
- [[Docs Superpowers Portfolio]] (14 shared connections)
- [[Tests Test Run.Py Engine]] (14 shared connections)
- [[Backtesting Reporting Frontend]] (13 shared connections)
- [[Tests Reporting Test_Builder]] (8 shared connections)
- [[Docs Superpowers Strategy]] (6 shared connections)
- [[Docs Superpowers Plans]] (5 shared connections)
- [[Docs Superpowers Reporting]] (5 shared connections)
- [[Backtesting Reporting Tests]] (4 shared connections)
- [[Tests Dashboard Backend]] (4 shared connections)

## Source Files

- `backtesting/construction/base.py`
- `backtesting/construction/long_only.py`
- `backtesting/construction/long_short.py`
- `backtesting/construction/sector_neutral.py`
- `backtesting/data/__init__.py`
- `backtesting/data/loader.py`
- `backtesting/policy/base.py`
- `backtesting/policy/pass_through.py`
- `backtesting/policy/staged.py`
- `backtesting/signals/base.py`
- `backtesting/signals/momentum.py`
- `backtesting/signals/op_fwd.py`
- `backtesting/strategies/__init__.py`
- `backtesting/strategies/base.py`
- `backtesting/strategies/breakout_simple.py`
- `backtesting/strategies/composable.py`
- `backtesting/strategies/momentum.py`
- `backtesting/strategies/op_fwd.py`
- `backtesting/strategies/registry.py`
- `backtesting/strategy/base.py`

## Audit Trail

- EXTRACTED: 292 (44%)
- INFERRED: 375 (56%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*