import streamlit as st
import os

def render_file_browser(start_path=".", max_items=10):
    with st.expander("File Browser", expanded=False):
        count = 0
        for root, dirs, files in os.walk(start_path):
            for d in dirs:
                st.markdown(f"📁 {os.path.join(root, d)}")
                count += 1
                if count >= max_items:
                    st.markdown("...")
                    return
            for f in files:
                st.markdown(f"📄 {os.path.join(root, f)}")
                count += 1
                if count >= max_items:
                    st.markdown("...")
                    return
            break