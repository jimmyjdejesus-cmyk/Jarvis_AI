# Agent Log
- Added configurable timeouts and retry with exponential backoff to `run_step`.
- Introduced optional `timeout` in `StepContext` and wired `PerformanceTracker` for step failures.
