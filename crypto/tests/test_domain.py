from __future__ import annotations

import unittest


from crypto.domain import (
    ExecutionPlan,
    FillRecord,
    InstrumentId,
    OrderIntent,
    OrderSide,
    OrderType,
    PositionSnapshot,
    PositionSide,
)


class DomainModelTests(unittest.TestCase):
    def test_execution_plan_requires_primary_timeframe_in_feature_inputs(self) -> None:
        with self.assertRaises(ValueError):
            ExecutionPlan(primary_timeframe="15m", feature_timeframes=("5m", "1h"))

    def test_binance_perpetual_symbol_normalizes_to_canonical_instrument(self) -> None:
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "BTC/USDT:USDT")

        self.assertEqual(instrument.exchange_id, "binance_perpetual")
        self.assertEqual(instrument.base_asset, "BTC")
        self.assertEqual(instrument.quote_asset, "USDT")
        self.assertEqual(instrument.settle_asset, "USDT")
        self.assertEqual(instrument.canonical_symbol, "BTC-USDT-PERP")

    def test_position_snapshot_derives_side_from_signed_quantity(self) -> None:
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "ETH/USDT:USDT")

        short_position = PositionSnapshot(
            instrument=instrument,
            quantity=-2.5,
            entry_price=3100.0,
            mark_price=3000.0,
        )
        flat_position = PositionSnapshot(
            instrument=instrument,
            quantity=0.0,
            entry_price=3100.0,
            mark_price=3000.0,
        )

        self.assertEqual(short_position.side, PositionSide.SHORT)
        self.assertAlmostEqual(short_position.notional_value, -7500.0)
        self.assertEqual(flat_position.side, PositionSide.FLAT)

    def test_order_intent_requires_positive_quantity(self) -> None:
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "SOL/USDT:USDT")

        with self.assertRaises(ValueError):
            OrderIntent(
                strategy_id="trend-breakout",
                instrument=instrument,
                side=OrderSide.BUY,
                quantity=0.0,
                order_type=OrderType.MARKET,
            )

    def test_fill_record_computes_gross_notional(self) -> None:
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "SOL/USDT:USDT")
        fill = FillRecord(
            fill_id="fill-1",
            order_id="order-1",
            instrument=instrument,
            side=OrderSide.SELL,
            quantity=3.0,
            price=150.5,
            fee=0.75,
        )

        self.assertAlmostEqual(fill.gross_notional, 451.5)
        self.assertAlmostEqual(fill.net_notional, 450.75)


if __name__ == "__main__":
    unittest.main()
