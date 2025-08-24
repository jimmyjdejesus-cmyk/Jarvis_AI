from __future__ import annotations

"""Tests for centralized critic and decentralized actors."""

import os
import sys

sys.path.append(os.getcwd())

from jarvis.learning.ctde_critic import CTDECritic
from jarvis.agents.decentralized_actor import DecentralizedActor
from benchmarks.ctde_benchmark import run_ctde_benchmark


def test_ctde_critic_updates_weights() -> None:
    critic = CTDECritic(n_agents=2, state_dim=2, learning_rate=0.5)
    state = [1.0, 0.0]
    td_error = critic.update(state, rewards=[1.0, 1.0])
    assert td_error != 0.0
    # Weight for first dimension should have moved in direction of error
    assert critic.weights[0] != 0.0
    assert critic.weights[1] == 0.0


def test_decentralized_actors_share_gradients() -> None:
    shared = [0.0, 0.0]
    actors = [DecentralizedActor(obs_dim=2, shared_gradients=shared) for _ in range(2)]
    observation = [1.0, 1.0]
    for actor in actors:
        actor.accumulate_gradient(observation, td_error=1.0)
    for actor in actors:
        actor.apply_shared_gradients(learning_rate=0.1)
    for i in range(len(shared)):
        shared[i] = 0.0
    # Parameters should be identical and non-zero
    assert actors[0].params == actors[1].params
    assert actors[0].params[0] > 0


def test_ctde_benchmark_returns_metrics() -> None:
    metrics = run_ctde_benchmark(episodes=10, learning_rate=0.1)
    assert set(metrics) == {"avg_action", "action_stability"}
    assert isinstance(metrics["avg_action"], float)
    assert metrics["action_stability"] >= 0
