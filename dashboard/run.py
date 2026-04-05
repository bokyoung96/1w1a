from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import uvicorn


def run_subprocess(command: list[str], *, cwd: Path, check: bool) -> None:
    subprocess.run(command, cwd=cwd, check=check)


def build_frontend(frontend_dir: Path) -> None:
    if not (frontend_dir / "node_modules").exists():
        run_subprocess(["npm", "install"], cwd=frontend_dir, check=True)

    run_subprocess(["npm", "run", "build"], cwd=frontend_dir, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and serve the 1W1A dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    dashboard_dir = Path(__file__).resolve().parent
    repo_root = dashboard_dir.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    build_frontend(dashboard_dir / "frontend")

    from dashboard.backend.main import app

    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
