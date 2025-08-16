# app.py
import streamlit as st
from ollama_client import get_available_models, stream_generation, pull_model_subprocess
from rag_handler import get_augmented_prompt

# --- Page Configuration ---
st.set_page_config(page_title="Janus AI Research Assistant", page_icon="🤖", layout="wide")

# --- Task Recommendations Dictionary ---
TASK_RECOMMENDATIONS = {
    "Conversational Chat": {
        "recommendation": "mixtral",
        "description": "Good for general Q&A, brainstorming, and fluid conversation."
    },
    "Code Generation & Debugging": {
        "recommendation": "codellama:34b",
        "description": "A specialist model for writing, completing, and explaining code."
    },
    "Creative Writing": {
        "recommendation": "llama3:8b",
        "description": "A great all-rounder for generating stories, marketing copy, and other creative text."
    },
    "Complex Reasoning": {
        "recommendation": "gemma3:12b",
        "description": "Best for tasks requiring multi-step thinking and analysis."
    }
}

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Configuration")

    # Task Selector
    task = st.selectbox("Choose a task:", list(TASK_RECOMMENDATIONS.keys()))

    # Display Recommendation based on Task
    recommendation = TASK_RECOMMENDATIONS[task]["recommendation"]
    description = TASK_RECOMMENDATIONS[task]["description"]
    st.info(f"**Recommended Model:** `{recommendation}`\n\n*_{description}_*")

    # Model Selector
    try:
        installed_models = get_available_models()
        if installed_models:
            selected_model = st.selectbox("Select Model", installed_models, index=installed_models.index(
                recommendation) if recommendation in installed_models else 0)
        else:
            selected_model = None
            st.warning("Ollama is not running or no models found.")
    except Exception as e:
        selected_model = None
        installed_models = []
        st.error(f"Failed to connect to Ollama: {e}")

    # Model Installation Logic
    if recommendation not in installed_models:
        st.warning(f"Recommended model '{recommendation}' is not installed.")
        if st.button(f"Download {recommendation}"):
            with st.spinner(f"Downloading {recommendation}... This may take a while."):
                progress_area = st.empty()
                for output in pull_model_subprocess(recommendation):
                    progress_area.text(output)
            st.success(f"Model '{recommendation}' has been downloaded!")
            st.rerun()

    # Web Research Checkbox
    enable_rag = st.checkbox("Enable Web Research", value=True)

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# --- Main Chat Interface ---
st.title("Janus: Private, Real-time AI Research Assistant")

# Display existing chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("Sources used for context"):
                for src in message["sources"]:
                    st.markdown(f"- [{src['title']}]({src['url']})")

# Chat input field
if prompt := st.chat_input("Ask your question..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        final_prompt, sources = (prompt, [])
        if enable_rag and selected_model:
            with st.spinner("Searching web and preparing context..."):
                final_prompt, sources = get_augmented_prompt(prompt)

        if sources:
            with st.expander("Sources used for context"):
                for src in sources:
                    st.markdown(f"- [{src['title']}]({src['url']})")

        response_placeholder = st.empty()
        full_response = ""

        if not selected_model:
            full_response = "Please select a model from the sidebar to begin."
        else:
            try:
                for part in stream_generation(selected_model, final_prompt):
                    if "response" in part:
                        full_response += part["response"]
                        response_placeholder.markdown(full_response + "▌")
                    elif "error" in part:
                        full_response = f"Error from Ollama: {part['error']}"
                        break
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"An error occurred: {e}"

        response_placeholder.markdown(full_response)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources if enable_rag else []
    })