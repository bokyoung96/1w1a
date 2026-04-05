import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { fetchRuns, fetchDashboard } = vi.hoisted(() => ({
  fetchRuns: vi.fn(),
  fetchDashboard: vi.fn(),
}));

vi.mock("../lib/api", () => ({
  fetchRuns,
  fetchDashboard,
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
  });

  it("renders the brand and selection heading", async () => {
    fetchRuns.mockResolvedValue([RUNS[0]]);
    fetchDashboard.mockResolvedValue({
      mode: "single",
      selectedRunIds: ["momentum_run"],
      availableRuns: RUNS,
      metrics: {},
      context: {},
      performance: { series: [], benchmark: null, drawdowns: [] },
      rolling: { rollingSharpe: [], rollingBeta: [] },
      exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
    });

    render(<App />);

    expect(await screen.findByText("1W1A")).toBeInTheDocument();
    expect(await screen.findByText("Live Performance")).toBeInTheDocument();
    expect(await screen.findByText("Select saved runs")).toBeInTheDocument();
    expect(await screen.findByText("Momentum")).toBeInTheDocument();
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
        context: {},
        performance: { series: [], benchmark: null, drawdowns: [] },
        rolling: { rollingSharpe: [], rollingBeta: [] },
        exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
      })
      .mockRejectedValueOnce(new Error("Failed to load dashboard."));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    expect(await screen.findByText("single")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: /OP Fwd Yield/i }));

    expect(await screen.findByText("Failed to load dashboard.")).toBeInTheDocument();
    expect(screen.queryByText("single")).not.toBeInTheDocument();
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
