"""Project-scoped memory stored as a layered hypergraph.

The memory system organises information into *namespaces* composed of a
``project``, ``session`` and ``team``. Each namespace owns a directed graph
whose nodes represent memory entries. Nodes are tagged with a layer
describing their type (facts, strategies, beliefs or constitutional rules)
and provenance in the form of ``run_id`` and ``mission_id``. Edges connect
related entries, providing a lightweight hypergraph suitable for retrieval
and reasoning tasks.

This graph underpins future GraphRAG and REX-RAG components where community
summaries, neighbourhood traversal and code-aware retrieval rely on these
structured relationships.

All content is sanitised before storage to avoid injection of malicious graph
data, and a pluggable persistence backend allows the hypergraph to be saved
and restored across process restarts.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import networkx as nx
import bleach

# Layer constants
L1_FACT = "fact"
L2_STRATEGY = "strategy"
L3_BELIEF = "belief"
L4_CONSTITUTION = "constitutional"

# Allowed layers for validation
_VALID_LAYERS = {L1_FACT, L2_STRATEGY, L3_BELIEF, L4_CONSTITUTION}


@dataclass(frozen=True)
class Namespace:
    """Namespace identifiers for project memory.

    Attributes
    ----------
    project:
        Project identifier.
    session:
        Session identifier.
    team:
        Team identifier.
    """

    project: str
    session: str
    team: str


class MemoryBackend(ABC):
    """Persistence backend interface for :class:`ProjectMemory`."""

    @abstractmethod
    def load(self) -> Dict[Tuple[str, str, str], nx.DiGraph]:
        """Return graphs previously saved to the backend."""

    @abstractmethod
    def save(self, graphs: Dict[Tuple[str, str, str], nx.DiGraph]) -> None:
        """Persist ``graphs`` to the backend."""


class JSONFileBackend(MemoryBackend):
    """Persist graphs as node-link JSON on disk."""

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> Dict[Tuple[str, str, str], nx.DiGraph]:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except FileNotFoundError:
            return {}

        graphs: Dict[Tuple[str, str, str], nx.DiGraph] = {}
        for key, data in raw.items():
            graphs[tuple(key.split(":"))] = nx.node_link_graph(
                data, directed=True, multigraph=False, links="links"
            )
        return graphs

    def save(self, graphs: Dict[Tuple[str, str, str], nx.DiGraph]) -> None:
        raw: Dict[str, Dict[str, object]] = {}
        for key, graph in graphs.items():
            raw[":".join(key)] = nx.node_link_data(graph, edges="links")
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(raw, fh)


class ProjectMemory:
    """Store and relate memories across project namespaces.

    Each namespace maintains a directed graph where nodes represent memory
    entries annotated with their layer and provenance (``run_id`` and
    ``mission_id``). Edges connect related entries, enabling a simple
    hypergraph structure. Graphs are stored in memory; applications needing
    persistence or distribution may supply a :class:`MemoryBackend` to persist
    data.
    """

    def __init__(self, backend: Optional[MemoryBackend] = None) -> None:
        self._backend = backend
        if backend:
            self._graphs = backend.load()
        else:
            self._graphs: Dict[Tuple[str, str, str], nx.DiGraph] = {}

    def _persist(self) -> None:
        if self._backend:
            self._backend.save(self._graphs)

    def _sanitize(self, text: str) -> str:
        """Sanitise input using :mod:`bleach`."""
        return bleach.clean(str(text), strip=True)

    def _key(self, ns: Namespace) -> Tuple[str, str, str]:
        return (ns.project, ns.session, ns.team)

    def add_entry(
        self,
        ns: Namespace,
        layer: str,
        content: str,
        run_id: str,
        mission_id: str,
        links: Optional[List[str]] = None,
    ) -> str:
        """Add a memory entry to ``ns`` and return its node identifier.

        Parameters
        ----------
        ns:
            Namespace identifying the project, session and team.
        layer:
            One of :data:`L1_FACT`, :data:`L2_STRATEGY`, :data:`L3_BELIEF` or
            :data:`L4_CONSTITUTION`.
        content:
            Textual content for the memory entry. Content is sanitised before
            storage.
        run_id, mission_id:
            Provenance identifiers for the run and mission generating the
            memory.
        links:
            Optional list of existing node identifiers to which this entry
            should link. Missing nodes are ignored.
        """
        if layer not in _VALID_LAYERS:
            raise ValueError(f"Invalid layer: {layer}")
        if not run_id or not mission_id:
            raise ValueError("run_id and mission_id are required")

        graph = self._graphs.setdefault(self._key(ns), nx.DiGraph())
        node_id = str(uuid4())
        graph.add_node(
            node_id,
            layer=layer,
            content=self._sanitize(content),
            run_id=run_id,
            mission_id=mission_id,
        )
        if links:
            for target in links:
                if graph.has_node(target):
                    graph.add_edge(node_id, target)
        self._persist()
        return node_id

    def get_graph(self, ns: Namespace) -> nx.DiGraph:
        """Return the graph for ``ns`` (creating if necessary)."""
        return self._graphs.setdefault(self._key(ns), nx.DiGraph())


__all__ = [
    "ProjectMemory",
    "Namespace",
    "MemoryBackend",
    "JSONFileBackend",
    "L1_FACT",
    "L2_STRATEGY",
    "L3_BELIEF",
    "L4_CONSTITUTION",
]