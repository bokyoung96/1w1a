# 1w1a Portfolio Construction And Staged Policy Design

## Goal

Extend `1w1a` so the current weight-based backtesting stack can support:

- composable long-only, long-short, dollar-neutral, and sector-neutral portfolio construction
- reusable signal outputs that include both alpha and context
- staged entry and staged exit policies that preserve the construction budget
- bucket-level position ledgers for analysis and reporting
- fast execution paths that keep the current vectorized engine model intact

The design must support this rollout order:

1. long-short and neutral portfolio construction
2. staged entry and staged exit overlays on top of construction results

## Scope

### In scope

- introducing a `Signal -> Portfolio Construction -> Position Policy -> Engine -> Reporting` flow
- separating raw alpha from context frames
- object-based construction rules such as long-only, long-short, dollar-neutral, and sector-neutral
- a budget-preserving staged policy layer that overlays construction outputs
- bucket-level long-format ledgers for staged entry and staged exit
- validation hooks for construction and policy contract checks
- performance-oriented implementation boundaries for vectorized and path-dependent logic

### Out of scope for this design

- borrow inventory constraints
- short borrow costs
- margin modeling
- event-driven execution engine replacement
- intraday execution
- unconstrained budget-expanding overlays by default

## Design Principles

- Keep the existing weight-based engine boundary intact.
- Separate alpha generation from portfolio construction.
- Make portfolio construction reusable across different signal sources.
- Make staged entry and exit an overlay, not a second strategy layer.
- Preserve construction budgets by default.
- Use vectorized computation wherever possible.
- Restrict path-dependent logic to the smallest possible scan surface.
- Store rich intermediate outputs when they remove ambiguity for later layers.

## Architecture

The target stack is:

```text
Signal -> Portfolio Construction -> Position Policy -> Engine -> Reporting
```

### Signal

The signal layer produces a `SignalBundle`, not a single score frame.

It is responsible for:

- raw alpha production
- context frame production
- data alignment and masking needed for later decisions

It is not responsible for:

- portfolio sizing
- long-short balancing
- neutralization
- staged entry or staged exit logic

### Portfolio Construction

The construction layer consumes a `SignalBundle` and produces a `ConstructionResult`.

It is responsible for:

- selection
- long and short leg sizing
- dollar-neutral balancing
- sector-neutral hard constraints
- outputting the base target position before any time-staged execution overlay

It is not responsible for:

- entry timing after selection
- staged adds or staged trims
- bucket state

### Position Policy

The position policy layer consumes a `ConstructionResult` and produces a `PositionPlan`.

It is responsible for:

- splitting the base target position over time
- staged entry
- staged exit
- bucket state transitions
- bucket-level ledger output

It must be an overlay. It must not:

- recompute alpha
- re-run selection
- redefine the construction budget
- exceed construction gross, net, or group budgets by default

### Engine

The engine remains a weight-based execution engine.

It consumes:

- aggregate `target_weights`

It does not need bucket awareness to remain fast.

### Reporting

Reporting continues to consume the aggregate run output and is extended to optionally consume:

- bucket ledger
- bucket weights
- staged policy metadata

## Core Contracts

### `SignalBundle`

Recommended fields:

- `alpha: pd.DataFrame`
- `context: dict[str, pd.DataFrame]`
- `meta: dict[str, pd.DataFrame | pd.Series] | None = None`

Expected context examples:

- `sector`
- `tradable`
- `liquidity_ok`
- `breakout_flag`
- `rebreakout_flag`
- `vol_regime`

The bundle contract should not require the alpha output to be only one score interpretation forever, but the first implementation should center on a primary `alpha` frame plus auxiliary context.

### `ConstructionRule`

Recommended interface:

- `build(bundle: SignalBundle) -> ConstructionResult`

This object is the reusable portfolio rule. It allows the same alpha source to be compared across multiple construction styles.

Examples:

- `LongOnlyTopN`
- `LongShortTopBottom`
- `SectorNeutralTopBottom`
- later: `BetaNeutralBySector`

### `ConstructionResult`

Recommended fields:

- `base_target_weights: pd.DataFrame`
- `selection_mask: pd.DataFrame`
- `group_budget_long: pd.DataFrame | None`
- `group_budget_short: pd.DataFrame | None`
- `meta: dict[str, pd.DataFrame | pd.Series]`

This output must be richer than a weight frame because the position policy should not need to reverse-engineer how the construction result was created.

### `PositionPolicy`

Recommended interface:

- `apply(construction: ConstructionResult, market: MarketData, bundle: SignalBundle) -> PositionPlan`

The policy is a budget-preserving overlay by default.

### `PositionPlan`

Recommended fields:

- `target_weights: pd.DataFrame`
- `bucket_ledger: pd.DataFrame | None`
- `bucket_meta: dict[str, pd.DataFrame | pd.Series]`
- `validation: dict[str, object] | None = None`

The engine consumes `target_weights`. Reporting and diagnostics consume the bucket ledger and bucket metadata.

## Reserved Metadata Keys

To avoid contract drift, reserve the following minimum keys from the start.

### In `SignalBundle.context`

- `sector`
- `tradable`
- `liquidity_ok`

### In `ConstructionResult.meta`

- `selected_long`
- `selected_short`
- `group_id`
- `group_budget_long`
- `group_budget_short`
- `constraint_violation`

Additional keys may be added later, but these reserved names should remain stable.

## Long-Short And Neutral Construction

### Phase 1 target rules

- `LongOnlyTopN`
- `LongShortTopBottom`
- `SectorNeutralTopBottom`

### Neutrality rules

- default long-short neutrality is `dollar-neutral`
- `sector-neutral` is a hard construction constraint
- `beta-neutral` is deferred

### Sector-neutral definition

The primary sector-neutral implementation should use a hard within-sector selection rule:

- rank within sector
- choose long and short names within that sector
- allocate long and short gross budget within sector
- aggregate across sectors

This is preferred over a soft after-the-fact sector exposure adjustment.

## Position Policy Design

### Default behavior

The default policy is budget-preserving.

If construction assigns a symbol a target of `6%`, the policy may release that as:

- `2% + 2% + 2%`

It may not turn that symbol into `8%` unless an explicit future option allows budget expansion.

### Policy responsibility

The policy should only modify execution timing and staging of a construction output.

Examples:

- first bucket enters on initial breakout
- second bucket enters after `+5%` from bucket one anchor
- third bucket enters after pullback and rebreakout
- partial trim after a threshold gain
- full exit after a stop, trail, timeout, or reverse signal

### Bucket model

The policy should treat staged entry and staged exit as transitions on fixed budget slices.

This means:

- bucket count is small and explicit
- each bucket owns a portion of the construction budget
- entry and exit are both bucket state transitions

This is simpler and faster than a free-form per-position object model.

## Bucket Ledger

The bucket ledger should be stored in long format.

Recommended columns:

- `date`
- `symbol`
- `side`
- `bucket_id`
- `stage_index`
- `target_weight`
- `actual_weight`
- `target_qty`
- `actual_qty`
- `entry_price`
- `mark_price`
- `bucket_return`
- `state`
- `event`
- `construction_group`
- `budget_id`

The design should prefer:

- dense array or matrix representation during calculation
- long-format output at persistence boundaries

## Validation Hooks

Add validation at the strategy contract boundary, not inside the execution engine.

Minimum validation checks:

- selected names do not violate tradability or liquidity masks
- group budgets do not exceed declared long and short budget totals
- net exposure stays within configured tolerance
- sector-neutral construction satisfies its hard constraints within tolerance
- policy output does not exceed construction budget
- aggregate target weights equal the sum of bucket-level target weights within tolerance

These checks belong in a portfolio validation layer rather than in engine core logic.

## Performance Strategy

Performance is a first-class design constraint.

### Keep the engine simple

The existing engine already handles vectorized weight execution. Do not replace it with a generic event-driven engine for this work.

### Use the right compute style by layer

#### Signal and construction

Prefer vectorized table operations.

Good candidates for `pandas` or `polars`:

- joins against sector and other context frames
- filtering and masking
- cross-sectional ranks
- sector grouping
- budget table construction
- long-format intermediate diagnostics

#### Position policy

Use two stages:

1. precompute all vectorizable eligibility masks
2. run the smallest possible path-dependent scan for bucket state transitions

Good precompute examples:

- `eligible_entry`
- `eligible_add_k`
- `eligible_reduce_k`
- `eligible_exit`
- breakout and rebreakout flags
- rolling bands
- volatility regimes

Good scan-state examples:

- `bucket_active`
- `bucket_filled`
- `entry_anchor_price`
- `peak_since_entry`
- `days_since_entry`

### Prefer dense arrays over Python objects

Avoid per-symbol strategy objects and bucket objects in hot loops.

The expected fast path is:

- vectorized table preparation in `pandas` or `polars`
- dense `numpy` arrays for state transitions
- conversion back to `pandas` at interface boundaries

### Keep bucket count small

Bucket count should be fixed and intentionally small, such as `2` to `5`.

This keeps the path-dependent portion bounded by:

- dates x symbols x buckets

### Ledger is not the compute core

Long-format ledgers are excellent for persistence and reporting, but they should be produced after the main calculation rather than serving as the primary in-memory execution format.

## Proposed File Layout

```text
backtesting/
  signals/
    base.py
    momentum.py
    op_fwd.py
  construction/
    base.py
    long_only.py
    long_short.py
    sector_neutral.py
  policy/
    base.py
    pass_through.py
    staged.py
  validation/
    portfolio.py
  strategies/
    base.py
    registry.py
```

### Responsibilities

- `backtesting/signals/`: alpha and context producers
- `backtesting/construction/`: reusable portfolio rule objects
- `backtesting/policy/`: budget-preserving overlays and staged bucket logic
- `backtesting/validation/portfolio.py`: strategy-contract validation
- `backtesting/strategies/`: composition and registry boundary for CLI and dashboard compatibility

## Integration Plan

### Phase 1

Refactor current strategies into composable parts without changing the engine boundary.

- existing `momentum` becomes `SignalProducer + LongOnlyTopN + pass-through policy`
- existing `op_fwd_yield` becomes `SignalProducer + LongOnlyTopN + pass-through policy`
- add long-short and sector-neutral variants as new registered strategies

### Phase 2

Add staged overlays while keeping construction outputs as the base budget contract.

- add `BudgetPreservingStagedPolicy`
- add bucket ledger persistence
- add staged-entry and staged-exit reporting surfaces

## Testing Strategy

### Construction tests

- long-only selection correctness
- long-short leg balance
- dollar-neutral net exposure
- sector-neutral hard-constraint enforcement
- insufficient names in a sector shrink exposure instead of violating rules

### Policy tests

- staged entry releases budget in the correct order
- staged exit trims only from active buckets
- policy never exceeds construction budget
- aggregated weights equal bucket totals

### Performance tests

- construction remains vectorized on realistic cross-sections
- staged policy runtime scales with bounded bucket count
- no Python object explosion in symbol-by-symbol loops

## Decisions Fixed By This Design

- rollout order is construction first, staged policy second
- signal outputs include raw alpha plus context
- construction is object-based and reusable
- position policy is an overlay
- default staged behavior preserves budget
- default long-short neutrality is dollar-neutral
- primary neutral implementation priority is hard sector-neutral construction
- bucket ledgers are persisted in long format
- validation hooks are part of the design
- speed is prioritized through vectorization and dense-state scans rather than an event-driven engine rewrite
