# Crypto Strategy Factory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first real crypto strategy factory layer on top of the current `crypto/` scaffold: 8-10 families, 30-50 candidates, robust/cost-aware scoring, orthogonality filtering, top-10 basket selection, event-driven hierarchical allocation, and strategy docs.

**Architecture:** Extend the existing `crypto/` package with focused factory modules rather than creating another parallel stack. Keep the flow explicit: candidate generation -> scoring -> orthogonality filtering -> allocation -> reporting. Preserve current package boundaries and use `crypto/paper` / `crypto/reporting` as downstream consumers of the chosen basket.

**Tech Stack:** Python, dataclasses, current `crypto/` package, pytest/unittest crypto tests, existing reporting models/graph series.

---

## File structure (planned)
- Create: `crypto/factory/__init__.py`
- Create: `crypto/factory/candidates.py`
- Create: `crypto/factory/scoring.py`
- Create: `crypto/factory/selection.py`
- Create: `crypto/factory/allocation.py`
- Create: `crypto/factory/registry.py`
- Create: `crypto/strategies/docs/`
- Modify: `crypto/strategies/registry.py`
- Modify: `crypto/reporting/builder.py`
- Create/modify tests under `crypto/tests/`
- Update: `docs/crypto-research-factory.md`

### Task 1: Strategy family expansion + docs scaffold
**Files:**
- Modify: `crypto/strategies/registry.py`
- Create: `crypto/strategies/docs/*.md`
- Test: `crypto/tests/test_strategies.py`

- [ ] Add the 5 new approved families to the registry and keep defaults explicit.
- [ ] Add one markdown doc per strategy/family under `crypto/strategies/docs/`.
- [ ] Verify family count and docs presence.

### Task 2: Parametric candidate generation
**Files:**
- Create: `crypto/factory/candidates.py`
- Test: `crypto/tests/test_factory_candidates.py`

- [ ] Implement fixed-grid seed generation.
- [ ] Implement bounded adaptive/random expansion around promising regions.
- [ ] Verify candidate pool size and deterministic seed behavior.

### Task 3: Strategy scoring
**Files:**
- Create: `crypto/factory/scoring.py`
- Test: `crypto/tests/test_factory_scoring.py`

- [ ] Implement score = post-cost performance + robustness, with explicit turnover/cost penalty.
- [ ] Encode robustness = OOS + parameter sensitivity + regime stability.
- [ ] Verify cost sensitivity and robustness breakdowns are testable separately.

### Task 4: Orthogonality filtering + family cap
**Files:**
- Create: `crypto/factory/selection.py`
- Test: `crypto/tests/test_factory_selection.py`

- [ ] Implement return-correlation + family-diversity filtering.
- [ ] Enforce max 3 strategies per family.
- [ ] Verify top-10 basket selection from 30-50 candidates.

### Task 5: All-in-one allocator
**Files:**
- Create: `crypto/factory/allocation.py`
- Test: `crypto/tests/test_factory_allocation.py`

- [ ] Implement hierarchical weighting by family first, strategy second.
- [ ] Support event-driven recompute triggers.
- [ ] Keep staged/split execution metadata in the output plan.
- [ ] Verify 10 active strategies collapse into one portfolio-level position plan.

### Task 6: Reporting integration
**Files:**
- Modify: `crypto/reporting/builder.py`
- Modify/create: `crypto/reporting/models.py`
- Test: `crypto/tests/test_reporting.py`

- [ ] Add factory/allocator outputs into reporting surfaces.
- [ ] Keep graph-ready results explicit.
- [ ] Verify reports can show strategy catalog, selected basket, and graph series for aggregate performance.

### Task 7: Documentation + cleanup
**Files:**
- Update: `docs/crypto-research-factory.md`
- Test/verify: focused crypto suite

- [ ] Document the factory flow and allocator rules.
- [ ] Refactor only where boundaries are still muddy.
- [ ] Run focused crypto tests and then full crypto tests.

## Self-review notes
- This plan is intentionally focused on the factory/allocator layer, not another exchange/runtime rewrite.
- `crypto/paper` and `crypto/reporting` are treated as already landed dependencies and only extended where needed.
- The plan stays aligned with the user’s approved A->B->C ordering and the locked allocator choices.
