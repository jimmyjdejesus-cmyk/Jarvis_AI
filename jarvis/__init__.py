"""Jarvis AI - Enhanced Core Package

Modern architecture with MCP, multi-agent, and advanced workflow capabilities.
"""

from __future__ import annotations

__version__ = "4.0.0"
__author__ = "Jimmy De Jesus"

# Configuration flags
DEFAULT_MCP_ENABLED = True
DEFAULT_MULTI_AGENT_ENABLED = True
DEFAULT_WORKFLOWS_ENABLED = True  # Phase 4: Advanced Workflows!

# Optional imports guarded to keep import surface clean in minimal contexts
try:  # pragma: no cover - optional dependencies
    from jarvis.core.simple_agent import JarvisAgent as SimpleJarvisAgent
except Exception:  # pragma: no cover
    SimpleJarvisAgent = None  # type: ignore

try:
    from jarvis.core.enhanced_agent import EnhancedJarvisAgent
except Exception:
    EnhancedJarvisAgent = None  # type: ignore

try:
    from jarvis.core.mcp_agent import MCPJarvisAgent
except Exception:
    MCPJarvisAgent = None  # type: ignore

try:
    from jarvis.database.db_manager import (
        DatabaseManager,
        get_database_manager,
    )
except Exception:
    DatabaseManager = None  # type: ignore
    get_database_manager = None  # type: ignore

try:
    from jarvis.auth.security_manager import (
        SecurityManager,
        get_security_manager,
    )
except Exception:
    SecurityManager = None  # type: ignore
    get_security_manager = None  # type: ignore

try:
    from jarvis.agents.coding_agent import CodingAgent
except Exception:  # pragma: no cover - optional dependency or syntax errors
    CodingAgent = None  # type: ignore

try:
    from jarvis.workflows.workflow_agent import (
        WorkflowJarvisAgent,
        create_workflow_jarvis,
    )
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
    WorkflowJarvisAgent = None  # type: ignore
    create_workflow_jarvis = None  # type: ignore
    WorkflowEngine = None  # type: ignore
    WorkflowTemplates = None  # type: ignore
    create_workflow = None  # type: ignore
    create_code_review_workflow = None  # type: ignore
    create_deployment_workflow = None  # type: ignore
    create_project_analysis_workflow = None  # type: ignore
    create_bug_fix_workflow = None  # type: ignore
