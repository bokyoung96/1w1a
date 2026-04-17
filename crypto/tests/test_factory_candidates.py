from __future__ import annotations

import unittest

from crypto.strategies.registry import DEFAULT_STRATEGIES, StrategyDefinition

from crypto.factory import (
    MAX_CANDIDATE_POOL_SIZE,
    MIN_CANDIDATE_POOL_SIZE,
    CandidateParameterRange,
    CandidateProfile,
    build_fixed_grid_candidates,
    expand_candidates,
    generate_candidate_pool,
)


class FactoryCandidateGenerationTests(unittest.TestCase):
    def test_build_fixed_grid_candidates_emits_an_ordered_cross_product(self) -> None:
        profile = CandidateProfile(
            strategy=StrategyDefinition(name="test_breakout", family="test family"),
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

        candidates = build_fixed_grid_candidates(profile)

        self.assertEqual(len(candidates), 6)
        self.assertEqual(
            [candidate.params for candidate in candidates],
            [
                {"lookback_bars": 20, "breakout_buffer_bps": 5.0},
                {"lookback_bars": 20, "breakout_buffer_bps": 10.0},
                {"lookback_bars": 40, "breakout_buffer_bps": 5.0},
                {"lookback_bars": 40, "breakout_buffer_bps": 10.0},
                {"lookback_bars": 60, "breakout_buffer_bps": 5.0},
                {"lookback_bars": 60, "breakout_buffer_bps": 10.0},
            ],
        )
        self.assertTrue(all(candidate.generation_stage == "fixed_grid" for candidate in candidates))
        self.assertEqual(candidates[0].candidate_id, "test_breakout:breakout_buffer_bps=5:lookback_bars=20")
        self.assertEqual(candidates[-1].candidate_id, "test_breakout:breakout_buffer_bps=10:lookback_bars=60")

    def test_expand_candidates_is_deterministic_and_respects_bounds(self) -> None:
        profile = CandidateProfile(
            strategy=StrategyDefinition(name="test_breakout", family="test family"),
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
        seeds = build_fixed_grid_candidates(profile)

        expanded_once = expand_candidates(
            profile=profile,
            seed_candidates=seeds,
            target_count=5,
            random_seed=11,
        )
        expanded_again = expand_candidates(
            profile=profile,
            seed_candidates=seeds,
            target_count=5,
            random_seed=11,
        )

        self.assertEqual(expanded_once, expanded_again)
        self.assertEqual(len(expanded_once), 5)
        self.assertEqual(expanded_once[:3], seeds)
        self.assertTrue(all(candidate.candidate_id for candidate in expanded_once))
        self.assertTrue(
            all(candidate.generation_stage == "adaptive_random" for candidate in expanded_once[3:])
        )
        self.assertTrue(
            all(candidate.parent_candidate_id == seeds[1].candidate_id for candidate in expanded_once[3:])
        )
        for candidate in expanded_once[3:]:
            self.assertGreaterEqual(candidate.params["lookback_bars"], 10)
            self.assertLessEqual(candidate.params["lookback_bars"], 80)
            self.assertGreaterEqual(candidate.params["breakout_buffer_bps"], 2.5)
            self.assertLessEqual(candidate.params["breakout_buffer_bps"], 20.0)

    def test_generate_candidate_pool_clamps_pool_size_and_covers_registered_strategies(self) -> None:
        minimum_pool = generate_candidate_pool(target_count=12, random_seed=7)
        maximum_pool = generate_candidate_pool(target_count=99, random_seed=7)

        self.assertEqual(len(minimum_pool), MIN_CANDIDATE_POOL_SIZE)
        self.assertEqual(len(maximum_pool), MAX_CANDIDATE_POOL_SIZE)
        self.assertEqual(len({candidate.candidate_id for candidate in maximum_pool}), len(maximum_pool))
        self.assertEqual(
            {candidate.strategy_name for candidate in minimum_pool},
            {strategy.name for strategy in DEFAULT_STRATEGIES},
        )
        self.assertTrue(any(candidate.generation_stage == "fixed_grid" for candidate in minimum_pool))
        self.assertTrue(any(candidate.generation_stage == "adaptive_random" for candidate in maximum_pool))

        deterministic_again = generate_candidate_pool(target_count=99, random_seed=7)
        self.assertEqual(maximum_pool, deterministic_again)


if __name__ == "__main__":
    unittest.main()
