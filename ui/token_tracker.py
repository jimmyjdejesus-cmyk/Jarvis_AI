import streamlit as st
import platform
import psutil
import time

def render_token_tracker(token_count: int, performance_score: float, last_latency=None, hardware_info=None):
    st.subheader("Performance Log")
    status = "Great" if performance_score > 0.8 else "Good" if performance_score > 0.5 else "Slow"
    st.markdown(f"**Tokens Used:** {token_count}")
    st.progress(performance_score, text=f"Performance: {status}")
    if last_latency is not None:
        st.markdown(f"**Last Response Latency:** {last_latency:.2f} seconds")
    else:
        st.markdown("**Last Response Latency:** n/a")
    # Hardware info
    if not hardware_info:
        hardware_info = {
            "CPU": platform.processor(),
            "RAM": f"{psutil.virtual_memory().total // (1024**2)} MB",
            "Platform": platform.system()
        }
    st.markdown("**Consumer Hardware Info:**")
    for k, v in hardware_info.items():
        st.markdown(f"- {k}: {v}")

    # Simple performance advice
    if performance_score < 0.5 or (last_latency and last_latency > 10):
        st.warning("Your hardware or model selection may be slow. Consider a smaller model or closing background apps.")
    elif performance_score > 0.8 and (last_latency is not None and last_latency < 2):
        st.success("Janus AI is running smoothly on your hardware!")

def update_performance_metrics(start_time):
    latency = time.time() - start_time
    # Update session state
    st.session_state["last_latency"] = latency
    # Optionally, update performance_score based on latency
    if latency < 2:
        st.session_state["performance_score"] = 1.0
    elif latency < 5:
        st.session_state["performance_score"] = 0.7
    elif latency < 10:
        st.session_state["performance_score"] = 0.5
    else:
        st.session_state["performance_score"] = 0.3