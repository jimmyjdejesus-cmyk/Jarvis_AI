import json
from typing import Any, Dict, Optional

import redis


class RedisTaskQueue:
    """A simple Redis-backed FIFO queue for mission tasks."""

    def __init__(
        self,
        name: str = "mission_tasks",
        redis_client: Optional[redis.Redis] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
    ) -> None:
        """Initialize the queue.

        Parameters
        ----------
        name: str
            Name of the Redis list.
        redis_client: Optional[redis.Redis]
            Preconfigured Redis client (used mainly for testing).
        host, port, db: connection parameters when ``redis_client`` is ``None``.
        """
        if redis_client is None:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        else:
            self.redis = redis_client
        self.name = name

    def enqueue(self, task: Dict[str, Any]) -> None:
        """Add a task to the queue."""
        try:
            self.redis.rpush(self.name, json.dumps(task))
        except redis.RedisError as exc:  # pragma: no cover - network failure
            raise RuntimeError("Failed to enqueue task") from exc

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieve the next task from the queue."""
        try:
            data = self.redis.lpop(self.name)
        except redis.RedisError as exc:  # pragma: no cover - network failure
            raise RuntimeError("Failed to dequeue task") from exc
        return json.loads(data) if data else None

    def length(self) -> int:
        """Return the number of tasks pending in the queue."""
        return int(self.redis.llen(self.name))
