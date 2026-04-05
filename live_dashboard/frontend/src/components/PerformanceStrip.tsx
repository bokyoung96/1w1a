import EChartsReact from "echarts-for-react";
import { motion } from "framer-motion";

import { formatMoney, formatPercent } from "../lib/format";
import type { DashboardPayload } from "../lib/types";

type PerformanceStripProps = {
  dashboard: DashboardPayload;
};

export function PerformanceStrip({ dashboard }: PerformanceStripProps) {
  const title = dashboard.mode === "single" ? "Single strategy view" : "Multi strategy comparison";
  const selectedRuns = dashboard.selectedRunIds.map((runId) => {
    const run = dashboard.availableRuns.find((entry) => entry.run_id === runId);
    const metric = dashboard.metrics[runId];
    const context = dashboard.context[runId];

    return {
      runId,
      label: context?.name ?? run?.label ?? runId,
      strategy: context?.strategy ?? run?.strategy ?? runId,
      metric,
    };
  });

  const summarySeries: any[] = dashboard.performance.series.map((series) => ({
    name: series.name,
    type: "line" as const,
    data: series.points.map((point) => [point.date, point.value]),
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2 },
    emphasis: { focus: "series" as const },
  }));

  if (dashboard.performance.benchmark) {
    summarySeries.push({
      name: dashboard.performance.benchmark.name,
      type: "line" as const,
      data: dashboard.performance.benchmark.points.map((point) => [point.date, point.value]),
      showSymbol: false,
      smooth: true,
      lineStyle: { width: 2, type: "dashed" as const },
      emphasis: { focus: "series" as const },
    });
  }

  const chartOption = {
    backgroundColor: "transparent",
    color: ["#d88d36", "#f3c97f", "#8bc6ff", "#f08f70"],
    grid: {
      left: 4,
      right: 14,
      top: 12,
      bottom: 24,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis" as const,
      valueFormatter: (value: number) => formatMoney(value),
    },
    legend: {
      show: summarySeries.length > 1,
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
    yAxis: {
      type: "value" as const,
      axisLabel: {
        color: "#b8aca0",
        formatter: (value: number) => formatMoney(value),
      },
      splitLine: {
        lineStyle: { color: "rgba(255, 248, 240, 0.08)" },
      },
    },
    series: summarySeries,
  };

  return (
    <motion.section
      className="workspace-strip performance-strip"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="workspace-strip-copy">
        <p className="section-label">Performance plane</p>
        <h2>{title}</h2>
        <p className="workspace-summary">
          {selectedRuns.length} active run{selectedRuns.length === 1 ? "" : "s"} inside the 1W1A live workspace.
        </p>
      </div>

      <div className="workspace-strip-grid">
        <motion.div className="workspace-chart-plane" whileHover={{ scale: 1.005 }}>
          <EChartsReact option={chartOption} style={{ height: 360, width: "100%" }} />
        </motion.div>

        <div className="workspace-metrics">
          {selectedRuns.map((run) => (
            <article key={run.runId} className="workspace-metric-line">
              <div className="workspace-metric-head">
                <strong>{run.label}</strong>
                <span>{run.strategy}</span>
              </div>
              <div className="workspace-metric-row">
                <span>CAGR {run.metric ? formatPercent(run.metric.cagr) : "n/a"}</span>
                <span>Sharpe {run.metric ? run.metric.sharpe.toFixed(2) : "n/a"}</span>
              </div>
              <div className="workspace-metric-row">
                <span>Max drawdown {run.metric ? formatPercent(run.metric.max_drawdown) : "n/a"}</span>
                <span>Turnover {run.metric ? formatPercent(run.metric.avg_turnover) : "n/a"}</span>
              </div>
              <div className="workspace-metric-row workspace-metric-accent">
                <span>Final equity</span>
                <span>{run.metric ? formatMoney(run.metric.final_equity) : "n/a"}</span>
              </div>
            </article>
          ))}
        </div>
      </div>
    </motion.section>
  );
}
