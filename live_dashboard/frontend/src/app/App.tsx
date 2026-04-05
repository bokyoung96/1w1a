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
          {error ? <p className="status-message">{error}</p> : null}
          <ul className="saved-runs-list">
            {runs.map((run) => (
              <li key={run.run_id} className="saved-run-item">
                {run.label}
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
