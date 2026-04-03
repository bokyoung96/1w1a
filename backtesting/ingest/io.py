from pathlib import Path

import pandas as pd


def find_raw_path(raw_dir: Path, stem: str) -> Path:
    for suffix in (".csv", ".xlsx"):
        path = raw_dir / f"{stem}{suffix}"
        if path.exists():
            return path
    raise FileNotFoundError(f"missing raw dataset: {stem}")


def read_raw_frame(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".xlsx":
        return pd.read_excel(path)
    raise ValueError(f"unsupported raw dataset format: {path.suffix}")
