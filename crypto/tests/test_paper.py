from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from crypto.domain import FillRecord, FundingRate, InstrumentId, OrderSide
from crypto.paper import PaperLedgerEntryType, PaperSession


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def test_paper_session_records_fill_funding_and_equity_events() -> None:
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

    assert session.exchange_id == "binance_perpetual"
    assert session.primary_cadence == "15m"
    assert session.feature_cadences == ("15m", "1h")
    assert [entry.entry_type for entry in session.entries] == [
        PaperLedgerEntryType.FILL,
        PaperLedgerEntryType.FUNDING,
        PaperLedgerEntryType.EQUITY,
        PaperLedgerEntryType.EQUITY,
    ]
    assert fill_entry.fee == pytest.approx(12.5)
    assert funding_entry.cash_flow == pytest.approx(-3.2)
    assert first_equity.equity == pytest.approx(10_000.0)
    assert second_equity.net_exposure == pytest.approx(14_500.0)
    assert session.latest_equity == pytest.approx(10_180.0)
    assert session.paper_days == 2


def test_paper_session_rejects_hidden_primary_cadence_changes() -> None:
    with pytest.raises(ValueError):
        PaperSession(
            session_id="paper-btc-breakout",
            strategy_id="trend_following_breakout",
            started_at=_utc("2026-01-01T00:00:00"),
            primary_cadence="15m",
            feature_cadences=("5m", "1h"),
        )
        self.execution_plan = ExecutionPlan(
            primary_timeframe="15m",
            feature_timeframes=("5m", "15m", "1h"),
        )

    def test_session_snapshot_keeps_approved_execution_metadata_visible(self) -> None:
        session = PaperTradingSession(
            strategy_id="trend-following-breakout",
            exchange_id="binance_perpetual",
            execution_plan=self.execution_plan,
            started_at=datetime(2026, 4, 17, 0, 0, tzinfo=timezone.utc),
            starting_equity=10_000.0,
        )

        snapshot = session.snapshot()

        self.assertEqual(snapshot.primary_cadence, "15m")
        self.assertEqual(snapshot.feature_cadences, ("5m", "15m", "1h"))
        self.assertEqual(snapshot.current_equity, 10_000.0)
        self.assertEqual(snapshot.open_positions, ())

    def test_record_fill_then_mark_creates_graph_ready_ledger_entries(self) -> None:
        session = PaperTradingSession(
            strategy_id="trend-following-breakout",
            exchange_id="binance_perpetual",
            execution_plan=self.execution_plan,
            started_at=datetime(2026, 4, 17, 0, 0, tzinfo=timezone.utc),
            starting_equity=10_000.0,
        )

        session.record_fill(
            FillRecord(
                fill_id="fill-1",
                order_id="order-1",
                instrument=self.instrument,
                side=OrderSide.BUY,
                quantity=2.0,
                price=100.0,
                fee=1.25,
            ),
            at=datetime(2026, 4, 17, 0, 15, tzinfo=timezone.utc),
        )
        session.mark_to_market(
            instrument=self.instrument,
            mark_price=110.0,
            at=datetime(2026, 4, 17, 0, 30, tzinfo=timezone.utc),
        )

        ledger = session.ledger_entries
        snapshot = session.snapshot()

        self.assertEqual([entry.event_type for entry in ledger], [LedgerEventType.FILL, LedgerEventType.MARK])
        self.assertEqual([entry.equity for entry in ledger], [9998.75, 10018.75])
        self.assertEqual([entry.exposure_notional for entry in ledger], [200.0, 220.0])
        self.assertEqual(snapshot.ledger_depth, 2)
        self.assertEqual(len(snapshot.open_positions), 1)
        self.assertAlmostEqual(snapshot.open_positions[0].quantity, 2.0)
        self.assertAlmostEqual(snapshot.open_positions[0].entry_price, 100.0)
        self.assertAlmostEqual(snapshot.open_positions[0].mark_price, 110.0)

    def test_record_funding_and_partial_close_updates_realized_and_equity(self) -> None:
        session = PaperTradingSession(
            strategy_id="trend-following-breakout",
            exchange_id="binance_perpetual",
            execution_plan=self.execution_plan,
            started_at=datetime(2026, 4, 17, 0, 0, tzinfo=timezone.utc),
            starting_equity=10_000.0,
        )

        session.record_fill(
            FillRecord(
                fill_id="fill-1",
                order_id="order-1",
                instrument=self.instrument,
                side=OrderSide.BUY,
                quantity=2.0,
                price=100.0,
                fee=1.0,
            ),
            at=datetime(2026, 4, 17, 0, 15, tzinfo=timezone.utc),
        )
        session.record_funding(
            FundingRate(
                instrument=self.instrument,
                timestamp=datetime(2026, 4, 17, 0, 45, tzinfo=timezone.utc),
                funding_rate=0.01,
                mark_price=110.0,
            )
        )
        session.record_fill(
            FillRecord(
                fill_id="fill-2",
                order_id="order-2",
                instrument=self.instrument,
                side=OrderSide.SELL,
                quantity=1.0,
                price=120.0,
                fee=0.5,
            ),
            at=datetime(2026, 4, 17, 1, 0, tzinfo=timezone.utc),
        )

        snapshot = session.snapshot()
        ledger = session.ledger_entries

        self.assertEqual(
            [entry.event_type for entry in ledger],
            [LedgerEventType.FILL, LedgerEventType.FUNDING, LedgerEventType.FILL],
        )
        self.assertAlmostEqual(snapshot.current_equity, 10036.3)
        self.assertAlmostEqual(snapshot.realized_pnl, 20.0)
        self.assertAlmostEqual(snapshot.funding_pnl, -2.2)
        self.assertAlmostEqual(snapshot.fees_paid, 1.5)
        self.assertEqual(len(snapshot.open_positions), 1)
        self.assertAlmostEqual(snapshot.open_positions[0].quantity, 1.0)
        self.assertAlmostEqual(snapshot.open_positions[0].entry_price, 100.0)
        self.assertAlmostEqual(snapshot.open_positions[0].mark_price, 120.0)
        self.assertAlmostEqual(ledger[-1].equity, 10036.3)


if __name__ == "__main__":
    unittest.main()
