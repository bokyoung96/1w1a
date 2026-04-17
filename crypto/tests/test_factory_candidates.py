from __future__ import annotations

import unittest

from crypto.factory import StrategyCandidate, build_candidate_pool
from crypto.strategies import DEFAULT_STRATEGIES


class CandidateFactoryTests(unittest.TestCase):
    def test_build_candidate_pool_hits_requested_target_and_covers_each_registered_strategy(self) -> None:
        candidates = build_candidate_pool(
            strategy_definitions=DEFAULT_STRATEGIES,
            target_size=36,
            random_seed=7,
        )

        self.assertEqual(len(candidates), 36)
        self.assertTrue(30 <= len(candidates) <= 50)
        self.assertTrue(all(isinstance(candidate, StrategyCandidate) for candidate in candidates))

        expected_strategy_names = {strategy.name for strategy in DEFAULT_STRATEGIES}
        self.assertEqual(
            {candidate.strategy_name for candidate in candidates},
            expected_strategy_names,
        )
        self.assertEqual(
            {candidate.family for candidate in candidates},
            {strategy.family for strategy in DEFAULT_STRATEGIES},
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
            [self._signature(candidate) for candidate in first],
            [self._signature(candidate) for candidate in second],
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
