import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { RunSelector } from "../components/RunSelector";
import { TopRail } from "../components/TopRail";
import { fetchDashboard, fetchRuns } from "../lib/api";
import type { DashboardPayload, RunOption } from "../lib/types";

export function App() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [selectedRunIds, setSelectedRunIds] = useState<string[]>([]);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    void fetchRuns()
      .then((nextRuns) => {
        if (!isMounted) {
          return;
        }

        setRuns(nextRuns);
        setError(null);
      })
      .catch((nextError: unknown) => {
        if (!isMounted) {
          return;
        }

        setError(nextError instanceof Error ? nextError.message : "Failed to load saved runs.");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    if (selectedRunIds.length === 0) {
      setDashboard(null);
      return () => {
        isMounted = false;
      };
    }

    void fetchDashboard(selectedRunIds)
      .then((nextDashboard) => {
        if (!isMounted) {
          return;
        }

        setDashboard(nextDashboard);
        setError(null);
      })
      .catch((nextError: unknown) => {
        if (!isMounted) {
          return;
        }

        setError(nextError instanceof Error ? nextError.message : "Failed to load dashboard.");
      });

    return () => {
      isMounted = false;
    };
  }, [selectedRunIds]);

  return (
    <div className="dashboard-shell">
      <TopRail selectionCount={selectedRunIds.length} />
      <main className="dashboard-stage">
        {error ? <ErrorState message={error} /> : null}
        {!error && runs.length === 0 ? <EmptyState /> : null}
        {runs.length > 0 ? (
          <RunSelector runs={runs} selectedRunIds={selectedRunIds} onToggle={toggleRun} />
        ) : null}
        {dashboard ? <pre className="selector-panel debug-state">{dashboard.mode}</pre> : null}
      </main>
    </div>
  );

  function toggleRun(runId: string) {
    setSelectedRunIds((current) =>
      current.includes(runId) ? current.filter((value) => value !== runId) : [...current, runId],
    );
  }
}
