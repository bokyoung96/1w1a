import pandas as pd


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"])
    normalized = normalized.sort_values("date")

    if normalized["date"].duplicated().any():
        raise ValueError("duplicate date values in raw dataset")

    return normalized.set_index("date")
