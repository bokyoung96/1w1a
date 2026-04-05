from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from live_dashboard.backend.api import router


def create_app(
    *,
    default_selected_run_ids: list[str],
    frontend_dist: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="1w1a Live Dashboard")
    app.state.default_selected_run_ids = list(default_selected_run_ids)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    if frontend_dist is not None:
        frontend_dist = frontend_dist.resolve()
        index_path = frontend_dist / "index.html"
        if not index_path.is_file():
            raise FileNotFoundError(f"missing frontend entrypoint: {index_path}")

        @app.get("/", include_in_schema=False)
        def serve_root() -> FileResponse:
            return FileResponse(index_path)

        @app.get("/{path_name:path}", include_in_schema=False)
        def serve_frontend(path_name: str) -> FileResponse:
            if path_name.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            asset_path = (frontend_dist / path_name).resolve(strict=False)
            try:
                asset_path.relative_to(frontend_dist)
            except ValueError as exc:
                raise HTTPException(status_code=404, detail="Not Found") from exc
            if path_name and asset_path.is_file():
                return FileResponse(asset_path)
            return FileResponse(index_path)

    return app


app = create_app(default_selected_run_ids=[])
