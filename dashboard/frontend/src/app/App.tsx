import { useEffect, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { ExposureBand } from "../components/ExposureBand";
import { ContextDrawer } from "../components/ContextDrawer";
import { DiagnosticStrip } from "../components/DiagnosticStrip";
import { PerformanceStrip } from "../components/PerformanceStrip";
import { RunSelector } from "../components/RunSelector";
import { TopRail } from "../components/TopRail";
import { fetchDashboard, fetchRuns } from "../lib/api";
import type { DashboardPayload, RunOption } from "../lib/types";

export function App() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [selectedRunIds, setSelectedRunIds] = useState<string[]>([]);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [runsLoading, setRunsLoading] = useState(true);
  const [runsError, setRunsError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    setRunsLoading(true);

    void fetchRuns()
      .then((nextRuns) => {
        if (!isMounted) {
          return;
        }

        setRuns(nextRuns);
        setRunsError(null);
      })
      .catch((nextError: unknown) => {
        if (!isMounted) {
          return;
        }

        setRunsError(nextError instanceof Error ? nextError.message : "Failed to load saved runs.");
      })
      .finally(() => {
        if (!isMounted) {
          return;
        }

        setRunsLoading(false);
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
        setDashboardError(null);
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

  return (
    <div className="dashboard-shell">
      <TopRail selectionCount={selectedRunIds.length} />
      <main className="dashboard-stage">
        {runsError ? <ErrorState message={runsError} /> : null}
        {dashboardError ? <ErrorState message={dashboardError} /> : null}
        {!runsLoading && !runsError && runs.length === 0 ? <EmptyState /> : null}
        {!runsLoading && runs.length > 0 ? (
          <RunSelector runs={runs} selectedRunIds={selectedRunIds} onToggle={toggleRun} />
        ) : null}
        {dashboard ? (
          <div className="cinema-workspace">
            <PerformanceStrip dashboard={dashboard} />
            <DiagnosticStrip dashboard={dashboard} />
            <div className="detail-band">
              <ExposureBand dashboard={dashboard} />
              <ContextDrawer dashboard={dashboard} />
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );

  function toggleRun(runId: string) {
    setSelectedRunIds((current) =>
      current.includes(runId) ? current.filter((value) => value !== runId) : [...current, runId],
    );
  }
}
