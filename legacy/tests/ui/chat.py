import streamlit as st
from database import save_message, load_session_history

def render_chat_interface():
    from database import get_user_preferences, get_user_settings, load_session_history
    user = st.session_state.get("username", "default")
    # Restore preferences/settings from DB
    prefs = get_user_preferences(user)
    settings = get_user_settings(user)
    selected_project = prefs.get("selected_project", "default")
    st.title(f"Janus AI | Project: {selected_project}")

    session_id = st.session_state.get('session_id')
    if session_id:
        if st.session_state.get('current_session_id') != session_id:
            st.session_state.chat_history = load_session_history(session_id)
            st.session_state.current_session_id = session_id
    else:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your question...")
    if prompt:
        if not session_id:
            st.warning("Please create or select a chat session to begin.")
            return
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat_history.append(user_message)
        if not st.session_state.get("ghost_mode", False):
            from database import save_message
            save_message(session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get active JarVS persona prompt (custom or default)
        jarvs_prompt = prefs.get("active_jarvs_prompt", "")
        # AI response
        from ollama_client import stream_generation
        from rag_handler import get_augmented_prompt
        enable_rag = prefs.get("enable_rag", True)
        selected_expert_model = prefs.get("selected_expert_model")
        selected_draft_model = prefs.get("selected_draft_model")

        # RAG augmentation if enabled
        interim_prompt, sources = (prompt, [])
        if enable_rag and selected_expert_model:
            with st.spinner("Searching..."):
                interim_prompt, sources = get_augmented_prompt(prompt, selected_expert_model)
        final_prompt_with_persona = f"{jarvs_prompt}\n\n---\n\nUser Question: {interim_prompt}"

        response_placeholder = st.empty()
        full_response = ""
        if not selected_expert_model:
            full_response = "Please select an expert model."
        else:
            try:
                for part in stream_generation(selected_expert_model, final_prompt_with_persona, selected_draft_model):
                    if "response" in part:
                        full_response += part["response"]
                        response_placeholder.markdown(full_response + "\u258c")
                    elif "error" in part:
                        full_response = f"Error from Ollama: {part['error']}"
                        break
            except Exception as e:
                full_response = f"An error occurred: {e}"

        response_placeholder.markdown(full_response)
        assistant_message = {"role": "assistant", "content": full_response, "sources": sources if enable_rag else []}
        st.session_state.chat_history.append(assistant_message)
        if not st.session_state.get("ghost_mode", False):
            from database import save_message
            save_message(session_id, "assistant", full_response, sources)
        st.experimental_rerun()