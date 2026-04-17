import type {
  BenchmarkOption,
  CategoryPoint,
  CategorySeries,
  DashboardContext,
  DashboardLaunch,
  DashboardMetric,
  DashboardPayload,
  DistributionBin,
  DrawdownEpisode,
  ExposureHolding,
  HeatmapCell,
  HoldingPerformance,
  LaunchBenchmarkContext,
  NamedSeries,
  RollingSeries,
  RunOption,
  SeriesPoint,
  SessionBootstrap,
} from "./types";

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_ROOT?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

const API_ROOT = import.meta.env.VITE_API_ROOT ?? "/api";

function asRecord(value: unknown) {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function asString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function normalizeSessionBootstrap(value: unknown): SessionBootstrap {
  const candidate = asRecord(value).defaultSelectedRunIds;
  if (!Array.isArray(candidate)) {
    return { defaultSelectedRunIds: [] };
  }

  return {
    defaultSelectedRunIds: candidate.filter((runId): runId is string => typeof runId === "string"),
  };
}

function normalizeRunOption(value: unknown): RunOption {
  const candidate = asRecord(value);
  const summary = asRecord(candidate.summary);

  return {
    run_id: asString(candidate.run_id || candidate.runId),
    label: asString(candidate.label),
    strategy: asString(candidate.strategy),
    start: typeof candidate.start === "string" ? candidate.start : undefined,
    end: typeof candidate.end === "string" ? candidate.end : undefined,
    summary: {
      finalEquity: asNumber(summary.final_equity ?? summary.finalEquity),
      avgTurnover: asNumber(summary.avg_turnover ?? summary.avgTurnover),
    },
  };
}

function normalizePoint(value: unknown): SeriesPoint {
  const candidate = asRecord(value);

  return {
    date: asString(candidate.date),
    value: asNumber(candidate.value),
  };
}

function normalizeNamedSeries(value: unknown): NamedSeries {
  const candidate = asRecord(value);

  return {
    runId: asString(candidate.run_id ?? candidate.runId),
    label: asString(candidate.label),
    points: Array.isArray(candidate.points) ? candidate.points.map(normalizePoint) : [],
  };
}

function normalizeBenchmarkOption(value: unknown): BenchmarkOption {
  const candidate = asRecord(value);

  return {
    code: asString(candidate.code),
    name: asString(candidate.name),
  };
}

function normalizeRollingSeries(value: unknown): RollingSeries {
  const candidate = asRecord(value);

  return {
    ...normalizeNamedSeries(value),
    benchmark: normalizeBenchmarkOption(candidate.benchmark),
    window: asNumber(candidate.window),
  };
}

function normalizeCategorySeries(value: unknown): CategorySeries {
  const candidate = asRecord(value);

  return {
    name: asString(candidate.name),
    points: Array.isArray(candidate.points) ? candidate.points.map(normalizePoint) : [],
  };
}

function normalizeCategoryPoint(value: unknown): CategoryPoint {
  const candidate = asRecord(value);

  return {
    name: asString(candidate.name),
    value: asNumber(candidate.value),
  };
}

function normalizeHolding(value: unknown): ExposureHolding {
  const candidate = asRecord(value);

  return {
    symbol: asString(candidate.symbol),
    targetWeight: asNumber(candidate.target_weight ?? candidate.targetWeight),
    absWeight: asNumber(candidate.abs_weight ?? candidate.absWeight),
  };
}

function normalizeHoldingPerformance(value: unknown): HoldingPerformance {
  const candidate = asRecord(value);

  return {
    ...normalizeHolding(value),
    returnSinceLatestRebalance: asNumber(
      candidate.return_since_latest_rebalance ?? candidate.returnSinceLatestRebalance,
    ),
  };
}

function normalizeLaunchBenchmarkContext(value: unknown): LaunchBenchmarkContext | null {
  const candidate = asRecord(value);
  if (Object.keys(candidate).length === 0) {
    return null;
  }

  const strategies = Array.isArray(candidate.strategies)
    ? candidate.strategies.map((entry) => {
        const strategy = asRecord(entry);
        return {
          strategy: asString(strategy.strategy),
          label: asString(strategy.label),
          benchmark: normalizeBenchmarkOption(strategy.benchmark),
        };
      })
    : [];

  return {
    kind: asString(candidate.kind),
    shared: candidate.shared == null ? null : normalizeBenchmarkOption(candidate.shared),
    strategies,
  };
}

function normalizeLaunch(value: unknown): DashboardLaunch {
  const candidate = asRecord(value);

  return {
    configuredStartDate:
      candidate.configured_start_date == null && candidate.configuredStartDate == null
        ? null
        : asString(candidate.configured_start_date ?? candidate.configuredStartDate),
    configuredEndDate:
      candidate.configured_end_date == null && candidate.configuredEndDate == null
        ? null
        : asString(candidate.configured_end_date ?? candidate.configuredEndDate),
    capital:
      candidate.capital == null
        ? null
        : asNumber(candidate.capital),
    schedule:
      candidate.schedule == null
        ? null
        : asString(candidate.schedule),
    fillMode:
      candidate.fill_mode == null && candidate.fillMode == null
        ? null
        : asString(candidate.fill_mode ?? candidate.fillMode),
    benchmark: normalizeLaunchBenchmarkContext(candidate.benchmark),
    fee: candidate.fee == null ? null : asNumber(candidate.fee),
    sellTax:
      candidate.sell_tax == null && candidate.sellTax == null
        ? null
        : asNumber(candidate.sell_tax ?? candidate.sellTax),
    slippage: candidate.slippage == null ? null : asNumber(candidate.slippage),
    asOfDate:
      candidate.as_of_date == null && candidate.asOfDate == null
        ? null
        : asString(candidate.as_of_date ?? candidate.asOfDate),
  };
}

function normalizeMetric(value: unknown, runId: string): DashboardMetric {
  const candidate = asRecord(value);

  return {
    label: asString(candidate.label) || runId,
    cumulativeReturn: asNumber(candidate.cumulative_return ?? candidate.cumulativeReturn),
    cagr: asNumber(candidate.cagr),
    annualVolatility: asNumber(candidate.annual_volatility ?? candidate.annualVolatility),
    sharpe: asNumber(candidate.sharpe),
    sortino: asNumber(candidate.sortino),
    calmar: asNumber(candidate.calmar),
    maxDrawdown: asNumber(candidate.max_drawdown ?? candidate.maxDrawdown),
    avgTurnover: asNumber(candidate.avg_turnover ?? candidate.avgTurnover),
    finalEquity: asNumber(candidate.final_equity ?? candidate.finalEquity),
    alpha: asNumber(candidate.alpha),
    beta: asNumber(candidate.beta),
    trackingError: asNumber(candidate.tracking_error ?? candidate.trackingError),
    informationRatio: asNumber(candidate.information_ratio ?? candidate.informationRatio),
  };
}

function normalizeContext(value: unknown): DashboardContext {
  const candidate = asRecord(value);
  const benchmark = asRecord(candidate.benchmark);

  return {
    label: asString(candidate.label),
    strategy: asString(candidate.strategy),
    benchmark: {
      code: asString(benchmark.code),
      name: asString(benchmark.name),
    },
    startDate: asString(candidate.start_date ?? candidate.startDate),
    endDate: asString(candidate.end_date ?? candidate.endDate),
    asOfDate: asString(candidate.as_of_date ?? candidate.asOfDate),
  };
}

function normalizeHeatmapCell(value: unknown): HeatmapCell {
  const candidate = asRecord(value);

  return {
    year: asNumber(candidate.year),
    month: asNumber(candidate.month),
    value: asNumber(candidate.value),
  };
}

function normalizeDistributionBin(value: unknown): DistributionBin {
  const candidate = asRecord(value);

  return {
    start: asNumber(candidate.start),
    end: asNumber(candidate.end),
    count: asNumber(candidate.count),
    frequency: asNumber(candidate.frequency),
  };
}

function normalizeDrawdownEpisode(value: unknown): DrawdownEpisode {
  const candidate = asRecord(value);

  return {
    peak: asString(candidate.peak),
    start: asString(candidate.start),
    trough: asString(candidate.trough),
    end: asString(candidate.end),
    drawdown: asNumber(candidate.drawdown),
    durationDays: asNumber(candidate.duration_days ?? candidate.durationDays),
    timeToTroughDays: asNumber(candidate.time_to_trough_days ?? candidate.timeToTroughDays),
    recoveryDays:
      candidate.recovery_days == null && candidate.recoveryDays == null
        ? null
        : asNumber(candidate.recovery_days ?? candidate.recoveryDays),
    recovered: Boolean(candidate.recovered),
  };
}

function normalizeRecordArray<T>(value: unknown, normalizeItem: (item: unknown) => T) {
  const candidate = asRecord(value);

  return Object.fromEntries(
    Object.entries(candidate).map(([key, entry]) => [key, Array.isArray(entry) ? entry.map(normalizeItem) : []]),
  ) as Record<string, T[]>;
}

function normalizeDashboardPayload(value: unknown): DashboardPayload {
  const candidate = asRecord(value);
  const metricsInput = asRecord(candidate.metrics);
  const contextInput = asRecord(candidate.context);
  const performance = asRecord(candidate.performance);
  const rolling = asRecord(candidate.rolling);
  const exposure = asRecord(candidate.exposure);
  const research = asRecord(candidate.research);
  const rollingSharpeInput = rolling.rolling_sharpe ?? rolling.rollingSharpe;
  const rollingBetaInput = rolling.rolling_beta ?? rolling.rollingBeta;
  const rollingCorrelationInput = rolling.rolling_correlation ?? rolling.rollingCorrelation;
  const holdingsCountInput = exposure.holdings_count ?? exposure.holdingsCount;

  return {
    mode: candidate.mode === "multi" ? "multi" : "single",
    selectedRunIds: Array.isArray(candidate.selectedRunIds)
      ? candidate.selectedRunIds.filter((runId): runId is string => typeof runId === "string")
      : [],
    availableRuns: Array.isArray(candidate.availableRuns) ? candidate.availableRuns.map(normalizeRunOption) : [],
    launch: normalizeLaunch(candidate.launch),
    metrics: Object.fromEntries(
      Object.entries(metricsInput).map(([runId, entry]) => [runId, normalizeMetric(entry, runId)]),
    ),
    context: Object.fromEntries(
      Object.entries(contextInput).map(([runId, entry]) => [runId, normalizeContext(entry)]),
    ),
    performance: {
      series: Array.isArray(performance.series) ? performance.series.map(normalizeNamedSeries) : [],
      benchmark: Array.isArray(performance.benchmark) ? performance.benchmark.map(normalizePoint) : null,
      benchmarks: Array.isArray(performance.benchmarks) ? performance.benchmarks.map(normalizeNamedSeries) : [],
      drawdowns: Array.isArray(performance.drawdowns) ? performance.drawdowns.map(normalizeNamedSeries) : [],
    },
    rolling: {
      rollingSharpe: Array.isArray(rollingSharpeInput) ? rollingSharpeInput.map(normalizeNamedSeries) : [],
      rollingBeta: Array.isArray(rollingBetaInput) ? rollingBetaInput.map(normalizeNamedSeries) : [],
      rollingCorrelation: Array.isArray(rollingCorrelationInput)
        ? rollingCorrelationInput.map(normalizeRollingSeries)
        : [],
    },
    exposure: {
      holdingsCount: Array.isArray(holdingsCountInput) ? holdingsCountInput.map(normalizeNamedSeries) : [],
      latestHoldings: normalizeRecordArray(exposure.latest_holdings ?? exposure.latestHoldings, normalizeHolding),
      latestHoldingsWinners: normalizeRecordArray(
        exposure.latest_holdings_winners ?? exposure.latestHoldingsWinners,
        normalizeHoldingPerformance,
      ),
      latestHoldingsLosers: normalizeRecordArray(
        exposure.latest_holdings_losers ?? exposure.latestHoldingsLosers,
        normalizeHoldingPerformance,
      ),
      sectorWeights: normalizeRecordArray(exposure.sector_weights ?? exposure.sectorWeights, normalizeCategoryPoint),
    },
    research: {
      focus: {
        kind: asString(research.focus && asRecord(research.focus).kind) || "all-selected",
        label: asString(research.focus && asRecord(research.focus).label) || "All Selected",
        value: (() => {
          const focusValue = research.focus && asRecord(research.focus).value;
          return typeof focusValue === "string" ? focusValue : null;
        })(),
      },
      sectorContributionMethod: asString(
        research.sector_contribution_method ?? research.sectorContributionMethod,
      ),
      monthlyHeatmap: normalizeRecordArray(research.monthly_heatmap ?? research.monthlyHeatmap, normalizeHeatmapCell),
      returnDistribution: normalizeRecordArray(
        research.return_distribution ?? research.returnDistribution,
        normalizeDistributionBin,
      ),
      monthlyReturnDistribution: normalizeRecordArray(
        research.monthly_return_distribution ?? research.monthlyReturnDistribution,
        normalizeDistributionBin,
      ),
      yearlyExcessReturns: normalizeRecordArray(
        research.yearly_excess_returns ?? research.yearlyExcessReturns,
        normalizePoint,
      ),
      sectorContributionSeries: normalizeRecordArray(
        research.sector_contribution_series ?? research.sectorContributionSeries,
        normalizeCategorySeries,
      ),
      sectorWeightSeries: normalizeRecordArray(
        research.sector_weight_series ?? research.sectorWeightSeries,
        normalizeCategorySeries,
      ),
      drawdownEpisodes: normalizeRecordArray(
        research.drawdown_episodes ?? research.drawdownEpisodes,
        normalizeDrawdownEpisode,
      ),
    },
  };
}

export async function fetchRuns(): Promise<RunOption[]> {
  const response = await fetch(`${API_ROOT}/runs`);
  if (!response.ok) {
    throw new Error(`Failed to load runs: ${response.status}`);
  }

  const payload = await response.json();
  return Array.isArray(payload) ? payload.map(normalizeRunOption) : [];
}

export async function fetchSession(): Promise<SessionBootstrap> {
  const response = await fetch(`${API_ROOT}/session`);
  if (!response.ok) {
    throw new Error(`Failed to load session: ${response.status}`);
  }

  return normalizeSessionBootstrap(await response.json());
}

export async function fetchDashboard(runIds: string[]): Promise<DashboardPayload> {
  const query = new URLSearchParams();
  runIds.forEach((runId) => query.append("run_ids", runId));

  const response = await fetch(`${API_ROOT}/dashboard?${query.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to load dashboard: ${response.status}`);
  }

  return normalizeDashboardPayload(await response.json());
}
