from __future__ import annotations

import unittest

from crypto.factory import (
    FactoryCandidate,
    RejectedCandidate,
    SelectedStrategy,
    SelectionCandidate,
    SelectionPolicy,
    StrategyScoreBreakdown,
    compute_return_correlation,
    select_orthogonal_candidates,
)


def _scorecard(
    *,
    family: str,
    strategy_name: str,
    total_score: float,
) -> StrategyScoreBreakdown:
    candidate = FactoryCandidate(
        candidate_id=f"{strategy_name}:seed=1",
        strategy_name=strategy_name,
        family=family,
        primary_cadence="15m",
        feature_cadences=("15m", "1h"),
        params={"seed": 1},
        generation_stage="fixed_grid",
    )
    return StrategyScoreBreakdown(
        candidate=candidate,
        gross_return=0.20,
        post_cost_return=0.15,
        cost_drag=0.05,
        performance_score=0.15,
        turnover=0.30,
        transaction_cost=0.05,
        turnover_penalty=0.02,
        oos_stability_score=0.80,
        parameter_stability_score=0.75,
        regime_stability_score=0.70,
        robustness_score=0.75,
        total_score=total_score,
    )


def _returns_for_family(index: int) -> tuple[float, ...]:
    base = [-0.01] * 10
    base[index] = 0.09
    return tuple(base)


class FactorySelectionTests(unittest.TestCase):
    def test_compute_return_correlation_handles_matching_series(self) -> None:
        correlation = compute_return_correlation(
            (0.01, 0.02, 0.03, 0.04),
            (0.01, 0.02, 0.03, 0.04),
        )

        assert correlation is not None
        self.assertAlmostEqual(correlation, 1.0)

    def test_select_orthogonal_candidates_builds_a_top_10_basket_from_a_30_candidate_pool(
        self,
    ) -> None:
        pool: list[SelectionCandidate] = []
        families = [f"family-{index}" for index in range(10)]
        for family_index, family in enumerate(families):
            base_returns = _returns_for_family(family_index)
            for variant in range(3):
                pool.append(
                    SelectionCandidate(
                        scorecard=_scorecard(
                            family=family,
                            strategy_name=f"{family}_variant_{variant}",
                            total_score=1.20 - (variant * 0.02) - (family_index * 0.01),
                        ),
                        returns=base_returns,
                        signal_strength=1.0 if variant % 2 == 0 else -1.0,
                        instrument_symbol="BTC/USDT:USDT",
                    )
                )

        result = select_orthogonal_candidates(
            pool,
            policy=SelectionPolicy(
                max_selected=10,
                max_pairwise_correlation=0.70,
                max_per_family=3,
                family_diversity_bonus=0.05,
            ),
        )

        self.assertEqual(len(result.selected), 10)
        self.assertEqual(len({item.scorecard.candidate.family for item in result.selected}), 10)
        self.assertTrue(all(isinstance(item, SelectedStrategy) for item in result.selected))
        self.assertTrue(
            all(item.max_pairwise_correlation <= 0.70 for item in result.selected)
        )
        correlation_rejections = [
            item for item in result.rejected if item.reason == "pairwise_correlation_exceeded"
        ]
        self.assertGreaterEqual(len(correlation_rejections), 20)
        self.assertTrue(all(isinstance(item, RejectedCandidate) for item in correlation_rejections))

    def test_selection_enforces_the_max_three_per_family_cap(self) -> None:
        candidates = []
        for index in range(8):
            returns = tuple(0.01 * ((spot + index) % 5) for spot in range(10))
            candidates.append(
                SelectionCandidate(
                    scorecard=_scorecard(
                        family="trend-following breakout",
                        strategy_name=f"trend_variant_{index}",
                        total_score=1.0 - (index * 0.01),
                    ),
                    returns=returns,
                )
            )

        result = select_orthogonal_candidates(
            candidates,
            policy=SelectionPolicy(max_selected=6, max_pairwise_correlation=0.99, max_per_family=3),
        )

        self.assertEqual(result.family_counts, {"trend-following breakout": 3})
        self.assertEqual(len(result.selected), 3)
        self.assertTrue(
            any(item.reason == "family_cap_reached" for item in result.rejected)
        )


if __name__ == "__main__":
    unittest.main()
