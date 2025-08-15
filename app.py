import streamlit as st
from ollama_client import get_available_models, stream_generation
from rag_handler import get_augmented_prompt  # Assuming this returns a tuple (prompt, sources)

# --- Page Configuration ---
st.set_page_config(page_title="Janus AI Research Assistant", page_icon="🤖", layout="wide")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Configuration")
    try:
        models = get_available_models()
        if models:
            selected_model = st.selectbox("Select Model", models)
        else:
            selected_model = None
            st.warning("Ollama is not running or no models found.")
    except Exception as e:
        selected_model = None
        st.error(f"Failed to connect to Ollama: {e}")

    enable_rag = st.checkbox("Enable Real-time Web Search (RAG)", value=True)
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# --- Main Chat Interface ---
st.title("Janus: Private, Real-time AI Research Assistant")

# Display existing chat messages from history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display sources if they exist
        if "sources" in message and message["sources"]:
            with st.expander("Sources used for context"):
                for src in message["sources"]:
                    st.markdown(f"- [{src['title']}]({src['url']})")

# Chat input field
if prompt := st.chat_input("Ask your question..."):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Generate and Stream Assistant Response ---
    with st.chat_message("assistant"):
        final_prompt = prompt
        sources = []

        # Prepare prompt (with RAG if enabled)
        if enable_rag and selected_model:
            with st.spinner("Searching web and preparing context..."):
                final_prompt, sources = get_augmented_prompt(prompt)

        # Display sources before streaming the answer
        if sources:
            with st.expander("Sources used for context"):
                for src in sources:
                    st.markdown(f"- [{src['title']}]({src['url']})")

        # Stream the response
        response_placeholder = st.empty()
        full_response = ""

        if not selected_model:
            full_response = "Please select a model from the sidebar to begin."
        else:
            try:
                # BUG FIX: Iterate through JSON objects and extract the 'response' key
                for part in stream_generation(selected_model, final_prompt):
                    # --- DEBUGGING STEP: Print the raw part from Ollama ---
                    print(f"RAW OLLAMA PART: {part}")
                    # --------------------------------------------------------

                    if "response" in part:
                        token = part["response"]
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")
                    elif "error" in part:
                        full_response = f"Error from Ollama: {part['error']}"
                        break
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"An error occurred: {e}"

        response_placeholder.markdown(full_response)

    # Add the complete assistant message and sources to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources if enable_rag else []
    })