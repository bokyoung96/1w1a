from __future__ import annotations

import unittest

from crypto.factory import (
    CandidateEvaluation,
    CandidatePerformanceMetrics,
    CandidateRobustnessMetrics,
    FactoryCandidate,
    RobustnessWeights,
    compute_robustness_score,
    rank_candidates,
    score_candidate,
)


def _candidate(*, candidate_id: str, family: str = "trend-following breakout") -> FactoryCandidate:
    return FactoryCandidate(
        candidate_id=candidate_id,
        strategy_name=candidate_id.split(":")[0],
        family=family,
        primary_cadence="15m",
        feature_cadences=("15m", "1h"),
        params={"lookback_bars": 20},
        generation_stage="fixed_grid",
    )


class FactoryScoringTests(unittest.TestCase):
    def test_robustness_score_keeps_component_breakdowns_explicit(self) -> None:
        metrics = CandidateRobustnessMetrics(
            oos_stability=0.90,
            parameter_stability=0.60,
            regime_stability=0.30,
        )

        score = compute_robustness_score(
            metrics,
            weights=RobustnessWeights(
                oos_stability=0.5,
                parameter_stability=0.25,
                regime_stability=0.25,
            ),
        )

        self.assertAlmostEqual(score, 0.675)

    def test_scoring_applies_post_cost_performance_with_explicit_turnover_penalty(self) -> None:
        candidate = _candidate(candidate_id="trend_following_breakout:lookback=20")
        low_turnover = score_candidate(
            CandidateEvaluation(
                candidate=candidate,
                performance=CandidatePerformanceMetrics(
                    gross_return=0.22,
                    post_cost_return=0.18,
                    turnover=0.40,
                    transaction_cost=0.04,
                ),
                robustness=CandidateRobustnessMetrics(
                    oos_stability=0.80,
                    parameter_stability=0.70,
                    regime_stability=0.75,
                ),
            ),
            turnover_penalty_rate=0.10,
        )
        high_turnover = score_candidate(
            CandidateEvaluation(
                candidate=candidate,
                performance=CandidatePerformanceMetrics(
                    gross_return=0.22,
                    post_cost_return=0.18,
                    turnover=1.20,
                    transaction_cost=0.04,
                ),
                robustness=CandidateRobustnessMetrics(
                    oos_stability=0.80,
                    parameter_stability=0.70,
                    regime_stability=0.75,
                ),
            ),
            turnover_penalty_rate=0.10,
        )

        self.assertAlmostEqual(low_turnover.performance_score, 0.18)
        self.assertAlmostEqual(low_turnover.cost_drag, 0.04)
        self.assertAlmostEqual(low_turnover.robustness_score, 0.755)
        self.assertAlmostEqual(low_turnover.turnover_penalty, 0.04)
        self.assertAlmostEqual(high_turnover.turnover_penalty, 0.12)
        self.assertGreater(low_turnover.total_score, high_turnover.total_score)

    def test_rank_candidates_orders_scorecards_by_total_score_descending(self) -> None:
        ranked = rank_candidates(
            (
                CandidateEvaluation(
                    candidate=_candidate(candidate_id="mean_reversion:z=1.0", family="mean reversion"),
                    performance=CandidatePerformanceMetrics(
                        gross_return=0.15,
                        post_cost_return=0.10,
                        turnover=0.30,
                    ),
                    robustness=CandidateRobustnessMetrics(
                        oos_stability=0.85,
                        parameter_stability=0.70,
                        regime_stability=0.65,
                    ),
                ),
                CandidateEvaluation(
                    candidate=_candidate(
                        candidate_id="trend_following_breakout:lookback=40",
                        family="trend-following breakout",
                    ),
                    performance=CandidatePerformanceMetrics(
                        gross_return=0.18,
                        post_cost_return=0.14,
                        turnover=0.20,
                    ),
                    robustness=CandidateRobustnessMetrics(
                        oos_stability=0.90,
                        parameter_stability=0.75,
                        regime_stability=0.80,
                    ),
                ),
            ),
            turnover_penalty_rate=0.05,
        )

        self.assertEqual(
            [scorecard.candidate.strategy_name for scorecard in ranked],
            ["trend_following_breakout", "mean_reversion"],
        )
        self.assertGreater(ranked[0].total_score, ranked[1].total_score)


if __name__ == "__main__":
    unittest.main()
