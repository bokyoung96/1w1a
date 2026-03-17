from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class DataStore:
    data_dir: Path = Path(__file__).resolve().parent / "DATA"

    FILES = {
        "mifq2": "MIFQ2.parquet",
        "mifq3": "MIFQ3.parquet",
        "eifq1": "EIFQ1.parquet",
        "eifq2": "EIFQ2.parquet",
        "price": "Price.parquet",
        "inst_trade": "InstTrade.parquet",
        "indiv_trade": "IndivTrade.parquet",
        "foreign_trade": "ForeignTrade.parquet",
        "pension_trade": "PensionTrade.parquet",
        "trade": "Trade.parquet",
    }

    def __post_init__(self) -> None:
        self.data_dir = Path(self.data_dir)
        self._cache: dict[str, pd.DataFrame] = {}

    def _read(self, key: str) -> pd.DataFrame:
        if key in self._cache:
            return self._cache[key]

        filename = self.FILES[key]
        path = self.data_dir / filename
        if not path.exists():
            available = sorted(p.name for p in self.data_dir.glob("*.parquet"))
            raise FileNotFoundError(
                f"Missing parquet: {path}. Available: {available}"
            )
        df = pd.read_parquet(path)
        self._cache[key] = df
        return df

    @property
    def mifq2(self) -> pd.DataFrame:
        return self._read("mifq2")

    @property
    def mifq3(self) -> pd.DataFrame:
        return self._read("mifq3")

    @property
    def eifq1(self) -> pd.DataFrame:
        return self._read("eifq1")

    @property
    def eifq2(self) -> pd.DataFrame:
        return self._read("eifq2")

    @property
    def price(self) -> pd.DataFrame:
        return self._read("price")

    @property
    def inst_trade(self) -> pd.DataFrame:
        return self._read("inst_trade")

    @property
    def indiv_trade(self) -> pd.DataFrame:
        return self._read("indiv_trade")

    @property
    def foreign_trade(self) -> pd.DataFrame:
        return self._read("foreign_trade")

    @property
    def pension_trade(self) -> pd.DataFrame:
        return self._read("pension_trade")

    @property
    def trade(self) -> pd.DataFrame:
        return self._read("trade")

    @property
    def all(self) -> dict[str, pd.DataFrame]:
        return {k: self._read(k) for k in self.FILES}


@dataclass
class StratStore:
    data_dir: Path = Path(__file__).resolve().parent / "DATA" / "strat"

    FILES = {
        "leader_tag": "leader_tag.parquet",
        "leader_counts": "leader_counts.parquet",
        "leader_score": "leader_score.parquet",
        "lead_strength": "lead_strength.parquet",
        "lag_strength": "lag_strength.parquet",
        "net_lead_score": "net_lead_score.parquet",
        "candidate": "candidate.parquet",
        "corr_surface": "corr_surface.parquet",
        "adv20": "adv20.parquet",
        "flow_raw": "flow_raw.parquet",
        "flow_scaled": "flow_scaled.parquet",
        "ret_1d": "ret_1d.parquet",
    }

    def __post_init__(self) -> None:
        self.data_dir = Path(self.data_dir)
        self._cache: dict[str, pd.DataFrame] = {}

    def _read(self, key: str) -> pd.DataFrame:
        if key in self._cache:
            return self._cache[key]

        filename = self.FILES[key]
        path = self.data_dir / filename
        if not path.exists():
            available = sorted(p.name for p in self.data_dir.glob("*.parquet"))
            raise FileNotFoundError(f"Missing parquet: {path}. Available: {available}")
        df = pd.read_parquet(path)
        self._cache[key] = df
        return df

    @property
    def leader_tag(self) -> pd.DataFrame:
        return self._read("leader_tag")

    @property
    def leader_counts(self) -> pd.DataFrame:
        return self._read("leader_counts")

    @property
    def leader_score(self) -> pd.DataFrame:
        return self._read("leader_score")

    @property
    def lead_strength(self) -> pd.DataFrame:
        return self._read("lead_strength")

    @property
    def lag_strength(self) -> pd.DataFrame:
        return self._read("lag_strength")

    @property
    def net_lead_score(self) -> pd.DataFrame:
        return self._read("net_lead_score")

    @property
    def candidate(self) -> pd.DataFrame:
        return self._read("candidate")

    @property
    def corr_surface(self) -> pd.DataFrame:
        return self._read("corr_surface")

    @property
    def adv20(self) -> pd.DataFrame:
        return self._read("adv20")

    @property
    def flow_raw(self) -> pd.DataFrame:
        return self._read("flow_raw")

    @property
    def flow_scaled(self) -> pd.DataFrame:
        return self._read("flow_scaled")

    @property
    def ret_1d(self) -> pd.DataFrame:
        return self._read("ret_1d")

    @property
    def leader_by_ticker(self) -> dict[str, pd.Series]:
        tag = self.leader_tag
        return {str(ticker): tag[ticker] for ticker in tag.columns}

    @property
    def all(self) -> dict[str, pd.DataFrame]:
        return {k: self._read(k) for k in self.FILES}


if __name__ == "__main__":
    ds = DataStore()
    st = StratStore()
