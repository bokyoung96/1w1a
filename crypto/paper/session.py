from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from crypto.domain import ExecutionPlan, FillRecord, FundingRate, InstrumentId, OrderSide

from .models import LedgerEventType, PaperLedgerEntry, PaperPosition, PaperSessionSnapshot


_ZERO_TOLERANCE = 1e-12


class PaperTradingSession:
    def __init__(
        self,
        *,
        strategy_id: str,
        exchange_id: str,
        execution_plan: ExecutionPlan,
        started_at: datetime,
        starting_equity: float,
    ) -> None:
        if starting_equity <= 0:
            raise ValueError("starting_equity must be positive")
        self.strategy_id = strategy_id
        self.exchange_id = exchange_id
        self.execution_plan = execution_plan
        self.started_at = started_at
        self.starting_equity = starting_equity
        self._positions: dict[str, PaperPosition] = {}
        self._ledger_entries: list[PaperLedgerEntry] = []
        self._latest_timestamp: datetime | None = None

    @property
    def ledger_entries(self) -> tuple[PaperLedgerEntry, ...]:
        return tuple(self._ledger_entries)

    @property
    def latest_timestamp(self) -> datetime | None:
        return self._latest_timestamp

    @property
    def realized_pnl(self) -> float:
        return sum(position.realized_pnl for position in self._positions.values())

    @property
    def funding_pnl(self) -> float:
        return sum(position.funding_pnl for position in self._positions.values())

    @property
    def fees_paid(self) -> float:
        return sum(position.fees_paid for position in self._positions.values())

    @property
    def unrealized_pnl(self) -> float:
        return sum(position.unrealized_pnl for position in self._positions.values())

    @property
    def exposure_notional(self) -> float:
        return sum(position.exposure_notional for position in self._positions.values())

    @property
    def current_equity(self) -> float:
        return (
            self.starting_equity
            + self.realized_pnl
            + self.funding_pnl
            - self.fees_paid
            + self.unrealized_pnl
        )

    def snapshot(self) -> PaperSessionSnapshot:
        open_positions = tuple(
            sorted(
                (
                    position.to_snapshot()
                    for position in self._positions.values()
                    if abs(position.quantity) > _ZERO_TOLERANCE
                ),
                key=lambda snapshot: snapshot.instrument.canonical_symbol,
            )
        )
        return PaperSessionSnapshot(
            strategy_id=self.strategy_id,
            exchange_id=self.exchange_id,
            execution_plan=self.execution_plan,
            started_at=self.started_at,
            latest_timestamp=self._latest_timestamp,
            starting_equity=self.starting_equity,
            current_equity=self.current_equity,
            realized_pnl=self.realized_pnl,
            funding_pnl=self.funding_pnl,
            fees_paid=self.fees_paid,
            exposure_notional=self.exposure_notional,
            ledger_depth=len(self._ledger_entries),
            open_positions=open_positions,
        )

    def record_fill(self, fill: FillRecord, *, at: datetime) -> PaperLedgerEntry:
        current = self._positions.get(fill.instrument.canonical_symbol, PaperPosition(fill.instrument))
        updated = _apply_fill(current, fill)
        updated = replace(
            updated,
            fees_paid=updated.fees_paid + fill.fee,
            mark_price=fill.price,
        )
        self._store_position(updated)
        return self._append_entry(
            timestamp=at,
            event_type=LedgerEventType.FILL,
            instrument=fill.instrument,
            quantity_delta=_signed_fill_quantity(fill),
            fill_price=fill.price,
            funding_rate=None,
        )

    def record_funding(self, rate: FundingRate) -> PaperLedgerEntry | None:
        current = self._positions.get(rate.instrument.canonical_symbol)
        if current is None or abs(current.quantity) <= _ZERO_TOLERANCE:
            return None

        mark_price = rate.mark_price if rate.mark_price is not None else current.mark_price
        if mark_price == 0.0:
            mark_price = current.average_entry_price

        funding_cashflow = -(current.quantity * mark_price * rate.funding_rate)
        updated = replace(
            current,
            funding_pnl=current.funding_pnl + funding_cashflow,
            mark_price=mark_price,
        )
        self._store_position(updated)
        return self._append_entry(
            timestamp=rate.timestamp,
            event_type=LedgerEventType.FUNDING,
            instrument=rate.instrument,
            quantity_delta=0.0,
            fill_price=None,
            funding_rate=rate.funding_rate,
        )

    def mark_to_market(
        self,
        *,
        instrument: InstrumentId,
        mark_price: float,
        at: datetime,
    ) -> PaperLedgerEntry:
        current = self._positions.get(instrument.canonical_symbol)
        if current is None or abs(current.quantity) <= _ZERO_TOLERANCE:
            raise KeyError(f"no open position for {instrument.canonical_symbol}")

        updated = replace(current, mark_price=mark_price)
        self._store_position(updated)
        return self._append_entry(
            timestamp=at,
            event_type=LedgerEventType.MARK,
            instrument=instrument,
            quantity_delta=0.0,
            fill_price=None,
            funding_rate=None,
        )

    def _store_position(self, position: PaperPosition) -> None:
        if abs(position.quantity) <= _ZERO_TOLERANCE:
            self._positions.pop(position.instrument.canonical_symbol, None)
            return
        self._positions[position.instrument.canonical_symbol] = position

    def _append_entry(
        self,
        *,
        timestamp: datetime,
        event_type: LedgerEventType,
        instrument: InstrumentId,
        quantity_delta: float,
        fill_price: float | None,
        funding_rate: float | None,
    ) -> PaperLedgerEntry:
        self._latest_timestamp = timestamp
        position = self._positions.get(instrument.canonical_symbol, PaperPosition(instrument))
        entry = PaperLedgerEntry(
            timestamp=timestamp,
            event_type=event_type,
            strategy_id=self.strategy_id,
            instrument=instrument,
            quantity_delta=quantity_delta,
            fill_price=fill_price,
            funding_rate=funding_rate,
            position_quantity=position.quantity,
            average_entry_price=position.average_entry_price,
            mark_price=position.mark_price,
            realized_pnl=self.realized_pnl,
            funding_pnl=self.funding_pnl,
            fees_paid=self.fees_paid,
            unrealized_pnl=self.unrealized_pnl,
            exposure_notional=self.exposure_notional,
            equity=self.current_equity,
        )
        self._ledger_entries.append(entry)
        return entry



def _signed_fill_quantity(fill: FillRecord) -> float:
    return fill.quantity if fill.side is OrderSide.BUY else -fill.quantity



def _apply_fill(position: PaperPosition, fill: FillRecord) -> PaperPosition:
    signed_delta = _signed_fill_quantity(fill)
    current_quantity = position.quantity
    current_average = position.average_entry_price
    realized_pnl = position.realized_pnl

    if abs(current_quantity) <= _ZERO_TOLERANCE:
        new_quantity = signed_delta
        new_average = fill.price
    elif current_quantity * signed_delta > 0:
        new_quantity = current_quantity + signed_delta
        new_average = (
            (abs(current_quantity) * current_average) + (abs(signed_delta) * fill.price)
        ) / abs(new_quantity)
    else:
        closing_quantity = min(abs(current_quantity), abs(signed_delta))
        direction = 1.0 if current_quantity > 0 else -1.0
        realized_pnl += closing_quantity * (fill.price - current_average) * direction
        new_quantity = current_quantity + signed_delta
        if abs(new_quantity) <= _ZERO_TOLERANCE:
            new_quantity = 0.0
            new_average = 0.0
        elif current_quantity * new_quantity > 0:
            new_average = current_average
        else:
            new_average = fill.price

    return replace(
        position,
        quantity=new_quantity,
        average_entry_price=new_average,
        mark_price=fill.price,
        realized_pnl=realized_pnl,
    )
