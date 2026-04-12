# 52-Week Breakout Strategies Design

## Goal

Add two real breakout strategies that sit on top of the existing composable strategy and staged-policy layers:

1. `breakout_52w_simple`
2. `breakout_52w_staged`

At the same time, remove recently added example-only strategy variants that are not part of the desired product surface.

The deliverable is not a new engine. The engine and staged-policy infrastructure already exist. The focus here is strategy implementation, verification, and running the strategies on local data to inspect actual results.

## Scope

### In scope

- Remove example strategy registrations and related README/test exposure for:
  - `momentum_long_short`
  - `momentum_sector_neutral`
  - `momentum_sector_neutral_staged`
- Add two production-facing breakout strategies under `backtesting/strategies/`
- Add or update tests so both strategies are exercised through the public registry and runner
- Run local backtests for both strategies and capture their output locations and summary results
- If tests and backtests are green, commit the work and merge the current branch into `main`

### Out of scope

- New generic portfolio-construction abstractions
- Replacing the staged engine/policy kernel
- Multi-asset or short-selling breakout variants
- UI/dashboard work

## Strategy Definitions

### 1. `breakout_52w_simple`

This is a long-only breakout strategy with one-shot entry.

#### Entry

- A symbol becomes eligible when the close breaks above the rolling 252-trading-day high.
- Use prior-history comparison so the breakout is based on information available before the current bar.

#### Positioning

- Equal-weight across active names.
- Full target allocation is taken immediately on entry.

#### Exit

- Exit when the close breaks below the rolling 20-day low.

#### Intent

- This provides the baseline "plain breakout" behavior against which the staged variant can be compared.

### 2. `breakout_52w_staged`

This is a long-only breakout strategy with three-stage entry and three-stage exit.

#### Stage 1 entry

- First entry occurs on the initial 252-trading-day breakout.

#### Stage 2 and 3 entry

- Additional entries are allowed only after:
  - the symbol pulls back to the 10-day moving average area, and
  - then reclaims the short-term trend by moving back above the 10-day moving average
- This is intentionally simpler than a strict prior-peak recapture rule because the immediate goal is to validate that the strategy layer can express staged breakout behavior on top of the existing framework.
- The staged implementation should use the existing staged-policy infrastructure or an equivalent strategy-local state machine that preserves the same bucket-ledger contract.

#### Position sizing

- Total target budget per selected symbol is split equally across three buckets.
- The strategy must remain budget-preserving: staged entry releases the already-assigned budget over time rather than creating extra exposure.

#### Exit / staged exit

- The staged strategy exits in three steps.
- Default rule set:
  - first reduction on 20-day low break
  - second reduction if the exit condition persists
  - final exit of remaining size if the condition still persists
- The exact implementation may use the staged-policy contract and bucket ledger, but behavior must remain visibly staged rather than collapsing to full liquidation on the first signal.

#### Intent

- This is the practical comparison point versus the simple breakout strategy: same broad thesis, slower capital deployment, slower liquidation.

## Implementation Shape

### Cleanup

- Remove the example strategy files or registrations that were added only to demonstrate long-short / sector-neutral / staged composition.
- Keep the shared infrastructure intact:
  - composable strategy layer
  - construction rules
  - staged policy kernel
  - position-plan validation and ledger persistence

### New strategy files

Expected target layout:

- `backtesting/strategies/breakout_simple.py`
- `backtesting/strategies/breakout_staged.py`

These files should own the strategy-specific logic and expose registered strategies through the existing registry path.

### Shared signal logic

- It is acceptable to keep breakout-specific signal producers local to these strategy modules if that keeps the implementation focused.
- The signal/context output should include the data needed for:
  - breakout detection
  - 20-day low exit detection
  - 10-day moving-average pullback and re-breakout detection
  - staged bucket transitions

### Registry surface

After implementation, the intended strategy names are:

- `breakout_52w_simple`
- `breakout_52w_staged`
- existing supported non-example strategies should remain, such as `momentum` and `op_fwd_yield`

## Testing Requirements

The new work must be test-driven.

### Required coverage

- Registry exposes the two breakout strategies
- Baseline breakout strategy opens and closes under the expected breakout / 20-day-low rules
- Staged breakout strategy:
  - opens first bucket on initial breakout
  - adds later buckets only after pullback and re-breakout conditions
  - performs staged reductions rather than immediate full liquidation
- Runner-level test persists a non-empty `bucket_ledger.parquet` for the staged breakout strategy

### Cleanup coverage

- Tests and documentation tied only to the removed example strategies should be updated or removed so the test suite reflects the final public surface

## Backtest And Output Requirements

After tests pass, run both strategies on the local dataset already present in the repo.

Minimum required outputs to inspect and report:

- output directory for each run
- summary metrics from `summary.json` or runner summary object
- confirmation that the staged strategy writes `positions/bucket_ledger.parquet`

The final user-facing report does not need a long narrative, but it must state what was run and where the results were written.

## Git And Merge Requirements

If and only if the relevant tests and backtests pass:

1. commit the strategy changes
2. merge the current working branch into `main`

The unrelated untracked planning document under `docs/superpowers/plans/` is not part of this change and should not be pulled into the implementation commit unless explicitly needed.

## Risks To Watch

- Using current-bar information when defining 52-week breakout or 20-day-low exits
- Letting staged entry rules fire just because a symbol has enough history instead of because it is actually selected
- Collapsing staged exit into immediate full liquidation
- Leaving stale test/README references to removed example strategies
- Running backtests on insufficient warmup history for 252-day breakout calculations
