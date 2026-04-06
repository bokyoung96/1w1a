export type RunSummary = {
  finalEquity: number;
  avgTurnover: number;
};

export type RunOption = {
  run_id: string;
  label: string;
  strategy: string;
  start?: string;
  end?: string;
  summary: RunSummary;
};

export type SessionBootstrap = {
  defaultSelectedRunIds: string[];
};

export type SeriesPoint = {
  date: string;
  value: number;
};

export type NamedSeries = {
  runId: string;
  label: string;
  points: SeriesPoint[];
};

export type RollingSeries = NamedSeries & {
  benchmark: BenchmarkOption;
  window: number;
};

export type CategorySeries = {
  name: string;
  points: SeriesPoint[];
};

export type ExposureHolding = {
  symbol: string;
  targetWeight: number;
  absWeight: number;
};

export type HoldingPerformance = ExposureHolding & {
  returnSinceLatestRebalance: number;
};

export type CategoryPoint = {
  name: string;
  value: number;
};

export type BenchmarkOption = {
  code: string;
  name: string;
};

export type LaunchStrategyBenchmark = {
  strategy: string;
  label: string;
  benchmark: BenchmarkOption;
};

export type LaunchBenchmarkContext = {
  kind: string;
  shared: BenchmarkOption | null;
  strategies: LaunchStrategyBenchmark[];
};

export type DashboardLaunch = {
  configuredStartDate: string | null;
  configuredEndDate: string | null;
  capital: number | null;
  schedule: string | null;
  fillMode: string | null;
  benchmark: LaunchBenchmarkContext | null;
  asOfDate: string | null;
};

export type DashboardMetric = {
  label: string;
  cumulativeReturn: number;
  cagr: number;
  annualVolatility: number;
  sharpe: number;
  sortino: number;
  calmar: number;
  maxDrawdown: number;
  avgTurnover: number;
  finalEquity: number;
  alpha: number;
  beta: number;
  trackingError: number;
  informationRatio: number;
};

export type DashboardContext = {
  label: string;
  strategy: string;
  benchmark: BenchmarkOption;
  startDate: string;
  endDate: string;
  asOfDate: string;
};

export type HeatmapCell = {
  year: number;
  month: number;
  value: number;
};

export type DistributionBin = {
  start: number;
  end: number;
  count: number;
  frequency: number;
};

export type DrawdownEpisode = {
  peak: string;
  start: string;
  trough: string;
  end: string;
  drawdown: number;
  durationDays: number;
  timeToTroughDays: number;
  recoveryDays: number | null;
  recovered: boolean;
};

export type DashboardResearchPayloadFocus = {
  kind: string;
  label: string;
  value: string | null;
};

export type ResearchFocus =
  | { kind: "all-selected" }
  | { kind: "strategy"; runId: string }
  | { kind: "sector"; sectorName: string };

export type DashboardPayload = {
  mode: "single" | "multi";
  selectedRunIds: string[];
  availableRuns: RunOption[];
  launch: DashboardLaunch;
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
    rollingCorrelation: RollingSeries[];
  };
  exposure: {
    holdingsCount: NamedSeries[];
    latestHoldings: Record<string, ExposureHolding[]>;
    latestHoldingsWinners: Record<string, HoldingPerformance[]>;
    latestHoldingsLosers: Record<string, HoldingPerformance[]>;
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
