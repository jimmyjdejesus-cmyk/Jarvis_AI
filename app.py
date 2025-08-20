"""
Jarvis AI - Main Application
A privacy-first modular AI development assistant
"""

import streamlit as st
import os
import sys
import json
import time
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Jarvis AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add legacy path to sys.path for imports
current_dir = Path(__file__).parent
legacy_dir = current_dir / "legacy"
sys.path.insert(0, str(legacy_dir))
sys.path.insert(0, str(current_dir))

# Import with fallbacks
try:
    from database.database import init_db, get_user
    from agent.security import hash_password, verify_password, log_security_event
    from ui import sidebar, render_analytics_dashboard
    from scripts import get_available_models
    FULL_FEATURES_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Some features unavailable: {e}")
    FULL_FEATURES_AVAILABLE = False
    
    # Minimal fallback functions
    import sqlite3
    
    def init_db():
        """Initialize basic database"""
        conn = sqlite3.connect('janus_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_user(username):
        """Get user from database"""
        conn = sqlite3.connect('janus_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, name, email, hashed_password, role, is_active FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "name": result[2] if result[2] else result[1].title(),
                "email": result[3],
                "hashed_password": result[4],
                "role": result[5],
                "is_active": bool(result[6])
            }
        return None
    
    def hash_password(password):
        """Simple password hashing fallback"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(password, hashed):
        """Simple password verification fallback"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def log_security_event(event_type, username=None, details=None):
        """Log security events"""
        st.info(f"Security Event: {event_type}")
    
    def sidebar():
        """Simple sidebar fallback"""
        return None
    
    def render_analytics_dashboard():
        """Simple analytics fallback"""
        st.subheader("📊 Analytics")
        st.info("Analytics dashboard unavailable in fallback mode")
    
    def get_available_models():
        """Simple model list fallback"""
        return ["llama3.2", "qwen2.5", "gemma2"]

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Initialize session state
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

def create_default_admin():
    """Create default admin user if none exists"""
    try:
        admin_user = get_user("admin")
        if not admin_user:
            import sqlite3
            conn = sqlite3.connect('janus_database.db')
            cursor = conn.cursor()
            
            # Create admin user with proper fields
            hashed_pw = hash_password("admin123")
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (username, name, email, hashed_password, role, is_active, is_verified) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("admin", "Administrator", "admin@localhost", hashed_pw, "admin", 1, 1))
            
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Failed to create admin user: {e}")
    return False

def login_form():
    """Display login form"""
    st.sidebar.title("🔐 Jarvis AI Login")
    
    if st.session_state.user:
        st.sidebar.success(f"Welcome, {st.session_state.user}!")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.user_data = {}
            st.session_state.is_admin = False
            st.session_state.user_role = "user"
            st.rerun()
        return True
    
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button and username and password:
            user = get_user(username)
            
            if user and user.get("is_active"):
                if verify_password(password, user["hashed_password"]):
                    st.session_state.user = username
                    st.session_state.user_data = user
                    st.session_state.is_admin = (user.get("role") == "admin")
                    st.session_state.user_role = user.get("role", "user")
                    
                    log_security_event("LOGIN_SUCCESS", username=username)
                    st.success(f"Welcome, {user.get('name', username)}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    log_security_event("LOGIN_FAILED", username=username)
            else:
                st.error("User not found or inactive")
    
    # Show default admin info
    if not get_user("admin"):
        st.sidebar.info("🔧 **First Time Setup**")
        if st.sidebar.button("Create Admin User"):
            if create_default_admin():
                st.sidebar.success("✅ Admin user created!")
                st.sidebar.info("Username: **admin**\nPassword: **admin123**")
            else:
                st.sidebar.error("Failed to create admin user")
    
    return False

def admin_panel():
    """Simple admin panel"""
    st.header("🔧 Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("Access denied. Admin privileges required.")
        return
    
    tabs = st.tabs(["👥 Users", "🤖 Models", "📊 System"])
    
    with tabs[0]:
        st.subheader("User Management")
        
        # List users
        try:
            import sqlite3
            conn = sqlite3.connect('janus_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT username, name, role, is_active FROM users")
            users = cursor.fetchall()
            conn.close()
            
            if users:
                for username, name, role, is_active in users:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        status = "🟢" if is_active else "🔴"
                        display_name = name if name else username
                        st.write(f"{status} **{username}** ({display_name}) - {role}")
                    with col2:
                        if st.button(f"Toggle", key=f"toggle_{username}"):
                            # Toggle user active status
                            new_status = 0 if is_active else 1
                            conn = sqlite3.connect('janus_database.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET is_active = ? WHERE username = ?", 
                                         (new_status, username))
                            conn.commit()
                            conn.close()
                            st.rerun()
            else:
                st.info("No users found")
        except Exception as e:
            st.error(f"Error loading users: {e}")
    
    with tabs[1]:
        st.subheader("Model Management")
        
        try:
            models = get_available_models()
            if models:
                st.success(f"Found {len(models)} models:")
                for model in models:
                    st.write(f"📦 {model}")
            else:
                st.warning("No models found")
        except Exception as e:
            st.error(f"Error loading models: {e}")
        
        # Test Ollama connection
        if st.button("🔄 Test Ollama Connection"):
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.ok:
                    st.success("✅ Ollama connection successful")
                else:
                    st.error(f"❌ Ollama connection failed: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Ollama connection failed: {e}")
    
    with tabs[2]:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Features Status", "Basic" if not FULL_FEATURES_AVAILABLE else "Full")
            st.metric("Database", "Connected" if os.path.exists('janus_database.db') else "Not Found")
        
        with col2:
            st.metric("Current User", st.session_state.user or "None")
            st.metric("User Role", st.session_state.user_role.title())

def chat_interface():
    """Main chat interface"""
    st.header("🤖 Jarvis AI Assistant")
    
    if not st.session_state.user:
        st.info("👈 Please login to use the AI assistant")
        return
    
    # Model selection
    models = get_available_models()
    selected_model = st.selectbox("Select Model:", models, index=0)
    
    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask Jarvis AI anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Simple echo response for now
                if FULL_FEATURES_AVAILABLE:
                    response = f"I received your message: '{prompt}' (using {selected_model}). Full AI integration would be here."
                else:
                    response = f"Echo response: {prompt} (Basic mode - using {selected_model})"
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    """Main application"""
    st.title("🤖 Jarvis AI")
    st.caption("Privacy-first modular AI development assistant")
    
    # Handle login
    is_logged_in = login_form()
    
    if is_logged_in:
        # Sidebar navigation
        st.sidebar.divider()
        
        page = st.sidebar.selectbox(
            "Navigation",
            ["💬 Chat", "📊 Analytics", "🔧 Admin Panel"] if st.session_state.is_admin 
            else ["💬 Chat", "📊 Analytics"]
        )
        
        # Page routing
        if page == "💬 Chat":
            chat_interface()
        elif page == "📊 Analytics":
            render_analytics_dashboard()
        elif page == "🔧 Admin Panel" and st.session_state.is_admin:
            admin_panel()
    else:
        # Welcome page for non-logged in users
        st.info("### Welcome to Jarvis AI!")
        st.write("A privacy-first AI assistant that runs entirely on your local machine.")
        
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
        
        st.divider()
        
        if FULL_FEATURES_AVAILABLE:
            st.success("✅ All features are available!")
        else:
            st.warning("⚠️ Running in basic mode. Some features may be limited.")
        
        # System status
        with st.expander("🔍 System Status"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Database:**", "✅" if os.path.exists('janus_database.db') else "❌")
                st.write("**Models:**", f"✅ {len(get_available_models())} available")
            with col2:
                st.write("**Features:**", "✅ Full" if FULL_FEATURES_AVAILABLE else "⚠️ Basic")
                st.write("**Security:**", "✅ Enabled")

if __name__ == "__main__":
    main()
