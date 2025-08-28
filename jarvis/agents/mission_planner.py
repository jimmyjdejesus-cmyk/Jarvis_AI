"""Mission Planner - Breaks high-level goals into tasks using LLM."""

from __future__ import annotations

import logging
import json
from typing import Any, Callable, Dict, List, Optional

from jarvis.world_model.predictive_simulation import PredictiveSimulator
try:  # pragma: no cover - optional dependency
    from jarvis.memory.project_memory import MemoryManager, ProjectMemory
except Exception:  # pragma: no cover - fallback for tests
    class MemoryManager:  # type: ignore[misc]
        def add(
            self, *args: Any, **kwargs: Any
        ) -> None:  # pragma: no cover - stub
            raise NotImplementedError

        def query(
            self, *args: Any, **kwargs: Any
        ) -> list[dict]:  # pragma: no cover - stub
            return []

    ProjectMemory = None  # type: ignore
from jarvis.world_model.knowledge_graph import KnowledgeGraph
from jarvis.orchestration.mission import (
    Mission,
    MissionDAG,
    MissionNode,
    save_mission,
)
import uuid

logger = logging.getLogger(__name__)


class MissionPlanner:
    """Plan missions by decomposing goals into executable tasks."""

    def __init__(
        self,
        client=None,
        model: str = "llama3.2",
        predictor: PredictiveSimulator | None = None,
        memory: Optional[MemoryManager] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        event_handler: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        if client is None:
            from jarvis.models.client import model_client
            self.client = model_client
        else:
            self.client = client
        self.model = model
        self.predictor = predictor
        self.memory = memory
        self.knowledge_graph = knowledge_graph
        self.event_handler = event_handler or (lambda _name, _payload: None)

    def _create_planning_prompt(self, goal: str, context: Dict[str, Any], memory_hits: List[Dict[str, Any]], kg_neighbors: List[str]) -> str:
        """Create the prompt for the LLM to generate a mission plan."""

        prompt = f"""You are an expert project planner. Your task is to break down a high-level goal into a series of smaller, actionable tasks.
The output must be a JSON object with a single key "tasks", which is a list of strings. Each string is a task.

Goal: {goal}
"""

        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2)}\n"

        if memory_hits:
            prompt += f"\nRelevant information from past projects:\n{json.dumps(memory_hits, indent=2)}\n"

        if kg_neighbors:
            prompt += f"\nRelevant files in the current project:\n{', '.join(kg_neighbors)}\n"

        prompt += "\nJSON output:"
        return prompt

    def plan(self, goal: str, context: Dict[str, Any]) -> MissionDAG:
        """Create and persist a mission plan for ``goal``.

        The planner consults project memory and the knowledge graph to propose
        initial steps and records a rationale. A ``Mission_Planned`` event is
        emitted with the DAG payload. If ``knowledge_graph`` is provided, the
        mission's nodes and edges are also persisted for historical audit.
        """

        project = context.get("project", "default")
        session = context.get("session", "default")

        memory_hits: List[Dict[str, Any]] = []
        if self.memory:
            try:
                memory_hits = self.memory.query(project, session, goal) or []
            except Exception:  # pragma: no cover - optional memory
                memory_hits = []

        kg_neighbors: List[str] = []
        if self.knowledge_graph:
            try:
                kg_neighbors = self.knowledge_graph.get_files()
            except Exception:  # pragma: no cover - optional KG
                kg_neighbors = []

        nodes: Dict[str, MissionNode] = {}
        edges: List[tuple[str, str]] = []
        rationale: List[str] = []

        # New LLM-based planning
        prompt = self._create_planning_prompt(goal, context, memory_hits, kg_neighbors)
        llm_response = self.client.generate_response(self.model, prompt)

        try:
            # Extract the JSON part of the response
            json_response_str = llm_response[llm_response.find('{'):llm_response.rfind('}')+1]
            planned_tasks = json.loads(json_response_str)
            task_list = planned_tasks.get("tasks", [])
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse LLM response for mission planning. Falling back to basic plan.")
            task_list = [goal] # Fallback to a single task

        nodes: Dict[str, MissionNode] = {}
        edges: List[tuple[str, str]] = []
        last_node_id = None

        # Create nodes for each task from the LLM
        for i, task_description in enumerate(task_list):
            node_id = f"task_{i+1}"
            nodes[node_id] = MissionNode(
                step_id=node_id,
                capability="execution", # Or determine from task
                team_scope="core",
                details=task_description,
                deps=[last_node_id] if last_node_id else []
            )
            if last_node_id:
                edges.append((last_node_id, node_id))
            last_node_id = node_id

        rationale = ["LLM-generated plan"]

        rationale_text = "; ".join(rationale) if rationale else "basic plan"
        mission_id = uuid.uuid4().hex
        dag = MissionDAG(
            mission_id=mission_id,
            nodes=nodes,
            edges=edges,
            rationale=rationale_text,
        )
        mission = Mission(
            id=mission_id,
            title=context.get("title", goal),
            goal=goal,
            inputs=context.get("inputs", {}),
            risk_level=context.get("risk_level", "low"),
            dag=dag,
        )
        save_mission(mission)
        if self.knowledge_graph:
            for node in dag.nodes.values():
                try:
                    self.knowledge_graph.add_node(
                        node.step_id,
                        "mission_node",
                        {
                            "mission_id": mission_id,
                            "capability": node.capability,
                            "team_scope": node.team_scope,
                            "hitl_gate": node.hitl_gate,
                            "status": node.state.status,
                        },
                    )
                except Exception as e:  # pragma: no cover - optional KG
                    logger.warning("Failed to add mission node %s to knowledge graph: %s", node.step_id, e)
            for src, tgt in dag.edges:
                try:
                    self.knowledge_graph.add_edge(
                        src, tgt, "depends_on", {"mission_id": mission_id}
                    )
                except Exception as e:  # pragma: no cover - optional KG
                    logger.warning("Failed to add mission edge %s->%s to knowledge graph: %s", src, tgt, e)
        try:
            self.event_handler("Mission_Planned", dag.to_dict())
        except Exception:  # pragma: no cover - event handler optional
            pass
        logger.debug("Planned DAG: %s", dag.to_dict())
        return dag

    def to_graph(self, tasks: List[str]) -> Dict[str, Any]:
        """Create a simple sequential LangGraph definition from tasks."""
        nodes = {
            f"task_{i+1}": {"description": task}
            for i, task in enumerate(tasks)
        }
        edges = [
            (f"task_{i}", f"task_{i+1}")
            for i in range(1, len(tasks))
        ]
        return {"nodes": nodes, "edges": edges}
