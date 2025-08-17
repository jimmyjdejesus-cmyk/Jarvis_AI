import streamlit as st
import os
import json
from agent.security import load_user_key, encrypt_json, decrypt_json, hash_password, verify_password
from agent.core import JarvisAgent
from ui.sidebar import sidebar
import agent.tools as tools
import agent.human_in_loop as human_in_loop

# --- Simple User Database (for demo; replace with DB for production) ---
USER_DB = {
    "Moodeux": hash_password("Passcode"),
    "jimmyjdejesus-cmyk": hash_password("your_password_here"),
    # Add more users as needed
}
ADMIN_USER = "Moodeux"

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USER_DB and verify_password(password, USER_DB[username]):
            st.session_state.user = username
            st.session_state.is_admin = (username == ADMIN_USER)
            st.success(f"Welcome, {username}!")
        else:
            st.session_state.user = None
            st.error("Invalid username or password")
    if "user" not in st.session_state:
        st.stop()

login()
USER = st.session_state.user
IS_ADMIN = st.session_state.get("is_admin", False)

PREFS_DIR = os.path.join(os.path.expanduser("~"), ".jarvis_prefs")
os.makedirs(PREFS_DIR, exist_ok=True)
PREFS_PATH = os.path.join(PREFS_DIR, f"{USER}_prefs.enc")
KEY_PATH = os.path.join(PREFS_DIR, f"{USER}.key")

def load_user_prefs():
    if os.path.exists(PREFS_PATH):
        key = load_user_key(KEY_PATH)
        with open(PREFS_PATH, "rb") as f:
            enc = f.read()
        try:
            data = decrypt_json(enc, key)
            return data
        except Exception as e:
            st.error(f"Failed to decrypt preferences for user {USER}: {e}")
    return {}

def save_user_prefs():
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
    key = load_user_key(KEY_PATH)
    enc = encrypt_json(prefs, key)
    with open(PREFS_PATH, "wb") as f:
        f.write(enc)

prefs = load_user_prefs()
for key, value in prefs.items():
    st.session_state[key] = value

sidebar(USER, save_user_prefs)

st.title(f"Jarvis Modular Agentic AI ({USER})")
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