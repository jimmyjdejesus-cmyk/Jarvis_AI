#!/usr/bin/env python3
"""
LangGraphUI integration for Jarvis AI.

This module provides visualization capabilities for the LangGraph workflow,
allowing users to see the agent's reasoning process and decision flow.
"""

import json
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    # Try to import LangGraphUI components if available
    from langgraph.graph import Graph
    from langgraph_ui import LangGraphUI  # Replace with actual UI component if different
    LANGGRAPH_UI_AVAILABLE = True
except ImportError:
    LANGGRAPH_UI_AVAILABLE = False


class WorkflowVisualizer:
    """Visualizer for LangGraph workflow execution."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.execution_history = []
        
    def add_execution(self, workflow_result: Dict[str, Any]):
        """Add a workflow execution to the history."""
        execution = {
            "timestamp": datetime.now().isoformat(),
            "result": workflow_result,
            "id": len(self.execution_history)
        }
        self.execution_history.append(execution)
    
    def render_workflow_visualization(self, workflow_result: Dict[str, Any] = None):
        """Render the workflow visualization in Streamlit."""
        
        st.subheader("🔍 Workflow Visualization")
        
        if not LANGGRAPH_UI_AVAILABLE:
            st.warning("LangGraphUI not fully available - showing simplified visualization")
        
        # Show current execution if provided
        if workflow_result:
            self.add_execution(workflow_result)
        
        if not self.execution_history:
            st.info("No workflow executions to display")
            return
        
        # Display execution selector
        execution_options = [f"Execution {ex['id']} - {ex['timestamp'][:19]}" 
                           for ex in self.execution_history]
        
        selected_idx = st.selectbox(
            "Select execution to visualize:",
            range(len(execution_options)),
            format_func=lambda x: execution_options[x],
            index=len(execution_options) - 1  # Default to latest
        )
        
        selected_execution = self.execution_history[selected_idx]
        result = selected_execution["result"]
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Flow Diagram", "Step Details", "Messages", "Reflection"])
        
        with tab1:
            self._render_flow_diagram(result)
        
        with tab2:
            self._render_step_details(result)
        
        with tab3:
            self._render_messages(result)
        
        with tab4:
            self._render_reflection(result)
    
    def _render_flow_diagram(self, result: Dict[str, Any]):
        """Render a flow diagram of the workflow execution."""
        st.markdown("### Workflow Flow")
        
        # Create a simple flow visualization
        steps = []
        
        if result.get("plan"):
            steps.append(("📋 Planning", "success", "Plan created successfully"))
        
        if result.get("code_output"):
            steps.append(("💻 Code/Tools", "success", "Code generation or tool execution"))
        
        if result.get("test_results"):
            steps.append(("🧪 Testing", "success", "System testing and validation"))
        
        if result.get("reflection"):
            steps.append(("🤔 Reflection", "success", "Analysis and reasoning"))
        
        if result.get("error"):
            steps.append(("❌ Error", "error", f"Error: {result['error']}"))
        
        # Display flow
        for i, (step_name, status, description) in enumerate(steps):
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                if status == "success":
                    st.success(f"Step {i+1}")
                else:
                    st.error(f"Step {i+1}")
            
            with col2:
                st.write(step_name)
            
            with col3:
                st.write(description)
            
            # Add arrow if not last step
            if i < len(steps) - 1:
                st.markdown("⬇️", unsafe_allow_html=True)
        
        # Show iteration count if available
        iterations = result.get("iterations", 0)
        if iterations > 1:
            st.info(f"Completed in {iterations} iterations")
    
    def _render_step_details(self, result: Dict[str, Any]):
        """Render detailed step information."""
        st.markdown("### Step Details")
        
        # Plan details
        if result.get("plan"):
            with st.expander("📋 Planning Details", expanded=True):
                try:
                    plan_data = json.loads(result["plan"]) if isinstance(result["plan"], str) else result["plan"]
                    st.json(plan_data)
                except:
                    st.text(str(result["plan"]))
        
        # Code/Tool output
        if result.get("code_output"):
            with st.expander("💻 Code/Tool Output"):
                try:
                    code_data = json.loads(result["code_output"]) if isinstance(result["code_output"], str) else result["code_output"]
                    st.json(code_data)
                except:
                    st.text(str(result["code_output"]))
        
        # Test results
        if result.get("test_results"):
            with st.expander("🧪 Test Results"):
                try:
                    test_data = json.loads(result["test_results"]) if isinstance(result["test_results"], str) else result["test_results"]
                    st.json(test_data)
                except:
                    st.text(str(result["test_results"]))
    
    def _render_messages(self, result: Dict[str, Any]):
        """Render workflow messages."""
        st.markdown("### Workflow Messages")
        
        messages = result.get("messages", [])
        if not messages:
            st.info("No messages available")
            return
        
        for i, message in enumerate(messages):
            with st.container():
                st.markdown(f"**Message {i+1}:** {message}")
    
    def _render_reflection(self, result: Dict[str, Any]):
        """Render the critic/reflection analysis."""
        st.markdown("### Reflection & Analysis")
        
        reflection = result.get("reflection")
        if not reflection:
            st.info("No reflection available")
            return
        
        try:
            if isinstance(reflection, str):
                reflection_data = json.loads(reflection)
            else:
                reflection_data = reflection
            
            # Success indicators
            if "success_indicators" in reflection_data:
                st.markdown("#### ✅ Success Indicators")
                for indicator in reflection_data["success_indicators"]:
                    st.success(indicator)
            
            # Concerns
            if "concerns" in reflection_data:
                st.markdown("#### ⚠️ Concerns")
                for concern in reflection_data["concerns"]:
                    st.warning(concern)
            
            # Recommendations
            if "recommendations" in reflection_data:
                st.markdown("#### 💡 Recommendations")
                for rec in reflection_data["recommendations"]:
                    st.info(rec)
            
            # Full reflection data
            with st.expander("Full Reflection Data"):
                st.json(reflection_data)
                
        except json.JSONDecodeError:
            st.text(str(reflection))
    
    def render_workflow_metrics(self):
        """Render workflow execution metrics."""
        if not self.execution_history:
            return
        
        st.subheader("📊 Workflow Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Executions", len(self.execution_history))
        
        with col2:
            successful = sum(1 for ex in self.execution_history 
                           if ex["result"].get("success", False))
            st.metric("Successful", successful)
        
        with col3:
            failed = len(self.execution_history) - successful
            st.metric("Failed", failed)
        
        # Recent execution trends
        if len(self.execution_history) >= 5:
            st.markdown("#### Recent Execution Trends")
            recent_executions = self.execution_history[-10:]
            
            success_rate = sum(1 for ex in recent_executions 
                             if ex["result"].get("success", False)) / len(recent_executions)
            
            if success_rate >= 0.8:
                st.success(f"Success rate: {success_rate:.1%}")
            elif success_rate >= 0.6:
                st.warning(f"Success rate: {success_rate:.1%}")
            else:
                st.error(f"Success rate: {success_rate:.1%}")


# Global visualizer instance
workflow_visualizer = WorkflowVisualizer()


def render_langgraph_ui(workflow_result: Dict[str, Any] = None):
    """Main function to render LangGraph UI components."""
    
    st.markdown("## 🔄 LangGraph Workflow Visualization")
    
    if not LANGGRAPH_UI_AVAILABLE:
        st.info("💡 For enhanced visualization, install LangGraphUI: `pip install langgraph-ui`")
    
    # Render the main workflow visualization
    workflow_visualizer.render_workflow_visualization(workflow_result)
    
    # Render metrics
    workflow_visualizer.render_workflow_metrics()


def get_workflow_visualizer() -> WorkflowVisualizer:
    """Get the global workflow visualizer instance."""
    return workflow_visualizer