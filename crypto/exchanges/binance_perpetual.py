from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from crypto.domain import Bar, ExecutionPlan, FundingRate, InstrumentId, NormalizationResult

from .base import CCXTMarketDataClient


@dataclass(slots=True)
class BinancePerpetualCCXTAdapter:
    client: CCXTMarketDataClient
    execution_plan: ExecutionPlan = field(default_factory=ExecutionPlan)
    exchange_id: str = field(default="binance_perpetual", init=False)

    def normalize_instrument(self, symbol: str) -> InstrumentId:
        market_loader = getattr(self.client, "market", None)
        market = market_loader(symbol) if callable(market_loader) else None
        return InstrumentId.from_exchange_symbol(self.exchange_id, symbol, market=market)

    def fetch_bars(
        self,
        symbol: str,
        *,
        timeframe: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> NormalizationResult[Bar]:
        resolved_timeframe = timeframe or self.execution_plan.primary_timeframe
        raw_rows = self.client.fetch_ohlcv(
            symbol,
            timeframe=resolved_timeframe,
            since=since,
            limit=limit,
            params=params,
        )
        instrument = self.normalize_instrument(symbol)
        bars = tuple(
            Bar.from_ohlcv(instrument=instrument, timeframe=resolved_timeframe, row=row)
            for row in raw_rows
        )
        raw_payload = tuple(tuple(row) for row in raw_rows)
        return NormalizationResult(raw_payload=raw_payload, records=bars)

    def fetch_funding_rates(
        self,
        symbol: str,
        *,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> NormalizationResult[FundingRate]:
        raw_rows = self.client.fetch_funding_rate_history(
            symbol,
            since=since,
            limit=limit,
            params=params,
        )
        instrument = self.normalize_instrument(symbol)
        rates = tuple(FundingRate.from_ccxt(instrument=instrument, payload=row) for row in raw_rows)
        raw_payload = tuple(dict(row) for row in raw_rows)
        return NormalizationResult(raw_payload=raw_payload, records=rates)
