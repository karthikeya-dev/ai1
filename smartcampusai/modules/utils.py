import streamlit as st
import os

def load_css():
    """Loads the main visual styling rules from styles/style.css into the app."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = os.path.join(base_dir, "styles", "style.css")
    
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to load styles/style.css: {str(e)}")

def check_access(allowed_roles: list[str]) -> bool:
    """
    Check if the user is authenticated and has one of the allowed roles.
    If not allowed, shows a clean access error screen and returns False.
    """
    # Load CSS globally
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required! Please log in first.", icon=":material/lock:")
        return False
        
    role = st.session_state.user.get("role")
    if role not in allowed_roles:
        st.error(f"Access Denied! Your role '{role}' is not authorized to view this page.", icon=":material/gpp_bad:")
        return False
        
    return True

def styled_header(title: str, subtitle: str = None, icon: str = None):
    """Generates a premium styled page header using linear gradient typography."""
    icon_str = f":material/{icon}: " if icon else ""
    st.markdown(
        f"""
        <div style='margin-bottom: 24px;'>
            <h1 style='margin: 0; font-size: 2.2rem; font-weight: 800;'>
                {icon_str}<span class="gradient-text">{title}</span>
            </h1>
            {f"<p style='margin: 6px 0 0 0; font-size: 1rem; opacity: 0.7;'>{subtitle}</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True
    )
