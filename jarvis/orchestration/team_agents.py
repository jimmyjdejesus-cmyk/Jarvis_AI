"""
Defines the hierarchical agent structure for the Jarvis V2 Orchestration System.
"""

import uuid
import os
import asyncio
from typing import List, Dict, Any, Callable, Optional

from jarvis.memory.memory_bus import MemoryBus
from jarvis.agents.research_agent import ResearchAgent
from jarvis.orchestration.message_bus import MessageBus
from jarvis.orchestration.pruning import PruningEvaluator
from jarvis.orchestration.mission import MissionDAG
from jarvis.orchestration.mission_planner import MissionPlanner
from jarvis.ecosystem import superintelligence

class TeamMemberAgent:
    """Base class for all team member agents."""
    def __init__(self, orchestrator: 'OrchestratorAgent', team_name: str):
        self.agent_id = f"{team_name.lower()}_{uuid.uuid4().hex[:8]}"
        self.orchestrator = orchestrator
        self.team = team_name
        self.tools: Dict[str, Callable] = {}
        # Each team has an isolated memory bus and access to shared docs
        self.local_bus = orchestrator.team_buses[team_name]
        self.docs_bus = orchestrator.shared_docs_bus

    def log(self, message: str, data: Dict[str, Any] = None):
        """Logs a message to the team's local memory bus."""
        self.local_bus.log_interaction(self.agent_id, self.team, message, data)

    def share_doc(self, message: str, data: Dict[str, Any] = None):
        """Share a document or finding with other teams via the shared channel."""
        self.docs_bus.log_interaction(self.agent_id, f"SharedDocs|{self.team}", message, data)

    def run(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """The main execution logic for the agent. To be implemented by subclasses."""
        raise NotImplementedError("Each team member must implement the 'run' method.")

# Define the specialized teams
class RedAdversaryAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "Red")

class BlueAdversaryAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "Blue")

class YellowCompetitiveAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "Yellow")
        self.research_agent = ResearchAgent(memory_bus=self.local_bus)

    def run(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Starting web research to generate competitive ideas.")
        report = self.research_agent.research(
            f"innovative ideas for {objective}", save_dir=self.local_bus.log_file.parent
        )
        self.log("Web research complete.", data=report)
        return {"research_summary": report}

class GreenCompetitiveAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "Green")

class WhiteSecurityAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "White")

class BlackInnovatorAgent(TeamMemberAgent):
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__(orchestrator, "Black")

    def run(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate disruptive strategies for the given objective.

        The agent logs its reasoning to the local memory bus and shares a
        summary with other teams via the shared docs bus.  The returned
        strategy mentions which context keys were considered.

        Parameters
        ----------
        objective:
            The high level goal to address.
        context:
            Filtered contextual information relevant to the objective.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the proposed disruptive strategy.
        """

        self.log("Generating disruptive strategy.", data={"objective": objective, "context": context})
        factors = ", ".join(sorted(context.keys())) if context else "no context"
        strategy = f"Use {factors} to challenge {objective}"
        self.share_doc("Disruptive strategy drafted", data={"strategy": strategy})
        return {"strategy": strategy}


class OrchestratorAgent:
    """
    Manages a set of five specialized teams to accomplish a complex objective.
    """
    def __init__(self, meta_agent: 'MetaAgent', objective: str, directory: str = ".", shared_bus: MemoryBus = None):
        self.agent_id = f"orchestrator_{uuid.uuid4().hex[:8]}"
        self.meta_agent = meta_agent
        self.objective = objective
        self.memory_bus = MemoryBus(directory) # Local bus for this project
        self.shared_bus = shared_bus # Shared bus for inter-orchestrator communication
        # Shared docs channel for team collaboration
        self.shared_docs_bus = MemoryBus(os.path.join(directory, "shared_docs"))
        # Per-team isolated memory buses
        team_names = ["Red", "Blue", "Yellow", "Green", "White", "Black"]
        self.team_buses = {name: MemoryBus(os.path.join(directory, name.lower())) for name in team_names}
        self.team_status = {name: "running" for name in team_names}
        self.lineage_log: List[Dict[str, Any]] = []
        # Event bus for coordination and pruning suggestions
        self.event_bus = MessageBus()
        self.pruning_evaluator = PruningEvaluator(self.event_bus)
        
        # Initialize the five teams
        self.teams = {
            "adversary_pair": (RedAdversaryAgent(self), BlueAdversaryAgent(self)),
            "competitive_pair": (YellowCompetitiveAgent(self), GreenCompetitiveAgent(self)),
            "security_quality": WhiteSecurityAgent(self),
            "innovators_disruptors": BlackInnovatorAgent(self),
        }
        # Record initial team lineage
        for name in team_names:
            event = {"action": "spawn", "team": name, "parent": self.agent_id}
            self.lineage_log.append(event)
            self.log("Lineage update", data=event)
        
        # Initialize the LangGraph orchestrator
        from jarvis.orchestration.graph import MultiTeamOrchestrator # Local import to break cycle
        self.orchestrator = MultiTeamOrchestrator(self, evaluator=self.pruning_evaluator)
        
        self.log(f"Orchestrator initialized for objective: {objective}")

    def log(self, message: str, data: Dict[str, Any] = None):
        """Logs a message from the orchestrator itself to its local bus."""
        self.memory_bus.log_interaction(self.agent_id, "Orchestrator", message, data)

    def broadcast(self, message: str, data: Dict[str, Any] = None):
        """Broadcasts a significant finding to the shared memory bus for other orchestrators."""
        if self.shared_bus:
            self.shared_bus.log_interaction(self.agent_id, f"Broadcast | {self.objective[:30]}...", message, data)

    @staticmethod
    def create_black_team_orchestrator(
        objective: str,
        directory: str = ".",
        shared_bus: Optional[MemoryBus] = None,
    ) -> "BlackTeamOrchestrator":
        """Spawn a standalone orchestrator for Black team missions."""
        from .black_team_orchestrator import BlackTeamOrchestrator

        return BlackTeamOrchestrator(objective, directory, shared_bus=shared_bus)

    # ---- Runtime control methods ----
    def pause_team(self, team_name: str):
        """Pause a team during live orchestration."""
        if team_name in self.team_status:
            self.team_status[team_name] = "paused"
            self.log(f"Team {team_name} paused by operator.")
            asyncio.run(
                self.event_bus.publish(
                    "team.paused",
                    {"team": team_name},
                    scope=self.agent_id,
                    run_id=self.agent_id,
                    step_id=f"pause.{team_name}",
                )
            )

    def restart_team(self, team_name: str):
        """Restart a previously paused team."""
        if team_name in self.team_status:
            self.team_status[team_name] = "running"
            self.log(f"Team {team_name} restarted by operator.")
            asyncio.run(
                self.event_bus.publish(
                    "team.restarted",
                    {"team": team_name},
                    scope=self.agent_id,
                    run_id=self.agent_id,
                    step_id=f"restart.{team_name}",
                )
            )

    def merge_teams(self, source_team: str, target_team: str):
        """Merge one team into another and record lineage."""
        if source_team in self.team_status and target_team in self.team_status:
            self.team_status[source_team] = "merged"
            event = {"action": "merge", "from": source_team, "into": target_team}
            self.lineage_log.append(event)
            self.log(f"Merging team {source_team} into {target_team}", data=event)
            asyncio.run(
                self.event_bus.publish(
                    "team.merged",
                    event,
                    scope=self.agent_id,
                    run_id=self.agent_id,
                    step_id=f"merge.{source_team}.{target_team}",
                    parent_id=source_team,
                )
            )

    def get_lineage(self) -> List[Dict[str, Any]]:
        """Return the recorded orchestration lineage."""
        return list(self.lineage_log)

    def run(self):
        """Executes the multi-team workflow to achieve the objective."""
        self.log("Starting multi-team orchestration...")
        result = self.orchestrator.run(self.objective)
        self.log("Multi-team orchestration finished.", data={"final_result": result})
        return result


class MetaAgent:
    """
    The top-level agent that oversees the entire operation and can spawn orchestrators.
    """
    def __init__(self, directory: str = "."):
        self.agent_id = f"meta_agent_{uuid.uuid4().hex[:8]}"
        self.orchestrators: List[OrchestratorAgent] = []
        # The MetaAgent manages the shared bus for all its orchestrators
        self.shared_memory_bus = MemoryBus(os.path.join(directory, "shared_orchestrator_bus"))
        missions_dir = os.path.join(directory, "config", "missions")
        self.mission_planner = MissionPlanner(missions_dir)
        # Internal metrics for evaluating emergent behavior
        self._metrics: Dict[str, List[Dict[str, Any]]] = {
            "plans": [],
            "critic_feedback": [],
        }
        self.log("Meta-Agent initialized and shared memory bus is active.")

    def log(self, message: str, data: Dict[str, Any] = None):
        """Logs a message from the Meta-Agent to the shared bus."""
        self.shared_memory_bus.log_interaction(self.agent_id, "Meta", message, data)

    def plan_mission(self, mission_name: str) -> MissionDAG:
        """Create a mission plan and enqueue its tasks.

        Parameters
        ----------
        mission_name: str
            Name of the mission file (without extension) located in
            ``config/missions``.

        Returns
        -------
        MissionDAG
            The planned mission graph.  Tasks are already enqueued on the
            planner's queue for downstream consumption.
        """

        dag = self.mission_planner.plan(mission_name)
        self.log(
            f"Planned mission '{mission_name}' with {len(dag.nodes)} nodes.")
        return dag

    def next_task(self) -> Dict[str, Any] | None:
        """Retrieve the next task from the mission queue."""
        task = self.mission_planner.queue.dequeue()
        if task:
            self.log(f"Dequeued task {task.get('id', '')}.")
        return task

    def spawn_orchestrator(
        self,
        objective: str,
        directory: str = ".",
        tags: Optional[List[str]] = None,
    ) -> "OrchestratorAgent" | "BlackTeamOrchestrator":
        """Dynamically create and deploy an orchestrator for a new objective.

        If ``tags`` contains ``"disruptive"`` a dedicated
        :class:`BlackTeamOrchestrator` is spawned; otherwise the standard
        :class:`OrchestratorAgent` is used.
        """
        score = self._evaluate_objective(objective)
        self._metrics["plans"].append({"objective": objective, "score": score})
        self.log(
            f"Spawning new orchestrator for objective: '{objective}' in directory '{directory}'.",
            data={"planning_score": score, "tags": tags},
        )
        if tags and "disruptive" in tags:
            orchestrator = OrchestratorAgent.create_black_team_orchestrator(
                objective,
                directory,
                shared_bus=self.shared_memory_bus,
            )
        else:
            orchestrator = OrchestratorAgent(self, objective, directory, shared_bus=self.shared_memory_bus)
        self.orchestrators.append(orchestrator)  # type: ignore[arg-type]
        return orchestrator

    def register_result(self, orchestrator: OrchestratorAgent, result: Any) -> Dict[str, Any]:
        """Record the result of an orchestrator run and gather critic feedback.

        Parameters
        ----------
        orchestrator:
            The orchestrator that produced the result.
        result:
            The final result from the orchestrator's run.

        Returns
        -------
        Dict[str, Any]
            The critic feedback for the result.
        """
        feedback = self._critic_feedback(result)
        self._metrics["critic_feedback"].append(feedback)
        self.log(
            "Critic feedback recorded",
            data={"orchestrator": orchestrator.agent_id, "feedback": feedback},
        )
        try:
            superintelligence.record_meta_output(orchestrator.agent_id, result, feedback)
        except Exception as exc:  # pragma: no cover - defensive
            self.log("Failed to record meta output", data={"error": str(exc)})
        return feedback

    def get_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return a copy of collected metrics for analysis."""
        return {k: list(v) for k, v in self._metrics.items()}

    def _evaluate_objective(self, objective: str) -> float:
        """Basic heuristic to estimate objective complexity.

        The heuristic scores objectives based on word count, capped at 1.0.
        """
        words = objective.split()
        return min(1.0, len(words) / 20)

    def _critic_feedback(self, result: Any) -> Dict[str, Any]:
        """Generate a simple critic assessment for a result."""
        success = bool(result)
        feedback = {"success": success, "issues": []}
        if not success:
            feedback["issues"].append("empty_result")
        return feedback

# Example usage:
if __name__ == "__main__":
    # 1. The Meta-Agent is initialized
    meta_agent = MetaAgent()

    # 2. The user provides a high-level objective, and the Meta-Agent spawns an orchestrator
    objective = "Develop a secure and innovative user authentication module."
    project_directory = "auth_module_project"
    os.makedirs(project_directory, exist_ok=True)
    
    orchestrator = meta_agent.spawn_orchestrator(objective, project_directory)
    
    # 3. The orchestrator would then run its complex, multi-team workflow
    # orchestrator.run() # This will be implemented with LangGraph

    print(f"Meta-Agent spawned Orchestrator {orchestrator.agent_id} for objective: '{objective}'")
    print(f"Project logs will be in: {os.path.abspath(project_directory)}/agent.md")