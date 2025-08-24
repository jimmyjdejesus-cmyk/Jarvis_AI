# Scoped Logs, HITL Risk, and Policy-Based Routing

This document outlines three related enhancements:

## Scoped Logs ↔ RAG
- After each run, markdown transcripts can be indexed.
- When a new task arrives the indexer surfaces:
  - **Positive citations** showing prior successes.
  - **Negative citations** highlighting paths to avoid.
- Both citation sets are intended to be visible in final answers.

## HITL ↔ Tools
- Tools may include a `risk` field in their metadata.
- The `RiskAnnotator` returns a risk level and raises
  `ActionRequestApproval` for high-risk actions.
- Callers can pause execution, display a UI approval modal, and
  resume or abort while recording the decision to logs and DAG.

## MCP Routing ↔ Policies
- The `ModelRouter` accepts `task_type`, `complexity`, and `budget`
  (`aggressive`, `balanced`, `conservative`).
- Selected model and justification are stored for UI tooltip display.
- This enables transparent, policy-aware model selection.
