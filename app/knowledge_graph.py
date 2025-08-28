"""In-memory knowledge graph service for FastAPI endpoints."""

from __future__ import annotations


class KnowledgeGraph:
    """Simple in-memory knowledge graph service."""

    def __init__(self) -> None:
        self._store = {"nodes": ["n1"]}

    def query(self, q: str) -> list[str]:
        """Return results for a supported query or raise ValueError."""
        if q not in self._store:
            raise ValueError("Unsupported query")
        return self._store[q]


knowledge_graph = KnowledgeGraph()
