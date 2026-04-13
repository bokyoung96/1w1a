# Docs Superpowers Policy

> 141 nodes · cohesion 0.03

## Key Concepts

- **2026-04-12-portfolio-construction-and-staged-policy-design.md** (126 connections) — `docs/superpowers/specs/2026-04-12-portfolio-construction-and-staged-policy-design.md`
- **MarketData** (23 connections) — `backtesting/data/loader.py`
- **test_registry.py** (20 connections) — `tests/strategies/test_registry.py`
- **SignalBundle** (18 connections) — `backtesting/signals/base.py`
- **PositionPolicy.apply()** (18 connections) — `backtesting/policy/base.py`
- **TRRegistry.all()** (17 connections) — `kis/tr_id/register.py`
- **test_staged.py** (15 connections) — `tests/policy/test_staged.py`
- **RegisteredStrategy.build_plan()** (15 connections) — `backtesting/strategies/base.py`
- **ConstructionResult** (14 connections) — `backtesting/construction/base.py`
- **BudgetPreservingStagedPolicy** (13 connections) — `backtesting/policy/staged.py`
- **test_rules.py** (11 connections) — `tests/construction/test_rules.py`
- **build_strategy()** (11 connections) — `backtesting/strategies/registry.py`
- **validate_position_plan()** (10 connections) — `backtesting/validation/portfolio.py`
- **test_staged_policy_never_exceeds_base_budget_when_all_rules_fire_each_bar()** (10 connections) — `tests/policy/test_staged.py`
- **test_staged_policy_releases_budget_over_multiple_buckets_and_handles_signed_base_weights()** (10 connections) — `tests/policy/test_staged.py`
- **StagedRuleSet** (9 connections) — `backtesting/policy/staged.py`
- **test_staged_policy_clears_active_buckets_when_base_weight_is_zero()** (9 connections) — `tests/policy/test_staged.py`
- **test_staged_policy_resets_progress_on_sign_flip()** (9 connections) — `tests/policy/test_staged.py`
- **test_staged_policy_zero_reset_is_per_symbol_with_same_day_progression()** (9 connections) — `tests/policy/test_staged.py`
- **BucketDefinition** (8 connections) — `backtesting/policy/staged.py`
- **staged.py** (8 connections) — `backtesting/policy/staged.py`
- **PassThroughPolicy.apply()** (8 connections) — `backtesting/policy/pass_through.py`
- **LongShortTopBottom** (7 connections) — `backtesting/construction/long_short.py`
- **SectorNeutralTopBottom** (7 connections) — `backtesting/construction/sector_neutral.py`
- **PassThroughPolicy** (7 connections) — `backtesting/policy/pass_through.py`
- *... and 116 more nodes in this community*

## Relationships

- [[Raw Ksdq Csv]] (48 shared connections)
- [[Docs Superpowers Reporting]] (23 shared connections)
- [[Tests Reporting Analytics]] (20 shared connections)
- [[Tests Test Run.Py Engine]] (15 shared connections)
- [[Docs Superpowers Plans]] (14 shared connections)
- [[Docs Superpowers Kosdaq150]] (13 shared connections)
- [[Backtesting Reporting Tests]] (8 shared connections)
- [[Backtesting Reporting Frontend]] (8 shared connections)
- [[Docs Superpowers Strategy]] (6 shared connections)
- [[Docs Superpowers Analytics]] (6 shared connections)
- [[Docs Superpowers Breakout]] (4 shared connections)
- [[Docs Superpowers Research]] (4 shared connections)

## Source Files

- `backtesting/construction/base.py`
- `backtesting/construction/long_only.py`
- `backtesting/construction/long_short.py`
- `backtesting/construction/sector_neutral.py`
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
- `backtesting/strategy/cross.py`

## Audit Trail

- EXTRACTED: 265 (38%)
- INFERRED: 426 (62%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*