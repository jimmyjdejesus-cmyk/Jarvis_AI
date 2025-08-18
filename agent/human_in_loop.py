import streamlit as st


def request_human_reasoning(prompt, reasoning_path=None):
    """
    Requests human reasoning for a given prompt and reasoning path.
    Returns the human's input or approval status.
    """
    import streamlit as st
    st.markdown(f"## Human-in-Loop Reasoning\nPrompt: {prompt}")
    if reasoning_path:
        st.markdown(f"**Reasoning Path:** {reasoning_path}")
    user_input = st.text_area("Your reasoning or next steps:")
    if st.button("Submit Reasoning"):
        return user_input or "No reasoning provided."
    return "Awaiting human reasoning..."