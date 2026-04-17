from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from crypto.domain import ExecutionPlan, FillRecord, FundingRate, OrderSide


class PaperLedgerEntryType(str, Enum):
    FILL = "fill"
    FUNDING = "funding"
    EQUITY = "equity"


@dataclass(frozen=True, slots=True)
class PaperLedgerEntry:
    entry_type: PaperLedgerEntryType
    timestamp: datetime
    instrument_symbol: str | None = None
    quantity: float | None = None
    price: float | None = None
    fee: float = 0.0
    funding_rate: float | None = None
    cash_flow: float = 0.0
    equity: float | None = None
    gross_exposure: float | None = None
    net_exposure: float | None = None


@dataclass(slots=True)
class PaperSession:
    session_id: str
    strategy_id: str
    started_at: datetime
    exchange_id: str = "binance_perpetual"
    primary_cadence: str = "15m"
    feature_cadences: tuple[str, ...] = ("15m",)
    _entries: list[PaperLedgerEntry] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        ExecutionPlan(
            primary_timeframe=self.primary_cadence,
            feature_timeframes=self.feature_cadences,
        )

    @property
    def entries(self) -> tuple[PaperLedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def equity_entries(self) -> tuple[PaperLedgerEntry, ...]:
        return tuple(entry for entry in self._entries if entry.entry_type is PaperLedgerEntryType.EQUITY)

    @property
    def latest_equity(self) -> float | None:
        if not self.equity_entries:
            return None
        return self.equity_entries[-1].equity

    @property
    def paper_days(self) -> int:
        if not self.equity_entries:
            return 0
        first = self.equity_entries[0].timestamp.date()
        last = self.equity_entries[-1].timestamp.date()
        return (last - first).days + 1

    @property
    def realized_fees(self) -> float:
        return sum(entry.fee for entry in self._entries if entry.entry_type is PaperLedgerEntryType.FILL)

    @property
    def net_funding(self) -> float:
        return sum(
            entry.cash_flow
            for entry in self._entries
            if entry.entry_type is PaperLedgerEntryType.FUNDING
        )

    def record_fill(self, fill: FillRecord, *, at: datetime) -> PaperLedgerEntry:
        cash_flow = fill.net_notional if fill.side is OrderSide.SELL else -fill.net_notional
        entry = PaperLedgerEntry(
            entry_type=PaperLedgerEntryType.FILL,
            timestamp=at,
            instrument_symbol=fill.instrument.canonical_symbol,
            quantity=fill.quantity,
            price=fill.price,
            fee=fill.fee,
            cash_flow=cash_flow,
        )
        self._entries.append(entry)
        return entry

    def record_funding(self, funding: FundingRate, *, cash_flow: float) -> PaperLedgerEntry:
        entry = PaperLedgerEntry(
            entry_type=PaperLedgerEntryType.FUNDING,
            timestamp=funding.timestamp,
            instrument_symbol=funding.instrument.canonical_symbol,
            funding_rate=funding.funding_rate,
            price=funding.mark_price,
            cash_flow=cash_flow,
        )
        self._entries.append(entry)
        return entry

    def record_equity(
        self,
        *,
        at: datetime,
        equity: float,
        gross_exposure: float,
        net_exposure: float,
    ) -> PaperLedgerEntry:
        entry = PaperLedgerEntry(
            entry_type=PaperLedgerEntryType.EQUITY,
            timestamp=at,
            equity=equity,
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
        )
        self._entries.append(entry)
        return entry
