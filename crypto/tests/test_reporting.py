from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from crypto.domain import FillRecord, FundingRate, InstrumentId, OrderSide
from crypto.paper import PaperSession
from crypto.reporting import build_paper_performance_report
from crypto.strategies import DEFAULT_STRATEGIES
from crypto.validation import DEFAULT_PROMOTION_THRESHOLDS


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def test_report_builder_returns_graph_ready_metrics_and_explicit_strategy_catalog() -> None:
    started_at = _utc("2026-01-01T00:00:00")
    instrument = InstrumentId.from_exchange_symbol("binance_perpetual", "BTC/USDT:USDT")
    session = PaperSession(
        session_id="paper-btc-breakout",
        strategy_id="trend_following_breakout",
        started_at=started_at,
        feature_cadences=("15m", "1h"),
    )
    session.record_fill(
        FillRecord(
            fill_id="fill-1",
            order_id="order-1",
            instrument=instrument,
            side=OrderSide.BUY,
            quantity=0.25,
            price=64000.0,
            fee=8.0,
        ),
        at=started_at + timedelta(minutes=15),
    )
    session.record_funding(
        FundingRate(
            instrument=instrument,
            timestamp=started_at + timedelta(hours=8),
            funding_rate=0.0001,
            mark_price=64100.0,
        ),
        cash_flow=-2.5,
    )
    session.record_equity(
        at=started_at + timedelta(minutes=15),
        equity=10_000.0,
        gross_exposure=16_000.0,
        net_exposure=16_000.0,
    )
    session.record_equity(
        at=started_at + timedelta(days=1, minutes=15),
        equity=10_300.0,
        gross_exposure=16_200.0,
        net_exposure=16_200.0,
    )
    session.record_equity(
        at=started_at + timedelta(days=2, minutes=15),
        equity=9_900.0,
        gross_exposure=14_900.0,
        net_exposure=14_900.0,
    )
    session.record_equity(
        at=started_at + timedelta(days=3, minutes=15),
        equity=10_450.0,
        gross_exposure=15_300.0,
        net_exposure=15_300.0,
    )

    report = build_paper_performance_report(
        session,
        strategy_definitions=DEFAULT_STRATEGIES,
        peer_returns={
            "mean_reversion": (
                0.03,
                -0.038834951456310676,
                0.05555555555555558,
            )
        },
    )

    assert report.metadata.strategy_id == "trend_following_breakout"
    assert report.metadata.exchange_id == "binance_perpetual"
    assert report.metadata.primary_cadence == "15m"
    assert report.metadata.feature_cadences == ("15m", "1h")

    assert [series.slug for series in report.graphs] == [
        "equity_curve",
        "drawdown_curve",
        "gross_exposure_curve",
        "net_exposure_curve",
    ]
    assert len(report.graphs[0].points) == 4
    assert report.graphs[0].points[-1].value == pytest.approx(10_450.0)

    assert report.summary.total_return == pytest.approx(0.045)
    assert report.summary.max_drawdown == pytest.approx(0.038834951456310676)
    assert report.summary.paper_days == 4
    assert report.summary.realized_fees == pytest.approx(8.0)
    assert report.summary.net_funding == pytest.approx(-2.5)
    assert report.summary.max_peer_correlation == pytest.approx(1.0)
    assert report.summary.paper_sharpe > 0.0

    assert report.thresholds.oos_sharpe == DEFAULT_PROMOTION_THRESHOLDS.oos_sharpe
    assert report.thresholds.paper_sharpe == DEFAULT_PROMOTION_THRESHOLDS.paper_sharpe
    assert tuple(item.name for item in report.registered_strategies) == tuple(
        strategy.name for strategy in DEFAULT_STRATEGIES
    )
