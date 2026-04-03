from dataclasses import dataclass

import pandas as pd
from tqdm.auto import tqdm

from backtesting.engine.result import BacktestResult
from backtesting.execution.costs import CostModel
from backtesting.execution.fill import fill_prices


@dataclass(slots=True)
class BacktestEngine:
    cost: CostModel

    def run(
        self,
        close: pd.DataFrame,
        weights: pd.DataFrame,
        capital: float,
        open: pd.DataFrame | None = None,
        tradable: pd.DataFrame | None = None,
        fill_mode: str = "next_open",
        allow_fractional: bool = True,
        show_progress: bool = False,
    ) -> BacktestResult:
        close = close.astype(float)
        weights = weights.reindex_like(close).fillna(0.0).astype(float)
        tradable = self._tradable(tradable=tradable, close=close)

        equity = pd.Series(0.0, index=close.index, dtype=float)
        qty = pd.DataFrame(0.0, index=close.index, columns=close.columns, dtype=float)
        turnover = pd.Series(0.0, index=close.index, dtype=float)

        cash = float(capital)
        current_qty = pd.Series(0.0, index=close.columns, dtype=float)
        dates = close.index

        if fill_mode == "next_open":
            open_ = None if open is None else open.reindex_like(close).astype(float)
            exec_prices = fill_prices(close=close, open_=open_, fill_mode="next_open")
            equity.iloc[0] = capital
            qty.iloc[0] = current_qty

            for ts in tqdm(dates[1:], desc="backtest", disable=not show_progress):
                prev_ts = dates[dates.get_loc(ts) - 1]
                cash, current_qty, turn = self._rebalance(
                    cash=cash,
                    current_qty=current_qty,
                    fill_price=exec_prices.loc[prev_ts],
                    target_weight=weights.loc[prev_ts],
                    tradable=tradable.loc[ts],
                    allow_fractional=allow_fractional,
                )
                equity.loc[ts] = cash + current_qty.mul(close.loc[ts]).sum()
                qty.loc[ts] = current_qty
                turnover.loc[ts] = turn
        elif fill_mode == "close":
            first_ts = dates[0]
            cash, current_qty, turn = self._rebalance(
                cash=cash,
                current_qty=current_qty,
                fill_price=close.loc[first_ts],
                target_weight=weights.loc[first_ts],
                tradable=tradable.loc[first_ts],
                allow_fractional=allow_fractional,
            )
            equity.loc[first_ts] = cash + current_qty.mul(close.loc[first_ts]).sum()
            qty.loc[first_ts] = current_qty
            turnover.loc[first_ts] = turn

            for ts in tqdm(dates[1:], desc="backtest", disable=not show_progress):
                cash, current_qty, turn = self._rebalance(
                    cash=cash,
                    current_qty=current_qty,
                    fill_price=close.loc[ts],
                    target_weight=weights.loc[ts],
                    tradable=tradable.loc[ts],
                    allow_fractional=allow_fractional,
                )
                equity.loc[ts] = cash + current_qty.mul(close.loc[ts]).sum()
                qty.loc[ts] = current_qty
                turnover.loc[ts] = turn
        else:
            fill_prices(close=close, open_=open, fill_mode=fill_mode)

        returns = equity.pct_change().fillna(0.0)
        return BacktestResult(
            equity=equity,
            returns=returns,
            weights=weights,
            qty=qty,
            turnover=turnover,
        )

    def _rebalance(
        self,
        cash: float,
        current_qty: pd.Series,
        fill_price: pd.Series,
        target_weight: pd.Series,
        tradable: pd.Series,
        allow_fractional: bool,
    ) -> tuple[float, pd.Series, float]:
        tradable = tradable.reindex(fill_price.index).fillna(False).astype(bool)
        safe_price = fill_price.where(fill_price.ne(0.0))
        can_trade = tradable & safe_price.notna()
        nav = cash + current_qty.mul(fill_price.fillna(0.0)).sum()

        target_qty = target_weight.mul(nav).div(safe_price).fillna(0.0)
        target_qty = target_qty.where(can_trade, current_qty)
        if not allow_fractional:
            target_qty = target_qty.fillna(0.0).round(0)

        delta = target_qty.sub(current_qty).fillna(0.0)
        trade_value = delta.mul(fill_price.fillna(0.0)).abs()

        next_cash = cash
        for symbol, qty_delta in delta.items():
            if qty_delta == 0.0:
                continue

            price = float(fill_price.loc[symbol])
            side = "buy" if qty_delta > 0 else "sell"
            gross = abs(price * float(qty_delta))
            trade_cost = self.cost.calc(price=price, qty=float(qty_delta), side=side)
            if side == "buy":
                next_cash -= gross + trade_cost.total
            else:
                next_cash += gross - trade_cost.total

        turn = 0.0 if nav == 0.0 else float(trade_value.sum() / nav)
        return next_cash, target_qty.astype(float), turn

    @staticmethod
    def _tradable(tradable: pd.DataFrame | None, close: pd.DataFrame) -> pd.DataFrame:
        if tradable is None:
            return pd.DataFrame(True, index=close.index, columns=close.columns)
        return tradable.reindex_like(close).fillna(False).astype(bool)
