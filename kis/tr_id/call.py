import json
import logging

from .bid_ask_list import BidAskList
from .deriv_minute import DerivMinute
from .protocol import TRName
from .register import TRBatchClient
from kis.tools import DataTools
from kis.symbols import SymbolType, Symbols

if __package__ in (None, ""):
    raise SystemExit("Run from repo root: python -m kis.tr_id.call")


def main() -> None:
    symbols_k200 = Symbols.load(symbol_type=SymbolType.K200)
    symbols_k200f = Symbols.load(symbol_type=SymbolType.K200F)

    with TRBatchClient() as client:
        results_stock, errors_stock = client.call_batch(
            TRName.BID_ASK_LIST,
            symbols_k200,
            concurrency=5,
            batch_size=50,
            retry=2,
            delay_sec=0,
            rate_limit_per_sec=20.0,
        )

        results_futures, errors_futures = client.call_batch(
            TRName.DERIV_MINUTE,
            symbols_k200f,
            concurrency=5,
            batch_size=50,
            retry=2,
            delay_sec=0,
            rate_limit_per_sec=20.0,
        )

    if errors_stock:
        logging.warning("stock errors: %s", json.dumps(errors_stock, ensure_ascii=False))

    if errors_futures:
        logging.warning("futures errors: %s", json.dumps(errors_futures, ensure_ascii=False))

    stock_summaries = {symbol: BidAskList.summary(resp) for symbol, resp in results_stock.items()}
    futures_summaries = {symbol: DerivMinute.summary(resp) for symbol, resp in results_futures.items()}

    logging.info("stock dataframe:\n%s", DataTools.to_frame(stock_summaries))
    logging.info("futures dataframe:\n%s", DataTools.to_frame(futures_summaries))


if __name__ == "__main__":
    main()
