from __future__ import annotations

"""Persistent hierarchical hypergraph backed by Neo4j with in-memory
fallback."""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import re
import time
from neo4j import GraphDatabase

from jarvis.security.secret_manager import get_secret


class HierarchicalHypergraph:
    """Persistent multi-layer hypergraph backed by Neo4j when available."""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Initialize the hypergraph.

        Parameters
        ----------
        uri, user, password:
            Optional overrides for Neo4j connection settings. When omitted,
            values are loaded from the OS keyring via ``keyring`` using the
            service name ``jarvis``. If none are supplied the hypergraph runs
            in in-memory mode.
        """

        uri = uri or get_secret("NEO4J_URI")
        user = user or get_secret("NEO4J_USER")
        password = password or get_secret("NEO4J_PASSWORD")
        if uri and user and password:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.layers = None
        else:
            self.driver = None
            self.layers = {1: {}, 2: {}, 3: {}}  # type: ignore[assignment]

    def load_from_json(self, path: str | Path) -> None:
        """Populate layers from a JSON file.

        Parameters
        ----------
        path:
            Location of the JSON file containing layer data.
        """

        with open(Path(path), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if self.driver:
            for key, node in data.get("layer1_concrete", {}).items():
                self.update_node(1, key, node)
            for key, node in data.get("layer2_abstract", {}).items():
                self.update_node(2, key, node)
            for key, node in data.get("layer3_causal", {}).items():
                self.update_node(3, key, node)
        else:
            self.layers[1] = data.get("layer1_concrete", {})
            self.layers[2] = data.get("layer2_abstract", {})
            self.layers[3] = data.get("layer3_causal", {})

    def query(self, layer: int, node: str) -> Optional[Dict[str, Any]]:
        """Retrieve a node from a specific layer.

        Parameters
        ----------
        layer:
            Graph layer to search.
        node:
            Node identifier.

        Returns
        -------
        Optional[Dict[str, Any]]
            Node properties if found; otherwise ``None``.
        """
        if self.driver:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (n {layer: $layer, key: $key}) RETURN n",
                    layer=layer,
                    key=node,
                )
                record = result.single()
                return dict(record["n"]) if record else None
        return self.layers.get(layer, {}).get(node)

    # ------------------------------------------------------------------
    def add_causal_belief(
        self, intervention: str, result: str, confidence: float
    ) -> str:
        """Record a causal belief in Layer 3.

        Parameters
        ----------
        intervention:
            The intervention or action taken.
        result:
            The resulting outcome observed.
        confidence:
            Confidence score between 0 and 1.

        Returns
        -------
        str
            The key used to store the belief.
        """

        key = f"{intervention}->{result}"
        data = {
            "intervention": intervention,
            "result": result,
            "confidence": confidence,
        }
        self.update_node(3, key, data)
        return key

    def add_strategy(
        self,
        steps: List[str],
        confidence: float,
        dependencies: List[str] | None = None,
    ) -> str:
        """Create a strategy node in Layer 2 from reasoning steps.

        Parameters
        ----------
        steps:
            Ordered list of reasoning steps.
        confidence:
            Confidence score between 0 and 1.
        dependencies:
            Optional list of prerequisite strategy keys.

        Returns
        -------
        str
            Generated key for the new strategy node.
        """
        key = (
            f"strategy_{len(self.layers.get(2, {})) + 1}"
            if not self.driver
            else f"strategy_{int(time.time()*1000)}"
        )
        data = {"steps": steps, "confidence": confidence}
        if dependencies:
            data["dependencies"] = dependencies
        self.update_node(2, key, data)
        return key

    def add_negative_pathway(
        self, strategy_key: str, root_cause: Dict[str, Any]
    ) -> str:
        """Record a negative pathway node linked to a failed strategy.

        Parameters
        ----------
        strategy_key:
            Identifier of the strategy that failed.
        root_cause:
            Details describing the failure.

        Returns
        -------
        str
            Key for the negative pathway node.
        """
        key = f"{strategy_key}_neg"
        data = {
            "strategy": strategy_key,
            "root_cause": root_cause,
            "type": "negative_pathway",
            "confidence": 0.0,
        }
        self.update_node(2, key, data)
        return key

    def get_low_confidence_nodes(
        self, threshold: float
    ) -> List[Tuple[int, str, Dict[str, Any]]]:
        """Return nodes across layers with confidence below ``threshold``.

        Parameters
        ----------
        threshold:
            Confidence cutoff. Nodes with confidence less than this value are
            returned.

        Returns
        -------
        List[Tuple[int, str, Dict[str, Any]]]
            Tuples containing layer, node key and node data.
        """
        if self.driver:
            with self.driver.session() as session:
                result = session.run(
                    (
                        "MATCH (n) WHERE n.confidence < $th "
                        "RETURN n.layer AS layer, n.key AS key, n"
                    ),
                    th=threshold,
                )
                return [
                    (record["layer"], record["key"], dict(record["n"]))
                    for record in result
                ]
        low: List[Tuple[int, str, Dict[str, Any]]] = []
        for layer, nodes in self.layers.items():
            for key, data in nodes.items():
                if data.get("confidence", 1.0) < threshold:
                    low.append((layer, key, data))
        return low

    def update_node(self, layer: int, key: str, data: Dict[str, Any]) -> None:
        """Insert or update a node in the hypergraph.

        Parameters
        ----------
        layer:
            Graph layer in which to store the node.
        key:
            Node identifier unique within ``layer``.
        data:
            Properties to associate with the node. When persisting to Neo4j,
            property names must match ``[A-Za-z_][A-Za-z0-9_]*``.

        Raises
        ------
        ValueError
            If any property name fails validation when using Neo4j storage.
        """

        data = {**data, "layer": layer, "key": key}
        if self.driver:
            for k in data.keys():
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k):
                    raise ValueError(f"Invalid property name: {k}")
            set_clause = ", ".join([f"n.{k} = ${k}" for k in data])
            with self.driver.session() as session:
                session.run(
                    f"MERGE (n {{layer: $layer, key: $key}}) SET {set_clause}",
                    **data,
                )
        else:
            self.layers.setdefault(layer, {}).setdefault(key, {}).update(data)


__all__ = ["HierarchicalHypergraph"]
