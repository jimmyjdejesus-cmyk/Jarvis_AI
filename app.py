import streamlit as st
import os
import json
from agent.security import load_user_key, encrypt_json, decrypt_json, hash_password, verify_password, is_rate_limited, log_security_event, validate_password_strength
from agent.core import JarvisAgent
from ui.sidebar import sidebar
import agent.tools as tools
import agent.human_in_loop as human_in_loop
import database

# Initialize database
database.init_db()

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
    
    tabs = st.tabs(["👥 User Management", "⏳ Pending Users", "📊 Security Logs", "⚙️ System Settings"])
    
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
                            database.update_user_role(user["username"], new_role, USER)
                            st.success(f"Updated {user['username']} role to {new_role}")
                            st.rerun()
                
                with col4:
                    if user["is_active"]:
                        if st.button("Deactivate", key=f"deactivate_{user['username']}"):
                            database.deactivate_user(user["username"], USER)
                            st.success(f"Deactivated {user['username']}")
                            st.rerun()
                    else:
                        if st.button("Activate", key=f"activate_{user['username']}"):
                            database.activate_user(user["username"], USER)
                            st.success(f"Activated {user['username']}")
                            st.rerun()
                
                with col5:
                    if st.button("Reset Pass", key=f"reset_{user['username']}"):
                        st.info(f"Password reset for {user['username']} would be implemented here")
                
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
                        if database.approve_pending_user(pending["username"], USER):
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
    
    with tabs[3]:  # System Settings
        st.markdown("### System Settings")
        st.info("System configuration options would be implemented here")
        
        # Rate limiting settings
        st.markdown("#### Rate Limiting")
        max_attempts = st.number_input("Max login attempts", min_value=3, max_value=10, value=5)
        window_minutes = st.number_input("Time window (minutes)", min_value=5, max_value=60, value=15)
        
        if st.button("Update Rate Limiting"):
            st.success("Rate limiting settings updated")
    
    if st.button("← Back to Main App"):
        st.session_state.show_admin_panel = False
        st.rerun()

def show_user_settings():
    """User settings panel"""
    st.markdown("## ⚙️ User Settings")
    
    tabs = st.tabs(["👤 Profile", "🔒 Security", "🔑 Two-Factor Auth"])
    
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
        
        if st.button("Update Profile"):
            # In a full implementation, you'd add database update functions
            st.success("Profile update functionality would be implemented here")
    
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
                        database.update_user_password(USER, new_hashed)
                        st.success("Password changed successfully!")
                        log_security_event("PASSWORD_CHANGED", username=USER, details="Changed via settings")
        
        st.markdown("#### Active Sessions")
        st.info("Session management would be implemented here")
    
    with tabs[2]:  # Two-Factor Auth
        st.markdown("### Two-Factor Authentication")
        
        try:
            from auth.two_factor import is_2fa_enabled, generate_2fa_secret, get_2fa_qr_code, enable_2fa, disable_2fa
            
            two_fa_enabled = is_2fa_enabled(USER)
            
            if two_fa_enabled:
                st.success("🔒 Two-Factor Authentication is ENABLED")
                st.write("Your account is protected with 2FA.")
                
                if st.button("Disable 2FA"):
                    if disable_2fa(USER):
                        st.success("Two-Factor Authentication has been disabled")
                        st.rerun()
                    else:
                        st.error("Failed to disable 2FA")
            else:
                st.warning("🔓 Two-Factor Authentication is DISABLED")
                st.write("Enable 2FA to add an extra layer of security to your account.")
                
                if st.button("Setup 2FA"):
                    st.session_state.setup_2fa = True
                    st.rerun()
                
                if st.session_state.get("setup_2fa", False):
                    st.markdown("#### Setup Two-Factor Authentication")
                    
                    # Generate secret and QR code
                    secret = generate_2fa_secret(USER)
                    qr_code = get_2fa_qr_code(USER, secret)
                    
                    st.markdown("1. Install an authenticator app (Google Authenticator, Authy, etc.)")
                    st.markdown("2. Scan this QR code with your authenticator app:")
                    
                    st.image(qr_code, width=200)
                    
                    st.markdown("3. Enter the 6-digit code from your authenticator app:")
                    
                    verification_code = st.text_input("Verification Code", max_chars=6)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Enable 2FA"):
                            if verification_code and len(verification_code) == 6:
                                if enable_2fa(USER, verification_code):
                                    st.success("Two-Factor Authentication has been enabled!")
                                    st.session_state.setup_2fa = False
                                    st.rerun()
                                else:
                                    st.error("Invalid verification code. Please try again.")
                            else:
                                st.error("Please enter a 6-digit verification code")
                    
                    with col2:
                        if st.button("Cancel"):
                            st.session_state.setup_2fa = False
                            st.rerun()
        
        except ImportError:
            st.info("Two-Factor Authentication requires additional setup")
    
    if st.button("← Back to Main App"):
        st.session_state.show_user_settings = False
        st.rerun()

login()
USER = st.session_state.user
USER_DATA = st.session_state.get("user_data", {})
IS_ADMIN = st.session_state.get("is_admin", False)
USER_ROLE = st.session_state.get("user_role", "user")

def load_user_prefs():
    """Load user preferences from database instead of encrypted files"""
    return database.get_user_preferences(USER)

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
    }
    try:
        current_prefs = database.get_user_preferences(USER)
        for key, value in prefs.items():
            if current_prefs.get(key) != value:
                database.save_user_preference(USER, key, value)
    except Exception as e:
        print(f"Error saving user preferences: {e}")

# Load user preferences from database
prefs = load_user_prefs()
for key, value in prefs.items():
    st.session_state[key] = value

sidebar(USER, save_user_prefs)

st.title(f"Jarvis Modular Agentic AI")

# User info and controls
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.markdown(f"**Welcome, {USER_DATA.get('name', USER)}** ({USER_ROLE})")
with col2:
    if IS_ADMIN:
        if st.button("🔧 Admin Panel"):
            st.session_state.show_admin_panel = True
            st.rerun()
with col3:
    if st.button("⚙️ Settings"):
        st.session_state.show_user_settings = True
        st.rerun()
with col4:
    if st.button("🚪 Logout"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Show various panels if requested
if st.session_state.get("show_admin_panel", False) and IS_ADMIN:
    show_admin_panel()

if st.session_state.get("show_user_settings", False):
    show_user_settings()

if IS_ADMIN:
    st.markdown("**You are logged in as Admin.**")

# --- Endpoint Configuration ---
st.sidebar.markdown("## Endpoints")
llm_endpoint = st.sidebar.text_input("LLM API Endpoint", value=st.session_state.get("llm_endpoint", "http://localhost:8000/llm"))
rag_endpoint = st.sidebar.text_input("RAG API Endpoint", value=st.session_state.get("rag_endpoint", "http://localhost:8000/rag"))
st.session_state.llm_endpoint = llm_endpoint
st.session_state.rag_endpoint = rag_endpoint
save_user_prefs()

# --- File Upload ---
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
if uploaded_files:
    user_upload_dir = os.path.join("uploads", USER)
    os.makedirs(user_upload_dir, exist_ok=True)
    for f in uploaded_files:
        with open(os.path.join(user_upload_dir, f.name), "wb") as out_f:
            out_f.write(f.getbuffer())

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Default": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default"

chat_history = st.session_state.chat_sessions[st.session_state.current_session]

# --- Source Evaluation for RAG ---
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
for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

user_msg = st.chat_input("Type your request.")
if user_msg:
    chat_history.append({"role": "user", "content": user_msg})
    uploaded_file_paths = [os.path.join("uploads", USER, f.name) for f in uploaded_files] if uploaded_files else []

    # Source evaluation step for RAG actions
    if "rag" in user_msg.lower() and uploaded_file_paths:
        usable, unusable, summaries = evaluate_sources(uploaded_file_paths)
        # Only pass usable files to RAG
        rag_files = usable
    else:
        rag_files = uploaded_file_paths

    agent = JarvisAgent(
        st.session_state.get("persona_prompt"),
        tools,
        human_in_loop.approval_callback,
        expert_model=st.session_state.get("selected_expert_model"),
        draft_model=st.session_state.get("selected_draft_model"),
        user=USER,
        llm_endpoint=llm_endpoint,
        rag_endpoint=rag_endpoint
    )
    plan = agent.parse_natural_language(user_msg, rag_files, chat_history)
    results = agent.execute_plan(plan)
    for result in results:
        if isinstance(result['result'], list):
            for item in result['result']:
                chat_history.append({"role": "assistant", "content": str(item)})
        else:
            chat_history.append({"role": "assistant", "content": str(result['result'])})
        if result['step']['tool'] == "image_generation" and result['result'] is not None:
            st.image(result['result'], caption="Generated Image")
    save_user_prefs()