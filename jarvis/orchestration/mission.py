from __future__ import annotations

import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - optional dependency
    from jarvis.world_model.knowledge_graph import KnowledgeGraph
except Exception:  # pragma: no cover
    KnowledgeGraph = Any  # type: ignore

from jarvis.world_model.neo4j_graph import Neo4jGraph


MISSION_DIR = os.path.join("data", "missions")
logger = logging.getLogger(__name__)


@dataclass
class MissionNodeState:
    """Runtime state for a mission node."""

    status: str = "pending"
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    provenance: Optional[dict] = None


@dataclass
class MissionNode:
    """Definition of a single mission step."""

    step_id: str
    capability: str
    team_scope: str
    details: Optional[str] = None
    hitl_gate: bool = False
    deps: List[str] = field(default_factory=list)
    state: MissionNodeState = field(default_factory=MissionNodeState)


@dataclass
class MissionDAG:
    """Directed acyclic graph of mission steps."""

    mission_id: str
    nodes: Dict[str, MissionNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> Dict[str, any]:
        return {
            "mission_id": self.mission_id,
            "nodes": {
                k: {**asdict(v), "state": asdict(v.state)}
                for k, v in self.nodes.items()
            },
            "edges": list(self.edges),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "MissionDAG":
        nodes = {
            k: MissionNode(
                step_id=v["step_id"],
                capability=v["capability"],
                team_scope=v["team_scope"],
                details=v.get("details"),
                hitl_gate=v.get("hitl_gate", False),
                deps=v.get("deps", []),
                state=MissionNodeState(**v.get("state", {})),
            )
            for k, v in data.get("nodes", {}).items()
        }
        edges = [tuple(e) for e in data.get("edges", [])]
        return cls(
            mission_id=data["mission_id"],
            nodes=nodes,
            edges=edges,
            rationale=data.get("rationale", ""),
        )


@dataclass
class Mission:
    """Top level mission container."""

    id: str
    title: str
    goal: str
    inputs: Dict[str, any]
    risk_level: str
    dag: MissionDAG

    def to_dict(self) -> Dict[str, any]:
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "inputs": self.inputs,
            "risk_level": self.risk_level,
            "dag": self.dag.to_dict(),
        }


def save_mission(mission: Mission, graph: Optional[Neo4jGraph] = None) -> None:
    os.makedirs(MISSION_DIR, exist_ok=True)
    path = os.path.join(MISSION_DIR, f"{mission.id}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(mission.to_dict(), fh, indent=2)
    graph = graph or Neo4jGraph()
    try:
        graph.write_mission_dag(mission.dag)
    except Exception as exc:  # pragma: no cover - neo4j optional
        logger.warning("Neo4j persistence failed: %s", exc)


def load_mission(mission_id: str) -> Mission:
    path = os.path.join(MISSION_DIR, f"{mission_id}.json")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    dag = MissionDAG.from_dict(data["dag"])
    return Mission(
        id=data["id"],
        title=data["title"],
        goal=data["goal"],
        inputs=data.get("inputs", {}),
        risk_level=data.get("risk_level", "low"),
        dag=dag,
    )


def load_mission_dag_from_neo4j(mission_id: str, graph: Optional[Neo4jGraph] = None) -> MissionDAG:
    """Retrieve a mission DAG from Neo4j."""

    graph = graph or Neo4jGraph()
    return graph.read_mission_dag(mission_id)


def update_node_state(
    mission_id: str,
    step_id: str,
    state: str,
    provenance: Optional[dict] = None,
    graph: KnowledgeGraph | None = None,
) -> None:
    """Persist state transition for a mission node and graph."""

    mission = load_mission(mission_id)
    node = mission.dag.nodes.get(step_id)
    if not node:
        return
    now = time.time()
    node.state.status = state
    if state == "running":
        node.state.started_at = now
    elif state in {"succeeded", "failed"}:
        node.state.completed_at = now
    node.state.provenance = provenance
    mission.dag.nodes[step_id] = node
    save_mission(mission)
    if graph:
        attrs: Dict[str, Any] = {
            "mission_id": mission_id,
            "status": state,
        }
        if provenance:
            attrs["provenance"] = provenance
        try:
            graph.add_node(step_id, "mission_node", attrs)
        except Exception:  # pragma: no cover - optional graph
            pass


def get_mission_graph(
    mission_id: str, graph: KnowledgeGraph
) -> Dict[str, Any]:
    """Return nodes and edges for ``mission_id`` from ``graph``."""

    nodes: List[tuple[str, Dict[str, Any]]] = []
    edges: List[tuple[str, str, Dict[str, Any]]] = []
    if hasattr(graph, "graph"):
        # type: ignore[attr-defined]
        for nid, data in graph.graph.nodes(data=True):
            if data.get("mission_id") == mission_id:
                nodes.append((nid, data))
        # type: ignore[attr-defined]
        for src, tgt, data in graph.graph.edges(data=True):
            if data.get("mission_id") == mission_id:
                edges.append((src, tgt, data))
    elif hasattr(graph, "driver"):
        with graph.driver.session() as session:  # type: ignore[attr-defined]
            node_res = session.run(
                "MATCH (n:Node {mission_id: $mid}) RETURN n.id AS id, n",
                mid=mission_id,
            )
            nodes = [(r["id"], dict(r["n"])) for r in node_res]
            edge_res = session.run(
                (
                    "MATCH (a:Node {mission_id: $mid})-[r]->"
                    "(b:Node {mission_id: $mid}) "
                    "RETURN a.id AS source, b.id AS target, TYPE(r) AS type, r"
                ),
                mid=mission_id,
            )
            edges = [
                (
                    r["source"],
                    r["target"],
                    {"type": r["type"], **dict(r["r"])},
                )
                for r in edge_res
            ]
    return {"nodes": nodes, "edges": edges}
