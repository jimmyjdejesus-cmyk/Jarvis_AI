import os
from typing import Dict, List, Any

import yaml

from .task_queue import RedisTaskQueue


class MissionPlanner:
    """Load mission definitions and enqueue their tasks for execution."""

    def __init__(self, missions_dir: str, queue: RedisTaskQueue | None = None) -> None:
        self.missions_dir = missions_dir
        self.queue = queue or RedisTaskQueue()

    def _mission_path(self, name: str) -> str:
        return os.path.join(self.missions_dir, f"{name}.yaml")

    def load_mission(self, name: str) -> Dict[str, Any]:
        """Load a mission definition from disk."""
        path = self._mission_path(name)
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def plan(self, name: str) -> List[Dict[str, Any]]:
        """Break the mission into sub-tasks and enqueue them.

        Returns the list of tasks that were enqueued.
        """
        mission = self.load_mission(name)
        tasks = mission.get("tasks", [])
        for task in tasks:
            self.queue.enqueue(task)
        return tasks
