from __future__ import annotations

import unittest
from datetime import datetime, timezone

from crypto.factory import (
    FactoryCandidate,
    SelectedStrategy,
    StrategyScoreBreakdown,
    build_allocation_trigger,
    build_portfolio_allocation,
)


def _selected_strategy(
    *,
    strategy_name: str,
    family: str,
    total_score: float,
    signal_strength: float,
    instrument_symbol: str = "BTC/USDT:USDT",
) -> SelectedStrategy:
    candidate = FactoryCandidate(
        candidate_id=f"{strategy_name}:seed=1",
        strategy_name=strategy_name,
        family=family,
        primary_cadence="15m",
        feature_cadences=("15m", "1h"),
        params={"seed": 1},
        generation_stage="fixed_grid",
    )
    scorecard = StrategyScoreBreakdown(
        candidate=candidate,
        gross_return=0.20,
        post_cost_return=0.16,
        cost_drag=0.04,
        performance_score=0.16,
        turnover=0.30,
        transaction_cost=0.04,
        turnover_penalty=0.02,
        oos_stability_score=0.80,
        parameter_stability_score=0.75,
        regime_stability_score=0.70,
        robustness_score=0.75,
        total_score=total_score,
    )
    return SelectedStrategy(
        scorecard=scorecard,
        returns=(0.01, 0.02, 0.03),
        signal_strength=signal_strength,
        instrument_symbol=instrument_symbol,
        max_pairwise_correlation=0.25,
        selection_score=total_score,
    )


class FactoryAllocationTests(unittest.TestCase):
    def test_portfolio_allocation_weights_families_first_and_strategies_second(self) -> None:
        selected = (
            _selected_strategy(
                strategy_name="trend_alpha_1",
                family="trend-following breakout",
                total_score=0.90,
                signal_strength=1.0,
            ),
            _selected_strategy(
                strategy_name="trend_alpha_2",
                family="trend-following breakout",
                total_score=0.60,
                signal_strength=1.0,
            ),
            _selected_strategy(
                strategy_name="mean_alpha_1",
                family="mean reversion",
                total_score=0.75,
                signal_strength=-1.0,
            ),
            _selected_strategy(
                strategy_name="mean_alpha_2",
                family="mean reversion",
                total_score=0.25,
                signal_strength=-1.0,
            ),
        )
        trigger = build_allocation_trigger(
            "funding_shift",
            event_keys=("funding", "volatility"),
            triggered_at=datetime(2026, 4, 17, tzinfo=timezone.utc),
        )

        plan = build_portfolio_allocation(selected, trigger=trigger)

        self.assertEqual(plan.trigger.reason, "funding_shift")
        self.assertEqual(len(plan.family_allocations), 2)
        family_weights = {item.family: item.weight for item in plan.family_allocations}
        self.assertAlmostEqual(sum(family_weights.values()), 1.0)
        self.assertGreater(
            family_weights["trend-following breakout"],
            family_weights["mean reversion"],
        )

        self.assertEqual(len(plan.strategy_allocations), 4)
        self.assertTrue(
            all(len(item.execution_slices) == 3 for item in plan.strategy_allocations)
        )
        self.assertTrue(
            all(
                abs(sum(stage.fraction for stage in item.execution_slices) - 1.0) < 1e-9
                for item in plan.strategy_allocations
            )
        )

        self.assertEqual(len(plan.instrument_allocations), 1)
        instrument = plan.instrument_allocations[0]
        self.assertEqual(instrument.instrument_symbol, "BTC/USDT:USDT")
        self.assertEqual(instrument.contributor_count, 4)
        self.assertAlmostEqual(instrument.gross_target_weight, 1.0)
        self.assertLess(instrument.net_target_weight, 0.25)

    def test_portfolio_allocation_requires_selected_strategies(self) -> None:
        with self.assertRaisesRegex(ValueError, "selected strategies"):
            build_portfolio_allocation(
                (),
                trigger=build_allocation_trigger("price_breakout"),
            )


if __name__ == "__main__":
    unittest.main()
