"""Monte Carlo exploration utilities.

This module defines :class:`MonteCarloExplorer` which coordinates with
:class:`~jarvis.agents.simulation_agent.SimulationAgent` to search a problem
space using a lightweight Monte Carlo tree search strategy.  It generates a
number of starting moves, evaluates them using the simulation agent and
iteratively expands the most promising branches.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .simulation_agent import SimulationAgent


@dataclass
class BranchResult:
    """Represents a simulated branch and its outcome score."""

    move: str
    score: float


class MonteCarloExplorer:
    """Search a problem space by simulating multiple futures."""

    def __init__(self, simulation_agent: SimulationAgent, branch_count: int = 20, depth: int = 2) -> None:
        self.sim_agent = simulation_agent
        self.branch_count = branch_count
        self.depth = depth

    async def explore(self, problem: str) -> BranchResult:
        """Run a Monte Carlo style exploration.

        Parameters
        ----------
        problem:
            Description of the problem to explore.  The format is intentionally
            generic; the simulation agent interprets it according to its own
            model.

        Returns
        -------
        BranchResult
            The highest scoring branch discovered during exploration.
        """

        # Initial set of candidate moves
        current_moves = [f"move_{i}" for i in range(self.branch_count)]
        best = BranchResult(move="", score=-1.0)

        for depth in range(self.depth):
            # Evaluate all current moves concurrently
            scores = await asyncio.gather(
                *[self.sim_agent.quick_simulate(problem, mv) for mv in current_moves]
            )
            branch_results = [BranchResult(mv, sc) for mv, sc in zip(current_moves, scores)]
            branch_results.sort(key=lambda br: br.score, reverse=True)

            if branch_results and branch_results[0].score > best.score:
                best = branch_results[0]

            # Narrow to top half for further expansion
            survivors = branch_results[: max(1, len(branch_results) // 2)]
            current_moves = [f"{br.move}_d{depth}" for br in survivors]

        return best


__all__ = ["MonteCarloExplorer", "BranchResult"]
