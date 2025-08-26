from __future__ import annotations

"""Benchmark utilities for CTDE training stability and efficiency."""

from statistics import mean, pstdev
from typing import Dict, List

from jarvis.learning.ctde_critic import CTDECritic
from jarvis.agents.decentralized_actor import DecentralizedActor


def run_ctde_benchmark(episodes: int = 50, learning_rate: float = 0.1) -> Dict[str, float]:
    """Run a toy CTDE training loop and return simple metrics.

    The benchmark simulates a cooperative two‑agent environment with a
    constant reward signal.  Although simplistic, it exercises the
    centralized critic and gradient sharing mechanisms, allowing unit tests
    to reason about sample efficiency and parameter stability.
    """

    critic = CTDECritic(n_agents=2, state_dim=2, learning_rate=learning_rate)
    shared_grads = [0.0, 0.0]
    actors = [DecentralizedActor(obs_dim=2, shared_gradients=shared_grads) for _ in range(2)]

    action_history: List[float] = []
    for _ in range(episodes):
        state = [1.0, 1.0]
        actions = [a.act(state) for a in actors]
        # Reward encourages actions near 1.0
        rewards = [1.0 - abs(a) for a in actions]
        td_error = critic.update(state, rewards)
        for actor in actors:
            actor.accumulate_gradient(state, td_error)
        for actor in actors:
            actor.apply_shared_gradients(learning_rate)
        for i in range(len(shared_grads)):
            shared_grads[i] = 0.0
        action_history.extend(actions)

    return {
        "avg_action": mean(action_history),
        "action_stability": pstdev(action_history),
    }


__all__ = ["run_ctde_benchmark"]
