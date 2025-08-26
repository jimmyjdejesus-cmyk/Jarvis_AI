"""Monte Carlo Tree Search based planner for toolchains."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Dict, Any


@dataclass
class _Node:
    """Node used in the MCTS search tree."""

    toolchain: List[str]
    parent: Optional["_Node"] = None
    children: List["_Node"] = field(default_factory=list)
    untried_tools: List[str] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0  # Sum of simulation rewards

    def is_fully_expanded(self) -> bool:
        return not self.untried_tools

    def select_child(self, exploration: float) -> "_Node":
        """Select a child node using the UCB1 formula."""
        assert self.children, "No children to select from"
        log_total_visits = math.log(self.visits)

        return max(
            self.children,
            key=lambda c: (c.value / c.visits) + exploration * math.sqrt(log_total_visits / c.visits),
        )

    def best_child(self) -> "_Node":
        """Select the child with the highest number of visits (most robust path)."""
        if not self.children:
            return self
        return max(self.children, key=lambda c: c.visits)

    def update(self, reward: float) -> None:
        self.visits += 1
        self.value += reward


class MCTSPlanner:
    """Plan toolchains using Monte Carlo Tree Search."""

    def __init__(
        self,
        mcp_client: Any,
        available_tools: List[str],
        iterations: int = 100,
        exploration_weight: float = 1.4,
    ) -> None:
        self.mcp_client = mcp_client
        self.available_tools = available_tools
        self.iterations = iterations
        self.exploration_weight = exploration_weight
        self.tree_root: Optional[_Node] = None

    async def _simulate(self, toolchain: List[str], goal: str) -> float:
        """
        Simulate the utility of a toolchain by asking an LLM to rate it.
        Returns a score between 0.0 and 1.0.
        """
        if not toolchain:
            return 0.0

        prompt = f"""
Given a goal and a sequence of tools (a toolchain), rate how effective this toolchain would be for accomplishing the goal.
Respond with a single integer score from 1 (not effective at all) to 10 (perfectly effective).

**Goal:** "{goal}"
**Toolchain:** {', '.join(toolchain)}

**Your Rating (1-10):**
"""
        try:
            response = await self.mcp_client.generate_response("ollama", "llama3.2", prompt)
            score = int(response.strip())
            return max(0.0, min(10.0, float(score))) / 10.0  # Normalize to 0-1
        except (ValueError, TypeError):
            return 0.1  # Default low score on parsing failure

    def build_tree(self, goal: str):
        """Build the MCTS search tree for a given goal."""
        self.tree_root = _Node(toolchain=[], untried_tools=list(self.available_tools))

        for _ in range(self.iterations):
            node = self.tree_root

            # 1. Selection: Traverse the tree to find a leaf or expandable node
            while node.is_fully_expanded() and node.children:
                node = node.select_child(self.exploration_weight)

            # 2. Expansion: If the node is not fully expanded, create a new child
            if not node.is_fully_expanded():
                tool = node.untried_tools.pop(0)
                new_toolchain = node.toolchain + [tool]

                # Prevent using the same tool twice in a row
                remaining_tools = [t for t in self.available_tools if t != tool]

                child = _Node(
                    toolchain=new_toolchain,
                    parent=node,
                    untried_tools=remaining_tools,
                )
                node.children.append(child)
                node = child

            # 3. Simulation: Estimate the value of the new node's state
            # In a real scenario, this would be an async call.
            # For simplicity in this structure, we'll assume the mcp_client can be called synchronously
            # or this whole loop is run in an async context.
            # Let's assume the caller will handle the async loop.
            # **NOTE**: For the test, we'll need an async runner.
            reward = asyncio.run(self._simulate(node.toolchain, goal))

            # 4. Backpropagation: Update the value and visit counts up the tree
            while node:
                node.update(reward)
                node = node.parent

    async def build_tree_async(self, goal: str):
        """Asynchronously build the MCTS search tree for a given goal."""
        self.tree_root = _Node(toolchain=[], untried_tools=list(self.available_tools))

        for _ in range(self.iterations):
            node = self.tree_root

            while node.is_fully_expanded() and node.children:
                node = node.select_child(self.exploration_weight)

            if not node.is_fully_expanded():
                tool = node.untried_tools.pop(0)
                new_toolchain = node.toolchain + [tool]
                remaining_tools = [t for t in self.available_tools if t != tool]

                child = _Node(
                    toolchain=new_toolchain,
                    parent=node,
                    untried_tools=remaining_tools,
                )
                node.children.append(child)
                node = child

            reward = await self._simulate(node.toolchain, goal)

            while node:
                node.update(reward)
                node = node.parent

    async def find_best_toolchain(self, goal: str) -> List[str]:
        """
        Builds the search tree and finds the best toolchain for the given goal.
        """
        await self.build_tree_async(goal)

        if not self.tree_root:
            return []

        best_node = self.tree_root
        path = []
        while best_node.children:
            best_node = best_node.best_child()
            # The toolchain is cumulative, we want the final one.
            path = best_node.toolchain

        return path
