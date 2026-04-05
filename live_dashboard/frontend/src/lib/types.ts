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
  key: string;
  name: string;
  points: SeriesPoint[];
};

export type DashboardPayload = {
  mode: "single" | "multi";
  selectedRunIds: string[];
  availableRuns: RunOption[];
  metrics: Record<
    string,
    {
      cagr: number;
      sharpe: number;
      max_drawdown: number;
      avg_turnover: number;
      final_equity: number;
    }
  >;
  context: Record<
    string,
    {
      name?: string;
      strategy?: string;
      start?: string;
      end?: string;
      validation?: object | null;
    }
  >;
  performance: {
    series: NamedSeries[];
    benchmark: NamedSeries | null;
    drawdowns: NamedSeries[];
  };
  rolling: {
    rollingSharpe: NamedSeries[];
    rollingBeta: NamedSeries[];
  };
  exposure: {
    holdingsCount: NamedSeries[];
    latestHoldings: Record<string, { symbol: string; target_weight: number }[]>;
    sectorWeights: Record<string, Record<string, number>>;
  };
};
