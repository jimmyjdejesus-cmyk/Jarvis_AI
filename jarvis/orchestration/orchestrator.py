"""Multi-Agent Orchestrator
Coordinates multiple specialist agents for complex tasks

This module also provides lifecycle management for nested orchestrators,
allowing complex missions to be decomposed into sub-missions with their own
scoped tools and agents."""
from __future__ import annotations

import asyncio
"""Orchestration Template
==========================

This module provides a light‑weight orchestration engine that builds
LangGraph workflows dynamically from simple agent specifications.  The
previous implementation contained a large, hand crafted orchestrator for a
fixed set of specialist agents.  For testing and experimentation we now use a
generic approach where each mission supplies a list of agent specs describing
nodes and edges of an execution graph.

The orchestrator focuses on three core ideas:

* **Dynamic graph construction** – Nodes are created at runtime based on the
  provided specification.  Edges can be linear or conditional allowing for
  branching, looping and early termination.
* **LangGraph integration** – `StateGraph` from the `langgraph` package is
  used to compile a workflow that can be executed asynchronously.
* **Minimal interface** – Only a small API is required for the tests.  The
  orchestrator accepts agent specifications and exposes a ``run`` coroutine
  which executes the compiled workflow and returns the final state.

The intent of this module is to act as a reusable template that higher level
systems (such as the ``MetaAgent``) can delegate to when constructing
mission‑specific workflows.
"""

import logging
import warnings
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .recovery import load_state, save_state
from .path_memory import PathMemory

from ..agents.specialists import (
    CodeReviewAgent,
    SecurityAgent,
    ArchitectureAgent,
    TestingAgent,
    DevOpsAgent,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .sub_orchestrator import SubOrchestrator
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


class RequestClassifier:
    """Classify user requests and suggest coordination strategy."""

    def __init__(self) -> None:
        self.complexity_indicators = {
            "high": [
                "architecture",
                "design",
                "system",
                "migrate",
                "refactor",
                "enterprise",
                "scale",
                "production",
                "deploy",
                "infrastructure",
                "security audit",
                "comprehensive",
                "full review",
            ],
            "medium": [
                "review",
                "improve",
                "optimize",
                "analyze",
                "test",
                "security",
                "performance",
                "best practices",
                "refactor",
                "debug",
            ],
            "low": [
                "fix",
                "simple",
                "quick",
                "basic",
                "help",
                "explain",
                "what is",
            ],
        }

        self.specialist_triggers = {
            "code_review": [
                "review",
                "code",
                "check",
                "improve",
                "quality",
                "bugs",
                "optimize",
                "refactor",
                "clean",
            ],
            "security": [
                "security",
                "secure",
                "vulnerability",
                "auth",
                "permission",
                "encrypt",
                "protect",
                "compliance",
                "audit",
                "threat",
            ],
            "architecture": [
                "architecture",
                "design",
                "system",
                "structure",
                "pattern",
                "scalability",
                "integration",
                "microservice",
            ],
            "testing": [
                "test",
                "testing",
                "quality",
                "qa",
                "coverage",
                "unit",
                "integration",
                "e2e",
            ],
            "devops": [
                "deploy",
                "deployment",
                "infrastructure",
                "ci/cd",
                "pipeline",
                "container",
                "kubernetes",
                "docker",
            ],
        }

    def classify(self, request: str, code: str | None = None) -> Dict[str, Any]:
        request_lower = request.lower()

        complexity = "low"
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                complexity = level
                break

        specialists_needed: List[str] = []
        for name, triggers in self.specialist_triggers.items():
            if any(trigger in request_lower for trigger in triggers):
                specialists_needed.append(name)

        coordination_type = self._determine_coordination_strategy(
            complexity, specialists_needed
        )

        return {
            "complexity": complexity,
            "specialists_needed": specialists_needed,
            "coordination_type": coordination_type,
        }

    def _determine_coordination_strategy(
        self, complexity: str, specialists: List[str]
    ) -> str:
        if len(specialists) <= 1:
            return "single"
        if complexity == "high" or len(specialists) > 3:
            return "sequential"
        return "parallel"


class MultiAgentOrchestrator:
    """Coordinates multiple specialist agents for complex analysis"""
    
    def __init__(
        self,
        mcp_client,
        child_specs: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """Initialize multi-agent orchestrator.

        Args:
            mcp_client: MCP client for agent communication
            child_specs: Optional mapping of sub-orchestrator names to their
                initialization specs. Each spec is forwarded to
                :class:`SubOrchestrator`.
        """
        self.mcp_client = mcp_client

        # Initialize specialist agents
        self.specialists = {
            "code_review": CodeReviewAgent(mcp_client),
            "security": SecurityAgent(mcp_client),
            "architecture": ArchitectureAgent(mcp_client),
            "testing": TestingAgent(mcp_client),
            "devops": DevOpsAgent(mcp_client),
        }

        # Request classifier used to determine coordination strategy
        self.request_classifier = RequestClassifier()

        self.task_history = []
        self.active_collaborations = {}

        # Lifecycle tracking for child orchestrators
        from .sub_orchestrator import SubOrchestrator

        self.child_orchestrators: Dict[str, 'SubOrchestrator'] = {}
        if child_specs:
            for name, spec in child_specs.items():
                self.child_orchestrators[name] = SubOrchestrator(
                    self.mcp_client, **spec
                )

        # Agent collaboration rules
        self.collaboration_patterns = {
            "code_review": {
                "always_collaborate": ["security"],
                "often_collaborate": ["testing"],
                "sometimes_collaborate": ["architecture", "devops"],
            },
            "security": {
                "always_collaborate": ["code_review"],
                "often_collaborate": ["architecture"],
                "sometimes_collaborate": ["testing", "devops"],
            },
            "architecture": {
                "always_collaborate": ["security"],
                "often_collaborate": ["devops"],
                "sometimes_collaborate": ["code_review", "testing"],
            },
            "testing": {
                "often_collaborate": ["code_review"],
                "sometimes_collaborate": ["security", "architecture", "devops"],
            },
            "devops": {
                "often_collaborate": ["architecture", "security"],
                "sometimes_collaborate": ["code_review", "testing"],
            },
        }

    # ------------------------------------------------------------------
    # Child orchestrator lifecycle management
    # ------------------------------------------------------------------

    def create_child_orchestrator(
        self, name: str, spec: Dict[str, Any]
    ) -> 'SubOrchestrator':
        """Create and register a child :class:`SubOrchestrator`.

        Args:
            name: Identifier for the sub-orchestrator.
            spec: Initialization specification forwarded to
                :class:`SubOrchestrator`.

        Returns:
            The created :class:`SubOrchestrator` instance.
        """
        from .sub_orchestrator import SubOrchestrator

        orchestrator = SubOrchestrator(self.mcp_client, **spec)
        self.child_orchestrators[name] = orchestrator
        return orchestrator

    def remove_child_orchestrator(self, name: str) -> bool:
        """Remove a previously registered child orchestrator."""
        return self.child_orchestrators.pop(name, None) is not None

    def list_child_orchestrators(self) -> List[str]:
        """List identifiers of active child orchestrators."""
        return list(self.child_orchestrators.keys())
    
    async def analyze_request_complexity(self, request: str, code: str = None) -> Dict[str, Any]:
        """Analyze a request using the :class:`RequestClassifier`."""
        return self.request_classifier.classify(request, code)
    
    def _determine_coordination_type(self, specialists: List[str], complexity: str) -> str:
        """Determine how specialists should be coordinated"""
        if len(specialists) <= 1:
            return "single"
        elif len(specialists) == 2 and complexity in ["low", "medium"]:
            return "parallel"
        elif complexity == "high" or len(specialists) > 3:
            return "sequential"
        else:
            return "parallel"
    
    def _determine_collaboration_depth(self, specialists: List[str]) -> str:
        """Determine depth of collaboration between specialists"""
        if len(specialists) <= 1:
            return "none"
        elif len(specialists) == 2:
            return "basic"
        elif len(specialists) <= 3:
            return "moderate"
        else:
            return "deep"
    
    async def coordinate_specialists(self, request: str, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """
        Coordinate multiple specialists to handle complex request
        
        Args:
            request: User request
            code: Optional code to analyze
            user_context: Additional user context
            
        Returns:
            Coordinated analysis results
        """
        # Analyze request complexity
        analysis = await self.analyze_request_complexity(request, code)

        # Initialize path memory and record planned specialists
        path_memory = PathMemory()
        for spec in analysis["specialists_needed"]:
            path_memory.add_step(spec)

        # Avoid previously failed paths
        if analysis["specialists_needed"] and path_memory.should_avoid():
            return self._create_error_response("Previously failed path detected", request)
        
        if not analysis["specialists_needed"]:
            return self._create_simple_response(request)
        
        logger.info(f"Coordinating {len(analysis['specialists_needed'])} specialists for {analysis['complexity']} complexity task")
        
        # Execute coordination strategy
        if analysis["coordination_type"] == "single":
            result = await self._single_specialist_analysis(request, analysis, path_memory, code, user_context)
        elif analysis["coordination_type"] == "parallel":
            result = await self._parallel_specialist_analysis(request, analysis, path_memory, code, user_context)
        else:  # sequential
            result = await self._sequential_specialist_analysis(request, analysis, path_memory, code, user_context)

        # Record outcome in path memory
        path_memory.record(result.get("type") != "error")
        return result
    
    async def _single_specialist_analysis(self, request: str, analysis: Dict, path_memory: PathMemory, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with single specialist"""
        specialist_type = analysis["specialists_needed"][0]
        specialist = self.specialists[specialist_type]
        
        # Create task with full context
        task = self._create_specialist_task(request, code, user_context)
        
        try:
            result = await specialist.process_task(task, context=None, user_context=user_context)
            path_memory.add_decisions(result.get("suggestions", [])[:3])
            
            return {
                "type": "single_specialist",
                "complexity": analysis["complexity"],
                "specialists_used": [specialist_type],
                "results": {specialist_type: result},
                "synthesized_response": result["response"],
                "confidence": result["confidence"],
                "coordination_summary": f"Analysis completed by {specialist_type} specialist"
            }
            
        except Exception as e:
            logger.error(f"Single specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    async def _parallel_specialist_analysis(self, request: str, analysis: Dict, path_memory: PathMemory, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with parallel specialist coordination"""
        specialists_needed = analysis["specialists_needed"]
        
        # Create tasks for all specialists
        task = self._create_specialist_task(request, code, user_context)
        
        # Run specialists in parallel
        tasks = []
        for specialist_type in specialists_needed:
            specialist = self.specialists[specialist_type]
            tasks.append(specialist.process_task(task, context=None, user_context=user_context))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            specialist_results = {}
            successful_results = []
            
            for i, result in enumerate(results):
                specialist_type = specialists_needed[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Specialist {specialist_type} failed: {result}")
                    specialist_results[specialist_type] = self._create_specialist_error(specialist_type, str(result))
                else:
                    specialist_results[specialist_type] = result
                    successful_results.append(result)
                    path_memory.add_decisions(result.get("suggestions", [])[:3])
            
            # Synthesize results
            synthesized_response = await self._synthesize_parallel_results(request, successful_results)
            overall_confidence = self._calculate_overall_confidence(successful_results)
            
            return {
                "type": "parallel_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": overall_confidence,
                "coordination_summary": f"Parallel analysis by {len(successful_results)} specialists"
            }
            
        except Exception as e:
            logger.error(f"Parallel specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    async def _sequential_specialist_analysis(self, request: str, analysis: Dict, path_memory: PathMemory, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with sequential specialist coordination"""
        specialists_needed = analysis["specialists_needed"]
        
        # Build context progressively
        shared_context = []
        specialist_results = {}
        
        task = self._create_specialist_task(request, code, user_context)
        
        try:
            for specialist_type in specialists_needed:
                specialist = self.specialists[specialist_type]
                
                # Process with accumulated context
                result = await specialist.process_task(task, context=shared_context, user_context=user_context)
                specialist_results[specialist_type] = result

                # Add result to shared context for next specialists
                decisions = result.get("suggestions", [])[:3]
                shared_context.append({
                    "specialist": specialist_type,
                    "key_points": decisions,
                    "confidence": result.get("confidence", 0.7),
                    "priority_issues": result.get("priority_issues", [])[:2]  # Top 2 issues
                })
                path_memory.add_decisions(decisions)
                
                logger.info(f"Completed {specialist_type} analysis, passing context to next specialist")
            
            # Final synthesis with all results
            synthesized_response = await self._synthesize_sequential_results(request, specialist_results)
            overall_confidence = self._calculate_overall_confidence(list(specialist_results.values()))
            
            return {
                "type": "sequential_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": overall_confidence,
                "coordination_summary": f"Sequential analysis with {len(specialists_needed)} specialists building on each other's insights"
            }
            
        except Exception as e:
            logger.error(f"Sequential specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    def _create_specialist_task(self, request: str, code: str = None, user_context: str = None) -> str:
        """Create comprehensive task description for specialists"""
        task_parts = [request]
        
        if code:
            task_parts.append(f"\n**Code to Analyze:**\n```\n{code}\n```")
        
        if user_context:
            task_parts.append(f"\n**Additional Context:**\n{user_context}")
        
        return "\n".join(task_parts)
    
    async def _synthesize_parallel_results(self, original_request: str, results: List[Dict]) -> str:
        """Synthesize results from parallel specialist analysis"""
        if not results:
            return "No successful analysis results to synthesize."
        
        synthesis_prompt = f"""
        **MULTI-SPECIALIST ANALYSIS SYNTHESIS**
        
        Original Request: {original_request}
        
        **Specialist Insights:**
        """
        
        for result in results:
            specialist = result.get("specialist", "unknown")
            confidence = result.get("confidence", 0.0)
            response = result.get("response", "No response")[:300]  # Limit length
            
            synthesis_prompt += f"\n**{specialist.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        synthesis_prompt += """
        
        **Your Task:**
        Synthesize these expert opinions into a comprehensive, actionable response.
        - Highlight areas of agreement and any conflicts
        - Prioritize recommendations by importance and feasibility
        - Provide a clear action plan
        - Maintain the technical accuracy of each specialist's input
        """
        
        try:
            # Use the best available model for synthesis
            synthesis_response = await self.mcp_client.generate_response(
                server="ollama",
                model="llama3.2",
                prompt=synthesis_prompt
            )
            
            return synthesis_response
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._create_fallback_synthesis(results)
    
    async def _synthesize_sequential_results(self, original_request: str, results: Dict[str, Dict]) -> str:
        """Synthesize results from sequential specialist analysis"""
        synthesis_prompt = f"""
        **SEQUENTIAL MULTI-SPECIALIST ANALYSIS SYNTHESIS**
        
        Original Request: {original_request}
        
        **Sequential Expert Analysis:**
        """
        
        for specialist_type, result in results.items():
            confidence = result.get("confidence", 0.0)
            response = result.get("response", "No response")[:300]
            
            synthesis_prompt += f"\n**{specialist_type.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        synthesis_prompt += """
        
        **Your Task:**
        Synthesize this sequential analysis into a comprehensive response.
        - Each specialist built upon previous insights
        - Integrate the progressive understanding developed
        - Provide unified recommendations that consider all perspectives
        - Create a coherent action plan
        """
        
        try:
            synthesis_response = await self.mcp_client.generate_response(
                server="ollama",
                model="llama3.2",
                prompt=synthesis_prompt
            )
            
            return synthesis_response
            
        except Exception as e:
            logger.error(f"Sequential synthesis failed: {e}")
            return self._create_fallback_synthesis(list(results.values()))
    
    def _create_fallback_synthesis(self, results: List[Dict]) -> str:
        """Create fallback synthesis when AI synthesis fails"""
        synthesis = "## Multi-Specialist Analysis Summary\n\n"
        
        for result in results:
            specialist = result.get("specialist", "unknown")
            suggestions = result.get("suggestions", [])
            priority_issues = result.get("priority_issues", [])
            
            synthesis += f"### {specialist.title()} Expert Insights:\n"
            
            if suggestions:
                synthesis += "**Key Recommendations:**\n"
                for suggestion in suggestions[:3]:
                    synthesis += f"- {suggestion}\n"
            
            if priority_issues:
                synthesis += "**Priority Issues:**\n"
                for issue in priority_issues[:2]:
                    synthesis += f"- {issue.get('description', 'Unknown issue')}\n"
            
            synthesis += "\n"
        
        synthesis += "**Next Steps:** Review each specialist's recommendations and prioritize based on your specific needs and constraints."
        
        return synthesis
    
    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        """Calculate overall confidence from multiple specialist results"""
        if not results:
            return 0.0
        
        confidences = [r.get("confidence", 0.5) for r in results]
        base_confidence = sum(confidences) / len(confidences)
        
        # Boost confidence when multiple specialists agree
        if len(results) > 1:
            base_confidence += min(0.1 * (len(results) - 1), 0.3)
        
        return min(base_confidence, 1.0)
    
    def _estimate_processing_time(self, complexity: str, num_specialists: int) -> str:
        """Estimate processing time for analysis"""
        base_times = {"low": 10, "medium": 20, "high": 40}
        estimated_seconds = base_times[complexity] * num_specialists
        
        if estimated_seconds < 60:
            return f"{estimated_seconds} seconds"
        else:
            return f"{estimated_seconds // 60} minutes"
    
    def _create_simple_response(self, request: str) -> Dict[str, Any]:
        """Create response for simple requests that don't need specialists"""
        return {
            "type": "simple",
            "complexity": "low",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"This appears to be a simple request that doesn't require specialist analysis: {request}",
            "confidence": 0.6,
            "coordination_summary": "No specialist coordination needed"
        }
    
    def _create_error_response(self, error_msg: str, request: str) -> Dict[str, Any]:
        """Create error response when coordination fails"""
        return {
            "type": "error",
            "complexity": "unknown",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"I apologize, but I encountered an error while coordinating specialist analysis for your request: {error_msg}",
            "confidence": 0.0,
            "error": True,
            "coordination_summary": f"Coordination failed: {error_msg}"
        }
    
    def _create_specialist_error(self, specialist_type: str, error_msg: str) -> Dict[str, Any]:
        """Create error result for failed specialist"""
        return {
            "specialist": specialist_type,
            "response": f"Analysis failed: {error_msg}",
            "confidence": 0.0,
            "suggestions": [],
            "priority_issues": [],
            "error": True
        }
    
    def get_specialist_status(self) -> Dict[str, Any]:
        """Get status of all specialists"""
        status = {}
        
        for name, specialist in self.specialists.items():
            status[name] = specialist.get_specialization_info()
        
        return {
            "available_specialists": list(self.specialists.keys()),
            "specialist_details": status,
            "total_tasks_completed": sum(len(s.task_history) for s in self.specialists.values()),
            "collaboration_patterns": self.collaboration_patterns
        }
    
    async def health_check_specialists(self) -> Dict[str, Any]:
        """Perform health check on all specialists"""
        health_results = {}
        
        test_task = "Health check test"
        
        for name, specialist in self.specialists.items():
            try:
                # Simple test to verify specialist is working
                result = await specialist.process_task(test_task)
                health_results[name] = {
                    "status": "healthy",
                    "confidence": result.get("confidence", 0.0),
                    "model_used": result.get("model_used", "unknown")
                }
            except Exception as e:
                health_results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        overall_health = "healthy" if all(
            h.get("status") == "healthy" for h in health_results.values()
        ) else "degraded"
        
        return {
            "overall_status": overall_health,
            "specialists": health_results,
            "timestamp": datetime.now().isoformat()
        }
# ---------------------------------------------------------------------------
# Agent specification model
# ---------------------------------------------------------------------------


AgentCallable = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class AgentSpec:
    """Specification for a single node in the workflow.

    Attributes
    ----------
    name:
        Identifier used inside the graph.
    fn:
        Callable executed when the node runs.  The callable receives and must
        return the workflow state (a mutable ``dict``).
    next:
        Optional name of the next node for a simple linear transition.
    condition:
        Optional callable returning a key from ``branches``.  When provided the
        orchestrator will create conditional edges using the mapping supplied
        in ``branches``.
    branches:
        Mapping of condition outputs to the name of the next node or ``END`` to
        finish the workflow.
    entry:
        Whether this node should be used as the entry point for the workflow.
    """

    name: str
    fn: AgentCallable
    next: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], str]] = None
    branches: Optional[Dict[str, Any]] = None
    entry: bool = False


# ---------------------------------------------------------------------------
# Dynamic orchestrator
# ---------------------------------------------------------------------------


class DynamicOrchestrator:
    """Build and execute LangGraph workflows from :class:`AgentSpec` objects."""

    def __init__(self, agent_specs: List[AgentSpec]):
        self.agent_specs = agent_specs

        # Build the StateGraph from the provided specifications
        graph = StateGraph(dict)

        for spec in agent_specs:
            graph.add_node(spec.name, spec.fn)

        # Determine entry point – default to the first spec if none marked
        entry = next((s.name for s in agent_specs if s.entry), agent_specs[0].name)
        graph.set_entry_point(entry)

        # Wire up edges
        for spec in agent_specs:
            if spec.next:
                graph.add_edge(spec.name, spec.next)

            if spec.condition and spec.branches:
                graph.add_conditional_edges(spec.name, spec.condition, spec.branches)

        # Compile to a runnable workflow
        self.workflow = graph.compile()

    # ------------------------------------------------------------------
    async def run(self, state: Dict[str, Any], resume: bool = True) -> Dict[str, Any]:
        """Execute the compiled workflow.

        Parameters
        ----------
        state:
            Initial state passed to the workflow. The state is mutated by
            nodes in the graph. The final state after execution is returned.
        resume:
            When ``True`` the orchestrator will attempt to load any previously
            saved state before executing the workflow. The state is persisted
            before and after execution to enable crash recovery.
        """

        if resume:
            saved = load_state()
            if saved is not None:
                state = saved

        logger.debug("Starting workflow with state: %s", state)
        # Persist starting state so we can recover mid-execution if needed
        save_state(state)
        result: Dict[str, Any] = {}
        try:
            result = await self.workflow.ainvoke(state)
            logger.debug("Workflow completed with state: %s", result)
            return result
        finally:
            if result:
                save_state(result)


# The specialist based ``MultiAgentOrchestrator`` defined earlier remains the
# primary export.  ``DynamicOrchestrator`` is provided for building simple
# workflow graphs but no longer replaces the specialist orchestrator.

__all__ = ["AgentSpec", "DynamicOrchestrator", "MultiAgentOrchestrator", "END"]

