from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from dashboard.backend.services.launch_resolution import LaunchResolutionService
from dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def test_resolution_reuses_newest_matching_run(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_090000", strategy="momentum")
    _write_matching_run(tmp_path, "momentum_20260405_100000", strategy="momentum")

    plan = LaunchResolutionService(tmp_path).resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]


def test_resolution_marks_all_presets_missing_when_global_config_changes(tmp_path: Path) -> None:
    _write_matching_default_runs(tmp_path)

    altered = replace(
        DEFAULT_LAUNCH_CONFIG,
        global_config=replace(DEFAULT_LAUNCH_CONFIG.global_config, fee=0.001),
    )

    plan = LaunchResolutionService(tmp_path).resolve(altered)

    assert plan.selected_run_ids == []
    assert [item.strategy_name for item in plan.missing_presets] == ["momentum", "op_fwd_yield"]


def test_resolution_executes_only_missing_strategy_when_partial_matches_exist(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_100000", strategy="momentum")

    plan = LaunchResolutionService(tmp_path).resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]


def test_resolution_marks_single_strategy_missing_when_strategy_params_change(tmp_path: Path) -> None:
    _write_matching_default_runs(tmp_path)
    updated_strategies = (
        DEFAULT_LAUNCH_CONFIG.strategies[0],
        replace(DEFAULT_LAUNCH_CONFIG.strategies[1], params={"top_n": 25}),
    )
    altered = replace(DEFAULT_LAUNCH_CONFIG, strategies=updated_strategies)

    plan = LaunchResolutionService(tmp_path).resolve(altered)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]


def test_resolution_ignores_malformed_saved_config(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_100000", strategy="momentum")
    _write_saved_run(
        tmp_path,
        "momentum_20260405_110000",
        config_text="{not valid json",
    )

    plan = LaunchResolutionService(tmp_path).resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]


def test_resolution_ignores_non_dict_saved_config(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_100000", strategy="momentum")
    _write_saved_run(
        tmp_path,
        "momentum_20260405_110000",
        config=[1, 2, 3],
    )

    plan = LaunchResolutionService(tmp_path).resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]


def _write_matching_default_runs(root: Path) -> None:
    _write_matching_run(root, "momentum_20260405_100000", strategy="momentum")
    _write_matching_run(root, "op_fwd_yield_20260405_110000", strategy="op_fwd_yield")


def _write_matching_run(root: Path, run_id: str, *, strategy: str) -> None:
    _write_saved_run(root, run_id, config=_saved_config(strategy))


def _write_saved_run(
    root: Path,
    run_id: str,
    *,
    config: object | None = None,
    config_text: str | None = None,
    summary: bool = True,
) -> None:
    run_dir = root / run_id
    run_dir.mkdir(parents=True)
    if summary:
        (run_dir / "summary.json").write_text(
            json.dumps({"final_equity": 100.0, "avg_turnover": 0.1}),
            encoding="utf-8",
        )

    if config_text is not None:
        (run_dir / "config.json").write_text(config_text, encoding="utf-8")
        return

    payload = _saved_config("momentum") if config is None else config
    (run_dir / "config.json").write_text(json.dumps(payload), encoding="utf-8")


def _saved_config(strategy: str) -> dict[str, object]:
    payload = asdict(DEFAULT_LAUNCH_CONFIG.global_config)
    payload["strategy"] = strategy

    preset = next(preset for preset in DEFAULT_LAUNCH_CONFIG.strategies if preset.strategy_name == strategy)
    payload.update(dict(preset.params))
    return payload
