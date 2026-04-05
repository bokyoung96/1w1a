# Live Dashboard Single-Command Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single-command live dashboard launcher that reuses matching saved runs, auto-executes missing or stale default strategies, and serves the built SPA plus API from one FastAPI process.

**Architecture:** A new launch-config module defines the desired global and per-strategy settings. A run-resolution service compares saved run configs against normalized desired signatures, selecting the newest matching run or triggering `BacktestRunner` when missing. The FastAPI app factory receives default selected run ids and serves both `/api/*` routes and the built frontend assets, while the React app hydrates from a bootstrap endpoint instead of assuming its own initial selection.

**Tech Stack:** Python 3.11, dataclasses, FastAPI, Uvicorn, existing `backtesting.run.BacktestRunner`, React, TypeScript, Vite, Vitest

---

## File Structure

- Create: `live_dashboard/strategies.py`
  Responsibility: Define global launch config, strategy presets, enabled preset filtering, and canonical conversion to `RunConfig` fields.
- Create: `live_dashboard/backend/services/launch_resolution.py`
  Responsibility: Normalize desired and saved configs, pick newest matching saved runs, and identify missing/stale presets that need execution.
- Modify: `live_dashboard/backend/schemas.py`
  Responsibility: Add bootstrap/session models for default selected run ids.
- Modify: `live_dashboard/backend/api.py`
  Responsibility: Expose a bootstrap endpoint and wire dependencies for launch defaults.
- Modify: `live_dashboard/backend/main.py`
  Responsibility: Convert global app singleton into `create_app(...)`, mount built frontend assets, and return the SPA entry point for non-API routes.
- Create: `live_dashboard/run.py`
  Responsibility: Build the frontend bundle, resolve or execute strategy runs, and start Uvicorn with the configured defaults.
- Modify: `live_dashboard/frontend/src/lib/api.ts`
  Responsibility: Fetch bootstrap state before dashboard hydration.
- Modify: `live_dashboard/frontend/src/lib/types.ts`
  Responsibility: Type the bootstrap payload.
- Modify: `live_dashboard/frontend/src/app/App.tsx`
  Responsibility: Hydrate initial run selection from the backend bootstrap payload rather than always defaulting to the first run.
- Modify: `live_dashboard/frontend/src/components/App.test.tsx`
  Responsibility: Cover bootstrap-driven initial hydration.
- Create: `tests/live_dashboard/test_strategies.py`
  Responsibility: Verify default launch config and enabled preset behavior.
- Create: `tests/live_dashboard/backend/test_launch_resolution.py`
  Responsibility: Verify config matching, newest-run reuse, partial reuse, and stale detection.
- Modify: `tests/live_dashboard/backend/test_dashboard_api.py`
  Responsibility: Verify bootstrap payload and app-factory default selection injection.
- Create: `tests/live_dashboard/test_run.py`
  Responsibility: Verify single-command launcher builds frontend, reuses matching runs, executes only missing/stale presets, and injects defaults into the app factory.
- Modify: `README.md`
  Responsibility: Document the single-command live dashboard run path and saved-run reuse rules.

### Task 1: Add Launch Config Surface

**Files:**
- Create: `live_dashboard/strategies.py`
- Test: `tests/live_dashboard/test_strategies.py`

- [ ] **Step 1: Write the failing default-config test**

```python
from live_dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def test_default_launch_config_enables_both_default_strategies() -> None:
    enabled = [preset.strategy_name for preset in DEFAULT_LAUNCH_CONFIG.strategies if preset.enabled]

    assert enabled == ["momentum", "op_fwd_yield"]
    assert DEFAULT_LAUNCH_CONFIG.global_config.start == "2020-01-01"
    assert DEFAULT_LAUNCH_CONFIG.global_config.fill_mode == "next_open"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/test_strategies.py::test_default_launch_config_enables_both_default_strategies -v`
Expected: FAIL with `ModuleNotFoundError` or missing `DEFAULT_LAUNCH_CONFIG`

- [ ] **Step 3: Write the failing enabled-preset filtering test**

```python
from live_dashboard.strategies import StrategyPreset, enabled_strategy_presets


def test_enabled_strategy_presets_filters_disabled_entries() -> None:
    presets = (
        StrategyPreset(enabled=True, strategy_name="momentum", display_label="Momentum", params={"top_n": 20}),
        StrategyPreset(enabled=False, strategy_name="op_fwd_yield", display_label="OP Fwd Yield", params={"top_n": 20}),
    )

    assert [preset.strategy_name for preset in enabled_strategy_presets(presets)] == ["momentum"]
```
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/test_strategies.py::test_enabled_strategy_presets_filters_disabled_entries -v`
Expected: FAIL with missing import or missing function

- [ ] **Step 5: Write the minimal implementation**

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GlobalRunConfig:
    start: str = "2020-01-01"
    end: str = "2025-12-31"
    capital: float = 100_000_000.0
    schedule: str = "monthly"
    fill_mode: str = "next_open"
    fee: float = 0.0
    sell_tax: float = 0.0
    slippage: float = 0.0
    use_k200: bool = True
    allow_fractional: bool = True


@dataclass(frozen=True, slots=True)
class StrategyPreset:
    enabled: bool
    strategy_name: str
    display_label: str
    params: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DashboardLaunchConfig:
    global_config: GlobalRunConfig
    strategies: tuple[StrategyPreset, ...]


DEFAULT_LAUNCH_CONFIG = DashboardLaunchConfig(
    global_config=GlobalRunConfig(),
    strategies=(
        StrategyPreset(True, "momentum", "Momentum", {"top_n": 20, "lookback": 20}),
        StrategyPreset(True, "op_fwd_yield", "OP Fwd Yield", {"top_n": 20}),
    ),
)


def enabled_strategy_presets(presets: tuple[StrategyPreset, ...]) -> tuple[StrategyPreset, ...]:
    return tuple(preset for preset in presets if preset.enabled)
```

- [ ] **Step 6: Run the strategy config tests**

Run: `pytest tests/live_dashboard/test_strategies.py -v`
Expected: PASS with both tests green

### Task 2: Resolve Saved Runs Against Desired Config

**Files:**
- Create: `live_dashboard/backend/services/launch_resolution.py`
- Test: `tests/live_dashboard/backend/test_launch_resolution.py`

- [ ] **Step 1: Write the failing newest-match selection test**

```python
from pathlib import Path

from live_dashboard.backend.services.launch_resolution import LaunchResolutionService
from live_dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def test_resolution_reuses_newest_matching_run(tmp_path: Path) -> None:
    _write_run(
        tmp_path,
        "momentum_20260405_090000",
        config={
            "strategy": "momentum",
            "start": "2020-01-01",
            "end": "2025-12-31",
            "capital": 100_000_000.0,
            "schedule": "monthly",
            "fill_mode": "next_open",
            "fee": 0.0,
            "sell_tax": 0.0,
            "slippage": 0.0,
            "use_k200": True,
            "allow_fractional": True,
            "top_n": 20,
            "lookback": 20,
        },
    )
    _write_run(
        tmp_path,
        "momentum_20260405_100000",
        config={
            "strategy": "momentum",
            "start": "2020-01-01",
            "end": "2025-12-31",
            "capital": 100_000_000.0,
            "schedule": "monthly",
            "fill_mode": "next_open",
            "fee": 0.0,
            "sell_tax": 0.0,
            "slippage": 0.0,
            "use_k200": True,
            "allow_fractional": True,
            "top_n": 20,
            "lookback": 20,
        },
    )

    service = LaunchResolutionService(tmp_path)

    plan = service.resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["op_fwd_yield"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/backend/test_launch_resolution.py::test_resolution_reuses_newest_matching_run -v`
Expected: FAIL with missing module or missing `LaunchResolutionService`

- [ ] **Step 3: Write the failing stale-global-config test**

```python
from dataclasses import replace

from live_dashboard.backend.services.launch_resolution import LaunchResolutionService
from live_dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def test_resolution_marks_all_presets_missing_when_global_config_changes(tmp_path: Path) -> None:
    _write_matching_default_runs(tmp_path)

    altered = replace(
        DEFAULT_LAUNCH_CONFIG,
        global_config=replace(DEFAULT_LAUNCH_CONFIG.global_config, fee=0.001),
    )

    plan = LaunchResolutionService(tmp_path).resolve(altered)

    assert plan.selected_run_ids == []
    assert [item.strategy_name for item in plan.missing_presets] == ["momentum", "op_fwd_yield"]
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/backend/test_launch_resolution.py::test_resolution_marks_all_presets_missing_when_global_config_changes -v`
Expected: FAIL with missing type or behavior

- [ ] **Step 5: Write the minimal implementation**

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from json import JSONDecodeError
from pathlib import Path

from live_dashboard.backend.services.run_index import RunIndexService
from live_dashboard.strategies import DashboardLaunchConfig, StrategyPreset, enabled_strategy_presets


@dataclass(frozen=True, slots=True)
class ResolvedRun:
    strategy_name: str
    run_id: str


@dataclass(frozen=True, slots=True)
class LaunchPlan:
    resolved_runs: tuple[ResolvedRun, ...]
    missing_presets: tuple[StrategyPreset, ...]

    @property
    def selected_run_ids(self) -> list[str]:
        return [item.run_id for item in self.resolved_runs]


class LaunchResolutionService:
    def __init__(self, runs_root: Path) -> None:
        self.runs_root = runs_root

    def resolve(self, config: DashboardLaunchConfig) -> LaunchPlan:
        resolved: list[ResolvedRun] = []
        missing: list[StrategyPreset] = []
        for preset in enabled_strategy_presets(config.strategies):
            matched = self._find_match(config, preset)
            if matched is None:
                missing.append(preset)
            else:
                resolved.append(ResolvedRun(strategy_name=preset.strategy_name, run_id=matched))
        return LaunchPlan(tuple(resolved), tuple(missing))

    def _find_match(self, config: DashboardLaunchConfig, preset: StrategyPreset) -> str | None:
        target = self._signature(config, preset)
        for run in RunIndexService(self.runs_root).list_runs():
            if run.strategy != preset.strategy_name:
                continue
            saved = self._load_signature(self.runs_root / run.run_id / "config.json")
            if saved == target:
                return run.run_id
        return None

    @staticmethod
    def _signature(config: DashboardLaunchConfig, preset: StrategyPreset) -> dict[str, object]:
        payload = asdict(config.global_config)
        payload["strategy"] = preset.strategy_name
        payload.update(preset.params)
        return payload

    @staticmethod
    def _load_signature(path: Path) -> dict[str, object] | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None
```

- [ ] **Step 6: Add the remaining tests for partial reuse and strategy-param invalidation**

```python
def test_resolution_executes_only_missing_strategy_when_partial_matches_exist(tmp_path: Path) -> None:
    ...


def test_resolution_marks_single_strategy_missing_when_strategy_params_change(tmp_path: Path) -> None:
    ...
```

- [ ] **Step 7: Run the launch-resolution tests**

Run: `pytest tests/live_dashboard/backend/test_launch_resolution.py -v`
Expected: PASS with reuse and invalidation tests green

### Task 3: Build Single-Command Launcher

**Files:**
- Create: `live_dashboard/run.py`
- Test: `tests/live_dashboard/test_run.py`

- [ ] **Step 1: Write the failing launcher orchestration test**

```python
from pathlib import Path

from live_dashboard.run import launch_dashboard
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
        lambda default_selected_run_ids: captured_defaults.setdefault("run_ids", default_selected_run_ids) or object(),
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/test_run.py::test_launch_dashboard_reuses_matching_runs_and_executes_missing_presets -v`
Expected: FAIL with missing module or missing `launch_dashboard`

- [ ] **Step 3: Write the minimal implementation**

```python
from __future__ import annotations

from pathlib import Path
import subprocess

import uvicorn

from backtesting.run import BacktestRunner, RunConfig
from live_dashboard.backend.main import create_app
from live_dashboard.backend.services.launch_resolution import LaunchResolutionService
from live_dashboard.strategies import DEFAULT_LAUNCH_CONFIG, enabled_strategy_presets
from root import ROOT


def build_frontend(frontend_dir: Path) -> None:
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)


def launch_dashboard(*, runs_root: Path | None = None, host: str = "127.0.0.1", port: int = 8000) -> None:
    resolved_root = runs_root or (ROOT.results_path / "backtests")
    build_frontend(ROOT.root / "live_dashboard" / "frontend")
    plan = LaunchResolutionService(resolved_root).resolve(DEFAULT_LAUNCH_CONFIG)
    runner = BacktestRunner(result_dir=resolved_root)
    selected_run_ids = list(plan.selected_run_ids)

    for preset in plan.missing_presets:
        config = RunConfig(
            start=DEFAULT_LAUNCH_CONFIG.global_config.start,
            end=DEFAULT_LAUNCH_CONFIG.global_config.end,
            capital=DEFAULT_LAUNCH_CONFIG.global_config.capital,
            strategy=preset.strategy_name,
            schedule=DEFAULT_LAUNCH_CONFIG.global_config.schedule,
            fill_mode=DEFAULT_LAUNCH_CONFIG.global_config.fill_mode,
            fee=DEFAULT_LAUNCH_CONFIG.global_config.fee,
            sell_tax=DEFAULT_LAUNCH_CONFIG.global_config.sell_tax,
            slippage=DEFAULT_LAUNCH_CONFIG.global_config.slippage,
            use_k200=DEFAULT_LAUNCH_CONFIG.global_config.use_k200,
            allow_fractional=DEFAULT_LAUNCH_CONFIG.global_config.allow_fractional,
            **preset.params,
        )
        report = runner.run(config)
        selected_run_ids.append(report.output_dir.name)

    app = create_app(default_selected_run_ids=selected_run_ids)
    uvicorn.run(app, host=host, port=port)
```

- [ ] **Step 4: Add a failing build-step test and pass it**

```python
def test_build_frontend_runs_npm_build(monkeypatch) -> None:
    ...
```

- [ ] **Step 5: Run the launcher tests**

Run: `pytest tests/live_dashboard/test_run.py -v`
Expected: PASS with launcher orchestration green

### Task 4: Expose Bootstrap State And Serve The SPA From FastAPI

**Files:**
- Modify: `live_dashboard/backend/schemas.py`
- Modify: `live_dashboard/backend/api.py`
- Modify: `live_dashboard/backend/main.py`
- Modify: `tests/live_dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Write the failing bootstrap API test**

```python
from fastapi.testclient import TestClient

from live_dashboard.backend.main import create_app


def test_session_endpoint_returns_default_selected_run_ids() -> None:
    client = TestClient(create_app(default_selected_run_ids=["momentum_20260405_100000"]))

    response = client.get("/api/session")

    assert response.status_code == 200
    assert response.json() == {"defaultSelectedRunIds": ["momentum_20260405_100000"]}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/backend/test_dashboard_api.py::test_session_endpoint_returns_default_selected_run_ids -v`
Expected: FAIL with missing route or missing `create_app`

- [ ] **Step 3: Add the failing SPA-serving test**

```python
def test_create_app_serves_index_html_for_non_api_routes(tmp_path: Path) -> None:
    frontend_dist = tmp_path / "dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text("<html><body>dashboard</body></html>", encoding="utf-8")

    client = TestClient(create_app(default_selected_run_ids=[], frontend_dist=frontend_dist))

    response = client.get("/workspace")

    assert response.status_code == 200
    assert "dashboard" in response.text
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `pytest tests/live_dashboard/backend/test_dashboard_api.py::test_create_app_serves_index_html_for_non_api_routes -v`
Expected: FAIL with 404

- [ ] **Step 5: Write the minimal implementation**

```python
class SessionBootstrapModel(DashboardBaseModel):
    default_selected_run_ids: list[str]
```

```python
def create_app(*, default_selected_run_ids: list[str], frontend_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="1w1a Live Dashboard")
    app.state.default_selected_run_ids = default_selected_run_ids
    ...
```

```python
@router.get("/session", response_model=SessionBootstrapModel)
def get_session(request: Request) -> dict[str, object]:
    return {"defaultSelectedRunIds": list(request.app.state.default_selected_run_ids)}
```

- [ ] **Step 6: Run the backend API tests**

Run: `pytest tests/live_dashboard/backend/test_dashboard_api.py -v`
Expected: PASS with dashboard and bootstrap tests green

### Task 5: Hydrate The Frontend From Bootstrap State

**Files:**
- Modify: `live_dashboard/frontend/src/lib/api.ts`
- Modify: `live_dashboard/frontend/src/lib/types.ts`
- Modify: `live_dashboard/frontend/src/app/App.tsx`
- Modify: `live_dashboard/frontend/src/components/App.test.tsx`

- [ ] **Step 1: Write the failing bootstrap hydration test**

```tsx
it("hydrates the initial selection from the backend bootstrap payload", async () => {
  fetchRuns.mockResolvedValue([
    { runId: "momentum_run", label: "Momentum", strategy: "momentum", summary: { finalEquity: 100, avgTurnover: 0.1 } },
    { runId: "op_fwd_run", label: "OP Fwd Yield", strategy: "op_fwd_yield", summary: { finalEquity: 100, avgTurnover: 0.1 } },
  ]);
  fetchSession.mockResolvedValue({ defaultSelectedRunIds: ["op_fwd_run"] });
  fetchDashboard.mockResolvedValue(...)

  render(<App />)

  expect(await screen.findByRole("button", { name: /OP Fwd Yield/i })).toHaveAttribute("aria-pressed", "true")
  expect(fetchDashboard).toHaveBeenCalledWith(["op_fwd_run"])
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd live_dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: FAIL with missing `fetchSession` or wrong default selection

- [ ] **Step 3: Write the minimal implementation**

```ts
export type SessionBootstrap = {
  defaultSelectedRunIds: string[];
};
```

```ts
export async function fetchSession(): Promise<SessionBootstrap> {
  const response = await fetch(`${API_ROOT}/session`);
  ...
}
```

```tsx
void Promise.all([fetchRuns(), fetchSession()]).then(([nextRuns, session]) => {
  const availableRunIds = new Set(nextRuns.map((run) => run.runId));
  const defaults = session.defaultSelectedRunIds.filter((runId) => availableRunIds.has(runId));
  setSelectedRunIds(defaults.length > 0 ? defaults : nextRuns[0] ? [nextRuns[0].runId] : []);
})
```

- [ ] **Step 4: Run the frontend test**

Run: `cd live_dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: PASS with bootstrap hydration green

- [ ] **Step 5: Build the frontend**

Run: `cd live_dashboard/frontend && npm run build`
Expected: PASS and write `dist/`

### Task 6: Document The One-Command Flow

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the README**

Add a `Live Dashboard` section documenting:

- `python live_dashboard/run.py`
- reuse of newest matching saved runs
- auto-execution of missing/stale default strategies
- normal browser URL `http://127.0.0.1:8000`

- [ ] **Step 2: Run the end-to-end verification commands**

Run: `pytest tests/live_dashboard -v`
Expected: PASS

Run: `cd live_dashboard/frontend && npm test -- --run`
Expected: PASS

Run: `cd live_dashboard/frontend && npm run build`
Expected: PASS

Run: `python live_dashboard/run.py --help`
Expected: PASS or prints launcher usage without crashing
