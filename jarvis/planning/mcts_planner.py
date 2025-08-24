"""Monte Carlo Tree Search based mission planner."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from jarvis.models.client import model_client


@dataclass
class _Node:
    """Node used in the MCTS search tree."""

    tasks: List[str]
    parent: Optional["_Node"] = None
    children: List["_Node"] = field(default_factory=list)
    untried_actions: List[str] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0

    def is_terminal(self) -> bool:
        return not self.untried_actions and not self.children

    def is_fully_expanded(self) -> bool:
        return not self.untried_actions

    def select_child(self, exploration: float) -> "_Node":
        assert self.children, "No children to select from"
        log_total = math.log(self.visits)
        return max(
            self.children,
            key=lambda c: (c.value / c.visits) + exploration * math.sqrt(log_total / c.visits),
        )

    def best_child(self) -> "_Node":
        return max(self.children, key=lambda c: c.visits)

    def update(self, reward: float) -> None:
        self.visits += 1
        self.value += reward


class MCTSPlanner:
    """Plan missions using Monte Carlo Tree Search."""

    def __init__(
        self,
        client=model_client,
        model: str = "llama3.2",
        iterations: int = 50,
        exploration_weight: float = 1.4,
    ) -> None:
        self.client = client
        self.model = model
        self.iterations = iterations
        self.exploration_weight = exploration_weight

    def _expand_state(self, goal: str, tasks: Sequence[str]) -> List[str]:
        prompt = (
            "You are an expert mission planner. Given the goal: "
            f"'{goal}' and completed tasks: {list(tasks)}, provide the next steps "
            "as a numbered list. If the mission is complete, return an empty response."
        )
        response = self.client.generate_response(self.model, prompt)
        actions: List[str] = []
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit():
                parts = line.split(".", 1)
                action = parts[1].strip() if len(parts) == 2 else line
            else:
                action = line
            if action:
                actions.append(action)
        return actions

    def plan(self, goal: str) -> List[str]:
        """Compute a plan for the given goal."""
        root = _Node(tasks=[], untried_actions=self._expand_state(goal, []))
        target_length = len(root.untried_actions)

        for _ in range(self.iterations):
            node = root
            # Selection
            while node.is_fully_expanded() and node.children:
                node = node.select_child(self.exploration_weight)
            # Expansion
            if node.untried_actions:
                action = node.untried_actions.pop(0)
                new_tasks = node.tasks + [action]
                child = _Node(
                    tasks=new_tasks,
                    parent=node,
                    untried_actions=self._expand_state(goal, new_tasks),
                )
                node.children.append(child)
                node = child
            # Simulation (1 if terminal else 0)
            reward = 1.0 if node.is_terminal() and len(node.tasks) == target_length else 0.0
            # Backpropagation
            while node:
                node.update(reward)
                node = node.parent

        best = root
        plan: List[str] = []
        while best.children:
            best = best.best_child()
            plan = best.tasks
        return plan
