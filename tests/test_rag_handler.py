import pytest

from agent.features.rag_handler import RAGHandler
from memory_service import vector_store
from jarvis.retrieval.self_rag_gate import SelfRAGGate


def test_index_and_search():
    handler = RAGHandler(gate=SelfRAGGate(enabled=True))
    principal, scope, key = "tester", "unit", "doc1"
    text = "Jarvis uses retrieval augmented generation"
    handler.index_document(principal, scope, key, text)

    try:
        results = handler.semantic_search("retrieval")
        assert any(text in doc for doc in results)
    finally:
        vector_store.delete_text(principal, scope, key)


def test_search_blocked_by_gate():
    gate = SelfRAGGate(enabled=False)
    handler = RAGHandler(gate=gate)
    principal, scope, key = "tester", "unit", "doc2"
    text = "Semantic search should be blocked"
    handler.index_document(principal, scope, key, text)

    try:
        results = handler.semantic_search("semantic")
        assert results == []
    finally:
        vector_store.delete_text(principal, scope, key)
