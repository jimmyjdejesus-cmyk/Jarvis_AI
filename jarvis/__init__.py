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
