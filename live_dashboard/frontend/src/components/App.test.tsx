import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { fetchRuns, fetchDashboard } = vi.hoisted(() => ({
  fetchRuns: vi.fn(),
  fetchDashboard: vi.fn(),
}));

const chartOptions: unknown[] = [];

vi.mock("../lib/api", () => ({
  fetchRuns,
  fetchDashboard,
}));

vi.mock("echarts-for-react", () => ({
  default: (props: { option?: unknown }) => {
    chartOptions.push(props.option);

    return <div data-testid="chart" />;
  },
}));

import { App } from "../app/App";

const RUNS = [
  {
    run_id: "momentum_run",
    label: "Momentum",
    strategy: "momentum",
    summary: { final_equity: 100000000, avg_turnover: 0.12 },
  },
  {
    run_id: "value_run",
    label: "OP Fwd Yield",
    strategy: "op_fwd_yield",
    summary: { final_equity: 105000000, avg_turnover: 0.2 },
  },
];

function createDashboard(mode: "single" | "multi", selectedRunIds: string[]) {
  return {
    mode,
    selectedRunIds,
    availableRuns: RUNS,
    metrics:
      mode === "single"
        ? {
            momentum_run: {
              cagr: 0.16,
              sharpe: 1.28,
              max_drawdown: -0.08,
              avg_turnover: 0.12,
              final_equity: 112000000,
            },
          }
    : {
            momentum_run: {
              cagr: 0.13,
              sharpe: 1.05,
              max_drawdown: -0.12,
              avg_turnover: 0.12,
              final_equity: 108000000,
            },
            value_run: {
              cagr: 0.09,
              sharpe: 0.82,
              max_drawdown: -0.06,
              avg_turnover: 0.2,
              final_equity: 103000000,
            },
          },
    context:
      mode === "single"
        ? {
            momentum_run: {
              label: "Momentum",
              strategy: "momentum",
              benchmark: { code: "KOSPI200", name: "KOSPI200 benchmark" },
              startDate: "2020-01-01",
              endDate: "2020-12-31",
              asOfDate: "2020-12-31",
            },
          }
        : {
            momentum_run: {
              label: "Momentum",
              strategy: "momentum",
              benchmark: { code: "KOSPI200", name: "KOSPI200 benchmark" },
              startDate: "2020-01-01",
              endDate: "2020-12-31",
              asOfDate: "2020-12-31",
            },
            value_run: {
              label: "OP Fwd Yield",
              strategy: "op_fwd_yield",
              benchmark: { code: "KOSPI200", name: "KOSPI200 benchmark" },
              startDate: "2020-01-01",
              endDate: "2020-12-31",
              asOfDate: "2020-12-31",
            },
          },
    rolling:
      mode === "single"
        ? {
            rollingSharpe: [
              {
                runId: "momentum_run",
                label: "Rolling Sharpe",
                points: [
                  { date: "2025-01-01", value: 0.12 },
                  { date: "2025-01-02", value: 0.18 },
                ],
              },
            ],
            rollingBeta: [
              {
                runId: "momentum_run",
                label: "Rolling Beta",
                points: [
                  { date: "2025-01-01", value: 0.92 },
                  { date: "2025-01-02", value: 0.96 },
                ],
              },
            ],
          }
        : {
            rollingSharpe: [],
            rollingBeta: [],
          },
    exposure:
      mode === "single"
        ? {
            holdingsCount: [
              {
                runId: "momentum_run",
                label: "Momentum",
                points: [
                  { date: "2025-01-01", value: 2.0 },
                  { date: "2025-01-02", value: 3.0 },
                ],
              },
            ],
            latestHoldings: {
              momentum_run: [
                { symbol: "AAPL", targetWeight: 0.6, absWeight: 0.6 },
                { symbol: "MSFT", targetWeight: 0.4, absWeight: 0.4 },
              ],
            },
            sectorWeights: {
              momentum_run: [
                { name: "Tech", value: 0.72 },
                { name: "Financials", value: 0.28 },
              ],
            },
          }
        : {
            holdingsCount: [],
            latestHoldings: {},
            sectorWeights: {},
          },
    performance:
      mode === "single"
        ? {
            series: [
              {
                runId: "momentum_run",
                label: "Momentum equity",
                points: [
                  { date: "2025-01-01", value: 100000000 },
                  { date: "2025-01-02", value: 100900000 },
                ],
              },
            ],
            benchmark: [
              { date: "2025-01-01", value: 100000000 },
              { date: "2025-01-02", value: 100500000 },
            ],
            drawdowns: [],
          }
        : {
            series: [
              {
                runId: "momentum_run",
                label: "Momentum equity",
                points: [
                  { date: "2025-01-01", value: 100000000 },
                  { date: "2025-01-02", value: 100700000 },
                ],
              },
              {
                runId: "value_run",
                label: "OP Fwd Yield equity",
                points: [
                  { date: "2025-01-01", value: 100000000 },
                  { date: "2025-01-02", value: 100400000 },
                ],
              },
            ],
            benchmark: [
              { date: "2025-01-01", value: 100000000 },
              { date: "2025-01-02", value: 100400000 },
            ],
            drawdowns: [
              {
                runId: "momentum_run",
                label: "Momentum drawdown",
                points: [
                  { date: "2025-01-01", value: -0.03 },
                  { date: "2025-01-02", value: -0.08 },
                ],
              },
              {
                runId: "value_run",
                label: "OP Fwd Yield drawdown",
                points: [
                  { date: "2025-01-01", value: -0.02 },
                  { date: "2025-01-02", value: -0.05 },
                ],
              },
            ],
          },
  };
}

function createDeferredPromise<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;

  const promise = new Promise<T>((innerResolve, innerReject) => {
    resolve = innerResolve;
    reject = innerReject;
  });

  return { promise, resolve, reject };
}

describe("App", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchRuns.mockReset();
    fetchDashboard.mockReset();
    chartOptions.length = 0;
  });

  it("renders the brand and selection heading", async () => {
    fetchRuns.mockResolvedValue([RUNS[0]]);
    fetchDashboard.mockResolvedValue(createDashboard("single", ["momentum_run"]));

    render(<App />);

    expect(await screen.findByText("1W1A")).toBeInTheDocument();
    expect(await screen.findByText("Live Performance")).toBeInTheDocument();
    expect(await screen.findByText("Select saved runs")).toBeInTheDocument();
    expect(await screen.findByText("Momentum")).toBeInTheDocument();
  });

  it("recomposes the workspace between single and multi strategy labels", async () => {
    const user = userEvent.setup();
    fetchRuns.mockResolvedValue(RUNS);
    fetchDashboard
      .mockResolvedValueOnce(createDashboard("single", ["momentum_run"]))
      .mockResolvedValueOnce(createDashboard("multi", ["momentum_run", "value_run"]));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    expect(await screen.findByText("Single strategy view")).toBeInTheDocument();
    expect(await screen.findByText("Rolling diagnostics")).toBeInTheDocument();
    expect(chartOptions.at(-2)).toMatchObject({
      series: [
        expect.objectContaining({ name: "Momentum equity" }),
        expect.objectContaining({ name: "KOSPI200 benchmark" }),
      ],
    });
    expect(chartOptions.at(-1)).toMatchObject({
      series: [
        expect.objectContaining({ name: "Rolling Sharpe" }),
        expect.objectContaining({ name: "Rolling Beta" }),
      ],
    });

    await user.click(screen.getByRole("button", { name: /OP Fwd Yield/i }));

    expect(await screen.findByText("Multi strategy comparison")).toBeInTheDocument();
    expect(await screen.findByText("Comparative pressure")).toBeInTheDocument();
    expect(chartOptions.at(-2)).toMatchObject({
      series: [
        expect.objectContaining({ name: "Momentum equity" }),
        expect.objectContaining({ name: "OP Fwd Yield equity" }),
        expect.objectContaining({ name: "KOSPI200 benchmark" }),
      ],
    });
    expect(chartOptions.at(-1)).toMatchObject({
      series: [
        expect.objectContaining({ name: "Momentum drawdown" }),
        expect.objectContaining({ name: "OP Fwd Yield drawdown" }),
      ],
    });
  });

  it("renders the exposure band and context drawer for a selected run", async () => {
    const user = userEvent.setup();
    fetchRuns.mockResolvedValue([RUNS[0]]);
    fetchDashboard.mockResolvedValue(createDashboard("single", ["momentum_run"]));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));

    expect(await screen.findByRole("heading", { name: "Latest holdings" })).toBeInTheDocument();
    expect(screen.getByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("Selected-run context")).toBeInTheDocument();
    expect(screen.getByText("KOSPI200 benchmark", { selector: "dd" })).toBeInTheDocument();
  });

  it("renders a failure message when saved runs fail to load", async () => {
    fetchRuns.mockRejectedValue(new Error("Failed to load saved runs."));

    render(<App />);

    expect(await screen.findByText("Failed to load saved runs.")).toBeInTheDocument();
  });

  it("does not show the empty-state copy while saved runs are still loading", () => {
    fetchRuns.mockReturnValue(new Promise(() => undefined));

    render(<App />);

    expect(screen.queryByRole("heading", { name: /No saved runs/i })).not.toBeInTheDocument();
  });

  it("clears dashboard errors when all runs are deselected", async () => {
    const user = userEvent.setup();
    fetchRuns.mockResolvedValue([RUNS[0]]);
    fetchDashboard.mockRejectedValue(new Error("Dashboard unavailable"));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    expect(await screen.findByRole("heading", { name: "Dashboard unavailable" })).toBeInTheDocument();
    expect(fetchDashboard).toHaveBeenCalledWith(["momentum_run"]);

    await user.click(screen.getByRole("button", { name: /Momentum/i }));

    expect(screen.queryByRole("heading", { name: "Dashboard unavailable" })).not.toBeInTheDocument();
    expect(screen.getByText("0 selected")).toBeInTheDocument();
  });

  it("removes stale dashboard content when a later dashboard request fails", async () => {
    const user = userEvent.setup();
    fetchRuns.mockResolvedValue(RUNS);
    fetchDashboard
      .mockResolvedValueOnce({
        mode: "single",
        selectedRunIds: ["momentum_run"],
        availableRuns: RUNS,
        metrics: {},
        context: {
          momentum_run: {
            label: "Momentum",
            strategy: "momentum",
            benchmark: { code: "KOSPI200", name: "KOSPI200 benchmark" },
            startDate: "2020-01-01",
            endDate: "2020-12-31",
            asOfDate: "2020-12-31",
          },
        },
        performance: {
          series: [],
          benchmark: [
            { date: "2025-01-01", value: 100000000 },
            { date: "2025-01-02", value: 100500000 },
          ],
          drawdowns: [],
        },
        rolling: { rollingSharpe: [], rollingBeta: [] },
        exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
      })
      .mockRejectedValueOnce(new Error("Failed to load dashboard."));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    expect(await screen.findByText("Single strategy view")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: /OP Fwd Yield/i }));

    expect(await screen.findByText("Failed to load dashboard.")).toBeInTheDocument();
    expect(screen.queryByText("Single strategy view")).not.toBeInTheDocument();
    expect(fetchDashboard).toHaveBeenNthCalledWith(1, ["momentum_run"]);
    expect(fetchDashboard).toHaveBeenNthCalledWith(2, ["momentum_run", "value_run"]);
  });

  it("renders dashboard errors without clearing the saved-run selector", async () => {
    const user = userEvent.setup();
    fetchRuns.mockResolvedValue(RUNS);
    fetchDashboard.mockRejectedValue(new Error("Failed to load dashboard."));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));

    expect(await screen.findByText("Failed to load dashboard.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Momentum/i })).toBeInTheDocument();
    expect(screen.getByText("1 selected")).toBeInTheDocument();
  });

  it("does not show the empty state after runs load until the request resolves with zero items", async () => {
    const deferredRuns = createDeferredPromise<(typeof RUNS)[number][]>();
    fetchRuns.mockReturnValue(deferredRuns.promise);

    render(<App />);

    expect(screen.queryByRole("heading", { name: /No saved runs/i })).not.toBeInTheDocument();

    deferredRuns.resolve([]);

    expect(await screen.findByRole("heading", { name: /No saved runs/i })).toBeInTheDocument();
  });
});
