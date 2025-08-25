from __future__ import annotations

"""Console based HITL approval modal.

This module provides a minimal asynchronous console modal used for human
in-the-loop approvals.  The real project uses a web UI; this console
version prints the request and waits for ``y`` or ``n`` input.  If no
input is received within the timeout the request is denied.
"""

from typing import Optional
import asyncio
import sys
import select

from agent.hitl.policy import ActionRequestApproval

__all__ = ["console_modal"]


def _prompt_user(timeout: float) -> bool:
    """Helper that blocks for input and returns ``True`` if approved."""
    print("Approve? [y/N]: ", end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        response = sys.stdin.readline().strip().lower()
        return response == "y"
    print("\nNo response; auto-denied")
    return False


async def console_modal(request: ActionRequestApproval, timeout: float = 5.0) -> bool:
    """Display a non-blocking console modal and return the decision.

    Parameters
    ----------
    request:
        The approval request to display.
    timeout:
        Seconds to wait for input before auto-denying.
    """

    print(f"Requesting approval: {request.action} — {request.reason}")
    return await asyncio.to_thread(_prompt_user, timeout)
