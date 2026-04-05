import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { fetchRuns, fetchSession, fetchDashboard } = vi.hoisted(() => ({
  fetchRuns: vi.fn(),
  fetchSession: vi.fn(),
  fetchDashboard: vi.fn(),
}));

vi.mock("../lib/api", () => ({
  fetchRuns,
  fetchSession,
  fetchDashboard,
}));

import { App } from "../app/App";

describe("App", () => {
  beforeEach(() => {
    fetchRuns.mockReset();
    fetchSession.mockReset();
    fetchDashboard.mockReset();
    fetchSession.mockResolvedValue({ defaultSelectedRunIds: [] });
  });

  afterEach(() => {
    cleanup();
  });

  it("hydrates launcher defaults and shows the single-run mode", async () => {
    fetchRuns.mockResolvedValue([
      {
        runId: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { finalEquity: 100000000, avgTurnover: 0.12 },
      },
      {
        runId: "op_fwd_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { finalEquity: 120000000, avgTurnover: 0.18 },
      },
    ]);
    fetchSession.mockResolvedValue({
      defaultSelectedRunIds: ["op_fwd_run", "missing_run"],
    });
    fetchDashboard.mockResolvedValue({
      mode: "single",
      selectedRunIds: ["op_fwd_run"],
      availableRuns: [],
      metrics: {
        op_fwd_run: {
          label: "OP Fwd Yield",
          cumulativeReturn: 0.2,
          cagr: 0.18,
          annualVolatility: 0.24,
          sharpe: 1.8,
          sortino: 1.5,
          calmar: 1.2,
          maxDrawdown: -0.06,
          finalEquity: 120000000,
          avgTurnover: 0.18,
          alpha: 0.01,
          beta: 0.9,
          trackingError: 0.12,
          informationRatio: 0.7,
        },
      },
      context: {},
      performance: { series: [], benchmark: null, drawdowns: [] },
      rolling: { rollingSharpe: [], rollingBeta: [] },
      exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
    });

    render(<App />);

    expect(await screen.findByText("1W1A")).toBeInTheDocument();
    expect(await screen.findByText("Select saved runs")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: /OP Fwd Yield/i })).toHaveAttribute("aria-pressed", "true");
    expect(fetchDashboard).toHaveBeenCalledWith(["op_fwd_run"]);
    expect(await screen.findByText("Single-run mode")).toBeInTheDocument();
    expect(await screen.findByText("OP Fwd Yield loaded")).toBeInTheDocument();
  });

  it("falls back to the first run when session bootstrap rejects", async () => {
    fetchRuns.mockResolvedValue([
      {
        runId: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { finalEquity: 100000000, avgTurnover: 0.12 },
      },
      {
        runId: "op_fwd_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { finalEquity: 120000000, avgTurnover: 0.18 },
      },
    ]);
    fetchSession.mockRejectedValue(new Error("session unavailable"));
    fetchDashboard.mockResolvedValue({
      mode: "single",
      selectedRunIds: ["momentum_run"],
      availableRuns: [],
      metrics: {
        momentum_run: {
          label: "Momentum",
          cumulativeReturn: 0.1,
          cagr: 0.12,
          annualVolatility: 0.2,
          sharpe: 1.4,
          sortino: 1.2,
          calmar: 1.1,
          maxDrawdown: -0.08,
          finalEquity: 110000000,
          avgTurnover: 0.12,
          alpha: 0.0,
          beta: 1.0,
          trackingError: 0.1,
          informationRatio: 0.5,
        },
      },
      context: {},
      performance: { series: [], benchmark: null, drawdowns: [] },
      rolling: { rollingSharpe: [], rollingBeta: [] },
      exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
    });

    render(<App />);

    expect(await screen.findByRole("button", { name: /Momentum/i })).toHaveAttribute("aria-pressed", "true");
    expect(fetchDashboard).toHaveBeenCalledWith(["momentum_run"]);
    expect(await screen.findByText("Single-run mode")).toBeInTheDocument();
    expect(await screen.findByText("Momentum loaded")).toBeInTheDocument();
  });

  it("falls back to the first run when session bootstrap payload is malformed", async () => {
    fetchRuns.mockResolvedValue([
      {
        runId: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { finalEquity: 100000000, avgTurnover: 0.12 },
      },
      {
        runId: "op_fwd_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { finalEquity: 120000000, avgTurnover: 0.18 },
      },
    ]);
    fetchSession.mockResolvedValue({
      defaultSelectedRunIds: "not-an-array",
    } as any);
    fetchDashboard.mockResolvedValue({
      mode: "single",
      selectedRunIds: ["momentum_run"],
      availableRuns: [],
      metrics: {
        momentum_run: {
          label: "Momentum",
          cumulativeReturn: 0.1,
          cagr: 0.12,
          annualVolatility: 0.2,
          sharpe: 1.4,
          sortino: 1.2,
          calmar: 1.1,
          maxDrawdown: -0.08,
          finalEquity: 110000000,
          avgTurnover: 0.12,
          alpha: 0.0,
          beta: 1.0,
          trackingError: 0.1,
          informationRatio: 0.5,
        },
      },
      context: {},
      performance: { series: [], benchmark: null, drawdowns: [] },
      rolling: { rollingSharpe: [], rollingBeta: [] },
      exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
    });

    render(<App />);

    expect(await screen.findByRole("button", { name: /Momentum/i })).toHaveAttribute("aria-pressed", "true");
    expect(fetchDashboard).toHaveBeenCalledWith(["momentum_run"]);
    expect(await screen.findByText("Single-run mode")).toBeInTheDocument();
    expect(await screen.findByText("Momentum loaded")).toBeInTheDocument();
  });

  it("adds another run to the selection and switches into multi-run mode", async () => {
    fetchRuns.mockResolvedValue([
      {
        runId: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { finalEquity: 100000000, avgTurnover: 0.12 },
      },
      {
        runId: "op_fwd_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { finalEquity: 120000000, avgTurnover: 0.18 },
      },
    ]);
    fetchSession.mockResolvedValue({
      defaultSelectedRunIds: ["momentum_run"],
    });
    fetchDashboard
      .mockResolvedValueOnce({
        mode: "single",
        selectedRunIds: ["momentum_run"],
        availableRuns: [],
        metrics: {
          momentum_run: {
            label: "Momentum",
            cumulativeReturn: 0.1,
            cagr: 0.12,
            annualVolatility: 0.2,
            sharpe: 1.4,
            sortino: 1.2,
            calmar: 1.1,
            maxDrawdown: -0.08,
            finalEquity: 110000000,
            avgTurnover: 0.12,
            alpha: 0.0,
            beta: 1.0,
            trackingError: 0.1,
            informationRatio: 0.5,
          },
        },
        context: {},
        performance: { series: [], benchmark: null, drawdowns: [] },
        rolling: { rollingSharpe: [], rollingBeta: [] },
        exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
      })
      .mockResolvedValueOnce({
        mode: "multi",
        selectedRunIds: ["momentum_run", "op_fwd_run"],
        availableRuns: [],
        metrics: {
          momentum_run: {
            label: "Momentum",
            cumulativeReturn: 0.1,
            cagr: 0.12,
            annualVolatility: 0.2,
            sharpe: 1.4,
            sortino: 1.2,
            calmar: 1.1,
            maxDrawdown: -0.08,
            finalEquity: 110000000,
            avgTurnover: 0.12,
            alpha: 0.0,
            beta: 1.0,
            trackingError: 0.1,
            informationRatio: 0.5,
          },
          op_fwd_run: {
            label: "OP Fwd Yield",
            cumulativeReturn: 0.2,
            cagr: 0.18,
            annualVolatility: 0.24,
            sharpe: 1.8,
            sortino: 1.5,
            calmar: 1.2,
            maxDrawdown: -0.06,
            finalEquity: 120000000,
            avgTurnover: 0.18,
            alpha: 0.01,
            beta: 0.9,
            trackingError: 0.12,
            informationRatio: 0.7,
          },
        },
        context: {},
        performance: { series: [], benchmark: null, drawdowns: [] },
        rolling: { rollingSharpe: [], rollingBeta: [] },
        exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
      });

    const user = userEvent.setup();

    render(<App />);

    await screen.findByText("Single-run mode");
    await user.click(screen.getByRole("button", { name: /OP Fwd Yield/i }));

    expect(fetchDashboard).toHaveBeenLastCalledWith(["momentum_run", "op_fwd_run"]);
    expect(await screen.findByText("Multi-run mode")).toBeInTheDocument();
    expect(await screen.findByText("Momentum loaded")).toBeInTheDocument();
    expect(await screen.findByText("OP Fwd Yield loaded")).toBeInTheDocument();
  });

  it("clears stale workspace content when a selection change fails to load", async () => {
    fetchRuns.mockResolvedValue([
      {
        runId: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { finalEquity: 100000000, avgTurnover: 0.12 },
      },
      {
        runId: "op_fwd_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { finalEquity: 120000000, avgTurnover: 0.18 },
      },
    ]);
    fetchSession.mockResolvedValue({
      defaultSelectedRunIds: ["momentum_run"],
    });
    fetchDashboard
      .mockResolvedValueOnce({
        mode: "single",
        selectedRunIds: ["momentum_run"],
        availableRuns: [],
        metrics: {
          momentum_run: {
            label: "Momentum",
            cumulativeReturn: 0.1,
            cagr: 0.12,
            annualVolatility: 0.2,
            sharpe: 1.4,
            sortino: 1.2,
            calmar: 1.1,
            maxDrawdown: -0.08,
            finalEquity: 110000000,
            avgTurnover: 0.12,
            alpha: 0.0,
            beta: 1.0,
            trackingError: 0.1,
            informationRatio: 0.5,
          },
        },
        context: {},
        performance: { series: [], benchmark: null, drawdowns: [] },
        rolling: { rollingSharpe: [], rollingBeta: [] },
        exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
      })
      .mockRejectedValueOnce(new Error("dashboard unavailable"));

    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByText("Momentum loaded")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /OP Fwd Yield/i }));

    expect(await screen.findByText("dashboard unavailable")).toBeInTheDocument();
    expect(screen.queryByText("Momentum loaded")).not.toBeInTheDocument();
    expect(screen.queryByText("Single-run mode")).not.toBeInTheDocument();
  });

  it("renders a failure message when saved runs fail to load", async () => {
    fetchRuns.mockRejectedValue(new Error("Failed to load saved runs."));

    render(<App />);

    expect(await screen.findByText("Failed to load saved runs.")).toBeInTheDocument();
  });
});
