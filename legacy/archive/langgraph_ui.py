#!/usr/bin/env python3
"""Archived LangGraphUI integration for reference.

Superseded by :mod:`v2.agent.adapters.langgraph_ui`.
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
        
        # === NEW: User Experience Enhancements - Interactive Explanation Visualization ===
        self._render_personalized_workflow_view(workflow_result)
        # === END: User Experience Enhancements ===
        
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


    # === NEW: User Experience Enhancements - Personalized Workflow Visualization ===
    def _render_personalized_workflow_view(self, workflow_result: Dict[str, Any] = None):
        """Render personalized workflow view with explanations and user context."""
        
        # Get user preferences for personalized display
        from database import get_user_preferences
        user_id = st.session_state.get('user', 'anonymous')
        user_prefs = get_user_preferences(user_id)
        
        # Personalized workflow display based on user preferences
        st.markdown("### 🎯 Personalized Workflow View")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Main workflow visualization
            if workflow_result:
                # Show explanations if enabled
                if user_prefs.get("show_code_explanations", True):
                    self._render_workflow_explanations(workflow_result, user_prefs)
                
                # Show workflow steps with rationale if enabled
                if user_prefs.get("show_completion_rationale", True):
                    self._render_workflow_rationale(workflow_result, user_prefs)
        
        with col2:
            # User context panel
            self._render_user_context_panel(user_prefs, workflow_result)
    
    def _render_workflow_explanations(self, workflow_result: Dict[str, Any], user_prefs: Dict[str, Any]):
        """Render workflow step explanations based on user preferences."""
        
        explanations = workflow_result.get("explanation_requests", [])
        if not explanations:
            return
        
        with st.expander("💡 Workflow Explanations", expanded=True):
            style = user_prefs.get("communication_style", "Professional")
            
            st.markdown(f"**Explanation Style:** {style}")
            
            for i, explanation in enumerate(explanations):
                step = explanation.get("step", f"Step {i+1}")
                content = explanation.get("explanation", "No explanation available")
                timestamp = explanation.get("timestamp", "")
                
                with st.container():
                    st.markdown(f"**{step.replace('_', ' ').title()}**")
                    st.markdown(content)
                    if timestamp:
                        st.caption(f"Generated at: {timestamp}")
                    st.markdown("---")
    
    def _render_workflow_rationale(self, workflow_result: Dict[str, Any], user_prefs: Dict[str, Any]):
        """Render workflow decision rationale."""
        
        with st.expander("🧠 Decision Rationale", expanded=False):
            
            # Show personalization context if available
            personalization_context = workflow_result.get("personalization_context", {})
            if personalization_context:
                st.markdown("**Personalization Applied:**")
                
                recent_prefs = personalization_context.get("recent_preferences", [])
                if recent_prefs:
                    st.markdown(f"- Based on {len(recent_prefs)} recent interactions")
                
                patterns = personalization_context.get("user_patterns", {})
                if patterns:
                    st.markdown(f"- User patterns analyzed: {len(patterns)} categories")
                
                adaptations = personalization_context.get("adaptations", {})
                if adaptations:
                    st.markdown(f"- Learning adaptations applied: {len(adaptations)} areas")
            
            # Show workflow decision points
            current_step = workflow_result.get("current_step", "unknown")
            iteration_count = workflow_result.get("iteration_count", 1)
            
            st.markdown("**Workflow Decisions:**")
            st.markdown(f"- Current step: {current_step.replace('_', ' ').title()}")
            st.markdown(f"- Iteration: {iteration_count}")
            
            # Show learning feedback if available
            learning_feedback = workflow_result.get("learning_feedback")
            if learning_feedback:
                st.markdown("**Learning Feedback:**")
                st.json(learning_feedback)
    
    def _render_user_context_panel(self, user_prefs: Dict[str, Any], workflow_result: Dict[str, Any] = None):
        """Render user context and personalization panel."""
        
        st.markdown("#### 👤 Your Profile")
        
        # Show user preferences
        learning_rate = user_prefs.get("learning_rate", "Moderate")
        domain = user_prefs.get("domain_specialization", "General")
        style = user_prefs.get("communication_style", "Professional")
        
        st.markdown(f"**Learning Rate:** {learning_rate}")
        st.markdown(f"**Domain Focus:** {domain}")
        st.markdown(f"**Communication Style:** {style}")
        
        # Show knowledge sources if enabled
        if user_prefs.get("show_knowledge_sources", True):
            st.markdown("#### 📚 Active Knowledge Sources")
            st.markdown("- Your interaction history")
            st.markdown(f"- {domain} domain knowledge")
            st.markdown("- LangGraph workflow patterns")
            
            if workflow_result:
                sources = workflow_result.get("sources", [])
                for source in sources:
                    st.markdown(f"- {source}")
        
        # Show learning status
        if workflow_result:
            interaction_history = workflow_result.get("interaction_history", [])
            if interaction_history:
                st.markdown("#### 📈 Learning Status")
                st.markdown(f"Recent interactions: {len(interaction_history)}")
                
                # Show learning trend
                positive_interactions = sum(1 for interaction in interaction_history[-10:] 
                                         if interaction.get('feedback', False))
                total_recent = min(len(interaction_history), 10)
                
                if total_recent > 0:
                    satisfaction_rate = (positive_interactions / total_recent) * 100
                    st.progress(satisfaction_rate / 100)
                    st.caption(f"Satisfaction rate: {satisfaction_rate:.1f}%")
        
        # Interactive feedback section
        st.markdown("#### 💬 Quick Feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Helpful", key="feedback_positive"):
                self._record_quick_feedback(True, workflow_result)
                st.success("Thanks for the feedback!")
        
        with col2:
            if st.button("👎 Not Helpful", key="feedback_negative"):
                self._record_quick_feedback(False, workflow_result)
                st.info("Feedback recorded. I'll improve!")
    
    def _record_quick_feedback(self, positive: bool, workflow_result: Dict[str, Any] = None):
        """Record quick user feedback for learning."""
        try:
            from agent.adapters.personalization_memory import get_user_personalization_memory
            from database import get_user_preferences
            
            user_id = st.session_state.get('user', 'anonymous')
            user_prefs = get_user_preferences(user_id)
            user_memory = get_user_personalization_memory(user_id)
            
            context = {
                "workflow_step": workflow_result.get("current_step", "workflow_display") if workflow_result else "ui_interaction",
                "domain": user_prefs.get("domain_specialization", "General"),
                "pattern": "quick_feedback",
                "description": "User provided quick feedback on workflow visualization"
            }
            
            user_memory.record_interaction(
                interaction_type="ui_feedback",
                context=context,
                feedback=positive,
                learning_rate=user_prefs.get("learning_rate", "Moderate")
            )
            
        except Exception as e:
            # Don't fail UI if feedback recording fails
            pass
    
    # === END: User Experience Enhancements ===


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