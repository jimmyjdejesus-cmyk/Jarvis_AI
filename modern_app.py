"""
Jarvis AI - Modern Web Application
Clean architecture with full feature support
"""

import streamlit as st
import os
import sys
import time
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Jarvis AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add jarvis package to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import modern Jarvis components
try:
    from jarvis.database.manager import db_manager
    from jarvis.auth.security import security_manager
    from jarvis.models.client import model_client
    from jarvis.ui.components import ui_components
    from jarvis.core.agent import jarvis_agent
    
    JARVIS_MODERN_AVAILABLE = True
    st.success("🚀 **Jarvis AI - Full Feature Mode**")
    
except ImportError as e:
    st.error(f"⚠️ Modern features unavailable: {e}")
    JARVIS_MODERN_AVAILABLE = False
    
    # Basic fallback (minimal implementation for testing)
    class MockManager:
        def init_database(self): pass
        def get_user(self, username): return None
        def create_user(self, *args): return True
        def get_all_users(self): return []
        def log_security_event(self, *args): pass
        def get_user_preferences(self, username): return {}
        def save_user_preference(self, *args): pass
    
    class MockSecurity:
        def hash_password(self, password): return f"hashed_{password}"
        def verify_password(self, password, hashed): return hashed == f"hashed_{password}"
        def is_rate_limited(self, *args): return False
        def log_security_event(self, *args): pass
    
    class MockModels:
        def get_available_models(self): return ["llama3.2", "qwen2.5", "gemma2"]
        def test_connection(self): return True
        def generate_response(self, model, prompt, stream=False): 
            return f"Mock response to: {prompt} (using {model})"
    
    class MockUI:
        def render_analytics_dashboard(self):
            st.subheader("📊 Basic Analytics")
            st.info("Full analytics available in modern mode")
    
    class MockAgent:
        def __init__(self): self.model_name = "llama3.2"
        def chat(self, message): return f"Mock AI: {message}"
        def set_model(self, model): self.model_name = model
    
    # Create mock instances
    db_manager = MockManager()
    security_manager = MockSecurity()
    model_client = MockModels()
    ui_components = MockUI()
    jarvis_agent = MockAgent()

# Initialize database
try:
    db_manager.init_database()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = {}
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "user"
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = "llama3.2"

init_session_state()

def create_default_admin():
    """Create default admin user if none exists"""
    try:
        admin_user = db_manager.get_user("admin")
        if not admin_user:
            hashed_pw = security_manager.hash_password("admin123")
            success = db_manager.create_user(
                username="admin",
                name="Administrator", 
                email="admin@localhost",
                hashed_password=hashed_pw,
                role="admin"
            )
            return success
    except Exception as e:
        st.error(f"Failed to create admin user: {e}")
    return False

def render_login_sidebar():
    """Render the login sidebar"""
    st.sidebar.title("🔐 Jarvis AI Login")
    
    if st.session_state.user:
        st.sidebar.success(f"Welcome, {st.session_state.user}!")
        
        # User info
        user_data = st.session_state.user_data
        st.sidebar.info(f"**Role:** {user_data.get('role', 'user').title()}")
        
        # Logout button
        if st.sidebar.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.user_data = {}
            st.session_state.is_admin = False
            st.session_state.user_role = "user"
            st.session_state.messages = []
            st.rerun()
        return True
    
    # Login form
    with st.sidebar.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button("🔑 Login")
        
        if login_button and username and password:
            # Check rate limiting
            if security_manager.is_rate_limited(f"login_{username}"):
                st.error("⏰ Too many login attempts. Please try again later.")
                security_manager.log_security_event("RATE_LIMITED", username=username)
                return False
            
            # Get user
            user = db_manager.get_user(username)
            
            if user and user.get("is_active"):
                if security_manager.verify_password(password, user["hashed_password"]):
                    # Successful login
                    st.session_state.user = username
                    st.session_state.user_data = user
                    st.session_state.is_admin = (user.get("role") == "admin")
                    st.session_state.user_role = user.get("role", "user")
                    
                    security_manager.log_security_event("LOGIN_SUCCESS", username=username)
                    st.success(f"✅ Welcome, {user.get('name', username)}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    # Failed login
                    st.error("❌ Invalid credentials")
                    security_manager.log_security_event("LOGIN_FAILED", username=username)
            else:
                st.error("❌ User not found or inactive")
    
    # First time setup
    st.sidebar.divider()
    st.sidebar.subheader("🔧 First Time Setup")
    
    if not db_manager.get_user("admin"):
        st.sidebar.info("No admin user found!")
        if st.sidebar.button("👑 Create Admin User"):
            if create_default_admin():
                st.sidebar.success("✅ Admin user created!")
                st.sidebar.info("**Username:** admin\n**Password:** admin123")
            else:
                st.sidebar.error("❌ Failed to create admin user")
    else:
        st.sidebar.success("✅ Admin user exists")
    
    return False

def render_chat_interface():
    """Render the main chat interface"""
    st.header("🤖 Jarvis AI Assistant")
    
    if not st.session_state.user:
        st.info("👈 Please login to use the AI assistant")
        
        # Welcome content for non-logged in users
        st.markdown("### Welcome to Jarvis AI!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🔐 Secure")
            st.write("All data stays on your machine")
        with col2:
            st.subheader("🎯 Intelligent") 
            st.write("Powered by advanced AI models")
        with col3:
            st.subheader("🔧 Customizable")
            st.write("Extensible and configurable")
        
        return
    
    # Model selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Chat with {st.session_state.selected_model}")
    with col2:
        models = model_client.get_available_models()
        selected_model = st.selectbox(
            "Model:",
            models,
            index=models.index(st.session_state.selected_model) if st.session_state.selected_model in models else 0,
            key="model_selector"
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            jarvis_agent.set_model(selected_model)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask Jarvis AI anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    if JARVIS_MODERN_AVAILABLE:
                        response = jarvis_agent.chat(prompt)
                    else:
                        response = model_client.generate_response(
                            st.session_state.selected_model, 
                            prompt
                        )
                    
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def render_admin_panel():
    """Render the admin panel"""
    st.header("🔧 Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("❌ Access denied. Admin privileges required.")
        return
    
    tabs = st.tabs(["👥 Users", "🤖 Models", "📊 Analytics", "⚙️ System"])
    
    with tabs[0]:
        st.subheader("User Management")
        
        # User list
        users = db_manager.get_all_users()
        if users:
            for user in users:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    status = "🟢" if user.get("is_active") else "🔴"
                    st.write(f"{status} **{user['username']}** ({user.get('name', 'N/A')}) - {user['role']}")
                with col2:
                    st.write(f"Active: {user.get('is_active', False)}")
                with col3:
                    if st.button("👤 Details", key=f"details_{user['username']}"):
                        st.json(user)
        else:
            st.info("No users found")
    
    with tabs[1]:
        st.subheader("Model Management")
        
        # Connection test
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Test Ollama Connection"):
                if model_client.test_connection():
                    st.success("✅ Ollama connection successful")
                else:
                    st.error("❌ Ollama connection failed")
        
        with col2:
            if st.button("📋 Refresh Models"):
                st.rerun()
        
        # Model list
        models = model_client.get_available_models()
        st.write(f"**Available Models:** {len(models)}")
        
        for model in models:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📦 {model}")
            with col2:
                if st.button("🏥 Health Check", key=f"health_{model}"):
                    if JARVIS_MODERN_AVAILABLE:
                        health = model_client.health_check_model(model)
                        st.json(health)
                    else:
                        st.info("Health check available in full mode")
            with col3:
                if st.button("ℹ️ Info", key=f"info_{model}"):
                    if JARVIS_MODERN_AVAILABLE:
                        info = model_client.get_model_info(model)
                        if info:
                            st.json(info)
                        else:
                            st.warning("No info available")
                    else:
                        st.info("Model info available in full mode")
    
    with tabs[2]:
        st.subheader("Analytics & Monitoring")
        ui_components.render_analytics_dashboard()
    
    with tabs[3]:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Feature Mode", "Full" if JARVIS_MODERN_AVAILABLE else "Basic")
            st.metric("Database", "Connected" if os.path.exists('janus_database.db') else "Not Found")
            st.metric("Models Available", len(model_client.get_available_models()))
        
        with col2:
            st.metric("Current User", st.session_state.user or "None")
            st.metric("User Role", st.session_state.user_role.title())
            st.metric("Active Sessions", "1")
        
        # System status
        if JARVIS_MODERN_AVAILABLE:
            ui_components.render_system_status()

def main():
    """Main application"""
    # App header
    st.title("🤖 Jarvis AI")
    
    # Feature mode indicator
    if JARVIS_MODERN_AVAILABLE:
        st.success("🚀 **Full Feature Mode** - All systems operational")
    else:
        st.warning("⚙️ **Basic Mode** - Some features limited")
    
    # Handle login
    is_logged_in = render_login_sidebar()
    
    if is_logged_in:
        # Navigation
        st.sidebar.divider()
        st.sidebar.subheader("📍 Navigation")
        
        pages = ["💬 Chat", "📊 Analytics"]
        if st.session_state.is_admin:
            pages.append("🔧 Admin Panel")
        
        page = st.sidebar.selectbox("Go to:", pages)
        
        # Page routing
        if page == "💬 Chat":
            render_chat_interface()
        elif page == "📊 Analytics":
            st.header("📊 Analytics Dashboard")
            ui_components.render_analytics_dashboard()
        elif page == "🔧 Admin Panel" and st.session_state.is_admin:
            render_admin_panel()
    else:
        # Landing page
        render_chat_interface()  # Shows welcome message when not logged in

if __name__ == "__main__":
    main()
