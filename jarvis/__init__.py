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
try:  # pragma: no cover - optional dependencies
    from jarvis.core.simple_agent import JarvisAgent as SimpleJarvisAgent
except ImportError:  # pragma: no cover
    SimpleJarvisAgent = None

try:  # pragma: no cover - optional dependencies
    from jarvis.core.enhanced_agent import EnhancedJarvisAgent
except Exception:  # pragma: no cover
    EnhancedJarvisAgent = None

try:  # pragma: no cover - optional dependencies
    from jarvis.core.mcp_agent import MCPJarvisAgent
except Exception:  # pragma: no cover
    MCPJarvisAgent = None

try:  # pragma: no cover - optional dependencies
    from jarvis.database.db_manager import DatabaseManager, get_database_manager
except Exception:  # pragma: no cover
    DatabaseManager = None
    get_database_manager = None

try:  # pragma: no cover - optional dependencies
    from jarvis.auth.security_manager import SecurityManager, get_security_manager
except Exception:  # pragma: no cover
    SecurityManager = None
    get_security_manager = None
try:
    from jarvis.agents.coding_agent import CodingAgent
except (ImportError, SyntaxError):  # pragma: no cover - optional dependency or syntax errors
    CodingAgent = None
    CodingAgent = None

try:  # pragma: no cover - optional dependencies
    from jarvis.workflows.workflow_agent import WorkflowJarvisAgent, create_workflow_jarvis
except Exception:  # pragma: no cover
    WorkflowJarvisAgent = None
    create_workflow_jarvis = None

try:  # pragma: no cover - optional dependencies
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
    mode: str = "auto",