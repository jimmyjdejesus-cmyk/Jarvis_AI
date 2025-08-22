# Human-in-the-Loop Safety

Jarvis employs a human-in-the-loop (HITL) policy to guard destructive
operations such as file writes, git commits, and outbound HTTP ``POST``
requests.

## Workflow

1. A guarded action is attempted.
2. `HITLPolicy` emits an `ActionRequestApproval`.
3. The UI displays a modal prompting the operator to approve or deny.
4. Absence of a response results in an automatic denial.
5. Every decision is recorded in an audit trail.

See `agent/hitl/policy.py` and `agent/ui/hitl_modal.py` for the reference
implementation.  The logging utilities in `agent/logging/scoped_writer.py`
can be used to persist transcripts for later review.
