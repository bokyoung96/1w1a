import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../lib/api", () => ({
  fetchRuns: vi.fn().mockResolvedValue([
    {
      run_id: "momentum_run",
      label: "Momentum",
      strategy: "momentum",
      summary: { final_equity: 100000000, avg_turnover: 0.12 },
    },
  ]),
  fetchDashboard: vi.fn().mockResolvedValue(null),
}));

import { App } from "../app/App";

describe("App", () => {
  it("renders the brand and selection heading", async () => {
    render(<App />);

    expect(await screen.findByText("1W1A")).toBeInTheDocument();
    expect(await screen.findByText("Live Performance")).toBeInTheDocument();
    expect(await screen.findByText("Select saved runs")).toBeInTheDocument();
  });
});
