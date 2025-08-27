# memory_service/config.py
"""
Configuration for the Memory Service, particularly Redis connection settings.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis key expiration in seconds (0 disables TTL)
MEMORY_TTL = int(os.getenv("MEMORY_TTL", "0"))

# Prefix for all keys in the memory service to avoid collisions
KEY_PREFIX = "jarvis:memory"

# Qdrant configuration for the vector store
QDRANT_URL = os.getenv("QDRANT_URL", ":memory:")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "jarvis_vectors")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "8"))

# Maximum number of vector entries to retain per (principal, scope)
MAX_VECTOR_ENTRIES = int(os.getenv("MAX_VECTOR_ENTRIES", "1000"))
