import type { RunOption } from "../lib/types";

type RunSelectorProps = {
  runs: RunOption[];
  selectedRunIds: string[];
  onToggle: (runId: string) => void;
};

export function RunSelector({ runs, selectedRunIds, onToggle }: RunSelectorProps) {
  return (
    <section className="selector-panel run-selector">
      <p className="section-label">Select saved runs</p>
      <div className="run-selector-list">
        {runs.map((run) => {
          const selected = selectedRunIds.includes(run.run_id);

          return (
            <button
              key={run.run_id}
              type="button"
              className={`run-chip ${selected ? "is-selected" : ""}`}
              onClick={() => onToggle(run.run_id)}
              aria-pressed={selected}
            >
              <span className="run-chip-label">{run.label}</span>
              <span className="run-chip-meta">{run.strategy}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
