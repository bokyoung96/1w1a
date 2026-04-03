from dataclasses import dataclass

from .enums import DatasetId


@dataclass(frozen=True, slots=True)
class DatasetSpec:
    id: DatasetId
    stem: str
    freq: str
    kind: str
    fill: str
    validity: str
    lag: int
    dtype: str
    axis: str = "date_symbol"
