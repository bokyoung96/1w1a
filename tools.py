from __future__ import annotations

from typing import Any, Mapping
import threading
import time
from datetime import datetime, timedelta, timezone

import pandas as pd


class DataTools:
    @staticmethod
    def to_frame(summaries: Mapping[str, Mapping[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(summaries, orient="index")
        df.index.name = "symbol"

        if "stck_shrn_iscd" in df.columns:
            df = df.drop(columns=["stck_shrn_iscd"])

        if not df.empty:
            for col in df.columns:
                numeric = pd.to_numeric(df[col], errors="coerce")
                if numeric.notna().any():
                    if (numeric.dropna() % 1 == 0).all():
                        df[col] = numeric.astype("Int64")
                    else:
                        df[col] = numeric

        return df


class RateLimiter:
    def __init__(self, max_per_sec: float) -> None:
        if max_per_sec <= 0:
            raise ValueError("max_per_sec must be positive")
        self._interval = 1.0 / max_per_sec
        self._lock = threading.Lock()
        self._next_time = time.monotonic()

    def wait(self) -> None:
        sleep_for = 0.0
        with self._lock:
            now = time.monotonic()
            if now < self._next_time:
                sleep_for = self._next_time - now
                self._next_time += self._interval
            else:
                self._next_time = now + self._interval
        if sleep_for > 0:
            time.sleep(sleep_for)


class TimeTools:
    KST = timezone(timedelta(hours=9))

    @staticmethod
    def now_kst() -> datetime:
        return datetime.now(TimeTools.KST)

    @staticmethod
    def kst_hhmmss() -> str:
        return TimeTools.now_kst().strftime("%H%M%S")

    @staticmethod
    def select_completed_futures_candle(candles: list[dict], current_time: str) -> dict | None:
        if not candles:
            return None
        if current_time.startswith("1545"):
            return candles[0]
        return candles[1] if len(candles) > 1 else candles[0]

    @staticmethod
    def adjust_futures_timestamp(candle_date: str, candle_time: str) -> datetime:
        timestamp_dt = datetime.strptime(f"{candle_date}{candle_time}", "%Y%m%d%H%M%S")
        if candle_time != "154500":
            timestamp_dt += timedelta(minutes=1)
        return timestamp_dt
