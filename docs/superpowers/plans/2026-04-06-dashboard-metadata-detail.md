# Dashboard Metadata & Detail Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Trim the hero metadata rail to start/end/benchmark/costs, normalize focus text, remove the ContextDrawer, and replace the Research Detail tables with a compact metrics grid plus the toughest drawdown highlight.

**Architecture:** Update PerformanceStrip for the refreshed launch rail and focus banner, remove ContextDrawer, and rework ResearchDetailPanel to render the requested metrics directly from dashboard.metrics. Keep the rest of the workspace unchanged while adjusting layout spacing after the drawer removal.

**Tech Stack:** React + TypeScript, Vitest, ECharts, FastAPI payload.

---

### Task 1: Hero Metadata Grid + Focus Copy

**Files:**
- Modify: dashboard/frontend/src/components/PerformanceStrip.tsx
- Modify: dashboard/frontend/src/app/App.tsx
- Modify: dashboard/frontend/src/components/App.test.tsx

- [ ] **Step 1: Normalize focus labels**

`	sx
function normalizeFocusLabel(value: string) {
  return value.replace(/\s(?:쨌|夷?)\s/g, 
