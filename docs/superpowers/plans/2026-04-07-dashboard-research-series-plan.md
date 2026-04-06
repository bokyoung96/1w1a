# Research Series Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the research detail metrics strip and the strategy-level sector trend charts described in the spec.

**Architecture:** Reuse the existing ResearchDetailPanel helpers to emit a single responsive metric strip and toughest-drawdown note, then add a new “Strategy sector trends” block in ResearchWorkspace that iterates through each selected run and renders normalized weight + cumulative contribution cards. CSS adjustments keep all new blocks aligned with the current study.

**Tech Stack:** React + TypeScript, ECharts, Vitest, CSS modules in `dashboard/frontend/src/app/dashboard.css`

---

### Task 1: Compact research detail metrics strip

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchDetailPanel.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/App.test.tsx` (assert new content appears via DOM queries)

- [ ] **Step 1: Update metric data for the new chip order**

```tsx
const metricOrder: Array<[string, string]> = [
  ["Cumulative return", formatPercent(metric?.cumulativeReturn ?? 0, 1)],
  ["Max drawdown", formatPercent(metric?.maxDrawdown ?? 0, 1)],
  ["Sharpe", formatNumberValue(metric?.sharpe ?? 0, 2)],
  ["Calmar", formatNumberValue(metric?.calmar ?? 0, 2)],
  ["Information Ratio", formatNumberValue(metric?.informationRatio ?? 0, 2)],
  ["Hit Rate", diffs.length ? formatPercent(hitRate, 1) : "n/a"],
  ["Profit / Risk", formatRewardRisk(profitRisk)],
];
```

- [ ] **Step 2: Render the metric row as a single flex/ grid strip and keep only the toughest drawdown banner**

```tsx
<div className="detail-metric-strip detail-metric-strip--row">
  {metricOrder.map(([label, value]) => (
    <div key={label} className="detail-metric-chip">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  ))}
</div>
```

Remove the `detail-sector-charts` block entirely from this component, leaving only the toughest drawdown summary beneath the metric strip.

- [ ] **Step 3: Simplify CSS to support a single responsive row**

Add a modifier (`.detail-metric-strip--row`) that uses `display: grid` / `grid-auto-flow: column` with wrapping and tighter spacing, and ensure the toughest drawdown text still has proper spacing below.

- [ ] **Step 4: Run existing tests to confirm nothing regresses**

Run `npm run test -- --watch=false src/components/App.test.tsx` and expect the suite to pass; the new DOM structure should still fulfill App-level expectations.

- [ ] **Step 5: Commit the detail-panel changes**

```bash
git add dashboard/frontend/src/components/ResearchDetailPanel.tsx dashboard/frontend/src/app/dashboard.css
git commit -m "feat: compact research detail metrics strip"
```

### Task 2: Strategy sector trends charts in ResearchWorkspace

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/ResearchWorkspace.test.tsx` (create if missing) or `App.test.tsx`

- [ ] **Step 1: Build per-strategy chart metadata**

```tsx
const strategySectorTrends = runIds.map((runId) => {
  const label = runLabel(dashboard, runId);
  return {
    runId,
    label,
    weightOption: buildNormalizedSectorWeightsOption(dashboard, runId),
    contributionOption: buildCumulativeContributionOption(dashboard, runId),
    hasData:
      (dashboard.research.sectorWeightSeries[runId] ?? []).length > 0 &&
      (dashboard.research.sectorContributionSeries[runId] ?? []).length > 0,
  };
});
```

- [ ] **Step 2: Insert a new “Strategy sector trends” section between the existing charts and ResearchDetailPanel**

```tsx
<div className="research-grid research-sector-trends">
  {strategySectorTrends.map(({ runId, label, weightOption, contributionOption, hasData }) => (
    <div key={runId} className="research-sector-trends__pair">
      <ResearchFigure
        title={`Sector weights (normalized 100%) — ${label}`}
        subtitle="How exposure shares stack up."
        option={weightOption}
        isEmpty={!hasData}
        emptyMessage="No sector data for this strategy."
      />
      <ResearchFigure
        title={`Sector contribution (cumulative) — ${label}`}
        subtitle="Cumulative attribution per sector."
        option={contributionOption}
        isEmpty={!hasData}
        emptyMessage="No contribution data for this strategy."
      />
    </div>
  ))}
</div>
```

Update the layout to ensure the new section uses a responsive grid that accommodates the pair of charts per strategy, e.g., `.research-sector-trends` with column wrapping.

- [ ] **Step 3: Remove the old “Sector contribution series / Sector weight series” ResearchFigures at the bottom**

Delete the final research-grid block that previously rendered those figures so only the new strategy-trends section shows sector data.

- [ ] **Step 4: Adjust CSS for the new section**

Add utilities (e.g., `.research-sector-trends`, `.research-sector-trends__pair`) in `dashboard.css` with appropriate grid/column spacing to keep cards aligned and wide enough for chart cards.

- [ ] **Step 5: Run targeted tests covering ResearchWorkspace**

Run `npm run test -- --watch=false src/components/ResearchWorkspace.test.tsx` or the relevant overall suite (`npm run test -- --watch=false src/components/App.test.tsx`) and expect pass.

- [ ] **Step 6: Commit the workspace changes**

```bash
git add dashboard/frontend/src/components/ResearchWorkspace.tsx dashboard/frontend/src/app/dashboard.css
git commit -m "feat: add strategy sector trend charts"
```

### Task 3: Update component tests/assertions

**Files:**
- Modify: `dashboard/frontend/src/components/App.test.tsx`
- Modify/Create: `dashboard/frontend/src/components/ResearchDetailPanel.test.tsx`
- Modify/Create: `dashboard/frontend/src/components/ResearchWorkspace.test.tsx`

- [ ] **Step 1: Write tests that assert the new metric strip content**

Add assertions that query each label (`Cumulative return`, `Max drawdown`, etc.) within `ResearchDetailPanel` and verify they render the expected formatted strings when `dashboard.metrics` is populated.

- [ ] **Step 2: Write tests validating the new strategy sector trend section exists**

Check that `ResearchWorkspace` renders the strategy-trends section, includes titles like “Sector weights (normalized 100%)” and that the mock `dashboard.research` data feeds through to `EChartsReact`.

- [ ] **Step 3: Run the tests**

Run `npm run test -- --watch=false src/components/ResearchDetailPanel.tsx src/components/ResearchWorkspace.tsx src/components/App.test.tsx`

- [ ] **Step 4: Commit the test updates**

```bash
git add dashboard/frontend/src/components/App.test.tsx dashboard/frontend/src/components/ResearchDetailPanel.test.tsx dashboard/frontend/src/components/ResearchWorkspace.test.tsx
git commit -m "test: cover refined research detail and sector charts"
```
