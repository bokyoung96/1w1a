from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from .selection import SelectedStrategy


@dataclass(frozen=True, slots=True)
class AllocationTrigger:
    reason: str
    triggered_at: datetime
    event_keys: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutionSlice:
    stage: str
    fraction: float
    target_weight: float


@dataclass(frozen=True, slots=True)
class StrategyAllocation:
    strategy_name: str
    family: str
    instrument_symbol: str
    signal_strength: float
    score: float
    family_weight: float
    within_family_weight: float
    target_weight: float
    max_pairwise_correlation: float
    execution_slices: tuple[ExecutionSlice, ...]


@dataclass(frozen=True, slots=True)
class FamilyAllocation:
    family: str
    weight: float
    strategy_count: int


@dataclass(frozen=True, slots=True)
class InstrumentAllocation:
    instrument_symbol: str
    net_target_weight: float
    gross_target_weight: float
    contributor_count: int


@dataclass(frozen=True, slots=True)
class PortfolioAllocationPlan:
    trigger: AllocationTrigger
    family_allocations: tuple[FamilyAllocation, ...]
    strategy_allocations: tuple[StrategyAllocation, ...]
    instrument_allocations: tuple[InstrumentAllocation, ...]
    total_net_target_weight: float
    total_gross_target_weight: float


def build_allocation_trigger(
    reason: str,
    *,
    event_keys: tuple[str, ...] = (),
    triggered_at: datetime | None = None,
) -> AllocationTrigger:
    return AllocationTrigger(
        reason=reason,
        triggered_at=triggered_at or datetime.now(timezone.utc),
        event_keys=event_keys,
    )


def build_portfolio_allocation(
    selected: Iterable[SelectedStrategy],
    *,
    trigger: AllocationTrigger,
    execution_stage_fractions: tuple[float, ...] = (0.5, 0.3, 0.2),
) -> PortfolioAllocationPlan:
    selected = tuple(selected)
    if not selected:
        raise ValueError("selected strategies are required to build an allocation plan")

    stage_fractions = _normalize_stage_fractions(execution_stage_fractions)

    family_strengths: dict[str, float] = {}
    strategies_by_family: dict[str, list[SelectedStrategy]] = {}
    for strategy in selected:
        family = strategy.scorecard.candidate.family
        strength = max(abs(strategy.scorecard.total_score), 1e-9)
        family_strengths[family] = family_strengths.get(family, 0.0) + strength
        strategies_by_family.setdefault(family, []).append(strategy)

    total_family_strength = sum(family_strengths.values())
    family_allocations = tuple(
        FamilyAllocation(
            family=family,
            weight=family_strength / total_family_strength,
            strategy_count=len(strategies_by_family[family]),
        )
        for family, family_strength in sorted(
            family_strengths.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )
    family_weight_map = {
        allocation.family: allocation.weight for allocation in family_allocations
    }

    strategy_allocations: list[StrategyAllocation] = []
    for family, strategies in sorted(strategies_by_family.items()):
        total_strategy_strength = sum(max(abs(strategy.scorecard.total_score), 1e-9) for strategy in strategies)
        family_weight = family_weight_map[family]
        for strategy in sorted(
            strategies,
            key=lambda item: (
                -item.scorecard.total_score,
                item.scorecard.candidate.strategy_name,
                item.scorecard.candidate.candidate_id,
            ),
        ):
            strategy_strength = max(abs(strategy.scorecard.total_score), 1e-9)
            within_family_weight = strategy_strength / total_strategy_strength
            absolute_weight = family_weight * within_family_weight
            signed_target_weight = absolute_weight if strategy.signal_strength >= 0 else -absolute_weight
            strategy_allocations.append(
                StrategyAllocation(
                    strategy_name=strategy.scorecard.candidate.strategy_name,
                    family=family,
                    instrument_symbol=strategy.instrument_symbol,
                    signal_strength=strategy.signal_strength,
                    score=strategy.scorecard.total_score,
                    family_weight=family_weight,
                    within_family_weight=within_family_weight,
                    target_weight=signed_target_weight,
                    max_pairwise_correlation=strategy.max_pairwise_correlation,
                    execution_slices=tuple(
                        ExecutionSlice(
                            stage=f"stage_{index + 1}",
                            fraction=fraction,
                            target_weight=signed_target_weight * fraction,
                        )
                        for index, fraction in enumerate(stage_fractions)
                    ),
                )
            )

    instrument_aggregates: dict[str, dict[str, float]] = {}
    for allocation in strategy_allocations:
        aggregate = instrument_aggregates.setdefault(
            allocation.instrument_symbol,
            {"net": 0.0, "gross": 0.0, "count": 0.0},
        )
        aggregate["net"] += allocation.target_weight
        aggregate["gross"] += abs(allocation.target_weight)
        aggregate["count"] += 1

    instrument_allocations = tuple(
        InstrumentAllocation(
            instrument_symbol=instrument_symbol,
            net_target_weight=values["net"],
            gross_target_weight=values["gross"],
            contributor_count=int(values["count"]),
        )
        for instrument_symbol, values in sorted(instrument_aggregates.items())
    )

    return PortfolioAllocationPlan(
        trigger=trigger,
        family_allocations=family_allocations,
        strategy_allocations=tuple(strategy_allocations),
        instrument_allocations=instrument_allocations,
        total_net_target_weight=sum(
            allocation.net_target_weight for allocation in instrument_allocations
        ),
        total_gross_target_weight=sum(
            allocation.gross_target_weight for allocation in instrument_allocations
        ),
    )


def _normalize_stage_fractions(stage_fractions: tuple[float, ...]) -> tuple[float, ...]:
    if not stage_fractions:
        raise ValueError("execution stage fractions must not be empty")
    if any(fraction <= 0 for fraction in stage_fractions):
        raise ValueError("execution stage fractions must be positive")
    total = sum(stage_fractions)
    return tuple(fraction / total for fraction in stage_fractions)


__all__ = (
    "AllocationTrigger",
    "ExecutionSlice",
    "FamilyAllocation",
    "InstrumentAllocation",
    "PortfolioAllocationPlan",
    "StrategyAllocation",
    "build_allocation_trigger",
    "build_portfolio_allocation",
)
