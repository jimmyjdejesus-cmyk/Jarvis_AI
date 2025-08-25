from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple


MISSION_DIR = os.path.join("data", "missions")


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
            "nodes": {k: {**asdict(v), "state": asdict(v.state)} for k, v in self.nodes.items()},
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
                hitl_gate=v.get("hitl_gate", False),
                deps=v.get("deps", []),
                state=MissionNodeState(**v.get("state", {})),
            )
            for k, v in data.get("nodes", {}).items()
        }
        edges = [tuple(e) for e in data.get("edges", [])]
        return cls(mission_id=data["mission_id"], nodes=nodes, edges=edges, rationale=data.get("rationale", ""))


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


def save_mission(mission: Mission) -> None:
    os.makedirs(MISSION_DIR, exist_ok=True)
    path = os.path.join(MISSION_DIR, f"{mission.id}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(mission.to_dict(), fh, indent=2)


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


def update_node_state(
    mission_id: str,
    step_id: str,
    state: str,
    provenance: Optional[dict] = None,
) -> None:
    """Persist state transition for a mission node."""

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
