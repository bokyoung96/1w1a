from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Generic, TypeVar


RecordT = TypeVar("RecordT")


def _coerce_symbol_parts(symbol: str) -> tuple[str, str, str]:
    normalized = symbol.strip().upper()
    if "/" not in normalized:
        raise ValueError(f"unsupported perpetual symbol format: {symbol!r}")

    base_asset, remainder = normalized.split("/", 1)
    if ":" in remainder:
        quote_asset, settle_asset = remainder.split(":", 1)
    else:
        quote_asset = remainder
        settle_asset = quote_asset

    if not base_asset or not quote_asset or not settle_asset:
        raise ValueError(f"incomplete perpetual symbol format: {symbol!r}")

    return base_asset, quote_asset, settle_asset


def _millis_to_utc(timestamp_ms: int | float) -> datetime:
    return datetime.fromtimestamp(float(timestamp_ms) / 1000.0, tz=timezone.utc)


def timeframe_to_timedelta(timeframe: str) -> timedelta:
    if len(timeframe) < 2:
        raise ValueError(f"invalid timeframe: {timeframe!r}")

    unit = timeframe[-1]
    value = int(timeframe[:-1])
    if value <= 0:
        raise ValueError(f"timeframe must be positive: {timeframe!r}")

    if unit == "m":
        return timedelta(minutes=value)
    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    if unit == "w":
        return timedelta(weeks=value)
    raise ValueError(f"unsupported timeframe unit: {timeframe!r}")


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass(frozen=True)
class ExecutionPlan:
    primary_timeframe: str = "15m"
    feature_timeframes: tuple[str, ...] = ("15m",)

    def __post_init__(self) -> None:
        if not self.feature_timeframes:
            raise ValueError("feature_timeframes must not be empty")
        if self.primary_timeframe not in self.feature_timeframes:
            raise ValueError("primary_timeframe must be included in feature_timeframes")
        for timeframe in self.feature_timeframes:
            timeframe_to_timedelta(timeframe)


@dataclass(frozen=True)
class InstrumentId:
    exchange_id: str
    base_asset: str
    quote_asset: str
    settle_asset: str
    contract_type: str = "perpetual"

    @property
    def canonical_symbol(self) -> str:
        return f"{self.base_asset}-{self.quote_asset}-PERP"

    @classmethod
    def from_exchange_symbol(
        cls,
        exchange_id: str,
        symbol: str,
        market: dict[str, Any] | None = None,
    ) -> InstrumentId:
        market = market or {}
        base_asset = str(market.get("base") or "").upper()
        quote_asset = str(market.get("quote") or "").upper()
        settle_asset = str(market.get("settle") or "").upper()

        if not base_asset or not quote_asset or not settle_asset:
            base_asset, quote_asset, settle_asset = _coerce_symbol_parts(symbol)

        return cls(
            exchange_id=exchange_id,
            base_asset=base_asset,
            quote_asset=quote_asset,
            settle_asset=settle_asset,
        )


@dataclass(frozen=True)
class Bar:
    instrument: InstrumentId
    timeframe: str
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_ohlcv(
        cls,
        *,
        instrument: InstrumentId,
        timeframe: str,
        row: tuple[Any, Any, Any, Any, Any, Any] | list[Any],
    ) -> Bar:
        if len(row) < 6:
            raise ValueError(f"expected 6 OHLCV fields, received {len(row)}")
        open_time = _millis_to_utc(row[0])
        close_time = open_time + timeframe_to_timedelta(timeframe)
        return cls(
            instrument=instrument,
            timeframe=timeframe,
            open_time=open_time,
            close_time=close_time,
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
        )


@dataclass(frozen=True)
class FundingRate:
    instrument: InstrumentId
    timestamp: datetime
    funding_rate: float
    mark_price: float | None = None

    @classmethod
    def from_ccxt(
        cls,
        *,
        instrument: InstrumentId,
        payload: dict[str, Any],
    ) -> FundingRate:
        timestamp = payload.get("timestamp")
        if timestamp is None:
            info = payload.get("info")
            if isinstance(info, dict):
                timestamp = info.get("fundingTime") or info.get("time")
        if timestamp is None:
            raise ValueError("funding payload missing timestamp")

        mark_price = payload.get("markPrice")
        return cls(
            instrument=instrument,
            timestamp=_millis_to_utc(timestamp),
            funding_rate=float(payload["fundingRate"]),
            mark_price=float(mark_price) if mark_price is not None else None,
        )


@dataclass(frozen=True)
class PositionSnapshot:
    instrument: InstrumentId
    quantity: float
    entry_price: float
    mark_price: float

    @property
    def side(self) -> PositionSide:
        if self.quantity > 0:
            return PositionSide.LONG
        if self.quantity < 0:
            return PositionSide.SHORT
        return PositionSide.FLAT

    @property
    def notional_value(self) -> float:
        return self.quantity * self.mark_price


@dataclass(frozen=True)
class NormalizationResult(Generic[RecordT]):
    raw_payload: tuple[Any, ...]
    records: tuple[RecordT, ...]
