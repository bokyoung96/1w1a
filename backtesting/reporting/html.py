from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import ReportBundle, SavedRun

__all__ = ("HtmlRenderer",)


class HtmlRenderer:
    def __init__(self) -> None:
        self.template_dir = Path(__file__).resolve().parent / "templates"
        self.styles_path = Path(__file__).resolve().parent / "styles.css"
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(("html", "xml")),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, bundle: ReportBundle) -> Path:
        bundle.out_dir.mkdir(parents=True, exist_ok=True)
        self._write_stylesheet(bundle.out_dir)
        template = self.env.get_template("base.html.j2")
        html = template.render(
            bundle=bundle,
            stylesheet="styles.css",
            summary=self._table(bundle.summary),
            appendix=self._table(bundle.appendix),
            plots=self._plot_context(bundle.plots, bundle.out_dir),
            runs=[self._run_context(run) for run in bundle.runs],
            notes=list(bundle.notes),
        )
        path = bundle.out_dir / "report.html"
        path.write_text(html, encoding="utf-8")
        return path

    def _write_stylesheet(self, out_dir: Path) -> None:
        target = out_dir / "styles.css"
        if target.exists() and target.read_text(encoding="utf-8") == self.styles_path.read_text(encoding="utf-8"):
            return
        shutil.copyfile(self.styles_path, target)

    @staticmethod
    def _table(frame: pd.DataFrame) -> dict[str, Any]:
        if frame.empty:
            return {"columns": [], "rows": []}
        display = frame.copy()
        display = display.where(pd.notna(display), "")
        return {
            "columns": list(display.columns),
            "rows": display.to_dict(orient="records"),
        }

    @staticmethod
    def _run_context(run: SavedRun) -> dict[str, Any]:
        return {
            "run_id": run.run_id,
            "strategy": str(run.config.get("strategy", "")),
            "latest_weights": HtmlRenderer._table(run.latest_weights if run.latest_weights is not None else _latest_frame(run.weights, "target_weight")),
            "latest_qty": HtmlRenderer._table(run.latest_qty if run.latest_qty is not None else _latest_frame(run.qty, "qty")),
        }

    @staticmethod
    def _plot_context(plots: dict[str, Path], out_dir: Path) -> dict[str, str]:
        return {name: os.path.relpath(path, out_dir).replace(os.sep, "/") for name, path in plots.items()}


def _latest_frame(frame: pd.DataFrame, value_column: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["symbol", value_column])
    latest_date = frame.index.max()
    latest = frame.loc[frame.index == latest_date].iloc[-1]
    table = pd.DataFrame({"symbol": latest.index, value_column: latest.values})
    table = table.loc[table[value_column].ne(0.0)].copy()
    return table.reset_index(drop=True)
