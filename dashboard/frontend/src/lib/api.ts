import type { DashboardPayload, RunOption, SessionBootstrap } from "./types";

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_ROOT?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

const API_ROOT = import.meta.env.VITE_API_ROOT ?? "/api";

function normalizeSessionBootstrap(value: unknown): SessionBootstrap {
  if (!value || typeof value !== "object") {
    return { defaultSelectedRunIds: [] };
  }

  const candidate = (value as { defaultSelectedRunIds?: unknown }).defaultSelectedRunIds;
  if (!Array.isArray(candidate)) {
    return { defaultSelectedRunIds: [] };
  }

  return {
    defaultSelectedRunIds: candidate.filter((runId): runId is string => typeof runId === "string"),
  };
}

function normalizeRunOption(value: unknown): RunOption {
  const candidate = value && typeof value === "object" ? (value as Record<string, unknown>) : {};
  const summary = candidate.summary && typeof candidate.summary === "object" ? (candidate.summary as Record<string, unknown>) : {};

  return {
    run_id:
      typeof candidate.run_id === "string"
        ? candidate.run_id
        : typeof candidate.runId === "string"
          ? candidate.runId
          : "",
    label: typeof candidate.label === "string" ? candidate.label : "",
    strategy: typeof candidate.strategy === "string" ? candidate.strategy : "",
    start: typeof candidate.start === "string" ? candidate.start : undefined,
    end: typeof candidate.end === "string" ? candidate.end : undefined,
    summary: {
      final_equity:
        typeof summary.final_equity === "number"
          ? summary.final_equity
          : typeof summary.finalEquity === "number"
            ? summary.finalEquity
            : 0,
      avg_turnover:
        typeof summary.avg_turnover === "number"
          ? summary.avg_turnover
          : typeof summary.avgTurnover === "number"
            ? summary.avgTurnover
            : 0,
    },
  };
}

function normalizeDashboardPayload(value: unknown): DashboardPayload {
  const candidate = value && typeof value === "object" ? (value as Record<string, unknown>) : {};
  const availableRuns = Array.isArray(candidate.availableRuns) ? candidate.availableRuns.map(normalizeRunOption) : [];
  const metricsInput = candidate.metrics && typeof candidate.metrics === "object" ? (candidate.metrics as Record<string, unknown>) : {};
  const metrics = Object.fromEntries(
    Object.entries(metricsInput).map(([runId, metric]) => {
      const entry = metric && typeof metric === "object" ? (metric as Record<string, unknown>) : {};
      return [
        runId,
        {
          label: typeof entry.label === "string" ? entry.label : runId,
          cagr: typeof entry.cagr === "number" ? entry.cagr : 0,
          sharpe: typeof entry.sharpe === "number" ? entry.sharpe : 0,
          max_drawdown:
            typeof entry.max_drawdown === "number"
              ? entry.max_drawdown
              : typeof entry.maxDrawdown === "number"
                ? entry.maxDrawdown
                : 0,
          avg_turnover:
            typeof entry.avg_turnover === "number"
              ? entry.avg_turnover
              : typeof entry.avgTurnover === "number"
                ? entry.avgTurnover
                : 0,
          final_equity:
            typeof entry.final_equity === "number"
              ? entry.final_equity
              : typeof entry.finalEquity === "number"
                ? entry.finalEquity
                : 0,
        },
      ];
    }),
  );

  return {
    mode: candidate.mode === "multi" ? "multi" : "single",
    selectedRunIds: Array.isArray(candidate.selectedRunIds)
      ? candidate.selectedRunIds.filter((runId): runId is string => typeof runId === "string")
      : [],
    availableRuns,
    metrics,
    context:
      candidate.context && typeof candidate.context === "object"
        ? (candidate.context as DashboardPayload["context"])
        : {},
    performance:
      candidate.performance && typeof candidate.performance === "object"
        ? (candidate.performance as DashboardPayload["performance"])
        : { series: [], benchmark: null, drawdowns: [] },
    rolling:
      candidate.rolling && typeof candidate.rolling === "object"
        ? (candidate.rolling as DashboardPayload["rolling"])
        : { rollingSharpe: [], rollingBeta: [] },
    exposure:
      candidate.exposure && typeof candidate.exposure === "object"
        ? (candidate.exposure as DashboardPayload["exposure"])
        : { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
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
