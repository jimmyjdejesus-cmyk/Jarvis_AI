import streamlit as st

def render_auth_screen(authenticator):
    st.title("Welcome to Janus")
    st.info("Please login or register to continue.")
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            # Call Streamlit Authenticator's login API
            st.session_state["username"] = username
            st.session_state["password"] = password
            authenticator.login()
            # Authenticator will update st.session_state["authentication_status"]

    with tabs[1]:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_name = st.text_input("Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register", key="register_button"):
            st.session_state["username"] = reg_username
            st.session_state["name"] = reg_name
            st.session_state["email"] = reg_email
            st.session_state["password"] = reg_password
            try:
                if authenticator.register_user(pre_authorized=False):
                    st.success('User registered successfully! Awaiting admin approval.')
            except Exception as e:
                st.error(e)