import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { fetchRuns } = vi.hoisted(() => ({
  fetchRuns: vi.fn(),
}));

vi.mock("../lib/api", () => ({
  fetchRuns,
  fetchDashboard: vi.fn().mockResolvedValue(null),
}));

import { App } from "../app/App";

describe("App", () => {
  beforeEach(() => {
    fetchRuns.mockReset();
  });

  it("renders the brand and selection heading", async () => {
    fetchRuns.mockResolvedValue([
      {
        run_id: "momentum_run",
        label: "Momentum",
        strategy: "momentum",
        summary: { final_equity: 100000000, avg_turnover: 0.12 },
      },
    ]);

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
});
