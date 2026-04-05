import EChartsReact from "echarts-for-react";
import { motion } from "framer-motion";

import { formatMoney, formatPercent } from "../lib/format";
import type { DashboardPayload } from "../lib/types";

type DiagnosticStripProps = {
  dashboard: DashboardPayload;
};

export function DiagnosticStrip({ dashboard }: DiagnosticStripProps) {
  const isSingleMode = dashboard.mode === "single";
  const selectedRuns = dashboard.selectedRunIds
    .map((runId) => {
      const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
      const metric = dashboard.metrics[runId];

      if (!run || !metric) {
        return null;
      }

      return {
        runId,
        label: dashboard.context[runId]?.label ?? run.label,
        metric,
      };
    })
    .filter((entry): entry is { runId: string; label: string; metric: DashboardPayload["metrics"][string] } => entry !== null);

  const rollingSharpeSeries = dashboard.rolling.rollingSharpe.map((series) => ({
    name: series.label,
    type: "line" as const,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2 },
    emphasis: { focus: "series" as const },
  }));

  const rollingBetaSeries = dashboard.rolling.rollingBeta.map((series) => ({
    name: series.label,
    type: "line" as const,
    yAxisIndex: 1,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2, type: "dashed" as const },
    emphasis: { focus: "series" as const },
  }));

  const drawdownSeries = dashboard.performance.drawdowns.map((series) => ({
    name: series.label,
    type: "line" as const,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    areaStyle: { opacity: 0.12 },
    lineStyle: { width: 2 },
    emphasis: { focus: "series" as const },
  }));

  const chartSeries = isSingleMode
    ? [...rollingSharpeSeries, ...rollingBetaSeries]
    : drawdownSeries.length > 0
      ? drawdownSeries
      : [...rollingSharpeSeries, ...rollingBetaSeries];

  const chartOption = {
    backgroundColor: "transparent",
    color: isSingleMode ? ["#f3c97f", "#8bc6ff", "#e3a7ff", "#79d6c0"] : ["#d88d36", "#f08f70", "#f3c97f", "#8bc6ff"],
    grid: {
      left: 4,
      right: 14,
      top: 12,
      bottom: 24,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis" as const,
    },
    legend: {
      show: chartSeries.length > 1,
      top: 0,
      textStyle: {
        color: "#b8aca0",
        fontFamily: "inherit",
      },
    },
    xAxis: {
      type: "time" as const,
      axisLine: { lineStyle: { color: "rgba(255, 248, 240, 0.18)" } },
      axisLabel: { color: "#b8aca0" },
      splitLine: { show: false },
    },
    yAxis: isSingleMode
      ? [
          {
            type: "value" as const,
            axisLabel: {
              color: "#b8aca0",
              formatter: (value: number) => value.toFixed(2),
            },
            splitLine: { lineStyle: { color: "rgba(255, 248, 240, 0.08)" } },
          },
          {
            type: "value" as const,
            axisLabel: {
              color: "#b8aca0",
              formatter: (value: number) => value.toFixed(2),
            },
            splitLine: { show: false },
          },
        ]
      : {
          type: "value" as const,
          axisLabel: {
            color: "#b8aca0",
            formatter: (value: number) => formatPercent(value),
          },
          splitLine: { lineStyle: { color: "rgba(255, 248, 240, 0.08)" } },
        },
    series: chartSeries,
  };

  const stripLabel = isSingleMode ? "Rolling diagnostics" : "Comparative pressure";
  const heading = isSingleMode ? "Single-run stability under the lens" : "Drawdown pressure across selected runs";
  const summary = isSingleMode
    ? "Rolling Sharpe and beta stay centered on the active run."
    : "Drawdown curves and max-drawdown readings show which strategy absorbs stress best.";

  const modeMetrics = isSingleMode
    ? [
        {
          label: rollingSharpeSeries[0]?.name ?? "Rolling Sharpe",
          value: latestSeriesValue(dashboard.rolling.rollingSharpe[0]),
          detail: "latest Sharpe",
        },
        {
          label: rollingBetaSeries[0]?.name ?? "Rolling Beta",
          value: latestSeriesValue(dashboard.rolling.rollingBeta[0]),
          detail: "latest beta",
        },
      ]
    : selectedRuns.map((run) => ({
        label: run.label,
        value: formatPercent(run.metric.max_drawdown),
        detail: formatMoney(run.metric.final_equity),
      }));

  return (
    <motion.section
      className={`workspace-strip diagnostic-strip ${isSingleMode ? "is-single" : "is-multi"}`}
      data-mode={dashboard.mode}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="workspace-strip-copy">
        <p className="section-label">{stripLabel}</p>
        <h2>{heading}</h2>
        <p className="workspace-summary">{summary}</p>
      </div>

      <div className="workspace-strip-grid workspace-strip-grid--diagnostic">
        <motion.div className="workspace-chart-plane workspace-chart-plane--diagnostic" whileHover={{ scale: 1.005 }}>
          <EChartsReact option={chartOption} style={{ height: 260, width: "100%" }} />
        </motion.div>

        <div className="workspace-quiet-metrics">
          {modeMetrics.map((entry) => (
            <div key={entry.label} className="workspace-quiet-line">
              <span>{entry.label}</span>
              <strong>{entry.value}</strong>
              <em>{entry.detail}</em>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}

function latestSeriesValue(series?: { points: { value: number }[] }) {
  if (!series || series.points.length === 0) {
    return "n/a";
  }

  return series.points[series.points.length - 1].value.toFixed(2);
}
