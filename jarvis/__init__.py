"""
Jarvis AI - Enhanced Core Package
Modern architecture with MCP, multi-agent, and advanced workflow capabilities
"""

__version__ = "4.0.0"
__author__ = "Jimmy De Jesus"

# Configuration
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
"""
Jarvis AI - Enhanced Core Package
Modern architecture with MCP, multi-agent, and advanced workflow capabilities
"""

__version__ = "4.0.0"
__author__ = "Jimmy De Jesus"

# Configuration
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
        WorkflowEngine, create_workflow, WorkflowTemplates,
        create_code_review_workflow, create_deployment_workflow,
        create_project_analysis_workflow, create_bug_fix_workflow
    )
except ImportError:
    WorkflowEngine = None
    WorkflowTemplates = None
    create_workflow = None
    create_code_review_workflow = None
    create_deployment_workflow = None
    create_project_analysis_workflow = None 
    create_bug_fix_workflow = None

# Main interface functions
def get_jarvis_agent(
    enable_mcp: bool = None, 
    enable_multi_agent: bool = None,
    enable_workflows: bool = None,
    mode: str = "auto"
):
    """
    Get Jarvis agent with configurable capabilities
    
    Args:
        enable_mcp: Enable MCP multi-model routing
        enable_multi_agent: Enable specialist agent coordination  
        enable_workflows: Enable advanced workflow orchestration
        mode: "simple", "mcp", "multi_agent", "workflow", "auto"
    
    Returns:
        Configured Jarvis agent
    """
    
    if mode == "simple" or not EnhancedJarvisAgent:
        if SimpleJarvisAgent:
            return SimpleJarvisAgent()
        else:
            raise ImportError("No Jarvis agent available")
    
    elif mode == "mcp":
        # Try enhanced agent first, fall back to MCP agent
        if EnhancedJarvisAgent:
            return EnhancedJarvisAgent(enable_mcp=True, enable_multi_agent=False)
        elif MCPJarvisAgent:
            return MCPJarvisAgent(enable_mcp=True, enable_multi_agent=False)
        else:
            # Fallback to simple
            if SimpleJarvisAgent:
                print("Warning: Enhanced agents not available, using simple agent")
                return SimpleJarvisAgent()
            else:
                raise ImportError("No Jarvis agent available")
    
    elif mode == "multi_agent":
        if EnhancedJarvisAgent:
            return EnhancedJarvisAgent(enable_mcp=True, enable_multi_agent=True)
        else:
            # Fallback to MCP or simple
            print("Warning: Multi-agent not available, falling back")
            return get_jarvis_agent(mode="mcp")
    
    elif mode == "workflow":
        # Phase 4: Advanced Workflow Mode
        if WorkflowJarvisAgent:
            return WorkflowJarvisAgent(enable_mcp=True, enable_multi_agent=True, enable_workflows=True)
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
        
        # Try workflow agent first (most capable)
        if WorkflowJarvisAgent and enable_workflows:
            try:
                return WorkflowJarvisAgent(
                    enable_mcp=enable_mcp, 
                    enable_multi_agent=enable_multi_agent,
                    enable_workflows=enable_workflows
                )
            except Exception as e:
                print(f"Warning: Workflow agent failed to initialize: {e}")
        
        # Fall back to enhanced agent
        if EnhancedJarvisAgent:
            try:
                return EnhancedJarvisAgent(enable_mcp=enable_mcp, enable_multi_agent=enable_multi_agent)
            except Exception as e:
                print(f"Warning: Enhanced agent failed to initialize: {e}")
        
        # Fall back to MCP agent
        if MCPJarvisAgent and enable_mcp:
            try:
                return MCPJarvisAgent(enable_mcp=enable_mcp, enable_multi_agent=False)
            except Exception as e:
                print(f"Warning: MCP agent failed to initialize: {e}")
        
        # Final fallback to simple agent
        if SimpleJarvisAgent:
            return SimpleJarvisAgent()
        else:
            raise ImportError("No Jarvis agent available")

# Convenience functions
def get_simple_jarvis():
    """Get simple Jarvis (fastest, local only)"""
    return get_jarvis_agent(mode="simple")

def get_smart_jarvis():
    """Get MCP-enabled Jarvis (multi-model routing)"""
    return get_jarvis_agent(mode="mcp")

def get_super_jarvis():
    """Get full multi-agent Jarvis (maximum capabilities)"""
    return get_jarvis_agent(mode="multi_agent")

def get_workflow_jarvis():
    """Get workflow-enabled Jarvis (Phase 4: Advanced orchestration)"""
    return get_jarvis_agent(mode="workflow")

def get_ultimate_jarvis():
    """Get the most advanced Jarvis (all capabilities enabled)"""
    return get_jarvis_agent(
        enable_mcp=True,
        enable_multi_agent=True, 
        enable_workflows=True,
        mode="auto"
    )

def get_coding_agent(base_agent=None, workspace_path: str = None):
    """Get enhanced coding agent"""
    if base_agent is None:
        base_agent = get_jarvis_agent()
    
    if CodingAgent:
        return CodingAgent(base_agent, workspace_path)
    else:
        print("Warning: CodingAgent not available")
        return base_agent

# Workflow convenience functions
def create_and_run_workflow(workflow_type: str, **kwargs):
    """Create and run a workflow using the workflow-enabled Jarvis"""
    
    if not WorkflowJarvisAgent:
        raise ImportError("Workflow capabilities not available")
    
    jarvis = get_workflow_jarvis()
    
    # Map workflow types to template functions
    if workflow_type == "code_review" and create_code_review_workflow:
        workflow = create_code_review_workflow(kwargs.get("file_path", "code.py"))
    elif workflow_type == "deployment" and create_deployment_workflow:
        workflow = create_deployment_workflow(
            kwargs.get("project_path", "."),
            kwargs.get("environment", "production")
        )
    elif workflow_type == "project_analysis" and create_project_analysis_workflow:
        workflow = create_project_analysis_workflow(kwargs.get("project_path", "."))
    elif workflow_type == "bug_fix" and create_bug_fix_workflow:
        workflow = create_bug_fix_workflow(
            kwargs.get("issue_description", "Bug to fix"),
            kwargs.get("code_files", [])
        )
    else:
        raise ValueError(f"Unknown or unavailable workflow type: {workflow_type}")
    
    # Execute the workflow
    return jarvis.execute_workflow_by_name(workflow_type, kwargs)

# Backward compatibility
JarvisAgent = get_jarvis_agent  # Alias for backward compatibility

__all__ = [
    'get_jarvis_agent',
    'get_simple_jarvis', 
    'get_smart_jarvis',
    'get_super_jarvis',
    'get_workflow_jarvis',
    'get_ultimate_jarvis',
    'get_coding_agent',
    'create_and_run_workflow',
    'JarvisAgent',
    'SimpleJarvisAgent',
    'MCPJarvisAgent',
    'EnhancedJarvisAgent',
    'WorkflowJarvisAgent',
    'DatabaseManager', 
    'get_database_manager',
    'SecurityManager',
    'get_security_manager',
    'CodingAgent',
    'WorkflowEngine',
    'WorkflowTemplates',
    'create_workflow',
    'create_code_review_workflow',
    'create_deployment_workflow',
    'create_project_analysis_workflow',
    'create_bug_fix_workflow'
]
