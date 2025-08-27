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

# Import minimal components; heavy submodules are optional and loaded lazily
try:
    from jarvis.core.simple_agent import JarvisAgent as SimpleJarvisAgent
except ImportError:
    SimpleJarvisAgent = None

try:
    from jarvis.core.enhanced_agent import EnhancedJarvisAgent
except ImportError:
    EnhancedJarvisAgent = None

try:
    from jarvis.core.mcp_agent import MCPJarvisAgent
except ImportError:
    MCPJarvisAgent = None

try:
    from jarvis.database.db_manager import DatabaseManager, get_database_manager
except ImportError:
    DatabaseManager = None
    get_database_manager = None

try:
    from jarvis.auth.security_manager import SecurityManager, get_security_manager
except ImportError:
    SecurityManager = None
    get_security_manager = None

try:
    from jarvis.agents.coding_agent import CodingAgent
except Exception:
    CodingAgent = None

try:
    from jarvis.workflows.workflow_agent import WorkflowJarvisAgent, create_workflow_jarvis
except ImportError:
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
except ImportError:
    WorkflowEngine = None
    WorkflowTemplates = None
    create_workflow = None
    create_code_review_workflow = None
    create_deployment_workflow = None
    create_project_analysis_workflow = None
    create_bug_fix_workflow = None