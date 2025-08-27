"""Lightweight Neo4j adapter mirroring :class:`KnowledgeGraph` API."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
import re

from neo4j import GraphDatabase, Driver


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
    def add_node(
        self,
        node_id: str,
        node_type: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
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
                (
                    "MATCH (a:Node {id: $source}), "
                    "(b:Node {id: $target}) "
                    f"MERGE (a)-[r:{rel}]->(b) SET r += $props"
                ),
                source=source_id,
                target=target_id,
                props=props,
            )

    # ------------------------------------------------------------------
    _READ_ONLY_START = re.compile(
        r"^\s*(MATCH|RETURN)\b",
        re.IGNORECASE,
    )
    _WRITE_CLAUSES = re.compile(
        r"\b(CREATE|MERGE|DELETE|SET|DROP)\b",
        re.IGNORECASE,
    )

    def _validate_cypher(self, query: str) -> None:
        """Ensure ``query`` is read-only and contains a single statement.

        Parameters
        ----------
        query:
            Cypher statement to validate.

        Raises
        ------
        ValueError
            If the query performs write operations or contains multiple
            statements.
        """

        if ";" in query:
            raise ValueError("Multiple Cypher statements are not allowed")

        if not self._READ_ONLY_START.match(query):
            raise ValueError("Query must start with MATCH or RETURN")

        if self._WRITE_CLAUSES.search(query):
            raise ValueError("Write operations are not permitted")

    # ------------------------------------------------------------------
    def query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """Execute a validated read-only Cypher query.

        Parameters
        ----------
        query:
            Cypher statement restricted to read-only operations.
        parameters:
            Optional mapping of query parameters.

        Returns
        -------
        list[Dict[str, Any]]
            Result rows represented as dictionaries.

        Raises
        ------
        ValueError
            If the query fails validation.
        """

        self._validate_cypher(query)
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
