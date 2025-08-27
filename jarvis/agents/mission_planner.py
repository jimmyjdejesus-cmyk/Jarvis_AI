"""Mission Planner - Breaks high-level goals into tasks using LLM."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from jarvis.models.client import model_client
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
        client=model_client,
        model: str = "llama3.2",
        predictor: PredictiveSimulator | None = None,
        memory: Optional[MemoryManager] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        event_handler: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.client = client
        self.model = model
        self.predictor = predictor
        self.memory = memory
        self.knowledge_graph = knowledge_graph
        self.event_handler = event_handler or (lambda _name, _payload: None)

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

        if memory_hits:
            nodes["memory_recall"] = MissionNode(
                step_id="memory_recall",
                capability="memory_lookup",
                team_scope="memory",
            )
            rationale.append("project memory")

        if kg_neighbors:
            nodes["kg_scan"] = MissionNode(
                step_id="kg_scan",
                capability="kg_lookup",
                team_scope="knowledge",
                deps=["memory_recall"] if "memory_recall" in nodes else [],
            )
            if "memory_recall" in nodes:
                edges.append(("memory_recall", "kg_scan"))
            rationale.append("knowledge graph")

        final_id = "execute_goal"
        nodes[final_id] = MissionNode(
            step_id=final_id,
            capability="execution",
            team_scope="core",
            deps=list(nodes.keys()),
        )
        for dep in nodes:
            if dep != final_id:
                edges.append((dep, final_id))

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
