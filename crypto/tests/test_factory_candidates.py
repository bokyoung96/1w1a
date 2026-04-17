from __future__ import annotations

from dataclasses import dataclass
import unittest

from crypto.factory import (
    DEFAULT_CANDIDATE_PROFILES,
    MAX_CANDIDATE_POOL_SIZE,
    MIN_CANDIDATE_POOL_SIZE,
    CandidateParameterRange,
    CandidateProfile,
    build_fixed_grid_candidates,
    expand_candidates,
    generate_candidate_pool,
)


@dataclass(frozen=True)
class _StrategyStub:
    name: str
    family: str
    primary_cadence: str = "15m"
    feature_cadences: tuple[str, ...] = ("15m",)


class FactoryCandidateGenerationTests(unittest.TestCase):
    def test_build_fixed_grid_candidates_emits_an_ordered_cross_product(self) -> None:
        profile = CandidateProfile(
            strategy=_StrategyStub(name="test_breakout", family="test family"),
            parameters=(
                CandidateParameterRange(
                    name="lookback_bars",
                    seed_values=(20, 40, 60),
                    min_value=10,
                    max_value=80,
                    expansion_step=10,
                    integer=True,
                ),
                CandidateParameterRange(
                    name="breakout_buffer_bps",
                    seed_values=(5.0, 10.0),
                    min_value=2.5,
                    max_value=20.0,
                    expansion_step=2.5,
                ),
            ),
        )

        self.assertEqual(len(candidates), 36)
        self.assertTrue(30 <= len(candidates) <= 50)
        self.assertTrue(all(isinstance(candidate, StrategyCandidate) for candidate in candidates))

        expected_strategy_names = {strategy.name for strategy in DEFAULT_STRATEGIES}
        self.assertEqual(
            {candidate.strategy_name for candidate in candidates},
            expected_strategy_names,
        )
        self.assertTrue(all(candidate.generation_stage == "fixed_grid" for candidate in candidates))
        self.assertEqual(candidates[0].candidate_id, "test_breakout:breakout_buffer_bps=5:lookback_bars=20")
        self.assertEqual(candidates[-1].candidate_id, "test_breakout:breakout_buffer_bps=10:lookback_bars=60")

    def test_expand_candidates_is_deterministic_and_respects_bounds(self) -> None:
        profile = CandidateProfile(
            strategy=_StrategyStub(name="test_breakout", family="test family"),
            parameters=(
                CandidateParameterRange(
                    name="lookback_bars",
                    seed_values=(20, 40, 60),
                    min_value=10,
                    max_value=80,
                    expansion_step=10,
                    integer=True,
                ),
                CandidateParameterRange(
                    name="breakout_buffer_bps",
                    seed_values=(5.0,),
                    min_value=2.5,
                    max_value=20.0,
                    expansion_step=2.5,
                ),
            ),
            promising_seed_indices=(1,),
        )

        signatures = [self._signature(candidate) for candidate in candidates]
        self.assertEqual(len(signatures), len(set(signatures)))

        for candidate in candidates:
            self.assertIn(candidate.origin, {"grid", "adaptive_random"})
            self.assertTrue(candidate.parameters)
            for parameter_name, parameter_value in candidate.parameters.items():
                self.assertIsInstance(parameter_name, str)
                self.assertIsInstance(parameter_value, (int, float))

    def test_candidate_pool_is_seed_deterministic_while_random_expansion_changes_with_seed(self) -> None:
        first = build_candidate_pool(
            strategy_definitions=DEFAULT_STRATEGIES,
            target_size=36,
            random_seed=11,
        )
        second = build_candidate_pool(
            strategy_definitions=DEFAULT_STRATEGIES,
            target_size=36,
            random_seed=11,
        )
        different_seed = build_candidate_pool(
            strategy_definitions=DEFAULT_STRATEGIES,
            target_size=36,
            random_seed=19,
        )

        self.assertEqual(
            {candidate.strategy_name for candidate in minimum_pool},
            {profile.strategy.name for profile in DEFAULT_CANDIDATE_PROFILES},
        )

        grid_first = {
            self._signature(candidate)
            for candidate in first
            if candidate.origin == "grid"
        }
        grid_different_seed = {
            self._signature(candidate)
            for candidate in different_seed
            if candidate.origin == "grid"
        }
        adaptive_first = {
            self._signature(candidate)
            for candidate in first
            if candidate.origin == "adaptive_random"
        }
        adaptive_different_seed = {
            self._signature(candidate)
            for candidate in different_seed
            if candidate.origin == "adaptive_random"
        }

        self.assertTrue(grid_first)
        self.assertTrue(adaptive_first)
        self.assertEqual(grid_first, grid_different_seed)
        self.assertNotEqual(adaptive_first, adaptive_different_seed)

    def test_candidate_pool_validates_target_size_bounds(self) -> None:
        with self.assertRaisesRegex(ValueError, "target_size"):
            build_candidate_pool(
                strategy_definitions=DEFAULT_STRATEGIES,
                target_size=29,
                random_seed=7,
            )

        with self.assertRaisesRegex(ValueError, "target_size"):
            build_candidate_pool(
                strategy_definitions=DEFAULT_STRATEGIES,
                target_size=51,
                random_seed=7,
            )

    @staticmethod
    def _signature(candidate: StrategyCandidate) -> tuple[str, str, str, tuple[tuple[str, float], ...]]:
        return (
            candidate.strategy_name,
            candidate.family,
            candidate.origin,
            tuple(sorted((name, float(value)) for name, value in candidate.parameters.items())),
        )


if __name__ == "__main__":
    unittest.main()
