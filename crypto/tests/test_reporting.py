from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from crypto.factory import (
    CandidateEvaluation,
    CandidatePerformanceMetrics,
    CandidateRobustnessMetrics,
    SelectionCandidate,
    SelectionPolicy,
    build_allocation_trigger,
    build_portfolio_allocation,
    rank_candidates,
    select_orthogonal_candidates,
)
from crypto.domain import FillRecord, FundingRate, InstrumentId, OrderSide
from crypto.paper import PaperSession
from crypto.reporting import (
    build_factory_overview,
    build_paper_performance_report,
    build_strategy_catalog,
)
from crypto.strategies import DEFAULT_STRATEGIES
from crypto.validation import DEFAULT_PROMOTION_THRESHOLDS


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


class ReportingBuilderTests(unittest.TestCase):
    def test_report_builder_returns_graph_ready_metrics_and_explicit_strategy_catalog(self) -> None:
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

        self.assertAlmostEqual(report.summary.total_return, 0.045)
        self.assertAlmostEqual(report.summary.max_drawdown, 0.038834951456310676)
        self.assertEqual(report.summary.paper_days, 4)
        self.assertAlmostEqual(report.summary.realized_fees, 8.0)
        self.assertAlmostEqual(report.summary.net_funding, -2.5)
        self.assertAlmostEqual(report.summary.max_peer_correlation or 0.0, 1.0)
        self.assertGreater(report.summary.paper_sharpe, 0.0)

        self.assertEqual(
            report.thresholds.oos_sharpe,
            DEFAULT_PROMOTION_THRESHOLDS.oos_sharpe,
        )
        self.assertEqual(
            report.thresholds.paper_sharpe,
            DEFAULT_PROMOTION_THRESHOLDS.paper_sharpe,
        )
        self.assertEqual(
            tuple(item.name for item in report.registered_strategies),
            tuple(strategy.name for strategy in DEFAULT_STRATEGIES),
        )

    def test_report_builder_requires_equity_history_for_graph_output(self) -> None:
        session = PaperSession(
            session_id="paper-btc-breakout",
            strategy_id="trend_following_breakout",
            started_at=_utc("2026-01-01T00:00:00"),
        )

        with self.assertRaisesRegex(ValueError, "equity observation"):
            build_paper_performance_report(session)

    def test_report_builder_can_attach_factory_selection_and_allocation_outputs(self) -> None:
        scored = rank_candidates(
            (
                CandidateEvaluation(
                    candidate=_factory_candidate(
                        strategy_name="trend_following_breakout",
                        family="trend-following breakout",
                    ),
                    performance=CandidatePerformanceMetrics(
                        gross_return=0.20,
                        post_cost_return=0.16,
                        turnover=0.30,
                    ),
                    robustness=CandidateRobustnessMetrics(
                        oos_stability=0.85,
                        parameter_stability=0.75,
                        regime_stability=0.70,
                    ),
                ),
                CandidateEvaluation(
                    candidate=_factory_candidate(
                        strategy_name="mean_reversion",
                        family="mean reversion",
                    ),
                    performance=CandidatePerformanceMetrics(
                        gross_return=0.18,
                        post_cost_return=0.15,
                        turnover=0.25,
                    ),
                    robustness=CandidateRobustnessMetrics(
                        oos_stability=0.80,
                        parameter_stability=0.70,
                        regime_stability=0.75,
                    ),
                ),
            )
        )
        selection = select_orthogonal_candidates(
            (
                SelectionCandidate(
                    scorecard=scored[0],
                    returns=(0.01, 0.02, 0.03, 0.01),
                    signal_strength=1.0,
                    instrument_symbol="BTC/USDT:USDT",
                ),
                SelectionCandidate(
                    scorecard=scored[1],
                    returns=(-0.02, 0.03, -0.01, 0.02),
                    signal_strength=-1.0,
                    instrument_symbol="BTC/USDT:USDT",
                ),
            ),
            policy=SelectionPolicy(max_selected=10, max_pairwise_correlation=0.70, max_per_family=3),
        )
        allocation = build_portfolio_allocation(
            selection.selected,
            trigger=build_allocation_trigger("volatility_breakout"),
        )
        overview = build_factory_overview(
            selection,
            allocation,
            candidate_pool_size=40,
            strategy_definitions=DEFAULT_STRATEGIES,
        )

        session = PaperSession(
            session_id="paper-btc-basket",
            strategy_id="crypto_factory_basket",
            started_at=_utc("2026-01-01T00:00:00"),
            feature_cadences=("15m", "1h"),
        )
        session.record_equity(
            at=_utc("2026-01-01T00:15:00"),
            equity=10_000.0,
            gross_exposure=12_000.0,
            net_exposure=4_000.0,
        )
        session.record_equity(
            at=_utc("2026-01-02T00:15:00"),
            equity=10_150.0,
            gross_exposure=12_500.0,
            net_exposure=3_500.0,
        )

        report = build_paper_performance_report(
            session,
            strategy_definitions=DEFAULT_STRATEGIES,
            factory_overview=overview,
        )

        assert report.factory_overview is not None
        self.assertEqual(report.factory_overview.candidate_pool_size, 40)
        self.assertEqual(report.factory_overview.trigger_reason, "volatility_breakout")
        self.assertEqual(len(report.factory_overview.selected_basket), 2)
        self.assertEqual(
            tuple(item.strategy_name for item in report.factory_overview.selected_basket),
            ("trend_following_breakout", "mean_reversion"),
        )
        self.assertEqual(len(report.factory_overview.instrument_allocations), 1)
        self.assertEqual(report.graphs[0].slug, "equity_curve")


def _factory_candidate(*, strategy_name: str, family: str):
    from crypto.factory import FactoryCandidate

    return FactoryCandidate(
        candidate_id=f"{strategy_name}:seed=1",
        strategy_name=strategy_name,
        family=family,
        primary_cadence="15m",
        feature_cadences=("15m", "1h"),
        params={"seed": 1},
        generation_stage="fixed_grid",
    )


if __name__ == "__main__":
    unittest.main()
