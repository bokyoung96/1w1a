from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from itertools import product
from pathlib import Path
from random import Random
import sys
from types import ModuleType
from typing import Protocol


MIN_CANDIDATE_POOL_SIZE = 30
MAX_CANDIDATE_POOL_SIZE = 50
DEFAULT_CANDIDATE_POOL_SIZE = 40


class StrategyDefinitionLike(Protocol):
    name: str
    family: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]


Numeric = int | float


@dataclass(frozen=True)
class CandidateParameterRange:
    name: str
    seed_values: tuple[Numeric, ...]
    min_value: float
    max_value: float
    expansion_step: float
    integer: bool = False

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("parameter name must not be empty")
        if not self.seed_values:
            raise ValueError(f"parameter {self.name!r} must provide at least one seed value")
        if self.min_value > self.max_value:
            raise ValueError(f"parameter {self.name!r} has invalid bounds")
        if self.expansion_step <= 0:
            raise ValueError(f"parameter {self.name!r} must use a positive expansion_step")
        for seed_value in self.seed_values:
            coerced = float(seed_value)
            if coerced < self.min_value or coerced > self.max_value:
                raise ValueError(
                    f"parameter {self.name!r} seed {seed_value!r} falls outside the declared bounds"
                )

    def coerce(self, value: float) -> Numeric:
        clamped = min(max(value, self.min_value), self.max_value)
        if self.integer:
            return int(round(clamped))
        return round(clamped, 6)


@dataclass(frozen=True)
class CandidateProfile:
    strategy: StrategyDefinitionLike
    parameters: tuple[CandidateParameterRange, ...]
    promising_seed_indices: tuple[int, ...] = (1,)

    def __post_init__(self) -> None:
        if not self.parameters:
            raise ValueError("candidate profiles require at least one parameter")
        if not self.strategy.name:
            raise ValueError("candidate profiles require a strategy name")
        if not self.strategy.family:
            raise ValueError("candidate profiles require a strategy family")
        if any(index < 0 for index in self.promising_seed_indices):
            raise ValueError("promising seed indices must be non-negative")


@dataclass(frozen=True)
class FactoryCandidate:
    candidate_id: str
    strategy_name: str
    family: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]
    params: dict[str, Numeric]
    generation_stage: str
    parent_candidate_id: str | None = None


@dataclass(frozen=True)
class _LoadedStrategyDefinition:
    name: str
    family: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]


def _format_numeric(value: Numeric) -> str:
    if isinstance(value, int):
        return str(value)
    if float(value).is_integer():
        return str(int(value))
    return format(float(value), ".6g")


def _build_candidate(
    *,
    strategy: StrategyDefinitionLike,
    params: dict[str, Numeric],
    generation_stage: str,
    parent_candidate_id: str | None = None,
) -> FactoryCandidate:
    candidate_id = ":".join(
        [
            strategy.name,
            ":".join(
                f"{name}={_format_numeric(value)}"
                for name, value in sorted(params.items())
            ),
        ]
    )
    return FactoryCandidate(
        candidate_id=candidate_id,
        strategy_name=strategy.name,
        family=strategy.family,
        primary_cadence=strategy.primary_cadence,
        feature_cadences=strategy.feature_cadences,
        params=params,
        generation_stage=generation_stage,
        parent_candidate_id=parent_candidate_id,
    )


def build_fixed_grid_candidates(profile: CandidateProfile) -> tuple[FactoryCandidate, ...]:
    value_axes = [parameter.seed_values for parameter in profile.parameters]
    candidates: list[FactoryCandidate] = []
    for combination in product(*value_axes):
        params = {
            parameter.name: parameter.coerce(float(value))
            for parameter, value in zip(profile.parameters, combination)
        }
        candidates.append(
            _build_candidate(
                strategy=profile.strategy,
                params=params,
                generation_stage="fixed_grid",
            )
        )
    return tuple(candidates)


def _iter_expanded_candidates(
    *,
    profile: CandidateProfile,
    seed_candidates: tuple[FactoryCandidate, ...],
    random_seed: int,
):
    if not seed_candidates:
        return

    anchor_indices = profile.promising_seed_indices or ((len(seed_candidates) - 1) // 2,)
    valid_anchor_indices = tuple(
        index for index in anchor_indices if index < len(seed_candidates)
    ) or ((len(seed_candidates) - 1) // 2,)

    rng = Random(random_seed)
    existing_ids = {candidate.candidate_id for candidate in seed_candidates}
    anchor_cursor = 0

    while True:
        anchor = seed_candidates[valid_anchor_indices[anchor_cursor % len(valid_anchor_indices)]]
        anchor_cursor += 1

        for _ in range(24):
            params: dict[str, Numeric] = {}
            for parameter in profile.parameters:
                anchor_value = float(anchor.params[parameter.name])
                if parameter.integer:
                    step_multiplier = float(rng.choice((-1, 1)))
                else:
                    step_multiplier = rng.choice((-1.0, -0.5, 0.5, 1.0))
                jitter = anchor_value + (parameter.expansion_step * step_multiplier)
                params[parameter.name] = parameter.coerce(jitter)

            candidate = _build_candidate(
                strategy=profile.strategy,
                params=params,
                generation_stage="adaptive_random",
                parent_candidate_id=anchor.candidate_id,
            )
            if candidate.candidate_id not in existing_ids:
                existing_ids.add(candidate.candidate_id)
                yield candidate
                break
        else:
            return


def expand_candidates(
    *,
    profile: CandidateProfile,
    seed_candidates: tuple[FactoryCandidate, ...],
    target_count: int,
    random_seed: int,
) -> tuple[FactoryCandidate, ...]:
    if target_count <= len(seed_candidates):
        return seed_candidates[:target_count]

    expanded = list(seed_candidates)
    for candidate in _iter_expanded_candidates(
        profile=profile,
        seed_candidates=seed_candidates,
        random_seed=random_seed,
    ):
        expanded.append(candidate)
        if len(expanded) >= target_count:
            break
    return tuple(expanded)


def normalize_target_candidate_count(target_count: int) -> int:
    return max(MIN_CANDIDATE_POOL_SIZE, min(MAX_CANDIDATE_POOL_SIZE, target_count))


def generate_candidate_pool(
    *,
    profiles: tuple[CandidateProfile, ...] | None = None,
    target_count: int = DEFAULT_CANDIDATE_POOL_SIZE,
    random_seed: int = 7,
) -> tuple[FactoryCandidate, ...]:
    profiles = profiles or DEFAULT_CANDIDATE_PROFILES
    normalized_target = normalize_target_candidate_count(target_count)

    fixed_grid_candidates: list[FactoryCandidate] = []
    expansion_streams = []

    for index, profile in enumerate(profiles):
        seeds = build_fixed_grid_candidates(profile)
        fixed_grid_candidates.extend(seeds)
        expansion_streams.append(
            _iter_expanded_candidates(
                profile=profile,
                seed_candidates=seeds,
                random_seed=random_seed + index,
            )
        )

    if normalized_target <= len(fixed_grid_candidates):
        return tuple(fixed_grid_candidates[:normalized_target])

    pool = list(fixed_grid_candidates)
    active_streams = list(expansion_streams)

    while len(pool) < normalized_target and active_streams:
        next_round: list[object] = []
        for stream in active_streams:
            try:
                pool.append(next(stream))
            except StopIteration:
                continue
            else:
                next_round.append(stream)
            if len(pool) >= normalized_target:
                break
        active_streams = next_round

    return tuple(pool)


def _load_strategy_registry_module() -> ModuleType:
    registry_path = Path(__file__).resolve().parents[1] / "strategies" / "registry.py"
    spec = importlib.util.spec_from_file_location("crypto_strategy_registry_for_factory", registry_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load strategy registry from {registry_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_default_strategies() -> tuple[_LoadedStrategyDefinition, ...]:
    registry_module = _load_strategy_registry_module()
    return tuple(
        _LoadedStrategyDefinition(
            name=strategy.name,
            family=strategy.family,
            primary_cadence=strategy.primary_cadence,
            feature_cadences=tuple(strategy.feature_cadences),
        )
        for strategy in registry_module.DEFAULT_STRATEGIES
    )


def _build_default_candidate_profiles() -> tuple[CandidateProfile, ...]:
    parameter_library = {
        "trend_following_breakout": (
            CandidateParameterRange("lookback_bars", (20, 40, 60), 10, 100, 10, integer=True),
            CandidateParameterRange("breakout_buffer_bps", (5.0,), 2.5, 20.0, 2.5),
        ),
        "mean_reversion": (
            CandidateParameterRange("zscore_entry", (1.0, 1.5, 2.0), 0.5, 3.0, 0.25),
            CandidateParameterRange("reversion_window_bars", (24,), 12, 72, 12, integer=True),
        ),
        "perp_momentum_relative_strength_rotation": (
            CandidateParameterRange("relative_strength_window", (12, 24, 48), 6, 72, 6, integer=True),
            CandidateParameterRange("top_bucket_count", (2,), 1, 5, 1, integer=True),
        ),
        "funding_rate_carry_funding_aware_filter": (
            CandidateParameterRange("funding_rank_window", (8, 16, 24), 4, 40, 4, integer=True),
            CandidateParameterRange("max_negative_funding_bps", (1.0,), 0.25, 4.0, 0.25),
        ),
        "volatility_regime_breakout_confirmation": (
            CandidateParameterRange("volatility_lookback_bars", (20, 40, 60), 10, 90, 10, integer=True),
            CandidateParameterRange("regime_threshold", (1.0,), 0.5, 2.0, 0.25),
        ),
        "trend_pullback_continuation": (
            CandidateParameterRange("pullback_window_bars", (10, 20, 30), 5, 45, 5, integer=True),
            CandidateParameterRange("retracement_pct", (0.25,), 0.1, 0.6, 0.05),
        ),
        "short_term_reversal_exhaustion_fade": (
            CandidateParameterRange("reversal_window_bars", (4, 8, 12), 2, 20, 2, integer=True),
            CandidateParameterRange("exhaustion_zscore", (1.5,), 0.5, 3.0, 0.25),
        ),
        "volume_participation_imbalance": (
            CandidateParameterRange("imbalance_window_bars", (6, 12, 18), 3, 24, 3, integer=True),
            CandidateParameterRange("participation_multiplier", (1.25,), 1.0, 2.0, 0.125),
        ),
        "basis_spread_dislocation_proxy": (
            CandidateParameterRange("basis_window_bars", (12, 24, 36), 6, 48, 6, integer=True),
            CandidateParameterRange("dislocation_zscore", (1.0,), 0.5, 2.5, 0.25),
        ),
        "market_structure_support_resistance_reaction": (
            CandidateParameterRange("structure_window_bars", (20, 40, 60), 10, 90, 10, integer=True),
            CandidateParameterRange("reaction_buffer_bps", (7.5,), 2.5, 20.0, 2.5),
        ),
    }

    profiles: list[CandidateProfile] = []
    for strategy in _load_default_strategies():
        parameters = parameter_library.get(strategy.name)
        if parameters is None:
            raise ValueError(f"missing candidate parameter profile for strategy {strategy.name!r}")
        profiles.append(
            CandidateProfile(
                strategy=strategy,
                parameters=parameters,
                promising_seed_indices=(1,),
            )
        )
    return tuple(profiles)


DEFAULT_CANDIDATE_PROFILES = _build_default_candidate_profiles()


__all__ = [
    "DEFAULT_CANDIDATE_POOL_SIZE",
    "DEFAULT_CANDIDATE_PROFILES",
    "MAX_CANDIDATE_POOL_SIZE",
    "MIN_CANDIDATE_POOL_SIZE",
    "CandidateParameterRange",
    "CandidateProfile",
    "FactoryCandidate",
    "build_fixed_grid_candidates",
    "expand_candidates",
    "generate_candidate_pool",
    "normalize_target_candidate_count",
]
