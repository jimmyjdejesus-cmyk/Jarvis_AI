"""
LangGraph Workflow for Reliability and Degraded Operation Management
Implements state transitions and decision trees for graceful degradation.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import sys
from pathlib import Path

# Try to import LangGraph components
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create fallback classes
    class StateGraph:
        def __init__(self): 
            self.nodes = {}
            self.edges = {}
        def add_node(self, name, func): 
            self.nodes[name] = func
        def add_edge(self, from_node, to_node): 
            self.edges[from_node] = to_node
        def add_conditional_edges(self, from_node, condition, mapping): 
            pass
        def set_entry_point(self, node): 
            self.entry_point = node
        def compile(self): 
            return ReliabilityWorkflowFallback(self.nodes, self.edges)
    
    END = "END"
    BaseMessage = object
    HumanMessage = lambda content: {"role": "human", "content": content}
    AIMessage = lambda content: {"role": "ai", "content": content}

# Add legacy path for imports
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from agent.core.reliability import get_reliability_manager, OperationMode, SystemState
    from agent.core.rag_fallback import get_offline_rag_handler
except ImportError:
    # We're in development, import from local modules
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from core.reliability import get_reliability_manager, OperationMode, SystemState
        from core.rag_fallback import get_offline_rag_handler
    except ImportError as e:
        print(f"Could not import reliability modules: {e}")
        get_reliability_manager = lambda: None
        OperationMode = type('OperationMode', (), {
            'FULL': 'full', 'LOCAL_ONLY': 'local_only', 
            'OFFLINE': 'offline', 'BASIC': 'basic', 'EMERGENCY': 'emergency'
        })
        SystemState = type('SystemState', (), {
            'HEALTHY': 'healthy', 'DEGRADED': 'degraded', 
            'CRITICAL': 'critical', 'OFFLINE': 'offline'
        })
        get_offline_rag_handler = lambda: None


@dataclass
class ReliabilityState:
    """State for the reliability workflow."""
    messages: List[Dict[str, Any]]
    current_mode: str
    system_state: str
    error_context: Optional[Dict[str, Any]] = None
    recovery_attempts: int = 0
    last_health_check: Optional[str] = None
    user_query: str = ""
    response: str = ""
    requires_escalation: bool = False


class ReliabilityWorkflow:
    """LangGraph workflow for managing system reliability and degraded operations."""
    
    def __init__(self):
        self.reliability_manager = get_reliability_manager()
        self.offline_rag = get_offline_rag_handler()
        
        # Initialize workflow graph
        if LANGGRAPH_AVAILABLE:
            self.graph = self._create_langgraph_workflow()
        else:
            self.graph = self._create_fallback_workflow()
    
    def _create_langgraph_workflow(self):
        """Create the LangGraph workflow for reliability management."""
        workflow = StateGraph(ReliabilityState)
        
        # Add nodes
        workflow.add_node("assess_system_health", self._assess_system_health)
        workflow.add_node("handle_healthy_state", self._handle_healthy_state)
        workflow.add_node("handle_degraded_state", self._handle_degraded_state)
        workflow.add_node("handle_critical_state", self._handle_critical_state)
        workflow.add_node("attempt_recovery", self._attempt_recovery)
        workflow.add_node("process_with_fallback", self._process_with_fallback)
        workflow.add_node("emergency_response", self._emergency_response)
        workflow.add_node("escalate_to_admin", self._escalate_to_admin)
        
        # Set entry point
        workflow.set_entry_point("assess_system_health")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "assess_system_health",
            self._route_by_health,
            {
                "healthy": "handle_healthy_state",
                "degraded": "handle_degraded_state", 
                "critical": "handle_critical_state",
                "offline": "emergency_response"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_degraded_state",
            self._should_attempt_recovery,
            {
                "attempt_recovery": "attempt_recovery",
                "process_fallback": "process_with_fallback"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_critical_state",
            self._should_escalate,
            {
                "escalate": "escalate_to_admin",
                "attempt_recovery": "attempt_recovery",
                "emergency": "emergency_response"
            }
        )
        
        workflow.add_conditional_edges(
            "attempt_recovery",
            self._check_recovery_success,
            {
                "success": "assess_system_health",
                "retry": "attempt_recovery",
                "fallback": "process_with_fallback",
                "emergency": "emergency_response"
            }
        )
        
        # Terminal edges
        workflow.add_edge("handle_healthy_state", END)
        workflow.add_edge("process_with_fallback", END)
        workflow.add_edge("emergency_response", END)
        workflow.add_edge("escalate_to_admin", END)
        
        return workflow.compile()
    
    def _create_fallback_workflow(self):
        """Create fallback workflow when LangGraph is not available."""
        return ReliabilityWorkflowFallback()
    
    # Workflow node implementations
    def _assess_system_health(self, state: ReliabilityState) -> ReliabilityState:
        """Assess current system health and update state."""
        if self.reliability_manager:
            # Trigger health check
            health_report = self.reliability_manager._check_system_health()
            
            state.current_mode = self.reliability_manager.get_current_mode().value
            state.system_state = self.reliability_manager.get_current_state().value
            state.last_health_check = datetime.now().isoformat()
            
            # Add health report to messages
            state.messages.append({
                "type": "health_assessment",
                "timestamp": state.last_health_check,
                "mode": state.current_mode,
                "state": state.system_state,
                "services": health_report.get("services", {})
            })
        else:
            # Fallback assessment
            state.current_mode = "unknown"
            state.system_state = "unknown"
            state.last_health_check = datetime.now().isoformat()
        
        return state
    
    def _handle_healthy_state(self, state: ReliabilityState) -> ReliabilityState:
        """Handle system in healthy state."""
        if state.user_query:
            # Process normally with full functionality
            state.response = f"System is healthy. Processing your request: {state.user_query}"
            
            # Use full RAG if available
            if self.offline_rag:
                try:
                    response = self.offline_rag.handle_rag_request(
                        state.user_query, [], "full", ""
                    )
                    state.response = response
                except Exception as e:
                    state.response = f"Processed in healthy mode, but encountered: {str(e)}"
        else:
            state.response = "System is operating normally. All services are available."
        
        state.messages.append({
            "type": "healthy_response",
            "timestamp": datetime.now().isoformat(),
            "response": state.response
        })
        
        return state
    
    def _handle_degraded_state(self, state: ReliabilityState) -> ReliabilityState:
        """Handle system in degraded state."""
        state.messages.append({
            "type": "degraded_handling",
            "timestamp": datetime.now().isoformat(),
            "mode": state.current_mode,
            "recovery_attempts": state.recovery_attempts
        })
        
        return state
    
    def _handle_critical_state(self, state: ReliabilityState) -> ReliabilityState:
        """Handle system in critical state."""
        state.messages.append({
            "type": "critical_handling",
            "timestamp": datetime.now().isoformat(),
            "mode": state.current_mode,
            "requires_escalation": True
        })
        
        state.requires_escalation = True
        return state
    
    def _attempt_recovery(self, state: ReliabilityState) -> ReliabilityState:
        """Attempt to recover system functionality."""
        state.recovery_attempts += 1
        
        recovery_success = False
        if self.reliability_manager:
            try:
                # Try recovery based on current state
                if state.system_state == "degraded":
                    # Attempt service-specific recovery
                    recovery_success = self.reliability_manager._recover_ollama_service()
                elif state.system_state == "critical":
                    # Multiple recovery attempts
                    recovery_success = (
                        self.reliability_manager._recover_ollama_service() or
                        self.reliability_manager._recover_rag_service() or
                        self.reliability_manager._recover_cache_service()
                    )
            except Exception as e:
                state.error_context = {"recovery_error": str(e)}
        
        state.messages.append({
            "type": "recovery_attempt",
            "timestamp": datetime.now().isoformat(),
            "attempt_number": state.recovery_attempts,
            "success": recovery_success,
            "error_context": state.error_context
        })
        
        return state
    
    def _process_with_fallback(self, state: ReliabilityState) -> ReliabilityState:
        """Process user query using fallback mechanisms."""
        if state.user_query and self.offline_rag:
            try:
                # Use appropriate mode based on system state
                mode = "offline" if state.current_mode in ["offline", "emergency"] else "local_only"
                
                response = self.offline_rag.handle_rag_request(
                    state.user_query, [], mode, ""
                )
                
                state.response = (f"[{state.current_mode.upper()} MODE] {response}")
                
            except Exception as e:
                state.response = (f"I'm operating in {state.current_mode} mode due to system issues. "
                                f"I cannot fully process your request: {state.user_query}. "
                                f"Error: {str(e)}")
        else:
            state.response = f"System is in {state.current_mode} mode. Limited functionality available."
        
        state.messages.append({
            "type": "fallback_response",
            "timestamp": datetime.now().isoformat(),
            "mode": state.current_mode,
            "response": state.response
        })
        
        return state
    
    def _emergency_response(self, state: ReliabilityState) -> ReliabilityState:
        """Handle emergency state with minimal functionality."""
        if self.offline_rag:
            emergency_response = self.offline_rag.enhanced_cache.get_emergency_response(
                state.user_query or "system status"
            )
        else:
            emergency_response = ("System is in emergency mode. Most functionality is unavailable. "
                                "Please contact system administrator.")
        
        state.response = f"[EMERGENCY MODE] {emergency_response}"
        
        state.messages.append({
            "type": "emergency_response",
            "timestamp": datetime.now().isoformat(),
            "response": state.response
        })
        
        return state
    
    def _escalate_to_admin(self, state: ReliabilityState) -> ReliabilityState:
        """Escalate critical issues to administrator."""
        escalation_message = {
            "type": "admin_escalation",
            "timestamp": datetime.now().isoformat(),
            "system_state": state.system_state,
            "recovery_attempts": state.recovery_attempts,
            "error_context": state.error_context,
            "user_query": state.user_query
        }
        
        state.messages.append(escalation_message)
        state.response = ("Critical system issues detected. Administrator has been notified. "
                         "System will attempt to continue in emergency mode.")
        
        return state
    
    # Routing functions
    def _route_by_health(self, state: ReliabilityState) -> str:
        """Route based on system health state."""
        health_state = state.system_state.lower()
        
        if health_state == "healthy":
            return "healthy"
        elif health_state == "degraded":
            return "degraded"
        elif health_state == "critical":
            return "critical"
        else:
            return "offline"
    
    def _should_attempt_recovery(self, state: ReliabilityState) -> str:
        """Determine if recovery should be attempted."""
        if state.recovery_attempts < 3:
            return "attempt_recovery"
        else:
            return "process_fallback"
    
    def _should_escalate(self, state: ReliabilityState) -> str:
        """Determine if issue should be escalated."""
        if state.recovery_attempts >= 2:
            return "escalate"
        elif state.recovery_attempts == 0:
            return "attempt_recovery"
        else:
            return "emergency"
    
    def _check_recovery_success(self, state: ReliabilityState) -> str:
        """Check if recovery was successful."""
        # Check last message for recovery success
        last_msg = state.messages[-1] if state.messages else {}
        
        if last_msg.get("success", False):
            return "success"
        elif state.recovery_attempts < 3:
            return "retry"
        elif state.system_state == "critical":
            return "emergency"
        else:
            return "fallback"
    
    # Public interface
    def execute_workflow(self, user_query: str = "", initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the reliability workflow."""
        # Initialize state
        state = ReliabilityState(
            messages=[],
            current_mode="unknown",
            system_state="unknown",
            user_query=user_query,
            response="",
            recovery_attempts=0
        )
        
        if initial_state:
            for key, value in initial_state.items():
                if hasattr(state, key):
                    setattr(state, key, value)
        
        try:
            # Execute workflow
            if LANGGRAPH_AVAILABLE:
                result = self.graph.invoke(state)
            else:
                result = self.graph.execute(state)
            
            return {
                "success": True,
                "final_state": result.system_state if hasattr(result, 'system_state') else "unknown",
                "operation_mode": result.current_mode if hasattr(result, 'current_mode') else "unknown",
                "response": result.response if hasattr(result, 'response') else "No response generated",
                "messages": result.messages if hasattr(result, 'messages') else [],
                "recovery_attempts": result.recovery_attempts if hasattr(result, 'recovery_attempts') else 0,
                "requires_escalation": result.requires_escalation if hasattr(result, 'requires_escalation') else False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Workflow execution failed: {str(e)}",
                "final_state": "error",
                "operation_mode": "emergency"
            }


class ReliabilityWorkflowFallback:
    """Fallback workflow implementation when LangGraph is not available."""
    
    def __init__(self, nodes=None, edges=None):
        self.nodes = nodes or {}
        self.edges = edges or {}
        self.reliability_manager = get_reliability_manager()
        self.offline_rag = get_offline_rag_handler()
    
    def execute(self, state: ReliabilityState) -> ReliabilityState:
        """Execute simplified workflow logic."""
        try:
            # Basic health assessment
            if self.reliability_manager:
                state.current_mode = self.reliability_manager.get_current_mode().value
                state.system_state = self.reliability_manager.get_current_state().value
            else:
                state.current_mode = "basic"
                state.system_state = "unknown"
            
            # Process based on state
            if state.system_state in ["healthy", "unknown"]:
                state.response = self._handle_normal_processing(state.user_query)
            elif state.system_state == "degraded":
                state.response = self._handle_degraded_processing(state.user_query)
            else:
                state.response = self._handle_emergency_processing(state.user_query)
            
            state.messages.append({
                "type": "fallback_execution",
                "timestamp": datetime.now().isoformat(),
                "state": state.system_state,
                "mode": state.current_mode,
                "response": state.response
            })
            
        except Exception as e:
            state.response = f"Fallback workflow error: {str(e)}"
            state.system_state = "error"
        
        return state
    
    def _handle_normal_processing(self, user_query: str) -> str:
        """Handle normal processing."""
        if self.offline_rag and user_query:
            try:
                return self.offline_rag.handle_rag_request(user_query, [], "full", "")
            except Exception as e:
                return f"Processing error: {str(e)}"
        return "System operating normally."
    
    def _handle_degraded_processing(self, user_query: str) -> str:
        """Handle degraded processing."""
        if self.offline_rag and user_query:
            try:
                return self.offline_rag.handle_rag_request(user_query, [], "local_only", "")
            except Exception as e:
                return f"Degraded mode error: {str(e)}"
        return "System in degraded mode. Limited functionality available."
    
    def _handle_emergency_processing(self, user_query: str) -> str:
        """Handle emergency processing."""
        if self.offline_rag:
            return self.offline_rag.enhanced_cache.get_emergency_response(user_query or "status")
        return "System in emergency mode. Please contact administrator."


# Global workflow instance
_reliability_workflow = None


def get_reliability_workflow() -> ReliabilityWorkflow:
    """Get global reliability workflow instance."""
    global _reliability_workflow
    if _reliability_workflow is None:
        _reliability_workflow = ReliabilityWorkflow()
    return _reliability_workflow


# Convenience function for quick workflow execution
def execute_reliability_check(user_query: str = "") -> Dict[str, Any]:
    """Execute reliability workflow with given user query."""
    workflow = get_reliability_workflow()
    return workflow.execute_workflow(user_query)