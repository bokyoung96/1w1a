import pandas as pd
from pandas.testing import assert_series_equal

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
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
