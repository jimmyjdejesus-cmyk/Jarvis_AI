"""
🚀 PHASE 4: WORKFLOW SYSTEM

Advanced workflow orchestration system for complex task automation,
intelligent problem-solving, and deep system integration.

This module provides:
- Workflow Engine: Task orchestration with dependency management
- Workflow Templates: Pre-built patterns for common scenarios  
- Integration Adapters: Deep system integration capabilities
- Workflow-Enhanced Agent: Intelligent workflow detection and execution

Key Features:
- Multi-step task orchestration
- Conditional workflow execution
- Parallel processing with resource management
- Integration with file systems, code generation, testing, and git
- Automated workflow detection from natural language
- Comprehensive workflow monitoring and analytics
"""

from .engine import (
    WorkflowEngine, Workflow, WorkflowTask, WorkflowContext, WorkflowStatus,
    SpecialistTask, CustomTask, TaskResult, TaskStatus,
    create_workflow, add_specialist_task, add_custom_task
)

from .templates import (
    WorkflowTemplates,
    create_code_review_workflow,
    create_deployment_workflow, 
    create_project_analysis_workflow,
    create_bug_fix_workflow
)

from .integrations import (
    IntegrationManager, IntegrationAdapter,
    FileSystemAdapter, CodeGenerationAdapter, TestingAdapter, GitAdapter,
    integration_manager,
    read_file, write_file, run_tests, git_status, analyze_code
)

from .workflow_agent import (
    WorkflowJarvisAgent,
    create_workflow_jarvis
)

__all__ = [
    # Core Engine
    "WorkflowEngine",
    "Workflow", 
    "WorkflowTask",
    "WorkflowContext",
    "WorkflowStatus",
    "SpecialistTask",
    "CustomTask", 
    "TaskResult",
    "TaskStatus",
    
    # Builder Functions
    "create_workflow",
    "add_specialist_task",
    "add_custom_task",
    
    # Templates
    "WorkflowTemplates",
    "create_code_review_workflow",
    "create_deployment_workflow",
    "create_project_analysis_workflow", 
    "create_bug_fix_workflow",
    
    # Integrations
    "IntegrationManager",
    "IntegrationAdapter",
    "FileSystemAdapter",
    "CodeGenerationAdapter", 
    "TestingAdapter",
    "GitAdapter",
    "integration_manager",
    "read_file",
    "write_file",
    "run_tests", 
    "git_status",
    "analyze_code",
    
    # Enhanced Agent
    "WorkflowJarvisAgent",
    "create_workflow_jarvis"
]

# Version info
__version__ = "4.0.0"
__phase__ = "Phase 4: Advanced Workflows"
