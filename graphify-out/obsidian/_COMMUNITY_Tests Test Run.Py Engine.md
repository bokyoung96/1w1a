---
type: community
cohesion: 0.06
members: 98
---

# Tests Test Run.Py Engine

**Cohesion:** 0.06 - loosely connected
**Members:** 98 nodes

## Members
- [[BacktestEngine]] - code - backtesting/engine/core.py
- [[BacktestEngine._cap_buy_delta()]] - code - backtesting/engine/core.py
- [[BacktestEngine._normalize_quantity()]] - code - backtesting/engine/core.py
- [[BacktestEngine._rebalance()]] - code - backtesting/engine/core.py
- [[BacktestEngine._schedule()]] - code - backtesting/engine/core.py
- [[BacktestEngine._tradable()]] - code - backtesting/engine/core.py
- [[BacktestEngine.run()]] - code - backtesting/engine/core.py
- [[BacktestResult]] - code - backtesting/engine/result.py
- [[BacktestRunner]] - code - backtesting/run.py
- [[BacktestRunner.__init__()]] - code - backtesting/run.py
- [[BacktestRunner._ensure_parquet()]] - code - backtesting/run.py
- [[BacktestRunner._resolve_dataset_ids()]] - code - backtesting/run.py
- [[BacktestRunner._resolve_effective_config()]] - code - backtesting/run.py
- [[BacktestRunner._resolve_load_start()]] - code - backtesting/run.py
- [[BacktestRunner._resolve_universe_spec()]] - code - backtesting/run.py
- [[BacktestRunner._trim_plan_to_display_range()]] - code - backtesting/run.py
- [[BacktestRunner._trim_result_to_display_range()]] - code - backtesting/run.py
- [[BacktestRunner._universe()]] - code - backtesting/run.py
- [[BacktestRunner.run()]] - code - backtesting/run.py
- [[CostModel]] - code - backtesting/execution/costs.py
- [[CostModel.calc()]] - code - backtesting/execution/costs.py
- [[DataLoader]] - code - backtesting/data/loader.py
- [[DataLoader._load_frame()]] - code - backtesting/data/loader.py
- [[DataLoader.load()]] - code - backtesting/data/loader.py
- [[IngestJob.run()]] - code - backtesting/ingest/pipeline.py
- [[LoadRequest]] - code - backtesting/data/loader.py
- [[ParquetStore]] - code - backtesting/data/store.py
- [[ParquetStore.__init__()]] - code - backtesting/data/store.py
- [[ParquetStore.write()]] - code - backtesting/data/store.py
- [[PositionPlan]] - code - backtesting/policy/base.py
- [[RunConfig]] - code - backtesting/run.py
- [[RunReport]] - code - backtesting/run.py
- [[StrategyStub]] - code - tests/test_run.py
- [[StrategyStub.build_plan()]] - code - tests/test_run.py
- [[StrategyStub.build_weights()]] - code - tests/test_run.py
- [[StubRunner]] - code - tests/test_run.py
- [[StubRunner.__init__()]] - code - tests/test_run.py
- [[StubRunner.run()]] - code - tests/test_run.py
- [[ValidationSession]] - code - backtesting/validation/session.py
- [[ValidationSession._covers_index()]] - code - backtesting/validation/session.py
- [[ValidationSession._has_sparse_row()]] - code - backtesting/validation/session.py
- [[ValidationSession._unique_sorted()]] - code - backtesting/validation/session.py
- [[ValidationSession.run()]] - code - backtesting/validation/session.py
- [[_build_report()]] - code - tests/reporting/test_reader.py
- [[_build_report()_1]] - code - tests/test_report_cli.py
- [[_fail_if_engine_runs()]] - code - tests/test_run.py
- [[_stub_plot_generation()_1]] - code - tests/test_run.py
- [[_write_placeholder_plot()_1]] - code - tests/test_run.py
- [[costs.py]] - code - backtesting/execution/costs.py
- [[main()_1]] - code - backtesting/run.py
- [[normalize.py]] - code - backtesting/ingest/normalize.py
- [[normalize_frame()]] - code - backtesting/ingest/normalize.py
- [[read_raw_frame()]] - code - backtesting/ingest/io.py
- [[result.py]] - code - backtesting/engine/result.py
- [[run.py_2]] - code - run.py
- [[test_core.py]] - code - tests/engine/test_core.py
- [[test_cost_model_applies_fee_tax_and_slippage()]] - code - tests/execution/test_costs.py
- [[test_cost_model_does_not_apply_sell_tax_on_buy()]] - code - tests/execution/test_costs.py
- [[test_cost_model_rejects_invalid_side()]] - code - tests/execution/test_costs.py
- [[test_costs.py]] - code - tests/execution/test_costs.py
- [[test_engine_close_mode_works_without_open()]] - code - tests/engine/test_core.py
- [[test_engine_rebalances_only_on_scheduled_close_bars()]] - code - tests/engine/test_core.py
- [[test_engine_requires_open_for_next_open_mode()]] - code - tests/engine/test_core.py
- [[test_engine_respects_tradable_mask()]] - code - tests/engine/test_core.py
- [[test_engine_rounds_target_quantity_when_fractional_disabled()]] - code - tests/engine/test_core.py
- [[test_engine_scales_buy_quantity_to_keep_costs_from_overspending()]] - code - tests/engine/test_core.py
- [[test_engine_tracks_equity_from_weights()]] - code - tests/engine/test_core.py
- [[test_engine_uses_next_open_fill_prices()]] - code - tests/engine/test_core.py
- [[test_engine_uses_prior_schedule_flag_for_next_open_rebalances()]] - code - tests/engine/test_core.py
- [[test_loader_expands_month_only_data_without_crossing_missing_months()]] - code - tests/data/test_loader.py
- [[test_loader_rejects_duplicate_semantic_frame_keys()]] - code - tests/data/test_loader.py
- [[test_loader_rejects_unsupported_price_mode()]] - code - tests/data/test_loader.py
- [[test_loader_returns_market_data()]] - code - tests/data/test_loader.py
- [[test_loader_uses_semantic_key_for_kosdaq_close_data()]] - code - tests/data/test_loader.py
- [[test_loader_uses_semantic_key_for_op_fwd_data()]] - code - tests/data/test_loader.py
- [[test_loader_uses_semantic_key_for_volume_data()]] - code - tests/data/test_loader.py
- [[test_report_cli_builds_report_bundle()]] - code - tests/test_report_cli.py
- [[test_root_run_delegates_to_backtesting_main()]] - code - tests/test_run.py
- [[test_run.py_1]] - code - tests/test_run.py
- [[test_run_parser_accepts_universe_argument()]] - code - tests/test_run.py
- [[test_run_reader_round_trips_writer_bundle_layout()]] - code - tests/reporting/test_reader.py
- [[test_runner_executes_breakout_52w_simple_strategy()]] - code - tests/test_run.py
- [[test_runner_executes_breakout_52w_staged_strategy_and_persists_bucket_ledger()]] - code - tests/test_run.py
- [[test_runner_executes_momentum_strategy()]] - code - tests/test_run.py
- [[test_runner_executes_op_fwd_strategy()]] - code - tests/test_run.py
- [[test_runner_executes_strategy_plan_and_stores_position_plan()]] - code - tests/test_run.py
- [[test_runner_persists_implicit_legacy_universe_as_none()]] - code - tests/test_run.py
- [[test_runner_raises_clear_error_when_trimmed_display_range_is_empty()]] - code - tests/test_run.py
- [[test_runner_rejects_invalid_position_plan_before_engine_execution()]] - code - tests/test_run.py
- [[test_runner_uses_kosdaq_default_next_open_path()]] - code - tests/test_run.py
- [[test_runner_uses_kosdaq_market_cap_remap_for_op_fwd_strategy()]] - code - tests/test_run.py
- [[test_runner_uses_kosdaq_universe_specific_datasets()]] - code - tests/test_run.py
- [[test_runner_uses_warmup_history_but_trims_persisted_outputs()]] - code - tests/test_run.py
- [[test_session.py]] - code - tests/validation/test_session.py
- [[test_validation_session_flags_expected_warnings()]] - code - tests/validation/test_session.py
- [[test_validation_session_marks_empty_signal_sparse()]] - code - tests/validation/test_session.py
- [[test_validation_session_marks_zero_column_frames_sparse()]] - code - tests/validation/test_session.py
- [[test_validation_session_returns_stable_unique_warnings()]] - code - tests/validation/test_session.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Test_Run.Py_Engine
SORT file.name ASC
```

## Connections to other communities
- 106 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 70 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 25 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 19 edges to [[_COMMUNITY_Backtesting Reporting Frontend]]
- 14 edges to [[_COMMUNITY_Backtesting Strategies Tests]]
- 14 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 13 edges to [[_COMMUNITY_Tests Reporting Analytics]]
- 13 edges to [[_COMMUNITY_Docs Superpowers Strategy]]
- 12 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Portfolio]]
- 1 edge to [[_COMMUNITY_Tests Reporting Test_Builder]]

## Top bridge nodes
- [[DataLoader.load()]] - degree 35, connects to 8 communities
- [[ParquetStore.write()]] - degree 40, connects to 7 communities
- [[main()_1]] - degree 26, connects to 6 communities
- [[CostModel.calc()]] - degree 20, connects to 6 communities
- [[BacktestEngine.run()]] - degree 53, connects to 5 communities