from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from dashboard.backend.api import router


def get_frontend_dist_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(title="1W1A Dashboard")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    dist_dir = get_frontend_dist_dir()
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="dashboard-assets")

    @app.get("/{path:path}", include_in_schema=False)
    def serve_frontend(path: str) -> FileResponse:
        if path.startswith("api"):
            raise HTTPException(status_code=404, detail="not found")

        if not dist_dir.exists():
            raise HTTPException(status_code=503, detail="dashboard frontend is not built")

        if path:
            candidate = dist_dir / path
            if candidate.exists() and candidate.is_file():
                return FileResponse(candidate)

        index_path = dist_dir / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=503, detail="dashboard frontend is not built")

        return FileResponse(index_path)

    return app


app = create_app()
