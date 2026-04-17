from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import pandas as pd

from crypto.validation import PromotionMetrics, PromotionThresholds, ValidationReport, evaluate_promotion_readiness


class PromotionStage(str, Enum):
    RESEARCH = "research"
    OOS_VALIDATED = "oos_validated"
    PAPER_TRADING = "paper_trading"
    PROMOTED = "promoted"
    REJECTED = "rejected"


_ALLOWED_TRANSITIONS: dict[PromotionStage, tuple[PromotionStage, ...]] = {
    PromotionStage.RESEARCH: (PromotionStage.OOS_VALIDATED, PromotionStage.REJECTED),
    PromotionStage.OOS_VALIDATED: (PromotionStage.PAPER_TRADING, PromotionStage.REJECTED),
    PromotionStage.PAPER_TRADING: (PromotionStage.PROMOTED, PromotionStage.REJECTED),
    PromotionStage.PROMOTED: (),
    PromotionStage.REJECTED: (),
}


@dataclass(frozen=True, slots=True)
class IdeaAuditRecord:
    idea_id: str
    thesis: str
    rationale: str
    prompt_reference: str
    input_references: tuple[str, ...]
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PromotionEvent:
    from_stage: PromotionStage
    to_stage: PromotionStage
    at: pd.Timestamp


@dataclass(slots=True)
class PromotionCandidate:
    strategy_id: str
    family: str
    exchange: str
    symbol: str
    primary_cadence: str
    audit: IdeaAuditRecord
    stage: PromotionStage = PromotionStage.RESEARCH
    history: list[PromotionEvent] = field(default_factory=list)
    validation: ValidationReport | None = None

    def transition_to(self, to_stage: PromotionStage, at: pd.Timestamp) -> None:
        allowed = _ALLOWED_TRANSITIONS[self.stage]
        if to_stage not in allowed:
            raise ValueError(
                f"invalid promotion transition: {self.stage.value} -> {to_stage.value}"
            )
        self.history.append(PromotionEvent(from_stage=self.stage, to_stage=to_stage, at=at))
        self.stage = to_stage

    def attach_validation(
        self,
        metrics: PromotionMetrics,
        thresholds: PromotionThresholds,
    ) -> ValidationReport:
        self.validation = evaluate_promotion_readiness(metrics=metrics, thresholds=thresholds)
        return self.validation
