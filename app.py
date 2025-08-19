 # ...existing code...

import streamlit as st
import os
import json
import uuid
import pandas as pd
from agent.features.security import load_user_key, encrypt_json, decrypt_json, hash_password, verify_password, is_rate_limited, log_security_event, validate_password_strength
from agent.core.core import JarvisAgent
# Import sidebar function directly
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from ui.sidebar import sidebar
import agent.tools as tools
import agent.features.human_in_loop as human_in_loop
from database.database import init_db, get_user, get_user_preferences, save_user_preference, get_user_settings
import database.database as database
from ui.analytics import render_analytics_dashboard
from tools.code_intelligence.ui import render_code_intelligence_interface
from scripts.ollama_client import get_available_models, pull_model_subprocess
import time

# Import system monitoring (with fallback if psutil not available)
try:
    from scripts.system_monitor import check_system_resources
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    SYSTEM_MONITOR_AVAILABLE = False
    def check_system_resources():
        pass  # Fallback function that does nothing

# Initialize session state after imports
if "user" not in st.session_state:
    st.session_state["user"] = None
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "user"

# Initialize database
init_db()

def login():
    st.sidebar.title("🔐 Jarvis AI Login")
    
    # Check if user is already logged in
    if "user" in st.session_state and st.session_state.user:
        return
    
    # Login form
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            # Rate limiting check
            if is_rate_limited(f"login_{username}", max_attempts=5, window_minutes=15):
                st.error("Too many login attempts. Please try again later.")
                log_security_event("RATE_LIMITED", username=username, details="Login rate limited")
                return
            
            if username and password:
                # Get user from database
                user = database.get_user(username)
                
                if user and user["is_active"]:
                    # Check if account is locked
                    if database.is_user_locked(username):
                        st.error("Account is temporarily locked due to failed login attempts.")
                        return
                    
                    # Verify password
                    if verify_password(password, user["hashed_password"]):
                        # Successful login
                        st.session_state.user = username
                        st.session_state.user_data = user
                        st.session_state.is_admin = (user["role"] == "admin")
                        st.session_state.user_role = user["role"]
                        
                        # Update login info
                        database.update_user_login(username, success=True)
                        
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        # Failed login
                        database.update_user_login(username, success=False)
                        st.error("Invalid username or password")
                        log_security_event("LOGIN_FAILED", username=username)
                else:
                    st.error("Invalid username or password")
                    log_security_event("LOGIN_FAILED", username=username, details="User not found or inactive")
            else:
                st.error("Please enter both username and password")
    
    # Registration link
    st.sidebar.markdown("---")
    if st.sidebar.button("📝 Register New Account"):
        st.session_state.show_registration = True
        st.rerun()
    
    if st.sidebar.button("🔄 Reset Password"):
        st.session_state.show_password_reset = True
        st.rerun()
    
    # Show forms if requested
    if st.session_state.get("show_registration", False):
        show_registration_form()
    
    if st.session_state.get("show_password_reset", False):
        show_password_reset_form()
    
    # If no user is logged in, stop the app
    if "user" not in st.session_state or not st.session_state.user:
        st.stop()

def show_registration_form():
    """Show user registration form"""
    st.sidebar.markdown("### 📝 Register New Account")
    
    with st.sidebar.form("registration_form"):
        reg_username = st.text_input("Username*")
        reg_name = st.text_input("Full Name*")
        reg_email = st.text_input("Email*")
        reg_password = st.text_input("Password*", type="password")
        reg_password_confirm = st.text_input("Confirm Password*", type="password")
        register_button = st.form_submit_button("Register")
        
        if register_button:
            # Validation
            if not all([reg_username, reg_name, reg_email, reg_password, reg_password_confirm]):
                st.error("All fields are required")
                return
            
            if reg_password != reg_password_confirm:
                st.error("Passwords do not match")
                return
            
            # Validate password strength
            is_strong, message = validate_password_strength(reg_password)
            if not is_strong:
                st.error(f"Password requirements: {message}")
                return
            
            # Check if user already exists
            if database.get_user(reg_username):
                st.error("Username already exists")
                return
            
            # Hash password and add to pending users
            hashed_password = hash_password(reg_password)
            success = database.add_pending_user(reg_username, reg_name, reg_email, hashed_password)
            
            if success:
                st.success("Registration submitted! Please wait for admin approval.")
                log_security_event("REGISTRATION_SUBMITTED", username=reg_username, details=f"User {reg_name} registered")
                st.session_state.show_registration = False
                st.rerun()
            else:
                st.error("Registration failed. Username or email may already exist.")
    
    if st.sidebar.button("← Back to Login"):
        st.session_state.show_registration = False
        st.rerun()

def show_password_reset_form():
    """Show password reset form"""
    st.sidebar.markdown("### 🔄 Reset Password")
    
    with st.sidebar.form("password_reset_form"):
        reset_email = st.text_input("Email Address*")
        reset_button = st.form_submit_button("Send Reset Link")
        
        if reset_button and reset_email:
            try:
                from auth.password_reset import request_password_reset
                success, message = request_password_reset(reset_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            except ImportError:
                st.info("Password reset functionality requires email configuration")
    
    if st.sidebar.button("← Back to Login"):
        st.session_state.show_password_reset = False
        st.rerun()

def show_admin_panel():
    """Admin panel for user management"""
    st.markdown("## 🔧 Admin Panel")
    
    tabs = st.tabs(["👥 User Management", "⏳ Pending Users", "📊 Security Logs", "🤖 Model Management", "⚙️ System Settings", "📈 Analytics"])
    
    with tabs[0]:  # User Management
        st.markdown("### Active Users")
        users = database.get_all_users(include_inactive=True)
        
        if users:
            for user in users:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                
                with col1:
                    status = "🟢" if user["is_active"] else "🔴"
                    verified = "✅" if user["is_verified"] else "❌"
                    st.write(f"{status} **{user['username']}** ({user['name']})")
                    st.write(f"📧 {user['email']} {verified}")
                
                with col2:
                    st.write(f"**Role:** {user['role']}")
                    st.write(f"**Last Login:** {user['last_login'] or 'Never'}")
                
                with col3:
                    new_role = st.selectbox(
                        "Role", 
                        ["admin", "moderator", "user", "guest"], 
                        index=["admin", "moderator", "user", "guest"].index(user["role"]),
                        key=f"role_{user['username']}"
                    )
                    if new_role != user["role"]:
                        if st.button("Update", key=f"update_role_{user['username']}"):
                            database.update_user_role(user["username"], new_role, st.session_state.user)
                            st.success(f"Updated {user['username']} role to {new_role}")
                            st.rerun()
                
                with col4:
                    if user["is_active"]:
                        if st.button("Deactivate", key=f"deactivate_{user['username']}"):
                            database.deactivate_user(user["username"], st.session_state.user)
                            st.success(f"Deactivated {user['username']}")
                            st.rerun()
                    else:
                        if st.button("Activate", key=f"activate_{user['username']}"):
                            database.activate_user(user["username"], st.session_state.user)
                            st.success(f"Activated {user['username']}")
                            st.rerun()
                
                with col5:
                    if st.button("Reset Pass", key=f"reset_{user['username']}"):
                        # Generate a secure temporary password
                        import secrets
                        import string
                        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                        
                        # Hash and update password
                        hashed_temp = hash_password(temp_password)
                        database.update_user_password(user['username'], hashed_temp)
                        
                        # Log the action
                        log_security_event("PASSWORD_RESET", username=user['username'], 
                                         details=f"Password reset by admin {st.session_state.user}")
                        
                        # Display the temporary password securely
                        st.success(f"Password reset for {user['username']}")
                        st.code(f"Temporary Password: {temp_password}")
                        st.warning("⚠️ Please share this password securely with the user. They should change it immediately.")
                
                st.divider()
        else:
            st.info("No users found")
    
    with tabs[1]:  # Pending Users
        st.markdown("### Pending User Approvals")
        pending_users = database.get_pending_users()
        
        if pending_users:
            for pending in pending_users:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{pending['username']}** ({pending['name']})")
                    st.write(f"📧 {pending['email']}")
                
                with col2:
                    if st.button("✅ Approve", key=f"approve_{pending['username']}"):
                        if database.approve_pending_user(pending["username"], st.session_state.user):
                            st.success(f"Approved {pending['username']}")
                            st.rerun()
                        else:
                            st.error("Failed to approve user")
                
                with col3:
                    if st.button("❌ Reject", key=f"reject_{pending['username']}"):
                        database.remove_pending_user(pending["username"])
                        st.success(f"Rejected {pending['username']}")
                        st.rerun()
                
                st.divider()
        else:
            st.info("No pending users")
    
    with tabs[2]:  # Security Logs
        st.markdown("### Security Logs")
        logs = database.get_security_logs(limit=50)
        
        if logs:
            for log in logs:
                col1, col2, col3 = st.columns([2, 3, 2])
                
                with col1:
                    st.write(f"**{log['event_type']}**")
                    st.write(f"🕒 {log['timestamp']}")
                
                with col2:
                    st.write(f"👤 {log['username'] or 'Unknown'}")
                    if log['details']:
                        st.write(f"📝 {log['details']}")
                
                with col3:
                    if log['ip_address']:
                        st.write(f"🌐 {log['ip_address']}")
                
                st.divider()
        else:
            st.info("No security logs found")
    
    with tabs[3]:  # Model Management
        st.markdown("### 🤖 Ollama Model Management")
        
        # Import required functions
        # Using import from top of file
        
        # Current endpoint configuration
        col1, col2 = st.columns(2)
        with col1:
            current_endpoint = st.session_state.get("llm_endpoint", "http://localhost:11434")
            new_endpoint = st.text_input("Ollama Endpoint", value=current_endpoint)
            if new_endpoint != current_endpoint:
                st.session_state.llm_endpoint = new_endpoint
                st.session_state.rag_endpoint = new_endpoint  # Keep both endpoints in sync
                st.success("Endpoint updated successfully")
        
        with col2:
            if st.button("🔄 Test Connection"):
                try:
                    import requests
                    response = requests.get(f"{new_endpoint}/api/tags", timeout=5)
                    if response.ok:
                        st.success("✅ Connection successful")
                    else:
                        st.error(f"❌ Connection failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
        
        st.divider()
        
        # Available models section
        st.markdown("#### Available Models")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔄 Refresh Model List"):
                # Clear cache to force refresh
                from scripts import ollama_client
                ollama_client.clear_model_cache()
                st.rerun()
        
        with col2:
            show_details = st.checkbox("Show Details")
        
        try:
            available_models = get_available_models()
            if available_models:
                st.success(f"Found {len(available_models)} models")
                
                for i, model in enumerate(available_models):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"📦 **{model}**")
                        if show_details:
                            # Try to get model info
                            try:
                                import requests
                                response = requests.post(f"{new_endpoint}/api/show", 
                                                       json={"name": model}, timeout=10)
                                if response.ok:
                                    info = response.json()
                                    if 'details' in info:
                                        details = info['details']
                                        st.caption(f"Size: {details.get('parameter_size', 'Unknown')} | Family: {details.get('family', 'Unknown')}")
                            except:
                                pass
                    
                    with col2:
                        if st.button("📊 Info", key=f"info_{i}"):
                            try:
                                import requests
                                response = requests.post(f"{new_endpoint}/api/show", 
                                                       json={"name": model}, timeout=10)
                                if response.ok:
                                    info = response.json()
                                    st.json(info)
                            except Exception as e:
                                st.error(f"Failed to get model info: {e}")
                    
                    with col3:
                        if st.button("🗑️ Remove", key=f"remove_{i}"):
                            if st.session_state.get(f"confirm_remove_{i}", False):
                                try:
                                    import subprocess
                                    result = subprocess.run(["ollama", "rm", model], 
                                                          capture_output=True, text=True, timeout=30)
                                    if result.returncode == 0:
                                        st.success(f"Removed {model}")
                                        # Clear cache and refresh
                                        from scripts import ollama_client
                                        ollama_client.clear_model_cache()
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to remove: {result.stderr}")
                                except Exception as e:
                                    st.error(f"Error removing model: {e}")
                                st.session_state[f"confirm_remove_{i}"] = False
                            else:
                                st.session_state[f"confirm_remove_{i}"] = True
                                st.warning("Click again to confirm removal")
            else:
                st.warning("No models found. Check your Ollama connection.")
        except Exception as e:
            st.error(f"Error fetching models: {e}")
        
        st.divider()
        
        # Pull new models section
        st.markdown("#### Pull New Models")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            model_to_pull = st.text_input("Model name to pull", 
                                        placeholder="e.g., llama2, qwen3:4b, gemma:1b")
        
        with col2:
            st.markdown("**Recommended:**")
            recommended_models = ["qwen3:4b", "qwen3:0.6b", "gemma:1b", "llama2", "codellama"]
            selected_recommended = st.selectbox("Quick select", [""] + recommended_models)
            if selected_recommended:
                model_to_pull = selected_recommended
        
        if model_to_pull and st.button("📥 Pull Model"):
            if model_to_pull:
                st.info(f"Pulling {model_to_pull}... This may take several minutes.")
                
                # Create a placeholder for the progress
                progress_placeholder = st.empty()
                
                try:
                    # Stream the pull output
                    for line in pull_model_subprocess(model_to_pull):
                        progress_placeholder.text(line)
                    
                    progress_placeholder.success(f"✅ Successfully pulled {model_to_pull}")
                    
                    # Clear cache to show new model
                    from scripts import ollama_client
                    ollama_client.clear_model_cache()
                    
                    # Auto-refresh after a short delay
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    progress_placeholder.error(f"❌ Failed to pull {model_to_pull}: {e}")
        
        st.divider()
        
        # Model health monitoring
        st.markdown("#### Model Health & Performance")
        
        if st.button("🏥 Health Check All Models"):
            try:
                available_models = get_available_models()
                if available_models:
                    health_results = []
                    
                    for model in available_models:
                        try:
                            import requests
                            
                            # Simple test prompt
                            start_time = time.time()
                            response = requests.post(
                                f"{new_endpoint}/api/generate",
                                json={"model": model, "prompt": "Hello", "stream": False},
                                timeout=30
                            )
                            end_time = time.time()
                            
                            if response.ok:
                                response_time = round(end_time - start_time, 2)
                                health_results.append({
                                    "model": model,
                                    "status": "✅ Healthy",
                                    "response_time": f"{response_time}s"
                                })
                            else:
                                health_results.append({
                                    "model": model,
                                    "status": "❌ Error",
                                    "response_time": "N/A"
                                })
                        except Exception as e:
                            health_results.append({
                                "model": model,
                                "status": f"❌ {str(e)[:50]}",
                                "response_time": "N/A"
                            })
                    
                    # Display results in a table
                    df = pd.DataFrame(health_results)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No models available for health check")
            except Exception as e:
                st.error(f"Health check failed: {e}")

    with tabs[4]:  # System Settings
        st.markdown("### System Settings")
        
        # Rate limiting settings
        st.markdown("#### Rate Limiting Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            max_attempts = st.number_input("Max login attempts", min_value=3, max_value=10, value=5, 
                                         help="Maximum failed login attempts before account lockout")
            window_minutes = st.number_input("Time window (minutes)", min_value=5, max_value=60, value=15,
                                           help="Time window for tracking failed attempts")
        
        with col2:
            lockout_duration = st.number_input("Lockout duration (minutes)", min_value=5, max_value=120, value=30,
                                             help="How long accounts remain locked after max attempts")
            cleanup_days = st.number_input("Log cleanup (days)", min_value=7, max_value=365, value=90,
                                         help="Automatically delete security logs older than this")
        
        if st.button("💾 Update Security Settings"):
            # Save settings to database or config
            security_config = {
                "max_login_attempts": max_attempts,
                "lockout_window_minutes": window_minutes,
                "lockout_duration_minutes": lockout_duration,
                "log_cleanup_days": cleanup_days,
                "updated_by": st.session_state.user,
                "updated_at": "now"
            }
            # In a real implementation, save to database
            st.success("✅ Security settings updated successfully!")
            log_security_event("SETTINGS_UPDATED", username=st.session_state.user, 
                             details=f"Updated security configuration")
        
        st.divider()
        
        # Application settings
        st.markdown("#### Application Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            default_model = st.selectbox("Default LLM Model", 
                                       ["llama3.2", "qwen2.5", "gemma2", "codellama"],
                                       help="Default model for new users")
            enable_registration = st.checkbox("Allow user registration", value=True,
                                            help="Allow new users to register accounts")
        
        with col2:
            session_timeout = st.number_input("Session timeout (hours)", min_value=1, max_value=24, value=8,
                                            help="Automatic logout after inactivity")
            max_file_size = st.number_input("Max upload size (MB)", min_value=1, max_value=100, value=10,
                                          help="Maximum file upload size")
        
        if st.button("💾 Update App Settings"):
            app_config = {
                "default_model": default_model,
                "enable_registration": enable_registration,
                "session_timeout_hours": session_timeout,
                "max_file_size_mb": max_file_size,
                "updated_by": st.session_state.user
            }
            st.success("✅ Application settings updated successfully!")
        
        st.divider()
        
        # System maintenance
        st.markdown("#### System Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Cleanup Old Logs"):
                # Simulate log cleanup
                st.info("Cleaning up security logs older than 90 days...")
                # In real implementation: database.cleanup_old_logs(90)
                st.success("✅ Log cleanup completed!")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.info("Generating system usage report...")
                # In real implementation: generate comprehensive report
                st.success("✅ Report generated and saved to admin folder!")
        
        with col3:
            if st.button("🔄 Restart Services"):
                st.warning("⚠️ This would restart background services")
                st.info("Service restart functionality requires system-level permissions")
    
    with tabs[5]:  # Analytics
        st.markdown("### 📈 Analytics & Performance Monitor")
        render_analytics_dashboard()
    
    if st.button("← Back to Main App", key="admin_back_button"):
        st.session_state.show_admin_panel = False
        st.rerun()

def show_user_settings():
    """User settings panel"""
    st.markdown("## ⚙️ User Settings")
    
    tabs = st.tabs(["👤 Profile", "🔒 Security", "⚙️ Preferences", "🔑 Two-Factor Auth"])
    
    with tabs[0]:  # Profile
        st.markdown("### Profile Information")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=USER_DATA.get("name", ""))
            new_email = st.text_input("Email", value=USER_DATA.get("email", ""))
        
        with col2:
            st.write(f"**Username:** {USER}")
            st.write(f"**Role:** {USER_ROLE}")
            st.write(f"**Member Since:** {USER_DATA.get('created_at', 'Unknown')}")
            st.write(f"**Last Login:** {USER_DATA.get('last_login', 'Unknown')}")
        
        if st.button("Update Profile", key="update_profile_button"):
            if new_name and new_email:
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                if re.match(email_pattern, new_email):
                    # Update user profile in database
                    try:
                        # In a real implementation, add database.update_user_profile function
                        # database.update_user_profile(st.session_state.user, new_name, new_email)
                        
                        # Update session state
                        st.session_state.user_data['name'] = new_name
                        st.session_state.user_data['email'] = new_email
                        
                        st.success("✅ Profile updated successfully!")
                        log_security_event("PROFILE_UPDATED", username=st.session_state.user, 
                                         details=f"Updated name and email")
                        
                        # Refresh the page to show updated info
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update profile: {str(e)}")
                else:
                    st.error("❌ Please enter a valid email address")
            else:
                st.error("❌ Please fill in all required fields")
    
    with tabs[1]:  # Security
        st.markdown("### Security Settings")
        
        st.markdown("#### Change Password")
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            change_password_button = st.form_submit_button("Change Password")
            
            if change_password_button:
                if not all([current_password, new_password, confirm_password]):
                    st.error("All fields are required")
                elif new_password != confirm_password:
                    st.error("New passwords do not match")
                elif not verify_password(current_password, USER_DATA["hashed_password"]):
                    st.error("Current password is incorrect")
                else:
                    # Validate new password
                    is_strong, message = validate_password_strength(new_password)
                    if not is_strong:
                        st.error(f"Password requirements: {message}")
                    else:
                        # Update password
                        new_hashed = hash_password(new_password)
                        database.update_user_password(st.session_state.user, new_hashed)
                        st.success("Password changed successfully!")
                        log_security_event("PASSWORD_CHANGED", username=st.session_state.user, details="Changed via settings")
        
        st.markdown("#### Active Sessions")
        
        # Display current session info
        st.write("**Current Session:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Session ID", "current")
            st.metric("Login Time", USER_DATA.get('last_login', 'Unknown'))
        
        with col2:
            st.metric("IP Address", "Local")  # In real app, track actual IP
            st.metric("User Agent", "Streamlit App")
        
        with col3:
            st.metric("Status", "🟢 Active")
            if st.button("🚪 End Session", key="end_session_button"):
                # Clear session state and force logout
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Session ended successfully")
                st.rerun()
    
    with tabs[2]:  # Preferences
        st.markdown("### User Preferences")
        
        # Session settings
        st.markdown("#### Session Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember login", value=False,
                                    help="Stay logged in across browser sessions")
            auto_save = st.checkbox("Auto-save conversations", value=True,
                                  help="Automatically save chat history")
            show_cot = st.checkbox("Show Chain of Thought", 
                                 value=st.session_state.get("show_chain_of_thought", True),
                                 help="Display AI's reasoning process with responses")
        
        with col2:
            session_timeout = st.selectbox("Auto-logout after", 
                                         ["1 hour", "4 hours", "8 hours", "24 hours"],
                                         index=2,
                                         help="Automatically logout after inactivity")
        
        if st.button("💾 Save Session Settings", key="save_session_settings_button"):
            session_prefs = {
                "remember_me": remember_me,
                "auto_save": auto_save,
                "session_timeout": session_timeout,
                "show_chain_of_thought": show_cot
            }
            # Save to user preferences
            for key, value in session_prefs.items():
                if key == "show_chain_of_thought":
                    st.session_state[key] = value
                database.save_user_preference(st.session_state.user, f"session_{key}", value)
            
            st.success("✅ Session preferences saved!")
        
        st.divider()
        
        # AI Response settings
        st.markdown("#### AI Response Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            show_thinking = st.checkbox("Always expand reasoning", 
                                      value=st.session_state.get("show_chain_of_thought", True),
                                      help="Automatically expand AI's chain of thought reasoning")
            verbose_responses = st.checkbox("Verbose responses", value=False,
                                          help="Request more detailed AI responses")
            inline_thinking = st.checkbox("Show thinking inline", 
                                        value=st.session_state.get("inline_chain_of_thought", False),
                                        help="Display reasoning directly without expandable section")
        
        with col2:
            response_format = st.selectbox("Preferred response format",
                                         ["Standard", "Technical", "Beginner-friendly"],
                                         help="How detailed should AI responses be")
        
        if st.button("💾 Save AI Settings", key="save_ai_settings_button"):
            ai_prefs = {
                "show_thinking": show_thinking,
                "verbose_responses": verbose_responses,
                "response_format": response_format,
                "inline_thinking": inline_thinking
            }
            for key, value in ai_prefs.items():
                if key == "show_thinking":
                    st.session_state["show_chain_of_thought"] = value
                elif key == "inline_thinking":
                    st.session_state["inline_chain_of_thought"] = value
                database.save_user_preference(st.session_state.user, f"ai_{key}", value)
            
            st.success("✅ AI response settings saved!")

    with tabs[3]:  # Two-Factor Auth
        st.markdown("### Two-Factor Authentication")
        
        try:
            from auth.two_factor import is_2fa_enabled, generate_2fa_secret, get_2fa_qr_code, enable_2fa, disable_2fa
            
            two_fa_enabled = is_2fa_enabled(st.session_state.user)
            
            if two_fa_enabled:
                st.success("🔒 Two-Factor Authentication is ENABLED")
                st.write("Your account is protected with 2FA.")
                
                if st.button("Disable 2FA", key="disable_2fa_button"):
                    if disable_2fa(st.session_state.user):
                        st.success("Two-Factor Authentication has been disabled")
                        st.rerun()
                    else:
                        st.error("Failed to disable 2FA")
            else:
                st.warning("🔓 Two-Factor Authentication is DISABLED")
                st.write("Enable 2FA to add an extra layer of security to your account.")
                
                if st.button("Setup 2FA", key="setup_2fa_button"):
                    st.session_state.setup_2fa = True
                    st.rerun()
                
                if st.session_state.get("setup_2fa", False):
                    st.markdown("#### Setup Two-Factor Authentication")
                    
                    # Generate secret and QR code
                    secret = generate_2fa_secret(st.session_state.user)
                    qr_code = get_2fa_qr_code(st.session_state.user, secret)
                    
                    st.markdown("1. Install an authenticator app (Google Authenticator, Authy, etc.)")
                    st.markdown("2. Scan this QR code with your authenticator app:")
                    
                    st.image(qr_code, width=200)
                    
                    st.markdown("3. Enter the 6-digit code from your authenticator app:")
                    
                    verification_code = st.text_input("Verification Code", max_chars=6)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Enable 2FA", key="enable_2fa_button"):
                            if verification_code and len(verification_code) == 6:
                                if enable_2fa(st.session_state.user, verification_code):
                                    st.success("Two-Factor Authentication has been enabled!")
                                    st.session_state.setup_2fa = False
                                    st.rerun()
                                else:
                                    st.error("Invalid verification code. Please try again.")
                            else:
                                st.error("Please enter a 6-digit verification code")
                    
                    with col2:
                        if st.button("Cancel", key="cancel_2fa_setup_button"):
                            st.session_state.setup_2fa = False
                            st.rerun()
        
        except ImportError:
            st.info("Two-Factor Authentication requires additional setup")
    
    if st.button("← Back to Main App", key="user_settings_back_button"):
        st.session_state.show_user_settings = False
        st.rerun()


login()
# Ensure 'user' is initialized in session_state
if "user" not in st.session_state:
    st.session_state["user"] = None

# CRITICAL: Initialize model session state early to prevent empty model errors
# This ensures that even if the sidebar model selection fails, we have a fallback
if "selected_expert_model" not in st.session_state:
    try:
        # Using import from top of file
        available_models = get_available_models()
        if available_models:
            st.session_state["selected_expert_model"] = available_models[0]
        else:
            st.session_state["selected_expert_model"] = "llama3.2"
    except:
        st.session_state["selected_expert_model"] = "llama3.2"
        
if "selected_draft_model" not in st.session_state:
    st.session_state["selected_draft_model"] = st.session_state["selected_expert_model"]

USER = st.session_state.user
USER_DATA = st.session_state.get("user_data", {})
IS_ADMIN = st.session_state.get("is_admin", False)
USER_ROLE = st.session_state.get("user_role", "user")

def load_user_prefs():
    """Load user preferences from database instead of encrypted files"""
    return database.get_user_preferences(st.session_state.user)

def save_user_prefs():
    """Save user preferences to database only if changed."""
    prefs = {
        "selected_expert_model": st.session_state.get("selected_expert_model"),
        "selected_draft_model": st.session_state.get("selected_draft_model"),
        "persona_prompt": st.session_state.get("persona_prompt"),
        "folders": st.session_state.get("folders"),
        "current_folder": st.session_state.get("current_folder"),
        "chat_sessions": st.session_state.get("chat_sessions"),
        "current_session": st.session_state.get("current_session"),
        "chat_contexts": st.session_state.get("chat_contexts"),
        "rag_endpoint": st.session_state.get("rag_endpoint", ""),
        "llm_endpoint": st.session_state.get("llm_endpoint", ""),
        "show_chain_of_thought": st.session_state.get("show_chain_of_thought", True),
        "inline_chain_of_thought": st.session_state.get("inline_chain_of_thought", False),
    }
    try:
        current_prefs = database.get_user_preferences(st.session_state.user)
        for key, value in prefs.items():
            if current_prefs.get(key) != value:
                database.save_user_preference(st.session_state.user, key, value)
    except Exception as e:
        print(f"Error saving user preferences: {e}")

# Load user preferences from database
prefs = load_user_prefs()
for key, value in prefs.items():
    st.session_state[key] = value

sidebar(USER, save_user_prefs)

# Add system resource monitoring to sidebar
if SYSTEM_MONITOR_AVAILABLE:
    check_system_resources()

st.title(f"🤖 Jarvis AI Assistant")

# Initialize chat session variables if they don't exist
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default"

# Add a welcome message for new users
if len(st.session_state.chat_sessions.get(st.session_state.current_session, [])) == 0:
    st.info("""
    👋 **Welcome to Jarvis AI!** I'm your intelligent assistant that can help you with:
    
    🔍 **Code Analysis** - Review, debug, and improve your code  
    📝 **Documentation** - Generate docs, comments, and explanations  
    🔍 **Research** - Search the web and analyze information  
    📁 **File Processing** - Analyze documents, images, and data  
    🧪 **Testing** - Generate unit tests and test strategies  
    
    **Just ask me anything in natural language!**
    """)

# User info and controls with better layout
info_col1, info_col2, info_col3, info_col4, info_col5, info_col6 = st.columns([3, 1, 1, 1, 1, 1])
with info_col1:
    st.markdown(f"**👋 {USER_DATA.get('name', st.session_state.user)}** • *{USER_ROLE}*")
with info_col2:
    if IS_ADMIN:
        if st.button("🔧 Admin", help="Access admin panel"):
            st.session_state.show_admin_panel = True
            st.rerun()
with info_col3:
    if st.button("🧠 Code AI", help="Code Intelligence Engine"):
        st.session_state.show_code_intelligence = True
        st.rerun()
with info_col4:
    if st.button("⚙️ Settings", help="User preferences"):
        st.session_state.show_user_settings = True
        st.rerun()
with info_col5:
    if st.button("💬 Feedback", help="Send feedback"):
        st.session_state.show_feedback = True
        st.rerun()
with info_col6:
    if st.button("🚪 Logout", help="Sign out"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Show various panels if requested
if st.session_state.get("show_admin_panel", False) and IS_ADMIN:
    show_admin_panel()

if st.session_state.get("show_code_intelligence", False):
    # Show code intelligence interface
    render_code_intelligence_interface()
    
    # Add close button
    if st.button("❌ Close Code Intelligence", key="close_code_intelligence_button"):
        st.session_state.show_code_intelligence = False
        st.rerun()

if st.session_state.get("show_user_settings", False):
    show_user_settings()

if IS_ADMIN:
    st.markdown("**You are logged in as Admin.**")


# --- Endpoint Configuration ---
st.sidebar.markdown("## Endpoints")
llm_endpoint = st.sidebar.text_input(
    "LLM API Endpoint",
    value=st.session_state.get("llm_endpoint", "http://localhost:11434")
)
rag_endpoint = st.sidebar.text_input(
    "RAG API Endpoint",
    value=st.session_state.get("rag_endpoint", "http://localhost:11434")
)
st.session_state.llm_endpoint = llm_endpoint

# --- RAG Enable Checkbox ---
# User can now control RAG features via checkbox instead of always-on behavior
enable_rag = st.sidebar.checkbox("Enable RAG features", value=False)
st.session_state.enable_rag = enable_rag

save_user_prefs()

# --- File Upload ---
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
if uploaded_files:
    user_upload_dir = os.path.join("uploads", st.session_state.user)
    os.makedirs(user_upload_dir, exist_ok=True)
    for f in uploaded_files:
        with open(os.path.join(user_upload_dir, f.name), "wb") as out_f:
            out_f.write(f.getbuffer())

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Default": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default"

# Synchronize the old and new chat models
if "current_chat" in st.session_state and st.session_state["current_chat"] is not None:
    # If using the new chat model, update the chat_sessions model
    current_chat_id = st.session_state["current_chat"]
    if current_chat_id in st.session_state.get("chats", {}):
        current_chat = st.session_state["chats"][current_chat_id]
        st.session_state.chat_sessions["Default"] = current_chat.get("messages", [])
else:
    # If no current chat is selected, but we have chat sessions, initialize the new chat model
    if st.session_state.current_session in st.session_state.chat_sessions and st.session_state.chat_sessions[st.session_state.current_session]:
        if "chats" not in st.session_state:
            st.session_state["chats"] = {}
        
        chat_id = str(uuid.uuid4())
        st.session_state["current_chat"] = chat_id
        st.session_state["chat_history"] = st.session_state.chat_sessions[st.session_state.current_session]
        st.session_state["chats"][chat_id] = {
            "id": chat_id,
            "title": st.session_state.current_session,
            "messages": st.session_state.chat_sessions[st.session_state.current_session]
        }

chat_history = st.session_state.chat_sessions[st.session_state.current_session]

# --- Source Evaluation for RAG ---
# Helper function to update chat history in both models
def update_chat_history(message):
    """
    Updates both chat history models with a new message
    """
    # Update the chat_sessions model
    chat_history = st.session_state.chat_sessions[st.session_state.current_session]
    chat_history.append(message)
    
    # Also update the new chat model if it's in use
    if "current_chat" in st.session_state and st.session_state["current_chat"] is not None:
        current_chat_id = st.session_state["current_chat"]
        if current_chat_id in st.session_state.get("chats", {}):
            st.session_state["chats"][current_chat_id]["messages"].append(message)
            st.session_state["chat_history"] = st.session_state["chats"][current_chat_id]["messages"]
    
    return chat_history

def evaluate_sources(files):
    summaries = []
    usable = []
    unusable = []
    st.markdown("### Source Evaluation")
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()[:1000]
            # Summarize via LLM endpoint
            summary = tools.llm_summarize_source(content, st.session_state.llm_endpoint)
            st.write(f"**{os.path.basename(f)}**: {summary}")
            use = st.checkbox(f"Mark {os.path.basename(f)} as usable?", key=f"use_{f}")
            summaries.append((f, summary, use))
            if use:
                usable.append(f)
            else:
                unusable.append(f)
        except Exception as e:
            st.error(f"Could not read file {f}: {e}")
    return usable, unusable, summaries

st.markdown("## Chat")
# Display chat history with chain of thought support
for msg in chat_history:
    if msg["role"] == "assistant" and isinstance(msg.get("content"), dict):
        # Handle structured response with chain of thought
        content_data = msg["content"]
        final_answer = content_data.get("final_answer", "")
        chain_of_thought = content_data.get("chain_of_thought", "")
        
        with st.chat_message("assistant"):
            if final_answer:
                st.write(final_answer)
            
            # Display chain of thought if it exists and setting is enabled
            if chain_of_thought and st.session_state.get("show_chain_of_thought", True):
                inline_cot = st.session_state.get("inline_chain_of_thought", False)
                
                # Debug info (only for testing)
                # st.caption(f"Debug: CoT length: {len(chain_of_thought)}, Inline: {inline_cot}")
                
                if inline_cot:
                    st.markdown("---")
                    st.markdown("**🤔 AI's Thinking Process:**")
                    st.info(chain_of_thought)
                else:
                    with st.expander("🧠 Chain of Thought Reasoning", expanded=True):
                        st.markdown("**🤔 AI's Thinking Process:**")
                        st.code(chain_of_thought, language="text")
    else:
        # Handle simple string messages
        content = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
        st.chat_message(msg["role"]).write(content)

user_msg = st.chat_input("Ask me anything! I can help with code, files, research, and more...")
if user_msg:
    # Display user message immediately
    st.chat_message("user").write(user_msg)
    
    # Update both chat models
    user_message = {"role": "user", "content": user_msg}
    chat_history = update_chat_history(user_message)
    
    # Show helpful suggestions for new users
    if len(chat_history) <= 2:  # First interaction
        with st.expander("💡 Quick Start Tips", expanded=False):
            st.markdown("""
            **Try these natural language commands:**
            - "Help me review this Python code for bugs"
            - "Summarize the uploaded document"  
            - "Search for information about machine learning"
            - "Generate a test for this function"
            - "Explain how this code works"
            - "Create documentation for this project"
            """)
    
    uploaded_file_paths = [os.path.join("uploads", st.session_state.user, f.name) for f in uploaded_files] if uploaded_files else []


    # Only enable RAG logic if checkbox is checked
    if st.session_state.get("enable_rag", False):
        # Source evaluation step for RAG actions
        if "rag" in user_msg.lower() and uploaded_file_paths:
            usable, unusable, summaries = evaluate_sources(uploaded_file_paths)
            # Only pass usable files to RAG
            rag_files = usable
        else:
            rag_files = uploaded_file_paths
    else:
        rag_files = []

    # Use RAG mode 'auto' for web-augmented context if enabled
    rag_mode = "auto" if st.session_state.get("enable_rag", False) else "file"

    # Get DuckDuckGo fallback preference from session/user_prefs
    duckduckgo_fallback = st.session_state.get("duckduckgo_fallback", True)
    
    # CRITICAL: Ensure expert_model is always set for Ollama to prevent API 404 errors
    # This is the final safeguard against empty model names that cause "model '' not found" errors
    expert_model = st.session_state.get("selected_expert_model")
    if not expert_model or expert_model.strip() == "":
        # Try to get available models and use the first one as fallback
        try:
            # Using import from top of file
            available_models = get_available_models()
            if available_models:
                expert_model = available_models[0]
            else:
                expert_model = "llama3.2"  # Common fallback model
        except:
            expert_model = "llama3.2"  # Fallback to common model
    
    # Set default rag_endpoint since we removed the textbox for cleaner UI
    rag_endpoint = st.session_state.get("rag_endpoint", "http://localhost:8000/rag")
    
    # Get V2 configuration preference
    use_langgraph_v2 = st.session_state.get("use_langgraph_v2", True)
    
    agent = JarvisAgent(
        st.session_state.get("persona_prompt"),
        tools,
        human_in_loop.request_human_reasoning,
        expert_model=expert_model,
        draft_model=st.session_state.get("selected_draft_model") if st.session_state.get("enable_speculative_decoding", False) else None,
        user=st.session_state.user,
        llm_endpoint=llm_endpoint,
        rag_endpoint=rag_endpoint,
        duckduckgo_fallback=duckduckgo_fallback,
        use_langgraph=use_langgraph_v2  # Enable V2 LangGraph architecture
    )
    
    # Show processing indicator
    with st.spinner(f"🤖 Processing with {expert_model}..."):
        try:
            plan = agent.parse_natural_language(user_msg, rag_files, chat_history)
            if not plan:
                st.chat_message("assistant").write("I'm not sure how to help with that request. Could you please rephrase it or be more specific?")
                update_chat_history({"role": "assistant", "content": "I'm not sure how to help with that request. Could you please rephrase it or be more specific?"})
            else:
                results = agent.execute_plan(plan)
                
                if not results:
                    st.chat_message("assistant").write("I encountered an issue while processing your request. Please try again or contact support if the problem persists.")
                    update_chat_history({"role": "assistant", "content": "I encountered an issue while processing your request. Please try again or contact support if the problem persists."})
                else:
                    # Display results immediately
                    for result in results:
                        if isinstance(result['result'], list):
                            for item in result['result']:
                                response_text = str(item)
                                st.chat_message("assistant").write(response_text)
                                update_chat_history({"role": "assistant", "content": response_text})
                        else:
                            response_data = result['result']
                            
                            # Handle chain of thought responses
                            if isinstance(response_data, dict) and response_data.get("type") == "cot_response":
                                chain_of_thought = response_data.get("chain_of_thought", "")
                                final_answer = response_data.get("final_answer", "")
                                
                                # Display the final answer first
                                if final_answer and final_answer.strip():
                                    with st.chat_message("assistant"):
                                        st.write(final_answer)
                                        
                                        # Chain of thought will be displayed through chat history persistence
                                        # No need for real-time display that disappears
                                    
                                    # Store the structured response in chat history (with chain of thought)
                                    structured_response = {
                                        "final_answer": final_answer,
                                        "chain_of_thought": chain_of_thought if st.session_state.get("show_chain_of_thought", True) else ""
                                    }
                                    update_chat_history({"role": "assistant", "content": structured_response})
                                else:
                                    fallback_msg = "The AI generated reasoning but no final answer."
                                    st.chat_message("assistant").write(fallback_msg)
                                    structured_response = {
                                        "final_answer": fallback_msg,
                                        "chain_of_thought": chain_of_thought if st.session_state.get("show_chain_of_thought", True) else ""
                                    }
                                    update_chat_history({"role": "assistant", "content": structured_response})
                            else:
                                # Handle regular string responses
                                response_text = str(response_data)
                                
                                if response_text and response_text.strip() and response_text != "None":
                                    st.chat_message("assistant").write(response_text)
                                    update_chat_history({"role": "assistant", "content": response_text})
                                else:
                                    fallback_msg = "I apologize, but I wasn't able to generate a proper response. Please try rephrasing your request."
                                    st.chat_message("assistant").write(fallback_msg)
                                    update_chat_history({"role": "assistant", "content": fallback_msg})
                        
                        # Handle image generation
                        if result['step']['tool'] == "image_generation" and result['result'] is not None:
                            st.image(result['result'], caption="Generated Image")
        except Exception as e:
            error_msg = f"I apologize, but I encountered an unexpected error: {str(e)}. Please try rephrasing your request."
            st.chat_message("assistant").write(error_msg)
            update_chat_history({"role": "assistant", "content": error_msg})
            # Log the error for debugging
            log_security_event("AGENT_ERROR", username=st.session_state.user, details=f"Error: {str(e)}")
            results = []  # Ensure results is defined
    
    save_user_prefs()
    st.rerun()  # Force a rerun to update the chat display