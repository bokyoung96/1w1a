# Dashboard Analytics Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add top-level launch metadata, denser return distributions, rolling correlation, latest-holdings winners/losers, and repaired sector/yearly visuals to the dashboard while preserving the existing sector analytics.

**Architecture:** Keep the backend as the source of truth for all new analytics. Extend the reporting snapshot and dashboard payload layers first, then update the frontend types and chart builders to consume the new fields without moving calculation logic into React. Preserve the existing research drill-down model and layer the new visuals onto the current dashboard shell.

**Tech Stack:** Python, pandas, FastAPI, Pydantic, React, TypeScript, Vitest, ECharts

---

## File Map

**Backend calculation and payload files**

- Modify: `backtesting/reporting/analytics.py`
  Responsibility: shared return-series helpers, daily/monthly distribution builders, research dataclass shape.
- Modify: `backtesting/reporting/benchmarks.py`
  Responsibility: latest-holdings price lookup helpers for rebalance-window leaderboard calculations.
- Modify: `backtesting/reporting/snapshots.py`
  Responsibility: rolling correlation, monthly distribution, latest-holdings leader/laggard analytics, and launch-metadata-compatible snapshot wiring.
- Modify: `dashboard/backend/schemas.py`
  Responsibility: API contract for launch metadata, rolling correlation, monthly distributions, and holdings winners/losers.
- Modify: `dashboard/backend/serializers.py`
  Responsibility: serialization helpers for leaderboard rows and new distribution buckets.
- Modify: `dashboard/backend/services/dashboard_payload.py`
  Responsibility: inject dashboard launch metadata from `dashboard/strategies.py` and expose new analytics in the payload.

**Frontend rendering files**

- Modify: `dashboard/frontend/src/lib/types.ts`
  Responsibility: TypeScript types for the expanded payload contract.
- Modify: `dashboard/frontend/src/components/TopRail.tsx`
  Responsibility: top-level shell badges that remain globally visible.
- Modify: `dashboard/frontend/src/components/PerformanceStrip.tsx`
  Responsibility: comparison hero plus compact launch metadata rail.
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
  Responsibility: histogram-style daily/monthly distributions, rolling risk trio, repaired yearly chart, preserved sector charts, and sector donut.
- Modify: `dashboard/frontend/src/components/ExposureBand.tsx`
  Responsibility: latest holdings, winners, losers, and latest sector snapshot presentation.
- Modify: `dashboard/frontend/src/app/dashboard.css`
  Responsibility: layout and visual treatment for the new metadata rail, histogram stack, rolling trio, leaderboard blocks, and donut support.

**Tests**

- Modify: `tests/dashboard/backend/test_dashboard_api.py`
  Responsibility: backend payload regression coverage for new fields.
- Modify: `dashboard/frontend/src/components/App.test.tsx`
  Responsibility: frontend rendering regression coverage for new metadata and charts.

### Task 1: Add failing backend payload tests for the new analytics contract

**Files:**
- Modify: `tests/dashboard/backend/test_dashboard_api.py`
- Test: `tests/dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_dashboard_payload_includes_launch_metadata_rolling_correlation_and_monthly_distribution(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=121.0,
        avg_turnover=0.03,
        weights=[
            [0.6, 0.4, 0.0],
            [0.6, 0.4, 0.0],
            [0.55, 0.45, 0.0],
        ],
        dates=["2024-01-02", "2024-01-03", "2024-02-01"],
        prices={
            "A": [100.0, 112.0, 118.0],
            "B": [100.0, 96.0, 92.0],
            "C": [100.0, 101.0, 102.0],
        },
        benchmark_prices=[200.0, 202.0, 205.0],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    payload = response.json()
    assert payload["launch"]["startDate"] == "2020-01-01"
    assert payload["launch"]["endDate"] == "2025-12-31"
    assert payload["launch"]["capital"] == 100000000.0
    assert payload["launch"]["schedule"] == "monthly"
    assert payload["launch"]["fillMode"] == "next_open"
    assert "alpha_20260405_100000" in payload["rolling"]["rollingCorrelationByRun"]
    assert payload["research"]["monthlyReturnDistribution"]["alpha_20260405_100000"]
```

```python
def test_dashboard_payload_includes_latest_holdings_winners_and_losers(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=118.0,
        avg_turnover=0.03,
        weights=[
            [0.4, 0.4, 0.2],
            [0.0, 0.5, 0.5],
            [0.0, 0.5, 0.5],
        ],
        dates=["2024-01-02", "2024-01-31", "2024-02-29"],
        prices={
            "A": [100.0, 100.0, 100.0],
            "B": [100.0, 110.0, 130.0],
            "C": [100.0, 95.0, 85.0],
        },
        benchmark_prices=[200.0, 201.0, 202.0],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    payload = response.json()
    leaders = payload["exposure"]["latestHoldingsLeaders"]["alpha_20260405_100000"]
    laggards = payload["exposure"]["latestHoldingsLaggards"]["alpha_20260405_100000"]
    assert leaders[0]["symbol"] == "B"
    assert leaders[0]["returnSinceRebalance"] == pytest.approx(0.1818181818)
    assert laggards[0]["symbol"] == "C"
    assert laggards[0]["rebalanceDate"] == "2024-01-31"
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `pytest tests/dashboard/backend/test_dashboard_api.py -q`
Expected: FAIL with missing keys such as `launch`, `monthlyReturnDistribution`, `latestHoldingsLeaders`, or `rollingCorrelationByRun`.

- [ ] **Step 3: Extend the test helpers to support multi-date fixtures**

```python
def _write_saved_run(
    root: Path,
    run_id: str,
    *,
    name: str,
    strategy: str = "momentum",
    final_equity: float,
    avg_turnover: float,
    weights: list[list[float]],
    dates: list[str] | None = None,
    prices: dict[str, list[float]] | None = None,
    benchmark_prices: list[float] | None = None,
    benchmark: dict[str, object] | None = None,
    latest_weights_rows: list[dict[str, object]] | None = None,
) -> None:
    dates = dates or ["2024-01-02", "2024-01-03"]
    index = pd.to_datetime(dates)
    equity = pd.Series(np.linspace(100.0, final_equity, len(index)), index=index, name="equity")
    returns = equity.pct_change().fillna(0.0).rename("returns")
    turnover = pd.Series(np.linspace(0.02, avg_turnover * 2 - 0.02, len(index)), index=index, name="turnover")
    weights_frame = pd.DataFrame(weights, columns=["A", "B", "C"], index=index)
    qty_frame = weights_frame.mul(10.0)
    equity.to_csv(series_dir / "equity.csv", index_label="date")
    returns.to_csv(series_dir / "returns.csv", index_label="date")
    turnover.to_csv(series_dir / "turnover.csv", index_label="date")
    weights_frame.to_parquet(positions_dir / "weights.parquet")
    qty_frame.to_parquet(positions_dir / "qty.parquet")
```

- [ ] **Step 4: Re-run the focused tests to keep them red for contract-only reasons**

Run: `pytest tests/dashboard/backend/test_dashboard_api.py -q`
Expected: FAIL on the new assertions, not on fixture shape or helper exceptions.

- [ ] **Step 5: Commit the red test scaffold**

```bash
git add tests/dashboard/backend/test_dashboard_api.py
git commit -m "test: cover dashboard analytics payload refresh"
```

### Task 2: Implement backend analytics helpers and snapshot calculations

**Files:**
- Modify: `backtesting/reporting/analytics.py`
- Modify: `backtesting/reporting/benchmarks.py`
- Modify: `backtesting/reporting/snapshots.py`
- Test: `tests/dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Write the minimal helper interfaces in the analytics layer**

```python
@dataclass(frozen=True, slots=True)
class HoldingsPerformanceSnapshot:
    leaders: pd.DataFrame = field(default_factory=pd.DataFrame)
    laggards: pd.DataFrame = field(default_factory=pd.DataFrame)


@dataclass(frozen=True, slots=True)
class ResearchSnapshot:
    monthly_heatmap: pd.DataFrame = field(default_factory=pd.DataFrame)
    return_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    monthly_return_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    yearly_excess_returns: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    sector_contribution_method: str = ""
    sector_contribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    sector_weights: pd.DataFrame = field(default_factory=pd.DataFrame)
    drawdown_episodes: pd.DataFrame = field(default_factory=pd.DataFrame)
```

```python
def build_holdings_rebalance_returns(
    weights: pd.DataFrame,
    prices: pd.DataFrame | None,
    *,
    limit: int = 5,
) -> HoldingsPerformanceSnapshot:
    if prices is None or weights.empty:
        return HoldingsPerformanceSnapshot()
    latest_weights = weights.fillna(0.0).iloc[-1]
    current = latest_weights.loc[latest_weights.ne(0.0)]
    if current.empty:
        return HoldingsPerformanceSnapshot()
    rebalance_dates = weights.fillna(0.0).index[weights.fillna(0.0).diff().abs().sum(axis=1).gt(0.0)]
    rebalance_date = pd.Timestamp(rebalance_dates[-1] if len(rebalance_dates) > 0 else weights.index[-1])
    start_prices = prices.reindex(index=[rebalance_date], columns=current.index).ffill().iloc[0]
    end_prices = prices.reindex(index=[weights.index[-1]], columns=current.index).ffill().iloc[0]
    frame = pd.DataFrame(
        {
            "symbol": current.index.astype(str),
            "target_weight": current.values,
            "abs_weight": current.abs().values,
            "rebalance_date": rebalance_date,
            "return_since_rebalance": end_prices.div(start_prices).sub(1.0).values,
        }
    ).dropna(subset=["return_since_rebalance"])
    leaders = frame.sort_values(["return_since_rebalance", "abs_weight"], ascending=[False, False]).head(limit).reset_index(drop=True)
    laggards = frame.sort_values(["return_since_rebalance", "abs_weight"], ascending=[True, False]).head(limit).reset_index(drop=True)
    return HoldingsPerformanceSnapshot(leaders=leaders, laggards=laggards)
```

- [ ] **Step 2: Add the benchmark/price repository helper needed by the snapshot factory**

```python
def latest_holdings_returns(self, weights: pd.DataFrame, *, limit: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    snapshot = build_holdings_rebalance_returns(weights, self.prices, limit=limit)
    return snapshot.leaders, snapshot.laggards
```

- [ ] **Step 3: Extend rolling metrics and research snapshot construction in `snapshots.py`**

```python
def _build_rolling_metrics(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> RollingMetrics:
    window = 252
    rolling_sharpe = strategy_returns.rolling(window=window, min_periods=252).apply(
        lambda values: annualized_sharpe(pd.Series(values)),
        raw=False,
    )
    benchmark_variance = benchmark_returns.rolling(window=window, min_periods=252).var(ddof=0)
    rolling_beta = strategy_returns.rolling(window=window, min_periods=252).cov(benchmark_returns, ddof=0).div(
        benchmark_variance
    )
    rolling_correlation = strategy_returns.rolling(window=window, min_periods=252).corr(benchmark_returns)
    rolling_beta = rolling_beta.replace([float("inf"), float("-inf")], pd.NA)
    rolling_correlation = rolling_correlation.replace([float("inf"), float("-inf")], pd.NA)
    return RollingMetrics(
        series={
            "rolling_sharpe": rolling_sharpe.rename("rolling_sharpe"),
            "rolling_beta": rolling_beta.rename("rolling_beta"),
            "rolling_correlation": rolling_correlation.rename("rolling_correlation"),
        }
    )
```

```python
def _build_research(
    self,
    run: SavedRun,
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    drawdowns: DrawdownStats,
) -> ResearchSnapshot:
    monthly_distribution = build_return_distribution(monthly_return_series(strategy_returns, run.monthly_returns))
    sector_weights = self.sector_repo.sector_weight_timeseries(run.weights)
    sector_contribution = self.sector_repo.sector_contribution_timeseries(run.weights, strategy_returns)
    return ResearchSnapshot(
        monthly_heatmap=build_monthly_heatmap(strategy_returns, run.monthly_returns),
        return_distribution=build_return_distribution(strategy_returns),
        monthly_return_distribution=monthly_distribution,
        yearly_excess_returns=build_yearly_excess_returns(strategy_returns, benchmark_returns),
        sector_contribution_method=SECTOR_CONTRIBUTION_METHOD_WEIGHTED_ASSET_RETURNS,
        sector_contribution=sector_contribution,
        sector_weights=sector_weights,
        drawdown_episodes=drawdowns.episodes.sort_values(["drawdown", "start"], ascending=[True, True]),
    )
```

- [ ] **Step 4: Extend exposure snapshot data with leaders and laggards**

```python
def _build_exposure(self, run: SavedRun) -> ExposureSnapshot:
    holdings_count = run.weights.fillna(0.0).ne(0.0).sum(axis=1).rename("holdings_count")
    latest_holdings = run.latest_weights.copy() if run.latest_weights is not None else self._latest_holdings(run.weights)
    leaders, laggards = self.sector_repo.latest_holdings_returns(run.weights, limit=5)
    return ExposureSnapshot(
        holdings_count=holdings_count.astype(float),
        latest_holdings=latest_holdings,
        latest_leaders=leaders,
        latest_laggards=laggards,
    )
```

- [ ] **Step 5: Run the backend payload tests and verify they pass**

Run: `pytest tests/dashboard/backend/test_dashboard_api.py -q`
Expected: PASS, including assertions for launch metadata, monthly distributions, rolling correlation, and winners/losers.

- [ ] **Step 6: Commit the backend analytics changes**

```bash
git add backtesting/reporting/analytics.py backtesting/reporting/benchmarks.py backtesting/reporting/snapshots.py tests/dashboard/backend/test_dashboard_api.py
git commit -m "feat: add dashboard analytics backend payloads"
```

### Task 3: Wire the expanded dashboard API contract

**Files:**
- Modify: `dashboard/backend/schemas.py`
- Modify: `dashboard/backend/serializers.py`
- Modify: `dashboard/backend/services/dashboard_payload.py`
- Test: `tests/dashboard/backend/test_dashboard_api.py`

- [ ] **Step 1: Add the new schema models and payload fields**

```python
class DashboardLaunchModel(DashboardBaseModel):
    start_date: str
    end_date: str
    capital: float
    schedule: str
    fill_mode: str
    benchmark_name: str


class HoldingReturnModel(DashboardBaseModel):
    symbol: str
    target_weight: float
    abs_weight: float
    rebalance_date: str
    return_since_rebalance: float


class DashboardRollingModel(DashboardBaseModel):
    rolling_sharpe: list[NamedSeriesModel]
    rolling_beta: list[NamedSeriesModel]
    rolling_correlation: list[NamedSeriesModel]
```

```python
class DashboardExposureModel(DashboardBaseModel):
    holdings_count: list[NamedSeriesModel]
    latest_holdings: dict[str, list[HoldingModel]]
    latest_holdings_leaders: dict[str, list[HoldingReturnModel]]
    latest_holdings_laggards: dict[str, list[HoldingReturnModel]]
    sector_weights: dict[str, list[CategoryPointModel]]
```

- [ ] **Step 2: Add serializers for the new leaderboard rows**

```python
def serialize_holding_returns(frame: pd.DataFrame | None) -> list[HoldingReturnModel]:
    if frame is None or frame.empty:
        return []
    rows: list[HoldingReturnModel] = []
    for _, row in frame.iterrows():
        target_weight = sanitize_finite_number(row["target_weight"])
        abs_weight = sanitize_finite_number(row["abs_weight"])
        performance = sanitize_finite_number(row["return_since_rebalance"])
        if target_weight is None or abs_weight is None or performance is None:
            continue
        rows.append(
            HoldingReturnModel(
                symbol=str(row["symbol"]),
                target_weight=target_weight,
                abs_weight=abs_weight,
                rebalance_date=pd.Timestamp(row["rebalance_date"]).date().isoformat(),
                return_since_rebalance=performance,
            )
        )
    return rows
```

- [ ] **Step 3: Inject launch config and new series in the payload service**

```python
from dashboard.strategies import DEFAULT_LAUNCH_CONFIG


def build(self, run_ids: list[str]) -> DashboardPayloadModel:
    selected_runs = [self._read_run(run_id) for run_id in run_ids]
    snapshots = [self.snapshot_factory.build(run, self._resolve_benchmark(run)) for run in selected_runs]
    launch = DashboardLaunchModel(
        start_date=DEFAULT_LAUNCH_CONFIG.global_config.start,
        end_date=DEFAULT_LAUNCH_CONFIG.global_config.end,
        capital=DEFAULT_LAUNCH_CONFIG.global_config.capital,
        schedule=DEFAULT_LAUNCH_CONFIG.global_config.schedule,
        fill_mode=DEFAULT_LAUNCH_CONFIG.global_config.fill_mode,
        benchmark_name="Strategy specific benchmarks",
    )
    return DashboardPayloadModel(
        launch=launch,
        mode="single" if len(run_ids) == 1 else "multi",
        selected_run_ids=run_ids,
        available_runs=self.run_index_service.list_runs(),
        metrics={snapshot.run_id: self._serialize_metrics(snapshot) for snapshot in snapshots},
        context={snapshot.run_id: self._serialize_context(snapshot) for snapshot in snapshots},
        rolling=DashboardRollingModel(
            rolling_sharpe=self._serialize_rolling_series(snapshots, "rolling_sharpe"),
            rolling_beta=self._serialize_rolling_series(snapshots, "rolling_beta"),
            rolling_correlation=self._serialize_rolling_series(snapshots, "rolling_correlation"),
        ),
        exposure=DashboardExposureModel(
            holdings_count=[self._serialize_series(snapshot, snapshot.exposure.holdings_count) for snapshot in snapshots],
            latest_holdings={snapshot.run_id: serialize_latest_holdings(snapshot.exposure.latest_holdings) for snapshot in snapshots},
            latest_holdings_leaders={snapshot.run_id: serialize_holding_returns(snapshot.exposure.latest_leaders) for snapshot in snapshots},
            latest_holdings_laggards={snapshot.run_id: serialize_holding_returns(snapshot.exposure.latest_laggards) for snapshot in snapshots},
            sector_weights={snapshot.run_id: serialize_named_values(snapshot.sectors.latest_weighted) for snapshot in snapshots},
        ),
        research=DashboardResearchModel(
            focus=ResearchFocusModel(kind="all-selected", label="All Selected", value=None),
            sector_contribution_method=SECTOR_CONTRIBUTION_METHOD_WEIGHTED_ASSET_RETURNS,
            monthly_heatmap={snapshot.run_id: serialize_heatmap(snapshot.research.monthly_heatmap) for snapshot in snapshots},
            return_distribution={snapshot.run_id: serialize_distribution(snapshot.research.return_distribution) for snapshot in snapshots},
            monthly_return_distribution={
                snapshot.run_id: serialize_distribution(snapshot.research.monthly_return_distribution)
                for snapshot in snapshots
            },
            yearly_excess_returns={
                snapshot.run_id: serialize_named_series(
                    snapshot.research.yearly_excess_returns,
                    run_id=snapshot.run_id,
                    label=snapshot.display_name,
                ).points
                for snapshot in snapshots
            },
            sector_contribution_series={
                snapshot.run_id: serialize_category_series(snapshot.research.sector_contribution) for snapshot in snapshots
            },
            sector_weight_series={
                snapshot.run_id: serialize_category_series(snapshot.research.sector_weights) for snapshot in snapshots
            },
            drawdown_episodes={
                snapshot.run_id: serialize_drawdown_episodes(snapshot.research.drawdown_episodes) for snapshot in snapshots
            },
        ),
    )
```

- [ ] **Step 4: Run the focused backend test suite again**

Run: `pytest tests/dashboard/backend/test_dashboard_api.py -q`
Expected: PASS with the new camelCase payload fields.

- [ ] **Step 5: Commit the payload contract changes**

```bash
git add dashboard/backend/schemas.py dashboard/backend/serializers.py dashboard/backend/services/dashboard_payload.py
git commit -m "feat: expand dashboard analytics api contract"
```

### Task 4: Add failing frontend tests for metadata, rolling risk, distributions, and exposure leaders

**Files:**
- Modify: `dashboard/frontend/src/components/App.test.tsx`
- Modify: `dashboard/frontend/src/lib/types.ts`
- Test: `dashboard/frontend/src/components/App.test.tsx`

- [ ] **Step 1: Extend the frontend fixture payload**

```typescript
function createDashboard(mode: "single" | "multi", selectedRunIds: string[]) {
  return {
    launch: {
      startDate: "2020-01-01",
      endDate: "2025-12-31",
      capital: 100000000,
      schedule: "monthly",
      fillMode: "next_open",
      benchmarkName: "Strategy specific benchmarks",
    },
    rolling: {
      rollingSharpe: [
        { runId: "momentum_run", label: "Momentum", points: [{ date: "2025-01-01", value: 0.8 }] },
        { runId: "value_run", label: "OP Fwd Yield", points: [{ date: "2025-01-01", value: 0.6 }] },
      ],
      rollingBeta: [
        { runId: "momentum_run", label: "Momentum", points: [{ date: "2025-01-01", value: 0.95 }] },
        { runId: "value_run", label: "OP Fwd Yield", points: [{ date: "2025-01-01", value: 0.72 }] },
      ],
      rollingCorrelation: [
        { runId: "momentum_run", label: "Momentum", points: [{ date: "2025-01-01", value: 0.88 }] },
        { runId: "value_run", label: "OP Fwd Yield", points: [{ date: "2025-01-01", value: 0.61 }] },
      ],
    },
    exposure: {
      holdingsCount: [],
      latestHoldings: {},
      sectorWeights: {},
      latestHoldingsLeaders: {
        momentum_run: [{ symbol: "AAPL", targetWeight: 0.34, absWeight: 0.34, rebalanceDate: "2025-02-28", returnSinceRebalance: 0.12 }],
      },
      latestHoldingsLaggards: {
        momentum_run: [{ symbol: "NVDA", targetWeight: 0.18, absWeight: 0.18, rebalanceDate: "2025-02-28", returnSinceRebalance: -0.08 }],
      },
    },
    research: {
      focus: { kind: "all-selected", label: "All Selected", value: null },
      sectorContributionMethod: "weighted-asset-return-attribution",
      monthlyHeatmap: {},
      returnDistribution: {},
      monthlyReturnDistribution: {
        momentum_run: [{ start: -0.05, end: -0.025, count: 1, frequency: 0.2 }],
      },
      yearlyExcessReturns: {},
      sectorContributionSeries: {},
      sectorWeightSeries: {},
      drawdownEpisodes: {},
    },
  };
}
```

- [ ] **Step 2: Add failing metadata and rolling risk expectations**

```typescript
it("renders the launch metadata rail in the comparison plane", async () => {
  fetchRuns.mockResolvedValue(RUNS);
  fetchDashboard.mockResolvedValue(createDashboard("single", ["momentum_run"]));

  render(<App />);

  expect(await screen.findByText("Start 2020-01-01")).toBeInTheDocument();
  expect(screen.getByText("End 2025-12-31")).toBeInTheDocument();
  expect(screen.getByText("Schedule monthly")).toBeInTheDocument();
  expect(screen.getByText("Fill next_open")).toBeInTheDocument();
});
```

```typescript
it("renders rolling sharpe correlation and beta together", async () => {
  fetchRuns.mockResolvedValue(RUNS);
  fetchDashboard.mockResolvedValue(createDashboard("multi", ["momentum_run", "value_run"]));

  render(<App />);

  await screen.findByRole("heading", { name: "Research charts" });
  expect(screen.getByRole("heading", { name: "Rolling risk" })).toBeInTheDocument();
  expect(findChartOption(["Momentum rolling correlation", "OP Fwd Yield rolling beta"])).toBeDefined();
});
```

- [ ] **Step 3: Add failing distribution and exposure expectations**

```typescript
it("renders daily and monthly return distributions as histogram-style charts", async () => {
  fetchRuns.mockResolvedValue(RUNS);
  fetchDashboard.mockResolvedValue(createDashboard("multi", ["momentum_run", "value_run"]));

  render(<App />);

  await screen.findByRole("heading", { name: "Research charts" });
  expect(screen.getByRole("heading", { name: "Daily return distribution" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Monthly return distribution" })).toBeInTheDocument();
});
```

```typescript
it("shows latest-holdings winners and losers panels", async () => {
  fetchRuns.mockResolvedValue(RUNS);
  fetchDashboard.mockResolvedValue(createDashboard("single", ["momentum_run"]));

  render(<App />);

  expect(await screen.findByText("Top winners since latest rebalance")).toBeInTheDocument();
  expect(screen.getByText("Top losers since latest rebalance")).toBeInTheDocument();
  expect(screen.getByText("AAPL")).toBeInTheDocument();
  expect(screen.getByText("NVDA")).toBeInTheDocument();
});
```

- [ ] **Step 4: Run the focused frontend test file and verify it fails**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: FAIL with missing headings, missing payload fields, or chart matchers that do not yet exist.

- [ ] **Step 5: Commit the red frontend tests**

```bash
git add dashboard/frontend/src/components/App.test.tsx dashboard/frontend/src/lib/types.ts
git commit -m "test: cover dashboard analytics frontend refresh"
```

### Task 5: Update frontend types and comparison-plane metadata rendering

**Files:**
- Modify: `dashboard/frontend/src/lib/types.ts`
- Modify: `dashboard/frontend/src/components/TopRail.tsx`
- Modify: `dashboard/frontend/src/components/PerformanceStrip.tsx`
- Modify: `dashboard/frontend/src/app/App.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/App.test.tsx`

- [ ] **Step 1: Add TypeScript types for the new payload shape**

```typescript
export type DashboardLaunch = {
  startDate: string;
  endDate: string;
  capital: number;
  schedule: string;
  fillMode: string;
  benchmarkName: string;
};

export type HoldingReturn = {
  symbol: string;
  targetWeight: number;
  absWeight: number;
  rebalanceDate: string;
  returnSinceRebalance: number;
};
```

```typescript
export type DashboardPayload = {
  launch: DashboardLaunch;
  mode: "single" | "multi";
  selectedRunIds: string[];
  availableRuns: RunOption[];
  metrics: Record<string, DashboardMetric>;
  context: Record<string, DashboardContext>;
  performance: {
    series: NamedSeries[];
    benchmark: SeriesPoint[] | null;
    benchmarks: NamedSeries[];
    drawdowns: NamedSeries[];
  };
  rolling: {
    rollingSharpe: NamedSeries[];
    rollingBeta: NamedSeries[];
    rollingCorrelation: NamedSeries[];
  };
  exposure: {
    holdingsCount: NamedSeries[];
    latestHoldings: Record<string, ExposureHolding[]>;
    latestHoldingsLeaders: Record<string, HoldingReturn[]>;
    latestHoldingsLaggards: Record<string, HoldingReturn[]>;
    sectorWeights: Record<string, CategoryPoint[]>;
  };
  research: {
    focus: DashboardResearchPayloadFocus;
    sectorContributionMethod: string;
    monthlyHeatmap: Record<string, HeatmapCell[]>;
    returnDistribution: Record<string, DistributionBin[]>;
    monthlyReturnDistribution: Record<string, DistributionBin[]>;
    yearlyExcessReturns: Record<string, SeriesPoint[]>;
    sectorContributionSeries: Record<string, CategorySeries[]>;
    sectorWeightSeries: Record<string, CategorySeries[]>;
    drawdownEpisodes: Record<string, DrawdownEpisode[]>;
  };
};
```

- [ ] **Step 2: Pass dashboard launch metadata into the comparison hero**

```tsx
function LaunchMetaRail({ launch, asOfDate }: { launch: DashboardLaunch; asOfDate: string }) {
  return (
    <div className="launch-meta-rail" aria-label="Launch metadata">
      <span className="launch-meta-pill">Start {launch.startDate}</span>
      <span className="launch-meta-pill">End {launch.endDate}</span>
      <span className="launch-meta-pill">Capital {formatMoney(launch.capital)}</span>
      <span className="launch-meta-pill">Schedule {launch.schedule}</span>
      <span className="launch-meta-pill">Fill {launch.fillMode}</span>
      <span className="launch-meta-pill">As of {asOfDate}</span>
    </div>
  );
}
```

- [ ] **Step 3: Add the CSS for the compact metadata rail**

```css
.launch-meta-rail {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.launch-meta-pill {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(247, 240, 231, 0.12);
  background: rgba(247, 240, 231, 0.03);
  color: var(--muted);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
```

- [ ] **Step 4: Run the focused frontend tests and verify the metadata tests pass**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: PASS for metadata/type-related expectations; remaining chart/exposure tests may still fail.

- [ ] **Step 5: Commit the comparison-plane metadata work**

```bash
git add dashboard/frontend/src/lib/types.ts dashboard/frontend/src/components/TopRail.tsx dashboard/frontend/src/components/PerformanceStrip.tsx dashboard/frontend/src/app/App.tsx dashboard/frontend/src/app/dashboard.css
git commit -m "feat: surface dashboard launch metadata"
```

### Task 6: Implement research workspace chart refresh

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/App.test.tsx`

- [ ] **Step 1: Replace the single smoothed distribution with daily and monthly histogram-style figures**

```tsx
function buildDistributionBarOption(dashboard: DashboardPayload, runIds: string[], source: "returnDistribution" | "monthlyReturnDistribution") {
  return {
    backgroundColor: "transparent",
    color: SERIES_COLORS,
    grid: { left: 12, right: 18, top: 36, bottom: 24, containLabel: true },
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    xAxis: { type: "value" as const, axisLabel: { color: "#bdaea1" } },
    yAxis: { type: "value" as const, axisLabel: { color: "#bdaea1" } },
    series: runIds.map((runId) => ({
      name: runLabel(dashboard, runId),
      type: "bar" as const,
      barGap: "8%",
      data: (dashboard.research[source][runId] ?? []).map((bin) => [distributionMidpoint(bin), bin.frequency]),
    })),
  };
}
```

```tsx
<ResearchFigure
  title="Daily return distribution"
  subtitle="Visible return bins for daily observations."
  option={buildDistributionBarOption(dashboard, runIds, "returnDistribution")}
  isEmpty={!hasDistributionData(dashboard, runIds)}
  emptyMessage="No daily return distribution data."
/>
<ResearchFigure
  title="Monthly return distribution"
  subtitle="Visible return bins for compounded monthly observations."
  option={buildDistributionBarOption(dashboard, runIds, "monthlyReturnDistribution")}
  isEmpty={!runIds.some((runId) => (dashboard.research.monthlyReturnDistribution[runId] ?? []).length > 0)}
  emptyMessage="No monthly return distribution data."
/>
```

- [ ] **Step 2: Combine Sharpe, correlation, and beta into the rolling risk section**

```tsx
const rollingRiskSeries = dashboard.rolling.rollingSharpe
  .filter((series) => runIds.includes(series.runId))
  .map((series) => ({ runId: series.runId, label: `${series.label} rolling sharpe`, points: series.points }))
  .concat(
    dashboard.rolling.rollingCorrelation
      .filter((series) => runIds.includes(series.runId))
      .map((series) => ({ runId: series.runId, label: `${series.label} rolling correlation`, points: series.points })),
  )
  .concat(
    dashboard.rolling.rollingBeta
      .filter((series) => runIds.includes(series.runId))
      .map((series) => ({ runId: series.runId, label: `${series.label} rolling beta`, points: series.points })),
  );
```

```tsx
<ResearchFigure
  title="Rolling risk"
  subtitle="Sharpe, correlation, and beta over the same rolling window."
  option={buildLineOption(rollingRiskSeries, (series) => series.label, (value) => formatNumberValue(value), (value) => formatNumberValue(value, 1))}
  isEmpty={!hasSeriesData(rollingRiskSeries)}
  emptyMessage="No rolling risk data."
/>
```

- [ ] **Step 3: Repair yearly excess and preserve sector charts while adding a donut**

```tsx
function buildYearlyExcessOption(dashboard: DashboardPayload, runIds: string[]) {
  const years = Array.from(
    new Set(runIds.flatMap((runId) => (dashboard.research.yearlyExcessReturns[runId] ?? []).map((point) => point.date.slice(0, 4)))),
  ).sort();
  return {
    backgroundColor: "transparent",
    color: SERIES_COLORS,
    grid: { left: 12, right: 18, top: 36, bottom: 24, containLabel: true },
    xAxis: { type: "category" as const, data: years, axisLabel: { color: "#bdaea1" } },
    series: runIds.map((runId) => ({
      name: runLabel(dashboard, runId),
      type: "bar" as const,
      data: years.map((year) => {
        const point = (dashboard.research.yearlyExcessReturns[runId] ?? []).find((entry) => entry.date.startsWith(year));
        return point ? point.value : null;
      }),
    })),
  };
}
```

```tsx
function buildSectorDonutOption(points: CategoryPoint[]) {
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    series: [
      {
        name: "Latest sector weights",
        type: "pie" as const,
        radius: ["48%", "72%"],
        data: points.map((point) => ({ name: point.name, value: point.value })),
      },
    ],
  };
}
```

- [ ] **Step 4: Run the focused frontend tests and verify the research workspace passes**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: PASS for distribution, rolling risk, yearly excess, and preserved sector chart assertions.

- [ ] **Step 5: Commit the research workspace refresh**

```bash
git add dashboard/frontend/src/components/ResearchWorkspace.tsx dashboard/frontend/src/app/dashboard.css dashboard/frontend/src/components/App.test.tsx
git commit -m "feat: refresh dashboard research charts"
```

### Task 7: Implement exposure-band winners, losers, and sector snapshot

**Files:**
- Modify: `dashboard/frontend/src/components/ExposureBand.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/App.test.tsx`

- [ ] **Step 1: Render latest holdings plus winners and losers per run**

```tsx
const leaders = dashboard.exposure.latestHoldingsLeaders[runId] ?? [];
const laggards = dashboard.exposure.latestHoldingsLaggards[runId] ?? [];
```

```tsx
<div className="detail-subsection">
  <div className="detail-subsection-head">
    <span>Top winners since latest rebalance</span>
    <span>{leaders.length} lines</span>
  </div>
  <div className="detail-list">
    {leaders.map((holding) => (
      <div key={`${holding.symbol}-winner`} className="detail-list-row">
        <strong>{holding.symbol}</strong>
        <span>{formatPercent(holding.returnSinceRebalance)}</span>
        <span>{holding.rebalanceDate}</span>
      </div>
    ))}
  </div>
</div>
```

```tsx
<div className="detail-subsection">
  <div className="detail-subsection-head">
    <span>Top losers since latest rebalance</span>
    <span>{laggards.length} lines</span>
  </div>
  <div className="detail-list">
    {laggards.map((holding) => (
      <div key={`${holding.symbol}-loser`} className="detail-list-row">
        <strong>{holding.symbol}</strong>
        <span>{formatPercent(holding.returnSinceRebalance)}</span>
        <span>{holding.rebalanceDate}</span>
      </div>
    ))}
  </div>
</div>
```

- [ ] **Step 2: Add a latest sector snapshot chart or compact summary next to the lists**

```tsx
<div className="detail-subsection detail-subsection--chart">
  <div className="detail-subsection-head">
    <span>Latest sector mix</span>
    <span>{visibleSectors.length} sectors</span>
  </div>
  <EChartsReact option={buildSectorDonutOption(visibleSectors)} style={{ height: 220, width: "100%" }} />
</div>
```

- [ ] **Step 3: Add the supporting CSS for the leaderboard blocks**

```css
.detail-subsection--chart {
  min-height: 280px;
}

.detail-list-row--returns {
  grid-template-columns: minmax(0, 1fr) auto auto;
}
```

- [ ] **Step 4: Run the focused frontend tests and verify the exposure expectations pass**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: PASS for winners/losers and latest sector snapshot assertions.

- [ ] **Step 5: Commit the exposure-band work**

```bash
git add dashboard/frontend/src/components/ExposureBand.tsx dashboard/frontend/src/app/dashboard.css dashboard/frontend/src/components/App.test.tsx
git commit -m "feat: add dashboard holdings leaders and laggards"
```

### Task 8: Full verification and finish

**Files:**
- Modify: `README.md` only if the visible dashboard behavior needs a brief note after implementation

- [ ] **Step 1: Run the backend verification suite**

Run: `pytest tests/dashboard/backend/test_dashboard_api.py tests/dashboard/test_run.py -q`
Expected: PASS

- [ ] **Step 2: Run the frontend focused suite**

Run: `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
Expected: PASS

- [ ] **Step 3: Run the frontend build**

Run: `cd dashboard/frontend && npm run build`
Expected: build completes successfully and outputs `dist/` assets without type or bundling errors.

- [ ] **Step 4: Run the broader dashboard verification**

Run: `pytest tests/dashboard -q`
Expected: PASS

- [ ] **Step 5: Commit the verification or doc touch-ups**

```bash
git add README.md docs/superpowers/plans/2026-04-06-dashboard-analytics-refresh.md
git commit -m "docs: finalize dashboard analytics refresh plan"
```

## Self-Review

**Spec coverage**

- Launch metadata visibility: covered by Tasks 1, 3, and 5.
- Daily and monthly distributions: covered by Tasks 1, 2, 3, 4, and 6.
- Rolling correlation alongside Sharpe and beta: covered by Tasks 1, 2, 3, 4, and 6.
- Latest holdings winners and losers using the latest rebalance cohort: covered by Tasks 1, 2, 3, 4, and 7.
- Preserved sector contribution and sector weight analytics plus donut: covered by Tasks 3, 6, and 7.
- Yearly excess return repair: covered by Tasks 3 and 6.

**Placeholder scan**

- No placeholder markers or shorthand cross-task references remain.
- Each execution task names the files, focused test command, and commit boundary.

**Type consistency**

- Backend names use `rolling_correlation`, `monthly_return_distribution`, `latest_holdings_leaders`, and `latest_holdings_laggards`.
- Frontend names use the matching camelCase forms `rollingCorrelation`, `monthlyReturnDistribution`, `latestHoldingsLeaders`, and `latestHoldingsLaggards`.
