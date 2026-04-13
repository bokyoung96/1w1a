---
source_file: "tests/test_run.py"
type: "code"
community: "Tests Test Run.Py Engine"
location: "L255"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Tests_Test_Run.Py_Engine
---

# test_runner_uses_warmup_history_but_trims_persisted_outputs()

## Connections
- [[BacktestEngine.run()]] - `calls` [INFERRED]
- [[BacktestRunner]] - `calls` [INFERRED]
- [[DataCatalog.default()]] - `calls` [INFERRED]
- [[ParquetStore]] - `calls` [INFERRED]
- [[ParquetStore.write()]] - `calls` [INFERRED]
- [[PositionPlan]] - `calls` [INFERRED]
- [[RunConfig]] - `calls` [INFERRED]
- [[StrategyStub]] - `calls` [INFERRED]
- [[test_run.py_1]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Tests_Test_Run.Py_Engine