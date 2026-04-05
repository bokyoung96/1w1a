import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("../lib/api", () => ({
  fetchRuns: vi.fn().mockResolvedValue([
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
  ]),
  fetchDashboard: vi.fn().mockResolvedValue({
    mode: "single",
    selectedRunIds: ["momentum_run"],
    availableRuns: [],
    metrics: {},
    context: {
      momentum_run: {
        name: "Momentum",
        strategy: "momentum",
        start: "2020-01-01",
        end: "2020-12-31",
        validation: null,
      },
    },
    performance: { series: [], benchmark: null, drawdowns: [] },
    rolling: { rollingSharpe: [], rollingBeta: [] },
    exposure: { holdingsCount: [], latestHoldings: {}, sectorWeights: {} },
  }),
}));

import { App } from "../app/App";

describe("Run selection", () => {
  it("allows selecting multiple runs from the manual selector", async () => {
    const user = userEvent.setup();

    render(<App />);

    await user.click(await screen.findByRole("button", { name: /Momentum/i }));
    await user.click(await screen.findByRole("button", { name: /OP Fwd Yield/i }));

    expect(screen.getByText("2 selected")).toBeInTheDocument();
  });
});
