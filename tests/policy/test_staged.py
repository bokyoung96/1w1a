from __future__ import annotations

import pandas as pd

from backtesting.construction.base import ConstructionResult
from backtesting.data import MarketData
from backtesting.policy.base import BUCKET_LEDGER_COLUMNS
from backtesting.policy.staged import BudgetPreservingStagedPolicy, BucketDefinition, StagedRuleSet
from backtesting.signals.base import SignalBundle
from backtesting.validation import validate_position_plan


def test_staged_policy_releases_budget_over_multiple_buckets_and_handles_signed_base_weights() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"])
    base = pd.DataFrame(
        {"LONG": [0.6, 0.6, 0.6, 0.6], "SHORT": [-0.8, -0.8, -0.8, -0.8]},
        index=index,
    )
    close = pd.DataFrame(
        {"LONG": [10.0, 10.5, 11.0, 11.5], "SHORT": [20.0, 19.5, 19.0, 18.5]},
        index=index,
    )
    construction = ConstructionResult(
        base_target_weights=base,
        selection_mask=base.ne(0.0),
        group_long_budget=None,
        group_short_budget=None,
        meta={},
    )
    bundle = SignalBundle(
        alpha=base,
        context={
            "tradable": base.notna(),
            "eligible_entry": pd.DataFrame(
                {"LONG": [True, False, False, False], "SHORT": [True, False, False, False]},
                index=index,
            ),
            "eligible_add_1": pd.DataFrame(
                {"LONG": [False, True, False, False], "SHORT": [False, True, False, False]},
                index=index,
            ),
            "eligible_add_2": pd.DataFrame(
                {"LONG": [False, False, True, False], "SHORT": [False, False, True, False]},
                index=index,
            ),
            "eligible_exit": pd.DataFrame(False, index=index, columns=base.columns),
        },
    )

    plan = BudgetPreservingStagedPolicy(
        buckets=(BucketDefinition("b0", 0.25), BucketDefinition("b1", 0.25), BucketDefinition("b2", 0.50)),
        rules=StagedRuleSet(
            entry_key="eligible_entry",
            add_keys=("eligible_add_1", "eligible_add_2"),
            exit_key="eligible_exit",
        ),
    ).apply(construction, MarketData(frames={"close": close}, universe=None, benchmark=None), bundle)

    assert tuple(plan.bucket_ledger.columns) == BUCKET_LEDGER_COLUMNS
    assert plan.target_weights["LONG"].tolist() == [0.15, 0.3, 0.6, 0.6]
    assert plan.target_weights["SHORT"].tolist() == [-0.2, -0.4, -0.8, -0.8]
    assert (plan.target_weights.abs() <= base.abs() + 1e-12).all().all()
    validate_position_plan(plan)


def test_staged_policy_clears_active_buckets_on_exit_and_allows_reentry() -> None:
    index = pd.to_datetime(
        ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06"]
    )
    base = pd.DataFrame({"A": [1.0] * len(index)}, index=index)
    close = pd.DataFrame({"A": [10.0, 10.5, 11.0, 11.5, 12.0]}, index=index)
    construction = ConstructionResult(
        base_target_weights=base,
        selection_mask=base.ne(0.0),
        group_long_budget=None,
        group_short_budget=None,
        meta={},
    )
    bundle = SignalBundle(
        alpha=base,
        context={
            "tradable": base.notna(),
            "eligible_entry": pd.DataFrame({"A": [True, False, False, True, False]}, index=index),
            "eligible_add_1": pd.DataFrame({"A": [False, True, False, False, True]}, index=index),
            "eligible_exit": pd.DataFrame({"A": [False, False, True, False, False]}, index=index),
        },
    )

    plan = BudgetPreservingStagedPolicy(
        buckets=(BucketDefinition("b0", 0.50), BucketDefinition("b1", 0.50)),
        rules=StagedRuleSet(
            entry_key="eligible_entry",
            add_keys=("eligible_add_1",),
            exit_key="eligible_exit",
        ),
    ).apply(construction, MarketData(frames={"close": close}, universe=None, benchmark=None), bundle)

    assert plan.target_weights["A"].tolist() == [0.5, 1.0, 0.0, 0.5, 1.0]
    validate_position_plan(plan)
