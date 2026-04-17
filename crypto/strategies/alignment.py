from __future__ import annotations

import pandas as pd



def align_feature_frames(
    primary_index: pd.DatetimeIndex,
    feature_frames: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Align slower or faster feature frames onto the primary execution cadence.

    The alignment is backward-looking only: each primary timestamp receives the
    latest known feature observation at or before that timestamp.
    """

    if not primary_index.is_monotonic_increasing:
        raise ValueError("primary_index must be monotonic increasing")

    aligned: dict[str, pd.DataFrame] = {}
    for name, frame in feature_frames.items():
        if not frame.index.is_monotonic_increasing:
            frame = frame.sort_index()
        aligned[name] = frame.reindex(primary_index, method="ffill")
    return aligned
