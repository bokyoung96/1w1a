from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.policy.base import PositionPlan, PositionPolicy
from backtesting.policy.staged import BudgetPreservingStagedPolicy, BucketDefinition, StagedRuleSet
from backtesting.signals.base import SignalBundle

from .composable import ComposableStrategy
from .sector_neutral import MomentumSectorSignalProducer


@dataclass(slots=True)
class ConstructionTransitionStagedPolicy(PositionPolicy):
    delegate: BudgetPreservingStagedPolicy

    def apply(
        self,
        construction,
        market,
        bundle,
    ) -> PositionPlan:
        base = construction.base_target_weights.fillna(0.0).astype(float)
        sign = base.apply(_sign_frame)
        prev_sign = sign.shift(1, fill_value=0)
        nonzero = sign.ne(0)
        same_side = nonzero & prev_sign.eq(sign)
        entry = nonzero & ~same_side
        add_1 = same_side
        exit_mask = pd.DataFrame(False, index=base.index, columns=base.columns)

        staged_bundle = SignalBundle(
            alpha=bundle.alpha,
            context={
                **bundle.context,
                "eligible_entry": entry,
                "eligible_add_1": add_1,
                "eligible_exit": exit_mask,
            },
            meta=dict(bundle.meta),
        )
        return self.delegate.apply(
            construction=construction,
            market=market,
            bundle=staged_bundle,
        )


def _sign_frame(column: pd.Series) -> pd.Series:
    return column.map(lambda value: 1 if value > 0.0 else (-1 if value < 0.0 else 0))


@dataclass(slots=True)
class MomentumSectorNeutralStaged(ComposableStrategy):
    top_n: int = 20
    lookback: int = 20
    bottom_n: int | None = None

    def __post_init__(self) -> None:
        bottom_n = self.top_n if self.bottom_n is None else self.bottom_n
        self.signal_producer = MomentumSectorSignalProducer(lookback=self.lookback)
        from backtesting.construction.sector_neutral import SectorNeutralTopBottom

        self.construction_rule = SectorNeutralTopBottom(
            top_n=self.top_n,
            bottom_n=bottom_n,
        )
        self.position_policy = ConstructionTransitionStagedPolicy(
            delegate=BudgetPreservingStagedPolicy(
                buckets=(
                    BucketDefinition(bucket_id="entry", budget_fraction=0.5),
                    BucketDefinition(bucket_id="add_1", budget_fraction=0.5),
                ),
                rules=StagedRuleSet(
                    entry_key="eligible_entry",
                    add_keys=("eligible_add_1",),
                    exit_key="eligible_exit",
                ),
            )
        )
