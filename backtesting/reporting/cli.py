from __future__ import annotations

import argparse
import json
from pathlib import Path

from root import ROOT

from .builder import ReportBuilder
from .html import HtmlRenderer
from .models import ReportSpec
from .pdf import PdfRenderer
from .reader import RunReader

__all__ = ("ReportCli", "main")


class ReportCli:
    def __init__(self, *, runs_root: Path | None = None, reports_root: Path | None = None) -> None:
        self.runs_root = Path(runs_root) if runs_root is not None else ROOT.results_path / "backtests"
        self.reports_root = Path(reports_root) if reports_root is not None else ROOT.results_path / "reports"
        self.reader = RunReader()
        self.builder = ReportBuilder(self.reports_root)
        self.html = HtmlRenderer()
        self.pdf = PdfRenderer()

    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Build backtest reports from saved runs.")
        parser.add_argument("--runs", nargs="+", required=True)
        parser.add_argument("--name", required=True)
        parser.add_argument("--title")
        return parser

    def run(self, argv: list[str] | None = None) -> dict[str, object]:
        args = self.parser().parse_args(argv)
        runs = [self.reader.read(self.runs_root / run_id) for run_id in args.runs]
        spec = ReportSpec(name=args.name, run_ids=tuple(args.runs), title=args.title)
        bundle = self.builder.build(spec, runs)
        html_path = self.html.render(bundle)
        pdf_path, pdf_status = self.pdf.render_with_status(html_path)

        payload: dict[str, object] = {
            "report_name": spec.name,
            "run_ids": list(spec.run_ids),
            "output_dir": str(bundle.out_dir),
            "html_path": str(html_path),
            "pdf_path": None if pdf_path is None else str(pdf_path),
        }
        payload.update(pdf_status)
        report_json = bundle.out_dir / "report.json"
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload


def main(argv: list[str] | None = None) -> None:
    payload = ReportCli().run(argv)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
