"""Retrieval-Augmented Generation handler.

Provides simple document indexing and semantic search capabilities using the
project's vector store. Retrieved documents can be used to inject additional
context into conversations.
"""

from __future__ import annotations

from typing import List

from memory_service import vector_store
from jarvis.retrieval.self_rag_gate import SelfRAGGate


class RAGHandler:
    """Handle document indexing and semantic search.

    Parameters
    ----------
    gate:
        Optional :class:`SelfRAGGate` instance used to determine whether
        retrieved context should be used. If not provided, a default gate with
        permissive settings is created.
    """

    def __init__(self, gate: SelfRAGGate | None = None) -> None:
        self.gate = gate or SelfRAGGate(enabled=True)

    def index_document(self, principal: str, scope: str, key: str, text: str) -> None:
        """Index ``text`` in the shared vector store."""

        vector_store.add_text(principal, scope, key, text)

    def semantic_search(self, query: str, n_results: int = 5) -> List[str]:
        """Search for documents semantically similar to ``query``.

        Parameters
        ----------
        query:
            The natural language query string.
        n_results:
            Maximum number of results to return.

        Returns
        -------
        list of str
            Retrieved documents. The list may be empty if the gate blocks
            retrieval or no documents are found.
        """

        results = vector_store.query_text(query, n_results)
        docs = results.get("documents", [[]])[0]
        structured = [{"relevant": True} for _ in docs]

        if not self.gate.should_retrieve(query, structured):
            return []
        return docs

    def build_context(self, query: str, n_results: int = 5) -> str:
        """Return a newline-delimited context string for ``query``."""

        docs = self.semantic_search(query, n_results)
        return "\n".join(docs)


__all__ = ["RAGHandler"]
