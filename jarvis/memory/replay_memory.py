"""Replay memory utilities for storing agent experiences."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
from typing import Any, Deque, Iterable, List, Tuple
import random

from .memory_bus import MemoryBus


@dataclass
class Experience:
    """Container for a single agent-environment interaction."""
    state: Any
    action: Any
    reward: float
    next_state: Any
    done: bool
    priority: float = 1.0


class ReplayMemory:
    """Ring-buffer replay memory with prioritized sampling and logging."""

    def __init__(
        self, capacity: int = 1000, alpha: float = 0.6, log_dir: str = "."
    ) -> None:
        """Create a replay memory.

        Args:
            capacity: Maximum number of experiences to store.
            alpha: How much prioritization to apply (0=no prioritization).
            log_dir: Directory where memory interactions should be logged.
        """
        self.capacity = capacity
        self.alpha = alpha
        self._storage: list[Experience] = []
        self._priorities: list[float] = []
        self._position = 0
        self._bus = MemoryBus(log_dir)

    def add(
        self, experience: Experience, priority: float | None = None
    ) -> None:
        """Add a new experience to memory and log the insertion."""
        if priority is None:
            priority = max(self._priorities, default=1.0)
        experience.priority = priority

        if len(self._storage) < self.capacity:
            self._storage.append(experience)
            self._priorities.append(priority)
        else:
            self._storage[self._position] = experience
            self._priorities[self._position] = priority
        self._position = (self._position + 1) % self.capacity

        self._bus.log_interaction(
            agent_id="replay_memory",
            team="memory",
            message="push experience into replay buffer.",
            data=asdict(experience),
        )

    def sample(self, batch_size: int) -> list[Experience]:
        """Sample experiences using prioritized sampling."""
        if not self._storage:
            return []

        scaled = [p ** self.alpha for p in self._priorities]
        indices = random.choices(
            range(len(self._storage)), weights=scaled, k=batch_size
        )
        return [self._storage[i] for i in indices]

    def recall(self, state: Any, top_k: int = 1) -> List[Experience]:
        """Retrieve experiences with matching state and log the recall."""
        matches = [
            exp for exp in reversed(self._storage) if exp.state == state
        ][:top_k]
        if self._bus:
            for exp in matches:
                self._bus.log_interaction(
                    agent_id="replay_memory",
                    team="memory",
                    message="recall experience from replay buffer.",
                    data=asdict(exp),
                )
        return matches

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    def push(self, state: Any, action: Any, reward: float, next_state: Any, done: bool) -> None:
        """Compatibility wrapper for adding experiences."""
        self.add(Experience(state, action, reward, next_state, done))

    def __len__(self) -> int:
        """Return the number of stored experiences."""
        return len(self._storage)