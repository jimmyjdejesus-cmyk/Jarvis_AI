from __future__ import annotations

"""Human-in-the-loop policy enforcement.

The :class:`HITLPolicy` class provides a minimal mechanism for guarding
potentially destructive operations (file writes, git commits, HTTP
``POST`` requests, etc.).  When such an action is attempted the policy
emits an ``ActionRequestApproval`` instance which can be displayed by a
UI component and resolved with an approval or denial.
"""

from dataclasses import dataclass
import inspect
import asyncio
from typing import Awaitable, Callable, List, Optional, Set, Union
import time

from config.config_loader import load_config

__all__ = [
    "HITLPolicy",
    "ActionRequestApproval",
    "ApprovalRecord",
    "ApprovalCallback",
]


# Default set used if configuration does not provide policy rules
DEFAULT_DESTRUCTIVE_OPS = {
    "git_write",
    "file_write",
    "file_delete",
    "external_post",
    "state_prune",
}


# Callback type for approval modals. The callback may be synchronous or
# asynchronous.
ApprovalCallback = Callable[
    ["ActionRequestApproval"], Union[bool, Awaitable[bool]]
]


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

    def __init__(self, config: Optional[dict] = None) -> None:
        cfg = config or load_config()
        ops = cfg.get("hitl", {}).get("destructive_ops", DEFAULT_DESTRUCTIVE_OPS)
        self.destructive_ops: Set[str] = set(ops)
        self.audit: List[ApprovalRecord] = []

    # ------------------------------------------------------------------
    def requires_approval(self, op: str) -> bool:
        """Return ``True`` if ``op`` is guarded by the policy."""

        return op in self.destructive_ops

    async def request_approval(
        self,
        op: str,
        reason: str,
        modal: ApprovalCallback,
        user: str = "unknown",
    ) -> bool:
        """Request approval via a modal callback.

        Parameters
        ----------
        op:
            Operation being attempted (e.g. ``"file_write"``).
        reason:
            Textual explanation shown to the user.
        modal:
            Callable that takes :class:`ActionRequestApproval` and returns
            ``True`` if approved. The callable may be synchronous or
            asynchronous.
        user:
            Identifier for the user performing the approval.
        """

        request = ActionRequestApproval(op, reason)
        result = modal(request)
        approved = await result if inspect.isawaitable(result) else bool(result)
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

    def request_approval_sync(
        self,
        op: str,
        reason: str,
        modal: ApprovalCallback,
        user: str = "unknown",
    ) -> bool:
        """Synchronously request approval via ``asyncio.run``.

        This helper enables usage from synchronous code paths.
        """

        return asyncio.run(self.request_approval(op, reason, modal, user))
