"""
Jarvis AI - Enhanced Core Package
Modern architecture with MCP, multi-agent, and advanced workflow capabilities.
"""

from __future__ import annotations

__version__ = "4.0.0"
__author__ = "Jimmy De Jesus"

# Configuration flags
DEFAULT_MCP_ENABLED = True
DEFAULT_MULTI_AGENT_ENABLED = True
DEFAULT_WORKFLOWS_ENABLED = True  # Phase 4: Advanced Workflows!

# Import with error handling - only working components
try:
    from jarvis.core.simple_agent import JarvisAgent as SimpleJarvisAgent
except Exception:  # pragma: no cover - optional component
    SimpleJarvisAgent = None

try:
    from jarvis.core.enhanced_agent import EnhancedJarvisAgent
except Exception:  # pragma: no cover
    EnhancedJarvisAgent = None

try:
    from jarvis.core.mcp_agent import MCPJarvisAgent
except Exception:  # pragma: no cover
    MCPJarvisAgent = None

try:
    from jarvis.database.db_manager import DatabaseManager, get_database_manager
except Exception:  # pragma: no cover
    DatabaseManager = None
    get_database_manager = None

try:
    from jarvis.auth.security_manager import SecurityManager, get_security_manager
except Exception:  # pragma: no cover
    SecurityManager = None
    get_security_manager = None

try:
    from jarvis.agents.coding_agent import CodingAgent
except Exception:  # pragma: no cover
    CodingAgent = None

try:
    from jarvis.workflows.workflow_agent import WorkflowJarvisAgent, create_workflow_jarvis
except Exception:  # pragma: no cover
    WorkflowJarvisAgent = None
    create_workflow_jarvis = None

try:
    from jarvis.workflows import (
        WorkflowEngine,
        create_workflow,
        WorkflowTemplates,
        create_code_review_workflow,
        create_deployment_workflow,
        create_project_analysis_workflow,
        create_bug_fix_workflow,
    )
except Exception:  # pragma: no cover
    WorkflowEngine = None
    WorkflowTemplates = None
    create_workflow = None
    create_code_review_workflow = None
    create_deployment_workflow = None
    create_project_analysis_workflow = None
    create_bug_fix_workflow = None


def get_jarvis_agent(
    enable_mcp: bool | None = None,
    enable_multi_agent: bool | None = None,
    enable_workflows: bool | None = None,
):
    """Return an appropriate Jarvis agent based on configuration."""

    enable_mcp = DEFAULT_MCP_ENABLED if enable_mcp is None else enable_mcp
    enable_multi_agent = DEFAULT_MULTI_AGENT_ENABLED if enable_multi_agent is None else enable_multi_agent
    enable_workflows = DEFAULT_WORKFLOWS_ENABLED if enable_workflows is None else enable_workflows

    if enable_workflows and WorkflowJarvisAgent:
        return WorkflowJarvisAgent()

    if enable_mcp and MCPJarvisAgent:
        return MCPJarvisAgent()

    if enable_multi_agent and EnhancedJarvisAgent:
        return EnhancedJarvisAgent()

    if SimpleJarvisAgent:
        return SimpleJarvisAgent()

    raise RuntimeError("No available Jarvis agent implementation")


# Convenience wrappers for backward compatibility
def get_simple_jarvis():
    """Get basic single-agent Jarvis."""
    return get_jarvis_agent(enable_mcp=False, enable_multi_agent=False, enable_workflows=False)


def get_smart_jarvis():
    """Get Jarvis with MCP enabled."""
    return get_jarvis_agent(enable_mcp=True, enable_multi_agent=False, enable_workflows=False)


def get_super_jarvis():
    """Get Jarvis with MCP and multi-agent features."""
    return get_jarvis_agent(enable_mcp=True, enable_multi_agent=True, enable_workflows=False)


def get_workflow_jarvis():
    """Get workflow-capable Jarvis."""
    return get_jarvis_agent(enable_mcp=True, enable_multi_agent=True, enable_workflows=True)


def get_ultimate_jarvis():
    """Get the most capable Jarvis configuration."""
    return get_workflow_jarvis()


def get_coding_agent(base_agent=None, workspace_path: str | None = None):
    """Return coding agent built on top of Jarvis."""
    base_agent = base_agent or get_jarvis_agent()
    if CodingAgent:
        return CodingAgent(base_agent, workspace_path)
    return base_agent


__all__ = [
    "get_jarvis_agent",
    "get_simple_jarvis",
    "get_smart_jarvis",
    "get_super_jarvis",
    "get_workflow_jarvis",
    "get_ultimate_jarvis",
    "get_coding_agent",
    "SimpleJarvisAgent",
    "MCPJarvisAgent",
    "EnhancedJarvisAgent",
    "WorkflowJarvisAgent",
    "DatabaseManager",
    "get_database_manager",
    "SecurityManager",
    "get_security_manager",
    "CodingAgent",
    "WorkflowEngine",
    "WorkflowTemplates",
    "create_workflow",
    "create_code_review_workflow",
    "create_deployment_workflow",
    "create_project_analysis_workflow",
    "create_bug_fix_workflow",
]
