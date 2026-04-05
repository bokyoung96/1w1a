import { useEffect, useState } from "react";

import { fetchDashboard, fetchRuns, fetchSession } from "../lib/api";
import type { DashboardPayload, RunOption, SessionBootstrap } from "../lib/types";

function normalizeSessionBootstrap(value: SessionBootstrap | unknown): SessionBootstrap {
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

function resolveInitialRunIds(runs: RunOption[], bootstrap: SessionBootstrap) {
  const availableRunIds = new Set(runs.map((run) => run.runId));
  const validBootstrapIds = Array.from(
    new Set(normalizeSessionBootstrap(bootstrap).defaultSelectedRunIds.filter((runId) => availableRunIds.has(runId))),
  );

  if (validBootstrapIds.length > 0) {
    return validBootstrapIds;
  }

  return runs[0] ? [runs[0].runId] : [];
}

export function App() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [selectedRunIds, setSelectedRunIds] = useState<string[]>([]);
  const [runsError, setRunsError] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    void Promise.all([
      fetchRuns(),
      fetchSession().catch(() => ({ defaultSelectedRunIds: [] })),
    ])
      .then(([nextRuns, bootstrap]) => {
        if (!isMounted) {
          return;
        }

        setRuns(nextRuns);
        setRunsError(null);
        setSelectedRunIds(resolveInitialRunIds(nextRuns, bootstrap));
      })
      .catch((nextError: unknown) => {
        if (!isMounted) {
          return;
        }

        setRunsError(nextError instanceof Error ? nextError.message : "Failed to load saved runs.");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    if (selectedRunIds.length === 0) {
      setDashboard(null);
      setDashboardError(null);
      return () => {
        isMounted = false;
      };
    }

    setDashboard(null);
    setDashboardError(null);

    void fetchDashboard(selectedRunIds)
      .then((nextDashboard) => {
        if (!isMounted) {
          return;
        }

        setDashboard(nextDashboard);
      })
      .catch((nextError: unknown) => {
        if (!isMounted) {
          return;
        }

        setDashboard(null);
        setDashboardError(nextError instanceof Error ? nextError.message : "Failed to load dashboard.");
      });

    return () => {
      isMounted = false;
    };
  }, [selectedRunIds]);

  function toggleRun(runId: string) {
    setSelectedRunIds((current) => {
      const nextSelection = current.includes(runId)
        ? current.filter((candidate) => candidate !== runId)
        : [...current, runId];
      const nextSelectionSet = new Set(nextSelection);
      return runs.filter((run) => nextSelectionSet.has(run.runId)).map((run) => run.runId);
    });
  }

  const loadedMetrics = dashboard
    ? dashboard.selectedRunIds.map((runId) => ({
        runId,
        label: dashboard.metrics[runId]?.label ?? runId,
      }))
    : [];

  return (
    <div className="dashboard-shell">
      <header className="top-rail">
        <div className="brand-lockup">
          <span className="brand-mark">1W1A</span>
          <span className="brand-subtitle">Live Performance</span>
        </div>
      </header>
      <main className="dashboard-stage">
        <section className="selector-panel">
          <p className="section-label">Select saved runs</p>
          {runsError ? <p className="status-message">{runsError}</p> : null}
          {!runsError && runs.length === 0 ? <p className="status-message">No saved runs found.</p> : null}
          <ul className="saved-runs-list">
            {runs.map((run) => (
              <li key={run.runId} className="saved-run-item">
                <button
                  type="button"
                  className="saved-run-button"
                  aria-pressed={selectedRunIds.includes(run.runId)}
                  onClick={() => toggleRun(run.runId)}
                >
                  <span>{run.label}</span>
                  <span className="saved-run-meta">{run.strategy}</span>
                </button>
              </li>
            ))}
          </ul>
        </section>
        <section className="workspace-panel" aria-live="polite">
          <p className="section-label">Operator workspace</p>
          {selectedRunIds.length === 0 ? <p className="status-message">Select at least one saved run.</p> : null}
          {dashboardError ? <p className="status-message">{dashboardError}</p> : null}
          {dashboard ? (
            <div className="workspace-summary">
              <h1 className="workspace-title">{dashboard.mode === "single" ? "Single-run mode" : "Multi-run mode"}</h1>
              <p className="workspace-copy">
                {dashboard.selectedRunIds.length} run{dashboard.selectedRunIds.length === 1 ? "" : "s"} active
              </p>
              <ul className="workspace-loaded-list">
                {loadedMetrics.map(({ runId, label }) => (
                  <li key={runId}>{label} loaded</li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      </main>
    </div>
  );
}
