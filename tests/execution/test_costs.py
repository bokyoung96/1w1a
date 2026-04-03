from backtesting.execution.costs import CostModel, TradeCost


def test_cost_model_applies_fee_tax_and_slippage() -> None:
    model = CostModel(fee=0.001, sell_tax=0.002, slippage=0.001)
    cost = model.calc(price=100.0, qty=10.0, side="sell")

    assert isinstance(cost, TradeCost)
    assert round(cost.total, 4) == 4.0
