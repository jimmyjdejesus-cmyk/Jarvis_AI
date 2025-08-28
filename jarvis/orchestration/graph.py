"""
Defines the LangGraph-based orchestration logic for the multi-agent teams.
"""

import asyncio
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
# from langgraph.checkpoints import SqliteSaver # Temporarily removed to resolve import error
from jarvis.orchestration.team_agents import OrchestratorAgent, TeamMemberAgent
from jarvis.orchestration.pruning import PruningEvaluator
from jarvis.critics import RedTeamCritic, BlueTeamCritic

# Define the state for our graph
class TeamWorkflowState(TypedDict):
    objective: str
    context: Dict[str, Any]
    team_outputs: Dict[str, Any]
    critics: Dict[str, Any]
    next_team: str

class MultiTeamOrchestrator:
    """Uses LangGraph to orchestrate the five specialized teams."""

    def __init__(
        self,
        orchestrator_agent: OrchestratorAgent,
        evaluator: PruningEvaluator | None = None,
    ) -> None:
        self.orchestrator = orchestrator_agent
        self.evaluator = evaluator
        self.red_critic = RedTeamCritic()
        self.blue_critic = BlueTeamCritic()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph for the multi-team workflow."""
        graph = StateGraph(TeamWorkflowState)

        # Define nodes for each team's execution
        graph.add_node("adversary_pair", self._run_adversary_pair)
        graph.add_node("competitive_pair", self._run_competitive_pair)
        graph.add_node("security_quality", self._run_security_quality)
        graph.add_node("innovators_disruptors", self._run_innovators_disruptors)
        graph.add_node("broadcast_findings", self._broadcast_findings)

        # The graph starts with the competitive pair to generate initial ideas
        graph.set_entry_point("competitive_pair")

        # Define the workflow logic
        graph.add_edge("competitive_pair", "adversary_pair")
        graph.add_edge("adversary_pair", "innovators_disruptors")
        graph.add_edge("innovators_disruptors", "broadcast_findings") # Broadcast after innovation
        graph.add_edge("broadcast_findings", "security_quality")
        graph.add_edge("security_quality", END) # The White team is the final check

        # Temporarily compiling without a checkpointer to resolve import issues.
        # State will not be persisted between runs.
        return graph.compile()

    def _run_team(self, team: TeamMemberAgent, state: TeamWorkflowState) -> Dict[str, Any]:
        """Helper function to run a single team member."""
        logger = getattr(team, "log", lambda *a, **k: None)
        if self.evaluator and self.evaluator.should_prune(team.team):
            logger("Team pruned; skipping execution.")
            return {"status": "pruned"}

        try:
            result = team.run(state["objective"], state["context"])
        except NotImplementedError:
            logger(f"Starting simulated task for objective: {state['objective']}")
            result = {
                f"{team.team.lower()}_output": f"Completed simulated task for {team.team} team."
            }
            logger("Simulated task finished.", data=result)

        if self.evaluator:
            output = {
                "text": str(result),
                "quality": result.get("quality", 0.0) if isinstance(result, dict) else 0.0,
                "cost": result.get("cost", 0.0) if isinstance(result, dict) else 0.0,
            }
            asyncio.run(self.evaluator.evaluate(team.team, output))

        return result

    async def _run_team_async(self, team: TeamMemberAgent, state: TeamWorkflowState) -> Dict[str, Any]:
        """Execute a team in a background thread for parallel coordination."""
        if self.evaluator and self.evaluator.should_prune(team.team):
            logger = getattr(team, "log", lambda *a, **k: None)
            logger("Team pruned; skipping execution.")
            return {"status": "pruned"}

        # Respect runtime controls like pause and merge
        while self.orchestrator.team_status.get(team.team) == "paused":
            await asyncio.sleep(0.1)
        if self.orchestrator.team_status.get(team.team) == "merged":
            team.log("Team merged; skipping execution.")
            return {"status": "merged"}
        return await asyncio.to_thread(self._run_team, team, state)

    def _run_adversary_pair(self, state: TeamWorkflowState) -> TeamWorkflowState:
        """Runs the Red and Blue teams in parallel and reviews their outputs."""
        red_agent, blue_agent = self.orchestrator.teams["adversary_pair"]

        async def run_pair():
            return await asyncio.gather(
                self._run_team_async(red_agent, state),
                self._run_team_async(blue_agent, state),
            )

        red_output, blue_output = asyncio.run(run_pair())

        async def review_pair() -> list:
            return await asyncio.gather(
                self.red_critic.review(red_output),
                asyncio.to_thread(self.blue_critic.review, blue_output),
            )

        red_verdict, blue_verdict = asyncio.run(review_pair())
        state.setdefault("critics", {})
        state["critics"]["red"] = red_verdict
        state["critics"]["blue"] = blue_verdict
        state["team_outputs"]["adversary_pair"] = [red_output, blue_output]
        return state

    def _run_competitive_pair(self, state: TeamWorkflowState) -> TeamWorkflowState:
        """Runs the Yellow and Green teams in parallel."""
        yellow_agent, green_agent = self.orchestrator.teams["competitive_pair"]

        async def run_pair():
            return await asyncio.gather(
                self._run_team_async(yellow_agent, state),
                self._run_team_async(green_agent, state),
            )

        yellow_output, green_output = asyncio.run(run_pair())
        oracle_result = self._oracle_judge(yellow_output, green_output)
        state["team_outputs"]["competitive_pair"] = [yellow_output, green_output]
        state["team_outputs"]["oracle_result"] = oracle_result
        state["context"]["reinforced_strategy"] = oracle_result["winning_output"]
        return state

    @staticmethod
    def _oracle_judge(yellow_output: Dict[str, Any], green_output: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate team outputs and select the winner based on a score."""

        def _score(output: Any) -> float:
            if isinstance(output, dict):
                for key in ("score", "quality"):
                    if key in output and isinstance(output[key], (int, float)):
                        return float(output[key])
                return float(len(str(output)))
            return float(len(str(output)))

        yellow_score = _score(yellow_output)
        green_score = _score(green_output)
        if yellow_score >= green_score:
            winner = "Yellow"
            winning_output = yellow_output
        else:
            winner = "Green"
            winning_output = green_output
        return {
            "winner": winner,
            "scores": {"Yellow": yellow_score, "Green": green_score},
            "winning_output": winning_output,
        }

    def _run_security_quality(self, state: TeamWorkflowState) -> TeamWorkflowState:
        """Runs the White team."""
        white_agent = self.orchestrator.teams["security_quality"]
        white_output = self._run_team(white_agent, state)
        state["team_outputs"]["security_quality"] = white_output
        return state

    def _run_innovators_disruptors(self, state: TeamWorkflowState) -> TeamWorkflowState:
        """Runs the Black team."""
        # This is where the special visibility rule applies.
        # The Black team's context would be filtered to exclude White team's outputs.
        black_agent = self.orchestrator.teams["innovators_disruptors"]
        
        # Create a filtered context for the Black team
        filtered_context = state["context"].copy()
        # In a real scenario, we would filter the memory bus view here.
        
        black_output = self._run_team(black_agent, state)
        state["team_outputs"]["innovators_disruptors"] = black_output
        return state

    def _broadcast_findings(self, state: TeamWorkflowState) -> TeamWorkflowState:
        """Broadcasts key findings from the innovator team to the shared bus."""
        innovator_output = state["team_outputs"].get("innovators_disruptors", {})
        if innovator_output:
            self.orchestrator.broadcast(
                "Broadcasting innovative findings for collective learning.",
                data=innovator_output
            )
        return state

    def run(self, objective: str):
        """Executes the full orchestration graph."""
        initial_state = {
            "objective": objective,
            "context": {},
            "team_outputs": {},
            "critics": {},
            "next_team": "competitive_pair"
        }
        
        # The `stream` method will execute the graph step-by-step
        for step in self.graph.stream(initial_state):
            # Each step is a dictionary with the node name and its output
            node, output = next(iter(step.items()))
            self.orchestrator.log(f"Completed step: {node}", data=output)
        
        return "Orchestration complete."
