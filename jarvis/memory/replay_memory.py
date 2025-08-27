"""Replay memory utilities with prioritized experience replay."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from typing import Any

from .memory_bus import MemoryBus


@dataclass
class Experience:
    """Container for a single agent-environment interaction.

    Attributes:
        state: Observation from the environment.
        action: Action taken by the agent.
        reward: Reward received after the action.
        next_state: Observation after taking the action.
        done: Flag indicating whether the episode terminated.
        priority: Sampling priority; larger values increase sampling chance.
    """

    state: Any
    action: Any
    reward: float
    next_state: Any
    done: bool
    priority: float = 1.0


class ReplayMemory:
    """Ring-buffer replay memory with prioritized sampling."""

    def __init__(
        self, capacity: int, alpha: float = 0.6, log_dir: str = "."
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
            message="Inserted experience into replay buffer.",
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

    def __len__(self) -> int:
        """Return the number of stored experiences."""
        return len(self._storage)
