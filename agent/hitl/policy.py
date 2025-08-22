from __future__ import annotations

"""Human-in-the-loop policy enforcement.

The :class:`HITLPolicy` class provides a minimal mechanism for guarding
potentially destructive operations (file writes, git commits, HTTP
``POST`` requests, etc.).  When such an action is attempted the policy
emits an ``ActionRequestApproval`` instance which can be displayed by a
UI component and resolved with an approval or denial.
"""

from dataclasses import dataclass
from typing import Callable, List
import time

__all__ = ["HITLPolicy", "ActionRequestApproval", "ApprovalRecord"]


DESTRUCTIVE_OPS = {"git_write", "file_write", "file_delete", "external_post"}


@dataclass
class ActionRequestApproval:
    """Represents a request for human approval."""

    action: str
    reason: str


@dataclass
class ApprovalRecord:
    """Audit record capturing the outcome of an approval request."""

    action: str
    approved: bool
    user: str
    reason: str
    timestamp: float


class HITLPolicy:
    """Policy engine for human approvals."""

    def __init__(self) -> None:
        self.audit: List[ApprovalRecord] = []

    # ------------------------------------------------------------------
    def requires_approval(self, op: str) -> bool:
        """Return ``True`` if ``op`` is guarded by the policy."""

        return op in DESTRUCTIVE_OPS

    def request_approval(self, op: str, reason: str, modal: Callable[[ActionRequestApproval], bool], user: str = "unknown") -> bool:
        """Request approval via a modal callback.

        Parameters
        ----------
        op:
            Operation being attempted (e.g. ``"file_write"``).
        reason:
            Textual explanation shown to the user.
        modal:
            Callable that takes :class:`ActionRequestApproval` and returns
            ``True`` if approved.
        user:
            Identifier for the user performing the approval.
        """

        request = ActionRequestApproval(op, reason)
        approved = modal(request)
        self.audit.append(
            ApprovalRecord(
                action=op,
                approved=approved,
                user=user,
                reason=reason,
                timestamp=time.time(),
            )
        )
        return approved
