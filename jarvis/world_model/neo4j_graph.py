"""Lightweight Neo4j adapter mirroring :class:`KnowledgeGraph` API."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, TYPE_CHECKING

from neo4j import GraphDatabase, Driver

if TYPE_CHECKING:  # pragma: no cover
    from jarvis.orchestration.mission import MissionDAG, MissionNode


class Neo4jGraph:
    """Persist graph entities to a Neo4j database."""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        driver: Optional[Driver] = None,
    ) -> None:
        if driver is not None:
            self.driver = driver
        else:
            uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = user or os.getenv("NEO4J_USER", "neo4j")
            password = password or os.getenv("NEO4J_PASSWORD", "test")
            self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    # ------------------------------------------------------------------
    def add_node(self, node_id: str, node_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Create or update a node in Neo4j."""

        props = attributes or {}
        with self.driver.session() as session:
            session.run(
                "MERGE (n:Node {id: $id}) SET n.type = $type, n += $props",
                id=node_id,
                type=node_type,
                props=props,
            )

    # ------------------------------------------------------------------
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create or update an edge in Neo4j."""

        props = attributes or {}
        rel = relationship_type.upper()
        with self.driver.session() as session:
            session.run(
                f"MATCH (a:Node {{id: $source}}), (b:Node {{id: $target}}) "
                f"MERGE (a)-[r:{rel}]->(b) SET r += $props",
                source=source_id,
                target=target_id,
                props=props,
            )

    # ------------------------------------------------------------------
    # Mission DAG operations
    def write_mission_dag(self, dag: "MissionDAG") -> None:
        """Persist an entire :class:`MissionDAG` to Neo4j."""

        with self.driver.session() as session:
            session.run(
                "MERGE (m:Mission {id: $mission_id}) SET m.rationale=$rationale",
                mission_id=dag.mission_id,
                rationale=dag.rationale,
            )
            for node in dag.nodes.values():
                session.run(
                    "MERGE (n:MissionNode {mission_id:$mission_id, step_id:$step_id}) "
                    "SET n.capability=$capability, n.team_scope=$team_scope, "
                    "n.hitl_gate=$hitl_gate, n.deps=$deps",
                    mission_id=dag.mission_id,
                    step_id=node.step_id,
                    capability=node.capability,
                    team_scope=node.team_scope,
                    hitl_gate=node.hitl_gate,
                    deps=node.deps,
                )
                session.run(
                    "MATCH (m:Mission {id:$mission_id}), (n:MissionNode {mission_id:$mission_id, step_id:$step_id}) "
                    "MERGE (m)-[:HAS_NODE]->(n)",
                    mission_id=dag.mission_id,
                    step_id=node.step_id,
                )
            for src, dst in dag.edges:
                session.run(
                    "MATCH (a:MissionNode {mission_id:$mission_id, step_id:$src}), "
                    "(b:MissionNode {mission_id:$mission_id, step_id:$dst}) "
                    "MERGE (a)-[:DEPENDS_ON]->(b)",
                    mission_id=dag.mission_id,
                    src=src,
                    dst=dst,
                )

    # ------------------------------------------------------------------
    def read_mission_dag(self, mission_id: str) -> "MissionDAG":
        """Load a :class:`MissionDAG` from Neo4j."""

        with self.driver.session() as session:
            rationale = ""
            result = session.run(
                "MATCH (m:Mission {id:$mission_id}) RETURN m.rationale AS rationale",
                mission_id=mission_id,
            )
            for record in result:
                rationale = record.get("rationale", "")

            node_records = session.run(
                "MATCH (n:MissionNode {mission_id:$mission_id}) "
                "RETURN n.step_id AS step_id, n.capability AS capability, "
                "n.team_scope AS team_scope, n.hitl_gate AS hitl_gate, n.deps AS deps",
                mission_id=mission_id,
            )
            from jarvis.orchestration.mission import MissionNode, MissionDAG

            nodes: Dict[str, MissionNode] = {}
            for rec in node_records:
                nodes[rec["step_id"]] = MissionNode(
                    step_id=rec["step_id"],
                    capability=rec["capability"],
                    team_scope=rec["team_scope"],
                    hitl_gate=rec.get("hitl_gate", False),
                    deps=rec.get("deps", []),
                )

            edge_records = session.run(
                "MATCH (a:MissionNode {mission_id:$mission_id})-[:DEPENDS_ON]->(b:MissionNode {mission_id:$mission_id}) "
                "RETURN a.step_id AS src, b.step_id AS dst",
                mission_id=mission_id,
            )
            edges = [(rec["src"], rec["dst"]) for rec in edge_records]

        return MissionDAG(mission_id=mission_id, nodes=nodes, edges=edges, rationale=rationale)
