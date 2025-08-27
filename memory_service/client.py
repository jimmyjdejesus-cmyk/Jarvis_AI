# memory_service/client.py
"""
The main client for interacting with the Memory Service.
Provides a high-level API for memory operations.
"""

from .hypergraph import Hypergraph
from .models import Node, Hyperedge
from typing import Optional, List, Dict, Any

class MemoryService:
    """A client for managing scoped agent memory in a hypergraph."""

    def __init__(self, scope: str = "global"):
        """Initialize the memory service with a default scope."""
        self.hypergraph = Hypergraph(scope)

    def set_scope(self, scope: str):
        """Set the active memory scope (e.g., for a specific agent)."""
        self.hypergraph.set_scope(scope)
        print(f"Memory scope set to: {scope}")

    def add_node(self, node_type: str, properties: Dict[str, Any] = None) -> str:
        """Create and add a new node to the current scope."""
        if not properties:
            properties = {}
        node = Node(node_type=node_type, properties=properties)
        return self.hypergraph.add_node(node)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by its ID from the current scope."""
        return self.hypergraph.get_node(node_id)

    def add_hyperedge(self, node_ids: List[str], edge_type: str, properties: Dict[str, Any] = None) -> str:
        """Create a hyperedge to connect multiple nodes in the current scope."""
        if not properties:
            properties = {}
        edge = Hyperedge(node_ids=node_ids, edge_type=edge_type, properties=properties)
        return self.hypergraph.add_hyperedge(edge)

    def get_neighbors(self, node_id: str) -> List[Node]:
        """Find all direct neighbors of a node (nodes sharing a hyperedge)."""
        edge_ids = self.hypergraph.get_hyperedges_for_node(node_id)
        neighbor_ids = set()

        for edge_id in edge_ids:
            nodes_in_edge = self.hypergraph.get_nodes_in_hyperedge(edge_id)
            for nid in nodes_in_edge:
                if nid != node_id:
                    neighbor_ids.add(nid)

        # Fetch node objects and filter out any that might have been deleted
        neighbors = [self.get_node(nid) for nid in neighbor_ids]
        return [n for n in neighbors if n is not None]

    def find_nodes_by_type(self, node_type: str) -> List[Node]:
        """(Advanced) A placeholder for finding nodes by type.
        This would require an indexing strategy in a real implementation.
        """
        print(f"WARNING: find_nodes_by_type is not yet implemented efficiently.")
        return []

    def find_edges_by_type(self, edge_type: str) -> List[Hyperedge]:
        """(Advanced) A placeholder for finding edges by type."""
        print(f"WARNING: find_edges_by_type is not yet implemented efficiently.")
        return []
