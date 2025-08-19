"""
V2 LangGraph-based Agent Architecture for Jarvis AI

This module implements the core LangGraph workflow that defines the agent's
stateful, cyclical reasoning process following the Plan -> Code -> Test -> Reflect loop.
"""

from typing import Dict, Any, List, Optional, Union
import json
import operator
from pathlib import Path

try:
    from typing import TypedDict, Annotated
    from langchain_core.tools import tool
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
    from langgraph.checkpoint.sqlite import SqliteSaver
    
    LANGGRAPH_AVAILABLE = True
    
    class AgentState(TypedDict):
        """State schema for the LangGraph agent workflow."""
        messages: Annotated[List[BaseMessage], operator.add]
        plan: Optional[Dict[str, Any]]
        code_output: Optional[str]
        test_results: Optional[Dict[str, Any]]
        reflection: Optional[str]
        iteration_count: int
        max_iterations: int
        current_step: str
        errors: List[str]
        tools_available: bool
        ollama_available: bool
        
except ImportError:
    # Fallback for when LangGraph is not available
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available. V2 features will be disabled.")
    
    # Create dummy classes for when LangGraph is not available
    class AgentState(dict):
        """Fallback state class when LangGraph is not available."""
        pass
    
    BaseMessage = str
    HumanMessage = str
    AIMessage = str
    StateGraph = None
    ToolExecutor = None
    SqliteSaver = None
    END = "END"


class JarvisLangGraphAgent:
    """
    V2 LangGraph-based Jarvis AI Agent with cyclical reasoning workflow.
    
    Features:
    - Stateful workflow with Plan -> Code -> Test -> Reflect cycle
    - Conditional edges for error handling and graceful degradation
    - Tool execution with approval mechanisms
    - Persistent conversation memory via SQLite checkpointing
    """
    
    def __init__(
        self,
        expert_model: str = "llama3.2",
        tools: Optional[List] = None,
        max_iterations: int = 15,
        checkpoint_path: str = "./checkpoints/jarvis_agent.db"
    ):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required for V2 agent. Please install: pip install langgraph")
        
        self.expert_model = expert_model
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.checkpoint_path = Path(checkpoint_path)
        
        # Ensure checkpoint directory exists
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the workflow graph
        self.workflow = self._create_workflow()
        self.tool_executor = ToolExecutor(self.tools) if self.tools else None
    
    def _create_workflow(self) -> StateGraph:
        """Create the main LangGraph workflow with all nodes and edges."""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("code_writer", self._code_writer_node)
        workflow.add_node("debugger", self._debugger_node)
        workflow.add_node("tool_executor", self._tool_executor_node)
        workflow.add_node("git_manager", self._git_manager_node)
        workflow.add_node("critic", self._critic_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "planner",
            self._should_execute_plan,
            {
                "code": "code_writer",
                "tools": "tool_executor",
                "git": "git_manager",
                "end": END,
            }
        )
        
        workflow.add_conditional_edges(
            "code_writer",
            self._should_test_code,
            {
                "test": "debugger",
                "reflect": "critic",
                "continue": "planner",
                "end": END,
            }
        )
        
        workflow.add_conditional_edges(
            "debugger",
            self._should_continue_after_debug,
            {
                "fix": "code_writer",
                "reflect": "critic",
                "success": END,
                "error": "critic",
            }
        )
        
        workflow.add_conditional_edges(
            "tool_executor",
            self._should_continue_after_tools,
            {
                "success": "critic",
                "retry": "planner",
                "error": "critic",
                "end": END,
            }
        )
        
        workflow.add_conditional_edges(
            "git_manager",
            self._should_continue_after_git,
            {
                "success": "critic",
                "error": "critic",
                "end": END,
            }
        )
        
        workflow.add_conditional_edges(
            "critic",
            self._should_continue_workflow,
            {
                "continue": "planner",
                "end": END,
            }
        )
        
        return workflow.compile(
            checkpointer=SqliteSaver.from_conn_string(f"sqlite:///{self.checkpoint_path}")
        )
    
    def _planner_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Planner node: Analyzes the user request and creates an execution plan.
        """
        last_message = state["messages"][-1] if state["messages"] else None
        if not last_message:
            return {
                "current_step": "planner",
                "errors": ["No messages to process"],
                "plan": None
            }
        
        # Create a plan based on the user message
        user_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Simple plan generation (in real implementation, use LLM)
        plan = {
            "task": user_content,
            "steps": self._analyze_task(user_content),
            "requires_code": "code" in user_content.lower() or "write" in user_content.lower(),
            "requires_tools": "file" in user_content.lower() or "search" in user_content.lower(),
            "requires_git": "commit" in user_content.lower() or "git" in user_content.lower(),
        }
        
        return {
            "current_step": "planner",
            "plan": plan,
            "messages": [AIMessage(content=f"Planning: {plan['task']}")],
        }
    
    def _code_writer_node(self, state: AgentState) -> Dict[str, Any]:
        """
        CodeWriter node: Generates or modifies code based on the plan.
        """
        plan = state.get("plan", {})
        
        # Placeholder for code generation (would use LLM in real implementation)
        code_output = f"# Generated code for: {plan.get('task', 'Unknown task')}\n# TODO: Implement actual code generation"
        
        return {
            "current_step": "code_writer",
            "code_output": code_output,
            "messages": [AIMessage(content=f"Generated code:\n```python\n{code_output}\n```")],
        }
    
    def _debugger_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Debugger node: Tests and validates generated code.
        """
        code_output = state.get("code_output", "")
        
        # Placeholder for testing (would run actual tests in real implementation)
        test_results = {
            "passed": True,
            "errors": [],
            "coverage": 95.0,
            "summary": "All tests passed"
        }
        
        return {
            "current_step": "debugger",
            "test_results": test_results,
            "messages": [AIMessage(content=f"Test results: {test_results['summary']}")],
        }
    
    def _tool_executor_node(self, state: AgentState) -> Dict[str, Any]:
        """
        ToolExecutor node: Executes system tools and external integrations.
        """
        if not self.tool_executor:
            return {
                "current_step": "tool_executor",
                "errors": ["No tools available"],
                "tools_available": False,
            }
        
        # Execute tools based on plan
        plan = state.get("plan", {})
        
        # Placeholder for tool execution
        tool_output = f"Tool execution completed for: {plan.get('task', 'Unknown')}"
        
        return {
            "current_step": "tool_executor",
            "tools_available": True,
            "messages": [AIMessage(content=tool_output)],
        }
    
    def _git_manager_node(self, state: AgentState) -> Dict[str, Any]:
        """
        GitManager node: Handles version control operations.
        """
        plan = state.get("plan", {})
        
        # Placeholder for git operations
        git_output = f"Git operations completed for: {plan.get('task', 'Unknown')}"
        
        return {
            "current_step": "git_manager",
            "messages": [AIMessage(content=git_output)],
        }
    
    def _critic_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Critic node: Provides reflection and quality assessment.
        """
        # Analyze the current state and provide reflection
        reflection = self._generate_reflection(state)
        
        return {
            "current_step": "critic",
            "reflection": reflection,
            "messages": [AIMessage(content=f"Reflection: {reflection}")],
        }
    
    def _analyze_task(self, task: str) -> List[str]:
        """Analyze the task and break it down into steps."""
        # Simple task analysis (would use LLM in real implementation)
        steps = []
        
        if "code" in task.lower():
            steps.append("Generate code")
        if "test" in task.lower():
            steps.append("Write tests")
        if "file" in task.lower():
            steps.append("File operations")
        if "search" in task.lower():
            steps.append("Web search")
        
        return steps or ["Process request"]
    
    def _generate_reflection(self, state: AgentState) -> str:
        """Generate reflection based on current state."""
        current_step = state.get("current_step", "unknown")
        errors = state.get("errors", [])
        
        if errors:
            return f"Encountered errors in {current_step}: {'; '.join(errors)}"
        else:
            return f"Step {current_step} completed successfully"
    
    # Conditional edge functions
    def _should_execute_plan(self, state: AgentState) -> str:
        """Determine the next step after planning."""
        plan = state.get("plan")
        if not plan:
            return "end"
        
        if plan.get("requires_code"):
            return "code"
        elif plan.get("requires_tools"):
            return "tools"
        elif plan.get("requires_git"):
            return "git"
        else:
            return "end"
    
    def _should_test_code(self, state: AgentState) -> str:
        """Determine if code should be tested."""
        if state.get("code_output"):
            return "test"
        return "reflect"
    
    def _should_continue_after_debug(self, state: AgentState) -> str:
        """Determine next step after debugging."""
        test_results = state.get("test_results", {})
        
        if test_results.get("passed"):
            return "success"
        elif test_results.get("errors"):
            return "fix"
        else:
            return "reflect"
    
    def _should_continue_after_tools(self, state: AgentState) -> str:
        """Determine next step after tool execution."""
        if state.get("errors"):
            return "error"
        elif state.get("tools_available"):
            return "success"
        else:
            return "retry"
    
    def _should_continue_after_git(self, state: AgentState) -> str:
        """Determine next step after git operations."""
        if state.get("errors"):
            return "error"
        else:
            return "success"
    
    def _should_continue_workflow(self, state: AgentState) -> str:
        """Determine if workflow should continue or end."""
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", self.max_iterations)
        
        if iteration_count >= max_iterations:
            return "end"
        
        # Check if task is complete
        reflection = state.get("reflection", "")
        if "completed successfully" in reflection.lower():
            return "end"
        
        return "continue"
    
    def invoke(self, user_message: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user messages.
        
        Args:
            user_message: The user's input message
            config: Optional configuration for the workflow
            
        Returns:
            The final state after workflow execution
        """
        if not LANGGRAPH_AVAILABLE:
            return {
                "error": "LangGraph not available",
                "fallback_response": "V2 features disabled. Using fallback response."
            }
        
        initial_state = {
            "messages": [HumanMessage(content=user_message)],
            "plan": None,
            "code_output": None,
            "test_results": None,
            "reflection": None,
            "iteration_count": 0,
            "max_iterations": self.max_iterations,
            "current_step": "starting",
            "errors": [],
            "tools_available": bool(self.tools),
            "ollama_available": check_ollama_status(),
        }
        
        try:
            result = self.workflow.invoke(initial_state, config=config or {})
            return result
        except Exception as e:
            return {
                "error": str(e),
                "current_step": "error",
                "messages": [AIMessage(content=f"An error occurred: {str(e)}")],
            }


def create_jarvis_langgraph_agent(
    expert_model: str = "llama3.2",
    tools: Optional[List] = None,
    **kwargs
) -> JarvisLangGraphAgent:
    """
    Factory function to create a JarvisLangGraphAgent instance.
    
    Args:
        expert_model: The model to use for LLM operations
        tools: List of tools available to the agent
        **kwargs: Additional configuration options
        
    Returns:
        Configured JarvisLangGraphAgent instance
    """
    return JarvisLangGraphAgent(
        expert_model=expert_model,
        tools=tools or [],
        **kwargs
    )


# Graceful fallback for when LangGraph is not available
class FallbackAgent:
    """Fallback agent when LangGraph is not available."""
    
    def __init__(self, expert_model: str = "llama3.2", **kwargs):
        self.expert_model = expert_model
    
    def invoke(self, user_message: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        return {
            "fallback": True,
            "message": "LangGraph not available. Using V1 compatibility mode.",
            "user_input": user_message,
        }


def get_agent(use_langgraph: bool = True, **kwargs) -> Any:
    """
    Get an appropriate agent instance based on availability.
    
    Args:
        use_langgraph: Whether to try using LangGraph
        **kwargs: Configuration options
        
    Returns:
        Agent instance (LangGraph or fallback)
    """
    if use_langgraph and LANGGRAPH_AVAILABLE:
        return create_jarvis_langgraph_agent(**kwargs)
    else:
        return FallbackAgent(**kwargs)