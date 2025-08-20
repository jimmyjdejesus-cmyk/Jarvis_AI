#!/usr/bin/env python3
"""
Enhanced Plugin Workflow Integration for Jarvis AI

This module provides enhanced LangGraph workflow integration specifically for
the plugin system, enabling complex multi-step workflows and state management.
"""

from typing import TypedDict, List, Dict, Any, Optional, Union
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, add_messages
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback when LangGraph is not available
    class StateGraph:
        def __init__(self, state_schema):
            self.nodes = {}
            self.edges = []
            self.entry_point = None
        
        def add_node(self, name, func):
            self.nodes[name] = func
        
        def add_edge(self, from_node, to_node):
            self.edges.append((from_node, to_node))
        
        def add_conditional_edges(self, from_node, condition_func, edges):
            pass
        
        def set_entry_point(self, node):
            self.entry_point = node
        
        def compile(self, **kwargs):
            return MockCompiledGraph(self)
    
    class MockCompiledGraph:
        def __init__(self, graph):
            self.graph = graph
        
        def invoke(self, state):
            return {"result": "LangGraph not available - mock execution"}
    
    def add_messages(messages, new_messages=None):
        if new_messages:
            return messages + new_messages
        return messages
    
    class MemorySaver:
        def __init__(self):
            pass
    
    class BaseMessage:
        def __init__(self, content=""):
            self.content = content
    
    class HumanMessage(BaseMessage):
        pass
    
    class AIMessage(BaseMessage):
        pass
    
    LANGGRAPH_AVAILABLE = False

from agent.adapters.plugin_base import PluginAction, PluginResult
from agent.adapters.plugin_registry import plugin_manager


# Workflow State Types
class PluginWorkflowState(TypedDict):
    """State for plugin execution workflows."""
    command: str
    context: Dict[str, Any]
    messages: List[BaseMessage]
    current_step: str
    results: List[Dict[str, Any]]
    plugin_outputs: Dict[str, Any]
    approval_required: List[str]
    approved_actions: List[str]
    workflow_metadata: Dict[str, Any]


class MultiStepWorkflowState(TypedDict):
    """State for multi-step plugin workflows."""
    original_command: str
    parsed_steps: List[Dict[str, Any]]
    current_step_index: int
    step_results: List[PluginResult]
    workflow_context: Dict[str, Any]
    continue_on_failure: bool
    rollback_actions: List[Dict[str, Any]]


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    plugin_name: str
    action_name: str
    args: Dict[str, Any]
    requires_approval: bool = False
    depends_on: List[str] = None
    timeout: int = 300
    retry_count: int = 0
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class PluginWorkflowOrchestrator:
    """Orchestrates plugin execution using LangGraph workflows."""
    
    def __init__(self):
        self.memory = MemorySaver() if LANGGRAPH_AVAILABLE else None
    
    def create_simple_plugin_workflow(self) -> StateGraph:
        """Create a simple plugin execution workflow."""
        
        def parse_command_node(state: PluginWorkflowState) -> PluginWorkflowState:
            """Parse command and identify applicable plugins."""
            command = state["command"]
            context = state["context"]
            
            logger.info(f"Parsing command: {command}")
            
            # Find plugins that can handle this command
            matching_plugins = plugin_manager.registry.find_plugins_for_command(command, context)
            
            results = []
            for plugin in matching_plugins:
                try:
                    action = plugin.parse_command(command, context)
                    if action:
                        results.append({
                            "plugin_name": plugin.metadata.name,
                            "action": asdict(action),
                            "confidence": self._calculate_confidence(plugin, command)
                        })
                except Exception as e:
                    logger.warning(f"Error parsing command with plugin {plugin.metadata.name}: {e}")
            
            # Sort by confidence
            results.sort(key=lambda x: x["confidence"], reverse=True)
            
            state["results"] = results
            state["current_step"] = "command_parsed"
            state["messages"] = add_messages(state["messages"], [
                AIMessage(content=f"Found {len(results)} plugins that can handle this command")
            ])
            
            return state
        
        def approval_node(state: PluginWorkflowState) -> PluginWorkflowState:
            """Handle approval for actions that require it."""
            approval_required = []
            
            for result in state["results"]:
                action = result["action"]
                if action.get("requires_approval", False):
                    approval_required.append(result["plugin_name"])
            
            state["approval_required"] = approval_required
            state["current_step"] = "waiting_for_approval"
            
            if approval_required:
                state["messages"] = add_messages(state["messages"], [
                    AIMessage(content=f"The following actions require approval: {', '.join(approval_required)}")
                ])
            else:
                state["approved_actions"] = [r["plugin_name"] for r in state["results"]]
                state["current_step"] = "approved"
            
            return state
        
        def execution_node(state: PluginWorkflowState) -> PluginWorkflowState:
            """Execute approved plugin actions."""
            plugin_outputs = {}
            
            for result in state["results"]:
                plugin_name = result["plugin_name"]
                
                # Skip if not approved
                if plugin_name not in state.get("approved_actions", []):
                    continue
                
                try:
                    # Get the plugin and execute the action
                    plugin = plugin_manager.registry.get_plugin(plugin_name)
                    if plugin:
                        action_dict = result["action"]
                        action = PluginAction(
                            name=action_dict["name"],
                            description=action_dict["description"],
                            args=action_dict["args"],
                            preview=action_dict.get("preview", ""),
                            requires_approval=action_dict.get("requires_approval", False)
                        )
                        
                        execution_result = plugin.execute_action(action, state["context"])
                        plugin_outputs[plugin_name] = {
                            "success": execution_result.success,
                            "output": execution_result.output,
                            "error": execution_result.error
                        }
                        
                        logger.info(f"Executed {plugin_name}: success={execution_result.success}")
                        
                except Exception as e:
                    logger.error(f"Error executing plugin {plugin_name}: {e}")
                    plugin_outputs[plugin_name] = {
                        "success": False,
                        "output": None,
                        "error": str(e)
                    }
            
            state["plugin_outputs"] = plugin_outputs
            state["current_step"] = "completed"
            
            # Create summary message
            successful_plugins = [name for name, output in plugin_outputs.items() if output["success"]]
            failed_plugins = [name for name, output in plugin_outputs.items() if not output["success"]]
            
            summary_parts = []
            if successful_plugins:
                summary_parts.append(f"Successfully executed: {', '.join(successful_plugins)}")
            if failed_plugins:
                summary_parts.append(f"Failed to execute: {', '.join(failed_plugins)}")
            
            summary = "; ".join(summary_parts) if summary_parts else "No plugins were executed"
            
            state["messages"] = add_messages(state["messages"], [
                AIMessage(content=f"Execution completed. {summary}")
            ])
            
            return state
        
        def should_continue_to_approval(state: PluginWorkflowState) -> str:
            """Decide whether to go to approval or directly to execution."""
            if not state["results"]:
                return "end"
            
            # Check if any actions require approval
            requires_approval = any(
                result["action"].get("requires_approval", False) 
                for result in state["results"]
            )
            
            return "approval" if requires_approval else "execution"
        
        def should_continue_to_execution(state: PluginWorkflowState) -> str:
            """Decide whether to proceed to execution."""
            if state["current_step"] == "approved" or state.get("approved_actions"):
                return "execution"
            return "end"
        
        # Create the workflow graph
        workflow = StateGraph(PluginWorkflowState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("approval", approval_node)
        workflow.add_node("execution", execution_node)
        
        # Add edges
        workflow.add_conditional_edges(
            "parse_command",
            should_continue_to_approval,
            {
                "approval": "approval",
                "execution": "execution",
                "end": "__end__"
            }
        )
        
        workflow.add_conditional_edges(
            "approval",
            should_continue_to_execution,
            {
                "execution": "execution",
                "end": "__end__"
            }
        )
        
        workflow.add_edge("execution", "__end__")
        workflow.set_entry_point("parse_command")
        
        return workflow
    
    def create_multi_step_workflow(self) -> StateGraph:
        """Create a workflow for executing multiple plugin steps in sequence."""
        
        def parse_multi_step_command(state: MultiStepWorkflowState) -> MultiStepWorkflowState:
            """Parse a command that contains multiple steps."""
            command = state["original_command"]
            
            # Simple parsing for commands with "then", "and", etc.
            separators = [" then ", " and ", " after ", " next "]
            steps = [command]
            
            for separator in separators:
                if separator in command.lower():
                    steps = command.lower().split(separator)
                    break
            
            parsed_steps = []
            for i, step in enumerate(steps):
                step = step.strip()
                if step:
                    parsed_steps.append({
                        "step_index": i,
                        "command": step,
                        "status": "pending"
                    })
            
            state["parsed_steps"] = parsed_steps
            state["current_step_index"] = 0
            state["step_results"] = []
            
            return state
        
        def execute_current_step(state: MultiStepWorkflowState) -> MultiStepWorkflowState:
            """Execute the current step in the workflow."""
            if state["current_step_index"] >= len(state["parsed_steps"]):
                return state
            
            current_step = state["parsed_steps"][state["current_step_index"]]
            step_command = current_step["command"]
            
            # Use the simple workflow to execute this step
            simple_workflow = self.create_simple_plugin_workflow().compile()
            
            step_state = {
                "command": step_command,
                "context": state["workflow_context"],
                "messages": [],
                "current_step": "initialized",
                "results": [],
                "plugin_outputs": {},
                "approval_required": [],
                "approved_actions": [],
                "workflow_metadata": {}
            }
            
            try:
                result = simple_workflow.invoke(step_state)
                step_result = PluginResult(
                    success=True,
                    output=result.get("plugin_outputs", {}),
                    error=None
                )
                
                # Update step status
                current_step["status"] = "completed"
                
            except Exception as e:
                logger.error(f"Error executing step {state['current_step_index']}: {e}")
                step_result = PluginResult(
                    success=False,
                    output=None,
                    error=str(e)
                )
                
                current_step["status"] = "failed"
                
                if not state["continue_on_failure"]:
                    return state
            
            state["step_results"].append(step_result)
            state["current_step_index"] += 1
            
            return state
        
        def should_continue_steps(state: MultiStepWorkflowState) -> str:
            """Decide whether to continue with more steps."""
            if state["current_step_index"] >= len(state["parsed_steps"]):
                return "end"
            
            # Check if we should stop due to failure
            if state["step_results"] and not state["step_results"][-1].success:
                if not state["continue_on_failure"]:
                    return "end"
            
            return "execute_step"
        
        # Create the workflow graph
        workflow = StateGraph(MultiStepWorkflowState)
        
        workflow.add_node("parse_steps", parse_multi_step_command)
        workflow.add_node("execute_step", execute_current_step)
        
        workflow.add_edge("parse_steps", "execute_step")
        workflow.add_conditional_edges(
            "execute_step",
            should_continue_steps,
            {
                "execute_step": "execute_step",
                "end": "__end__"
            }
        )
        
        workflow.set_entry_point("parse_steps")
        
        return workflow
    
    def _calculate_confidence(self, plugin, command: str) -> float:
        """Calculate confidence score for plugin handling a command."""
        confidence = 0.0
        
        # Check trigger phrase matches
        for trigger in plugin.metadata.triggers:
            if trigger.lower() in command.lower():
                confidence += 0.8
                break
        
        # Check if plugin says it can handle the command
        try:
            if plugin.can_handle(command):
                confidence += 0.5
        except Exception:
            pass
        
        # Boost confidence for exact matches
        if any(trigger.lower() == command.lower() for trigger in plugin.metadata.triggers):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def execute_workflow(self, command: str, context: Dict[str, Any] = None, 
                        workflow_type: str = "simple") -> Dict[str, Any]:
        """Execute a workflow for the given command."""
        
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph not available, falling back to direct plugin execution")
            return self._fallback_execution(command, context)
        
        try:
            if workflow_type == "simple":
                workflow = self.create_simple_plugin_workflow().compile(checkpointer=self.memory)
                
                initial_state = {
                    "command": command,
                    "context": context or {},
                    "messages": [HumanMessage(content=command)],
                    "current_step": "initialized",
                    "results": [],
                    "plugin_outputs": {},
                    "approval_required": [],
                    "approved_actions": [],
                    "workflow_metadata": {"workflow_type": "simple"}
                }
                
            elif workflow_type == "multi_step":
                workflow = self.create_multi_step_workflow().compile(checkpointer=self.memory)
                
                initial_state = {
                    "original_command": command,
                    "parsed_steps": [],
                    "current_step_index": 0,
                    "step_results": [],
                    "workflow_context": context or {},
                    "continue_on_failure": False,
                    "rollback_actions": []
                }
            
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            # Execute the workflow
            result = workflow.invoke(initial_state)
            
            return {
                "success": True,
                "workflow_type": workflow_type,
                "result": result,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error executing {workflow_type} workflow: {e}")
            return {
                "success": False,
                "workflow_type": workflow_type,
                "result": None,
                "error": str(e)
            }
    
    def _fallback_execution(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback execution when LangGraph is not available."""
        try:
            action = plugin_manager.parse_command(command, context)
            if action:
                result = plugin_manager.execute_action(action, context)
                return {
                    "success": result.success,
                    "workflow_type": "fallback",
                    "result": {
                        "plugin_outputs": {"fallback": {
                            "success": result.success,
                            "output": result.output,
                            "error": result.error
                        }}
                    },
                    "error": result.error if not result.success else None
                }
            else:
                return {
                    "success": False,
                    "workflow_type": "fallback",
                    "result": None,
                    "error": "No plugin found to handle command"
                }
        except Exception as e:
            return {
                "success": False,
                "workflow_type": "fallback",
                "result": None,
                "error": str(e)
            }
    
    def approve_actions(self, workflow_id: str, approved_plugins: List[str]) -> bool:
        """Approve actions for a workflow waiting for approval."""
        # This would integrate with the checkpointer to update workflow state
        # For now, return a simple success indication
        logger.info(f"Approved actions for workflow {workflow_id}: {approved_plugins}")
        return True


# Global workflow orchestrator instance
workflow_orchestrator = PluginWorkflowOrchestrator()


# Convenience functions
def execute_plugin_workflow(command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a plugin workflow for a command."""
    return workflow_orchestrator.execute_workflow(command, context, "simple")


def execute_multi_step_workflow(command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a multi-step workflow for a complex command."""
    return workflow_orchestrator.execute_workflow(command, context, "multi_step")


def create_custom_workflow(workflow_definition: Dict[str, Any]) -> StateGraph:
    """Create a custom workflow from a definition."""
    # This would allow users to define custom workflows
    # Implementation would depend on the specific format
    pass


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Enhanced Plugin Workflow Integration...")
    
    # Test simple workflow
    result = execute_plugin_workflow("git status", {"repository_path": "."})
    print(f"Simple workflow result: {result}")
    
    # Test multi-step workflow
    result = execute_multi_step_workflow("git status then git diff")
    print(f"Multi-step workflow result: {result}")
    
    print("Enhanced plugin workflow integration test completed!")