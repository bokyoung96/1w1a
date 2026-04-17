import pandas as pd
import pytest

from crypto.promotion import IdeaAuditRecord, PromotionCandidate, PromotionStage
from crypto.validation import DEFAULT_PROMOTION_THRESHOLDS, PromotionMetrics


def _build_candidate() -> PromotionCandidate:
    return PromotionCandidate(
        strategy_id="btc-breakout-v1",
        family="trend-following breakout",
        exchange="binance_perpetual",
        symbol="BTCUSDT",
        primary_cadence="15m",
        audit=IdeaAuditRecord(
            idea_id="idea-001",
            thesis="15m breakout entries strengthened by higher-timeframe trend alignment",
            rationale="Use the approved launch cohort while keeping multi-frequency inputs at the feature layer.",
            prompt_reference="prompt://research/idea-001",
            input_references=("dataset://bars/15m", "dataset://funding/1h"),
            tags=("breakout", "multi-frequency"),
        ),
    )


def test_promotion_candidate_rejects_invalid_stage_jump() -> None:
    candidate = _build_candidate()

    with pytest.raises(ValueError, match="invalid promotion transition"):
        candidate.transition_to(PromotionStage.PAPER_TRADING, at=pd.Timestamp("2026-02-01", tz="UTC"))


def test_promotion_candidate_records_an_explicit_evidence_trail() -> None:
    candidate = _build_candidate()
    metrics = PromotionMetrics(
        oos_sharpe=0.91,
        paper_sharpe=0.61,
        max_drawdown=0.11,
        paper_days=45,
        pairwise_correlation=0.42,
    )

    candidate.transition_to(PromotionStage.OOS_VALIDATED, at=pd.Timestamp("2026-02-01", tz="UTC"))
    candidate.attach_validation(metrics=metrics, thresholds=DEFAULT_PROMOTION_THRESHOLDS)
    candidate.transition_to(PromotionStage.PAPER_TRADING, at=pd.Timestamp("2026-03-15", tz="UTC"))
    candidate.transition_to(PromotionStage.PROMOTED, at=pd.Timestamp("2026-04-17", tz="UTC"))

    assert candidate.stage is PromotionStage.PROMOTED
    assert [event.to_stage for event in candidate.history] == [
        PromotionStage.OOS_VALIDATED,
        PromotionStage.PAPER_TRADING,
        PromotionStage.PROMOTED,
    ]
    assert candidate.validation is not None
    assert candidate.validation.ready is True
    assert candidate.audit.prompt_reference == "prompt://research/idea-001"
    assert candidate.audit.input_references == ("dataset://bars/15m", "dataset://funding/1h")
    assert candidate.validation.metrics.paper_days == 45
