from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import ReportBundle, ReportSpec, SavedRun
from .plots import PlotLibrary
from .tables import build_appendix_table, build_latest_qty_table, build_latest_weights_table, build_summary_table

__all__ = ("ReportBuilder",)


class ReportBuilder:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)

    def build(self, spec: ReportSpec, runs: list[SavedRun]) -> ReportBundle:
        out_dir = self.root_dir / spec.name
        plots_dir = out_dir / "plots"
        tables_dir = out_dir / "tables"
        for path in (out_dir, plots_dir, tables_dir):
            path.mkdir(parents=True, exist_ok=True)

        plotter = PlotLibrary(plots_dir)
        plots = {
            "equity": plotter.equity(runs),
            "drawdown": plotter.drawdown(runs),
            "turnover": plotter.turnover(runs),
            "top_weights": plotter.top_weights(runs),
            "monthly_heatmap": plotter.monthly_heatmap(runs),
        }

        summary = build_summary_table(runs)
        appendix = build_appendix_table(runs)
        self._write_table(tables_dir / "summary.csv", summary)
        self._write_table(tables_dir / "appendix.csv", appendix)
        for run in runs:
            self._write_table(tables_dir / f"{run.run_id}_latest_weights.csv", build_latest_weights_table(run))
            self._write_table(tables_dir / f"{run.run_id}_latest_qty.csv", build_latest_qty_table(run))

        notes = self._build_notes(spec, runs)
        return ReportBundle(
            spec=spec,
            out_dir=out_dir,
            runs=tuple(runs),
            summary=summary,
            appendix=appendix,
            plots=plots,
            notes=notes,
        )

    @staticmethod
    def _write_table(path: Path, table: pd.DataFrame) -> None:
        table.to_csv(path, index=False)

    @staticmethod
    def _build_notes(spec: ReportSpec, runs: list[SavedRun]) -> tuple[str, ...]:
        notes: list[str] = []
        for run in runs:
            if spec.include_validation and run.validation is None:
                notes.append(f"missing_validation:{run.run_id}")
            if spec.include_is_oos and run.split is None:
                notes.append(f"missing_split:{run.run_id}")
            if spec.include_factor and run.factor is None:
                notes.append(f"missing_factor:{run.run_id}")
        return tuple(notes)
