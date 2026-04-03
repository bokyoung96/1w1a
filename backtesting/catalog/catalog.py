from dataclasses import dataclass

from .enums import DatasetId
from .specs import DatasetSpec


@dataclass(slots=True)
class DataCatalog:
    specs: dict[DatasetId, DatasetSpec]

    @classmethod
    def default(cls) -> "DataCatalog":
        specs = {
            DatasetId.QW_ADJ_C: DatasetSpec(
                id=DatasetId.QW_ADJ_C,
                stem="qw_adj_c",
                freq="D",
                kind="price",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_ADJ_O: DatasetSpec(
                id=DatasetId.QW_ADJ_O,
                stem="qw_adj_o",
                freq="D",
                kind="price",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_ADJ_H: DatasetSpec(
                id=DatasetId.QW_ADJ_H,
                stem="qw_adj_h",
                freq="D",
                kind="price",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_ADJ_L: DatasetSpec(
                id=DatasetId.QW_ADJ_L,
                stem="qw_adj_l",
                freq="D",
                kind="price",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_V: DatasetSpec(
                id=DatasetId.QW_V,
                stem="qw_v",
                freq="D",
                kind="volume",
                fill="zero",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_MKTCAP: DatasetSpec(
                id=DatasetId.QW_MKTCAP,
                stem="qw_mktcap",
                freq="D",
                kind="market_cap",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
            DatasetId.QW_K200_YN: DatasetSpec(
                id=DatasetId.QW_K200_YN,
                stem="qw_k200_yn",
                freq="D",
                kind="flag",
                fill="zero",
                validity="daily",
                lag=0,
                dtype="int64",
            ),
        }
        return cls(specs=specs)

    def get(self, dataset_id: DatasetId) -> DatasetSpec:
        return self.specs[dataset_id]
