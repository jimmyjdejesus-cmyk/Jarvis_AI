"""Mission Planner - Breaks high-level goals into tasks using LLM."""

from __future__ import annotations

import logging
from typing import List, Dict

from jarvis.models.client import model_client

logger = logging.getLogger(__name__)


class MissionPlanner:
    """Plan missions by decomposing goals into executable tasks."""

    def __init__(self, client=model_client, model: str = "llama3.2"):
        self.client = client
        self.model = model

    def plan(self, goal: str) -> List[str]:
        """Break a high-level goal into tasks using the LLM.

        Args:
            goal: The mission goal to decompose.

        Returns:
            List of task descriptions.
        """
        prompt = (
            "You are an expert mission planner. Break the following goal into a "
            "numbered list of concise tasks.\nGoal: " + goal
        )
        try:
            response = self.client.generate_response(self.model, prompt)
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Mission planning failed: %s", exc)
            return []

        tasks = []
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit():
                # strip leading number and punctuation
                parts = line.split(".", 1)
                if len(parts) == 2:
                    task = parts[1].strip()
                else:
                    task = line
            else:
                task = line
            if task:
                tasks.append(task)
        logger.debug("Planned tasks: %s", tasks)
        return tasks

    def to_graph(self, tasks: List[str]) -> Dict[str, Any]:
        """Create a simple sequential LangGraph definition from tasks."""
        nodes = {
            f"task_{i+1}": {"description": task}
            for i, task in enumerate(tasks)
        }
        edges = [
            (f"task_{i}", f"task_{i+1}")
            for i in range(1, len(tasks))
        ]
        return {"nodes": nodes, "edges": edges}

