import streamlit as st

def render_sidebar():
    """Renders custom headers, indicators, and a logout button inside the sidebar area."""
    with st.sidebar:
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        
        # Display logo if it exists (using local logo path or standard placeholder icons)
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 20px;'>
                <div style='font-size: 2.5rem; color: #00f0ff; margin-bottom: 8px;'>
                    :material/school:
                </div>
                <h3 style='margin: 0; font-weight: 700; color: var(--text-color);'>SmartCampusAI</h3>
                <p style='margin: 4px 0 0 0; font-size: 0.8rem; opacity: 0.6;'>Next-Gen Campus Hub</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # User details card inside sidebar
        if "user" in st.session_state and st.session_state.user:
            user = st.session_state.user
            st.markdown(
                f"""
                <div style='background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); 
                            border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: center;'>
                    <div style='font-weight: 600; font-size: 0.9rem;'>{user.get("name", "User")}</div>
                    <div style='font-size: 0.75rem; opacity: 0.6; margin-top: 2px;'>@{user.get("username", "username")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Logout button
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            if st.button("Log out", icon=":material/logout:", key="sidebar_logout_btn"):
                # Clear session state
                st.session_state.user = None
                st.session_state.authenticated = False
                st.toast("Logged out successfully!", icon=":material/check_circle:")
                st.rerun()
        else:
            st.markdown(
                """
                <div style='text-align: center; padding: 16px; opacity: 0.6; font-size: 0.85rem;'>
                    :material/lock: Authentication required
                </div>
                """,
                unsafe_allow_html=True
            )
