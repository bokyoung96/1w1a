import json

from .bid_ask_list import BidAskList
from .protocol import TRName
from .register import TRClient

if __package__ in (None, ""):
    raise SystemExit("Run from repo root: python -m tr_id.call")


def main() -> None:
    symbol = "005930"

    with TRClient() as client:
        response = client.call(TRName.BID_ASK_LIST, symbol)

    if response.rt_cd != "0":
        print(f"error: {response.msg_cd} {response.msg1}")
        return

    print(json.dumps(BidAskList.summary(response), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
