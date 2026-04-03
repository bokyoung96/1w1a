import pandas as pd

from backtesting.validation import SplitConfig, split_frame


def test_split_frame_returns_is_and_oos_slices() -> None:
    frame = pd.DataFrame(
        {"signal": [1, 2, 3, 4, 5]},
        index=pd.to_datetime(
            [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ]
        ),
    )
    config = SplitConfig(
        is_start=pd.Timestamp("2024-01-02"),
        is_end=pd.Timestamp("2024-01-03"),
        oos_start=pd.Timestamp("2024-01-04"),
        oos_end=pd.Timestamp("2024-01-05"),
    )

    result = split_frame(frame, config)

    assert list(result.is_frame.index) == list(pd.to_datetime(["2024-01-02", "2024-01-03"]))
    assert list(result.oos_frame.index) == list(pd.to_datetime(["2024-01-04", "2024-01-05"]))
