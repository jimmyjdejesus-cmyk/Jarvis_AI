import streamlit as st
import time
from ollama_client import get_available_models, stream_generation, pull_model_subprocess
from rag_handler import get_augmented_prompt

# --- Page Configuration ---
st.set_page_config(page_title="Janus AI Research Assistant", page_icon="🤖", layout="wide")

# --- Persona Definitions (with new, user-friendly names) ---
PERSONA_PROMPTS = {
    "Code Expert (Default)": "You are an expert-level programmer and systems thinker. Engage in technical debate, review code, and collaborate on solutions as an equal partner.",
    "Critical Thinking Teacher": "You will not provide direct answers. Instead, you will guide the user through a series of reflective, open-ended questions to help them arrive at their own conclusions. Your goal is to foster critical thinking.",
    "Harsh Critic": "You will adopt a critical stance. Your goal is to identify weaknesses, challenge assumptions, and play devil's advocate to strengthen the user's work.",
    "Strategic Guide/Project Planning": "You will act as a strategic guide for high-level planning. Help formulate research questions, structure projects, and define methodologies."
}

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
if "last_generation_stats" not in st.session_state:
    st.session_state.last_generation_stats = {}

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Configuration")

    # NEW: Persona Selector
    selected_persona = st.selectbox("Choose a Persona:", list(PERSONA_PROMPTS.keys()))

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
            index = installed_models.index(recommendation) if recommendation in installed_models else 0
            selected_model = st.selectbox("Select Model", installed_models, index=index)
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
        st.session_state.last_generation_stats = {}
        st.rerun()

    # Token Tracker Display
    st.divider()
    st.header("📊 Token Tracker")
    stats = st.session_state.last_generation_stats
    if stats:
        st.metric(label="Generation Speed", value=f"{stats.get('tokens_per_sec', 0):.2f} t/s")
        st.text(f"Prompt Tokens: {stats.get('prompt_tokens', 0)}")
        st.text(f"Response Tokens: {stats.get('response_tokens', 0)}")
        st.text(f"Total Time: {stats.get('total_duration_s', 0):.2f}s")
    else:
        st.text("No generation yet.")

# --- Main Chat Interface ---
st.title("Janus: Private, Real-time AI Research Assistant")

# Display existing chat messages from history
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
        interim_prompt, sources = (prompt, [])
        if enable_rag and selected_model:
            with st.spinner("Searching web and preparing context..."):
                interim_prompt, sources = get_augmented_prompt(prompt)

        # Prepend the persona system prompt
        system_prompt = PERSONA_PROMPTS[selected_persona]
        final_prompt_with_persona = f"{system_prompt}\n\n---\n\nUser Question: {interim_prompt}"

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
                final_stats = {}
                for part in stream_generation(selected_model, final_prompt_with_persona):
                    if "response" in part:
                        full_response += part["response"]
                        response_placeholder.markdown(full_response + "▌")
                    elif "error" in part:
                        full_response = f"Error from Ollama: {part['error']}"
                        break

                    if part.get("done", False):
                        final_stats = part

                response_placeholder.markdown(full_response)

                if final_stats:
                    eval_duration_s = final_stats.get("eval_duration", 1) / 1e9
                    eval_count = final_stats.get("eval_count", 0)
                    tokens_per_sec = eval_count / eval_duration_s if eval_duration_s > 0 else 0

                    st.session_state.last_generation_stats = {
                        "prompt_tokens": final_stats.get("prompt_eval_count", 0),
                        "response_tokens": eval_count,
                        "total_duration_s": final_stats.get("total_duration", 0) / 1e9,
                        "tokens_per_sec": tokens_per_sec
                    }
            except Exception as e:
                full_response = f"An error occurred: {e}"

        response_placeholder.markdown(full_response)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources if enable_rag else []
    })

    st.rerun()