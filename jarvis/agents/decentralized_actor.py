from __future__ import annotations

"""Decentralized actor with shared gradient buffers.

This module defines :class:`DecentralizedActor`, a minimal policy used for
multi‑agent reinforcement learning experiments.  Each actor maintains its
own set of parameters but writes policy‑gradient updates to a shared
buffer.  After all actors have contributed their gradients the buffer can
be applied to every actor, yielding a form of synchronous parameter
sharing without a central coordinator.
"""

from typing import List, Sequence


class DecentralizedActor:
    """Linear policy with shared gradient accumulation."""

    def __init__(self, obs_dim: int, shared_gradients: List[float]) -> None:
        if len(shared_gradients) != obs_dim:
            raise ValueError("Shared gradient buffer has incorrect size")
        self.obs_dim = obs_dim
        self.params = [0.0 for _ in range(obs_dim)]
        # Reference to a gradient buffer shared across all actors.
        self.shared_gradients = shared_gradients

    def act(self, observation: Sequence[float]) -> float:
        """Compute the action as a dot product of params and observation."""
        if len(observation) != self.obs_dim:
            raise ValueError("Observation has incorrect dimension")
        return float(sum(p * o for p, o in zip(self.params, observation)))

    def accumulate_gradient(self, observation: Sequence[float], td_error: float) -> None:
        """Accumulate policy gradient into the shared buffer."""
        if len(observation) != self.obs_dim:
            raise ValueError("Observation has incorrect dimension")
        for i in range(self.obs_dim):
            self.shared_gradients[i] += td_error * observation[i]

    def apply_shared_gradients(self, learning_rate: float) -> None:
        """Apply gradients from the shared buffer to local parameters.

        The shared gradient buffer is not cleared by this method so that
        multiple actors can apply the same update.  Clearing should be
        performed by whoever manages the shared buffer once all actors have
        synchronised their parameters.
        """
        for i in range(self.obs_dim):
            self.params[i] += learning_rate * self.shared_gradients[i]


__all__ = ["DecentralizedActor"]
