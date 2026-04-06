import { motion } from "framer-motion";

import { formatPercent } from "../lib/format";
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

function contributionMethodLabel(method: string) {
  if (method === WEIGHTED_ASSET_RETURN_METHOD) {
    return "Weighted asset return attribution";
  }

  return method || "not provided";
}

function formatNumberValue(value: number, digits = 2) {
  return value.toFixed(digits);
}

export function ResearchDetailPanel({ dashboard, focus }: ResearchDetailPanelProps) {
  const runIds = visibleRunIds(dashboard, focus);
  const episodes = flattenEpisodes(dashboard, runIds);
  const metricRunId =
    focus.kind === "strategy" && dashboard.metrics[focus.runId] ? focus.runId : runIds[0] ?? "";
  const metric = metricRunId ? dashboard.metrics[metricRunId] : undefined;
  const metricRows = metric
    ? [
        ["Sharpe", formatNumberValue(metric.sharpe, 2)],
        ["Calmar", formatNumberValue(metric.calmar, 2)],
        ["Information Ratio", formatNumberValue(metric.informationRatio, 2)],
        ["Hit Rate", formatPercent(metric.cagr / Math.max(metric.cumulativeReturn, 1e-6), 1)],
        ["Profit / Risk", formatPercent(metric.cagr / Math.max(metric.maxDrawdown, 1e-6), 2)],
      ]
    : [];
  const toughest = episodes.filter((entry) => !entry.episode.recovered);
  const longestOpen = toughest.sort(
    (left, right) => right.episode.durationDays - left.episode.durationDays,
  )[0];

  return (
    <motion.section
      className="detail-section research-detail-panel"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.42, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Details</p>
        <h2>Research details</h2>
        <p className="workspace-summary">Key metrics and drawdown context for the current focus.</p>
      </div>

      <div className="focus-banner focus-banner--inline">
        <span className="section-label">Current focus</span>
        <strong>{focusSummary(focus, dashboard)}</strong>
      </div>

      <div className="detail-panel-grid">
        <div className="detail-metric-grid">
          {metricRows.length > 0 ? (
            metricRows.map(([label, value]) => (
              <div key={label} className="detail-metric-row">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))
          ) : (
            <div className="detail-metric-row detail-metric-row--empty">
              <span>No metric data available.</span>
            </div>
          )}
        </div>
        <div className="detail-note">
          <span className="section-label">Toughest drawdown</span>
          <strong>{longestOpen ? `${longestOpen.episode.durationDays}d open` : "None in progress"}</strong>
          <p>{longestOpen ? `Peaked ${longestOpen.episode.peak}` : "All drawdowns recovered."}</p>
        </div>
      </div>

      <div className="detail-note-list">
        <div className="detail-note">
          <span className="section-label">Sector contribution</span>
          <strong>Sector contribution series</strong>
          <p>Method: {contributionMethodLabel(dashboard.research.sectorContributionMethod)}.</p>
        </div>
        <div className="detail-note">
          <span className="section-label">Benchmark</span>
          <strong>Yearly excess returns</strong>
          <p>Excess return panels remain benchmark-relative for each selected run.</p>
        </div>
      </div>
    </motion.section>
  );
}
