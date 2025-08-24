from __future__ import annotations

"""Centralized critic for CTDE training.

This module implements a lightweight centralized critic used in
Centralized Training with Decentralized Execution (CTDE) setups.  The
critic maintains a simple linear value function over the joint state of
all agents.  During training it receives the joint state and individual
rewards, computes a baseline value estimate, and updates its weights
using a temporal‑difference style rule.  The returned TD error can then
be used by decentralized actors to compute policy gradients that share a
common baseline.
"""

from typing import Sequence


class CTDECritic:
    """Minimal centralized critic based on a linear value function.

    Parameters
    ----------
    n_agents:
        Number of decentralized actors in the environment.
    state_dim:
        Dimensionality of the joint state representation provided to the
        critic.  The critic expects the state as a flat sequence of
        ``state_dim`` floats.
    learning_rate:
        Step size applied when updating the value function weights.
    """

    def __init__(self, n_agents: int, state_dim: int, learning_rate: float = 0.01) -> None:
        self.n_agents = n_agents
        self.state_dim = state_dim
        self.learning_rate = learning_rate
        # Linear value function weights initialised to zero.
        self._weights = [0.0 for _ in range(state_dim)]

    def predict(self, joint_state: Sequence[float]) -> float:
        """Return the critic's value estimate for the given state."""
        if len(joint_state) != self.state_dim:
            raise ValueError("Joint state has incorrect dimension")
        return float(sum(w * s for w, s in zip(self._weights, joint_state)))

    def update(self, joint_state: Sequence[float], rewards: Sequence[float]) -> float:
        """Update the critic and return the TD error.

        The critic computes a baseline value for the joint state, compares it
        against the mean reward across agents, and performs a stochastic
        gradient step.  The temporal‑difference error is returned so that
        decentralized actors can compute policy gradients using the shared
        baseline.
        """

        baseline = self.predict(joint_state)
        if len(rewards) != self.n_agents:
            raise ValueError("Reward vector has incorrect length")
        target = sum(rewards) / self.n_agents
        td_error = target - baseline
        for i in range(self.state_dim):
            self._weights[i] += self.learning_rate * td_error * joint_state[i]
        return td_error

    @property
    def weights(self) -> Sequence[float]:
        """Read‑only view of the critic's weights."""
        return tuple(self._weights)


__all__ = ["CTDECritic"]
