#!/usr/bin/env python3
"""Reusable LangGraph workflow nodes for Jarvis AI V2.

Ported from the legacy implementation, these nodes provide the Plan → Code →
Test → Reflect cycle with conditional edges for error handling and graceful
degradation.
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated
import json
import logging
from datetime import datetime

try:
    from langgraph.graph import Graph, StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain.schema import BaseMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback when LangGraph is not available
    LANGGRAPH_AVAILABLE = False
    
    class TypedDict:
        pass
    
    def add_messages(x, y):
        return x + y
    
    class BaseMessage:
        def __init__(self, content):
            self.content = content
    
    class HumanMessage(BaseMessage):
        pass
    
    class AIMessage(BaseMessage):
        pass
    
    class StateGraph:
        def __init__(self, state_type):
            self.state_type = state_type
        
        def add_node(self, name, func):
            pass
        
        def add_edge(self, from_node, to_node):
            pass
        
        def add_conditional_edges(self, from_node, condition_func, edges):
            pass
        
        def set_entry_point(self, node):
            pass
        
        def compile(self):
            return MockGraph()
    
    class MockGraph:
        def invoke(self, state):
            return state
    
    START = "START"
    END = "END"


# Import existing Jarvis functionality
from agent.adapters.langchain_tools import create_langchain_tools, CheckOllamaStatusTool
import agent.tools as jarvis_tools
from agent.core.core import JarvisAgent


class WorkflowState(TypedDict):
    """State object for the LangGraph workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    plan: Optional[str]
    code_output: Optional[str] 
    test_results: Optional[str]
    reflection: Optional[str]
    current_step: str
    iteration_count: int
    max_iterations: int
    tools_available: bool
    error_context: Optional[str]
    user_input: str
    available_files: List[str]
    # === NEW: User Experience Enhancements (Issue #30) ===
    user_id: Optional[str]
    user_preferences: Optional[Dict[str, Any]]
    personalization_context: Optional[Dict[str, Any]]
    interaction_history: List[Dict[str, Any]]
    explanation_requests: List[str]
    learning_feedback: Optional[Dict[str, Any]]
    # === END: User Experience Enhancements ===


class JarvisWorkflowGraph:
    """LangGraph implementation of the Jarvis AI workflow."""
    
    def __init__(self, agent: JarvisAgent, max_iterations: int = 15):
        """Initialize the workflow graph."""
        self.agent = agent
        self.max_iterations = max_iterations
        self.tools = create_langchain_tools() if LANGGRAPH_AVAILABLE else []
        self.logger = logging.getLogger(__name__)
        
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
        else:
            self.graph = None
            self.logger.warning("LangGraph not available - using fallback implementation")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("code_writer", self._code_writer_node)
        workflow.add_node("debugger", self._debugger_node)
        workflow.add_node("tool_executor", self._tool_executor_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # === NEW: User Experience Enhancement Nodes (Issue #30) ===
        workflow.add_node("personalization_init", self._personalization_init_node)
        workflow.add_node("explanation_generator", self._explanation_generator_node)
        workflow.add_node("learning_feedback", self._learning_feedback_node)
        # === END: User Experience Enhancement Nodes ===
        
        # Add edges - Start with personalization initialization
        workflow.set_entry_point("personalization_init")
        workflow.add_edge("personalization_init", "planner")
        
        # Conditional edges for workflow routing
        workflow.add_conditional_edges(
            "planner",
            self._route_after_planning,
            {
                "execute": "tool_executor",
                "code": "code_writer", 
                "error": "error_handler",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "code_writer",
            self._route_after_coding,
            {
                "test": "debugger",
                "reflect": "critic",
                "error": "error_handler",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "debugger", 
            self._route_after_testing,
            {
                "fix": "code_writer",
                "reflect": "critic",
                "error": "error_handler", 
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "tool_executor",
            self._route_after_tools,
            {
                "continue": "planner",
                "reflect": "critic",
                "error": "error_handler",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "critic",
            self._route_after_reflection,
            {
                "continue": "planner",
                "end": END
            }
        )
        
        workflow.add_edge("error_handler", END)
        
        # === NEW: Add explanation generation edges ===
        # Add explanation generation after key workflow steps
        workflow.add_edge("planner", "explanation_generator")
        workflow.add_edge("code_writer", "explanation_generator") 
        workflow.add_edge("debugger", "explanation_generator")
        workflow.add_edge("critic", "explanation_generator")
        
        # Add learning feedback processing at the end
        workflow.add_edge("explanation_generator", "learning_feedback")
        workflow.add_edge("learning_feedback", END)
        # === END: Explanation generation edges ===
        
        return workflow.compile()
    
    def _planner_node(self, state: WorkflowState) -> WorkflowState:
        """Planning node - analyzes user input and creates execution plan."""
        try:
            user_msg = state["user_input"]
            available_files = state["available_files"]
            
            # Use existing agent planning capability
            plan = self.agent.parse_natural_language(user_msg, available_files)
            
            state["plan"] = json.dumps(plan, indent=2)
            state["current_step"] = "planning_complete"
            state["messages"].append(AIMessage(content=f"Created plan with {len(plan)} steps"))
            
            return state
            
        except Exception as e:
            state["error_context"] = f"Planning error: {str(e)}"
            state["current_step"] = "error"
            return state
    
    def _code_writer_node(self, state: WorkflowState) -> WorkflowState:
        """Code writing node - generates or modifies code based on plan."""
        try:
            # For now, use existing tool execution for code-related tasks
            plan = json.loads(state["plan"]) if state["plan"] else []
            
            # Find code-related steps
            code_steps = [step for step in plan if step.get("tool") in ["file_update", "code_review"]]
            
            if code_steps:
                results = []
                for step in code_steps:
                    result = jarvis_tools.run_tool(step)
                    results.append(result)
                
                state["code_output"] = json.dumps(results, indent=2)
                state["current_step"] = "code_complete"
            else:
                state["code_output"] = "No code steps in plan"
                state["current_step"] = "code_skipped"
            
            state["messages"].append(AIMessage(content="Code writing completed"))
            return state
            
        except Exception as e:
            state["error_context"] = f"Code writing error: {str(e)}"
            state["current_step"] = "error"
            return state
    
    def _debugger_node(self, state: WorkflowState) -> WorkflowState:
        """Debugging node - runs tests and checks for issues."""
        try:
            # Check Ollama status as part of system monitoring
            ollama_tool = CheckOllamaStatusTool()
            ollama_status = ollama_tool._run()
            
            # Run any test-related tools
            plan = json.loads(state["plan"]) if state["plan"] else []
            test_steps = [step for step in plan if "test" in step.get("tool", "").lower()]
            
            test_results = {
                "ollama_status": ollama_status,
                "test_steps": len(test_steps),
                "timestamp": datetime.now().isoformat()
            }
            
            if test_steps:
                for step in test_steps:
                    result = jarvis_tools.run_tool(step)
                    test_results[f"test_{step['tool']}"] = result
            
            state["test_results"] = json.dumps(test_results, indent=2)
            state["current_step"] = "testing_complete"
            state["messages"].append(AIMessage(content="Testing and debugging completed"))
            
            return state
            
        except Exception as e:
            state["error_context"] = f"Testing error: {str(e)}"
            state["current_step"] = "error"
            return state
    
    def _tool_executor_node(self, state: WorkflowState) -> WorkflowState:
        """Tool execution node - executes planned tools."""
        try:
            plan = json.loads(state["plan"]) if state["plan"] else []
            
            if not plan:
                state["current_step"] = "no_tools"
                return state
            
            # Execute plan using existing agent functionality
            results = self.agent.execute_plan(plan)
            
            state["code_output"] = json.dumps(results, indent=2)
            state["current_step"] = "tools_complete"
            state["messages"].append(AIMessage(content=f"Executed {len(results)} tool steps"))
            
            return state
            
        except Exception as e:
            state["error_context"] = f"Tool execution error: {str(e)}"
            state["current_step"] = "error"
            return state
    
    def _critic_node(self, state: WorkflowState) -> WorkflowState:
        """Critic/Reflection node - analyzes results and provides rationale."""
        try:
            # Analyze the current state and provide reflection
            reflection_data = {
                "iteration": state["iteration_count"],
                "current_step": state["current_step"],
                "plan_summary": "Plan executed" if state["plan"] else "No plan",
                "code_status": "Code generated" if state["code_output"] else "No code output",
                "test_status": "Tests run" if state["test_results"] else "No tests",
                "success_indicators": [],
                "concerns": [],
                "recommendations": []
            }
            
            # Add success indicators
            if state["plan"]:
                reflection_data["success_indicators"].append("Valid plan created")
            if state["code_output"]:
                reflection_data["success_indicators"].append("Code/tools executed")
            if state["test_results"]:
                reflection_data["success_indicators"].append("System checks completed")
            
            # Add concerns
            if state["error_context"]:
                reflection_data["concerns"].append(f"Error occurred: {state['error_context']}")
            if state["iteration_count"] > 5:
                reflection_data["concerns"].append("Multiple iterations - may indicate complexity")
            
            # Add recommendations
            if state["iteration_count"] < state["max_iterations"]:
                reflection_data["recommendations"].append("Can continue with additional iterations if needed")
            else:
                reflection_data["recommendations"].append("Reached maximum iterations - should conclude")
            
            state["reflection"] = json.dumps(reflection_data, indent=2)
            state["current_step"] = "reflection_complete"
            state["messages"].append(AIMessage(content="Reflection and analysis completed"))
            
            return state
            
        except Exception as e:
            state["error_context"] = f"Reflection error: {str(e)}"
            state["current_step"] = "error"
            return state
    
    def _error_handler_node(self, state: WorkflowState) -> WorkflowState:
        """Error handling node - graceful degradation."""
        try:
            error_msg = state.get("error_context", "Unknown error")
            
            # Log the error
            self.logger.error(f"Workflow error: {error_msg}")
            
            # Attempt graceful degradation
            fallback_result = {
                "error": error_msg,
                "fallback_attempted": True,
                "timestamp": datetime.now().isoformat(),
                "suggestion": "Try a simpler request or check system status"
            }
            
            # Try to provide some basic functionality
            if "ollama" in error_msg.lower():
                fallback_result["suggestion"] = "Ollama service may be down. Check connection."
            elif "tool" in error_msg.lower():
                fallback_result["suggestion"] = "Tool execution failed. Try a different approach."
            
            state["reflection"] = json.dumps(fallback_result, indent=2)
            state["current_step"] = "error_handled"
            state["messages"].append(AIMessage(content=f"Error handled: {error_msg}"))
            
            return state
            
        except Exception as e:
            # Last resort fallback
            state["reflection"] = f"Critical error in error handler: {str(e)}"
            state["current_step"] = "critical_error"
            return state
    
    # === NEW: User Experience Enhancement Nodes (Issue #30) ===
    
    def _personalization_init_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize personalization context for the workflow."""
        try:
            # Import personalization memory
            from agent.adapters.personalization_memory import get_user_personalization_memory
            
            user_id = state.get("user_id", "anonymous")
            user_prefs = state.get("user_preferences", {})
            
            # Get user's personalization memory
            user_memory = get_user_personalization_memory(user_id)
            personalization_context = user_memory.get_personalized_context("workflow")
            
            # Update state with personalization data
            state["personalization_context"] = personalization_context
            state["interaction_history"] = personalization_context.get("recent_preferences", [])
            
            # Add personalized system message
            learning_rate = user_prefs.get("learning_rate", "Moderate")
            domain = user_prefs.get("domain_specialization", "General")
            style = user_prefs.get("communication_style", "Professional")
            
            personalized_msg = (
                f"User Profile - Learning Rate: {learning_rate}, "
                f"Domain: {domain}, Style: {style}. "
                f"Adapt responses accordingly."
            )
            
            state["messages"].append(SystemMessage(content=personalized_msg))
            
            return state
            
        except Exception as e:
            # Don't fail the workflow if personalization fails
            state["personalization_context"] = {}
            state["interaction_history"] = []
            return state
    
    def _explanation_generator_node(self, state: WorkflowState) -> WorkflowState:
        """Generate explanations for workflow steps based on user preferences."""
        try:
            user_prefs = state.get("user_preferences", {})
            
            # Check if explanations are enabled
            if not user_prefs.get("show_code_explanations", True):
                return state
            
            # Generate explanations for each workflow step
            explanations = []
            current_step = state.get("current_step", "unknown")
            
            explanation_templates = {
                "planning": "I'm analyzing your request and creating a step-by-step plan.",
                "coding": "I'm implementing the solution based on the plan.",
                "testing": "I'm running tests to verify the implementation works correctly.",
                "reflection": "I'm reviewing the results and learning from the outcome.",
                "tool_execution": "I'm using specialized tools to accomplish specific tasks.",
                "error": "I encountered an issue and I'm working on a solution."
            }
            
            explanation = explanation_templates.get(current_step, "I'm processing your request.")
            
            # Personalize explanation based on communication style
            style = user_prefs.get("communication_style", "Professional")
            domain = user_prefs.get("domain_specialization", "General")
            
            if style == "Casual":
                explanation = f"Hey! {explanation.lower()}"
            elif style == "Tutorial":
                explanation = f"Step {state.get('iteration_count', 1)}: {explanation}"
            elif style == "Detailed":
                explanation = f"{explanation} This involves {domain.lower()} concepts and practices."
            
            explanations.append({
                "step": current_step,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat()
            })
            
            # Store explanations in state
            if "explanation_requests" not in state:
                state["explanation_requests"] = []
            state["explanation_requests"].extend(explanations)
            
            return state
            
        except Exception as e:
            # Don't fail workflow if explanation generation fails
            return state
    
    def _learning_feedback_node(self, state: WorkflowState) -> WorkflowState:
        """Process learning feedback and update personalization."""
        try:
            from agent.adapters.personalization_memory import get_user_personalization_memory
            
            user_id = state.get("user_id", "anonymous")
            user_prefs = state.get("user_preferences", {})
            
            # Check if there's feedback to process
            feedback = state.get("learning_feedback")
            if not feedback:
                return state
            
            # Get user's personalization memory
            user_memory = get_user_personalization_memory(user_id)
            
            # Record the interaction for learning
            context = {
                "workflow_step": state.get("current_step", "unknown"),
                "domain": user_prefs.get("domain_specialization", "General"),
                "pattern": feedback.get("pattern", "workflow_completion"),
                "description": f"Workflow execution with {state.get('iteration_count', 1)} iterations"
            }
            
            user_memory.record_interaction(
                interaction_type="workflow",
                context=context,
                feedback=feedback.get("positive", True),
                learning_rate=user_prefs.get("learning_rate", "Moderate")
            )
            
            # Clear processed feedback
            state["learning_feedback"] = None
            
            return state
            
        except Exception as e:
            # Don't fail workflow if learning feedback fails
            return state
    
    # === END: User Experience Enhancement Nodes ===
    
    def _route_after_planning(self, state: WorkflowState) -> str:
        """Route workflow after planning step."""
        if state["current_step"] == "error":
            return "error"
        
        plan = json.loads(state["plan"]) if state["plan"] else []
        if not plan:
            return "end"
        
        # Check if plan contains code-related steps
        has_code_steps = any(step.get("tool") in ["file_update", "code_review"] for step in plan)
        if has_code_steps:
            return "code"
        
        return "execute"
    
    def _route_after_coding(self, state: WorkflowState) -> str:
        """Route workflow after code writing."""
        if state["current_step"] == "error":
            return "error"
        
        if state["current_step"] == "code_skipped":
            return "reflect"
        
        return "test"
    
    def _route_after_testing(self, state: WorkflowState) -> str:
        """Route workflow after testing."""
        if state["current_step"] == "error":
            return "error"
        
        # For now, always go to reflection after testing
        return "reflect"
    
    def _route_after_tools(self, state: WorkflowState) -> str:
        """Route workflow after tool execution."""
        if state["current_step"] == "error":
            return "error"
        
        if state["iteration_count"] >= state["max_iterations"]:
            return "end"
        
        return "reflect"
    
    def _route_after_reflection(self, state: WorkflowState) -> str:
        """Route workflow after reflection."""
        if state["iteration_count"] >= state["max_iterations"]:
            return "end"
        
        reflection = json.loads(state["reflection"]) if state["reflection"] else {}
        
        # Check if there are significant concerns that need addressing
        concerns = reflection.get("concerns", [])
        if concerns and state["iteration_count"] < state["max_iterations"] - 2:
            return "continue"
        
        return "end"
    
    def execute_workflow(self, user_input: str, available_files: List[str] = None) -> Dict[str, Any]:
        """Execute the complete workflow."""
        
        if not LANGGRAPH_AVAILABLE:
            # Fallback to existing agent execution
            self.logger.warning("LangGraph not available, using fallback execution")
            plan = self.agent.parse_natural_language(user_input, available_files or [])
            results = self.agent.execute_plan(plan)
            return {
                "plan": plan,
                "results": results,
                "reflection": "Executed using fallback agent (LangGraph not available)",
                "success": True
            }
        
        # Initialize state
        initial_state = WorkflowState(
            messages=[HumanMessage(content=user_input)],
            plan=None,
            code_output=None,
            test_results=None,
            reflection=None,
            current_step="start",
            iteration_count=0,
            max_iterations=self.max_iterations,
            tools_available=bool(self.tools),
            error_context=None,
            user_input=user_input,
            available_files=available_files or []
        )
        
        try:
            # Execute the graph
            final_state = self.graph.invoke(initial_state)
            
            return {
                "plan": final_state.get("plan"),
                "code_output": final_state.get("code_output"),
                "test_results": final_state.get("test_results"),
                "reflection": final_state.get("reflection"),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "success": final_state.get("current_step") != "critical_error",
                "iterations": final_state.get("iteration_count", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            return {
                "error": str(e),
                "reflection": "Workflow execution failed",
                "success": False
            }


def create_jarvis_workflow(agent: JarvisAgent, max_iterations: int = 15) -> JarvisWorkflowGraph:
    """Create a new Jarvis workflow graph."""
    return JarvisWorkflowGraph(agent, max_iterations)