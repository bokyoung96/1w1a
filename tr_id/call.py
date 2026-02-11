import json

from .bid_ask_list import BidAskList
from .protocol import TRName
from .register import TRBatchClient
from tools import DataTools

if __package__ in (None, ""):
    raise SystemExit("Run from repo root: python -m tr_id.call")


def main() -> None:
    symbols = ["005930", "000660", "373220"]

    with TRBatchClient() as client:
        results, errors = client.call_batch(
            TRName.BID_ASK_LIST,
            symbols,
            concurrency=5,
            batch_size=50,
            retry=1,
            delay_sec=0.0,
        )

    if errors:
        print(json.dumps(errors, ensure_ascii=False, indent=2))

    summaries = {symbol: BidAskList.summary(resp) for symbol, resp in results.items()}
    df = DataTools.to_frame(summaries)
    print(df)


if __name__ == "__main__":
    main()
