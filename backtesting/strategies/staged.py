from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.policy.staged import BudgetPreservingStagedPolicy, BucketDefinition, StagedRuleSet
from backtesting.signals.base import SignalBundle

from .composable import ComposableStrategy
from .sector_neutral import MomentumSectorSignalProducer


@dataclass(frozen=True, slots=True)
class MomentumStagedSectorSignalProducer(MomentumSectorSignalProducer):
    def build(self, market) -> SignalBundle:
        bundle = MomentumSectorSignalProducer.build(self, market)
        alpha = bundle.alpha
        alpha_ready = alpha.notna()
        prior_ready = alpha_ready.shift(1, fill_value=False)
        context = dict(bundle.context)
        context["eligible_entry"] = alpha_ready & ~prior_ready
        context["eligible_add_1"] = alpha_ready & prior_ready
        context["eligible_exit"] = pd.DataFrame(False, index=alpha.index, columns=alpha.columns)
        return SignalBundle(alpha=alpha, context=context, meta=dict(bundle.meta))


@dataclass(slots=True)
class MomentumSectorNeutralStaged(ComposableStrategy):
    top_n: int = 20
    lookback: int = 20
    bottom_n: int | None = None

    def __post_init__(self) -> None:
        bottom_n = self.top_n if self.bottom_n is None else self.bottom_n
        self.signal_producer = MomentumStagedSectorSignalProducer(lookback=self.lookback)
        from backtesting.construction.sector_neutral import SectorNeutralTopBottom

        self.construction_rule = SectorNeutralTopBottom(
            top_n=self.top_n,
            bottom_n=bottom_n,
        )
        self.position_policy = BudgetPreservingStagedPolicy(
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
