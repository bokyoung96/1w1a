from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Mapping, Protocol

import httpx


@unique
class TRName(str, Enum):
    BID_ASK_LIST = "bid_ask_list"


@dataclass(frozen=True)
class ResponseHeader:
    content_type: str | None
    tr_id: str | None
    tr_cont: str | None
    gt_uid: str | None


@dataclass(frozen=True)
class TRResponse:
    header: ResponseHeader
    rt_cd: str
    msg_cd: str
    msg1: str
    output1: Mapping[str, Any] | None
    output2: Mapping[str, Any] | None

    @classmethod
    def from_http(cls, response: httpx.Response) -> "TRResponse":
        data = response.json()
        header = ResponseHeader(
            content_type=response.headers.get("content-type"),
            tr_id=response.headers.get("tr_id"),
            tr_cont=response.headers.get("tr_cont"),
            gt_uid=response.headers.get("gt_uid"),
        )
        return cls(
            header=header,
            rt_cd=str(data.get("rt_cd", "")),
            msg_cd=str(data.get("msg_cd", "")),
            msg1=str(data.get("msg1", "")),
            output1=data.get("output1"),
            output2=data.get("output2"),
        )


class TRSpec(Protocol):
    name: TRName
    path: str

    def params(self, symbol: str) -> Mapping[str, str]:
        ...

    def parse(self, response: httpx.Response) -> TRResponse:
        ...
