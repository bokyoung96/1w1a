---
title: Dashboard Metadata & Detail Panel Redesign
date: 2026-04-06
author: codex
---

# Goal

Expose the launch metadata and current focus metrics exactly where they are needed:
- Launch statistics (start, end, benchmark context, and trading cost assumptions) should live in the hero strip so they are visible immediately without scrolling.
- The research detail panel should surface Sharpe, Calmar, Information Ratio, Hit Rate, profit/risk, and the toughest open drawdown recovery period (if any) while removing the old drawdown table and run metadata drawer.
- Detail focus copy must render consistently (e.g., “Focus: Strategy · Momentum”).

# Scope & Changes

1. **Performance Strip**
   - Keep the metadata rail within the hero comparison panel but trim it to a single grid showing: configured start date, configured end date, benchmark summary (shared name or per-strategy list), and a “costs” summary that lists fee / sell tax / slippage.
   - Ensure the focus banner uses a reusable normalization helper so legacy “쨌” separators render as `·`.
   - Remove the redundant `ContextDrawer` component and drop the “Run metadata” section from `App.tsx`.

2. **Research Detail Panel**
   - Replace the dual tables (metrics + drawdown episodes) with a compact metrics grid featuring Sharpe, Calmar, Information Ratio, Hit Rate, Profit/Risk, and the currently “toughest” open drawdown (longest recovery duration or “in progress” state).
   - When no active drawdown exists, show “None in progress” plus a short note.
   - Keep the contribution/benchmark notes below the grid but update their language to reflect the new metrics.

3. **Exposure & Research Workspace**
   - Leave `ResearchWorkspace` charts unchanged; drop the `ContextDrawer` sibling so Exposure + Research fill the available height.
   - Adjust CSS spacing (`.detail-band`, `.cinema-workspace`) so the removed drawer doesn’t leave a gap.

4. **Types & API**
   - No backend contract change is required—the existing `DashboardMetricModel` already provides the needed values (Sharpe, calmar, information_ratio, etc.).

5. **Testing**
   - Update `App.test.tsx` expectations for the trimmed metadata rail and the new research detail metrics.
   - Remove selectors that depended on the old “Run metadata” drawer or drawdown table.

The next step is to invoke `writing-plans` after you review and confirm this spec.
