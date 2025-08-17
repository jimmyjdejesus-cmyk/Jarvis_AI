import streamlit as st

def render_sidebar(config, authenticator):
    st.title(f"Welcome, {st.session_state.get('name', 'User')}!")
    authenticator.logout('Logout')
    st.divider()
    st.header("🗂️ Projects & Sessions")

    from database import get_projects, add_project, get_sessions_for_project, create_new_session, rename_session, \
        delete_session, delete_project
    username = st.session_state.get("username")
    projects = get_projects(username)
    if not projects:
        projects = ["default"]

    # Project tree UI
    for project in projects:
        with st.expander(f"📁 {project}", expanded=(project == st.session_state.get('selected_project', projects[0]))):
            st.session_state.selected_project = project
            if st.button("🗑️ Delete Project", key=f"del_proj_{project}"):
                delete_project(username, project)
                st.experimental_rerun()
            sessions = get_sessions_for_project(username, project)
            for session in sessions:
                col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                with col1:
                    if st.button(f"💬 {session['name']}", key=f"select_{session['id']}", use_container_width=True):
                        st.session_state.session_id = session['id']
                        st.experimental_rerun()
                with col2:
                    if st.button("✏️", key=f"rename_btn_{session['id']}"):
                        new_name = st.text_input("Rename to:", value=session['name'], key=f"rename_txt_{session['id']}")
                        if st.button("Save", key=f"save_rename_{session['id']}"):
                            rename_session(session['id'], new_name)
                            st.experimental_rerun()
                with col3:
                    if st.button("🗑️", key=f"del_{session['id']}"):
                        delete_session(session['id'])
                        st.experimental_rerun()
            if st.button("➕ New Session", key=f"new_sess_{project}"):
                new_session_id = create_new_session(username, project)
                st.session_state.session_id = new_session_id
                st.experimental_rerun()
    if st.button("➕ New Project"):
        new_project_name = st.text_input("Project Name", key="new_project_name")
        if st.button("Create", key="create_project_btn"):
            if new_project_name and new_project_name not in projects:
                add_project(username, new_project_name)
                st.session_state.selected_project = new_project_name
                st.success(f"Project '{new_project_name}' created!")
                st.experimental_rerun()
            else:
                st.warning("Please enter a unique project name.")


DEFAULT_JARVS = {
    "Code Expert (Default)": "You are an expert-level programmer and systems thinker. Engage in technical debate, review code, and collaborate on solutions as an superior.",
    "Critical Thinking Teacher": "You will not provide direct answers. Instead, you will guide the user through a series of reflective, open-ended questions to help them arrive at their own conclusions. Your goal is to foster critical thinking.",
    "Harsh Critic": "You will adopt a critical stance. Your goal is to identify weaknesses, challenge assumptions, and play devil's advocate to strengthen the user's work.",
    "Strategic Guide/Project Planning": "You will act as a strategic guide for high-level planning. Help formulate research questions, structure projects, and define methodologies."
}