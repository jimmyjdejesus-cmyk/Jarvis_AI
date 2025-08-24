from __future__ import annotations

"""Agent responsible for applying corrective actions to failing components."""

from typing import Callable, Dict


class RemediationAgent:
    """Attempt to remediate a failing component by executing a mapped action.

    Parameters
    ----------
    actions: Dict[str, Callable[[], None]] | None
        Mapping of component identifiers to callables implementing the
        remediation logic.
    """

    def __init__(self, actions: Dict[str, Callable[[], None]] | None = None) -> None:
        self.actions = actions or {}

    # ------------------------------------------------------------------
    def remediate(self, component: str) -> bool:
        """Execute a remediation action for the specified component.

        Returns True when the associated action executes without raising an
        exception.  When no action is registered or an error occurs the method
        returns False, signalling that manual intervention is required.
        """

        action = self.actions.get(component)
        if not action:
            return False
        try:
            action()
            return True
        except Exception:
            return False


__all__ = ["RemediationAgent"]
