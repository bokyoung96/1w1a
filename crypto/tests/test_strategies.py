import pandas as pd
from pandas.testing import assert_frame_equal

from crypto.strategies import (
    DEFAULT_STRATEGIES,
    align_feature_frames,
    list_strategy_families,
)


EXPECTED_FAMILIES = (
    "trend-following breakout",
    "mean reversion",
    "perp momentum / relative-strength rotation",
    "funding-rate carry / funding-aware filter",
    "volatility regime / breakout confirmation",
)


def test_registry_lists_the_approved_initial_strategy_families() -> None:
    assert list_strategy_families() == EXPECTED_FAMILIES
    assert tuple(strategy.family for strategy in DEFAULT_STRATEGIES) == EXPECTED_FAMILIES
    assert {strategy.primary_cadence for strategy in DEFAULT_STRATEGIES} == {"15m"}


def test_multi_frequency_alignment_reindexes_features_to_primary_15m_cadence_without_lookahead() -> None:
    primary_index = pd.to_datetime(
        [
            "2026-01-01 00:15:00+00:00",
            "2026-01-01 00:30:00+00:00",
            "2026-01-01 00:45:00+00:00",
            "2026-01-01 01:00:00+00:00",
        ]
    )
    feature_frames = {
        "funding_rate_1h": pd.DataFrame(
            {"BTCUSDT": [0.0010, 0.0020]},
            index=pd.to_datetime(["2026-01-01 00:00:00+00:00", "2026-01-01 01:00:00+00:00"]),
        ),
        "micro_trend_5m": pd.DataFrame(
            {"BTCUSDT": [10.0, 20.0, 30.0, 40.0, 50.0]},
            index=pd.to_datetime(
                [
                    "2026-01-01 00:10:00+00:00",
                    "2026-01-01 00:20:00+00:00",
                    "2026-01-01 00:35:00+00:00",
                    "2026-01-01 00:50:00+00:00",
                    "2026-01-01 01:00:00+00:00",
                ]
            ),
        ),
    }

    aligned = align_feature_frames(primary_index=primary_index, feature_frames=feature_frames)

    expected_funding = pd.DataFrame(
        {"BTCUSDT": [0.0010, 0.0010, 0.0010, 0.0020]},
        index=primary_index,
    )
    expected_micro = pd.DataFrame(
        {"BTCUSDT": [10.0, 20.0, 30.0, 40.0]},
        index=primary_index,
    )

    assert_frame_equal(aligned["funding_rate_1h"], expected_funding)
    assert_frame_equal(aligned["micro_trend_5m"], expected_micro)

    aligned_again = align_feature_frames(primary_index=primary_index, feature_frames=feature_frames)
    assert_frame_equal(aligned_again["funding_rate_1h"], expected_funding)
    assert_frame_equal(aligned_again["micro_trend_5m"], expected_micro)
