import EChartsReact from "echarts-for-react";
import { motion } from "framer-motion";

import { formatPercent } from "../lib/format";
import type { DashboardPayload } from "../lib/types";

type DiagnosticStripProps = {
  dashboard: DashboardPayload;
};

export function DiagnosticStrip({ dashboard }: DiagnosticStripProps) {
  const rollingSharpeSeries = dashboard.rolling.rollingSharpe.map((series) => ({
    name: series.name,
    type: "line" as const,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2 },
    emphasis: { focus: "series" as const },
  }));

  const rollingBetaSeries = dashboard.rolling.rollingBeta.map((series) => ({
    name: series.name,
    type: "line" as const,
    yAxisIndex: 1,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2, type: "dashed" as const },
    emphasis: { focus: "series" as const },
  }));

  const chartOption = {
    backgroundColor: "transparent",
    color: ["#f3c97f", "#8bc6ff", "#e3a7ff", "#79d6c0"],
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
      show: rollingSharpeSeries.length + rollingBetaSeries.length > 1,
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
    yAxis: [
      {
        type: "value" as const,
        axisLabel: {
          color: "#b8aca0",
          formatter: (value: number) => formatPercent(value),
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
    ],
    series: [...rollingSharpeSeries, ...rollingBetaSeries],
  };

  const holdingsLine = dashboard.selectedRunIds
    .map((runId) => {
      const holdings = dashboard.exposure.holdingsCount.find((series) => series.key === runId);
      const latest = holdings?.points[holdings.points.length - 1];

      if (!latest) {
        return null;
      }

      const label = dashboard.context[runId]?.name ?? dashboard.availableRuns.find((run) => run.run_id === runId)?.label ?? runId;

      return { label, value: latest.value };
    })
    .filter((entry): entry is { label: string; value: number } => entry !== null);

  return (
    <motion.section
      className="workspace-strip diagnostic-strip"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="workspace-strip-copy">
        <p className="section-label">Diagnostics band</p>
        <h2>Risk and execution signals</h2>
        <p className="workspace-summary">Rolling Sharpe and beta stay in view while the selected strategies recombine.</p>
      </div>

      <div className="workspace-strip-grid workspace-strip-grid--diagnostic">
        <motion.div className="workspace-chart-plane workspace-chart-plane--diagnostic" whileHover={{ scale: 1.005 }}>
          <EChartsReact option={chartOption} style={{ height: 260, width: "100%" }} />
        </motion.div>

        <div className="workspace-quiet-metrics">
          {holdingsLine.map((entry) => (
            <div key={entry.label} className="workspace-quiet-line">
              <span>{entry.label}</span>
              <strong>{entry.value}</strong>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}
