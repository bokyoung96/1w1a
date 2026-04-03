from pathlib import Path

import pandas as pd

from backtesting.reporting.models import BenchmarkConfig, ComparisonBundle, ReportKind, ReportSpec, TearsheetBundle


def test_report_spec_defaults_to_tearsheet_for_single_run() -> None:
    spec = ReportSpec(name="single", run_ids=("run-a",))
    assert spec.kind is ReportKind.TEARSHEET
    assert spec.benchmark.code == "IKS200"
    assert spec.benchmark.name == "KOSPI200"


def test_report_spec_defaults_to_comparison_for_multiple_runs() -> None:
    spec = ReportSpec(name="compare", run_ids=("run-a", "run-b"))
    assert spec.kind is ReportKind.COMPARISON


def test_bundles_expose_display_metadata(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(name="single", run_ids=("run-a",)),
        out_dir=tmp_path,
        run_id="run-a",
        display_name="Momentum",
        pages={"executive": tmp_path / "executive.png"},
        tables={"summary": pd.DataFrame([{"metric": "CAGR", "value": 0.1}])},
        notes=(),
    )
    assert bundle.display_name == "Momentum"
    assert "executive" in bundle.pages
