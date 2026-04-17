# Crypto Research Factory

This document promotes the approved OMX launch brief into repo-local documentation so the implementation, test, and review lanes have one stable reference inside the codebase.

## Scope

The `crypto/` package is a separate research lane for perpetual-futures research. It is intentionally distinct from the existing stock-oriented `backtesting/` package.

Current v1 constraints:

- default exchange: `binance_perpetual`
- primary execution cadence: `15m`
- multi-frequency feature and data inputs are allowed for alpha capture
- no real-money execution logic
- keep diffs small, explicit, and reversible

## Approved strategy families

The current explicit registry covers these ten approved strategy families:

1. trend-following breakout
2. mean reversion
3. perp momentum / relative-strength rotation
4. funding-rate carry / funding-aware filter
5. volatility regime / breakout confirmation
6. trend pullback continuation
7. short-term reversal / exhaustion fade
8. volume / participation imbalance
9. basis / spread dislocation proxy
10. market structure / support-resistance reaction

Each registered family should keep a matching markdown brief under `crypto/strategies/docs/` so the research lane can review the family thesis without digging through code first.

## Promotion thresholds

Promotion and report outputs should use the approved research thresholds:

- out-of-sample Sharpe > `0.75`
- paper-trading Sharpe > `0.5`
- max drawdown < `15%`
- minimum paper window `30` days
- pairwise correlation threshold < `0.70`

## Package boundaries

Lane ownership should stay explicit in the package layout:

```text
crypto/
  domain/       # core market, contract, position, and run configuration models
  exchanges/    # exchange adapters and exchange-specific metadata
  strategies/   # alpha families and composition logic
  promotion/    # promotion rules and threshold evaluation
  validation/   # research validation and offline evaluation helpers
  paper/        # paper ledger, portfolio state, and paper-session persistence
  reporting/    # research summaries, paper-trading reports, and promotion output
```

The paper and reporting lanes should remain separate from:

- strategy definition logic
- exchange adapter details
- any live execution or order-routing behavior

## Lane 3 expectations: paper ledger and reporting

The paper and reporting surfaces are the operational record for the crypto research lane.

Minimum expectations:

- paper trading keeps a durable ledger for fills, fees, funding effects, exposure, and equity changes
- reports make the approved promotion thresholds visible instead of burying them in ad hoc logs
- paper performance summaries cover Sharpe, drawdown, duration, and cross-strategy correlation
- report payloads stay graph-ready so dashboards or promotion reviews can render equity, drawdown, and exposure without rebuilding finance logic
- the primary `15m` execution cadence is explicit in paper-session and report metadata
- higher-frequency or lower-frequency inputs stay represented as feature inputs, not as a hidden execution-cadence change

## Current integrated scaffold status

Reviewed against the currently integrated `crypto/` scaffold on leader HEAD:

- present now: `domain/`, `exchanges/`, `strategies/`, `promotion/`, `validation/`, `paper/`, and `reporting/`
- verified defaults already encoded in code:
  - exchange id remains `binance_perpetual`
  - primary execution cadence remains `15m`
  - multi-frequency feature inputs remain allowed through strategy and execution-plan metadata
  - promotion thresholds remain aligned with the approved launch brief
  - paper sessions keep ledger entries explicit instead of hiding them in exchange adapters
  - reporting outputs carry graph-ready equity, drawdown, and exposure series

Lane-3 interpretation for review:

- paper and reporting remain explicit package boundaries rather than being hidden inside exchange, strategy, or promotion modules
- the public paper API exposes one exported session model (`crypto.paper.PaperSession`) so reporting and promotion evidence have a single ledger source of truth
- strategy registration stays visible through an explicit reporting catalog view built from the registered crypto strategy definitions
- promotion evidence can now combine threshold checks with paper-session metrics instead of relying only on validation artifacts

## Review checklist

When reviewing `crypto/` changes, reject implementations that:

- mix crypto research code into the existing daily stock backtesting package
- add real-money execution, broker wiring, or order-routing behavior
- hide the default `binance_perpetual` venue behind ambiguous config
- silently change the primary execution cadence away from `15m`
- collapse lane boundaries by putting paper/reporting logic into strategy or exchange modules
- omit promotion-threshold reporting from paper-trading outputs

## Notes for future implementation

- Reuse proven reporting and snapshot ideas from `backtesting/reporting/` where helpful, but keep the `crypto/` package boundary intact.
- Prefer a small, composable paper ledger plus explicit report models over a monolithic runtime object.
- Keep repo documentation in sync with the shared launch brief if the approved defaults change later.

## Review verification commands

Focused checks used for the integrated scaffold review:

```bash
uv run python -m unittest crypto.tests.test_paper crypto.tests.test_reporting -v
uv run python -m unittest discover -s crypto/tests -v
```

Notes:

- Run the crypto suite through `uv run` so the lane uses the repo's Python 3.11 toolchain instead of whichever system Python happens to be active in a shell.
- Keep paper/reporting coverage in `unittest`-discoverable `TestCase` classes so the documented verification command actually exercises the graph/reporting lane.
- The crypto tests intentionally stay on `unittest` so the baseline scaffold can be verified without an extra `pytest` dependency during team execution.
