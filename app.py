import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

from database import init_db
from ui.auth import render_auth_screen
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface
from ui.file_browser import render_file_browser
from ui.token_tracker import render_token_tracker

init_db()

try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("`config.yaml` not found. Please create it and restart the app.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookies']['cookie_name'],
    config['cookies']['key'],
    config['cookies']['cookie_expiry_days']
)

if not st.session_state.get("authentication_status"):
    render_auth_screen(authenticator)
else:
    with st.sidebar:
        render_sidebar(config, authenticator)
        # Place file browser as a small expander in the sidebar
        render_file_browser(start_path=".", max_items=10)
    tabs = st.tabs(["💬 Chat", "🧮 Performance Log"])
    with tabs[0]:
        render_chat_interface()
    with tabs[1]:
        render_token_tracker(
            token_count=st.session_state.get("token_count", 0),
            performance_score=st.session_state.get("performance_score", 1.0),
            last_latency=st.session_state.get("last_latency", None),
            hardware_info=st.session_state.get("hardware_info", None),
        )