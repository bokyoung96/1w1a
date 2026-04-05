# Dashboard Chart Followups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make return distribution visibly readable as a chart and change sector weight visualization to a clearer picture while preserving the existing dashboard flow.

**Architecture:** Keep the existing payload contract and improve only the frontend chart transforms in the research workspace. Use a numeric-axis distribution chart for return bins and a sector-weight heatmap so the visuals are denser and easier to read.

**Tech Stack:** React, TypeScript, Vitest, ECharts

---

### Task 1: Red tests for the new chart shapes

**Files:**
- Modify: `dashboard/frontend/src/components/App.test.tsx`

- [ ] Add a failing test that expects return distribution to render on a numeric x-axis as a line/area distribution chart.
- [ ] Add a failing test that expects sector weight visualization to render as a heatmap with run/sector rows.
- [ ] Run `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx` and confirm the new expectations fail.

### Task 2: Implement the new chart transforms

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`

- [ ] Replace the categorical return-distribution bar chart with a numeric distribution curve built from histogram bin midpoints.
- [ ] Replace the sector-weight line chart with a heatmap option derived from the filtered sector-weight series.
- [ ] Keep the existing empty-state handling and sector filter behavior intact.
- [ ] Re-run `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx` and confirm it passes.

### Task 3: Verify and finish

**Files:**
- Add: `docs/superpowers/plans/2026-04-05-dashboard-chart-followups.md`

- [ ] Run `cd dashboard/frontend && npm test -- --run`
- [ ] Run `cd dashboard/frontend && npm run build`
- [ ] Commit the branch changes.
- [ ] Merge back into `main`, push `origin/main`, and remove the temporary worktree and branch.
