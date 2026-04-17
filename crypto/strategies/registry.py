from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StrategyDefinition:
    name: str
    family: str
    primary_cadence: str = "15m"
    feature_cadences: tuple[str, ...] = ("15m",)


INITIAL_STRATEGY_FAMILIES: tuple[str, ...] = (
    "trend-following breakout",
    "mean reversion",
    "perp momentum / relative-strength rotation",
    "funding-rate carry / funding-aware filter",
    "volatility regime / breakout confirmation",
)


DEFAULT_STRATEGIES: tuple[StrategyDefinition, ...] = (
    StrategyDefinition(
        name="trend_following_breakout",
        family="trend-following breakout",
        feature_cadences=("15m", "1h"),
    ),
    StrategyDefinition(
        name="mean_reversion",
        family="mean reversion",
        feature_cadences=("15m", "1h"),
    ),
    StrategyDefinition(
        name="perp_momentum_relative_strength_rotation",
        family="perp momentum / relative-strength rotation",
        feature_cadences=("15m", "1h", "4h"),
    ),
    StrategyDefinition(
        name="funding_rate_carry_funding_aware_filter",
        family="funding-rate carry / funding-aware filter",
        feature_cadences=("15m", "1h", "8h"),
    ),
    StrategyDefinition(
        name="volatility_regime_breakout_confirmation",
        family="volatility regime / breakout confirmation",
        feature_cadences=("15m", "1h"),
    ),
)



def list_strategy_families() -> tuple[str, ...]:
    return INITIAL_STRATEGY_FAMILIES
