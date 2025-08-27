"""
Main entry point for the Memory Service module.
Provides access to the core MemoryService client and other sub-modules.
"""

from .models import Metrics, NegativeCheck, Outcome, PathRecord, PathSignature
from .client import MemoryService
from .vector_store import VectorStore

# Shared vector store instance
vector_store = VectorStore()

# Placeholders for path memory functions
def avoid_negative(check: NegativeCheck):
    """Placeholder for checking negative path memory."""
    print(f"INFO: Negative path check is not yet implemented. Check: {check}")
    return {"avoid": False, "results": []}

def record_path(path: PathRecord):
    """Placeholder for recording a new path."""
    print(f"INFO: Path recording is not yet implemented. Path: {path}")
    pass

def get_path_details(path_id):
    """Placeholder for getting path details."""
    print(f"INFO: Path detail retrieval is not yet implemented. Path ID: {path_id}")
    return None

def update_path_feedback(path_id, feedback):
    """Placeholder for updating path feedback."""
    print(f"INFO: Path feedback update is not yet implemented. Path ID: {path_id}, Feedback: {feedback}")
    pass

def get_path_memory_summary():
    """Placeholder for getting a summary of path memory."""
    print("INFO: Path memory summary is not yet implemented.")
    return {}

__all__ = [
    "MemoryService",
    "vector_store",
    "Metrics",
    "NegativeCheck",
    "Outcome",
    "PathRecord",
    "PathSignature",
    "avoid_negative",
    "record_path",
    "get_path_details",
    "update_path_feedback",
    "get_path_memory_summary",
]
