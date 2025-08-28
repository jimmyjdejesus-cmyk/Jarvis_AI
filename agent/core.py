"""Core agent functionality for Jarvis AI with replay memory support."""

from __future__ import annotations

from typing import Any

from jarvis.memory.memory_bus import MemoryBus
from jarvis.memory.replay_memory import ReplayMemory


class JarvisAgent:
    """Minimal agent demonstrating replay-memory integration."""

    def __init__(self, model_name: str = "llama3.2", memory_bus: MemoryBus | None = None):
        self.model_name = model_name
        self.memory_bus = memory_bus or MemoryBus()
        self.replay_memory = ReplayMemory(memory_bus=self.memory_bus)

    def chat(self, message: str) -> str:
        """Echo the message and store interaction in replay memory."""
        response = f"Echo: {message} (using {self.model_name})"
        # Store as transition with dummy reward and no next state yet
        self.replay_memory.push(message, response, 0.0, None, False)
        return response

    def recall(self, state: Any, top_k: int = 1):
        """Expose replay-memory recall to planning steps."""
        return self.replay_memory.recall(state, top_k)

    def plan(self, state: Any) -> Any:
        """Very small planning example using recalled transitions."""
        recalled = self.recall(state, top_k=1)
        if recalled:
            # Return the previously taken action for this state
            return recalled[0][1]
        return None
