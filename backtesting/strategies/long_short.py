from __future__ import annotations

from dataclasses import dataclass

from backtesting.construction.long_short import LongShortTopBottom
from backtesting.signals.momentum import MomentumSignalProducer

from .composable import ComposableStrategy


@dataclass(slots=True)
class MomentumLongShort(ComposableStrategy):
    top_n: int = 20
    lookback: int = 20
    bottom_n: int | None = None

    def __post_init__(self) -> None:
        bottom_n = self.top_n if self.bottom_n is None else self.bottom_n
        self.signal_producer = MomentumSignalProducer(lookback=self.lookback)
        self.construction_rule = LongShortTopBottom(
            top_n=self.top_n,
            bottom_n=bottom_n,
        )
