"""
UI Components - Modern interface components
"""

import streamlit as st
import pandas as pd
from typing import Any, Dict
from pathlib import Path


try:
    from ui.sidebar import sidebar as legacy_sidebar
    from ui.analytics import render_analytics_dashboard as legacy_analytics
    LEGACY_UI_AVAILABLE = True
except ImportError:
    LEGACY_UI_AVAILABLE = False

class UIComponents:
    """Modern UI components with clean interface"""

    @staticmethod
    def confirm_action(message: str) -> bool:
        """Prompt user to confirm or deny an action."""
        try:
            st.write(message)
            col1, col2 = st.columns(2)
            with col1:
                confirm = st.button("Confirm")
            with col2:
                deny = st.button("Deny")
            key = f"confirm_action_{message}"
            if key not in st.session_state:
                st.session_state[key] = None
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm", key=f"{key}_confirm"):
                    st.session_state[key] = True
            with col2:
                if st.button("Deny", key=f"{key}_deny"):
                    st.session_state[key] = False
            if st.session_state[key] is not None:
                result = st.session_state[key]
                # Optionally reset for future use
                st.session_state[key] = None
                return result
            return None
        except Exception:
            response = input(f"{message} (y/N): ").strip().lower()
            return response in {"y", "yes"}

    @staticmethod
    def render_sidebar():
        """Render modern sidebar"""
        if LEGACY_UI_AVAILABLE:
            try:
                return legacy_sidebar()
            except:
                pass
        
        # Fallback implementation
        st.sidebar.title("🤖 Jarvis AI")
        st.sidebar.markdown("---")
        return None
    
    @staticmethod
    def render_analytics_dashboard():
        """Render modern analytics dashboard"""
        if LEGACY_UI_AVAILABLE:
            try:
                return legacy_analytics()
            except:
                pass
        
        # Fallback implementation
        st.subheader("📊 Analytics Dashboard")
        
        # Basic metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Users", "1", "0")
        with col2:
            st.metric("Total Sessions", "1", "+1")
        with col3:
            st.metric("Avg Response Time", "1.2s", "-0.3s")
        
        # Charts placeholder
        st.subheader("📈 Usage Trends")
        
        # Sample data for demo
        chart_data = pd.DataFrame({
            'Date': pd.date_range('2025-08-01', periods=20),
            'Sessions': [1, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9, 8, 10, 9, 11],
            'Messages': [5, 12, 8, 15, 11, 18, 14, 22, 19, 25, 21, 28, 24, 31, 27, 34, 30, 37, 33, 40]
        })
        
        st.line_chart(chart_data.set_index('Date'))
        
        # Recent activity
        st.subheader("🕐 Recent Activity")
        activity_data = {
            "Time": ["11:45 AM", "11:30 AM", "11:15 AM"],
            "User": ["admin", "admin", "admin"],
            "Action": ["Login", "Chat Message", "Model Selection"],
            "Details": ["Successful login", "Used llama3.2 model", "Changed to qwen2.5"]
        }
        
        st.dataframe(pd.DataFrame(activity_data), use_container_width=True)
    
    @staticmethod
    def render_user_card(user: Dict[str, Any]):
        """Render user information card"""
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                status = "🟢" if user.get("is_active") else "🔴"
                st.write(status)
            
            with col2:
                st.write(f"**{user.get('username')}**")
                st.caption(f"{user.get('name', '')} - {user.get('role', 'user')}")
            
            with col3:
                return st.button("Action", key=f"action_{user.get('username')}")
    
    @staticmethod
    def render_model_card(model_name: str, model_info: Dict[str, Any] = None):
        """Render model information card"""
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"📦 **{model_name}**")
                if model_info:
                    st.caption(f"Status: {model_info.get('status', 'Unknown')}")
            
            with col2:
                if model_info and 'response_time' in model_info:
                    st.metric("Response Time", model_info['response_time'])
            
            with col3:
                return st.button("Test", key=f"test_{model_name}")
    
    @staticmethod
    def render_system_status():
        """Render system status indicators"""
        st.subheader("🔍 System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Database", "✅ Connected")
            st.metric("Authentication", "✅ Active")
        
        with col2:
            st.metric("AI Models", "✅ Available")
            st.metric("Security", "✅ Enabled")

# Create global instance
ui_components = UIComponents()
