"""Legacy knowledge graph shim for tests.

This file provides a lightweight `knowledge_graph` object used by legacy
`legacy/app/main.py` for test import-time resolution. It does not implement
the full functionality of the legacy knowledge graph, but exposes the
`knowledge_graph` variable and minimal method stubs used by the app/tests.
"""
from __future__ import annotations

class DummyKnowledgeGraph:
    def __init__(self):
        self.nodes = []

    def add(self, item):
        self.nodes.append(item)

    def search(self, query):
        return []


knowledge_graph = DummyKnowledgeGraph()
