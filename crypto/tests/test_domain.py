from __future__ import annotations

import unittest


from crypto.domain import ExecutionPlan, InstrumentId, PositionSnapshot, PositionSide


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


if __name__ == "__main__":
    unittest.main()
