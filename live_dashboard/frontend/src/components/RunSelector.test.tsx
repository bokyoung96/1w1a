import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { fetchRuns, fetchDashboard } = vi.hoisted(() => ({
  fetchRuns: vi.fn(),
  fetchDashboard: vi.fn(),
}));

vi.mock("../lib/api", () => ({
  fetchRuns,
  fetchDashboard,
}));

beforeEach(() => {
  fetchRuns.mockReset();
  fetchDashboard.mockReset();
  fetchRuns.mockResolvedValue([
    {
      run_id: "momentum_run",
      label: "Momentum",
      strategy: "momentum",
      summary: { final_equity: 100, avg_turnover: 0.1 },
    },
    {
      run_id: "value_run",
      label: "OP Fwd Yield",
      strategy: "op_fwd_yield",
      summary: { final_equity: 105, avg_turnover: 0.2 },
    },
  ]);
  fetchDashboard.mockResolvedValue({
    mode: "single",
    selectedRunIds: ["momentum_run"],
    availableRuns: [
      {
        run_id: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { final_equity: 100, avg_turnover: 0.1 },
      },
      {
        run_id: "value_run",
        label: "OP Fwd Yield",
        strategy: "op_fwd_yield",
        summary: { final_equity: 105, avg_turnover: 0.2 },
      },
    ],
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
        { date: "2025-01-01", value: 100 },
        { date: "2025-01-02", value: 101 },
      ],
      drawdowns: [],
    },
    rolling: { rollingSharpe: [], rollingBeta: [] },
    exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
  });
});

import { App } from "../app/App";

describe("Run selection", () => {
  it("allows selecting and deselecting runs from the manual selector", async () => {
    const user = userEvent.setup();

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    await user.click(await screen.findByRole("button", { name: /OP Fwd Yield/i }));

    expect(screen.getByText("2 selected")).toBeInTheDocument();
    expect(fetchDashboard).toHaveBeenNthCalledWith(1, ["momentum_run"]);
    expect(fetchDashboard).toHaveBeenNthCalledWith(2, ["momentum_run", "value_run"]);

    await user.click(screen.getByRole("button", { name: /Momentum/i }));

    expect(screen.getByText("1 selected")).toBeInTheDocument();
    expect(fetchDashboard).toHaveBeenNthCalledWith(3, ["value_run"]);

    await user.click(screen.getByRole("button", { name: /OP Fwd Yield/i }));

    expect(screen.getByText("0 selected")).toBeInTheDocument();
    expect(fetchDashboard).toHaveBeenCalledTimes(3);
  });
});
