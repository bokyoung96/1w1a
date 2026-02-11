from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx

from tr_id.protocol import TRName, TRResponse


@dataclass(frozen=True)
class BidAskListSpec:
    name: TRName = TRName.BID_ASK_LIST
    path: str = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"

    def params(self, symbol: str) -> Mapping[str, str]:
        return {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
        }

    def parse(self, response: httpx.Response) -> TRResponse:
        return TRResponse.from_http(response)


class BidAskList:
    @staticmethod
    def summary(response: TRResponse) -> dict[str, Any]:
        output1 = response.output1 or {}
        output2 = response.output2 or {}
        return {
            "askp1": output1.get("askp1"),
            "askp2": output1.get("askp2"),
            "askp3": output1.get("askp3"),
            "askp4": output1.get("askp4"),
            "askp5": output1.get("askp5"),
            "bidp1": output1.get("bidp1"),
            "bidp2": output1.get("bidp2"),
            "bidp3": output1.get("bidp3"),
            "bidp4": output1.get("bidp4"),
            "bidp5": output1.get("bidp5"),
            "askp_rsqn1": output1.get("askp_rsqn1"),
            "askp_rsqn2": output1.get("askp_rsqn2"),
            "askp_rsqn3": output1.get("askp_rsqn3"),
            "askp_rsqn4": output1.get("askp_rsqn4"),
            "askp_rsqn5": output1.get("askp_rsqn5"),
            "bidp_rsqn1": output1.get("bidp_rsqn1"),
            "bidp_rsqn2": output1.get("bidp_rsqn2"),
            "bidp_rsqn3": output1.get("bidp_rsqn3"),
            "bidp_rsqn4": output1.get("bidp_rsqn4"),
            "bidp_rsqn5": output1.get("bidp_rsqn5"),
            "total_askp_rsqn": output1.get("total_askp_rsqn"),
            "total_bidp_rsqn": output1.get("total_bidp_rsqn"),
            "stck_prpr": output2.get("stck_prpr"),
            "stck_shrn_iscd": output2.get("stck_shrn_iscd"),
        }
