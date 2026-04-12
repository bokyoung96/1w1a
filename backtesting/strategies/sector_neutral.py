from __future__ import annotations

from dataclasses import dataclass

from backtesting.catalog import DatasetId
from backtesting.construction.sector_neutral import SectorNeutralTopBottom
from backtesting.data import MarketData
from backtesting.signals.base import SignalBundle

from .composable import ComposableStrategy


@dataclass(frozen=True, slots=True)
class MomentumSectorSignalProducer:
    lookback: int = 20

    @property
    def datasets(self) -> tuple[DatasetId, ...]:
        return (DatasetId.QW_ADJ_C, DatasetId.QW_WICS_SEC_BIG)

    def build(self, market: MarketData) -> SignalBundle:
        close = market.frames["close"]
        sector = market.frames["sector_big"]
        alpha = close.pct_change(self.lookback, fill_method=None)
        tradable = alpha.notna() & sector.reindex(index=alpha.index, columns=alpha.columns).notna()
        return SignalBundle(
            alpha=alpha,
            context={
                "close": close,
                "tradable": tradable,
                "sector": sector,
            },
        )


@dataclass(slots=True)
class MomentumSectorNeutral(ComposableStrategy):
    top_n: int = 20
    lookback: int = 20
    bottom_n: int | None = None

    def __post_init__(self) -> None:
        bottom_n = self.top_n if self.bottom_n is None else self.bottom_n
        self.signal_producer = MomentumSectorSignalProducer(lookback=self.lookback)
        self.construction_rule = SectorNeutralTopBottom(
            top_n=self.top_n,
            bottom_n=bottom_n,
        )
