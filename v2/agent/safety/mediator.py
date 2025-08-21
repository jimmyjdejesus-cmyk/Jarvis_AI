"""Safety mediator for sensitive tool actions.

The mediator acts as a lightweight policy enforcement point.  When the agent
attempts to perform potentially destructive operations – writing files or
interacting with Git/GitHub – the mediator requests explicit user approval via
UI components.  This keeps the core agent logic clean while providing a single
place to extend safety rules.
"""

from __future__ import annotations

from typing import Callable

from jarvis.ui.components import ui_components


class ActionMediator:
    """Prompt the user for approval before executing sensitive actions."""

    def __init__(self, ui=ui_components):
        self.ui = ui
        self.protected_actions = {"write_file", "git_commit"}

    def requires_approval(self, action: str) -> bool:
        """Return ``True`` if the given action needs user approval."""

        return action in self.protected_actions or action.startswith("github_")

    def approve(self, action: str, context: str = "") -> bool:
        """Request user approval for an action.

        Parameters
        ----------
        action:
            Name of the action about to be performed.
        context:
            Optional human readable context describing the operation.
        """

        if not self.requires_approval(action):
            return True

        message = f"Allow action '{action}'? {context}".strip()
        try:
            return bool(self.ui.confirm_action(message))
        except Exception:
            return False

    def mediate(self, action: str, fn: Callable, *args, **kwargs):
        """Execute ``fn`` only if the user approves the ``action``."""

        if self.approve(action, str(args) or str(kwargs)):
            return fn(*args, **kwargs)
        raise PermissionError(f"Action '{action}' was not approved")


__all__ = ["ActionMediator"]

