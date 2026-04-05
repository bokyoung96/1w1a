import { motion } from "framer-motion";

import { formatPercent } from "../lib/format";
import type { DashboardPayload, ResearchFocus } from "../lib/types";

const MAX_VISIBLE_HOLDINGS = 5;

type ExposureBandProps = {
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

export function ExposureBand({ dashboard, focus, onFocusChange }: ExposureBandProps) {
  const runIds = resolveRunIds(dashboard, focus);

  return (
    <motion.section
      className="detail-section exposure-band"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      aria-label="Exposure band"
    >
      <div className="detail-section-copy">
        <p className="section-label">Exposure band</p>
        <h2>Latest holdings and sector context</h2>
        <p className="workspace-summary">
          Sector rows act as in-page drill-down controls. Holdings stay pinned to the latest available snapshot.
        </p>
      </div>

      {focus.kind === "sector" ? (
        <div className="focus-banner focus-banner--inline">
          <span className="section-label">Sector drill-down</span>
          <strong>{focus.sectorName}</strong>
          <button type="button" className="workspace-inline-action" onClick={() => onFocusChange({ kind: "all-selected" })}>
            Show all selected
          </button>
        </div>
      ) : null}

      <div className="detail-run-list">
        {runIds.map((runId) => {
          const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
          const context = dashboard.context[runId];
          const holdings = (dashboard.exposure.latestHoldings[runId] ?? []).slice(0, MAX_VISIBLE_HOLDINGS);
          const sectorWeights = dashboard.exposure.sectorWeights[runId] ?? [];
          const visibleSectors =
            focus.kind === "sector"
              ? sectorWeights.filter((sector) => sector.name === focus.sectorName)
              : sectorWeights;

          return (
            <div key={runId} className="detail-run-block">
              <div className="detail-run-head">
                <strong>{context?.label ?? run?.label ?? runId}</strong>
                <span>{context?.strategy ?? run?.strategy ?? "strategy"}</span>
              </div>

              <div className="detail-subgrid">
                <div className="detail-subsection">
                  <div className="detail-subsection-head">
                    <span>Latest holdings</span>
                    <span>{holdings.length} lines</span>
                  </div>
                  <div className="detail-column-labels">
                    <span>Symbol</span>
                    <span>Target weight</span>
                    <span>Absolute weight</span>
                  </div>
                  <div className="detail-list">
                    {holdings.length > 0 ? (
                      holdings.map((holding) => (
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
                    <span>Sector weights</span>
                    <span>{visibleSectors.length} sectors</span>
                  </div>
                  <div className="detail-column-labels detail-column-labels--sectors">
                    <span>Sector</span>
                    <span>Weight</span>
                  </div>
                  <div className="detail-list">
                    {visibleSectors.length > 0 ? (
                      visibleSectors.map((sector) => {
                        const isFocused = focus.kind === "sector" && focus.sectorName === sector.name;

                        return (
                          <button
                            key={sector.name}
                            type="button"
                            className={`detail-list-row detail-list-row--button ${isFocused ? "is-focused" : ""}`}
                            onClick={() => onFocusChange({ kind: "sector", sectorName: sector.name })}
                            aria-label={`Focus sector ${sector.name}`}
                          >
                            <strong>{sector.name}</strong>
                            <span>{formatPercent(sector.value)}</span>
                          </button>
                        );
                      })
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
          );
        })}
      </div>
    </motion.section>
  );
}
