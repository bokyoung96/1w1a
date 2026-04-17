from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum

from crypto.domain import ExecutionPlan, FillRecord, FundingRate, InstrumentId, OrderSide


_ZERO_TOLERANCE = 1e-12


class PaperLedgerEntryType(str, Enum):
    FILL = "fill"
    FUNDING = "funding"
    MARK = "mark"
    EQUITY = "equity"


LedgerEventType = PaperLedgerEntryType


@dataclass(frozen=True, slots=True)
class PaperLedgerEntry:
    entry_type: PaperLedgerEntryType
    timestamp: datetime
    strategy_id: str | None = None
    instrument: InstrumentId | None = None
    instrument_symbol: str | None = None
    quantity: float | None = None
    quantity_delta: float | None = None
    price: float | None = None
    fill_price: float | None = None
    fee: float = 0.0
    funding_rate: float | None = None
    cash_flow: float = 0.0
    position_quantity: float | None = None
    average_entry_price: float | None = None
    mark_price: float | None = None
    realized_pnl: float = 0.0
    funding_pnl: float = 0.0
    fees_paid: float = 0.0
    unrealized_pnl: float = 0.0
    exposure_notional: float = 0.0
    equity: float | None = None
    gross_exposure: float | None = None
    net_exposure: float | None = None

    @property
    def event_type(self) -> PaperLedgerEntryType:
        return self.entry_type


@dataclass(frozen=True, slots=True)
class PaperPositionSnapshot:
    instrument: InstrumentId
    quantity: float
    average_entry_price: float
    mark_price: float

    @property
    def exposure_notional(self) -> float:
        mark_price = self.mark_price or self.average_entry_price
        return abs(self.quantity) * mark_price

    @property
    def unrealized_pnl(self) -> float:
        mark_price = self.mark_price or self.average_entry_price
        return (mark_price - self.average_entry_price) * self.quantity


@dataclass(frozen=True, slots=True)
class PaperPosition:
    instrument: InstrumentId
    quantity: float = 0.0
    average_entry_price: float = 0.0
    mark_price: float = 0.0

    @property
    def exposure_notional(self) -> float:
        mark_price = self.mark_price or self.average_entry_price
        return abs(self.quantity) * mark_price

    @property
    def net_exposure(self) -> float:
        mark_price = self.mark_price or self.average_entry_price
        return self.quantity * mark_price

    @property
    def unrealized_pnl(self) -> float:
        mark_price = self.mark_price or self.average_entry_price
        return (mark_price - self.average_entry_price) * self.quantity

    def to_snapshot(self) -> PaperPositionSnapshot:
        return PaperPositionSnapshot(
            instrument=self.instrument,
            quantity=self.quantity,
            average_entry_price=self.average_entry_price,
            mark_price=self.mark_price,
        )


@dataclass(frozen=True, slots=True)
class PaperSessionSnapshot:
    session_id: str
    strategy_id: str
    exchange_id: str
    execution_plan: ExecutionPlan
    started_at: datetime
    latest_timestamp: datetime | None
    starting_equity: float
    current_equity: float | None
    realized_pnl: float
    funding_pnl: float
    fees_paid: float
    unrealized_pnl: float
    exposure_notional: float
    net_exposure: float
    ledger_depth: int
    open_positions: tuple[PaperPositionSnapshot, ...]


class PaperSession:
    def __init__(
        self,
        *,
        strategy_id: str,
        started_at: datetime,
        session_id: str | None = None,
        exchange_id: str = "binance_perpetual",
        primary_cadence: str = "15m",
        feature_cadences: tuple[str, ...] | None = None,
        execution_plan: ExecutionPlan | None = None,
        starting_equity: float = 0.0,
    ) -> None:
        if execution_plan is None:
            feature_cadences = feature_cadences or (primary_cadence,)
            execution_plan = ExecutionPlan(
                primary_timeframe=primary_cadence,
                feature_timeframes=feature_cadences,
            )
        else:
            if feature_cadences is not None and tuple(feature_cadences) != execution_plan.feature_timeframes:
                raise ValueError("feature_cadences must match execution_plan.feature_timeframes")
            primary_cadence = execution_plan.primary_timeframe
            feature_cadences = execution_plan.feature_timeframes

        if starting_equity < 0:
            raise ValueError("starting_equity must not be negative")

        self.session_id = session_id or strategy_id
        self.strategy_id = strategy_id
        self.started_at = started_at
        self.exchange_id = exchange_id
        self.execution_plan = execution_plan
        self.primary_cadence = primary_cadence
        self.feature_cadences = tuple(feature_cadences)
        self.starting_equity = float(starting_equity)
        self._entries: list[PaperLedgerEntry] = []
        self._positions: dict[str, PaperPosition] = {}
        self._latest_timestamp: datetime | None = None
        self._realized_pnl = 0.0
        self._funding_pnl = 0.0
        self._fees_paid = 0.0

    @property
    def entries(self) -> tuple[PaperLedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def ledger_entries(self) -> tuple[PaperLedgerEntry, ...]:
        return self.entries

    @property
    def latest_timestamp(self) -> datetime | None:
        return self._latest_timestamp

    @property
    def equity_entries(self) -> tuple[PaperLedgerEntry, ...]:
        return tuple(entry for entry in self._entries if entry.entry_type is PaperLedgerEntryType.EQUITY)

    @property
    def latest_equity(self) -> float | None:
        if self.equity_entries:
            return self.equity_entries[-1].equity
        return self._computed_equity()

    @property
    def paper_days(self) -> int:
        if self.equity_entries:
            first = self.equity_entries[0].timestamp.date()
            last = self.equity_entries[-1].timestamp.date()
            return (last - first).days + 1
        if self._latest_timestamp is None:
            return 0
        return (self._latest_timestamp.date() - self.started_at.date()).days + 1

    @property
    def realized_pnl(self) -> float:
        return self._realized_pnl

    @property
    def funding_pnl(self) -> float:
        return self._funding_pnl

    @property
    def fees_paid(self) -> float:
        return self._fees_paid

    @property
    def realized_fees(self) -> float:
        return self.fees_paid

    @property
    def net_funding(self) -> float:
        return self.funding_pnl

    @property
    def unrealized_pnl(self) -> float:
        return sum(position.unrealized_pnl for position in self._positions.values())

    @property
    def exposure_notional(self) -> float:
        return sum(position.exposure_notional for position in self._positions.values())

    @property
    def gross_exposure(self) -> float:
        return self.exposure_notional

    @property
    def net_exposure(self) -> float:
        return sum(position.net_exposure for position in self._positions.values())

    @property
    def current_equity(self) -> float | None:
        return self._computed_equity()

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
            session_id=self.session_id,
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
            unrealized_pnl=self.unrealized_pnl,
            exposure_notional=self.exposure_notional,
            net_exposure=self.net_exposure,
            ledger_depth=len(self._entries),
            open_positions=open_positions,
        )

    def record_fill(self, fill: FillRecord, *, at: datetime) -> PaperLedgerEntry:
        current = self._positions.get(fill.instrument.canonical_symbol, PaperPosition(fill.instrument))
        updated, realized_delta = _apply_fill(current, fill)
        updated = replace(updated, mark_price=fill.price)
        self._realized_pnl += realized_delta
        self._fees_paid += fill.fee
        self._store_position(updated)

        cash_flow = fill.net_notional if fill.side is OrderSide.SELL else -fill.net_notional
        return self._append_entry(
            entry_type=PaperLedgerEntryType.FILL,
            timestamp=at,
            instrument=fill.instrument,
            quantity=fill.quantity,
            quantity_delta=_signed_fill_quantity(fill),
            price=fill.price,
            fill_price=fill.price,
            fee=fill.fee,
            funding_rate=None,
            cash_flow=cash_flow,
        )

    def record_funding(
        self,
        funding: FundingRate,
        *,
        cash_flow: float | None = None,
    ) -> PaperLedgerEntry | None:
        current = self._positions.get(funding.instrument.canonical_symbol)
        if current is None or abs(current.quantity) <= _ZERO_TOLERANCE:
            if cash_flow is None:
                return None
            mark_price = funding.mark_price
            position_quantity = 0.0
            average_entry_price = None
        else:
            mark_price = funding.mark_price if funding.mark_price is not None else current.mark_price
            if mark_price == 0.0:
                mark_price = current.average_entry_price
            if cash_flow is None:
                cash_flow = -(current.quantity * mark_price * funding.funding_rate)
            self._store_position(replace(current, mark_price=mark_price))
            position_quantity = current.quantity
            average_entry_price = current.average_entry_price

        self._funding_pnl += cash_flow
        return self._append_entry(
            entry_type=PaperLedgerEntryType.FUNDING,
            timestamp=funding.timestamp,
            instrument=funding.instrument,
            quantity=None,
            quantity_delta=0.0,
            price=mark_price,
            fill_price=None,
            fee=0.0,
            funding_rate=funding.funding_rate,
            cash_flow=cash_flow,
            position_quantity=position_quantity,
            average_entry_price=average_entry_price,
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
            entry_type=PaperLedgerEntryType.MARK,
            timestamp=at,
            instrument=instrument,
            quantity=None,
            quantity_delta=0.0,
            price=mark_price,
            fill_price=None,
            fee=0.0,
            funding_rate=None,
            cash_flow=0.0,
        )

    def record_equity(
        self,
        *,
        at: datetime,
        equity: float,
        gross_exposure: float,
        net_exposure: float,
    ) -> PaperLedgerEntry:
        return self._append_entry(
            entry_type=PaperLedgerEntryType.EQUITY,
            timestamp=at,
            instrument=None,
            quantity=None,
            quantity_delta=None,
            price=None,
            fill_price=None,
            fee=0.0,
            funding_rate=None,
            cash_flow=0.0,
            equity=equity,
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
        )

    def _store_position(self, position: PaperPosition) -> None:
        if abs(position.quantity) <= _ZERO_TOLERANCE:
            self._positions.pop(position.instrument.canonical_symbol, None)
            return
        self._positions[position.instrument.canonical_symbol] = position

    def _append_entry(
        self,
        *,
        entry_type: PaperLedgerEntryType,
        timestamp: datetime,
        instrument: InstrumentId | None,
        quantity: float | None,
        quantity_delta: float | None,
        price: float | None,
        fill_price: float | None,
        fee: float,
        funding_rate: float | None,
        cash_flow: float,
        position_quantity: float | None = None,
        average_entry_price: float | None = None,
        equity: float | None = None,
        gross_exposure: float | None = None,
        net_exposure: float | None = None,
    ) -> PaperLedgerEntry:
        self._latest_timestamp = timestamp
        position = self._positions.get(instrument.canonical_symbol) if instrument is not None else None
        if position_quantity is None:
            position_quantity = position.quantity if position is not None else None
        if average_entry_price is None:
            average_entry_price = position.average_entry_price if position is not None else None
        resolved_mark_price = position.mark_price if position is not None else None
        if price is not None and entry_type is PaperLedgerEntryType.MARK:
            resolved_mark_price = price

        entry = PaperLedgerEntry(
            entry_type=entry_type,
            timestamp=timestamp,
            strategy_id=self.strategy_id,
            instrument=instrument,
            instrument_symbol=instrument.canonical_symbol if instrument is not None else None,
            quantity=quantity,
            quantity_delta=quantity_delta,
            price=price,
            fill_price=fill_price,
            fee=fee,
            funding_rate=funding_rate,
            cash_flow=cash_flow,
            position_quantity=position_quantity,
            average_entry_price=average_entry_price,
            mark_price=resolved_mark_price,
            realized_pnl=self.realized_pnl,
            funding_pnl=self.funding_pnl,
            fees_paid=self.fees_paid,
            unrealized_pnl=self.unrealized_pnl,
            exposure_notional=self.exposure_notional,
            equity=equity if entry_type is PaperLedgerEntryType.EQUITY else self._computed_equity(),
            gross_exposure=gross_exposure if entry_type is PaperLedgerEntryType.EQUITY else self.gross_exposure,
            net_exposure=net_exposure if entry_type is PaperLedgerEntryType.EQUITY else self.net_exposure,
        )
        self._entries.append(entry)
        return entry

    def _computed_equity(self) -> float | None:
        if self.starting_equity > 0.0:
            return (
                self.starting_equity
                + self.realized_pnl
                + self.funding_pnl
                - self.fees_paid
                + self.unrealized_pnl
            )
        if self.equity_entries:
            return self.equity_entries[-1].equity
        if self._entries:
            return self.realized_pnl + self.funding_pnl - self.fees_paid + self.unrealized_pnl
        return None


def _signed_fill_quantity(fill: FillRecord) -> float:
    return fill.quantity if fill.side is OrderSide.BUY else -fill.quantity


def _apply_fill(position: PaperPosition, fill: FillRecord) -> tuple[PaperPosition, float]:
    signed_delta = _signed_fill_quantity(fill)
    current_quantity = position.quantity
    current_average = position.average_entry_price
    realized_delta = 0.0

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
        realized_delta = closing_quantity * (fill.price - current_average) * direction
        new_quantity = current_quantity + signed_delta
        if abs(new_quantity) <= _ZERO_TOLERANCE:
            new_quantity = 0.0
            new_average = 0.0
        elif current_quantity * new_quantity > 0:
            new_average = current_average
        else:
            new_average = fill.price

    return (
        replace(
            position,
            quantity=new_quantity,
            average_entry_price=new_average,
            mark_price=fill.price,
        ),
        realized_delta,
    )
