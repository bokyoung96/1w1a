export type RunSummary = {
  final_equity: number;
  avg_turnover: number;
};

export type RunOption = {
  run_id: string;
  label: string;
  strategy: string;
  start?: string;
  end?: string;
  summary: RunSummary;
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

export type DashboardMetric = {
  label: string;
  cumulativeReturn: number;
  cagr: number;
  annualVolatility: number;
  sharpe: number;
  sortino: number;
  calmar: number;
  maxDrawdown: number;
  finalEquity: number;
  avgTurnover: number;
  alpha: number;
  beta: number;
  trackingError: number;
  informationRatio: number;
};

export type DashboardContext = {
  label: string;
  strategy: string;
  benchmark: {
    code: string;
    name: string;
  };
  startDate: string;
  endDate: string;
  asOfDate: string;
};

export type DashboardPayload = {
  mode: "single" | "multi";
  selectedRunIds: string[];
  availableRuns: RunOption[];
  metrics: Record<string, DashboardMetric>;
  context: Record<string, DashboardContext>;
  performance: {
    series: NamedSeries[];
    benchmark: SeriesPoint[] | null;
    drawdowns: NamedSeries[];
  };
  rolling: {
    rollingSharpe: NamedSeries[];
    rollingBeta: NamedSeries[];
  };
  exposure: {
    holdingsCount: NamedSeries[];
    latestHoldings: Record<
      string,
      {
        symbol: string;
        targetWeight: number;
        absWeight: number;
      }[]
    >;
    sectorWeights: Record<
      string,
      {
        name: string;
        value: number;
      }[]
    >;
  };
};
