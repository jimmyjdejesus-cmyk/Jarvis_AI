# memory_service/hypergraph.py
"""
Core hypergraph logic using Redis as a backend.
Manages nodes, hyperedges, and their connections.
"""

import redis
from .config import REDIS_HOST, REDIS_PORT, REDIS_DB, KEY_PREFIX
from .models import Node, Hyperedge
from typing import Optional, List, Dict, Any

class Hypergraph:
    """A Redis-backed hypergraph implementation."""

    def __init__(self, scope: str = "global"):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        self.scope = scope

    def _get_key(self, *parts: str) -> str:
        """Construct a Redis key with the service and scope prefix."""
        return f"{KEY_PREFIX}:{self.scope}:{':'.join(parts)}"

    def add_node(self, node: Node) -> str:
        """Add a node to the hypergraph."""
        node_key = self._get_key("node", node.id)
        self.redis.hset(node_key, mapping=node.to_redis())
        return node.id

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by its ID."""
        node_key = self._get_key("node", node_id)
        data = self.redis.hgetall(node_key)
        if not data:
            return None

        # Separate properties from main fields
        properties = {k.replace("prop:", ""): v for k, v in data.items() if k.startswith("prop:")}
        main_data = {k: v for k, v in data.items() if not k.startswith("prop:")}
        main_data["properties"] = properties

        return Node.model_validate(main_data)

    def add_hyperedge(self, edge: Hyperedge) -> str:
        """Add a hyperedge, connecting multiple nodes."""
        edge_key = self._get_key("edge", edge.id)

        # Store edge properties
        self.redis.hset(edge_key, mapping=edge.to_redis())

        # Store the set of nodes in this edge
        nodes_key = self._get_key("edge_nodes", edge.id)
        self.redis.sadd(nodes_key, *edge.node_ids)

        # Link each node to this edge
        for node_id in edge.node_ids:
            node_edges_key = self._get_key("node_edges", node_id)
            self.redis.sadd(node_edges_key, edge.id)

        return edge.id

    def get_nodes_in_hyperedge(self, edge_id: str) -> List[str]:
        """Get all node IDs connected by a hyperedge."""
        nodes_key = self._get_key("edge_nodes", edge_id)
        return list(self.redis.smembers(nodes_key))

    def get_hyperedges_for_node(self, node_id: str) -> List[str]:
        """Get all hyperedge IDs that a node belongs to."""
        node_edges_key = self._get_key("node_edges", node_id)
        return list(self.redis.smembers(node_edges_key))

    def set_scope(self, scope: str):
        """Change the active scope for memory operations."""
        self.scope = scope

    def get_scope(self) -> str:
        """Get the current active scope."""
        return self.scope
