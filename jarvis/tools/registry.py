"""Tool registry with RBAC and HITL approval hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional

import importlib.util
from pathlib import Path

_audit_spec = importlib.util.spec_from_file_location(
    "audit", Path(__file__).resolve().parents[2] / "auth" / "audit.py"
)
_audit_module = importlib.util.module_from_spec(_audit_spec)
assert _audit_spec and _audit_spec.loader
_audit_spec.loader.exec_module(_audit_module)
log_action = _audit_module.log_action
from jarvis.tools.risk import ActionRequestApproval, RiskAnnotator


@dataclass
class ToolMeta:
    """Metadata for a registered tool."""

    func: Callable[..., Any]
    capability_tags: Iterable[str]
    risk_tier: str = "low"
    required_role: str = "user"


class ToolsRegistry:
    """Registry that enforces policy before tool execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolMeta] = {}
        self._annotator = RiskAnnotator()

    def register_tool(self, name: str, meta: ToolMeta) -> None:
        """Add a tool to the registry."""
        self._tools[name] = meta

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        capabilities: Optional[Iterable[str]] = None,
        risk: str = "low",
        required_role: str = "user",
    ) -> None:
        """Backward-compatible registration API."""
        meta = ToolMeta(func, capabilities or [], risk_tier=risk, required_role=required_role)
        self.register_tool(name, meta)

    def run_tool(
        self,
        name: str,
        username: str,
        security_manager,
        *args: Any,
        approval_fn: Optional[Callable[[str, str], bool]] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a registered tool after RBAC, risk, and audit checks."""

        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        meta = self._tools[name]

        # RBAC check using security manager role
        user_role = security_manager._get_user_role(username)
        if meta.required_role and user_role != meta.required_role:
            log_action(username, f"{name}:denied")
            raise PermissionError("Insufficient role")

        # Risk evaluation requiring approval for high risk
        try:
            self._annotator.evaluate(name, {"risk": meta.risk_tier})
        except ActionRequestApproval:
            approved = approval_fn(username, name) if approval_fn else False
            if not approved:
                log_action(username, f"{name}:approval_required")
                raise

        result = meta.func(*args, username=username, security_manager=security_manager, **kwargs)
        log_action(username, f"{name}:executed")
        return result


registry = ToolsRegistry()

__all__ = ["ToolsRegistry", "ToolMeta", "registry"]

