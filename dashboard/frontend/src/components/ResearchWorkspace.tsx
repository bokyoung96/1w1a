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
};

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const SERIES_COLORS = ["#f0a44b", "#e3c06b", "#7cb8d8", "#c98f7d", "#8fa77f", "#bea1d8", "#dca96e", "#7ea5a5"];
const WEIGHTED_ASSET_RETURN_METHOD = "weighted-asset-return-attribution";

function contributionSubtitle(method: string) {
  if (method === WEIGHTED_ASSET_RETURN_METHOD) {
    return "Sector-level cumulative contribution computed from weighted asset returns.";
  }

  return `Sector-level contribution series using backend method: ${method || "not provided"}.`;
}

function ResearchFigure({ title, subtitle, option, height = 280 }: ResearchFigureProps) {
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
        <EChartsReact option={option} style={{ height, width: "100%" }} />
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
  focus: ResearchFocus,
) {
  const collected: NamedSeries[] = [];

  runIds.forEach((runId) => {
    const label = runLabel(dashboard, runId);
    const seriesSet = source[runId] ?? [];
    const visible = focus.kind === "sector" ? seriesSet.filter((entry) => entry.name === focus.sectorName) : seriesSet;

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

export function ResearchWorkspace({ dashboard, focus, onFocusChange }: ResearchWorkspaceProps) {
  const runIds = visibleRunIds(dashboard, focus);
  const activeHeatmapRunId = heatmapRunId(dashboard, focus);
  const activeHeatmapLabel = activeHeatmapRunId ? runLabel(dashboard, activeHeatmapRunId) : "Selected run";
  const heatmapCells = activeHeatmapRunId ? dashboard.research.monthlyHeatmap[activeHeatmapRunId] ?? [] : [];
  const rollingSharpeSeries = dashboard.rolling.rollingSharpe.filter((series) => runIds.includes(series.runId));
  const sectorContributionSeries = collectSectorSeries(
    dashboard,
    runIds,
    dashboard.research.sectorContributionSeries,
    focus,
  );
  const sectorWeightSeries = collectSectorSeries(dashboard, runIds, dashboard.research.sectorWeightSeries, focus);

  return (
    <section className="research-workspace">
      <div className="research-workspace-head">
        <div>
          <p className="section-label">Analytics area</p>
          <h2 id="research-workspace-heading">Research workspace</h2>
        </div>
        <p className="workspace-summary">
          Multi-strategy comparison remains the default. Strategy and sector clicks narrow the same in-page workspace.
        </p>
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
      </div>

      <div className="research-grid research-grid--full">
        <ResearchFigure
          title="Return and max drawdown"
          subtitle="Shared figure row for strategy equity and underwater pressure."
          option={buildReturnDrawdownOption(dashboard, runIds)}
          height={360}
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Return distribution"
          subtitle="Frequency by return bucket across the active comparison set."
          option={buildDistributionOption(dashboard, runIds)}
        />
        <ResearchFigure
          title="Monthly heatmap"
          subtitle={`Monthly return heatmap for ${activeHeatmapLabel}.`}
          option={buildHeatmapOption(heatmapCells)}
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Rolling Sharpe"
          subtitle="Rolling Sharpe stays aligned to the current strategy selection."
          option={buildLineOption(rollingSharpeSeries)}
        />
        <ResearchFigure
          title="Yearly excess returns"
          subtitle="Benchmark-relative yearly return spread by run."
          option={buildYearlyExcessOption(dashboard, runIds)}
        />
      </div>

      <div className="research-grid research-grid--double">
        <ResearchFigure
          title="Sector contribution series"
          subtitle={contributionSubtitle(dashboard.research.sectorContributionMethod)}
          option={buildLineOption(sectorContributionSeries)}
        />
        <ResearchFigure
          title="Sector weight series"
          subtitle="Sector allocations over time for the current comparison focus."
          option={buildLineOption(sectorWeightSeries)}
        />
      </div>

      <ResearchDetailPanel dashboard={dashboard} focus={focus} />
    </section>
  );
}
