"""Lightweight workflow engine with persistence and DAG events."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Callable, Dict, List, Optional, Any

from agent.ui.dag_panel import StepEvent


class TaskState(str, Enum):
    """Possible states for a workflow task."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A single executable unit within a workflow."""

    id: str
    fn: Callable[[Dict[str, Any]], Any]
    depends_on: List[str] = field(default_factory=list)
    state: TaskState = TaskState.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    runtime: float = 0.0


@dataclass
class Workflow:
    """Collection of tasks tracked under a run identifier."""

    id: str
    tasks: Dict[str, Task]
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Execute workflows and emit :class:`StepEvent` records."""

    def __init__(
        self,
        storage_dir: str = "logs/workflows",
        event_handler: Optional[Callable[[StepEvent], None]] = None,
    ) -> None:
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.event_handler = event_handler or (lambda e: None)
        self.active_workflows: Dict[str, Workflow] = {}

    # ------------------------------------------------------------------
    # Workflow creation & persistence
    # ------------------------------------------------------------------
    def create_workflow(
        self, tasks: List[Task], metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Register a new workflow and persist its definition."""

        run_id = uuid.uuid4().hex
        workflow = Workflow(id=run_id, tasks={t.id: t for t in tasks}, metadata=metadata or {})
        self.active_workflows[run_id] = workflow
        self._persist_definition(workflow)
        return workflow

    def _persist_definition(self, workflow: Workflow) -> None:
        path = os.path.join(self.storage_dir, f"{workflow.id}_definition.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "id": workflow.id,
                    "tasks": {tid: {"depends_on": t.depends_on} for tid, t in workflow.tasks.items()},
                    "metadata": workflow.metadata,
                },
                fh,
                indent=2,
            )

    def _persist_event(self, event: StepEvent) -> None:
        path = os.path.join(self.storage_dir, f"{event.run_id}_events.json")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(event)) + "\n")

    def _emit_event(self, event: StepEvent) -> None:
        self._persist_event(event)
        self.event_handler(event)

    # ------------------------------------------------------------------
    # Workflow execution
    # ------------------------------------------------------------------
    def run(self, workflow: Workflow, context: Optional[Dict[str, Any]] = None) -> Dict[str, Task]:
        """Execute tasks when their dependencies are satisfied."""

        context = context or {}
        while True:
            ready = [
                t
                for t in workflow.tasks.values()
                if t.state is TaskState.PENDING
                and all(workflow.tasks[d].state is TaskState.COMPLETED for d in t.depends_on)
            ]
            for task in ready:
                task.state = TaskState.READY

            if not ready:
                pending = [t for t in workflow.tasks.values() if t.state is TaskState.PENDING]
                running = [t for t in workflow.tasks.values() if t.state is TaskState.RUNNING]
                if not running:
                    # Mark unresolved tasks as failed
                    for task in pending:
                        task.state = TaskState.FAILED
                        task.error = "Unresolved dependencies"
                        self._emit_event(
                            StepEvent(
                                run_id=workflow.id,
                                step_id=task.id,
                                parent_id=task.depends_on[0] if task.depends_on else None,
                                event_type="error",
                                payload={"error": task.error},
                                status="failed",
                            )
                        )
                    break

            for task in [t for t in workflow.tasks.values() if t.state is TaskState.READY]:
                self._run_task(workflow, task, context)

        return workflow.tasks

    def _run_task(self, workflow: Workflow, task: Task, context: Dict[str, Any]) -> None:
        parent = task.depends_on[0] if task.depends_on else None
        self._emit_event(
            StepEvent(
                run_id=workflow.id,
                step_id=task.id,
                parent_id=parent,
                event_type="start",
                payload={},
                status="active",
            )
        )
        task.state = TaskState.RUNNING
        start = time.time()
        try:
            result = task.fn(context)
            task.result = result
            task.state = TaskState.COMPLETED
            task.runtime = time.time() - start
            self._emit_event(
                StepEvent(
                    run_id=workflow.id,
                    step_id=task.id,
                    parent_id=parent,
                    event_type="complete",
                    payload={"result": result},
                    status="completed",
                )
            )
        except Exception as exc:  # pragma: no cover - safety net
            task.error = str(exc)
            task.state = TaskState.FAILED
            task.runtime = time.time() - start
            self._emit_event(
                StepEvent(
                    run_id=workflow.id,
                    step_id=task.id,
                    parent_id=parent,
                    event_type="error",
                    payload={"error": task.error},
                    status="failed",
                )
            )

    # ------------------------------------------------------------------
    # Recovery helpers
    # ------------------------------------------------------------------
    def load_workflow(self, run_id: str) -> Workflow:
        """Load a workflow definition without executable functions."""

        path = os.path.join(self.storage_dir, f"{run_id}_definition.json")
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        tasks = {
            tid: Task(id=tid, fn=lambda _ctx: None, depends_on=info["depends_on"])
            for tid, info in data["tasks"].items()
        }
        return Workflow(id=data["id"], tasks=tasks, metadata=data.get("metadata", {}))

    def replay_events(self, run_id: str) -> List[StepEvent]:
        """Return the list of previously emitted events for a workflow."""

        path = os.path.join(self.storage_dir, f"{run_id}_events.json")
        events: List[StepEvent] = []
        if not os.path.exists(path):
            return events
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                events.append(StepEvent(**json.loads(line)))
        return events
