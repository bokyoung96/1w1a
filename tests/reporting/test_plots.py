from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from backtesting.reporting.models import SavedRun
from backtesting.reporting.plots import PlotLibrary


def test_plot_library_writes_equity_plot(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )

    path = PlotLibrary(tmp_path).equity([run])

    assert path.exists()
    assert path.suffix == ".png"


def test_plot_library_writes_all_expected_plots(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-02-01"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0, 108.0], index=index),
        returns=pd.Series([0.0, 0.1, -0.01818181818181818], index=index),
        turnover=pd.Series([0.0, 0.05, 0.02], index=index),
        weights=pd.DataFrame({"A": [1.0, 0.0, 0.5], "B": [0.0, -0.25, 0.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 0.0, 5.0], "B": [0.0, -5.0, 0.0]}, index=index),
        monthly_returns=pd.Series([0.05, -0.02], index=pd.to_datetime(["2024-01-31", "2024-02-29"])),
    )

    plotter = PlotLibrary(tmp_path)

    for path in (
        plotter.drawdown([run]),
        plotter.turnover([run]),
        plotter.top_weights([run]),
        plotter.monthly_heatmap([run]),
    ):
        assert path.exists()
        assert path.suffix == ".png"


def test_plot_library_writes_html_fallback_when_image_export_fails(tmp_path: Path, monkeypatch) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )

    def fail_write_image(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("no image export")

    monkeypatch.setattr(go.Figure, "write_image", fail_write_image)

    path = PlotLibrary(tmp_path).equity([run])

    assert path.exists()
    assert path.suffix == ".png"
    assert path.with_suffix(".html").exists()
