
# Agent Log - config

- Added `ENABLE_CURIOSITY_ROUTING` flag to toggle curiosity question routing.
- Added default severity weight mapping for critic insights.
- Exposed default credibility and unknown severity weight for critic insights.
- Added default severity for critic insights.
- Added `max_examples` setting for critic insight summaries.
- Documented `max_examples` with inline comment.
- Introduced `max_summary_groups` configuration to bound severity groups in summaries.
- Added `summary_score_threshold` configuration to filter low-scoring severity groups.
- Added `summary_score_ratio` option for dynamic score-based pruning of summary groups.
## Dev Log
- Added ENABLE_CURIOSITY_ROUTING flag for controlling curiosity directive execution.- Marked sample mission with disruptive tag for black-team orchestration.
