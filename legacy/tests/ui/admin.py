import streamlit as st

def render_admin_panel():
    st.header("Admin Panel")
    from database import get_pending_users, remove_pending_user
    pending_users = get_pending_users()
    if not pending_users:
        st.info("No pending users.")
        return
    for user in pending_users:
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown(f"**{user['username']}** - {user['name']} ({user['email']})")
        with col2:
            if st.button(f"Approve {user['username']}"):
                # Approve logic: move user from pending_users to authenticator (not shown, depends on your system)
                remove_pending_user(user['username'])
                st.success(f"Approved {user['username']}")
                st.rerun()
            if st.button(f"Reject {user['username']}"):
                remove_pending_user(user['username'])
                st.warning(f"Rejected {user['username']}")
                st.rerun()