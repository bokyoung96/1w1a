from __future__ import annotations

import unittest


from crypto.domain import Bar, FundingRate
from crypto.exchanges import BinancePerpetualCCXTAdapter, build_exchange_adapter


class _FakeBinanceClient:
    def market(self, symbol: str) -> dict[str, object]:
        return {
            "symbol": symbol,
            "base": "BTC",
            "quote": "USDT",
            "settle": "USDT",
            "type": "swap",
            "linear": True,
        }

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "15m",
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, object] | None = None,
    ) -> list[list[float]]:
        return [
            [1713312000000, 64000.0, 64250.0, 63900.0, 64150.0, 125.0],
            [1713312900000, 64150.0, 64500.0, 64100.0, 64480.0, 118.5],
        ]

    def fetch_funding_rate_history(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        return [
            {
                "symbol": symbol,
                "fundingRate": "0.0001",
                "timestamp": 1713312000000,
                "markPrice": "64150.0",
            }
        ]


class ExchangeAdapterTests(unittest.TestCase):
    def test_factory_rejects_unknown_exchange(self) -> None:
        with self.assertRaises(ValueError):
            build_exchange_adapter("kraken_perpetual", client=object())

    def test_binance_adapter_uses_approved_defaults(self) -> None:
        adapter = BinancePerpetualCCXTAdapter(client=_FakeBinanceClient())

        self.assertEqual(adapter.exchange_id, "binance_perpetual")
        self.assertEqual(adapter.execution_plan.primary_timeframe, "15m")
        self.assertIn("15m", adapter.execution_plan.feature_timeframes)
        self.assertEqual(adapter.execution_plan.feature_timeframes, ("5m", "15m", "1h"))

    def test_fetch_bars_normalizes_ccxt_payload_to_canonical_bars(self) -> None:
        adapter = BinancePerpetualCCXTAdapter(client=_FakeBinanceClient())

        result = adapter.fetch_bars("BTC/USDT:USDT")

        self.assertEqual(len(result.raw_payload), 2)
        self.assertIsInstance(result.records[0], Bar)
        self.assertEqual(result.records[0].instrument.canonical_symbol, "BTC-USDT-PERP")
        self.assertEqual(result.records[0].timeframe, "15m")
        self.assertEqual(result.records[1].close, 64480.0)

    def test_fetch_funding_rates_normalizes_ccxt_payload_to_canonical_records(self) -> None:
        adapter = BinancePerpetualCCXTAdapter(client=_FakeBinanceClient())

        result = adapter.fetch_funding_rates("BTC/USDT:USDT")

        self.assertEqual(len(result.raw_payload), 1)
        self.assertIsInstance(result.records[0], FundingRate)
        self.assertEqual(result.records[0].instrument.canonical_symbol, "BTC-USDT-PERP")
        self.assertAlmostEqual(result.records[0].funding_rate, 0.0001)
        self.assertAlmostEqual(result.records[0].mark_price, 64150.0)


if __name__ == "__main__":
    unittest.main()
