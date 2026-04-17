from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
import unittest

from crypto.domain import FillRecord, FundingRate, InstrumentId, OrderSide
from crypto.paper import PaperSession
from crypto.reporting import build_paper_performance_report, build_strategy_catalog
from crypto.strategies import DEFAULT_STRATEGIES
from crypto.validation import DEFAULT_PROMOTION_THRESHOLDS


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def _build_session() -> PaperSession:
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
    return session


class ReportingBuilderTests(unittest.TestCase):
    def test_report_builder_returns_graph_ready_metrics_and_explicit_strategy_catalog(self) -> None:
        session = _build_session()

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

        self.assertEqual(report.metadata.strategy_id, "trend_following_breakout")
        self.assertEqual(report.metadata.exchange_id, "binance_perpetual")
        self.assertEqual(report.metadata.primary_cadence, "15m")
        self.assertEqual(report.metadata.feature_cadences, ("15m", "1h"))

        self.assertEqual(
            [series.slug for series in report.graphs],
            [
                "equity_curve",
                "drawdown_curve",
                "gross_exposure_curve",
                "net_exposure_curve",
            ],
        )
        self.assertEqual(len(report.graphs[0].points), 4)
        self.assertAlmostEqual(report.graphs[0].points[-1].value, 10_450.0)
        self.assertAlmostEqual(report.graphs[1].points[2].value, 0.038834951456310676)

        self.assertAlmostEqual(report.summary.total_return, 0.045)
        self.assertAlmostEqual(report.summary.max_drawdown, 0.038834951456310676)
        self.assertEqual(report.summary.paper_days, 4)
        self.assertAlmostEqual(report.summary.realized_fees, 8.0)
        self.assertAlmostEqual(report.summary.net_funding, -2.5)
        self.assertAlmostEqual(report.summary.max_peer_correlation or 0.0, 1.0)
        self.assertGreater(report.summary.paper_sharpe, 0.0)

        self.assertEqual(report.thresholds.oos_sharpe, DEFAULT_PROMOTION_THRESHOLDS.oos_sharpe)
        self.assertEqual(
            tuple(item.name for item in report.registered_strategies),
            tuple(strategy.name for strategy in DEFAULT_STRATEGIES),
        )

    def test_report_builder_requires_equity_observations(self) -> None:
        session = PaperSession(
            session_id="paper-btc-breakout",
            strategy_id="trend_following_breakout",
            started_at=_utc("2026-01-01T00:00:00"),
        )

        with self.assertRaisesRegex(ValueError, "paper reporting requires at least one equity observation"):
            build_paper_performance_report(session)

    def test_strategy_catalog_stays_explicit_for_custom_strategy_sets(self) -> None:
        catalog = build_strategy_catalog(DEFAULT_STRATEGIES[:2])

        self.assertEqual(len(catalog), 2)
        self.assertEqual(catalog[0].name, DEFAULT_STRATEGIES[0].name)
        self.assertEqual(catalog[1].family, DEFAULT_STRATEGIES[1].family)


if __name__ == "__main__":
    unittest.main()
