import { useEffect, useState } from "react";

import EChartsReact from "echarts-for-react";
import { motion } from "framer-motion";

import type {
  CategorySeries,
  DashboardPayload,
  DistributionBin,
  HeatmapCell,
  NamedSeries,
  ResearchFocus,
  SeriesPoint,
} from "../lib/types";
import { ResearchDetailPanel } from "./ResearchDetailPanel";

type ResearchWorkspaceProps = {
  dashboard: DashboardPayload;
  focus: ResearchFocus;
  onFocusChange: (focus: ResearchFocus) => void;
};

type ResearchFigureProps = {
  title: string;
  subtitle: string;
  option: object;
  height?: number;
  isEmpty?: boolean;
  emptyMessage?: string;
};

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const SERIES_COLORS = ["#f0a44b", "#e3c06b", "#7cb8d8", "#c98f7d", "#8fa77f", "#bea1d8", "#dca96e", "#7ea5a5"];
const WEIGHTED_ASSET_RETURN_METHOD = "weighted-asset-return-attribution";
const DEFAULT_VISIBLE_SECTORS = 4;

function contributionSubtitle(method: string) {
  if (method === WEIGHTED_ASSET_RETURN_METHOD) {
    return "How much each sector added or detracted over time.";
  }

  return `Sector contribution from ${method || "the backend method"}.`;
}

function ResearchFigure({
  title,
  subtitle,
  option,
  height = 280,
  isEmpty = false,
  emptyMessage = "No data available.",
}: ResearchFigureProps) {
  return (
    <motion.article
      className="research-figure"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.38, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="research-figure-copy">
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>
      <div className="research-figure-chart">
        {isEmpty ? (
          <div className="research-figure-empty">{emptyMessage}</div>
        ) : (
          <EChartsReact option={option} style={{ height, width: "100%" }} />
        )}
      </div>
    </motion.article>
  );
}

function visibleRunIds(dashboard: DashboardPayload, focus: ResearchFocus) {
  if (focus.kind === "strategy" && dashboard.selectedRunIds.includes(focus.runId)) {
    return [focus.runId];
  }

  return dashboard.selectedRunIds;
}

function runLabel(dashboard: DashboardPayload, runId: string) {
  return dashboard.context[runId]?.label ?? runId;
}

function hasDistributionData(dashboard: DashboardPayload, runIds: string[]) {
  return runIds.some((runId) => (dashboard.research.returnDistribution[runId] ?? []).length > 0);
}

function hasSeriesData(series: NamedSeries[]) {
  return series.some((entry) => entry.points.length > 0);
}

function hasHeatmapData(cells: HeatmapCell[]) {
  return cells.length > 0;
}

function chartBase() {
  return {
    backgroundColor: "transparent",
    color: SERIES_COLORS,
    animationDuration: 420,
    animationEasing: "cubicOut",
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    legend: {
      top: 0,
      textStyle: { color: "#bdaea1", fontFamily: "inherit" },
    },
  };
}

function buildReturnDrawdownOption(dashboard: DashboardPayload, runIds: string[]) {
  const equitySeries = dashboard.performance.series
    .filter((series) => runIds.includes(series.runId))
    .map((series) => ({
      name: series.label,
      type: "line" as const,
      data: series.points.map((point) => [point.date, point.value]),
      xAxisIndex: 0,
      yAxisIndex: 0,
      showSymbol: false,
      smooth: true,
      lineStyle: { width: 2.2 },
      emphasis: { focus: "series" as const },
    }));

  const drawdownSeries = dashboard.performance.drawdowns
    .filter((series) => runIds.includes(series.runId))
    .map((series) => ({
      name: `${series.label}`,
      type: "line" as const,
      data: series.points.map((point) => [point.date, point.value]),
      xAxisIndex: 1,
      yAxisIndex: 1,
      showSymbol: false,
      smooth: true,
      areaStyle: { opacity: 0.14 },
      lineStyle: { width: 1.8 },
      emphasis: { focus: "series" as const },
    }));

  return {
    ...chartBase(),
    grid: [
      { left: 12, right: 18, top: 36, height: "34%", containLabel: true },
      { left: 12, right: 18, top: "58%", height: "24%", containLabel: true },
    ],
    xAxis: [
      {
        type: "time" as const,
        gridIndex: 0,
        axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
        axisLabel: { color: "#bdaea1" },
        splitLine: { show: false },
      },
      {
        type: "time" as const,
        gridIndex: 1,
        axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
        axisLabel: { color: "#bdaea1" },
        splitLine: { show: false },
      },
    ],
    yAxis: [
      {
        type: "value" as const,
        gridIndex: 0,
        axisLabel: { color: "#bdaea1" },
        splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
      },
      {
        type: "value" as const,
        gridIndex: 1,
        axisLabel: { color: "#bdaea1" },
        splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
      },
    ],
    series: [...equitySeries, ...drawdownSeries],
  };
}

function buildDistributionOption(dashboard: DashboardPayload, runIds: string[]) {
  const labels = Array.from(
    new Set(
      runIds.flatMap((runId) =>
        (dashboard.research.returnDistribution[runId] ?? []).map((bin) => `${bin.start.toFixed(2)} to ${bin.end.toFixed(2)}`),
      ),
    ),
  );

  return {
    ...chartBase(),
    grid: { left: 12, right: 18, top: 36, bottom: 40, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: labels,
      axisLabel: { color: "#bdaea1", interval: 0, rotate: 25 },
      axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#bdaea1" },
      splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
    },
    series: runIds.map((runId) => {
      const bins = dashboard.research.returnDistribution[runId] ?? [];
      const frequencyByLabel = new Map(bins.map((bin) => [`${bin.start.toFixed(2)} to ${bin.end.toFixed(2)}`, bin.frequency]));
      return {
        name: runLabel(dashboard, runId),
        type: "bar" as const,
        data: labels.map((label) => frequencyByLabel.get(label) ?? 0),
        barMaxWidth: 18,
      };
    }),
  };
}

function heatmapRunId(dashboard: DashboardPayload, focus: ResearchFocus) {
  if (focus.kind === "strategy" && dashboard.selectedRunIds.includes(focus.runId)) {
    return focus.runId;
  }

  return dashboard.selectedRunIds[0] ?? "";
}

function buildHeatmapOption(cells: HeatmapCell[]) {
  const years = Array.from(new Set(cells.map((cell) => String(cell.year)))).sort();
  const data = cells.map((cell) => [cell.month - 1, years.indexOf(String(cell.year)), cell.value]);

  return {
    backgroundColor: "transparent",
    tooltip: {
      position: "top" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    grid: { left: 12, right: 18, top: 16, bottom: 18, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: MONTH_LABELS,
      splitArea: { show: true },
      axisLabel: { color: "#bdaea1" },
      axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
    },
    yAxis: {
      type: "category" as const,
      data: years,
      splitArea: { show: true },
      axisLabel: { color: "#bdaea1" },
      axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
    },
    visualMap: {
      min: -0.15,
      max: 0.15,
      calculable: true,
      orient: "horizontal" as const,
      left: "center" as const,
      bottom: 0,
      textStyle: { color: "#bdaea1" },
      inRange: {
        color: ["#5a2e28", "#a4684f", "#171b1f", "#7d8f74", "#d4b15c"],
      },
    },
    series: [
      {
        name: "Monthly return",
        type: "heatmap" as const,
        data,
        label: { show: false },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0, 0, 0, 0.3)" } },
      },
    ],
  };
}

function buildLineOption(series: NamedSeries[], labelFormatter?: (series: NamedSeries) => string) {
  return {
    ...chartBase(),
    grid: { left: 12, right: 18, top: 36, bottom: 24, containLabel: true },
    xAxis: {
      type: "time" as const,
      axisLabel: { color: "#bdaea1" },
      axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#bdaea1" },
      splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
    },
    series: series.map((entry) => ({
      name: labelFormatter ? labelFormatter(entry) : entry.label,
      type: "line" as const,
      data: entry.points.map((point) => [point.date, point.value]),
      showSymbol: false,
      smooth: true,
      lineStyle: { width: 2 },
      emphasis: { focus: "series" as const },
    })),
  };
}

function buildYearlyExcessOption(dashboard: DashboardPayload, runIds: string[]) {
  const years = Array.from(
    new Set(
      runIds.flatMap((runId) => (dashboard.research.yearlyExcessReturns[runId] ?? []).map((point) => point.date.slice(0, 4))),
    ),
  ).sort();

  return {
    ...chartBase(),
    grid: { left: 12, right: 18, top: 36, bottom: 24, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: years,
      axisLabel: { color: "#bdaea1" },
      axisLine: { lineStyle: { color: "rgba(247, 240, 231, 0.18)" } },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#bdaea1" },
      splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
    },
    series: runIds.map((runId) => {
      const values = new Map((dashboard.research.yearlyExcessReturns[runId] ?? []).map((point) => [point.date.slice(0, 4), point.value]));
      return {
        name: runLabel(dashboard, runId),
        type: "bar" as const,
        data: years.map((year) => values.get(year) ?? 0),
        barMaxWidth: 18,
      };
    }),
  };
}

function collectSectorSeries(
  dashboard: DashboardPayload,
  runIds: string[],
  source: Record<string, CategorySeries[]>,
  sectorNames: string[],
) {
  const collected: NamedSeries[] = [];
  const visibleSectors = new Set(sectorNames);

  runIds.forEach((runId) => {
    const label = runLabel(dashboard, runId);
    const seriesSet = source[runId] ?? [];
    const visible = seriesSet.filter((entry) => visibleSectors.has(entry.name));

    visible.forEach((entry) => {
      collected.push({
        runId,
        label: `${label} · ${entry.name}`,
        points: entry.points,
      });
    });
  });

  return collected;
}

function collectSectorNamesByRelevance(dashboard: DashboardPayload, runIds: string[]) {
  const scores = new Map<string, number>();
  const sources = [dashboard.research.sectorContributionSeries, dashboard.research.sectorWeightSeries];

  sources.forEach((source) => {
    runIds.forEach((runId) => {
      (source[runId] ?? []).forEach((entry) => {
        const latestPoint = entry.points[entry.points.length - 1];
        const score = latestPoint ? Math.abs(latestPoint.value) : 0;
        scores.set(entry.name, (scores.get(entry.name) ?? 0) + score);
      });
    });
  });

  return Array.from(scores.entries())
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }
      return left[0].localeCompare(right[0]);
    })
    .map(([name]) => name);
}

export function ResearchWorkspace({ dashboard, focus, onFocusChange }: ResearchWorkspaceProps) {
  const runIds = visibleRunIds(dashboard, focus);
  const availableSectorNames = collectSectorNamesByRelevance(dashboard, runIds);
  const availableSectorNamesKey = availableSectorNames.join("|");
  const [selectedSectorNames, setSelectedSectorNames] = useState<string[]>([]);

  useEffect(() => {
    setSelectedSectorNames((current) => {
      const next = current.filter((name) => availableSectorNames.includes(name));
      if (next.length === current.length && next.every((name, index) => name === current[index])) {
        return current;
      }
      return next;
    });
  }, [availableSectorNamesKey]);

  const fallbackSectorNames =
    focus.kind === "sector" && availableSectorNames.includes(focus.sectorName)
      ? [focus.sectorName]
      : availableSectorNames.slice(0, DEFAULT_VISIBLE_SECTORS);
  const activeSectorNames = selectedSectorNames.length > 0 ? selectedSectorNames : fallbackSectorNames;
  const activeHeatmapRunId = heatmapRunId(dashboard, focus);
  const activeHeatmapLabel = activeHeatmapRunId ? runLabel(dashboard, activeHeatmapRunId) : "Selected run";
  const heatmapCells = activeHeatmapRunId ? dashboard.research.monthlyHeatmap[activeHeatmapRunId] ?? [] : [];
  const rollingSharpeSeries = dashboard.rolling.rollingSharpe.filter((series) => runIds.includes(series.runId));
  const sectorContributionSeries = collectSectorSeries(dashboard, runIds, dashboard.research.sectorContributionSeries, activeSectorNames);
  const sectorWeightSeries = collectSectorSeries(dashboard, runIds, dashboard.research.sectorWeightSeries, activeSectorNames);

  return (
    <section className="research-workspace">
      <div className="research-workspace-head">
        <div>
          <p className="section-label">Research</p>
          <h2 id="research-workspace-heading">Research charts</h2>
        </div>
        <p className="workspace-summary">Returns, risk, and sector trends for the selected strategies.</p>
        <div className="focus-chip-row">
          <button
            type="button"
            className={`focus-chip ${focus.kind === "all-selected" ? "is-active" : ""}`}
            onClick={() => onFocusChange({ kind: "all-selected" })}
            aria-label="Show all selected strategies"
          >
            All selected
          </button>
          {dashboard.selectedRunIds.map((runId) => (
            <button
              key={runId}
              type="button"
              className={`focus-chip ${focus.kind === "strategy" && focus.runId === runId ? "is-active" : ""}`}
              onClick={() => onFocusChange({ kind: "strategy", runId })}
              aria-label={`Show strategy ${runLabel(dashboard, runId)}`}
            >
              {runLabel(dashboard, runId)}
            </button>
          ))}
        </div>
        <div className="research-filter-panel">
          <div className="research-filter-copy">
            <p className="section-label">Sector filter</p>
            <p className="workspace-summary">
              Pick sectors to compare. Without a manual selection, the charts show the most relevant sectors.
            </p>
          </div>
          <div className="focus-chip-row focus-chip-row--filters">
            <button
              type="button"
              className={`focus-chip ${selectedSectorNames.length === 0 ? "is-active" : ""}`}
              onClick={() => setSelectedSectorNames([])}
              aria-label="Show all sectors"
              aria-pressed={selectedSectorNames.length === 0}
            >
              All sectors
            </button>
            {availableSectorNames.map((sectorName) => {
              const isActive =
                selectedSectorNames.includes(sectorName) ||
                (selectedSectorNames.length === 0 && fallbackSectorNames.includes(sectorName));
              return (
                <button
                  key={sectorName}
                  type="button"
                  className={`focus-chip ${isActive ? "is-active" : ""}`}
                  onClick={() =>
                    setSelectedSectorNames((current) =>
                      current.includes(sectorName) ? current.filter((name) => name !== sectorName) : [...current, sectorName],
                    )
                  }
                  aria-label={`Toggle sector ${sectorName}`}
                  aria-pressed={selectedSectorNames.includes(sectorName)}
                >
                  {sectorName}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="research-grid research-grid--full">
        <ResearchFigure
          title="Cumulative return and drawdown"
          subtitle="Cumulative return above, drawdown below."
          option={buildReturnDrawdownOption(dashboard, runIds)}
          height={360}
          isEmpty={!hasSeriesData(dashboard.performance.series.filter((series) => runIds.includes(series.runId)))}
          emptyMessage="No performance history available."
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Return distribution"
          subtitle="How daily returns are distributed."
          option={buildDistributionOption(dashboard, runIds)}
          isEmpty={!hasDistributionData(dashboard, runIds)}
          emptyMessage="No return distribution data."
        />
        <ResearchFigure
          title="Monthly heatmap"
          subtitle={`Monthly returns for ${activeHeatmapLabel}.`}
          option={buildHeatmapOption(heatmapCells)}
          isEmpty={!hasHeatmapData(heatmapCells)}
          emptyMessage="No monthly return data."
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Rolling Sharpe"
          subtitle="Rolling risk-adjusted return."
          option={buildLineOption(rollingSharpeSeries)}
          isEmpty={!hasSeriesData(rollingSharpeSeries)}
          emptyMessage="No rolling Sharpe data."
        />
        <ResearchFigure
          title="Yearly excess returns"
          subtitle="Annual return minus benchmark."
          option={buildYearlyExcessOption(dashboard, runIds)}
          isEmpty={!runIds.some((runId) => (dashboard.research.yearlyExcessReturns[runId] ?? []).length > 0)}
          emptyMessage="No yearly excess return data."
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Sector contribution series"
          subtitle={
            selectedSectorNames.length > 0
              ? `Selected sectors: ${selectedSectorNames.join(", ")}.`
              : contributionSubtitle(dashboard.research.sectorContributionMethod)
          }
          option={buildLineOption(sectorContributionSeries)}
          isEmpty={!hasSeriesData(sectorContributionSeries)}
          emptyMessage="No sector contribution data."
        />
        <ResearchFigure
          title="Sector weight series"
          subtitle="How sector weights changed over time."
          option={buildLineOption(sectorWeightSeries)}
          isEmpty={!hasSeriesData(sectorWeightSeries)}
          emptyMessage="No sector weight data."
        />
      </div>

      <ResearchDetailPanel dashboard={dashboard} focus={focus} />
    </section>
  );
}
