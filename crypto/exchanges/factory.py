from __future__ import annotations

from typing import Any

from crypto.domain import ExecutionPlan

from .binance_perpetual import BinancePerpetualCCXTAdapter


def build_exchange_adapter(
    exchange_id: str,
    *,
    client: Any,
    execution_plan: ExecutionPlan | None = None,
) -> BinancePerpetualCCXTAdapter:
    if exchange_id != "binance_perpetual":
        raise ValueError(f"unsupported exchange adapter: {exchange_id!r}")

    return BinancePerpetualCCXTAdapter(
        client=client,
        execution_plan=execution_plan or ExecutionPlan(primary_timeframe="15m", feature_timeframes=("15m",)),
    )


def create_public_ccxt_client(
    exchange_id: str,
    *,
    testnet: bool = True,
    options: dict[str, Any] | None = None,
) -> Any:
    if exchange_id != "binance_perpetual":
        raise ValueError(f"unsupported exchange adapter: {exchange_id!r}")

    try:
        import ccxt  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "ccxt is required to build a live public-data client; inject a mocked client in tests"
        ) from exc

    client = ccxt.binanceusdm(options or {})
    if testnet and hasattr(client, "set_sandbox_mode"):
        client.set_sandbox_mode(True)
    return client
