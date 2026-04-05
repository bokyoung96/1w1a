import { useEffect, useState } from "react";

import { fetchRuns } from "../lib/api";
import type { RunOption } from "../lib/types";

export function App() {
  const [runs, setRuns] = useState<RunOption[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    void fetchRuns()
      .then((nextRuns) => {
        if (isMounted) {
          setRuns(nextRuns);
        }
      })
      .catch((nextError: unknown) => {
        if (isMounted) {
          setError(nextError instanceof Error ? nextError.message : "Failed to load saved runs.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard-shell">
      <header className="top-rail">
        <div className="brand-lockup">
          <h1 className="brand-mark">1W1A</h1>
          <p className="brand-subtitle">Live Dashboard</p>
        </div>
      </header>
      <main className="dashboard-stage">
        <section className="selector-panel" aria-label="Saved run selection">
          <p className="section-label">Select saved runs</p>
          {error ? <p className="status-message">{error}</p> : null}
          {runs.length > 0 ? (
            <ul className="saved-runs-list">
              {runs.map((run) => (
                <li key={run.run_id} className="saved-run-item">
                  <span>{run.label}</span>
                  <span className="saved-run-meta">{run.strategy}</span>
                </li>
              ))}
            </ul>
          ) : (
            !error ? <p className="status-message">No saved runs available yet.</p> : null
          )}
        </section>
      </main>
    </div>
  );
}
