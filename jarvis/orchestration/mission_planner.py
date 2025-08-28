"""Mission planning utilities for the orchestration layer.

This module bridges high level mission descriptions and the task queue used by
the orchestrator.  The previous implementation simply loaded YAML definitions
and enqueued each task.  The new planner leverages the LLM driven
``jarvis.agents.mission_planner`` to generate a directed acyclic graph (DAG)
for a mission.  Each node is automatically assigned to a team based on
knowledge graph facts and sub‑tasks are expanded into their own sub‑DAGs.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any, Dict

import yaml

from jarvis.agents.mission_planner import MissionPlanner as LLMMissionPlanner
from jarvis.orchestration.mission import (
    Mission,
    MissionDAG,
    MissionNode,
    save_mission,
)
from jarvis.world_model.knowledge_graph import KnowledgeGraph

from .task_queue import RedisTaskQueue

logger = logging.getLogger(__name__)


class MissionPlanner:
    """Generate mission DAGs and enqueue their tasks for execution."""

    def __init__(
        self,
        missions_dir: str,
        queue: RedisTaskQueue | None = None,
        knowledge_graph: KnowledgeGraph | None = None,
    ) -> None:
        self.missions_dir = missions_dir
        self.queue = queue or RedisTaskQueue()
        self.knowledge_graph = knowledge_graph
        self.llm_planner = LLMMissionPlanner(knowledge_graph=knowledge_graph)
        self.last_dag: MissionDAG | None = None

    # ------------------------------------------------------------------
    def _mission_path(self, name: str) -> str:
        return os.path.join(self.missions_dir, f"{name}.yaml")

    # ------------------------------------------------------------------
    def load_mission(self, name: str) -> Dict[str, Any]:
        """Load a mission definition from disk."""

        path = self._mission_path(name)
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # ------------------------------------------------------------------
    def _assign_team(self, description: str) -> str:
        """Determine which team should execute ``description``.

        The knowledge graph stores simple factual triples of the form
        ``(team, "capable_of", capability)``.  A task is assigned to the first
        team whose capability string appears in the description.
        If no match is found, the task defaults to the "core" team.
        """

        if not self.knowledge_graph:
            return "core"
        desc = description.lower()
        facts = self.knowledge_graph.get_facts()
        for subject, predicate, obj, _ in facts:
            if (
                predicate == "capable_of"
                and obj.lower() in desc
            ):
                return subject
        return "core"

    # ------------------------------------------------------------------
    def _spawn_sub_dag(
        self,
        dag: MissionDAG,
        node: MissionNode,
        context: Dict[str, Any],
    ) -> None:
        """Expand ``node`` into a sub‑DAG and merge into ``dag``.

        Only a single level of expansion is performed to avoid infinite
        recursion.  The sub‑DAG is planned using the same LLM planner and its
        nodes are linked sequentially starting from ``node``.
        """

        try:
            sub_dag = self.llm_planner.plan(node.details or "", context)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Failed to spawn sub-DAG for %s: %s", node.step_id, exc
            )
            return
        # Skip if the planner returned a single step identical to the parent
        if len(sub_dag.nodes) <= 1:
            return
        prev = node.step_id
        for sub_id, sub_node in sub_dag.nodes.items():
            new_id = f"{node.step_id}_{sub_id}"
            sub_node.step_id = new_id
            sub_node.team_scope = self._assign_team(sub_node.details or "")
            dag.nodes[new_id] = sub_node
            dag.edges.append((prev, new_id))
            prev = new_id

    # ------------------------------------------------------------------
    def plan(
        self,
        name: str | None = None,
        goal: str | None = None,
        context: Dict[str, Any] | None = None,
    ) -> MissionDAG:
        """Create a mission plan.

        Parameters
        ----------
        name:
            Optional mission file name in ``config/missions``.
            If provided, the file supplies the goal and context for planning.
        goal:
            Explicit mission goal.  Used when ``name`` is not supplied.
        context:
            Additional planning context.

        Returns
        -------
        MissionDAG
            The generated mission DAG.  All tasks are enqueued onto the task
            queue and the DAG is persisted for later retrieval.
        """

        if name:
            mission = self.load_mission(name)
            goal = mission.get("goal")
            context = mission.get("context", {})
        if goal is None:
            raise ValueError("A mission goal must be provided")
        context = context or {}

        dag = self.llm_planner.plan(goal, context)

        for node in list(dag.nodes.values()):
            node.team_scope = self._assign_team(node.details or "")
            self._spawn_sub_dag(dag, node, context)

        for node in dag.nodes.values():
            self.queue.enqueue(
                {
                    "id": node.step_id,
                    "description": node.details,
                    "team": node.team_scope,
                }
            )

        mission_id = dag.mission_id or uuid.uuid4().hex
        mission = Mission(
            id=mission_id,
            title=context.get("title", goal),
            goal=goal,
            inputs=context.get("inputs", {}),
            risk_level=context.get("risk_level", "low"),
            dag=dag,
        )
        save_mission(mission)
        self.last_dag = dag
        return dag
