import networkx as nx

from jarvis.world_model.knowledge_graph import KnowledgeGraph


def test_knowledge_graph_uses_networkx():
    kg = KnowledgeGraph()
    assert isinstance(kg.graph, nx.DiGraph)
    kg.add_node("a", "entity")
    kg.add_node("b", "entity")
    kg.add_edge("a", "b", "rel")
    assert ("a", "b") in kg.graph.edges()
