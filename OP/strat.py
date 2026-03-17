from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OP_DIR = Path(__file__).resolve().parent
if str(OP_DIR) not in sys.path:
    sys.path.insert(0, str(OP_DIR))

from loader import DataStore, StratStore


FLOW_KEYS = ("inst", "foreign", "indiv", "pension")


@dataclass
class StratConfig:
    adv_window: int = 20
    scale_window: int = 252
    eps: float = 1e-6
    adv_min: float = 0.0
    window: int = 126
    max_lag: int = 10
    candidate_quantile: float = 0.70
    nls_floor: float | None = None
    output_dir: Path = Path(__file__).resolve().parent / "DATA" / "strat"
    save_intermediate: bool = True


@dataclass
class StratResult:
    tag_time: pd.DataFrame
    tag_counts: pd.DataFrame
    leader_score: pd.DataFrame
    lead_strength: Dict[str, pd.DataFrame]
    lag_strength: Dict[str, pd.DataFrame]
    net_lead_score: Dict[str, pd.DataFrame]
    candidate: Dict[str, pd.DataFrame]
    corr_map: Dict[str, pd.DataFrame]
    adv20: pd.DataFrame
    flow_raw: Dict[str, pd.DataFrame]
    flow_scaled: Dict[str, pd.DataFrame]
    ret_1d: pd.DataFrame


@dataclass
class Strat:
    store: DataStore = field(default_factory=DataStore)
    cfg: StratConfig = field(default_factory=StratConfig)

    def _frame(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out.index = pd.to_datetime(out.index, errors="coerce")
        out = out.loc[out.index.notna()].sort_index()
        out.columns = pd.Index(out.columns).astype(str)
        out = out.loc[:, ~out.columns.duplicated()]
        return out

    def _common_panel(self) -> dict[str, pd.DataFrame]:
        frames = {
            "price": self._frame(self.store.price),
            "trade": self._frame(self.store.trade),
            "inst": self._frame(self.store.inst_trade),
            "foreign": self._frame(self.store.foreign_trade),
            "indiv": self._frame(self.store.indiv_trade),
            "pension": self._frame(self.store.pension_trade),
        }
        idx = frames["price"].index
        cols = frames["price"].columns
        for key in ("trade", "inst", "foreign", "indiv", "pension"):
            idx = idx.intersection(frames[key].index)
            cols = cols.intersection(frames[key].columns)
        for key in frames:
            frames[key] = frames[key].reindex(index=idx, columns=cols)
        return frames

    def _adv20(self, trade: pd.DataFrame) -> pd.DataFrame:
        value = trade.where(trade >= 0)
        return value.shift(1).rolling(self.cfg.adv_window, min_periods=self.cfg.adv_window).mean()

    def _scale(self, flow_raw: pd.DataFrame) -> pd.DataFrame:
        med = flow_raw.rolling(self.cfg.scale_window, min_periods=self.cfg.scale_window).median()
        mad = (flow_raw - med).abs().rolling(self.cfg.scale_window, min_periods=self.cfg.scale_window).median()
        return (flow_raw - med) / mad.clip(lower=self.cfg.eps)

    def _daily_return(self, price: pd.DataFrame) -> pd.DataFrame:
        safe_price = price.where(price > 0)
        ret = np.log(safe_price).diff()
        return ret.replace([np.inf, -np.inf], np.nan)

    def _rolling_corr_asof(self, x_df: pd.DataFrame, r_df: pd.DataFrame, lag: int) -> pd.DataFrame:
        # rho(lag) = corr(x_t, r_{t+lag}).
        # For lag>0, r_{t+lag} is only known at t+lag, so shift the estimate by +lag.
        y_df = r_df.shift(-int(lag))
        out = pd.DataFrame(index=x_df.index, columns=x_df.columns, dtype=float)
        w = int(self.cfg.window)
        for col in x_df.columns:
            out[col] = x_df[col].rolling(w, min_periods=w).corr(y_df[col])
        if lag > 0:
            out = out.shift(int(lag))
        return out

    def _build_corr_map(self, flow_scaled: Dict[str, pd.DataFrame], ret_1d: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        corr_map: Dict[str, pd.DataFrame] = {}
        for subject in FLOW_KEYS:
            for lag in range(-int(self.cfg.max_lag), int(self.cfg.max_lag) + 1):
                if lag == 0:
                    continue
                key = f"{subject}_lag{lag:+d}"
                corr_map[key] = self._rolling_corr_asof(flow_scaled[subject], ret_1d, lag)
        return corr_map

    @staticmethod
    def _signed_max(frames: list[pd.DataFrame]) -> pd.DataFrame:
        base = frames[0]
        stacked = np.stack([f.to_numpy(dtype=float) for f in frames], axis=0)
        masked = np.where(np.isnan(stacked), -np.inf, stacked)
        out = masked.max(axis=0)
        out[np.isneginf(out)] = np.nan
        return pd.DataFrame(out, index=base.index, columns=base.columns)

    def _subject_scores(
        self, corr_map: Dict[str, pd.DataFrame], subject: str
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        lead_frames = [corr_map[f"{subject}_lag{lag:+d}"] for lag in range(1, int(self.cfg.max_lag) + 1)]
        chase_frames = [corr_map[f"{subject}_lag{lag:+d}"] for lag in range(-int(self.cfg.max_lag), 0)]

        lead_strength = self._signed_max(lead_frames)
        lag_strength = self._signed_max(chase_frames)
        net_lead_score = lead_strength - lag_strength

        ls_threshold = lead_strength.quantile(float(self.cfg.candidate_quantile), axis=1)
        candidate = lead_strength.ge(ls_threshold, axis=0) & lead_strength.notna() & net_lead_score.notna()
        if self.cfg.nls_floor is not None:
            candidate = candidate & (net_lead_score.abs() >= float(self.cfg.nls_floor))
        return lead_strength, lag_strength, net_lead_score, candidate

    def _tag_time(
        self,
        net_lead_score: Dict[str, pd.DataFrame],
        candidate: Dict[str, pd.DataFrame],
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        order = ["foreign", "inst", "pension", "indiv"]
        arrays = [net_lead_score[k].where(candidate[k], -np.inf).to_numpy(dtype=float) for k in order]
        stacked = np.stack(arrays, axis=0)
        best_idx = np.argmax(stacked, axis=0)
        best_val = np.max(stacked, axis=0)
        has_leader = np.isfinite(best_val)

        tag_arr = np.full(best_idx.shape, "no-flow", dtype=object)
        for i, subject in enumerate(order):
            lead_mask = has_leader & (best_idx == i) & (best_val > 0.0)
            chase_mask = has_leader & (best_idx == i) & (best_val <= 0.0)
            tag_arr[lead_mask] = f"{subject}-lead"
            tag_arr[chase_mask] = f"{subject}-chase"

        base = net_lead_score[order[0]]
        tag = pd.DataFrame(tag_arr, index=base.index, columns=base.columns, dtype="string")
        leader_score = pd.DataFrame(best_val, index=base.index, columns=base.columns).where(has_leader)
        return tag, leader_score

    def _tag_counts(self, tag_time: pd.DataFrame) -> pd.DataFrame:
        counts = (
            tag_time.stack(future_stack=True)
            .rename("tag")
            .reset_index()
            .groupby(["date", "tag"])
            .size()
            .unstack("tag", fill_value=0)
            .sort_index()
        )
        counts.index = pd.DatetimeIndex(counts.index)
        return counts

    @staticmethod
    def _concat_subject_frames(frames: Dict[str, pd.DataFrame], prefix: str) -> pd.DataFrame:
        return pd.concat({f"{prefix}_{k}": v for k, v in frames.items()}, axis=1)

    @staticmethod
    def _concat_corr_frames(frames: Dict[str, pd.DataFrame], prefix: str) -> pd.DataFrame:
        return pd.concat({f"{prefix}_{k}": v for k, v in frames.items()}, axis=1)

    def _save_outputs(self, result: StratResult) -> None:
        out_dir = Path(self.cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        result.tag_time.to_parquet(out_dir / "leader_tag.parquet")
        result.tag_counts.to_parquet(out_dir / "leader_counts.parquet")
        result.leader_score.to_parquet(out_dir / "leader_score.parquet")
        self._concat_subject_frames(result.lead_strength, "lead_strength").to_parquet(out_dir / "lead_strength.parquet")
        self._concat_subject_frames(result.lag_strength, "lag_strength").to_parquet(out_dir / "lag_strength.parquet")
        self._concat_subject_frames(result.net_lead_score, "net_lead_score").to_parquet(out_dir / "net_lead_score.parquet")
        self._concat_subject_frames(result.candidate, "candidate").to_parquet(out_dir / "candidate.parquet")
        self._concat_corr_frames(result.corr_map, "corr").to_parquet(out_dir / "corr_surface.parquet")

        if not self.cfg.save_intermediate:
            return
        result.adv20.to_parquet(out_dir / "adv20.parquet")
        self._concat_subject_frames(result.flow_raw, "flow_raw").to_parquet(out_dir / "flow_raw.parquet")
        self._concat_subject_frames(result.flow_scaled, "flow_scaled").to_parquet(out_dir / "flow_scaled.parquet")
        result.ret_1d.to_parquet(out_dir / "ret_1d.parquet")

    def run(self, save: bool = True) -> StratResult:
        frames = self._common_panel()
        price = frames["price"]
        trade = frames["trade"]
        flow_src = {
            "inst": frames["inst"],
            "foreign": frames["foreign"],
            "indiv": frames["indiv"],
            "pension": frames["pension"],
        }

        adv20 = self._adv20(trade)
        denom = adv20.where(adv20 > float(self.cfg.adv_min))
        flow_raw = {k: v.div(denom) for k, v in flow_src.items()}
        flow_scaled = {k: self._scale(v) for k, v in flow_raw.items()}
        ret_1d = self._daily_return(price)

        corr_map = self._build_corr_map(flow_scaled=flow_scaled, ret_1d=ret_1d)

        lead_strength: Dict[str, pd.DataFrame] = {}
        lag_strength: Dict[str, pd.DataFrame] = {}
        net_lead_score: Dict[str, pd.DataFrame] = {}
        candidate: Dict[str, pd.DataFrame] = {}
        for subject in FLOW_KEYS:
            lead_j, lag_j, nls_j, cand_j = self._subject_scores(corr_map=corr_map, subject=subject)
            lead_strength[subject] = lead_j
            lag_strength[subject] = lag_j
            net_lead_score[subject] = nls_j
            candidate[subject] = cand_j

        tag_time, leader_score = self._tag_time(net_lead_score=net_lead_score, candidate=candidate)
        tag_counts = self._tag_counts(tag_time)

        result = StratResult(
            tag_time=tag_time,
            tag_counts=tag_counts,
            leader_score=leader_score,
            lead_strength=lead_strength,
            lag_strength=lag_strength,
            net_lead_score=net_lead_score,
            candidate=candidate,
            corr_map=corr_map,
            adv20=adv20,
            flow_raw=flow_raw,
            flow_scaled=flow_scaled,
            ret_1d=ret_1d,
        )
        if save:
            self._save_outputs(result)
        return result


@dataclass
class Plot:
    store: StratStore = field(default_factory=StratStore)
    output_dir: Path = Path(__file__).resolve().parent / "DATA" / "strat" / "plots"

    def _resolve_date(self, index: pd.DatetimeIndex, date: str | pd.Timestamp | None) -> pd.Timestamp:
        if date is None:
            return pd.Timestamp(index.max())
        target = pd.Timestamp(date)
        if target in index:
            return target
        pos = index.searchsorted(target, side="right") - 1
        if pos < 0:
            raise ValueError(f"No available date <= {target.date()}")
        return pd.Timestamp(index[pos])

    def snapshot_matrix(
        self,
        ticker: str,
        date: str | pd.Timestamp | None = None,
    ) -> tuple[pd.DataFrame, pd.Timestamp]:
        corr_surface = self.store.corr_surface
        ticker = str(ticker)
        tickers = corr_surface.columns.get_level_values(1)
        if ticker not in tickers:
            raise KeyError(f"{ticker} not found in corr_surface")

        corr_ticker = corr_surface.xs(ticker, level=1, axis=1)
        resolved_date = self._resolve_date(pd.DatetimeIndex(corr_ticker.index), date)

        pattern = re.compile(r"^corr_(?P<subject>inst|foreign|indiv|pension)_lag(?P<lag>[+-]?\d+)$")
        lags_set: set[int] = set()
        for col in corr_ticker.columns:
            match = pattern.match(str(col))
            if match is None:
                continue
            lag = int(match.group("lag"))
            if lag != 0:
                lags_set.add(lag)
        lags = sorted([lag for lag in lags_set if lag < 0]) + sorted([lag for lag in lags_set if lag > 0])
        matrix = pd.DataFrame(index=list(FLOW_KEYS), columns=lags, dtype=float)

        for col in corr_ticker.columns:
            col_name = str(col)
            match = pattern.match(col_name)
            if match is None:
                continue
            subject = match.group("subject")
            lag = int(match.group("lag"))
            if lag == 0 or lag not in matrix.columns:
                continue
            matrix.loc[subject, lag] = corr_ticker.loc[resolved_date, col_name]

        return matrix, resolved_date

    def plot_snapshot(
        self,
        ticker: str,
        date: str | pd.Timestamp | None = None,
        filename: str | None = None,
    ) -> Path:
        matrix, resolved_date = self.snapshot_matrix(ticker=ticker, date=date)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        values = matrix.to_numpy(dtype=float)
        finite = np.isfinite(values)
        vmax = float(np.nanmax(np.abs(values[finite]))) if finite.any() else 0.1
        vmax = max(vmax, 0.1)

        fig, ax = plt.subplots(figsize=(12, 3.4))
        im = ax.imshow(values, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)

        x_labels = [f"{lag:+d}" for lag in matrix.columns]
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels)
        ax.set_yticks(np.arange(len(matrix.index)))
        ax.set_yticklabels(matrix.index.tolist())
        ax.set_xlabel("Lag (corr(flow_t, ret_{t+lag}))")
        ax.set_ylabel("Subject")

        leader = self.store.leader_tag.loc[resolved_date, str(ticker)] if str(ticker) in self.store.leader_tag.columns else "n/a"
        score = self.store.leader_score.loc[resolved_date, str(ticker)] if str(ticker) in self.store.leader_score.columns else np.nan
        score_text = "nan" if pd.isna(score) else f"{float(score):.3f}"
        ax.set_title(f"{ticker} | {resolved_date.date()} | tag={leader} | score={score_text}")

        cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label("Rolling Corr")
        fig.tight_layout()

        if filename is None:
            filename = f"heatmap_{ticker}_{resolved_date:%Y%m%d}.png"
        out_path = self.output_dir / filename
        fig.savefig(out_path, dpi=160)
        plt.close(fig)
        return out_path


if __name__ == "__main__":
    strat = Strat()
    out = strat.run(save=True)
    print(out.tag_counts.tail(10).to_string())
    latest = pd.Timestamp(out.tag_time.index.max())
    tags_latest = out.tag_time.loc[latest]
    active = tags_latest[tags_latest != "no-flow"]
    sample_ticker = str(active.index[0]) if not active.empty else str(out.tag_time.columns[0])
    plotter = Plot()
    heatmap_path = plotter.plot_snapshot(ticker=sample_ticker, date=latest)
    print(f"heatmap saved: {heatmap_path}")
