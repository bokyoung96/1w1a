from __future__ import annotations

from pathlib import Path
import unittest

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
    "trend pullback continuation",
    "short-term reversal / exhaustion fade",
    "volume / participation imbalance",
    "basis / spread dislocation proxy",
    "market structure / support-resistance reaction",
)

EXPECTED_STRATEGY_NAMES = (
    "trend_following_breakout",
    "mean_reversion",
    "perp_momentum_relative_strength_rotation",
    "funding_rate_carry_funding_aware_filter",
    "volatility_regime_breakout_confirmation",
    "trend_pullback_continuation",
    "short_term_reversal_exhaustion_fade",
    "volume_participation_imbalance",
    "basis_spread_dislocation_proxy",
    "market_structure_support_resistance_reaction",
)

STRATEGY_DOCS_ROOT = (
    Path(__file__).resolve().parents[2] / "crypto" / "strategies" / "docs"
)


class StrategyRegistryTests(unittest.TestCase):
    def test_registry_lists_the_approved_initial_strategy_families(self) -> None:
        self.assertEqual(list_strategy_families(), EXPECTED_FAMILIES)
        self.assertEqual(
            tuple(strategy.name for strategy in DEFAULT_STRATEGIES),
            EXPECTED_STRATEGY_NAMES,
        )
        self.assertEqual(
            tuple(strategy.family for strategy in DEFAULT_STRATEGIES),
            EXPECTED_FAMILIES,
        )
        self.assertEqual(len(DEFAULT_STRATEGIES), len(EXPECTED_FAMILIES))
        self.assertEqual(
            len({strategy.name for strategy in DEFAULT_STRATEGIES}),
            len(DEFAULT_STRATEGIES),
        )
        self.assertEqual(
            {strategy.primary_cadence for strategy in DEFAULT_STRATEGIES},
            {"15m"},
        )

    def test_each_strategy_family_has_a_matching_markdown_doc(self) -> None:
        self.assertTrue(
            STRATEGY_DOCS_ROOT.is_dir(),
            f"missing strategy docs directory: {STRATEGY_DOCS_ROOT}",
        )

        self.assertEqual(
            len(list(STRATEGY_DOCS_ROOT.glob("*.md"))),
            len(EXPECTED_STRATEGY_NAMES),
        )

        for strategy in DEFAULT_STRATEGIES:
            doc_path = STRATEGY_DOCS_ROOT / f"{strategy.name}.md"
            self.assertTrue(
                doc_path.is_file(),
                f"missing doc for strategy {strategy.name!r}: {doc_path}",
            )

            content = doc_path.read_text(encoding="utf-8").lower()
            self.assertIn("# ", content)
            self.assertIn("what it is", content)
            self.assertIn("how it works", content)
            self.assertIn("economic rationale", content)

    def test_multi_frequency_alignment_reindexes_features_to_primary_15m_cadence_without_lookahead(
        self,
    ) -> None:
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
                index=pd.to_datetime(
                    ["2026-01-01 00:00:00+00:00", "2026-01-01 01:00:00+00:00"]
                ),
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

        aligned = align_feature_frames(
            primary_index=primary_index,
            feature_frames=feature_frames,
        )

        expected_funding = pd.DataFrame(
            {"BTCUSDT": [0.0010, 0.0010, 0.0010, 0.0020]},
            index=primary_index,
        )
        expected_micro = pd.DataFrame(
            {"BTCUSDT": [10.0, 20.0, 30.0, 50.0]},
            index=primary_index,
        )

        assert_frame_equal(aligned["funding_rate_1h"], expected_funding)
        assert_frame_equal(aligned["micro_trend_5m"], expected_micro)

        aligned_again = align_feature_frames(
            primary_index=primary_index,
            feature_frames=feature_frames,
        )
        assert_frame_equal(aligned_again["funding_rate_1h"], expected_funding)
        assert_frame_equal(aligned_again["micro_trend_5m"], expected_micro)


if __name__ == "__main__":
    unittest.main()
