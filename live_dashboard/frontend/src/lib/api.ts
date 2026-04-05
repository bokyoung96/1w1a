import type { DashboardPayload, RunOption } from "./types";

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_ROOT?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

const API_ROOT = import.meta.env.VITE_API_ROOT ?? "http://localhost:8000/api";

export async function fetchRuns(): Promise<RunOption[]> {
  const response = await fetch(`${API_ROOT}/runs`);
  if (!response.ok) {
    throw new Error(`Failed to load runs: ${response.status}`);
  }
  return response.json() as Promise<RunOption[]>;
}

export async function fetchDashboard(runIds: string[]): Promise<DashboardPayload> {
  const query = new URLSearchParams();
  runIds.forEach((runId) => query.append("run_ids", runId));

  const response = await fetch(`${API_ROOT}/dashboard?${query.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to load dashboard: ${response.status}`);
  }
  return response.json() as Promise<DashboardPayload>;
}
