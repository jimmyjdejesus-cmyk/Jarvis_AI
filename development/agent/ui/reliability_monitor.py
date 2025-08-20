"""
Reliability Monitoring UI Components
Provides visualization and monitoring interfaces for system reliability.
"""

import json
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add legacy path for imports  
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from agent.core.reliability import get_reliability_manager, OperationMode, SystemState
    from agent.core.rag_fallback import get_enhanced_rag_cache
    from agent.workflows.reliability_workflow import get_reliability_workflow
except ImportError:
    # We're in development, import from local modules
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from core.reliability import get_reliability_manager, OperationMode, SystemState
        from core.rag_fallback import get_enhanced_rag_cache
        from workflows.reliability_workflow import get_reliability_workflow
    except ImportError as e:
        print(f"Could not import reliability modules: {e}")
        # Create fallback functions
        get_reliability_manager = lambda: None
        get_enhanced_rag_cache = lambda: None
        get_reliability_workflow = lambda: None
        OperationMode = type('OperationMode', (), {
            'FULL': 'full', 'LOCAL_ONLY': 'local_only', 
            'OFFLINE': 'offline', 'BASIC': 'basic', 'EMERGENCY': 'emergency'
        })
        SystemState = type('SystemState', (), {
            'HEALTHY': 'healthy', 'DEGRADED': 'degraded', 
            'CRITICAL': 'critical', 'OFFLINE': 'offline'
        })


class ReliabilityMonitor:
    """UI component for monitoring system reliability and health."""
    
    def __init__(self):
        self.reliability_manager = get_reliability_manager()
        self.enhanced_cache = get_enhanced_rag_cache()
        self.workflow = get_reliability_workflow()
    
    def render_system_status_dashboard(self):
        """Render the main system status dashboard."""
        st.header("🔧 System Reliability Dashboard")
        
        # Get current system status
        if self.reliability_manager:
            status = self.reliability_manager.get_system_status()
            current_mode = status.get("mode", "unknown")
            current_state = status.get("state", "unknown")
            services = status.get("services", {})
        else:
            current_mode = "unknown"
            current_state = "unknown"
            services = {}
        
        # Main status display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_mode_status(current_mode)
        
        with col2:
            self._render_health_status(current_state)
        
        with col3:
            self._render_quick_actions()
        
        # Service status grid
        st.subheader("📊 Service Health")
        self._render_service_grid(services)
        
        # Recent events
        st.subheader("📋 Recent Events")
        self._render_recent_events()
        
        # Cache statistics
        if self.enhanced_cache:
            st.subheader("💾 Cache Statistics")
            self._render_cache_stats()
    
    def _render_mode_status(self, current_mode: str):
        """Render current operation mode status."""
        mode_colors = {
            "full": "🟢",
            "local_only": "🟡", 
            "offline": "🟠",
            "basic": "🔴",
            "emergency": "🚨",
            "unknown": "⚪"
        }
        
        mode_descriptions = {
            "full": "All features available",
            "local_only": "No web RAG, local only",
            "offline": "Cached knowledge only",
            "basic": "Minimal functionality",
            "emergency": "Critical systems only",
            "unknown": "Status unknown"
        }
        
        color = mode_colors.get(current_mode, "⚪")
        description = mode_descriptions.get(current_mode, "Unknown mode")
        
        st.metric(
            label="Operation Mode",
            value=f"{color} {current_mode.upper()}",
            help=description
        )
    
    def _render_health_status(self, current_state: str):
        """Render system health status."""
        state_colors = {
            "healthy": "🟢",
            "degraded": "🟡",
            "critical": "🔴", 
            "offline": "⚫",
            "unknown": "⚪"
        }
        
        state_descriptions = {
            "healthy": "All systems operational",
            "degraded": "Some services affected",
            "critical": "Major issues detected",
            "offline": "System offline",
            "unknown": "Health status unknown"
        }
        
        color = state_colors.get(current_state, "⚪")
        description = state_descriptions.get(current_state, "Unknown state")
        
        st.metric(
            label="System Health",
            value=f"{color} {current_state.upper()}",
            help=description
        )
    
    def _render_quick_actions(self):
        """Render quick action buttons."""
        st.markdown("**Quick Actions**")
        
        if st.button("🔄 Refresh Status", key="refresh_status"):
            if self.reliability_manager:
                self.reliability_manager._check_system_health()
                st.success("Status refreshed!")
            else:
                st.warning("Reliability manager not available")
        
        if st.button("🚨 Test Emergency Mode", key="test_emergency"):
            if self.reliability_manager:
                self.reliability_manager.force_mode_switch(
                    OperationMode.EMERGENCY, "Manual test"
                )
                st.warning("Switched to emergency mode")
            else:
                st.warning("Reliability manager not available")
        
        if st.button("🔧 Run Recovery", key="run_recovery"):
            if self.workflow:
                result = self.workflow.execute_workflow("system recovery test")
                if result.get("success"):
                    st.success("Recovery workflow completed")
                else:
                    st.error(f"Recovery failed: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Workflow not available")
    
    def _render_service_grid(self, services: Dict[str, Any]):
        """Render service status grid."""
        if not services:
            st.info("No service status available")
            return
        
        cols = st.columns(len(services))
        
        for i, (service_name, service_status) in enumerate(services.items()):
            with cols[i]:
                is_healthy = service_status.get("healthy", False)
                status_icon = "✅" if is_healthy else "❌"
                error = service_status.get("error", "")
                last_check = service_status.get("last_check", "Never")
                
                # Parse timestamp if available
                if last_check and last_check != "Never":
                    try:
                        check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                        last_check = check_time.strftime("%H:%M:%S")
                    except:
                        pass
                
                st.metric(
                    label=f"{status_icon} {service_name.title()}",
                    value="Healthy" if is_healthy else "Error",
                    delta=f"Last check: {last_check}",
                    help=error if error else f"{service_name} service status"
                )
                
                # Additional service-specific info
                if service_name == "ollama" and "models" in service_status:
                    models = service_status["models"]
                    if models:
                        st.caption(f"Models: {len(models)}")
                        with st.expander(f"View {service_name} models"):
                            for model in models[:10]:  # Show first 10
                                st.text(f"• {model}")
                
                elif service_name == "rag" and "cache_size" in service_status:
                    cache_size = service_status["cache_size"]
                    st.caption(f"Cache: {cache_size} entries")
    
    def _render_recent_events(self):
        """Render recent system events."""
        if self.reliability_manager:
            status = self.reliability_manager.get_system_status()
            events = status.get("fallback_history", [])
        else:
            events = []
        
        if not events:
            st.info("No recent events")
            return
        
        # Display events in a table
        for event in events[-5:]:  # Show last 5 events
            timestamp = event.get("timestamp", "Unknown")
            from_mode = event.get("from_mode", "unknown")
            to_mode = event.get("to_mode", "unknown") 
            reason = event.get("reason", "No reason provided")
            
            # Parse timestamp
            try:
                event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = event_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp
            
            # Color code based on transition
            if to_mode in ["emergency", "critical"]:
                alert_type = "🚨"
                color = "red"
            elif to_mode in ["offline", "basic"]:
                alert_type = "⚠️" 
                color = "orange"
            elif to_mode == "full":
                alert_type = "✅"
                color = "green"
            else:
                alert_type = "ℹ️"
                color = "blue"
            
            with st.container():
                st.markdown(
                    f"**{alert_type} {time_str}**: {from_mode} → {to_mode}"
                )
                st.caption(f"Reason: {reason}")
                st.divider()
    
    def _render_cache_stats(self):
        """Render cache statistics."""
        if not self.enhanced_cache:
            st.info("Cache statistics not available")
            return
        
        try:
            stats = self.enhanced_cache.get_cache_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Entries", stats.get("total_entries", 0))
            
            with col2:
                st.metric("Memory Entries", stats.get("memory_entries", 0))
            
            with col3:
                cache_size_mb = stats.get("cache_size_mb", 0)
                st.metric("Cache Size", f"{cache_size_mb:.1f} MB")
            
            with col4:
                last_cleanup = stats.get("last_cleanup", "Never")
                if last_cleanup and last_cleanup != "Never":
                    try:
                        cleanup_time = datetime.fromisoformat(last_cleanup)
                        last_cleanup = cleanup_time.strftime("%H:%M")
                    except:
                        pass
                st.metric("Last Cleanup", last_cleanup)
            
            # Cache directory info
            cache_dir = stats.get("cache_dir", "Unknown")
            st.caption(f"Cache directory: {cache_dir}")
            
        except Exception as e:
            st.error(f"Failed to load cache statistics: {e}")
    
    def render_degraded_mode_interface(self):
        """Render interface for when system is in degraded mode."""
        st.warning("⚠️ System Operating in Degraded Mode")
        
        if self.reliability_manager:
            current_mode = self.reliability_manager.get_current_mode().value
            current_state = self.reliability_manager.get_current_state().value
        else:
            current_mode = "unknown"
            current_state = "unknown"
        
        st.info(f"Current mode: **{current_mode.upper()}** | State: **{current_state.upper()}**")
        
        # Show limitations
        limitations = self._get_mode_limitations(current_mode)
        if limitations:
            st.markdown("**Current Limitations:**")
            for limitation in limitations:
                st.markdown(f"• {limitation}")
        
        # Recovery options
        st.subheader("🔧 Recovery Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Attempt Automatic Recovery"):
                if self.workflow:
                    result = self.workflow.execute_workflow("automatic recovery")
                    if result.get("success"):
                        st.success("Recovery attempt completed")
                        if result.get("requires_escalation"):
                            st.warning("Issue escalated to administrator")
                    else:
                        st.error("Recovery failed")
                else:
                    st.error("Recovery workflow not available")
        
        with col2:
            if st.button("Force Full Mode (Admin Only)"):
                if self.reliability_manager:
                    self.reliability_manager.force_mode_switch(
                        OperationMode.FULL, "Administrator override"
                    )
                    st.success("Forced switch to full mode")
                else:
                    st.error("Reliability manager not available")
    
    def _get_mode_limitations(self, mode: str) -> List[str]:
        """Get limitations for current operation mode."""
        limitations = {
            "local_only": [
                "Web search and external APIs unavailable",
                "RAG limited to local knowledge only",
                "Real-time data not accessible"
            ],
            "offline": [
                "All external connections disabled",
                "Only cached knowledge available",
                "No model updates possible"
            ],
            "basic": [
                "Minimal feature set only",
                "Basic completion mode",
                "Limited processing capabilities"
            ],
            "emergency": [
                "Critical systems only",
                "Most features disabled",
                "Emergency responses only"
            ]
        }
        
        return limitations.get(mode, [])


class WorkflowVisualizer:
    """Visualizer for reliability workflow execution."""
    
    def __init__(self):
        self.execution_history = []
    
    def add_execution(self, workflow_result: Dict[str, Any]):
        """Add workflow execution result to history."""
        execution = {
            "timestamp": datetime.now(),
            "result": workflow_result,
            "success": workflow_result.get("success", False),
            "final_state": workflow_result.get("final_state", "unknown"),
            "operation_mode": workflow_result.get("operation_mode", "unknown"),
            "recovery_attempts": workflow_result.get("recovery_attempts", 0)
        }
        
        self.execution_history.append(execution)
        
        # Keep only last 50 executions
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
    
    def render_workflow_status(self):
        """Render workflow execution status."""
        st.subheader("🔄 Workflow Execution History")
        
        if not self.execution_history:
            st.info("No workflow executions recorded")
            return
        
        # Summary metrics
        recent_executions = self.execution_history[-10:]
        success_rate = sum(1 for ex in recent_executions if ex["success"]) / len(recent_executions)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Success Rate (Last 10)", f"{success_rate:.1%}")
        
        with col2:
            st.metric("Total Executions", len(self.execution_history))
        
        with col3:
            last_execution = self.execution_history[-1]
            st.metric("Last Status", 
                     "✅ Success" if last_execution["success"] else "❌ Failed")
        
        # Execution timeline
        with st.expander("View Execution Timeline"):
            for execution in reversed(self.execution_history[-10:]):
                timestamp = execution["timestamp"].strftime("%H:%M:%S")
                success_icon = "✅" if execution["success"] else "❌"
                
                st.markdown(
                    f"**{success_icon} {timestamp}** - "
                    f"State: {execution['final_state']} | "
                    f"Mode: {execution['operation_mode']} | "
                    f"Recoveries: {execution['recovery_attempts']}"
                )
                
                if not execution["success"]:
                    error = execution["result"].get("error", "Unknown error")
                    st.caption(f"Error: {error}")


# Global visualizer instance
_workflow_visualizer = None

def get_workflow_visualizer() -> WorkflowVisualizer:
    """Get global workflow visualizer instance."""
    global _workflow_visualizer
    if _workflow_visualizer is None:
        _workflow_visualizer = WorkflowVisualizer()
    return _workflow_visualizer


# Convenience functions for Streamlit integration
def render_reliability_sidebar():
    """Render reliability information in sidebar."""
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        reliability_manager = get_reliability_manager()
        if reliability_manager:
            current_mode = reliability_manager.get_current_mode().value
            current_state = reliability_manager.get_current_state().value
            
            # Status indicators
            if current_state == "healthy":
                st.success(f"✅ {current_state.upper()}")
            elif current_state == "degraded":
                st.warning(f"⚠️ {current_state.upper()}")
            else:
                st.error(f"🚨 {current_state.upper()}")
            
            st.caption(f"Mode: {current_mode.upper()}")
        else:
            st.info("Status: Unknown")


def render_reliability_dashboard():
    """Render full reliability dashboard."""
    monitor = ReliabilityMonitor()
    monitor.render_system_status_dashboard()


def render_degraded_mode_ui():
    """Render degraded mode interface."""
    monitor = ReliabilityMonitor()
    monitor.render_degraded_mode_interface()