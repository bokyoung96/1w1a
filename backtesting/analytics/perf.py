from __future__ import annotations

from math import sqrt

import pandas as pd


def summarize_perf(returns: pd.Series) -> dict[str, float]:
    ret = returns.dropna()
    if ret.empty:
        return {"cagr": 0.0, "mdd": 0.0, "sharpe": 0.0}

    eq = (1.0 + ret).cumprod()
    growth = float(eq.iloc[-1])
    years = len(ret) / 252.0
    cagr = 0.0 if growth == 1.0 else (growth ** (1.0 / years) - 1.0 if growth > 0 else -1.0)

    peak = eq.cummax()
    dd = eq.div(peak).sub(1.0)
    mdd = float(dd.min())

    std = float(ret.std(ddof=0))
    sharpe = 0.0 if abs(std) < 1e-12 else float(ret.mean() / std * sqrt(252.0))

    return {"cagr": float(cagr), "mdd": mdd, "sharpe": sharpe}
