from __future__ import annotations

from typing import Any, Protocol

from crypto.domain import Bar, ExecutionPlan, FundingRate, InstrumentId, NormalizationResult


class CCXTMarketDataClient(Protocol):
    def market(self, symbol: str) -> dict[str, Any]:
        ...

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "15m",
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        ...

    def fetch_funding_rate_history(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        ...


class ExchangeAdapter(Protocol):
    exchange_id: str
    execution_plan: ExecutionPlan

    def normalize_instrument(self, symbol: str) -> InstrumentId:
        ...

    def fetch_bars(
        self,
        symbol: str,
        *,
        timeframe: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> NormalizationResult[Bar]:
        ...

    def fetch_funding_rates(
        self,
        symbol: str,
        *,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> NormalizationResult[FundingRate]:
        ...
