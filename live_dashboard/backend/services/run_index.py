from __future__ import annotations

import json
from pathlib import Path

from live_dashboard.backend.schemas import RunOptionModel, RunSummaryModel
from root import ROOT


class RunIndexService:
    def __init__(self, runs_root: Path | None = None) -> None:
        self.runs_root = runs_root or (ROOT.results_path / "backtests")

    def list_runs(self) -> list[RunOptionModel]:
        runs: list[RunOptionModel] = []
        if not self.runs_root.exists():
            return runs

        for run_dir in sorted(self.runs_root.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue

            config_path = run_dir / "config.json"
            summary_path = run_dir / "summary.json"
            if not config_path.exists() or not summary_path.exists():
                continue

            config = json.loads(config_path.read_text(encoding="utf-8"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            runs.append(
                RunOptionModel(
                    run_id=run_dir.name,
                    label=str(config.get("name") or run_dir.name),
                    strategy=str(config.get("strategy") or "unknown"),
                    start=config.get("start"),
                    end=config.get("end"),
                    summary=RunSummaryModel(
                        final_equity=float(summary.get("final_equity") or 0.0),
                        avg_turnover=float(summary.get("avg_turnover") or 0.0),
                    ),
                )
            )

        return runs
