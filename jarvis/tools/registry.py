from __future__ import annotations

"""Tool registry with RBAC and HITL enforcement.

The registry stores callable tools along with security metadata such as
required roles and risk tiers. Tools marked as high risk trigger a
Human-in-the-Loop (HITL) approval step prior to execution. All activity is
logged and persisted via an encrypted audit log handler.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, get_type_hints

# These imports are required by the main branch's implementation
from pydantic import BaseModel, create_model

from agent.hitl.policy import ApprovalCallback, HITLPolicy
from jarvis.auth.security_manager import SecurityManager
from jarvis.tools.risk import ActionRequestApproval, RiskAnnotator
from jarvis.security.encrypted_logging import EncryptedFileHandler

logger = logging.getLogger(__name__)
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
    args_schema: type[BaseModel] | None = None  #: Generated Pydantic model.

    def json_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's arguments."""
        return self.args_schema.schema() if self.args_schema else {}


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
            fields[arg] = (annotation, ...)
        schema = create_model(f"{name}_Args", **fields)
        self._tools[name] = Tool(
            name,
            func,
            description,
            capabilities,
            risk_tier,
            required_role,
            schema,
        )

    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        return self._tools[name]

    def all(self) -> Dict[str, Tool]:
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
        """Execute ``name`` for ``user`` enforcing RBAC and HITL policies."""
        tool = self.get(name)
        role = security._get_user_role(user)  # RBAC lookup
        if tool.required_role and role != tool.required_role:
            # Log and block when user lacks the required role.
            logger.warning("RBACDenied", extra={"user": user, "tool": name})
            raise PermissionError("Insufficient role")

        annotator = RiskAnnotator()
        try:
            annotator.evaluate(name, {"risk": tool.risk_tier})
        except ActionRequestApproval as req:
            # High-risk actions require explicit approval.
            approved = hitl.request_approval_sync(name, req.message, modal, user=user)
            if not approved:
                logger.warning("HITLDenied", extra={"user": user, "tool": name})
                raise PermissionError("HITL denial")

        logger.info("ToolExecuted", extra={"user": user, "tool": name})
        return tool.func(*args, **kwargs)


registry = ToolsRegistry()

__all__ = ["ToolsRegistry", "Tool", "registry"]