import { useEffect, useState } from "react";

import { fetchRuns } from "../lib/api";
import type { RunOption } from "../lib/types";

export function App() {
  const [runs, setRuns] = useState<RunOption[]>([]);

  useEffect(() => {
    void fetchRuns().then(setRuns);
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
          <ul>
            {runs.map((run) => (
              <li key={run.run_id}>{run.label}</li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
