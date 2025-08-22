from __future__ import annotations

"""Console based HITL approval modal.

The real project uses a web based UI to present approval requests.  This
lightweight stand-in prints the request to stdout and waits for ``y`` or
``n`` input.  If no input is provided (e.g. in a non-interactive
environment) the request is denied automatically.
"""

from typing import Optional
import sys
import select
import time

from agent.hitl.policy import ActionRequestApproval

__all__ = ["console_modal"]


def console_modal(request: ActionRequestApproval, timeout: float = 5.0) -> bool:
    """Display a blocking modal in the console.

    Parameters
    ----------
    request:
        The approval request to display.
    timeout:
        Seconds to wait for input before auto-denying.
    """

    print(f"Requesting approval: {request.action} — {request.reason}")
    print("Approve? [y/N]: ", end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        response = sys.stdin.readline().strip().lower()
        return response == "y"
    print("\nNo response; auto-denied")
    return False
