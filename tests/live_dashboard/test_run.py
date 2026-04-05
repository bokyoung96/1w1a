from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from live_dashboard.run import build_frontend, launch_dashboard
from live_dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def test_launch_dashboard_reuses_matching_runs_and_executes_missing_presets(tmp_path: Path, monkeypatch) -> None:
    observed_configs = []
    captured_defaults = {}

    class FakeRunner:
        def run(self, config):
            observed_configs.append(config)
            return type("Report", (), {"output_dir": tmp_path / f"{config.strategy}_20260405_120000"})()

    monkeypatch.setattr("live_dashboard.run.build_frontend", lambda frontend_dir: None)
    monkeypatch.setattr("live_dashboard.run.DEFAULT_LAUNCH_CONFIG", DEFAULT_LAUNCH_CONFIG)
    monkeypatch.setattr("live_dashboard.run.BacktestRunner", lambda result_dir=None: FakeRunner())
    monkeypatch.setattr(
        "live_dashboard.run.create_app",
        lambda default_selected_run_ids, frontend_dist=None: captured_defaults.setdefault("run_ids", default_selected_run_ids) or object(),
    )
    monkeypatch.setattr("live_dashboard.run.uvicorn.run", lambda app, host, port: None)
    monkeypatch.setattr(
        "live_dashboard.run.LaunchResolutionService.resolve",
        lambda self, config: type(
            "Plan",
            (),
            {
                "resolved_runs": (type("ResolvedRun", (), {"run_id": "momentum_20260405_100000", "strategy_name": "momentum"})(),),
                "missing_presets": (config.strategies[1],),
                "selected_run_ids": ["momentum_20260405_100000"],
            },
        )(),
    )

    launch_dashboard(runs_root=tmp_path, host="127.0.0.1", port=8000)

    assert [config.strategy for config in observed_configs] == ["op_fwd_yield"]
    assert captured_defaults["run_ids"] == ["momentum_20260405_100000", "op_fwd_yield_20260405_120000"]


def test_build_frontend_runs_npm_install_and_build(tmp_path: Path, monkeypatch) -> None:
    observed_commands = []
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    package_lock = frontend_dir / "package-lock.json"
    node_modules = frontend_dir / "node_modules"
    package_lock.write_text('{"lockfileVersion":3}', encoding="utf-8")
    node_modules.mkdir()
    (node_modules / ".package-lock.json").write_text('{"lockfileVersion":3}', encoding="utf-8")

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> None:
        observed_commands.append((command, cwd, check))

    monkeypatch.setattr("live_dashboard.run.subprocess.run", fake_run)

    build_frontend(frontend_dir)

    assert observed_commands == [
        (["npm", "run", "build"], frontend_dir, True),
    ]


def test_build_frontend_installs_dependencies_when_node_modules_are_missing(tmp_path: Path, monkeypatch) -> None:
    observed_commands = []
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package.json").write_text('{"name":"dashboard"}', encoding="utf-8")
    (frontend_dir / "package-lock.json").write_text('{"lockfileVersion":3}', encoding="utf-8")

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> None:
        observed_commands.append((command, cwd, check))

    monkeypatch.setattr("live_dashboard.run.subprocess.run", fake_run)

    build_frontend(frontend_dir)

    assert observed_commands == [
        (["npm", "install"], frontend_dir, True),
        (["npm", "run", "build"], frontend_dir, True),
    ]


def test_build_frontend_reinstalls_when_lockfile_is_newer_than_install_marker(tmp_path: Path, monkeypatch) -> None:
    observed_commands = []
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    package_lock = frontend_dir / "package-lock.json"
    node_modules = frontend_dir / "node_modules"
    node_modules.mkdir()
    install_marker = node_modules / ".package-lock.json"
    install_marker.write_text('{"lockfileVersion":2}', encoding="utf-8")
    stale_time = time.time() - 60
    os.utime(install_marker, (stale_time, stale_time))
    package_lock.write_text('{"lockfileVersion":3}', encoding="utf-8")

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> None:
        observed_commands.append((command, cwd, check))

    monkeypatch.setattr("live_dashboard.run.subprocess.run", fake_run)

    build_frontend(frontend_dir)

    assert observed_commands == [
        (["npm", "install"], frontend_dir, True),
        (["npm", "run", "build"], frontend_dir, True),
    ]


def test_launch_dashboard_prints_help(capsys) -> None:
    from live_dashboard.run import build_parser

    parser = build_parser()

    parser.print_help()

    assert "Launch the live dashboard" in capsys.readouterr().out


def test_run_script_help_works_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = subprocess.run(
        [sys.executable, "live_dashboard/run.py", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Launch the live dashboard" in result.stdout
