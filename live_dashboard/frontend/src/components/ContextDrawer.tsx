import { motion } from "framer-motion";

import type { DashboardPayload } from "../lib/types";

type ContextDrawerProps = {
  dashboard: DashboardPayload;
};

export function ContextDrawer({ dashboard }: ContextDrawerProps) {
  const selectedRuns = dashboard.selectedRunIds.map((runId) => {
    const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
    const context = dashboard.context[runId];

    return {
      runId,
      label: context?.label ?? run?.label ?? runId,
      strategy: context?.strategy ?? run?.strategy ?? "unknown",
      benchmark: context?.benchmark.name ?? "unknown",
      startDate: context?.startDate ?? "n/a",
      endDate: context?.endDate ?? "n/a",
      asOfDate: context?.asOfDate ?? "n/a",
    };
  });

  return (
    <motion.section
      className="detail-section context-drawer"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.05, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Selected-run context</p>
        <h2>Run metadata</h2>
        <p className="workspace-summary">This panel keeps the timeline and benchmark framing visible while the strips above do the heavy lifting.</p>
      </div>

      <div className="context-list">
        {selectedRuns.map((run) => (
          <div key={run.runId} className="context-entry">
            <div className="detail-run-head">
              <strong>{run.label}</strong>
              <span>{run.strategy}</span>
            </div>
            <dl className="context-definition-list">
              <div>
                <dt>Benchmark</dt>
                <dd>{run.benchmark}</dd>
              </div>
              <div>
                <dt>Start</dt>
                <dd>{run.startDate}</dd>
              </div>
              <div>
                <dt>End</dt>
                <dd>{run.endDate}</dd>
              </div>
              <div>
                <dt>As of</dt>
                <dd>{run.asOfDate}</dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
    </motion.section>
  );
}
