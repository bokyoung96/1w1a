from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from backtesting.construction.base import ConstructionResult
    from backtesting.data import MarketData
    from backtesting.signals.base import SignalBundle


@dataclass(frozen=True, slots=True)
class PositionPlan:
    target_weights: pd.DataFrame
    bucket_ledger: pd.DataFrame
    bucket_meta: dict[str, pd.DataFrame | pd.Series] = field(default_factory=dict)
    validation: dict[str, object] | None = None


class PositionPolicy(ABC):
    @abstractmethod
    def apply(
        self,
        construction: ConstructionResult,
        market: MarketData,
        bundle: SignalBundle,
    ) -> PositionPlan:
        raise NotImplementedError
