from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from crypto.domain import FillRecord, FundingRate, InstrumentId, OrderSide
from crypto.paper import PaperLedgerEntryType, PaperSession


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


class PaperSessionTests(unittest.TestCase):
    def test_paper_session_records_fill_funding_and_equity_events(self) -> None:
        started_at = _utc("2026-01-01T00:00:00")
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "BTC/USDT:USDT")
        session = PaperSession(
            session_id="paper-btc-breakout",
            strategy_id="trend_following_breakout",
            started_at=started_at,
            feature_cadences=("15m", "1h"),
        )

        fill = FillRecord(
            fill_id="fill-1",
            order_id="order-1",
            instrument=instrument,
            side=OrderSide.BUY,
            quantity=0.25,
            price=64000.0,
            fee=12.5,
        )
        funding = FundingRate(
            instrument=instrument,
            timestamp=started_at + timedelta(hours=8),
            funding_rate=0.0001,
            mark_price=64100.0,
        )

        fill_entry = session.record_fill(fill, at=started_at + timedelta(minutes=15))
        funding_entry = session.record_funding(funding, cash_flow=-3.2)
        first_equity = session.record_equity(
            at=started_at + timedelta(minutes=15),
            equity=10_000.0,
            gross_exposure=16_000.0,
            net_exposure=16_000.0,
        )
        second_equity = session.record_equity(
            at=started_at + timedelta(days=1, minutes=15),
            equity=10_180.0,
            gross_exposure=14_500.0,
            net_exposure=14_500.0,
        )

        self.assertEqual(session.exchange_id, "binance_perpetual")
        self.assertEqual(session.primary_cadence, "15m")
        self.assertEqual(session.feature_cadences, ("15m", "1h"))
        self.assertEqual(
            [entry.entry_type for entry in session.entries],
            [
                PaperLedgerEntryType.FILL,
                PaperLedgerEntryType.FUNDING,
                PaperLedgerEntryType.EQUITY,
                PaperLedgerEntryType.EQUITY,
            ],
        )
        self.assertAlmostEqual(fill_entry.fee, 12.5)
        self.assertAlmostEqual(funding_entry.cash_flow, -3.2)
        self.assertAlmostEqual(first_equity.equity or 0.0, 10_000.0)
        self.assertAlmostEqual(second_equity.net_exposure or 0.0, 14_500.0)
        self.assertAlmostEqual(session.latest_equity or 0.0, 10_180.0)
        self.assertEqual(session.paper_days, 2)

    def test_paper_session_rejects_hidden_primary_cadence_changes(self) -> None:
        with self.assertRaises(ValueError):
            PaperSession(
                session_id="paper-btc-breakout",
                strategy_id="trend_following_breakout",
                started_at=_utc("2026-01-01T00:00:00"),
                primary_cadence="15m",
                feature_cadences=("5m", "1h"),
            )

    def test_paper_session_records_sell_fills_as_positive_cash_flow(self) -> None:
        started_at = _utc("2026-01-01T00:00:00")
        instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "ETH/USDT:USDT")
        session = PaperSession(
            session_id="paper-eth-mean-reversion",
            strategy_id="mean_reversion",
            started_at=started_at,
        )

        sell_fill = FillRecord(
            fill_id="fill-2",
            order_id="order-2",
            instrument=instrument,
            side=OrderSide.SELL,
            quantity=1.5,
            price=3000.0,
            fee=4.0,
        )

        entry = session.record_fill(sell_fill, at=started_at + timedelta(minutes=15))

        self.assertAlmostEqual(entry.cash_flow, 4496.0)

    def test_package_surface_keeps_paper_session_as_the_supported_entry_point(self) -> None:
        self.assertEqual(PaperSession.__module__, "crypto.paper.models")
        self.assertEqual(PaperSession.__name__, "PaperSession")


if __name__ == "__main__":
    unittest.main()
