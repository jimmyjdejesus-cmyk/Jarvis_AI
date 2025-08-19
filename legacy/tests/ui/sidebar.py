import streamlit as st
import uuid
import json

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
        # --- Model Configuration & Status ---
        st.markdown("## 🤖 AI Models")
        
        model_list = get_available_models()
        if not model_list:
            st.warning("🟡 No models found. Check Ollama connection or pull models via Admin Panel.")
            if st.button("🔄 Retry Connection"):
                # Clear cache to force refresh
                import ollama_client
                ollama_client.clear_model_cache()
                st.rerun()
        else:
            st.success(f"🟢 {len(model_list)} models available!")
            
            # Model status indicator
            if st.button("🔄 Refresh Models"):
                import ollama_client
                ollama_client.clear_model_cache()
                st.rerun()
        # ...existing code...
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
        # Ensure we have a fallback model if list is empty
        if not model_list:
            model_list = ["qwen3:0.6b"]
        
        # Initialize session state if not set
        if "selected_expert_model" not in st.session_state:
            st.session_state.selected_expert_model = model_list[0]
        if "selected_draft_model" not in st.session_state:
            st.session_state.selected_draft_model = model_list[0] if len(model_list) == 1 else model_list[1] if len(model_list) > 1 else model_list[0]
        
        # Expert Model Selection with enhanced UI
        expert_model = st.selectbox(
            "🧠 Expert Model", 
            model_list, 
            index=model_list.index(st.session_state.selected_expert_model) if st.session_state.selected_expert_model in model_list else 0,
            help="Primary model for complex reasoning and final responses"
        )
        if expert_model != st.session_state.get("selected_expert_model"):
            st.session_state.selected_expert_model = expert_model
            save_user_preference(user, "selected_expert_model", expert_model)
            st.success(f"Expert model switched to: {expert_model}")
        
        # Speculative Decoding Configuration
        enable_speculative = st.checkbox(
            "⚡ Enable Speculative Decoding", 
            value=st.session_state.get("enable_speculative_decoding", False),
            help="Use a draft model to speed up generation"
        )
        st.session_state.enable_speculative_decoding = enable_speculative
        save_user_preference(user, "enable_speculative_decoding", enable_speculative)
        
        if enable_speculative:
            draft_model = st.selectbox(
                "🏃 Draft Model", 
                model_list, 
                index=model_list.index(st.session_state.selected_draft_model) if st.session_state.selected_draft_model in model_list else (1 if len(model_list) > 1 else 0),
                help="Faster model for initial draft generation"
            )
            if draft_model != st.session_state.get("selected_draft_model"):
                st.session_state.selected_draft_model = draft_model
                save_user_preference(user, "selected_draft_model", draft_model)
                st.success(f"Draft model switched to: {draft_model}")
            
            # Show performance tip
            if expert_model == draft_model:
                st.warning("💡 Tip: Use different models for expert and draft to maximize speculative decoding benefits")
        else:
            # If speculative decoding is disabled, still maintain draft model for compatibility
            draft_model = expert_model
            st.session_state.selected_draft_model = draft_model
        
        # Model performance info
        if len(model_list) > 1:
            with st.expander("📊 Model Performance Tips"):
                st.markdown("""
                **Expert Model**: Choose your most capable model for final responses
                - Larger models (4b, 7b+) for complex reasoning
                - Smaller models (0.5b, 1b) for simple tasks
                
                **Speculative Decoding**: Speeds up generation by ~20-40%
                - Use a smaller/faster model as draft
                - Expert model refines the draft output
                - Best when models have similar training data
                """)
        
        # Persona configuration with model context
        persona_prompt = st.text_area(
            "🧠 Agent Persona Prompt", 
            value=st.session_state.get("persona_prompt", 
                f"You are an expert assistant using {expert_model} for responses" + 
                (f" with {draft_model} for draft generation" if enable_speculative else "") + 
                ". Provide helpful, accurate, and detailed responses."),
            help="Customize the AI's personality and expertise"
        )
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