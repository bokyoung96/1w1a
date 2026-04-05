import { motion } from "framer-motion";

import { formatMoney, formatPercent } from "../lib/format";
import type { DashboardPayload, DrawdownEpisode, ResearchFocus } from "../lib/types";

type ResearchDetailPanelProps = {
  dashboard: DashboardPayload;
  focus: ResearchFocus;
};

const WEIGHTED_ASSET_RETURN_METHOD = "weighted-asset-return-attribution";

function visibleRunIds(dashboard: DashboardPayload, focus: ResearchFocus) {
  if (focus.kind === "strategy" && dashboard.selectedRunIds.includes(focus.runId)) {
    return [focus.runId];
  }

  return dashboard.selectedRunIds;
}

function focusSummary(focus: ResearchFocus, dashboard: DashboardPayload) {
  if (focus.kind === "strategy") {
    return dashboard.context[focus.runId]?.label ?? focus.runId;
  }

  if (focus.kind === "sector") {
    return `Sector · ${focus.sectorName}`;
  }

  return "All selected";
}

function flattenEpisodes(dashboard: DashboardPayload, runIds: string[]) {
  return runIds.flatMap((runId) => {
    const label = dashboard.context[runId]?.label ?? runId;
    return (dashboard.research.drawdownEpisodes[runId] ?? []).map((episode) => ({
      runId,
      label,
      episode,
    }));
  });
}

function renderEpisodeStatus(episode: DrawdownEpisode) {
  if (!episode.recovered) {
    return "Open";
  }

  return episode.recoveryDays == null ? "Recovered" : `${episode.recoveryDays}d recovery`;
}

function contributionMethodLabel(method: string) {
  if (method === WEIGHTED_ASSET_RETURN_METHOD) {
    return "Weighted asset return attribution";
  }

  return method || "not provided";
}

export function ResearchDetailPanel({ dashboard, focus }: ResearchDetailPanelProps) {
  const runIds = visibleRunIds(dashboard, focus);
  const episodes = flattenEpisodes(dashboard, runIds);

  return (
    <motion.section
      className="detail-section research-detail-panel"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.42, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Detail inspector</p>
        <h2>Research detail layer</h2>
        <p className="workspace-summary">
          Metrics, drawdown episodes, and sector contribution context update with the current in-page focus.
        </p>
      </div>

      <div className="focus-banner focus-banner--inline">
        <span className="section-label">Current focus</span>
        <strong>{focusSummary(focus, dashboard)}</strong>
      </div>

      <div className="detail-panel-grid">
        <div className="detail-table-shell">
          <table className="detail-table" aria-label="Detail metrics">
            <thead>
              <tr>
                <th scope="col">Strategy</th>
                <th scope="col">Return</th>
                <th scope="col">Sharpe</th>
                <th scope="col">Max drawdown</th>
                <th scope="col">Final equity</th>
              </tr>
            </thead>
            <tbody>
              {runIds.map((runId) => {
                const metric = dashboard.metrics[runId];
                const label = dashboard.context[runId]?.label ?? runId;
                return (
                  <tr key={runId}>
                    <th scope="row">{label}</th>
                    <td>{metric ? formatPercent(metric.cumulativeReturn) : "n/a"}</td>
                    <td>{metric ? metric.sharpe.toFixed(2) : "n/a"}</td>
                    <td>{metric ? formatPercent(metric.maxDrawdown) : "n/a"}</td>
                    <td>{metric ? formatMoney(metric.finalEquity) : "n/a"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="detail-table-shell">
          <table className="detail-table" aria-label="Drawdown episodes">
            <thead>
              <tr>
                <th scope="col">Strategy</th>
                <th scope="col">Peak</th>
                <th scope="col">Trough</th>
                <th scope="col">Drawdown</th>
                <th scope="col">Duration</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {episodes.length > 0 ? (
                episodes.map(({ runId, label, episode }) => (
                  <tr key={`${runId}-${episode.peak}-${episode.trough}`}>
                    <th scope="row">{label}</th>
                    <td>{episode.peak}</td>
                    <td>{episode.trough}</td>
                    <td>{formatPercent(episode.drawdown)}</td>
                    <td>{episode.durationDays}d</td>
                    <td>{renderEpisodeStatus(episode)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <th scope="row">No drawdowns</th>
                  <td colSpan={5}>No drawdown episodes are available for the current focus.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="detail-note-list">
        <div className="detail-note">
          <span className="section-label">Contribution naming</span>
          <strong>Sector contribution series</strong>
          <p>Method: {contributionMethodLabel(dashboard.research.sectorContributionMethod)}.</p>
        </div>
        <div className="detail-note">
          <span className="section-label">Benchmark context</span>
          <strong>Yearly excess returns</strong>
          <p>Excess return panels remain benchmark-relative for each selected run.</p>
        </div>
      </div>
    </motion.section>
  );
}
