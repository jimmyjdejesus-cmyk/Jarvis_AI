"""
Defines the LangGraph-based orchestration logic for the multi-agent teams.
"""
import asyncio
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
# from langgraph.checkpoints import SqliteSaver
# Temporarily removed to resolve import error
from jarvis.orchestration.team_agents import OrchestratorAgent, TeamMemberAgent
from jarvis.orchestration.pruning import PruningEvaluator
from jarvis.orchestration.context_utils import filter_context, filter_team_outputs

from jarvis.critics import WhiteGate, CriticVerdict
from jarvis.critics import RedTeamCritic, BlueTeamCritic

# Team name constants
COMPETITIVE_PAIR_TEAM = "competitive_pair"
ADVERSARY_PAIR_TEAM = "adversary_pair"
INNOVATORS_DISRUPTORS_TEAM = "innovators_disruptors"
SECURITY_QUALITY_TEAM = "security_quality"


# Team name constants to avoid hardcoded strings
ADVERSARY_PAIR_TEAM = "adversary_pair"
COMPETITIVE_PAIR_TEAM = "competitive_pair"
SECURITY_QUALITY_TEAM = "security_quality"
INNOVATORS_DISRUPTORS_TEAM = "innovators_disruptors"


# Team identifiers used throughout the orchestration graph
ADVERSARY_PAIR_TEAM = "adversary_pair"
COMPETITIVE_PAIR_TEAM = "competitive_pair"
SECURITY_QUALITY_TEAM = "security_quality"
INNOVATORS_DISRUPTORS_TEAM = "innovators_disruptors"


# Define the state for our graph


class TeamWorkflowState(TypedDict, total=False):
    objective: str
    context: Dict[str, Any]
    team_outputs: Dict[str, Any]
    critics: Dict[str, Any]
    next_team: str
    halt: bool



class MultiTeamOrchestrator:
    """Uses LangGraph to orchestrate the five specialized teams."""

    def __init__(
        self,
        orchestrator_agent: OrchestratorAgent,
        evaluator: PruningEvaluator | None = None,
        red_critic: RedTeamCritic | None = None,
        blue_critic: BlueTeamCritic | None = None,
        white_gate: WhiteGate | None = None,
    ) -> None:
        self.orchestrator = orchestrator_agent
        self.evaluator = evaluator
        self.red_critic = red_critic or RedTeamCritic()
        self.blue_critic = blue_critic or BlueTeamCritic()
        self.white_gate = white_gate or WhiteGate()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph for the multi-team workflow."""
        graph = StateGraph(TeamWorkflowState)

        # Define nodes for each team's execution
        graph.add_node(ADVERSARY_PAIR_TEAM, self._run_adversary_pair)
        graph.add_node(COMPETITIVE_PAIR_TEAM, self._run_competitive_pair)
        graph.add_node(SECURITY_QUALITY_TEAM, self._run_security_quality)
        graph.add_node(
            INNOVATORS_DISRUPTORS_TEAM, self._run_innovators_disruptors
        )
        graph.add_node("broadcast_findings", self._broadcast_findings)

        # The graph starts with the competitive pair to generate initial ideas
        graph.set_entry_point(COMPETITIVE_PAIR_TEAM)

        # Define the workflow logic
        graph.add_edge(COMPETITIVE_PAIR_TEAM, ADVERSARY_PAIR_TEAM)
        graph.add_edge(ADVERSARY_PAIR_TEAM, INNOVATORS_DISRUPTORS_TEAM)
        graph.add_edge(
            INNOVATORS_DISRUPTORS_TEAM,
            "broadcast_findings",
        )  # Broadcast after innovation
        graph.add_edge("broadcast_findings", SECURITY_QUALITY_TEAM)
        graph.add_edge(
            SECURITY_QUALITY_TEAM,
            END,
        )  # The White team is the final check

        # Temporarily compiling without a checkpointer to resolve import
        # issues.
        # State will not be persisted between runs.
        return graph.compile()

    def _run_team(
        self, team: TeamMemberAgent, state: TeamWorkflowState
    ) -> Dict[str, Any]:
        """Helper function to run a single team member."""
        logger = getattr(team, "log", lambda *a, **k: None)
        if self.evaluator and self.evaluator.should_prune(team.team):
            logger("Team pruned; skipping execution.")
            return {"status": "pruned"}

        try:
            result = team.run(state["objective"], state["context"])
        except NotImplementedError:
            logger(
                f"Starting simulated task for objective: {state['objective']}"
            )
            result = {
                f"{team.team.lower()}_output": (
                    f"Completed simulated task for {team.team} team."
                ),
            }
            logger("Simulated task finished.", data=result)

        if self.evaluator:
            output = {
                "text": str(result),
                "quality": (
                    result.get("quality", 0.0)
                    if isinstance(result, dict)
                    else 0.0
                ),
                "cost": (
                    result.get("cost", 0.0)
                    if isinstance(result, dict)
                    else 0.0
                ),
            }
            asyncio.run(self.evaluator.evaluate(team.team, output))

        return result

    async def _run_team_async(
        self, team: TeamMemberAgent, state: TeamWorkflowState
    ) -> Dict[str, Any]:
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

def _run_adversary_pair(
        self, state: TeamWorkflowState
    ) -> TeamWorkflowState:
        """Run Red and Blue teams and merge critic verdicts via WhiteGate."""
        red_agent, blue_agent = self.orchestrator.teams[ADVERSARY_PAIR_TEAM]
        # Strip White team findings so Red and Blue operate without bias.
        filtered_context = filter_team_outputs(
            state["context"], state.get("team_outputs"), SECURITY_QUALITY_TEAM
        )
        base_state = dict(state)
        base_state["context"] = filtered_context

        async def run_pair():
            red_state = dict(base_state)
            blue_state = dict(base_state)
            return await asyncio.gather(
                self._run_team_async(red_agent, red_state),
                self._run_team_async(blue_agent, blue_state),
            )

        red_output, blue_output = asyncio.run(run_pair())

        def _to_verdict(output: Any) -> CriticVerdict:
            if isinstance(output, CriticVerdict):
                return output
            if isinstance(output, dict):
                return CriticVerdict(
                    approved=bool(output.get("approved")),
                    fixes=list(output.get("fixes", [])),
                    risk=float(output.get("risk", 0.0)),
                    notes=str(output.get("notes", "")),
                )
            return CriticVerdict(
                False,
                [],
                1.0,
                f"Unsupported output type: {type(output).__name__}",
            )

        red_verdict = _to_verdict(red_output)
        blue_verdict = _to_verdict(blue_output)
        merged = self.white_gate.merge(red_verdict, blue_verdict)

        state.setdefault("critics", {})["white_gate"] = merged.to_dict()
        state["team_outputs"][ADVERSARY_PAIR_TEAM] = [
            red_output,
            blue_output,
        ]
        state["halt"] = not merged.approved

        self.orchestrator.log(
            "WhiteGate merged verdict",
            data=merged.to_dict(),
        )
        if state["halt"]:
            self.orchestrator.log(
                "Downstream execution halted by WhiteGate."
            )
        return state

    def _run_competitive_pair(
        self, state: TeamWorkflowState
    ) -> TeamWorkflowState:
        """Run Yellow and Green teams in parallel."""
        yellow_agent, green_agent = self.orchestrator.teams[
            COMPETITIVE_PAIR_TEAM
        ]
        # Early teams shouldn't see White team findings from prior runs.
        filtered_context = filter_team_outputs(
            state["context"], state.get("team_outputs"), SECURITY_QUALITY_TEAM
        )
        base_state = dict(state)
        base_state["context"] = filtered_context

        async def run_pair():
            yellow_state = dict(base_state)
            green_state = dict(base_state)
            return await asyncio.gather(
                self._run_team_async(yellow_agent, yellow_state),
                self._run_team_async(green_agent, green_state),
            )

        yellow_output, green_output = asyncio.run(run_pair())
        oracle_result = self._oracle_judge(yellow_output, green_output)
        state["team_outputs"][COMPETITIVE_PAIR_TEAM] = [
            yellow_output,
            green_output,
        ]
        state["team_outputs"]["oracle_result"] = oracle_result
        state["context"]["reinforced_strategy"] = (
            oracle_result["winning_output"]
        )
        return state

    @staticmethod
    def _oracle_judge(
        yellow_output: Dict[str, Any], green_output: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def _run_security_quality(
        self, state: TeamWorkflowState
    ) -> TeamWorkflowState:
        """Run the White team."""
        white_agent = self.orchestrator.teams[SECURITY_QUALITY_TEAM]
        white_output = self._run_team(white_agent, state)
        state["team_outputs"][SECURITY_QUALITY_TEAM] = white_output
        return state

    def _run_innovators_disruptors(
        self, state: TeamWorkflowState
    ) -> TeamWorkflowState:
def _run_innovators_disruptors(
    self, state: TeamWorkflowState
) -> TeamWorkflowState:
    """Run the Black team in isolation from White team feedback."""
    # Start from the shared context but drop keys derived from White team
    # outputs so disruptive exploration isn't biased by security data.
    black_agent = self.orchestrator.teams[INNOVATORS_DISRUPTORS_TEAM]
    filtered_context = filter_team_outputs(
        state["context"], state["team_outputs"], SECURITY_QUALITY_TEAM
    )
    temp_state = dict(state)
    temp_state["context"] = filtered_context

    black_output = self._run_team(black_agent, temp_state)
    state["team_outputs"][INNOVATORS_DISRUPTORS_TEAM] = black_output
    return state
        temp_state = dict(state)
        temp_state["context"] = filtered_context

        black_output = self._run_team(black_agent, temp_state)
state["team_outputs"][INNOVATORS_DISRUPTORS_TEAM] = black_output
        return state

    def _broadcast_findings(
        self, state: TeamWorkflowState
    ) -> TeamWorkflowState:
        """Broadcast key findings from the innovator team to the shared bus."""
        innovator_output = state["team_outputs"].get(
            INNOVATORS_DISRUPTORS_TEAM,
            {},
        )
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
            "next_team": COMPETITIVE_PAIR_TEAM
        }

        # The `stream` method will execute the graph step-by-step
        for step in self.graph.stream(initial_state):
            node, state = next(iter(step.items()))
            self.orchestrator.log(f"Completed step: {node}", data=state)
            if state.get("halt"):
                break

        return "Orchestration complete."
