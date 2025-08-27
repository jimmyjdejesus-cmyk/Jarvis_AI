"""Tool registry with RBAC and HITL enforcement.

The registry stores callable tools along with security metadata such as
required roles and risk tiers. Tools marked as high risk trigger a
Human-in-the-Loop (HITL) approval step prior to execution. All activity is
logged and persisted via an encrypted audit log handler.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, get_type_hints

from pydantic import BaseModel, create_model

# Assuming these are the correct import paths for your project structure
from agent.hitl.policy import ApprovalCallback, HITLPolicy
from jarvis.auth.security_manager import SecurityManager
from jarvis.security.encrypted_logging import EncryptedFileHandler
from jarvis.tools.risk import ActionRequestApproval, RiskAnnotator

logger = logging.getLogger(__name__)
# Ensure the logs directory exists before adding the handler
import os
os.makedirs("logs", exist_ok=True)
logger.addHandler(EncryptedFileHandler("logs/audit.log.enc"))


@dataclass
class Tool:
    """Metadata describing a registered tool."""

    name: str
    func: Callable[..., Any]
    description: str
    capabilities: List[str]
    risk_tier: str = "low"  #: Risk tier influencing HITL gating.
    required_role: str | None = None  #: RBAC role required to execute.
    args_schema: type[BaseModel] | None = None  #: Generated Pydantic model for arguments.

    def json_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's arguments."""
        return self.args_schema.schema() if self.args_schema else {}


# Backwards compatibility alias so older imports of ToolMeta continue to work.
ToolMeta = Tool


class ToolsRegistry:
    """Registry that enforces policy before tool execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

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
        """Register ``func`` under ``name`` with associated metadata."""
        annotations = get_type_hints(func)
        fields: Dict[str, tuple[Any, Any]] = {}
        for arg, annotation in annotations.items():
            if arg == "return":
                continue
            # Ellipsis (...) marks the field as required
            fields[arg] = (annotation, ...)
        
        # Create a dynamic Pydantic model for argument validation
        schema = create_model(f"{name}_Args", **fields)
        
        self._tools[name] = Tool(
            name=name,
            func=func,
            description=description,
            capabilities=capabilities,
            risk_tier=risk_tier,
            required_role=required_role,
            args_schema=schema,
        )

    def get(self, name: str) -> Tool:
        """Get a tool by name. Raises KeyError if not found."""
        return self._tools[name]

    def all(self) -> Dict[str, Tool]:
        """Return all registered tools."""
        return self._tools.copy()

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
        user: str,
        security: SecurityManager,
        hitl: HITLPolicy,
        modal: ApprovalCallback,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute ``name`` for ``user`` enforcing RBAC and HITL policies."""
        tool = self.get(name)
        
        # NOTE: Accessing a protected member `_get_user_role`.
        # This suggests a potential design improvement in SecurityManager.
        role = security._get_user_role(user)  # RBAC lookup
        if tool.required_role and role != tool.required_role:
            logger.warning("RBACDenied", extra={"user": user, "tool": name, "required_role": tool.required_role})
            raise PermissionError(f"User '{user}' with role '{role}' lacks required role '{tool.required_role}' for tool '{name}'")

        annotator = RiskAnnotator()
        try:
            annotator.evaluate(name, {"risk": tool.risk_tier})
        except ActionRequestApproval as req:
            # High-risk actions require explicit approval.
            logger.info("HITLRequired", extra={"user": user, "tool": name, "reason": req.message})
            approved = hitl.request_approval_sync(name, req.message, modal, user=user)
            if not approved:
                logger.warning("HITLDenied", extra={"user": user, "tool": name})
                raise PermissionError(f"Execution of tool '{name}' was denied by the user.")

        logger.info("ToolExecuted", extra={"user": user, "tool": name, "args": args, "kwargs": kwargs})
        return tool.func(*args, **kwargs)


# Global instance of the registry
registry = ToolsRegistry()

__all__ = ["ToolsRegistry", "Tool", "ToolMeta", "registry"]