"""Tool registry v2 with JSON schema export and capability tagging."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, get_type_hints

# These imports are required by the main branch's implementation
from pydantic import BaseModel, create_model

from agent.hitl.policy import ApprovalCallback, HITLPolicy
from jarvis.auth.security_manager import SecurityManager
from jarvis.tools.risk import ActionRequestApproval, RiskAnnotator

logger = logging.getLogger(__name__)


@dataclass
class ToolMeta:
    """Metadata for a registered tool."""

    func: Callable[..., Any]
    description: str
    capabilities: List[str]
    risk_tier: str = "low"
    required_role: str | None = None
    args_schema: type[BaseModel] | None = None

    def json_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's arguments."""
        return self.args_schema.schema() if self.args_schema else {}


class ToolsRegistry:
    """Registry that enforces policy before tool execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolMeta] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str,
        capabilities: List[str],
        *,
        risk_tier: str = "low",
        required_role: str | None = None,
    ) -> None:
        """Add a tool to the registry and generate its argument schema."""
        annotations = get_type_hints(func)
        fields: Dict[str, tuple[Any, Any]] = {}
        for arg, annotation in annotations.items():
            if arg == "return":
                continue
            fields[arg] = (annotation, ...)
        schema = create_model(f"{name}_Args", **fields)
        self._tools[name] = ToolMeta(
            func,
            description,
            capabilities,
            risk_tier,
            required_role,
            schema,
        )

    def get(self, name: str) -> ToolMeta:
        """Get a tool by name."""
        return self._tools[name]

    def all(self) -> Dict[str, ToolMeta]:
        """Return all registered tools."""
        return dict(self._tools)

    def json_export(self) -> Dict[str, Any]:
        """Export the registry's contents as a JSON-serializable dictionary."""
        return {
            name: {
                "description": tool.description,
                "capabilities": tool.capabilities,
                "risk_tier": tool.risk_tier,
                "required_role": tool.required_role,
                "args_schema": tool.json_schema(),
            }
            for name, tool in self._tools.items()
        }

    def execute(
        self,
        name: str,
        *args: Any,
        user: str,
        security: SecurityManager,
        hitl: HITLPolicy,
        modal: ApprovalCallback,
        **kwargs: Any,
    ) -> Any:
        """Execute a tool for a user, enforcing RBAC and HITL policies."""
        tool = self.get(name)
        role = security._get_user_role(user)  # Leveraging existing lookup
        if tool.required_role and role != tool.required_role:
            logger.warning("RBACDenied", extra={"user": user, "tool": name})
            raise PermissionError("Insufficient role")

        annotator = RiskAnnotator()
        try:
            annotator.evaluate(name, {"risk": tool.risk_tier})
        except ActionRequestApproval as req:
            approved = hitl.request_approval_sync(name, req.message, modal, user=user)
            if not approved:
                logger.warning("HITLDenied", extra={"user": user, "tool": name})
                raise PermissionError("HITL approval denied")

        logger.info("ToolExecuted", extra={"user": user, "tool": name})
        return tool.func(*args, **kwargs)


registry = ToolsRegistry()

__all__ = ["ToolsRegistry", "ToolMeta", "registry"]