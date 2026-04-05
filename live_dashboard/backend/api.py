from __future__ import annotations

from fastapi import APIRouter

from live_dashboard.backend.services.run_index import RunIndexService

router = APIRouter(prefix="/api")


@router.get("/runs")
def list_runs() -> list[dict[str, object]]:
    return [run.model_dump() for run in RunIndexService().list_runs()]
