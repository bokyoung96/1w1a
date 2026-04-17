from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StrategyDefinition:
    name: str
    family: str
    primary_cadence: str = "15m"
    feature_cadences: tuple[str, ...] = ("15m",)

    @property
    def documentation_path(self) -> Path:
        return Path(__file__).with_name("docs") / f"{self.name}.md"


INITIAL_STRATEGY_FAMILIES: tuple[str, ...] = (
    "trend-following breakout",
    "mean reversion",
    "perp momentum / relative-strength rotation",
    "funding-rate carry / funding-aware filter",
    "volatility regime / breakout confirmation",
    "trend pullback continuation",
    "short-term reversal / exhaustion fade",
    "volume / participation imbalance",
    "basis / spread dislocation proxy",
    "market structure / support-resistance reaction",
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
    StrategyDefinition(
        name="trend_pullback_continuation",
        family="trend pullback continuation",
        feature_cadences=("15m", "1h", "4h"),
    ),
    StrategyDefinition(
        name="short_term_reversal_exhaustion_fade",
        family="short-term reversal / exhaustion fade",
        feature_cadences=("5m", "15m", "1h"),
    ),
    StrategyDefinition(
        name="volume_participation_imbalance",
        family="volume / participation imbalance",
        feature_cadences=("5m", "15m", "1h"),
    ),
    StrategyDefinition(
        name="basis_spread_dislocation_proxy",
        family="basis / spread dislocation proxy",
        feature_cadences=("15m", "1h", "8h"),
    ),
    StrategyDefinition(
        name="market_structure_support_resistance_reaction",
        family="market structure / support-resistance reaction",
        feature_cadences=("5m", "15m", "1h"),
    ),
)



def list_strategy_families() -> tuple[str, ...]:
    return INITIAL_STRATEGY_FAMILIES
