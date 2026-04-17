from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Iterable, Sequence

from .scoring import StrategyScoreBreakdown


@dataclass(frozen=True, slots=True)
class SelectionCandidate:
    scorecard: StrategyScoreBreakdown
    returns: tuple[float, ...]
    signal_strength: float = 1.0
    instrument_symbol: str = "BTC/USDT:USDT"


@dataclass(frozen=True, slots=True)
class SelectionPolicy:
    max_selected: int = 10
    max_pairwise_correlation: float = 0.70
    max_per_family: int = 3
    family_diversity_bonus: float = 0.05

    def __post_init__(self) -> None:
        if self.max_selected <= 0:
            raise ValueError("max_selected must be positive")
        if not 0 <= self.max_pairwise_correlation <= 1:
            raise ValueError("max_pairwise_correlation must be between 0 and 1")
        if self.max_per_family <= 0:
            raise ValueError("max_per_family must be positive")
        if self.family_diversity_bonus < 0:
            raise ValueError("family_diversity_bonus must not be negative")


@dataclass(frozen=True, slots=True)
class SelectedStrategy:
    scorecard: StrategyScoreBreakdown
    returns: tuple[float, ...]
    signal_strength: float
    instrument_symbol: str
    max_pairwise_correlation: float
    selection_score: float


@dataclass(frozen=True, slots=True)
class RejectedCandidate:
    scorecard: StrategyScoreBreakdown
    reason: str
    max_pairwise_correlation: float | None = None


@dataclass(frozen=True, slots=True)
class SelectionResult:
    selected: tuple[SelectedStrategy, ...]
    rejected: tuple[RejectedCandidate, ...]
    family_counts: dict[str, int]


def compute_return_correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None

    left_mean = mean(left)
    right_mean = mean(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    numerator = sum(a * b for a, b in zip(left_centered, right_centered))
    left_norm = sqrt(sum(value * value for value in left_centered))
    right_norm = sqrt(sum(value * value for value in right_centered))
    denominator = left_norm * right_norm
    if denominator == 0:
        return None
    return numerator / denominator


def select_orthogonal_candidates(
    candidates: Iterable[SelectionCandidate],
    *,
    policy: SelectionPolicy = SelectionPolicy(),
) -> SelectionResult:
    remaining = list(candidates)
    selected: list[SelectedStrategy] = []
    rejected: list[RejectedCandidate] = []
    family_counts: dict[str, int] = {}

    while remaining and len(selected) < policy.max_selected:
        best_index: int | None = None
        best_priority: tuple[float, float, str, str] | None = None
        best_correlation = 0.0

        for index, candidate in enumerate(remaining):
            family = candidate.scorecard.candidate.family
            if family_counts.get(family, 0) >= policy.max_per_family:
                continue

            max_correlation = _max_book_correlation(candidate, selected)
            if max_correlation > policy.max_pairwise_correlation:
                continue

            priority_score = candidate.scorecard.total_score
            if family not in family_counts:
                priority_score += policy.family_diversity_bonus

            priority = (
                priority_score,
                -max_correlation,
                family,
                candidate.scorecard.candidate.candidate_id,
            )
            if best_priority is None or priority > best_priority:
                best_priority = priority
                best_index = index
                best_correlation = max_correlation

        if best_index is None:
            break

        chosen = remaining.pop(best_index)
        family = chosen.scorecard.candidate.family
        family_counts[family] = family_counts.get(family, 0) + 1
        selected.append(
            SelectedStrategy(
                scorecard=chosen.scorecard,
                returns=chosen.returns,
                signal_strength=chosen.signal_strength,
                instrument_symbol=chosen.instrument_symbol,
                max_pairwise_correlation=best_correlation,
                selection_score=best_priority[0],
            )
        )

    for candidate in remaining:
        family = candidate.scorecard.candidate.family
        if family_counts.get(family, 0) >= policy.max_per_family:
            rejected.append(
                RejectedCandidate(
                    scorecard=candidate.scorecard,
                    reason="family_cap_reached",
                )
            )
            continue

        max_correlation = _max_book_correlation(candidate, selected)
        if max_correlation > policy.max_pairwise_correlation:
            rejected.append(
                RejectedCandidate(
                    scorecard=candidate.scorecard,
                    reason="pairwise_correlation_exceeded",
                    max_pairwise_correlation=max_correlation,
                )
            )
            continue

        rejected.append(
            RejectedCandidate(
                scorecard=candidate.scorecard,
                reason="selection_limit_reached",
                max_pairwise_correlation=max_correlation,
            )
        )

    return SelectionResult(
        selected=tuple(selected),
        rejected=tuple(rejected),
        family_counts=family_counts,
    )


def _max_book_correlation(
    candidate: SelectionCandidate,
    selected: Sequence[SelectedStrategy],
) -> float:
    max_correlation = 0.0
    for existing in selected:
        correlation = compute_return_correlation(candidate.returns, existing.returns)
        if correlation is None:
            continue
        max_correlation = max(max_correlation, abs(correlation))
    return max_correlation


__all__ = (
    "RejectedCandidate",
    "SelectedStrategy",
    "SelectionCandidate",
    "SelectionPolicy",
    "SelectionResult",
    "compute_return_correlation",
    "select_orthogonal_candidates",
)
