# memory_service/config.py
"""
Configuration for the Memory Service, particularly Redis connection settings.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Prefix for all keys in the memory service to avoid collisions
KEY_PREFIX = "jarvis:memory"
