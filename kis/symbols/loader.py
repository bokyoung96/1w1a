from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path

import pandas as pd

from root import ROOT


DEFAULT_PATH = ROOT.kis_path / "symbols" / "symbols.xlsx"


@unique
class SymbolType(str, Enum):
    K200 = "K200"
    K200F = "K200F"


class Symbols:
    @classmethod
    def load(
        cls,
        path: str | Path | None = None,
        *,
        symbol_type: SymbolType = SymbolType.K200,
    ) -> list[str]:
        target = Path(path) if path else DEFAULT_PATH
        if not target.exists():
            raise FileNotFoundError(f"symbols file not found: {target}")

        df = pd.read_excel(target, sheet_name=symbol_type.value, header=None, dtype=str)
        values = (
            df.stack(future_stack=True)
            .dropna()
            .astype(str)
            .map(str.strip)
            .tolist()
        )

        return [cls._normalize_symbol(value) for value in values if value]

    @staticmethod
    def _normalize_symbol(symbol: str, *, width: int = 6) -> str:
        if symbol.isdigit() and len(symbol) < width:
            return symbol.zfill(width)
        return symbol
