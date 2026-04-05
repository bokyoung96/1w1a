# Research Dashboard Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a research-grade dashboard that reuses or auto-runs deduplicated saved strategies, honors warmup history, always renders per-strategy benchmarks, and exposes richer drill-down analytics in one page.

**Architecture:** Extend dashboard strategy presets so each preset carries params, warmup, and benchmark metadata. Push dedupe and warmup-aware run resolution into the launcher/backend, expand the API with research payload sections computed server-side from saved runs, then replace the thin frontend strips with a full-width research workspace that supports multi-strategy comparison and in-page focus changes.

**Tech Stack:** Python, FastAPI, pandas, Pydantic, React, TypeScript, Vite, ECharts, pytest, Vitest

---

### Task 1: Warmup-Aware Presets And Duplicate Run Hygiene

**Files:**
- Modify: `dashboard/strategies.py`
- Modify: `dashboard/run.py`
- Modify: `dashboard/backend/services/launch_resolution.py`
- Modify: `backtesting/run.py`
- Test: `tests/dashboard/test_strategies.py`
- Test: `tests/dashboard/backend/test_launch_resolution.py`
- Test: `tests/dashboard/test_run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write failing tests for preset metadata and normalized signatures**

```python
def test_strategy_preset_exposes_benchmark_and_warmup() -> None:
    preset = DEFAULT_LAUNCH_CONFIG.strategies[0]

    assert preset.benchmark.code == "IKS200"
    assert preset.warmup.extra_days > 0


def test_resolution_signature_includes_benchmark_metadata(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_090000", strategy="momentum")
    altered = replace(
        DEFAULT_LAUNCH_CONFIG,
        strategies=(
            replace(
                DEFAULT_LAUNCH_CONFIG.strategies[0],
                benchmark=BenchmarkConfig(code="SPX", name="S&P 500"),
            ),
            DEFAULT_LAUNCH_CONFIG.strategies[1],
        ),
    )

    plan = LaunchResolutionService(tmp_path).resolve(altered)

    assert [item.strategy_name for item in plan.missing_presets] == ["momentum", "op_fwd_yield"]
```

- [ ] **Step 2: Run tests to verify current behavior fails**

Run: `pytest tests/dashboard/test_strategies.py tests/dashboard/backend/test_launch_resolution.py -v`

Expected: FAIL because `StrategyPreset` does not define `benchmark` or `warmup`, and signature matching ignores benchmark metadata.

- [ ] **Step 3: Implement preset metadata, dedupe/archive support, and warmup-aware run config**

```python
@dataclass(frozen=True, slots=True)
class WarmupConfig:
    extra_days: int = 0


@dataclass(frozen=True, slots=True)
class StrategyPreset:
    enabled: bool
    strategy_name: str
    display_label: str
    params: Mapping[str, object] = field(default_factory=dict)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig.default_kospi200)
    warmup: WarmupConfig = field(default_factory=lambda: WarmupConfig(extra_days=252))
```

```python
@dataclass(frozen=True, slots=True)
class LaunchPlan:
    resolved_runs: tuple[ResolvedRun, ...]
    missing_presets: tuple[StrategyPreset, ...]
    archived_run_ids: tuple[str, ...] = ()
```

```python
def _build_run_config(preset: StrategyPreset) -> RunConfig:
    config = DEFAULT_LAUNCH_CONFIG.global_config
    return RunConfig(
        start=config.start,
        end=config.end,
        display_start=config.start,
        display_end=config.end,
        benchmark_code=preset.benchmark.code,
        benchmark_name=preset.benchmark.name,
        warmup_days=preset.warmup.extra_days,
        ...
    )
```

```python
def _archive_duplicate_runs(self, available_runs: Sequence[RunOptionModel], runs_root: Path) -> tuple[str, ...]:
    active: dict[tuple[tuple[str, Any], ...], str] = {}
    archived: list[str] = []
    archive_root = runs_root / "_archived"
    archive_root.mkdir(parents=True, exist_ok=True)
    for run in available_runs:
        signature = self._saved_signature_tuple(...)
        if signature not in active:
            active[signature] = run.run_id
            continue
        shutil.move(str(runs_root / run.run_id), str(archive_root / run.run_id))
        archived.append(run.run_id)
    return tuple(archived)
```

- [ ] **Step 4: Add trimming logic to the backtest runner after warmup computation**

```python
load_start = self._resolve_load_start(config.start, config.warmup_days)
market = self.loader.load(LoadRequest(datasets=dataset_ids, start=load_start, end=config.end))
...
result = self._trim_result_to_display_range(result, start=config.display_start or config.start, end=config.display_end or config.end)
```

```python
def _trim_result_to_display_range(self, result: BacktestResult, *, start: str, end: str) -> BacktestResult:
    return BacktestResult(
        equity=result.equity.loc[start:end],
        returns=result.returns.loc[start:end],
        turnover=result.turnover.loc[start:end],
        weights=result.weights.loc[start:end],
        qty=result.qty.loc[start:end],
        trades=result.trades.loc[(result.trades["date"] >= start) & (result.trades["date"] <= end)].copy(),
    )
```

- [ ] **Step 5: Add launch tests for duplicate archival and missing-only reruns**

```python
def test_resolution_archives_older_duplicate_run(tmp_path: Path) -> None:
    _write_matching_run(tmp_path, "momentum_20260405_090000", strategy="momentum")
    _write_matching_run(tmp_path, "momentum_20260405_100000", strategy="momentum")

    plan = LaunchResolutionService(tmp_path).resolve(DEFAULT_LAUNCH_CONFIG)

    assert plan.selected_run_ids == ["momentum_20260405_100000"]
    assert plan.archived_run_ids == ("momentum_20260405_090000",)
    assert (tmp_path / "_archived" / "momentum_20260405_090000").is_dir()
```

- [ ] **Step 6: Run targeted tests and fix until green**

Run: `pytest tests/dashboard/test_strategies.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/test_run.py tests/test_run.py -v`

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add dashboard/strategies.py dashboard/run.py dashboard/backend/services/launch_resolution.py backtesting/run.py tests/dashboard/test_strategies.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/test_run.py tests/test_run.py
git commit -m "feat: add warmup-aware dashboard run resolution"
```

### Task 2: Research Analytics Payload And Benchmark-Aware Snapshots

**Files:**
- Modify: `backtesting/reporting/analytics.py`
- Modify: `backtesting/reporting/benchmarks.py`
- Modify: `backtesting/reporting/snapshots.py`
- Modify: `dashboard/backend/schemas.py`
- Modify: `dashboard/backend/serializers.py`
- Modify: `dashboard/backend/services/dashboard_payload.py`
- Test: `tests/reporting/test_snapshots.py`
- Test: `tests/dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Write failing snapshot and API tests for research payload sections**

```python
def test_snapshot_factory_builds_sector_timeseries_and_heatmap(...) -> None:
    snapshot = factory.build(run, BenchmarkConfig.default_kospi200())

    assert not snapshot.research.monthly_heatmap.empty
    assert not snapshot.research.sector_weights.empty
    assert "rolling_sharpe" in snapshot.research.rolling
```

```python
def test_dashboard_payload_includes_research_sections(tmp_path: Path) -> None:
    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])
    payload = response.json()

    assert "research" in payload
    assert payload["research"]["focus"]["kind"] == "all-selected"
    assert payload["research"]["sectorWeightSeries"]["alpha_20260405_100000"]
    assert payload["research"]["yearlyExcessReturns"]["alpha_20260405_100000"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/reporting/test_snapshots.py tests/dashboard/backend/test_dashboard_api.py -v`

Expected: FAIL because the snapshot and API models do not yet expose `research`, sector time series, monthly heatmaps, or yearly excess returns.

- [ ] **Step 3: Introduce research dataclasses and reusable calculations**

```python
@dataclass(frozen=True, slots=True)
class ResearchSnapshot:
    monthly_heatmap: pd.DataFrame
    monthly_distribution: pd.Series
    daily_distribution: pd.Series
    yearly_excess_returns: pd.Series
    sector_performance: pd.DataFrame
    sector_weights: pd.DataFrame
    drawdown_episodes: pd.DataFrame
```

```python
def build_monthly_heatmap(returns: pd.Series) -> pd.DataFrame:
    monthly = (1.0 + returns).resample("ME").prod().sub(1.0)
    frame = monthly.to_frame("return")
    frame["year"] = frame.index.year
    frame["month"] = frame.index.month
    return frame.pivot(index="year", columns="month", values="return").sort_index()
```

- [ ] **Step 4: Extend sector repository helpers to compute time series instead of latest snapshot only**

```python
def sector_weight_timeseries(self, weights: pd.DataFrame) -> pd.DataFrame:
    records = []
    for date, row in weights.fillna(0.0).iterrows():
        sector_row = self.latest_sector_row(pd.Timestamp(date))
        aligned = pd.DataFrame({"sector": sector_row.reindex(row.index), "weight": row.astype(float)}).dropna()
        grouped = aligned.groupby("sector", sort=False)["weight"].sum()
        records.append(grouped.rename(pd.Timestamp(date)))
    return pd.DataFrame(records).fillna(0.0).sort_index()
```

- [ ] **Step 5: Serialize research-focused payloads in backend schemas and payload service**

```python
class HeatmapCellModel(DashboardBaseModel):
    year: int
    month: int
    value: float


class DashboardResearchModel(DashboardBaseModel):
    focus: ResearchFocusModel
    benchmark_series: dict[str, list[ValuePointModel]]
    return_distribution: dict[str, DistributionModel]
    monthly_heatmap: dict[str, list[HeatmapCellModel]]
    yearly_excess_returns: dict[str, list[ValuePointModel]]
    sector_performance_series: dict[str, list[CategorySeriesModel]]
    sector_weight_series: dict[str, list[CategorySeriesModel]]
    drawdown_episodes: dict[str, list[DrawdownEpisodeModel]]
```

```python
research = DashboardResearchModel(
    focus=ResearchFocusModel(kind="all-selected"),
    benchmark_series={snapshot.run_id: serialize_value_points(snapshot.benchmark_equity) for snapshot in snapshots},
    monthly_heatmap={snapshot.run_id: serialize_heatmap(snapshot.research.monthly_heatmap) for snapshot in snapshots},
    ...
)
```

- [ ] **Step 6: Run targeted backend tests and fix until green**

Run: `pytest tests/reporting/test_snapshots.py tests/dashboard/backend/test_dashboard_api.py -v`

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backtesting/reporting/analytics.py backtesting/reporting/benchmarks.py backtesting/reporting/snapshots.py dashboard/backend/schemas.py dashboard/backend/serializers.py dashboard/backend/services/dashboard_payload.py tests/reporting/test_snapshots.py tests/dashboard/backend/test_dashboard_api.py
git commit -m "feat: add dashboard research analytics payload"
```

### Task 3: Frontend Research Workspace, Benchmark Overlays, And Drill-Down

**Files:**
- Modify: `dashboard/frontend/src/app/App.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Modify: `dashboard/frontend/src/components/PerformanceStrip.tsx`
- Modify: `dashboard/frontend/src/components/DiagnosticStrip.tsx`
- Modify: `dashboard/frontend/src/components/ExposureBand.tsx`
- Modify: `dashboard/frontend/src/components/ContextDrawer.tsx`
- Create: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
- Create: `dashboard/frontend/src/components/ResearchDetailPanel.tsx`
- Modify: `dashboard/frontend/src/lib/types.ts`
- Test: `dashboard/frontend/src/components/App.test.tsx`
- Test: `dashboard/frontend/src/components/RunSelector.test.tsx`

- [ ] **Step 1: Write failing frontend tests for research workspace rendering and focus changes**

```tsx
it("renders research panels and switches focus when a strategy tile is clicked", async () => {
  render(<App />);

  expect(await screen.findByText(/rolling sharpe/i)).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: /alpha strategy/i }));
  expect(screen.getByText(/focus: alpha strategy/i)).toBeInTheDocument();
});
```

```tsx
it("does not render duplicate active runs in the selector", async () => {
  server.use(http.get("/api/runs", () => HttpResponse.json([duplicateRun, latestRun])));
  render(<App />);

  const options = await screen.findAllByRole("button", { name: /op fwd yield/i });
  expect(options).toHaveLength(1);
});
```

- [ ] **Step 2: Run tests to verify current behavior fails**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx src/components/RunSelector.test.tsx`

Expected: FAIL because the app does not expose a research workspace, focus state, or duplicate suppression logic in the UI contract.

- [ ] **Step 3: Expand client types and build a dedicated research workspace**

```ts
export type ResearchFocus =
  | { kind: "all-selected" }
  | { kind: "strategy"; runId: string }
  | { kind: "sector"; sector: string };

export type DashboardResearch = {
  focus: ResearchFocus;
  benchmarkSeries: Record<string, ValuePoint[]>;
  monthlyHeatmap: Record<string, HeatmapCell[]>;
  sectorWeightSeries: Record<string, CategorySeries[]>;
  sectorPerformanceSeries: Record<string, CategorySeries[]>;
  yearlyExcessReturns: Record<string, ValuePoint[]>;
};
```

```tsx
export function ResearchWorkspace({ dashboard, focus, onFocusChange }: Props) {
  return (
    <section className="research-workspace">
      <ResearchFigure title="Return vs Drawdown" />
      <ResearchFigure title="Return Distribution" />
      <ResearchFigure title="Monthly Heatmap" />
      <ResearchFigure title="Rolling Sharpe" />
      <ResearchFigure title="Yearly Excess Returns" />
      <ResearchFigure title="Sector Performance" />
      <ResearchFigure title="Sector Weights" />
      <ResearchDetailPanel dashboard={dashboard} focus={focus} onFocusChange={onFocusChange} />
    </section>
  );
}
```

- [ ] **Step 4: Replace single benchmark handling with per-run benchmark overlays and click-driven focus**

```tsx
const summarySeries = dashboard.selectedRunIds.flatMap((runId) => [
  buildEquitySeries(runId),
  buildBenchmarkSeries(runId),
]);

onEvents={{
  click: (params) => {
    const runId = seriesNameToRunId[params.seriesName];
    if (runId) {
      onFocusChange({ kind: "strategy", runId });
    }
  },
}}
```

- [ ] **Step 5: Refresh layout and keep dense charting readable**

```css
.research-workspace {
  display: grid;
  gap: 1.5rem;
}

.research-grid--double {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.research-figure {
  min-height: 320px;
  border: 1px solid rgba(255, 248, 240, 0.08);
  background: linear-gradient(180deg, rgba(17, 20, 24, 0.94), rgba(11, 13, 16, 0.98));
}
```

- [ ] **Step 6: Run frontend tests and production build**

Run: `cd dashboard/frontend && npm test -- --run`

Expected: PASS

Run: `cd dashboard/frontend && npm run build`

Expected: PASS, with at most chunk-size warnings.

- [ ] **Step 7: Commit**

```bash
git add dashboard/frontend/src/app/App.tsx dashboard/frontend/src/app/dashboard.css dashboard/frontend/src/components/PerformanceStrip.tsx dashboard/frontend/src/components/DiagnosticStrip.tsx dashboard/frontend/src/components/ExposureBand.tsx dashboard/frontend/src/components/ContextDrawer.tsx dashboard/frontend/src/components/ResearchWorkspace.tsx dashboard/frontend/src/components/ResearchDetailPanel.tsx dashboard/frontend/src/lib/types.ts dashboard/frontend/src/components/App.test.tsx dashboard/frontend/src/components/RunSelector.test.tsx
git commit -m "feat: add dashboard research workspace"
```

### Task 4: Documentation, Refactoring, And End-To-End Verification

**Files:**
- Modify: `README.md`
- Modify: `dashboard/backend/api.py`
- Modify: `dashboard/backend/main.py`
- Modify: `dashboard/backend/services/run_index.py`
- Test: `tests/dashboard/backend/test_run_index_service.py`
- Test: `tests/dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Write failing tests for archived-run filtering and bootstrap contract**

```python
def test_run_index_ignores_archived_runs(tmp_path: Path) -> None:
    _write_saved_run(tmp_path, "alpha_20260405_100000")
    _write_saved_run(tmp_path / "_archived", "alpha_20260404_100000")

    runs = RunIndexService(tmp_path).list_runs()

    assert [run.run_id for run in runs] == ["alpha_20260405_100000"]
```

- [ ] **Step 2: Run tests to verify current behavior fails**

Run: `pytest tests/dashboard/backend/test_run_index_service.py tests/dashboard/backend/test_dashboard_api.py -v`

Expected: FAIL because the index service currently walks all directories under the result root without archive-aware filtering.

- [ ] **Step 3: Refactor route/service boundaries and update README**

```markdown
## Dashboard

Run:

```bash
python dashboard/run.py
```

Dashboard presets live in `dashboard/strategies.py`.
Backtest strategy implementations live in `backtesting/strategies/`.
Saved duplicate runs are archived under `results/backtests/_archived/`.
```

- [ ] **Step 4: Run full verification**

Run: `pytest tests/dashboard tests/reporting tests/test_run.py -v`

Expected: PASS

Run: `cd dashboard/frontend && npm test -- --run`

Expected: PASS

Run: `cd dashboard/frontend && npm run build`

Expected: PASS

Run: `python dashboard/run.py --help`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md dashboard/backend/api.py dashboard/backend/main.py dashboard/backend/services/run_index.py tests/dashboard/backend/test_run_index_service.py tests/dashboard/backend/test_dashboard_api.py
git commit -m "docs: document dashboard operations and archive behavior"
```
