"""Counterfactual simulation specialist.

This module defines :class:`SimulationAgent`, a lightweight specialist that
leverages the project-wide ``BaseSpecialist`` infrastructure.  The agent
accepts concrete historical facts, a causal event, and an intervention
describing how the event's outcome should be altered.  It then composes a
structured prompt that clearly separates the known facts, the original causal
explanation, and the point of divergence.  The prompt is sent to the provided
``mcp_client`` which is responsible for generating the alternate‑history
narrative.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import random

from jarvis.agents.base_specialist import BaseSpecialist
from jarvis.world_model.hypergraph import HierarchicalHypergraph
from jarvis.world_model.predictive_simulation import PredictiveSimulator


class SimulationAgent(BaseSpecialist):
    """Runs counterfactual simulations based on an altered world state."""

    def __init__(
        self,
        mcp_client: Any,
        hypergraph: HierarchicalHypergraph | None = None,
        simulator: PredictiveSimulator | None = None,
    ) -> None:
        self.mcp_client = mcp_client
        self.hypergraph = hypergraph
        self.simulator = simulator
        self.specialization = (
            "Runs counterfactual simulations based on an altered world state."
        )

    async def quick_simulate(self, state: Any, move: str) -> float:
        """Estimate outcome score for a potential move.

        The evaluation blends heuristic predictions from ``PredictiveSimulator``
        with a numeric judgment from the LLM.  If either component is
        unavailable, the remaining signal is used.  A random score is returned
        only when no evaluation could be produced.
        """

        model_score: float | None = None
        prompt = (
            "Rate from 0 to 1 how promising the following move is in the given "
            f"state. Only return the numeric score.\nSTATE: {state}\nMOVE: {move}"
        )
        try:
            response = await self.mcp_client.generate_response(prompt=prompt)
            model_score = float(response.strip())
        except Exception:
            model_score = None

        sim_score: float | None = None
        if self.simulator:
            sim_score = self.simulator.evaluate(state, move)

        if model_score is not None and sim_score is not None:
            return (model_score + sim_score) / 2
        if model_score is not None:
            return model_score
        if sim_score is not None:
            return sim_score
        return random.random()

    async def run_counterfactual(
        self,
        concrete_facts: Dict[str, Any],
        causal_event: Dict[str, Any],
        intervention: Dict[str, Any],
        confidence: float = 0.5,
    ) -> str:
        """Execute the counterfactual simulation.

        Parameters
        ----------
        concrete_facts:
            Data from Layer 1 (the "what").
        causal_event:
            The original event node from Layer 3 (the "why").
        intervention:
            The change to apply to the causal event.
        """

        print("SIMULATION AGENT: Received counterfactual mission.")

        # Create a temporary, altered copy of the causal event for the simulation
        sim_causal_event = causal_event.copy()
        event_to_change = intervention["node"]
        new_outcome = intervention["new_outcome"]
        sim_causal_event["outcome"] = new_outcome
        # Remove original effects, as they are no longer valid
        sim_causal_event.pop("effects", None)

        print(
            f"SIMULATION AGENT: Applying intervention -> '{event_to_change}' outcome is now '{new_outcome}'."
        )

        # Structured prompt that forces the model to honor the intervention
        prompt = f"""
        You are a historian simulating an alternate timeline.
        Your task is to generate a plausible narrative based on a single point of divergence.
        Ground your narrative in the provided facts.

        KNOWN FACTS (Layer 1 - Concrete):
        {json.dumps(concrete_facts, indent=2)}

        PIVOTAL EVENT & ACTUAL OUTCOME (Layer 3 - Causal):
        {json.dumps(causal_event, indent=2)}

        THE INTERVENTION (The Point of Divergence):
        The outcome of the '{event_to_change}' is now '{new_outcome}'.

        YOUR TASK:
        Narrate the immediate, plausible consequences of this new outcome. What happens in the hours and days following Napoleon's victory at Waterloo?
        """

        narrative = await self.mcp_client.generate_response(prompt=prompt)

        if self.hypergraph:
            self.hypergraph.add_causal_belief(event_to_change, new_outcome, confidence)

        return narrative

    # ------------------------------------------------------------------
    async def process_task(
        self,
        task: str,
        context: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stub implementation to satisfy :class:`BaseSpecialist`.

        This agent currently exposes only the ``run_counterfactual`` method and
        does not support generic task processing."""

        raise NotImplementedError(
            "SimulationAgent.process_task is not implemented; use run_counterfactual instead."
        )

    def get_specialization_info(self) -> Dict[str, Any]:
        """Return metadata describing this specialist."""

        return {"specialization": self.specialization}


__all__ = ["SimulationAgent"]

