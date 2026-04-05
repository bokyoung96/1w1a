from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from dashboard.backend.schemas import RunOptionModel
from dashboard.backend.services.run_index import RunIndexService
from dashboard.strategies import DashboardLaunchConfig, StrategyPreset, enabled_strategy_presets


@dataclass(frozen=True, slots=True)
class ResolvedRun:
    run_id: str
    strategy_name: str


@dataclass(frozen=True, slots=True)
class LaunchPlan:
    resolved_runs: tuple[ResolvedRun, ...]
    missing_presets: tuple[StrategyPreset, ...]

    @property
    def selected_run_ids(self) -> list[str]:
        return [resolved_run.run_id for resolved_run in self.resolved_runs]


class LaunchResolutionService:
    def __init__(self, runs_root: Path | None = None) -> None:
        self.runs_root = runs_root

    def resolve(self, config: DashboardLaunchConfig) -> LaunchPlan:
        run_index_service = RunIndexService(self.runs_root)
        # Own newest-first matching here so resolution does not depend on index ordering.
        available_runs = sorted(
            run_index_service.list_runs(),
            key=self._run_sort_key,
            reverse=True,
        )
        resolved_runs: list[ResolvedRun] = []
        missing_presets: list[StrategyPreset] = []

        for preset in enabled_strategy_presets(config.strategies):
            desired_signature = self._build_signature(config, preset)
            matched_run = self._find_matching_run(available_runs, desired_signature, run_index_service.runs_root)
            if matched_run is None:
                missing_presets.append(preset)
                continue

            resolved_runs.append(ResolvedRun(run_id=matched_run.run_id, strategy_name=preset.strategy_name))

        return LaunchPlan(resolved_runs=tuple(resolved_runs), missing_presets=tuple(missing_presets))

    def _find_matching_run(
        self,
        available_runs: Sequence[RunOptionModel],
        desired_signature: dict[str, Any],
        runs_root: Path,
    ) -> RunOptionModel | None:
        for run in available_runs:
            config = self._load_saved_config(runs_root, run.run_id)
            if config is None:
                continue
            if self._build_saved_signature(config, desired_signature) == desired_signature:
                return run
        return None

    def _load_saved_config(self, runs_root: Path, run_id: str) -> dict[str, Any] | None:
        config_path = runs_root / run_id / "config.json"
        try:
            raw_config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return None

        if not isinstance(raw_config, dict):
            return None
        return raw_config

    @staticmethod
    def _build_signature(config: DashboardLaunchConfig, preset: StrategyPreset) -> dict[str, Any]:
        signature = asdict(config.global_config)
        signature["strategy"] = preset.strategy_name
        signature.update(dict(preset.params))
        return LaunchResolutionService._normalize_value(signature)

    @staticmethod
    def _build_saved_signature(saved_config: dict[str, Any], desired_signature: dict[str, Any]) -> dict[str, Any]:
        return LaunchResolutionService._normalize_value(
            {
                key: saved_config.get(key)
                for key in desired_signature
            }
        )

    @staticmethod
    def _run_sort_key(run: RunOptionModel) -> tuple[datetime, str]:
        timestamp = LaunchResolutionService._parse_run_timestamp(run.run_id)
        return timestamp, run.run_id

    @staticmethod
    def _parse_run_timestamp(run_id: str) -> datetime:
        parts = run_id.rsplit("_", 2)
        if len(parts) != 3:
            return datetime.min

        suffix = "_".join(parts[-2:])
        try:
            return datetime.strptime(suffix, "%Y%m%d_%H%M%S")
        except ValueError:
            return datetime.min

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: LaunchResolutionService._normalize_value(value[key]) for key in sorted(value)}
        if isinstance(value, list):
            return [LaunchResolutionService._normalize_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple(LaunchResolutionService._normalize_value(item) for item in value)
        return value
