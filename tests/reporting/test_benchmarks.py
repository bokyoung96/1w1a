import warnings

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository, _read_quantwise_benchmark_frame
from backtesting.reporting.models import BenchmarkConfig


def test_benchmark_repository_load_returns_uses_kospi200_price_path() -> None:
    index = pd.to_datetime(["2024-01-04", "2024-01-02", "2024-01-03"])
    frame = pd.DataFrame(
        {
            "IKS200": [102.0, 100.0, 101.0],
            "IKS001": [12.0, 10.0, 11.0],
        },
        index=index,
    )

    returns = BenchmarkRepository.from_frame(frame).load_returns(
        BenchmarkConfig.default_kospi200(),
        start="2024-01-02",
        end="2024-01-04",
    )

    expected_index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    expected = pd.Series(
        [0.0, (101.0 / 100.0) - 1.0, (102.0 / 101.0) - 1.0],
        index=expected_index,
        name="KOSPI200",
    )
    expected.index.name = "date"

    assert returns.name == "KOSPI200"
    assert list(returns.index) == list(expected_index)
    assert returns.iloc[-1] == expected.iloc[-1]
    assert_series_equal(returns, expected)


def test_sector_repository_latest_sector_weights_maps_latest_date() -> None:
    sector_index = pd.to_datetime(["2024-02-29", "2024-01-31"])
    sector_frame = pd.DataFrame(
        {
            "A": ["G20", "G10"],
            "B": ["G30", "G10"],
            "C": ["G40", "G15"],
        },
        index=sector_index,
    )
    weights = pd.DataFrame(
        {
            "A": [0.25],
            "B": [0.35],
            "C": [0.40],
        },
        index=pd.to_datetime(["2024-02-15"]),
    )

    exposure = SectorRepository.from_frame(sector_frame).latest_sector_weights(weights)

    expected = pd.Series({"G10": 0.6, "G15": 0.4})
    expected.index.name = None

    assert_series_equal(exposure, expected)


def test_sector_repository_exposes_latest_row_and_counts_without_internal_access() -> None:
    sector_frame = pd.DataFrame(
        {
            "A": ["Tech", "Energy"],
            "B": ["Utilities", "Utilities"],
            "C": ["Health Care", "Energy"],
        },
        index=pd.to_datetime(["2024-01-31", "2024-02-29"]),
    )
    weights = pd.DataFrame(
        {
            "A": [0.6],
            "B": [0.4],
            "C": [0.0],
        },
        index=pd.to_datetime(["2024-02-15"]),
    )
    repo = SectorRepository.from_frame(sector_frame)

    latest_row = repo.latest_sector_row(pd.Timestamp("2024-02-15"))
    latest_count = repo.latest_sector_counts(weights)

    expected_row = pd.Series({"A": "Tech", "B": "Utilities", "C": "Health Care"}, name=pd.Timestamp("2024-01-31"))
    expected_count = pd.Series({"Tech": 1.0, "Utilities": 1.0}, name="count")
    expected_count.index.name = "sector"

    assert_series_equal(latest_row, expected_row)
    assert_series_equal(latest_count.sort_index(), expected_count.sort_index())


def test_sector_contribution_timeseries_avoids_pct_change_future_warning() -> None:
    sector_frame = pd.DataFrame(
        {
            "A": ["Tech"],
            "B": ["Utilities"],
        },
        index=pd.to_datetime(["2024-01-02"]),
    )
    prices = pd.DataFrame(
        {
            "A": [100.0, None, 101.0],
            "B": [50.0, 50.5, 50.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    weights = pd.DataFrame(
        {
            "A": [0.6, 0.55, 0.5],
            "B": [0.4, 0.45, 0.5],
        },
        index=prices.index,
    )
    repo = SectorRepository.from_frame(sector_frame, prices=prices)

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        contributions = repo.sector_contribution_timeseries(weights, pd.Series(0.0, index=prices.index))

    assert not [warning for warning in recorded if issubclass(warning.category, FutureWarning)]
    assert contributions.loc[pd.Timestamp("2024-01-04"), "Tech"] == pytest.approx(0.0)
    assert_frame_equal(contributions.fillna(0.0), contributions.fillna(0.0).replace([float("inf"), float("-inf")], 0.0))


def test_sector_contribution_timeseries_disables_pct_change_forward_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    sector_frame = pd.DataFrame({"A": ["Tech"]}, index=pd.to_datetime(["2024-01-02"]))
    prices = pd.DataFrame({"A": [100.0, 101.0]}, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
    weights = pd.DataFrame({"A": [1.0, 1.0]}, index=prices.index)
    captured: dict[str, object] = {}
    original_pct_change = pd.DataFrame.pct_change

    def patched_pct_change(self: pd.DataFrame, *args: object, **kwargs: object):
        captured["fill_method"] = kwargs.get("fill_method", "__missing__")
        return original_pct_change(self, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "pct_change", patched_pct_change)

    SectorRepository.from_frame(sector_frame, prices=prices).sector_contribution_timeseries(
        weights,
        pd.Series(0.0, index=prices.index),
    )

    assert captured["fill_method"] is None


def test_read_quantwise_benchmark_frame_extracts_codes_and_dates(tmp_path) -> None:
    raw = pd.DataFrame(
        [
            ["Refresh", "Last Update", None],
            ["Code", "IKS200", "IKS001"],
            ["Name", "KOSPI200", "KOSPI"],
            ["Item Code", "I100100", "I100100"],
            ["Unit", "P", "P"],
            ["D A T E", "종가지수", "종가지수"],
            [pd.Timestamp("2024-01-02"), 100.0, 200.0],
            [pd.Timestamp("2024-01-03"), 101.0, 201.0],
        ]
    )
    path = tmp_path / "qw_BM.xlsx"
    raw.to_excel(path, index=False, header=False)

    frame = _read_quantwise_benchmark_frame(path)

    expected = pd.DataFrame(
        {
            "IKS200": [100.0, 101.0],
            "IKS001": [200.0, 201.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    expected.index.name = "date"

    assert_frame_equal(frame, expected, check_dtype=False)
