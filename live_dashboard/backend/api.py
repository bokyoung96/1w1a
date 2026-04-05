from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from live_dashboard.backend.schemas import DashboardPayloadModel
from live_dashboard.backend.services.dashboard_payload import DashboardPayloadService
from live_dashboard.backend.services.run_index import RunIndexService

router = APIRouter(prefix="/api")


def get_run_index_service() -> RunIndexService:
    return RunIndexService()


def get_dashboard_payload_service() -> DashboardPayloadService:
    return DashboardPayloadService()


@router.get("/runs")
def list_runs() -> list[dict[str, object]]:
    return [run.model_dump() for run in get_run_index_service().list_runs()]


@router.get("/dashboard", response_model=DashboardPayloadModel)
def get_dashboard(
    run_ids: Annotated[list[str], Query(alias="run_ids")],
    service: DashboardPayloadService = Depends(get_dashboard_payload_service),
) -> dict[str, object]:
    return service.build(run_ids).model_dump(by_alias=True)
