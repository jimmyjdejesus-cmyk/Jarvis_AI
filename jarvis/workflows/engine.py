"""
🚀 PHASE 4: ADVANCED WORKFLOW ENGINE

Core workflow orchestration system for complex multi-step task execution
with dependency management, conditional execution, and state tracking.
"""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

from jarvis.orchestration.mission import MissionDAG

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(Enum):
    """Individual task status"""
    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskResult:
    """Result of a workflow task execution"""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowContext:
    """Shared context across workflow execution"""
    workflow_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, TaskResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result from a specific task"""
        return self.results.get(task_id)
    
    def get_output(self, task_id: str) -> Any:
        """Get output from a specific task"""
        result = self.get_result(task_id)
        return result.output if result else None
    
    def set_variable(self, key: str, value: Any):
        """Set a workflow variable"""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a workflow variable"""
        return self.variables.get(key, default)

class WorkflowTask(ABC):
    """Abstract base class for workflow tasks"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 description: str = "",
                 dependencies: List[str] = None,
                 conditions: Dict[str, Any] = None,
                 timeout: float = 300.0):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.conditions = conditions or {}
        self.timeout = timeout
        self.status = TaskStatus.WAITING
    
    @abstractmethod
    async def execute(self, context: WorkflowContext) -> TaskResult:
        """Execute the task with given context"""
        pass
    
    def should_execute(self, context: WorkflowContext) -> bool:
        """Check if task should execute based on conditions"""
        if not self.conditions:
            return True
        
        for condition_key, expected_value in self.conditions.items():
            if "." in condition_key:
                # Handle nested conditions like "task1.status" or "variables.flag"
                parts = condition_key.split(".")
                if parts[0] == "variables":
                    actual_value = context.get_variable(parts[1])
                elif parts[0] in context.results:
                    result = context.get_result(parts[0])
                    if parts[1] == "status":
                        actual_value = result.status.value if result else None
                    elif parts[1] == "output":
                        actual_value = result.output if result else None
                    else:
                        actual_value = getattr(result, parts[1], None) if result else None
                else:
                    actual_value = None
            else:
                actual_value = context.get_variable(condition_key)
            
            if actual_value != expected_value:
                return False
        
        return True
    
    def dependencies_satisfied(self, context: WorkflowContext) -> bool:
        """Check if all dependencies are satisfied"""
        for dep_id in self.dependencies:
            result = context.get_result(dep_id)
            if not result or result.status != TaskStatus.COMPLETED:
                return False
        return True

class SpecialistTask(WorkflowTask):
    """Task that uses one of our specialist agents"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 specialist_type: str,
                 prompt: str,
                 description: str = "",
                 dependencies: List[str] = None,
                 conditions: Dict[str, Any] = None,
                 timeout: float = 300.0):
        super().__init__(task_id, name, description, dependencies, conditions, timeout)
        self.specialist_type = specialist_type
        self.prompt = prompt
    
    async def execute(self, context: WorkflowContext) -> TaskResult:
        """Execute using specialist agent"""
        start_time = datetime.now()
        
        try:
            # Import here to avoid circular imports
            from ..ecosystem.meta_intelligence import ExecutiveAgent

            orchestrator = ExecutiveAgent("workflow_meta")
            
            # Replace context variables in prompt
            formatted_prompt = self._format_prompt(context)
            
            # Execute with specific specialist
            result = await orchestrator.coordinate_specialists(
                formatted_prompt,
                [self.specialist_type],
                coordination_strategy="single"
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=self.task_id,
                status=TaskStatus.COMPLETED,
                output=result,
                execution_time=execution_time,
                metadata={"specialist": self.specialist_type}
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Task {self.task_id} failed: {str(e)}")
            
            return TaskResult(
                task_id=self.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                metadata={"specialist": self.specialist_type}
            )
    
    def _format_prompt(self, context: WorkflowContext) -> str:
        """Format prompt with context variables"""
        prompt = self.prompt
        
        # Replace variables
        for key, value in context.variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        # Replace task outputs
        for task_id, result in context.results.items():
            if result.output:
                prompt = prompt.replace(f"{{{task_id}.output}}", str(result.output))
        
        return prompt

class CustomTask(WorkflowTask):
    """Task that executes a custom function"""
    
    def __init__(self,
                 task_id: str,
                 name: str,
                 function: Callable[[WorkflowContext], Any],
                 description: str = "",
                 dependencies: List[str] = None,
                 conditions: Dict[str, Any] = None,
                 timeout: float = 300.0):
        super().__init__(task_id, name, description, dependencies, conditions, timeout)
        self.function = function
    
    async def execute(self, context: WorkflowContext) -> TaskResult:
        """Execute custom function"""
        start_time = datetime.now()
        
        try:
            # Execute function (handle both sync and async)
            if asyncio.iscoroutinefunction(self.function):
                result = await self.function(context)
            else:
                result = self.function(context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=self.task_id,
                status=TaskStatus.COMPLETED,
                output=result,
                execution_time=execution_time,
                metadata={"function": self.function.__name__}
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Task {self.task_id} failed: {str(e)}")
            
            return TaskResult(
                task_id=self.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                metadata={"function": self.function.__name__}
            )

@dataclass
class Workflow:
    """Workflow definition with tasks and execution logic"""
    
    workflow_id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    max_parallel: int = 5
    timeout: float = 3600.0  # 1 hour default
    retry_failed: bool = True
    max_retries: int = 3
    
    def __post_init__(self):
        self.status = WorkflowStatus.PENDING
        self.context = WorkflowContext(workflow_id=self.workflow_id)
        self.execution_start: Optional[datetime] = None
        self.execution_end: Optional[datetime] = None
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_ready_tasks(self) -> List[WorkflowTask]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        
        for task in self.tasks:
            if (task.status == TaskStatus.WAITING and 
                task.dependencies_satisfied(self.context) and 
                task.should_execute(self.context)):
                ready_tasks.append(task)
        
        return ready_tasks
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        for task in self.tasks:
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED]:
                return False
        return True
    
    def has_failed_critical_tasks(self) -> bool:
        """Check if any critical tasks have failed"""
        for task in self.tasks:
            if task.status == TaskStatus.FAILED:
                # For now, consider all failed tasks as critical
                # This could be enhanced with task criticality levels
                return True
        return False

class WorkflowEngine:
    """Advanced workflow orchestration engine"""
    
    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.completed_workflows: Dict[str, Workflow] = {}
        self.workflow_history: List[Dict[str, Any]] = []
    
    async def execute_workflow(self, workflow: Workflow) -> Workflow:
        """Execute a complete workflow"""
        logger.info(f"Starting workflow: {workflow.name} ({workflow.workflow_id})")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.execution_start = datetime.now()
        self.active_workflows[workflow.workflow_id] = workflow
        
        try:
            while not workflow.is_complete() and not workflow.has_failed_critical_tasks():
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # No tasks ready - check if we're stuck
                    waiting_tasks = [t for t in workflow.tasks if t.status == TaskStatus.WAITING]
                    if waiting_tasks:
                        logger.warning(f"Workflow {workflow.workflow_id} appears stuck - no ready tasks")
                        break
                    else:
                        break
                
                # Execute ready tasks (with parallelism limit)
                semaphore = asyncio.Semaphore(workflow.max_parallel)
                tasks_to_execute = ready_tasks[:workflow.max_parallel]
                
                # Mark tasks as running
                for task in tasks_to_execute:
                    task.status = TaskStatus.RUNNING
                
                # Execute tasks in parallel
                execution_coroutines = [
                    self._execute_task_with_semaphore(task, workflow, semaphore)
                    for task in tasks_to_execute
                ]
                
                await asyncio.gather(*execution_coroutines, return_exceptions=True)
            
            # Determine final status
            if workflow.has_failed_critical_tasks():
                workflow.status = WorkflowStatus.FAILED
            elif workflow.is_complete():
                workflow.status = WorkflowStatus.COMPLETED
            else:
                workflow.status = WorkflowStatus.FAILED  # Stuck or other issue
            
            workflow.execution_end = datetime.now()
            
            # Move to completed workflows
            self.completed_workflows[workflow.workflow_id] = workflow
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
            
            # Record in history
            self._record_workflow_completion(workflow)
            
            logger.info(f"Workflow {workflow.name} completed with status: {workflow.status.value}")
            
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} failed with exception: {str(e)}")
            workflow.status = WorkflowStatus.FAILED
            workflow.execution_end = datetime.now()
            
            # Move to completed workflows
            self.completed_workflows[workflow.workflow_id] = workflow
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
            
            self._record_workflow_completion(workflow)
            return workflow
    
    async def _execute_task_with_semaphore(self, task: WorkflowTask, workflow: Workflow, semaphore: asyncio.Semaphore):
        """Execute a single task with semaphore control"""
        async with semaphore:
            try:
                logger.info(f"Executing task: {task.name} ({task.task_id})")
                result = await asyncio.wait_for(task.execute(workflow.context), timeout=task.timeout)
                
                # Store result in context
                workflow.context.results[task.task_id] = result
                task.status = result.status
                
                logger.info(f"Task {task.name} completed with status: {result.status.value}")
                
            except asyncio.TimeoutError:
                logger.error(f"Task {task.task_id} timed out")
                task.status = TaskStatus.FAILED
                workflow.context.results[task.task_id] = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error="Task timed out"
                )
            
            except Exception as e:
                logger.error(f"Task {task.task_id} failed with exception: {str(e)}")
                task.status = TaskStatus.FAILED
                workflow.context.results[task.task_id] = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=str(e)
                )
    
    def _record_workflow_completion(self, workflow: Workflow):
        """Record workflow completion in history"""
        execution_time = 0.0
        if workflow.execution_start and workflow.execution_end:
            execution_time = (workflow.execution_end - workflow.execution_start).total_seconds()
        
        history_entry = {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "execution_time": execution_time,
            "task_count": len(workflow.tasks),
            "completed_tasks": len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in workflow.tasks if t.status == TaskStatus.FAILED]),
            "timestamp": workflow.execution_end or datetime.now()
        }
        
        self.workflow_history.append(history_entry)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        workflow = (self.active_workflows.get(workflow_id) or 
                   self.completed_workflows.get(workflow_id))
        
        if not workflow:
            return None
        
        task_statuses = {task.task_id: task.status.value for task in workflow.tasks}
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "task_statuses": task_statuses,
            "execution_start": workflow.execution_start,
            "execution_end": workflow.execution_end,
            "context_variables": workflow.context.variables
        }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.execution_end = datetime.now()
            
            # Move to completed
            self.completed_workflows[workflow_id] = workflow
            del self.active_workflows[workflow_id]
            
            self._record_workflow_completion(workflow)
            return True
        
        return False

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Workflow Builder Helper Functions
def create_workflow(name: str, description: str = "", max_parallel: int = 5) -> Workflow:
    """Create a new workflow"""
    workflow_id = str(uuid.uuid4())
    return Workflow(
        workflow_id=workflow_id,
        name=name,
        description=description,
        tasks=[],
        max_parallel=max_parallel
    )

def add_specialist_task(workflow: Workflow,
                       task_id: str,
                       name: str,
                       specialist_type: str,
                       prompt: str,
                       dependencies: List[str] = None,
                       conditions: Dict[str, Any] = None) -> Workflow:
    """Add a specialist task to workflow"""
    task = SpecialistTask(
        task_id=task_id,
        name=name,
        specialist_type=specialist_type,
        prompt=prompt,
        dependencies=dependencies,
        conditions=conditions
    )
    workflow.tasks.append(task)
    return workflow

def add_custom_task(workflow: Workflow,
                   task_id: str,
                   name: str,
                   function: Callable,
                   dependencies: List[str] = None,
                   conditions: Dict[str, Any] = None) -> Workflow:
    """Add a custom task to workflow"""
    task = CustomTask(
        task_id=task_id,
        name=name,
        function=function,
        dependencies=dependencies,
        conditions=conditions
    )
    workflow.tasks.append(task)
    return workflow

def from_mission_dag(dag: MissionDAG) -> Workflow:
    """Convert a MissionDAG to a Workflow that can be executed by the engine."""
    workflow = create_workflow(name=dag.mission_id, description=dag.rationale)

    for node_id, node in dag.nodes.items():
        # Use team_scope as the specialist_type, and details or capability as the prompt
        add_specialist_task(
            workflow=workflow,
            task_id=node.step_id,
            name=node.step_id,
            specialist_type=node.team_scope,
            prompt=node.details or node.capability,
            dependencies=node.deps,
        )

    return workflow
