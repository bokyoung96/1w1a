from __future__ import annotations

from pydantic import BaseModel


class RunSummaryModel(BaseModel):
    final_equity: float
    avg_turnover: float


class RunOptionModel(BaseModel):
    run_id: str
    label: str
    strategy: str
    start: str | None = None
    end: str | None = None
    summary: RunSummaryModel
