import EChartsReact from "echarts-for-react";
import { motion } from "framer-motion";

import { formatMoney, formatPercent } from "../lib/format";
import type { CryptoFactoryPayload } from "../lib/types";

type CryptoFactoryPanelProps = {
  factory: CryptoFactoryPayload;
};

function metricChips(factory: CryptoFactoryPayload) {
  return [
    ["Candidate pool", String(factory.summary.candidatePoolSize)],
    ["Selected basket", String(factory.summary.selectedBasketSize)],
    ["Registered strategies", String(factory.summary.registeredStrategyCount)],
    ["Family cap", `${factory.summary.familyCap} / family`],
    ["Paper Sharpe", factory.performanceSummary.paperSharpe.toFixed(2)],
    ["Total return", formatPercent(factory.performanceSummary.totalReturn, 1)],
  ];
}

function buildEquityOption(factory: CryptoFactoryPayload) {
  return {
    backgroundColor: "transparent",
    color: ["#f0a44b", "#c98f7d"],
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    legend: { top: 0, textStyle: { color: "#bdaea1", fontFamily: "inherit" } },
    grid: { left: 12, right: 18, top: 36, bottom: 20, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: factory.performance.equityCurve.map((point) => point.date),
      axisLabel: { color: "#bdaea1" },
    },
    yAxis: [
      {
        type: "value" as const,
        axisLabel: { color: "#bdaea1", formatter: (value: number) => formatMoney(value) },
        splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
      },
      {
        type: "value" as const,
        axisLabel: { color: "#bdaea1", formatter: (value: number) => formatPercent(value, 0) },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Aggregate equity",
        type: "line" as const,
        smooth: true,
        showSymbol: false,
        data: factory.performance.equityCurve.map((point) => point.value),
      },
      {
        name: "Drawdown",
        type: "line" as const,
        smooth: true,
        showSymbol: false,
        yAxisIndex: 1,
        data: factory.performance.drawdownCurve.map((point) => point.value),
      },
    ],
  };
}

function buildAllocationOption(factory: CryptoFactoryPayload) {
  return {
    backgroundColor: "transparent",
    color: ["#7cb8d8", "#8fa77f"],
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "rgba(15, 18, 21, 0.96)",
      borderColor: "rgba(240, 164, 75, 0.22)",
      textStyle: { color: "#f7f0e7" },
    },
    legend: { top: 0, textStyle: { color: "#bdaea1", fontFamily: "inherit" } },
    grid: { left: 12, right: 18, top: 36, bottom: 40, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: factory.familyAllocations.map((entry) => entry.family),
      axisLabel: { color: "#bdaea1", rotate: 24 },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#bdaea1", formatter: (value: number) => formatPercent(value, 0) },
      splitLine: { lineStyle: { color: "rgba(247, 240, 231, 0.08)" } },
    },
    series: [
      {
        name: "Family weight",
        type: "bar" as const,
        data: factory.familyAllocations.map((entry) => entry.weight),
      },
      {
        name: "Strategies",
        type: "line" as const,
        data: factory.familyAllocations.map((entry) => entry.strategyCount),
      },
    ],
  };
}

export function CryptoFactoryPanel({ factory }: CryptoFactoryPanelProps) {
  return (
    <motion.section
      className="detail-section crypto-factory-panel"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="detail-section-copy">
        <p className="section-label">Crypto factory</p>
        <h2>AI strategy basket, orthogonality, and allocation</h2>
        <p className="workspace-summary">
          Registered crypto strategies are expanded into a candidate pool, scored post-cost, filtered for
          orthogonality, then collapsed into one portfolio allocation plan for dashboard review.
        </p>
      </div>

      <div className="detail-metric-strip detail-metric-strip--row">
        {metricChips(factory).map(([label, value]) => (
          <div key={label} className="detail-metric-chip">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="detail-panel-grid crypto-factory-grid">
        <article className="detail-run-block">
          <div className="detail-subsection-head">
            <span>Aggregate performance preview</span>
            <span>{factory.summary.triggerReason}</span>
          </div>
          <EChartsReact option={buildEquityOption(factory)} style={{ height: 280, width: "100%" }} />
        </article>

        <article className="detail-run-block">
          <div className="detail-subsection-head">
            <span>Family allocation</span>
            <span>{factory.familyAllocations.length} families</span>
          </div>
          <EChartsReact option={buildAllocationOption(factory)} style={{ height: 280, width: "100%" }} />
        </article>
      </div>

      <div className="detail-panel-grid crypto-factory-grid">
        <article className="detail-run-block">
          <div className="detail-subsection-head">
            <span>Selected basket</span>
            <span>Top orthogonal candidates</span>
          </div>
          <div className="detail-column-labels crypto-factory-table-head">
            <span>Strategy</span>
            <span>Score</span>
            <span>Weight</span>
            <span>Corr</span>
          </div>
          <div className="detail-list">
            {factory.selectedBasket.map((strategy) => (
              <div key={strategy.candidateId} className="detail-list-row crypto-factory-table-row">
                <div>
                  <strong>{strategy.strategyName}</strong>
                  <p>{strategy.family}</p>
                </div>
                <span>{strategy.totalScore.toFixed(3)}</span>
                <span>{formatPercent(strategy.targetWeight, 1)}</span>
                <span>{formatPercent(strategy.maxPairwiseCorrelation, 1)}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="detail-run-block">
          <div className="detail-subsection-head">
            <span>Registry management</span>
            <span>{factory.registry.length} registered strategies</span>
          </div>
          <div className="crypto-registry-list">
            {factory.registry.map((entry) => (
              <div key={entry.name} className="crypto-registry-card">
                <div className="crypto-registry-head">
                  <strong>{entry.name}</strong>
                  <span className={`top-rail-pill ${entry.selected ? "is-selected" : ""}`}>
                    {entry.selected ? "selected" : "registered"}
                  </span>
                </div>
                <p>{entry.family}</p>
                <p>{entry.rationaleExcerpt}</p>
                <div className="crypto-registry-meta">
                  <span>{entry.candidateCount} candidates</span>
                  <span>top score {entry.topScore.toFixed(3)}</span>
                </div>
              </div>
            ))}
          </div>
        </article>
      </div>
    </motion.section>
  );
}
