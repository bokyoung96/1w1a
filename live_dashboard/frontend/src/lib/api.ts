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

export function normalizeSessionBootstrap(value: unknown): SessionBootstrap {
  const defaultSelectedRunIds = (() => {
    if (!value || typeof value !== "object") {
      return [];
    }

    const candidate = (value as { defaultSelectedRunIds?: unknown }).defaultSelectedRunIds;
    if (!Array.isArray(candidate)) {
      return [];
    }

    return candidate.filter((runId): runId is string => typeof runId === "string");
  })();

  return { defaultSelectedRunIds };
}

export async function fetchRuns(): Promise<RunOption[]> {
  const response = await fetch(`${API_ROOT}/runs`);
  if (!response.ok) {
    throw new Error(`Failed to load runs: ${response.status}`);
  }
  return response.json() as Promise<RunOption[]>;
}

export async function fetchSession(): Promise<SessionBootstrap> {
  const response = await fetch(`${API_ROOT}/session`);
  if (!response.ok) {
    throw new Error(`Failed to load session: ${response.status}`);
  }

  try {
    return normalizeSessionBootstrap(await response.json());
  } catch {
    return { defaultSelectedRunIds: [] };
  }
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
