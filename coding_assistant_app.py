"""
Jarvis AI - Advanced Coding Assistant
Enhanced web interface with deep coding capabilities
"""

import streamlit as st
import sys
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Jarvis AI - Coding Assistant",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_coding_features():
    """Check if coding agent features are available"""
    try:
        import jarvis
        
        # Check if coding components are available
        features_available = all([
            jarvis.DatabaseManager is not None,
            jarvis.SecurityManager is not None,
            jarvis.JarvisAgent is not None,
            jarvis.CodingAgent is not None,
            jarvis.get_coding_agent is not None
        ])
        
        return features_available, jarvis
    except ImportError as e:
        logger.warning(f"Coding features not available: {e}")
        return False, None

def initialize_coding_components():
    """Initialize coding-enhanced Jarvis components"""
    try:
        import jarvis
        
        # Initialize core components
        db_manager = jarvis.get_database_manager()
        security_manager = jarvis.get_security_manager(db_manager)
        base_agent = jarvis.get_jarvis_agent()
        
        # Initialize coding agent with workspace context
        workspace_path = str(Path.cwd())
        coding_agent = jarvis.get_coding_agent(base_agent, workspace_path)
        
        return db_manager, security_manager, base_agent, coding_agent
    except Exception as e:
        logger.error(f"Error initializing coding components: {e}")
        return None, None, None, None

def render_coding_sidebar(security_manager, db_manager, coding_agent):
    """Render enhanced sidebar with coding features"""
    with st.sidebar:
        st.title("👨‍💻 Jarvis AI")
        st.markdown("**Advanced Coding Assistant**")
        
        # Authentication section (same as before)
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = None
        
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
                st.rerun()
            
            # Coding mode selection
            st.markdown("---")
            st.subheader("🎯 Coding Mode")
            
            coding_modes = [
                "💬 General Chat",
                "🔍 Code Review", 
                "🐛 Debug Assistant",
                "⚡ Code Generator",
                "🏗️ Architecture Advisor",
                "📚 Learning Mentor",
                "🧪 Test Generator",
                "♻️ Code Refactoring",
                "📊 Performance Analysis"
            ]
            
            selected_mode = st.selectbox("Select Mode", coding_modes, key="coding_mode")
            st.session_state.current_mode = selected_mode
            
            # Workspace info
            st.markdown("---")
            st.subheader("📁 Workspace")
            
            # Current workspace display
            current_workspace = getattr(coding_agent, 'workspace_path', Path.cwd())
            st.write(f"**Current:** `{current_workspace}`")
            
            # Workspace path input
            with st.expander("Change Workspace"):
                new_workspace = st.text_input(
                    "Project Path", 
                    value=str(current_workspace),
                    help="Enter the full path to your project directory"
                )
                if st.button("Set Workspace") and new_workspace:
                    if Path(new_workspace).exists():
                        coding_agent.workspace_path = Path(new_workspace)
                        st.success(f"Workspace changed to: {new_workspace}")
                        st.rerun()
                    else:
                        st.error("Path does not exist!")
            
            if st.button("Analyze Codebase"):
                with st.spinner("Analyzing codebase..."):
                    analysis = coding_agent.analyze_codebase()
                    st.session_state.codebase_analysis = analysis
                    st.success("Analysis complete!")
            
            # Show codebase summary if available
            if hasattr(st.session_state, 'codebase_analysis'):
                analysis = st.session_state.codebase_analysis
                with st.expander("Codebase Analysis", expanded=False):
                    st.write("**Languages:**")
                    for lang, count in analysis['languages'].items():
                        st.write(f"- {lang}: {count} files")
                    
                    st.write("**Project Type:**")
                    st.write(coding_agent._infer_project_type(analysis))
                    
                    if analysis['dependencies']:
                        st.write("**Dependencies:**")
                        for dep in analysis['dependencies'][:10]:
                            st.write(f"- {dep}")
                    
                    st.write("**Structure:**")
                    for dir_name in analysis['structure']['directories'][:10]:
                        st.write(f"📁 {dir_name}")
                    
                    for config in analysis['structure']['config_files']:
                        st.write(f"⚙️ {config}")
            
            # Admin features
            if st.session_state.get('user_role') == 'admin':
                st.markdown("---")
                st.subheader("⚙️ Admin")
                if st.button("User Management"):
                    st.session_state.show_admin = True

def render_coding_interface(base_agent, coding_agent, db_manager):
    """Render the main coding interface"""
    current_mode = st.session_state.get('current_mode', '💬 General Chat')
    
    # Mode-specific headers and instructions
    mode_configs = {
        "💬 General Chat": {
            "header": "💬 General AI Assistant",
            "placeholder": "Ask me anything about coding or general topics...",
            "instructions": "General conversation mode. Ask questions, get explanations, or discuss any topic."
        },
        "🔍 Code Review": {
            "header": "🔍 Code Review Assistant", 
            "placeholder": "Paste your code here for review...",
            "instructions": "Paste code for comprehensive review including quality, security, and best practices analysis."
        },
        "🐛 Debug Assistant": {
            "header": "🐛 Debug Helper",
            "placeholder": "Describe your error or paste error messages...",
            "instructions": "Describe bugs, paste error messages, or share problematic code for debugging help."
        },
        "⚡ Code Generator": {
            "header": "⚡ Code Generator",
            "placeholder": "Describe what code you need...",
            "instructions": "Describe the functionality you need and I'll generate clean, documented code."
        },
        "🏗️ Architecture Advisor": {
            "header": "🏗️ Architecture Consultant",
            "placeholder": "Ask about system design, patterns, or architecture decisions...",
            "instructions": "Get advice on software architecture, design patterns, and technical decisions."
        },
        "📚 Learning Mentor": {
            "header": "📚 Coding Mentor", 
            "placeholder": "What coding concept would you like to learn?",
            "instructions": "Learn coding concepts, get explanations, and receive guided tutorials."
        },
        "🧪 Test Generator": {
            "header": "🧪 Test Case Generator",
            "placeholder": "Paste code to generate tests for...",
            "instructions": "Paste your code and I'll generate comprehensive test cases."
        },
        "♻️ Code Refactoring": {
            "header": "♻️ Code Refactoring Assistant",
            "placeholder": "Paste code to refactor...",
            "instructions": "Paste code for refactoring suggestions and improved implementations."
        },
        "📊 Performance Analysis": {
            "header": "📊 Performance Analyzer",
            "placeholder": "Paste code for performance analysis...",
            "instructions": "Analyze code performance, complexity, and get optimization suggestions."
        }
    }
    
    config = mode_configs.get(current_mode, mode_configs["💬 General Chat"])
    
    st.header(config["header"])
    st.info(config["instructions"])
    
    # Language selection for coding modes
    if current_mode != "💬 General Chat":
        col1, col2 = st.columns([3, 1])
        with col2:
            language = st.selectbox(
                "Language",
                ["python", "javascript", "typescript", "java", "cpp", "c", "csharp", "go", "rust"],
                key="selected_language"
            )
    
    # Initialize chat history for current mode
    history_key = f"chat_history_{current_mode.replace(' ', '_').replace('💬', '').replace('🔍', '').replace('🐛', '').replace('⚡', '').replace('🏗️', '').replace('📚', '').replace('🧪', '').replace('♻️', '').replace('📊', '').strip()}"
    
    if history_key not in st.session_state:
        st.session_state[history_key] = []
    
    # Display chat history for current mode
    for i, (user_msg, ai_msg) in enumerate(st.session_state[history_key]):
        with st.chat_message("user"):
            st.write(user_msg)
        with st.chat_message("assistant"):
            st.write(ai_msg)
    
    # Chat input
    if prompt := st.chat_input(config["placeholder"]):
        # Add user message to chat history
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response based on mode
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    # Route to appropriate coding agent method
                    if current_mode == "💬 General Chat":
                        response = base_agent.chat(prompt)
                    elif current_mode == "🔍 Code Review":
                        response = coding_agent.code_review(prompt, language)
                    elif current_mode == "🐛 Debug Assistant":
                        response = coding_agent.debug_assistance(prompt, language=language)
                    elif current_mode == "⚡ Code Generator":
                        response = coding_agent.generate_code(prompt, language)
                    elif current_mode == "🏗️ Architecture Advisor":
                        response = coding_agent.architecture_advice(prompt)
                    elif current_mode == "📚 Learning Mentor":
                        response = coding_agent.explain_code(prompt, language)
                    elif current_mode == "🧪 Test Generator":
                        response = coding_agent.create_tests(prompt, language)
                    elif current_mode == "♻️ Code Refactoring":
                        response = coding_agent.refactor_code(prompt, language)
                    elif current_mode == "📊 Performance Analysis":
                        response = coding_agent.performance_analysis(prompt, language)
                    else:
                        response = base_agent.chat(prompt)
                    
                    st.write(response)
                    
                    # Save to session history
                    st.session_state[history_key].append((prompt, response))
                    
                    # Save to database if user is authenticated
                    if st.session_state.get('authenticated') and st.session_state.get('username'):
                        db_manager.save_chat_message(
                            st.session_state.username, 
                            f"[{current_mode}] {prompt}", 
                            response,
                            base_agent.model_name
                        )
                        
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[history_key].append((prompt, error_msg))

def render_coding_capabilities(coding_agent):
    """Render coding capabilities overview"""
    st.header("🚀 Coding Assistant Capabilities")
    
    capabilities = coding_agent.get_coding_capabilities()
    
    cols = st.columns(3)
    
    for i, (category, features) in enumerate(capabilities.items()):
        with cols[i % 3]:
            st.subheader(category.replace('_', ' ').title())
            for feature in features:
                st.write(f"• {feature}")

def create_default_admin(security_manager):
    """Create default admin user if none exists"""
    try:
        users = security_manager.db_manager.get_all_users()
        admin_users = [u for u in users if u.get('role') == 'admin']
        
        if not admin_users:
            success = security_manager.create_user(
                "admin", "admin123", "admin@jarvis.ai", "admin"
            )
            if success:
                st.info("🔧 Default admin user created: admin/admin123")
                logger.info("Default admin user created")
                
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")

def main():
    """Main application"""
    
    # Check for coding features
    features_available, jarvis_module = check_coding_features()
    
    if not features_available:
        st.error("🚨 Coding features not available. Please check your installation.")
        return
    
    # Initialize components
    db_manager, security_manager, base_agent, coding_agent = initialize_coding_components()
    
    if not all([db_manager, security_manager, base_agent, coding_agent]):
        st.error("🚨 Failed to initialize coding components")
        return
    
    # Create default admin if needed
    create_default_admin(security_manager)
    
    # Show feature status
    st.success("🚀 **Coding Assistant Mode** - Advanced AI coding features enabled!")
    
    # Render sidebar
    render_coding_sidebar(security_manager, db_manager, coding_agent)
    
    # Main content
    if st.session_state.get('show_admin') and st.session_state.get('user_role') == 'admin':
        from modern_app_clean import render_admin_panel
        render_admin_panel(db_manager, security_manager)
        if st.button("← Back to Coding Assistant"):
            st.session_state.show_admin = False
            st.rerun()
    elif st.session_state.get('show_capabilities'):
        render_coding_capabilities(coding_agent)
        if st.button("← Back to Chat"):
            st.session_state.show_capabilities = False
            st.rerun()
    else:
        render_coding_interface(base_agent, coding_agent, db_manager)
    
    # Add capabilities button
    if st.sidebar.button("📋 View All Capabilities"):
        st.session_state.show_capabilities = True
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("👨‍💻 **Jarvis AI Coding Assistant v2.0** - Your AI Programming Partner | Built with Streamlit")

if __name__ == "__main__":
    main()
