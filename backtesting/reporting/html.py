from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import ReportBundle, SavedRun
from .tables import build_latest_qty_table, build_latest_weights_table

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
            "latest_weights": HtmlRenderer._table(build_latest_weights_table(run)),
            "latest_qty": HtmlRenderer._table(build_latest_qty_table(run)),
        }

    @staticmethod
    def _plot_context(plots: dict[str, Path], out_dir: Path) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for name, path in plots.items():
            kind = path.suffix.lower().lstrip(".") or "file"
            items.append(
                {
                    "name": name,
                    "title": name.replace("_", " "),
                    "path": os.path.relpath(path, out_dir).replace(os.sep, "/"),
                    "kind": kind,
                }
            )
        return items
