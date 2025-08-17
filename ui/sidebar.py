import streamlit as st
import uuid

AVAILABLE_MODELS = [
    "Gemm3:12b-it-qat",
    "gemma3:1b",
    "Deepeek-r1-0528-qwen3-8b",
    "qwen3-.6b"
]

def auto_chat_name(context):
    if not context:
        return "New Chat"
    context = context.strip()
    if len(context) > 40:
        context = context[:37] + "..."
    return context.replace("\n", " ") or "New Chat"

def sidebar(user, save_user_prefs):
    with st.sidebar:
        st.markdown(f"### 👤 User: `{user}`")
        st.markdown("## 📁 Projects & Chats")
        if "folders" not in st.session_state:
            st.session_state.folders = {"Main": ["Default"]}
        if "current_folder" not in st.session_state:
            st.session_state.current_folder = "Main"
        if "current_session" not in st.session_state:
            st.session_state.current_session = "Default"
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = {"Default": []}
        if "chat_contexts" not in st.session_state:
            st.session_state.chat_contexts = {"Default": "New Chat"}

        folder_names = list(st.session_state.folders.keys())
        selected_folder = st.selectbox("📂 Select Folder", folder_names, index=folder_names.index(st.session_state.current_folder), help="Choose or organize folders/projects")
        if selected_folder != st.session_state.current_folder:
            st.session_state.current_folder = selected_folder
            save_user_prefs()

        session_names = st.session_state.folders[selected_folder]
        session_display_names = [st.session_state.chat_contexts.get(sess, sess) for sess in session_names]
        selected_session_idx = session_names.index(st.session_state.current_session)
        selected_session = st.selectbox("💬 Select Chat", session_display_names, index=selected_session_idx, help="Right-click to rename (coming soon), drag to reorder (coming soon)")
        if session_names[selected_session_idx] != st.session_state.current_session:
            st.session_state.current_session = session_names[selected_session_idx]
            save_user_prefs()

        st.markdown('<span title="Start a new chat based on context"><button style="font-size:1.1em;">➕ New Chat</button></span>', unsafe_allow_html=True)
        if st.button("Create New Chat (plus button above)"):
            prev_context = ""
            if st.session_state.current_session in st.session_state.chat_sessions and len(st.session_state.chat_sessions[st.session_state.current_session]) > 0:
                prev_context = st.session_state.chat_sessions[st.session_state.current_session][0]["content"]
            new_chat_name = auto_chat_name(prev_context)
            new_id = str(uuid.uuid4())[:8]
            new_session = f"Chat_{new_id}"
            st.session_state.folders[selected_folder].append(new_session)
            st.session_state.chat_sessions[new_session] = []
            st.session_state.chat_contexts[new_session] = new_chat_name
            st.session_state.current_session = new_session
            st.success(f"Chat '{new_chat_name}' created.")
            save_user_prefs()

        rename_session = st.text_input("✏️ Rename current chat", value=st.session_state.chat_contexts.get(st.session_state.current_session, st.session_state.current_session))
        if st.button("Rename Chat"):
            st.session_state.chat_contexts[st.session_state.current_session] = rename_session
            st.success(f"Chat renamed to '{rename_session}'.")
            save_user_prefs()

        new_folder = st.text_input("New Folder Name")
        if st.button("Add Folder"):
            if new_folder and new_folder not in folder_names:
                st.session_state.folders[new_folder] = []
                st.success(f"Folder '{new_folder}' created.")
                save_user_prefs()

        rename_folder = st.text_input("Rename current folder", value=st.session_state.current_folder)
        if st.button("Rename Folder"):
            if rename_folder and rename_folder not in folder_names:
                old_folder = st.session_state.current_folder
                st.session_state.folders[rename_folder] = st.session_state.folders.pop(old_folder)
                st.session_state.current_folder = rename_folder
                st.success(f"Folder renamed to '{rename_folder}'.")
                save_user_prefs()

        expert_model = st.selectbox("🤖 Expert Model", AVAILABLE_MODELS, index=0)
        if expert_model != st.session_state.get("selected_expert_model", AVAILABLE_MODELS[0]):
            st.session_state.selected_expert_model = expert_model
            save_user_prefs()

        draft_model = st.selectbox("🤖 Draft Model", AVAILABLE_MODELS, index=1)
        if draft_model != st.session_state.get("selected_draft_model", AVAILABLE_MODELS[1]):
            st.session_state.selected_draft_model = draft_model
            save_user_prefs()

        persona_prompt = st.text_area("🧠 Agent Persona Prompt", value=st.session_state.get("persona_prompt", f"You are an expert assistant using the {expert_model} (expert) and {draft_model} (draft) models."))
        if persona_prompt != st.session_state.get("persona_prompt", ""):
            st.session_state.persona_prompt = persona_prompt
            save_user_prefs()

        st.markdown("---")
        st.caption("💡 Tip: Drag & drop and right-click features coming soon for chat/folder management!")