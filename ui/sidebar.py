import streamlit as st
import uuid


from ollama_client import get_available_models


def auto_chat_name(context):
    if not context:
        return "New Chat"
    context = context.strip()
    if len(context) > 40:
        context = context[:37] + "..."
    return context.replace("\n", " ") or "New Chat"

def sidebar(user, save_user_prefs):
    from database import get_user_preferences, save_user_preference, backup_user_data, import_user_data, get_user_settings, save_user_settings
    with st.sidebar:
        st.markdown(f"### 👤 User: `{user}`")
        st.markdown("## 📁 Projects & Chats")
        # Load preferences from DB
        prefs = get_user_preferences(user)
        settings = get_user_settings(user)
        # Restore session state from DB if available
        st.session_state.folders = prefs.get("folders", {"Main": ["Default"]})
        st.session_state.current_folder = prefs.get("current_folder", "Main")
        st.session_state.current_session = prefs.get("current_session", "Default")
        st.session_state.chat_sessions = prefs.get("chat_sessions", {"Default": []})
        st.session_state.chat_contexts = prefs.get("chat_contexts", {"Default": "New Chat"})
        folder_names = list(st.session_state.folders.keys())
        selected_folder = st.selectbox("📂 Select Folder", folder_names, index=folder_names.index(st.session_state.current_folder), help="Choose or organize folders/projects")
        if selected_folder != st.session_state.current_folder:
            st.session_state.current_folder = selected_folder
            save_user_preference(user, "current_folder", selected_folder)
        session_names = st.session_state.folders[selected_folder]
        session_display_names = [st.session_state.chat_contexts.get(sess, sess) for sess in session_names]
        selected_session_idx = session_names.index(st.session_state.current_session)
        selected_session = st.selectbox("💬 Select Chat", session_display_names, index=selected_session_idx, help="Right-click to rename (coming soon), drag to reorder (coming soon)")
        if session_names[selected_session_idx] != st.session_state.current_session:
            st.session_state.current_session = session_names[selected_session_idx]
            save_user_preference(user, "current_session", st.session_state.current_session)
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
            save_user_preference(user, "folders", st.session_state.folders)
            save_user_preference(user, "chat_sessions", st.session_state.chat_sessions)
            save_user_preference(user, "chat_contexts", st.session_state.chat_contexts)
            save_user_preference(user, "current_session", new_session)
        rename_session = st.text_input("✏️ Rename current chat", value=st.session_state.chat_contexts.get(st.session_state.current_session, st.session_state.current_session))
        if st.button("Rename Chat"):
            st.session_state.chat_contexts[st.session_state.current_session] = rename_session
            st.success(f"Chat renamed to '{rename_session}'.")
            save_user_preference(user, "chat_contexts", st.session_state.chat_contexts)
        new_folder = st.text_input("New Folder Name")
        if st.button("Add Folder"):
            if new_folder and new_folder not in folder_names:
                st.session_state.folders[new_folder] = []
                st.success(f"Folder '{new_folder}' created.")
                save_user_preference(user, "folders", st.session_state.folders)
        rename_folder = st.text_input("Rename current folder", value=st.session_state.current_folder)
        if st.button("Rename Folder"):
            if rename_folder and rename_folder not in folder_names:
                old_folder = st.session_state.current_folder
                st.session_state.folders[rename_folder] = st.session_state.folders.pop(old_folder)
                st.session_state.current_folder = rename_folder
                st.success(f"Folder renamed to '{rename_folder}'.")
                save_user_preference(user, "folders", st.session_state.folders)
                save_user_preference(user, "current_folder", rename_folder)
        model_list = get_available_models()
        expert_model = st.selectbox("🤖 Expert Model", model_list, index=0 if model_list else None)
        if expert_model != st.session_state.get("selected_expert_model", (model_list[0] if model_list else None)):
            st.session_state.selected_expert_model = expert_model
            save_user_preference(user, "selected_expert_model", expert_model)
        draft_model = st.selectbox("🤖 Draft Model", model_list, index=1 if len(model_list) > 1 else 0)
        if draft_model != st.session_state.get("selected_draft_model", (model_list[1] if len(model_list) > 1 else model_list[0] if model_list else None)):
            st.session_state.selected_draft_model = draft_model
            save_user_preference(user, "selected_draft_model", draft_model)
        persona_prompt = st.text_area("🧠 Agent Persona Prompt", value=st.session_state.get("persona_prompt", f"You are an expert assistant using the {expert_model} (expert) and {draft_model} (draft) models."))
        if persona_prompt != st.session_state.get("persona_prompt", ""):
            st.session_state.persona_prompt = persona_prompt
            save_user_preference(user, "persona_prompt", persona_prompt)
        # Backup/export/import UI
        st.markdown("---")
        st.subheader("Backup & Import/Export")
        if st.button("Backup My Data"):
            backup = backup_user_data(user)
            st.download_button("Download Backup", data=json.dumps(backup, indent=2), file_name=f"{user}_backup.json")
        uploaded = st.file_uploader("Import Data (JSON)", type=["json"])
        if uploaded:
            try:
                import_data = json.load(uploaded)
                import_user_data(user, import_data)
                st.success("Data imported successfully!")
            except Exception as e:
                st.error(f"Import failed: {e}")
        st.markdown("---")
        st.caption("💡 Tip: Drag & drop and right-click features coming soon for chat/folder management!")