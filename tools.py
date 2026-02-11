from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


class DataTools:
    @staticmethod
    def to_frame(summaries: Mapping[str, Mapping[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(summaries, orient="index")
        df.index.name = "symbol"

        if "stck_shrn_iscd" in df.columns:
            df = df.drop(columns=["stck_shrn_iscd"])

        if not df.empty:
            numeric_cols = [col for col in df.columns]
            numeric = df[numeric_cols].apply(lambda s: pd.to_numeric(s, errors="coerce"))
            df[numeric_cols] = numeric.astype("Int64")

        return df
