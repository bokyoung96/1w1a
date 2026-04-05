import { motion } from "framer-motion";

import type { DashboardPayload, ResearchFocus } from "../lib/types";

type ContextDrawerProps = {
  dashboard: DashboardPayload;
  focus: ResearchFocus;
  onFocusChange: (focus: ResearchFocus) => void;
};

function resolveRunIds(dashboard: DashboardPayload, focus: ResearchFocus) {
  if (focus.kind === "strategy" && dashboard.selectedRunIds.includes(focus.runId)) {
    return [focus.runId];
  }

  return dashboard.selectedRunIds;
}

export function ContextDrawer({ dashboard, focus, onFocusChange }: ContextDrawerProps) {
  const runIds = resolveRunIds(dashboard, focus);

  return (
    <motion.section
      className="detail-section context-drawer"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.04, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Context panel</p>
        <h2>Run metadata</h2>
        <p className="workspace-summary">Benchmark framing, timeline bounds, and drill-down state stay visible while you inspect the research figures.</p>
      </div>

      {focus.kind !== "all-selected" ? (
        <div className="focus-banner focus-banner--inline">
          <span className="section-label">Active drill-down</span>
          <strong>
            {focus.kind === "strategy"
              ? dashboard.context[focus.runId]?.label ?? focus.runId
              : `Sector · ${focus.sectorName}`}
          </strong>
          <button type="button" className="workspace-inline-action" onClick={() => onFocusChange({ kind: "all-selected" })}>
            Reset focus
          </button>
        </div>
      ) : null}

      <div className="context-list">
        {runIds.map((runId) => {
          const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
          const context = dashboard.context[runId];

          return (
            <button
              key={runId}
              type="button"
              className={`context-entry context-entry--button ${
                focus.kind === "strategy" && focus.runId === runId ? "is-focused" : ""
              }`}
              onClick={() => onFocusChange({ kind: "strategy", runId })}
              aria-label={`Open context for strategy ${context?.label ?? run?.label ?? runId}`}
            >
              <div className="detail-run-head">
                <strong>{context?.label ?? run?.label ?? runId}</strong>
                <span>{context?.strategy ?? run?.strategy ?? "unknown"}</span>
              </div>
              <dl className="context-definition-list">
                <div>
                  <dt>Benchmark</dt>
                  <dd>{context?.benchmark.name ?? "n/a"}</dd>
                </div>
                <div>
                  <dt>Start</dt>
                  <dd>{context?.startDate ?? "n/a"}</dd>
                </div>
                <div>
                  <dt>End</dt>
                  <dd>{context?.endDate ?? "n/a"}</dd>
                </div>
                <div>
                  <dt>As of</dt>
                  <dd>{context?.asOfDate ?? "n/a"}</dd>
                </div>
              </dl>
            </button>
          );
        })}
      </div>
    </motion.section>
  );
}
