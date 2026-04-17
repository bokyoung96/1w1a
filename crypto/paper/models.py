from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from crypto.domain import ExecutionPlan, InstrumentId, PositionSide, PositionSnapshot


class LedgerEventType(str, Enum):
    FILL = "fill"
    FUNDING = "funding"
    MARK = "mark"


@dataclass(frozen=True, slots=True)
class PaperPosition:
    instrument: InstrumentId
    quantity: float = 0.0
    average_entry_price: float = 0.0
    mark_price: float = 0.0
    realized_pnl: float = 0.0
    funding_pnl: float = 0.0
    fees_paid: float = 0.0

    @property
    def side(self) -> PositionSide:
        if self.quantity > 0:
            return PositionSide.LONG
        if self.quantity < 0:
            return PositionSide.SHORT
        return PositionSide.FLAT

    @property
    def unrealized_pnl(self) -> float:
        if self.quantity == 0:
            return 0.0
        return self.quantity * (self.mark_price - self.average_entry_price)

    @property
    def exposure_notional(self) -> float:
        return self.quantity * self.mark_price

    def to_snapshot(self) -> PositionSnapshot:
        return PositionSnapshot(
            instrument=self.instrument,
            quantity=self.quantity,
            entry_price=self.average_entry_price,
            mark_price=self.mark_price,
        )


@dataclass(frozen=True, slots=True)
class PaperLedgerEntry:
    timestamp: datetime
    event_type: LedgerEventType
    strategy_id: str
    instrument: InstrumentId
    quantity_delta: float
    fill_price: float | None
    funding_rate: float | None
    position_quantity: float
    average_entry_price: float
    mark_price: float
    realized_pnl: float
    funding_pnl: float
    fees_paid: float
    unrealized_pnl: float
    exposure_notional: float
    equity: float


@dataclass(frozen=True, slots=True)
class PaperSessionSnapshot:
    strategy_id: str
    exchange_id: str
    execution_plan: ExecutionPlan
    started_at: datetime
    latest_timestamp: datetime | None
    starting_equity: float
    current_equity: float
    realized_pnl: float
    funding_pnl: float
    fees_paid: float
    exposure_notional: float
    ledger_depth: int
    open_positions: tuple[PositionSnapshot, ...]

    @property
    def primary_cadence(self) -> str:
        return self.execution_plan.primary_timeframe

    @property
    def feature_cadences(self) -> tuple[str, ...]:
        return self.execution_plan.feature_timeframes
