import pandas as pd

from crypto.validation import (
    DEFAULT_PROMOTION_THRESHOLDS,
    PromotionMetrics,
    evaluate_promotion_readiness,
    pairwise_correlation_diagnostics,
)


def test_threshold_validation_uses_the_approved_launch_thresholds() -> None:
    passing = PromotionMetrics(
        oos_sharpe=0.80,
        paper_sharpe=0.55,
        max_drawdown=0.10,
        paper_days=31,
        pairwise_correlation=0.69,
    )
    failing = PromotionMetrics(
        oos_sharpe=0.74,
        paper_sharpe=0.49,
        max_drawdown=0.16,
        paper_days=29,
        pairwise_correlation=0.70,
    )

    ready_report = evaluate_promotion_readiness(passing, DEFAULT_PROMOTION_THRESHOLDS)
    blocked_report = evaluate_promotion_readiness(failing, DEFAULT_PROMOTION_THRESHOLDS)

    assert ready_report.ready is True
    assert ready_report.failed_checks == {}

    assert blocked_report.ready is False
    assert blocked_report.failed_checks == {
        "oos_sharpe": "must be > 0.75",
        "paper_sharpe": "must be > 0.5",
        "max_drawdown": "must be < 0.15",
        "paper_days": "must be >= 30",
        "pairwise_correlation": "must be < 0.70",
    }


def test_pairwise_overlap_diagnostics_are_deterministic_for_the_strategy_cohort() -> None:
    returns = pd.DataFrame(
        {
            "trend-following breakout": [0.01, 0.02, 0.03, 0.04, 0.05],
            "mean reversion": [-0.01, -0.02, -0.01, 0.00, 0.01],
            "perp momentum / relative-strength rotation": [0.011, 0.021, 0.031, 0.039, 0.049],
        },
        index=pd.date_range("2026-01-01", periods=5, freq="D", tz="UTC"),
    )

    diagnostics = pairwise_correlation_diagnostics(returns, threshold=0.70)

    assert diagnostics.max_pairwise_correlation > 0.99
    assert diagnostics.violating_pairs == [
        (
            "perp momentum / relative-strength rotation",
            "trend-following breakout",
            diagnostics.correlation_matrix.loc[
                "perp momentum / relative-strength rotation",
                "trend-following breakout",
            ],
        )
    ]
    assert diagnostics.correlation_matrix.loc[
        "trend-following breakout",
        "mean reversion",
    ] < 0.0
