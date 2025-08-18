"""
Workflow system for chaining plugin actions and handling approval previews.

This module provides workflow chaining capabilities, allowing users to create
complex automation sequences with natural language commands.
"""

import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from agent.plugin_base import PluginAction, PluginResult, BasePlugin
from agent.plugin_registry import plugin_manager


logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    action: PluginAction
    plugin_name: str
    depends_on: List[int] = None  # Indices of steps this depends on
    output_mapping: Dict[str, str] = None  # Map output to input of next steps
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.output_mapping is None:
            self.output_mapping = {}


@dataclass
class Workflow:
    """A workflow consisting of multiple steps."""
    name: str
    description: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass 
class WorkflowResult:
    """Result of a workflow execution."""
    workflow: Workflow
    step_results: List[PluginResult]
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0


class WorkflowParser:
    """Parses natural language commands into workflows."""
    
    def __init__(self):
        # Common workflow patterns
        self.workflow_patterns = [
            # Sequential workflow pattern: "do X then Y then Z"
            {
                'pattern': r'(.+?)\s+then\s+(.+)',
                'type': 'sequential'
            },
            # Conditional workflow: "if X then Y"
            {
                'pattern': r'if\s+(.+?)\s+then\s+(.+)',
                'type': 'conditional'
            },
            # Parallel workflow: "do X and Y"
            {
                'pattern': r'(.+?)\s+and\s+(.+)',
                'type': 'parallel'
            },
            # Chain workflow: "pull repo, run tests, open results"
            {
                'pattern': r'(.+?),\s*(.+)',
                'type': 'chain'
            }
        ]
    
    def parse_workflow(self, command: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Parse a natural language command into a workflow."""
        command = command.strip()
        
        # Check if this is a workflow command
        workflow_type = self._detect_workflow_type(command)
        if not workflow_type:
            # Try to parse as a single action
            action = plugin_manager.parse_command(command, context)
            if action:
                step = WorkflowStep(action=action, plugin_name=action.name.split('_')[0])
                return Workflow(
                    name=f"Single Action: {action.name}",
                    description=command,
                    steps=[step]
                )
            return None
        
        if workflow_type == 'sequential':
            return self._parse_sequential_workflow(command, context)
        elif workflow_type == 'chain':
            return self._parse_chain_workflow(command, context)
        elif workflow_type == 'parallel':
            return self._parse_parallel_workflow(command, context)
        elif workflow_type == 'conditional':
            return self._parse_conditional_workflow(command, context)
        
        return None
    
    def _detect_workflow_type(self, command: str) -> Optional[str]:
        """Detect the type of workflow from the command."""
        command_lower = command.lower()
        
        for pattern_info in self.workflow_patterns:
            if re.search(pattern_info['pattern'], command_lower):
                return pattern_info['type']
        
        return None
    
    def _parse_sequential_workflow(self, command: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Parse a sequential workflow (X then Y then Z)."""
        parts = re.split(r'\s+then\s+', command, flags=re.IGNORECASE)
        return self._create_workflow_from_parts(parts, "Sequential Workflow", command, context, sequential=True)
    
    def _parse_chain_workflow(self, command: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Parse a chain workflow (X, Y, Z)."""
        parts = [part.strip() for part in command.split(',')]
        return self._create_workflow_from_parts(parts, "Chain Workflow", command, context, sequential=True)
    
    def _parse_parallel_workflow(self, command: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Parse a parallel workflow (X and Y)."""
        parts = re.split(r'\s+and\s+', command, flags=re.IGNORECASE)
        return self._create_workflow_from_parts(parts, "Parallel Workflow", command, context, sequential=False)
    
    def _parse_conditional_workflow(self, command: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Parse a conditional workflow (if X then Y)."""
        match = re.match(r'if\s+(.+?)\s+then\s+(.+)', command, re.IGNORECASE)
        if not match:
            return None
        
        condition_part = match.group(1).strip()
        action_part = match.group(2).strip()
        
        # For now, treat condition as a regular action
        # In the future, this could be enhanced with actual conditional logic
        parts = [condition_part, action_part]
        return self._create_workflow_from_parts(parts, "Conditional Workflow", command, context, sequential=True)
    
    def _create_workflow_from_parts(self, parts: List[str], name: str, description: str, 
                                  context: Dict[str, Any] = None, sequential: bool = True) -> Optional[Workflow]:
        """Create a workflow from parsed command parts."""
        if not parts:
            return None
        
        steps = []
        for i, part in enumerate(parts):
            action = plugin_manager.parse_command(part.strip(), context)
            if not action:
                logger.warning(f"Could not parse workflow step: {part}")
                continue
            
            depends_on = [i-1] if sequential and i > 0 else []
            plugin_name = action.name.split('_')[0] if '_' in action.name else action.name
            
            step = WorkflowStep(
                action=action,
                plugin_name=plugin_name,
                depends_on=depends_on
            )
            steps.append(step)
        
        if not steps:
            return None
        
        return Workflow(
            name=name,
            description=description,
            steps=steps
        )


class WorkflowExecutor:
    """Executes workflows with approval and monitoring capabilities."""
    
    def __init__(self, approval_callback: Optional[Callable[[Workflow], bool]] = None):
        self.approval_callback = approval_callback
        self.active_workflows: Dict[str, Workflow] = {}
    
    def preview_workflow(self, workflow: Workflow) -> str:
        """Generate a human-readable preview of the workflow."""
        preview_lines = [
            f"Workflow: {workflow.name}",
            f"Description: {workflow.description}",
            f"Steps ({len(workflow.steps)}):"
        ]
        
        for i, step in enumerate(workflow.steps, 1):
            preview = plugin_manager.preview_action(step.action)
            depends_text = ""
            if step.depends_on:
                depends_text = f" (depends on step{'s' if len(step.depends_on) > 1 else ''} {', '.join(map(str, [d+1 for d in step.depends_on]))})"
            
            preview_lines.append(f"  {i}. {preview}{depends_text}")
        
        # Check for actions that require approval
        approval_steps = [i+1 for i, step in enumerate(workflow.steps) if step.action.requires_approval]
        if approval_steps:
            preview_lines.append(f"\nSteps requiring approval: {', '.join(map(str, approval_steps))}")
        
        return "\n".join(preview_lines)
    
    def execute_workflow(self, workflow: Workflow, context: Dict[str, Any] = None) -> WorkflowResult:
        """Execute a workflow with approval handling."""
        import time
        start_time = time.time()
        
        try:
            # Check if approval is needed
            if self._requires_approval(workflow):
                workflow.status = WorkflowStatus.PENDING
                if self.approval_callback:
                    if not self.approval_callback(workflow):
                        workflow.status = WorkflowStatus.CANCELLED
                        return WorkflowResult(
                            workflow=workflow,
                            step_results=[],
                            success=False,
                            error="Workflow cancelled by user"
                        )
            
            workflow.status = WorkflowStatus.APPROVED
            
            # Store workflow as active
            workflow_id = f"wf_{int(time.time())}"
            self.active_workflows[workflow_id] = workflow
            
            try:
                workflow.status = WorkflowStatus.RUNNING
                step_results = self._execute_steps(workflow.steps, context or {})
                workflow.status = WorkflowStatus.COMPLETED
                
                success = all(result.success for result in step_results)
                error = None if success else "One or more steps failed"
                
                return WorkflowResult(
                    workflow=workflow,
                    step_results=step_results,
                    success=success,
                    error=error,
                    execution_time=time.time() - start_time
                )
            
            finally:
                # Remove from active workflows
                if workflow_id in self.active_workflows:
                    del self.active_workflows[workflow_id]
        
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            return WorkflowResult(
                workflow=workflow,
                step_results=[],
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _requires_approval(self, workflow: Workflow) -> bool:
        """Check if the workflow requires approval."""
        return any(step.action.requires_approval for step in workflow.steps)
    
    def _execute_steps(self, steps: List[WorkflowStep], context: Dict[str, Any]) -> List[PluginResult]:
        """Execute workflow steps respecting dependencies."""
        results = [None] * len(steps)
        executed = [False] * len(steps)
        step_outputs = {}
        
        while not all(executed):
            progress_made = False
            
            for i, step in enumerate(steps):
                if executed[i]:
                    continue
                
                # Check if dependencies are met
                if all(executed[dep] for dep in step.depends_on):
                    # Prepare context with outputs from dependent steps
                    step_context = context.copy()
                    for dep_idx in step.depends_on:
                        if dep_idx in step_outputs:
                            step_context.update(step_outputs[dep_idx])
                    
                    # Execute the step
                    try:
                        result = plugin_manager.execute_action(step.action, step_context)
                        results[i] = result
                        executed[i] = True
                        progress_made = True
                        
                        # Store output for dependent steps
                        if result.success and result.output:
                            step_outputs[i] = {"previous_output": result.output}
                    
                    except Exception as e:
                        results[i] = PluginResult(success=False, output=None, error=str(e))
                        executed[i] = True
                        progress_made = True
            
            if not progress_made:
                # Circular dependency or other issue
                for i, executed_flag in enumerate(executed):
                    if not executed_flag:
                        results[i] = PluginResult(
                            success=False, 
                            output=None, 
                            error="Dependency resolution failed"
                        )
                        executed[i] = True
                break
        
        return [r for r in results if r is not None]


# Global workflow parser and executor
workflow_parser = WorkflowParser()
workflow_executor = WorkflowExecutor()