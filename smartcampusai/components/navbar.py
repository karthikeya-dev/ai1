import streamlit as st
from datetime import datetime

def render_navbar():
    """Renders the top navigation header containing logo, user context, role, and current time."""
    if "user" in st.session_state and st.session_state.user:
        user = st.session_state.user
        role = user.get("role", "Student")
        name = user.get("name", "User")
        
        # Color classes based on role
        badge_class = f"badge-{role.lower()}"
        
        # Format current system time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Custom navbar HTML injection (incorporates layout and styling classes from style.css)
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 12px 24px; background: rgba(255, 255, 255, 0.02); 
                        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); 
                        margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem; font-weight: 800; 
                                 background: linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%);
                                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                         SmartCampusAI
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 16px;">
                    <span style="font-size: 0.85rem; opacity: 0.7;">
                        :material/schedule: {current_time}
                    </span>
                    <span class="custom-badge {badge_class}">
                        {role}
                    </span>
                    <span style="font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; gap: 6px;">
                        :material/person: {name}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 12px 24px; background: rgba(255, 255, 255, 0.02); 
                        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); 
                        margin-bottom: 24px;">
                <span style="font-size: 1.5rem; font-weight: 800; 
                             background: linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%);
                             -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                     SmartCampusAI
                </span>
                <span style="font-size: 0.85rem; opacity: 0.7;">
                    Please log in to continue
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
