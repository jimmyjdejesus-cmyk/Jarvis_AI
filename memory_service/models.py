# memory_service/models.py
"""
Pydantic models for the data structures used in the Memory Service.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import time

class Node(BaseModel):
    """Represents a single entity or vertex in the hypergraph."""
    id: str = Field(default_factory=lambda: f"node:{uuid.uuid4()}")
    node_type: str = "generic"
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def to_redis(self) -> Dict[str, str]:
        """Serialize model to a dictionary for Redis HSET."""
        data = self.model_dump(exclude={"properties"})
        # Flatten properties into the main dictionary
        for key, value in self.properties.items():
            data[f"prop:{key}"] = str(value)
        return {k: str(v) for k, v in data.items()}

class Metrics(BaseModel):
    """Represents metrics associated with a path or operation."""
    novelty: float = 0.0
    growth: float = 0.0
    cost: float = 0.0

class NegativeCheck(BaseModel):
    """Represents a check for negative path memory."""
    actor: str
    target: str
    signature: "PathSignature"
    threshold: float

class Outcome(BaseModel):
    """Represents the outcome of a path."""
    result: str
    oracle_score: float

class PathSignature(BaseModel):
    """Represents the signature of a path for similarity comparison."""
    steps: List[str]
    tools_used: List[str]
    key_decisions: List[str]
    embedding: List[float]
    metrics: Metrics
    outcome: Outcome
    scope: str

class PathRecord(BaseModel):
    """Represents a recorded path or trajectory of execution."""
    actor: str
    target: str
    signature: PathSignature

class Hyperedge(BaseModel):
    """Represents a connection between multiple nodes."""
    id: str = Field(default_factory=lambda: f"edge:{uuid.uuid4()}")
    edge_type: str = "generic"
    node_ids: List[str]
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

    def to_redis(self) -> Dict[str, str]:
        """Serialize model to a dictionary for Redis HSET."""
        data = self.model_dump(exclude={"properties", "node_ids"})
        # Flatten properties
        for key, value in self.properties.items():
            data[f"prop:{key}"] = str(value)
        return {k: str(v) for k, v in data.items()}
