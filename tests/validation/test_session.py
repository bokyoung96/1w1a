import pandas as pd

from backtesting.validation import ValidationSession


def test_validation_session_flags_expected_warnings() -> None:
    signal = pd.DataFrame(
        {
            "a": [1.0, None, None],
            "b": [None, None, 4.0],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
    )
    benchmark = pd.Series(
        [1.0],
        index=pd.to_datetime(["2024-01-01"]),
    )

    session = ValidationSession()
    warnings = session.run(
        signal,
        lag_sensitive_datasets=["alpha", "beta"],
        lag_map={"alpha": 1},
        benchmark=benchmark,
        sparse_threshold=0.75,
        stale_gap_datasets=["alpha", "gamma"],
    )

    assert "missing_lag:beta" in warnings
    assert "duplicate_index" in warnings
    assert "short_benchmark" in warnings
    assert "sparse_signal" in warnings
    assert "stale_gap:alpha" in warnings
    assert "stale_gap:gamma" in warnings
