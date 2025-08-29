# Agent Log
- Extended `PerformanceTracker` to capture failed step counts for monitoring.

- Added weighted scoring and argument synthesis to `CriticInsightMerger`.
- Configured severity weights via default.yaml and handled missing fields in merger.
- Fixed indentation in `PerformanceTracker.record_event` to prevent import errors.
- Corrected PerformanceTracker.record_event indentation and shortened comments.
- Added weighted scoring and argument synthesis to `CriticInsightMerger`.
- Configured severity weights via default.yaml and handled missing fields in merger.
- Extracted default credibility and unknown severity weight into configuration and wired into merger logic.
- Loaded default severity from configuration and applied in merger.
- Made example limit configurable via `max_examples` and documented new parameter.
- Expanded docstring for `max_examples` helper to reference configuration key.
- Added `max_summary_groups` option to limit severity groups in synthesized summaries and documented new helper.
- Introduced `summary_score_threshold` to drop low-scoring severity groups from summaries and updated merger tests.
- Added dynamic `summary_score_ratio` filtering to prune groups relative to top score and broadened threshold documentation.
