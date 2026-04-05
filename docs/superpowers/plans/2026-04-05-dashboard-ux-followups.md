# Dashboard UX Followups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the sector attribution warning, make the research charts easier to read, and add explicit sector selection controls so users can choose which sector series to compare.

**Architecture:** Keep the existing dashboard payload shape, but tighten the backend attribution calculation to avoid deprecated pandas behavior and refine the frontend research workspace with lighter copy, no-data handling, and local sector filtering controls. Preserve saved-run compatibility and avoid another API contract change unless tests prove it is necessary.

**Tech Stack:** Python, pandas, FastAPI backend payload serializers, React, TypeScript, Vitest, pytest, ECharts

---

### Task 1: Remove the sector attribution warning at the source

**Files:**
- Modify: `backtesting/reporting/benchmarks.py`
- Test: `tests/reporting/test_snapshots.py`

- [ ] Add a regression test that exercises sector contribution generation and fails if pandas emits the deprecated `pct_change` warning.
- [ ] Run the focused pytest command and confirm the new test fails for the expected warning-sensitive path.
- [ ] Update sector attribution return generation to avoid the implicit forward-fill behavior and keep finite numeric output.
- [ ] Re-run the focused pytest command and confirm it passes.

### Task 2: Make research figures clearer and resilient when data is sparse

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
- Modify: `dashboard/frontend/src/components/ResearchDetailPanel.tsx`
- Modify: `dashboard/frontend/src/app/dashboard.css`
- Test: `dashboard/frontend/src/components/App.test.tsx`

- [ ] Add a failing frontend test covering simpler chart copy and visible fallback behavior for empty research data.
- [ ] Run the focused Vitest command and confirm the new expectation fails before implementation.
- [ ] Simplify figure titles/subtitles, remove “layer/area” wording, and add explicit no-data messaging for figures such as return distribution.
- [ ] Re-run the focused Vitest command and confirm it passes.

### Task 3: Add explicit sector filters for research charts

**Files:**
- Modify: `dashboard/frontend/src/components/ResearchWorkspace.tsx`
- Modify: `dashboard/frontend/src/components/App.test.tsx`
- Modify: `dashboard/frontend/src/lib/types.ts` only if a new lightweight UI type is required

- [ ] Add a failing frontend test that selects sectors explicitly and verifies only the chosen sector series are sent to the sector charts.
- [ ] Run the focused Vitest command and confirm the new expectation fails.
- [ ] Implement local sector filter controls with an “All sectors” reset and a sensible default that limits clutter when nothing is manually selected.
- [ ] Re-run the focused Vitest command and confirm it passes.

### Task 4: Verify, commit, merge, and clean up

**Files:**
- Modify: `README.md` only if the visible dashboard behavior needs a brief note

- [ ] Run: `pytest tests/reporting/test_snapshots.py tests/dashboard/backend/test_dashboard_api.py -q`
- [ ] Run: `pytest tests/dashboard tests/reporting -q`
- [ ] Run: `cd dashboard/frontend && npm test -- --run`
- [ ] Run: `cd dashboard/frontend && npm run build`
- [ ] Run: `python dashboard/run.py --help`
- [ ] Commit the feature branch changes with a concise message.
- [ ] Fast-forward or merge back into `main`, re-run the verification needed on the merged result, push `origin/main`, and remove the temporary worktree and branch.
