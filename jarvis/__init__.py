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

# Import with error handling for optional components
try:  # pragma: no cover - optional dependencies
    from jarvis.core.simple_agent import JarvisAgent as SimpleJarvisAgent
    from jarvis.core.enhanced_agent import EnhancedJarvisAgent
    from jarvis.core.mcp_agent import MCPJarvisAgent
    from jarvis.database.db_manager import DatabaseManager, get_database_manager
    from jarvis.auth.security_manager import SecurityManager, get_security_manager
    from jarvis.agents.coding_agent import CodingAgent
    from jarvis.workflows.workflow_agent import WorkflowJarvisAgent, create_workflow_jarvis
    from jarvis.workflows import (
        WorkflowEngine,
        create_workflow,
        WorkflowTemplates,
        create_code_review_workflow,
        create_deployment_workflow,
        create_project_analysis_workflow,
        create_bug_fix_workflow,
    )
except (ImportError, SyntaxError, Exception):  # pragma: no cover
    SimpleJarvisAgent = None
    EnhancedJarvisAgent = None
    MCPJarvisAgent = None
    DatabaseManager = None
    get_database_manager = None
    SecurityManager = None
    get_security_manager = None
    CodingAgent = None
    WorkflowJarvisAgent = None
    create_workflow_jarvis = None
    WorkflowEngine = None
    WorkflowTemplates = None
    create_workflow = None
    create_code_review_workflow = None
    create_deployment_workflow = None
    create_project_analysis_workflow = None
    create_bug_fix_workflow = None