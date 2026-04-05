from __future__ import annotations

from pathlib import Path

from dashboard.run import build_frontend


def test_build_frontend_installs_then_builds_when_node_modules_missing(tmp_path: Path, monkeypatch) -> None:
    commands: list[tuple[str, ...]] = []
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> None:
        assert cwd == frontend_dir
        assert check is True
        commands.append(tuple(command))

    monkeypatch.setattr("dashboard.run.run_subprocess", fake_run)

    build_frontend(frontend_dir)

    assert commands == [
        ("npm", "install"),
        ("npm", "run", "build"),
    ]


def test_build_frontend_only_builds_when_node_modules_exists(tmp_path: Path, monkeypatch) -> None:
    commands: list[tuple[str, ...]] = []
    frontend_dir = tmp_path / "frontend"
    (frontend_dir / "node_modules").mkdir(parents=True)

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> None:
        assert cwd == frontend_dir
        assert check is True
        commands.append(tuple(command))

    monkeypatch.setattr("dashboard.run.run_subprocess", fake_run)

    build_frontend(frontend_dir)

    assert commands == [
        ("npm", "run", "build"),
    ]
