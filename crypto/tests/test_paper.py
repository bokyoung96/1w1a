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
