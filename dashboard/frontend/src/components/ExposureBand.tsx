import { motion } from "framer-motion";

import { formatPercent } from "../lib/format";
import type { DashboardPayload } from "../lib/types";

const MAX_VISIBLE_HOLDINGS = 4;
const MAX_VISIBLE_SECTORS = 4;

type ExposureBandProps = {
  dashboard: DashboardPayload;
};

export function ExposureBand({ dashboard }: ExposureBandProps) {
  const selectedRuns = dashboard.selectedRunIds.map((runId) => {
    const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
    const context = dashboard.context[runId];
    const holdings = (dashboard.exposure.latestHoldings[runId] ?? []).slice(0, MAX_VISIBLE_HOLDINGS);
    const sectorWeights = (dashboard.exposure.sectorWeights[runId] ?? []).slice(0, MAX_VISIBLE_SECTORS);

    return {
      runId,
      label: context?.label ?? run?.label ?? runId,
      holdings,
      sectorWeights,
    };
  });

  return (
    <motion.section
      className="detail-section exposure-band"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Exposure band</p>
        <h2>Latest holdings</h2>
        <p className="workspace-summary">Holdings and sector mix are pulled from the latest available snapshot for each selected run.</p>
      </div>

      <div className="detail-run-list">
        {selectedRuns.map((run) => (
          <div key={run.runId} className="detail-run-block">
            <div className="detail-run-head">
              <strong>{run.label}</strong>
              <span>latest position table</span>
            </div>

            <div className="detail-subgrid">
              <div className="detail-subsection">
                <div className="detail-subsection-head">
                  <span>Latest holdings</span>
                  <span>{run.holdings.length} line{run.holdings.length === 1 ? "" : "s"}</span>
                </div>
                <div className="detail-column-labels">
                  <span>Symbol</span>
                  <span>Target weight</span>
                  <span>Absolute weight</span>
                </div>
                <div className="detail-list">
                  {run.holdings.length > 0 ? (
                    run.holdings.map((holding) => (
                      <div key={holding.symbol} className="detail-list-row">
                        <strong>{holding.symbol}</strong>
                        <span>{formatPercent(holding.targetWeight)}</span>
                        <span>{formatPercent(holding.absWeight)}</span>
                      </div>
                    ))
                  ) : (
                    <div className="detail-list-row detail-list-row--empty">
                      <strong>No holdings</strong>
                      <span>latest snapshot missing</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-subsection">
                <div className="detail-subsection-head">
                  <span>Sector mix</span>
                  <span>{run.sectorWeights.length} segment{run.sectorWeights.length === 1 ? "" : "s"}</span>
                </div>
                <div className="detail-column-labels detail-column-labels--sectors">
                  <span>Sector</span>
                  <span>Weight</span>
                </div>
                <div className="detail-list">
                  {run.sectorWeights.length > 0 ? (
                    run.sectorWeights.map((sector) => (
                      <div key={sector.name} className="detail-list-row">
                        <strong>{sector.name}</strong>
                        <span>{formatPercent(sector.value)}</span>
                      </div>
                    ))
                  ) : (
                    <div className="detail-list-row detail-list-row--empty">
                      <strong>No sectors</strong>
                      <span>latest snapshot missing</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.section>
  );
}
