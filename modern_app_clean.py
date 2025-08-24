"""
Modern Jarvis AI Application
Clean, modern architecture with full feature support
"""

import streamlit as st
import sys
import logging
from datetime import datetime
import os
import time

from v2.agent.adapters.langgraph_ui import visualizer
from ui.settings_manager import SettingsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Jarvis AI - Modern",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_modern_features():
    """Check if modern Jarvis features are available"""
    try:
        import jarvis
        
        # Check if all major components are available
        features_available = all([
            jarvis.DatabaseManager is not None,
            jarvis.SecurityManager is not None,
            jarvis.JarvisAgent is not None,
            jarvis.get_database_manager is not None,
            jarvis.get_security_manager is not None
        ])
        
        return features_available, jarvis
    except ImportError as e:
        logger.warning(f"Modern jarvis package not available: {e}")
        return False, None

def initialize_modern_components():
    """Initialize modern Jarvis components"""
    try:
        import jarvis
        
        # Initialize database manager
        db_manager = jarvis.get_database_manager()
        
        # Initialize security manager with database
        security_manager = jarvis.get_security_manager(db_manager)
        
        # Initialize agent
        agent = jarvis.get_jarvis_agent()
        
        return db_manager, security_manager, agent
    except Exception as e:
        logger.error(f"Error initializing modern components: {e}")
        return None, None, None

def render_modern_sidebar(security_manager, db_manager):
    """Render modern sidebar"""
    with st.sidebar:
        st.title("🤖 Jarvis AI")
        st.markdown("**Modern Architecture**")
        
        # Authentication section
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = None
        st.session_state.setdefault('show_admin', False)
        st.session_state.setdefault('show_security', False)
        st.session_state.setdefault('show_settings', False)
        
        if not st.session_state.authenticated:
            st.subheader("🔐 Login")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login")
                
                if login_btn and username and password:
                    user = security_manager.authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = user.get('role', 'user')
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            st.success(f"Welcome, {st.session_state.username}!")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.session_state.show_admin = False
                st.session_state.show_security = False
                st.session_state.show_settings = False
                st.rerun()
            
            # User info
            st.markdown("---")
            st.subheader("👤 User Info")
            st.write(f"**Role:** {st.session_state.get('user_role', 'user')}")
            
            # Admin features
            if st.session_state.get('user_role') == 'admin':
                st.markdown("---")
                st.subheader("⚙️ Admin")
                if st.button("User Management"):
                    st.session_state.show_admin = True
                if st.button("Security Dashboard"):
                    st.session_state.show_security = True
                if st.button("Settings"):
                    st.session_state.show_settings = True

def render_modern_chat(agent, db_manager):
    """Render modern chat interface"""
    st.header("💬 Chat with Jarvis")
    
    # Model info
    col1, col2 = st.columns([3, 1])
    with col2:
        st.info(f"Model: {agent.model_name}")
        badge_color = "#28a745" if agent.is_available() else "#dc3545"
        badge_label = "Online" if agent.is_available() else "Offline"
        st.markdown(
            f"<span style='background-color:{badge_color};color:white;padding:0.2em 0.6em;"
            "border-radius:0.25em;font-weight:bold;'>Agent {badge_label}</span>",
            unsafe_allow_html=True,
        )
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for i, (user_msg, ai_msg) in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(user_msg)
        with st.chat_message("assistant"):
            st.write(ai_msg)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            progress = st.progress(0)
            with st.spinner("Thinking..."):
                try:
                    for i in range(100):
                        progress.progress(i + 1)
                        time.sleep(0.01)
                    response = agent.chat(prompt)
                    progress.empty()
                    st.write(response)

                    # Visualisation features
                    indicators = visualizer.get_team_indicators()
                    if indicators:
                        st.markdown("**Team Indicators**")
                        cols = st.columns(len(indicators))
                        for col, info in zip(cols, indicators):
                            col.markdown(f"{info['icon']} {info['label']}")

                    dead_ends = visualizer.get_dead_ends()
                    if dead_ends:
                        with st.expander("🛑 Dead-End Shelf"):
                            st.write("\n".join(dead_ends))

                    try:
                        png = visualizer.export("png")
                        if png:
                            st.image(png)
                    except Exception:
                        pass

                    # Save to session history
                    st.session_state.chat_history.append((prompt, response))

                    # Save to database if user is authenticated
                    if st.session_state.get('authenticated') and st.session_state.get('username'):
                        db_manager.save_chat_message(
                            st.session_state.username,
                            prompt,
                            response,
                            agent.model_name
                        )
                        
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append((prompt, error_msg))

def render_admin_panel(db_manager, security_manager):
    """Render admin panel"""
    st.header("⚙️ Administration Panel")
    
    tabs = st.tabs(["Users", "Security", "System"])
    
    with tabs[0]:
        st.subheader("👥 User Management")
        
        # Get all users
        users = db_manager.get_all_users()
        
        if users:
            import pandas as pd
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")
        
        # Create new user
        st.subheader("➕ Create New User")
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("Create User"):
                if new_username and new_password:
                    success = security_manager.create_user(
                        new_username, new_password, new_email, new_role
                    )
                    if success:
                        st.success(f"User {new_username} created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create user")
                else:
                    st.error("Username and password are required")
    
    with tabs[1]:
        st.subheader("🔒 Security Dashboard")
        
        # Security info
        security_info = security_manager.get_security_info()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Rate Limits", security_info['active_rate_limits'])
            st.metric("Failed Attempts", security_info['failed_attempts'])
        
        with col2:
            st.metric("Max Attempts", security_info['max_attempts'])
            st.metric("Lockout Duration", f"{security_info['lockout_duration']}s")
    
    with tabs[2]:
        st.subheader("🖥️ System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Application Info:**")
            st.write(f"- Version: 2.0.0")
            st.write(f"- Mode: Full Feature Mode")
            st.write(f"- Database: SQLite")
            
        with col2:
            st.write("**Available Components:**")
            st.write("- ✅ Modern Database Manager")
            st.write("- ✅ Security Manager")
            st.write("- ✅ Jarvis Agent")

def create_default_admin(security_manager):
    """Create default admin user if none exists"""
    try:
        # Check if any admin users exist
        users = security_manager.db_manager.get_all_users()
        admin_users = [u for u in users if u.get('role') == 'admin']
        
        if not admin_users:
            # Create default admin
            success = security_manager.create_user(
                "admin", "admin123", "admin@jarvis.ai", "admin"
            )
            if success:
                st.info("🔧 Default admin user created: admin/admin123")
                logger.info("Default admin user created")
            else:
                logger.warning("Failed to create default admin user")
                
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")

def main():
    """Main application"""
    
    # Check for modern features
    features_available, jarvis_module = check_modern_features()
    
    if not features_available:
        st.error("🚨 Modern Jarvis features not available. Running in basic mode.")
        st.info("Please check your installation and ensure all components are properly configured.")
        return
    
    # Initialize components
    db_manager, security_manager, agent = initialize_modern_components()
    
    if not all([db_manager, security_manager, agent]):
        st.error("🚨 Failed to initialize modern components")
        return
    
    # Create default admin if needed
    create_default_admin(security_manager)
    
    # Show feature status
    st.success("🚀 **Full Feature Mode** - All modern components loaded successfully!")
    
    # Render sidebar
    render_modern_sidebar(security_manager, db_manager)

    # Main content
    manager = SettingsManager()
    if st.session_state.get('show_settings') and st.session_state.get('user_role') == 'admin':
        manager.render_settings_ui()
        if st.button("← Back to Chat"):
            st.session_state.show_settings = False
            st.rerun()
    elif st.session_state.get('show_admin') and st.session_state.get('user_role') == 'admin':
        render_admin_panel(db_manager, security_manager)
        if st.button("← Back to Chat"):
            st.session_state.show_admin = False
            st.rerun()
    else:
        render_modern_chat(agent, db_manager)
    
    # Footer
    st.markdown("---")
    st.markdown("🤖 **Jarvis AI v2.0** - Modern Architecture | Built with Streamlit")

if __name__ == "__main__":
    main()
