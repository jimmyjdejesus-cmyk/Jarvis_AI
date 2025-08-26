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
except ImportError:
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


def get_jarvis_agent(
    mode: str = "auto",
    enable_mcp: bool | None = None,
    enable_multi_agent: bool | None = None,
    enable_workflows: bool | None = None,
):
    """Get Jarvis agent with configurable capabilities.
    
    Args:
        mode: One of "simple", "mcp", "multi_agent", "workflow", or "auto"
        enable_mcp: Enable MCP capabilities
        enable_multi_agent: Enable multi-agent capabilities
        enable_workflows: Enable workflow capabilities
        
    Returns:
        Configured Jarvis agent instance
    """
    
    if mode == "simple":
        if SimpleJarvisAgent:
            return SimpleJarvisAgent()
        else:
            raise ImportError("No Jarvis agent available")
    
    elif mode == "mcp":
        if EnhancedJarvisAgent:
            return EnhancedJarvisAgent(enable_mcp=True, enable_multi_agent=False)
        elif MCPJarvisAgent:
            return MCPJarvisAgent(enable_mcp=True, enable_multi_agent=False)
        elif SimpleJarvisAgent:
            print("Warning: Enhanced agents not available, using simple agent")
            return SimpleJarvisAgent()
        else:
            raise ImportError("No Jarvis agent available")
    
    elif mode == "multi_agent":
        if EnhancedJarvisAgent:
            return EnhancedJarvisAgent(enable_mcp=True, enable_multi_agent=True)
        else:
            print("Warning: Multi-agent not available, falling back")
            return get_jarvis_agent(mode="mcp")
    
    elif mode == "workflow":
        if WorkflowJarvisAgent:
            return WorkflowJarvisAgent(
                enable_mcp=True, 
                enable_multi_agent=True, 
                enable_workflows=True
            )
        elif EnhancedJarvisAgent:
            print("Warning: Workflow agent not available, using enhanced agent")
            return EnhancedJarvisAgent(enable_mcp=True, enable_multi_agent=True)
        else:
            print("Warning: Workflow capabilities not available, falling back")
            return get_jarvis_agent(mode="multi_agent")
    
    else:  # auto mode
        enable_mcp = enable_mcp if enable_mcp is not None else DEFAULT_MCP_ENABLED
        enable_multi_agent = enable_multi_agent if enable_multi_agent is not None else DEFAULT_MULTI_AGENT_ENABLED
        enable_workflows = enable_workflows if enable_workflows is not None else DEFAULT_WORKFLOWS_ENABLED
        
        # Try from most to least capable
        if WorkflowJarvisAgent and enable_workflows:
            try:
                return WorkflowJarvisAgent(
                    enable_mcp=enable_mcp,
                    enable_multi_agent=enable_multi_agent,
                    enable_workflows=enable_workflows,
                )
            except Exception as e:
                print(f"Warning: Workflow agent failed to initialize: {e}")
        
        if EnhancedJarvisAgent:
            try:
                return EnhancedJarvisAgent(
                    enable_mcp=enable_mcp, 
                    enable_multi_agent=enable_multi_agent
                )
            except Exception as e:
                print(f"Warning: Enhanced agent failed to initialize: {e}")
        
        if MCPJarvisAgent and enable_mcp:
            try:
                return MCPJarvisAgent(enable_mcp=enable_mcp, enable_multi_agent=False)
            except Exception as e:
                print(f"Warning: MCP agent failed to initialize: {e}")
        
        if SimpleJarvisAgent:
            return SimpleJarvisAgent()
        else:
            raise ImportError("No Jarvis agent available")


# Convenience functions
def get_simple_jarvis():
    """Get basic single-agent Jarvis."""
    return get_jarvis_agent(mode="simple")


def get_smart_jarvis():
    """Get Jarvis with MCP enabled."""
    return get_jarvis_agent(mode="mcp")


def get_super_jarvis():
    """Get Jarvis with MCP and multi-agent features."""
    return get_jarvis_agent(mode="multi_agent")


def get_workflow_jarvis():
    """Get workflow-capable Jarvis."""
    return get_jarvis_agent(mode="workflow")


def get_ultimate_jarvis():
    """Get the most capable Jarvis configuration."""
    return get_jarvis_agent(
        mode="auto",
        enable_mcp=True,
        enable_multi_agent=True,
        enable_workflows=True,
    )


def get_coding_agent(base_agent=None, workspace_path: str | None = None):
    """Get enhanced coding agent.
    
    Args:
        base_agent: Base Jarvis agent to use (creates one if None)
        workspace_path: Path to workspace for coding operations
        
    Returns:
        CodingAgent instance or base agent if CodingAgent unavailable
    """
    if base_agent is None:
        base_agent = get_jarvis_agent()
    
    if CodingAgent:
        return CodingAgent(base_agent, workspace_path)
    return base_agent


def create_and_run_workflow(workflow_type: str, **kwargs):
    """Create and run a workflow using the workflow-enabled Jarvis.
    
    Args:
        workflow_type: Type of workflow to run
        **kwargs: Workflow-specific parameters
        
    Returns:
        Workflow execution results
    """
    if not WorkflowJarvisAgent:
        raise ImportError("Workflow capabilities not available")
    
    jarvis = get_workflow_jarvis()
    
    if workflow_type == "code_review" and create_code_review_workflow:
        workflow = create_code_review_workflow(kwargs.get("file_path", "code.py"))
    elif workflow_type == "deployment" and create_deployment_workflow:
        workflow = create_deployment_workflow(
            kwargs.get("project_path", "."),
            kwargs.get("environment", "production"),
        )
    elif workflow_type == "project_analysis" and create_project_analysis_workflow:
        workflow = create_project_analysis_workflow(kwargs.get("project_path", "."))
    elif workflow_type == "bug_fix" and create_bug_fix_workflow:
        workflow = create_bug_fix_workflow(
            kwargs.get("issue_description", "Bug to fix"),
            kwargs.get("code_files", []),
        )
    else:
        raise ValueError(f"Unknown or unavailable workflow type: {workflow_type}")
    
    return jarvis.execute_workflow_by_name(workflow_type, kwargs)


# Backward compatibility
JarvisAgent = get_jarvis_agent  # Alias for backward compatibility

__all__ = [
    # Main function
    "get_jarvis_agent",
    "JarvisAgent",  # Backward compatibility alias
    
    # Convenience functions
    "get_simple_jarvis",
    "get_smart_jarvis",
    "get_super_jarvis",
    "get_workflow_jarvis",
    "get_ultimate_jarvis",
    "get_coding_agent",
    "create_and_run_workflow",
    
    # Agent classes (may be None if not available)
    "SimpleJarvisAgent",
    "MCPJarvisAgent",
    "EnhancedJarvisAgent",
    "WorkflowJarvisAgent",
    "CodingAgent",
    
    # Managers
    "DatabaseManager",
    "get_database_manager",
    "SecurityManager",
    "get_security_manager",
    
    # Workflow components
    "WorkflowEngine",
    "WorkflowTemplates",
    "create_workflow",
    "create_code_review_workflow",
    "create_deployment_workflow",
    "create_project_analysis_workflow",
    "create_bug_fix_workflow",
]
