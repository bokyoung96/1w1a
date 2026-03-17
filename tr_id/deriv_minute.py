from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx

from tools import TimeTools
from tr_id.protocol import TRName, TRResponse


@dataclass(frozen=True)
class DerivMinuteSpec:
    name: TRName = TRName.DERIV_MINUTE
    path: str = "/uapi/domestic-futureoption/v1/quotations/inquire-time-fuopchartprice"

    def params(self, symbol: str) -> Mapping[str, str]:
        return {
            "fid_cond_mrkt_div_code": "F",
            "fid_input_iscd": symbol,
            "fid_hour_cls_code": "60",
            "fid_pw_data_incu_yn": "Y",
            "fid_fake_tick_incu_yn": "N",
            "fid_input_date_1": "",
            "fid_input_hour_1": TimeTools.kst_hhmmss(),
        }

    def parse(self, response: httpx.Response) -> TRResponse:
        return TRResponse.from_http(response)


class DerivMinute:
    @staticmethod
    def summary(response: TRResponse) -> dict[str, Any]:
        candles = response.output2 or []
        if not isinstance(candles, list) or not candles:
            return {}

        current_time = candles[0].get("stck_cntg_hour", "")
        candle = TimeTools.select_completed_futures_candle(candles, current_time)
        if not candle:
            return {}

        candle_date = candle.get("stck_bsop_date")
        candle_time = candle.get("stck_cntg_hour")
        if not candle_date or not candle_time:
            return {}

        timestamp = TimeTools.adjust_futures_timestamp(candle_date, candle_time)

        return {
            "timestamp": timestamp.isoformat(),
            "stck_bsop_date": candle_date,
            "stck_cntg_hour": candle_time,
            "futs_oprc": candle.get("futs_oprc"),
            "futs_hgpr": candle.get("futs_hgpr"),
            "futs_lwpr": candle.get("futs_lwpr"),
            "futs_prpr": candle.get("futs_prpr"),
            "cntg_vol": candle.get("cntg_vol"),
        }
