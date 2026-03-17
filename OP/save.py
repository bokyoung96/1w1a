from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

import pandas as pd


@dataclass
class Save:
    excel_path: Path
    output_dir: Path
    header_row: int = 7

    @staticmethod
    def _sheet_name(name: str) -> str:
        return (re.sub(r'[<>:"/\\|?*]', "_", str(name).strip()).rstrip(". ")) or "sheet"

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        cols = pd.Series(df.columns, dtype="object").map(
            lambda v: "" if pd.isna(v) else str(v).strip()
        )
        cols.iloc[0] = "date"
        cols = cols.str.replace(r"^(A\d{6})\.\d+$", r"\1", regex=True)
        out.columns = cols.tolist()
        return out

    @classmethod
    def _to_frame(cls, raw: pd.DataFrame) -> pd.DataFrame:
        out = cls._rename_columns(raw)
        out = out.loc[:, out.columns != ""]
        out = out.loc[:, ~out.columns.duplicated()]
        out["date"] = pd.to_datetime(out["date"], format="%Y-%m-%d", errors="coerce")
        out = out.dropna(subset=["date"])
        out = out.set_index("date").sort_index()
        out = out.apply(pd.to_numeric, errors="coerce")
        out.index.name = "date"
        out.columns.name = "ticker"
        return out

    def save(self) -> dict[str, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sheets = pd.read_excel(self.excel_path, sheet_name=None, header=self.header_row)
        saved: dict[str, Path] = {}
        for sheet_name, raw in sheets.items():
            out_path = self.output_dir / f"{self._sheet_name(sheet_name)}.parquet"
            self._to_frame(raw).to_parquet(out_path, index=True)
            saved[str(sheet_name)] = out_path
        return saved

def main() -> None:
    base = Path(__file__).resolve().parent
    saver = Save(
        excel_path=base / "DATA" / "DATA.xlsx",
        output_dir=base / "DATA",
    )
    saved = saver.save()
    for sheet, path in saved.items():
        print(f"{sheet} -> {path}")


if __name__ == "__main__":
    main()
