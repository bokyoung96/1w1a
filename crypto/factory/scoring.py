from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .candidates import FactoryCandidate


@dataclass(frozen=True, slots=True)
class RobustnessWeights:
    oos_stability: float = 0.4
    parameter_stability: float = 0.3
    regime_stability: float = 0.3

    def __post_init__(self) -> None:
        total = self.oos_stability + self.parameter_stability + self.regime_stability
        if total <= 0:
            raise ValueError("robustness weights must sum to a positive value")


@dataclass(frozen=True, slots=True)
class CandidatePerformanceMetrics:
    gross_return: float
    post_cost_return: float
    turnover: float
    transaction_cost: float = 0.0

    @property
    def cost_drag(self) -> float:
        return self.gross_return - self.post_cost_return


@dataclass(frozen=True, slots=True)
class CandidateRobustnessMetrics:
    oos_stability: float
    parameter_stability: float
    regime_stability: float


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    candidate: FactoryCandidate
    performance: CandidatePerformanceMetrics
    robustness: CandidateRobustnessMetrics


@dataclass(frozen=True, slots=True)
class StrategyScoreBreakdown:
    candidate: FactoryCandidate
    gross_return: float
    post_cost_return: float
    cost_drag: float
    performance_score: float
    turnover: float
    transaction_cost: float
    turnover_penalty: float
    oos_stability_score: float
    parameter_stability_score: float
    regime_stability_score: float
    robustness_score: float
    total_score: float


def compute_robustness_score(
    metrics: CandidateRobustnessMetrics,
    *,
    weights: RobustnessWeights = RobustnessWeights(),
) -> float:
    total_weight = (
        weights.oos_stability + weights.parameter_stability + weights.regime_stability
    )
    return (
        (metrics.oos_stability * weights.oos_stability)
        + (metrics.parameter_stability * weights.parameter_stability)
        + (metrics.regime_stability * weights.regime_stability)
    ) / total_weight


def compute_turnover_penalty(
    metrics: CandidatePerformanceMetrics,
    *,
    turnover_penalty_rate: float = 0.05,
) -> float:
    if turnover_penalty_rate < 0:
        raise ValueError("turnover_penalty_rate must not be negative")
    return max(metrics.turnover, 0.0) * turnover_penalty_rate


def score_candidate(
    evaluation: CandidateEvaluation,
    *,
    weights: RobustnessWeights = RobustnessWeights(),
    turnover_penalty_rate: float = 0.05,
) -> StrategyScoreBreakdown:
    robustness_score = compute_robustness_score(evaluation.robustness, weights=weights)
    turnover_penalty = compute_turnover_penalty(
        evaluation.performance,
        turnover_penalty_rate=turnover_penalty_rate,
    )
    performance_score = evaluation.performance.post_cost_return
    total_score = performance_score + robustness_score - turnover_penalty

    return StrategyScoreBreakdown(
        candidate=evaluation.candidate,
        gross_return=evaluation.performance.gross_return,
        post_cost_return=evaluation.performance.post_cost_return,
        cost_drag=evaluation.performance.cost_drag,
        performance_score=performance_score,
        turnover=evaluation.performance.turnover,
        transaction_cost=evaluation.performance.transaction_cost,
        turnover_penalty=turnover_penalty,
        oos_stability_score=evaluation.robustness.oos_stability,
        parameter_stability_score=evaluation.robustness.parameter_stability,
        regime_stability_score=evaluation.robustness.regime_stability,
        robustness_score=robustness_score,
        total_score=total_score,
    )


def rank_candidates(
    evaluations: Iterable[CandidateEvaluation],
    *,
    weights: RobustnessWeights = RobustnessWeights(),
    turnover_penalty_rate: float = 0.05,
) -> tuple[StrategyScoreBreakdown, ...]:
    scorecards = tuple(
        score_candidate(
            evaluation,
            weights=weights,
            turnover_penalty_rate=turnover_penalty_rate,
        )
        for evaluation in evaluations
    )
    return tuple(
        sorted(
            scorecards,
            key=lambda scorecard: (
                -scorecard.total_score,
                scorecard.candidate.family,
                scorecard.candidate.strategy_name,
                scorecard.candidate.candidate_id,
            ),
        )
    )


__all__ = (
    "CandidateEvaluation",
    "CandidatePerformanceMetrics",
    "CandidateRobustnessMetrics",
    "RobustnessWeights",
    "StrategyScoreBreakdown",
    "compute_robustness_score",
    "compute_turnover_penalty",
    "rank_candidates",
    "score_candidate",
)
