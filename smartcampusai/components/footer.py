import streamlit as st

def render_footer():
    """Renders a simple, elegant system footer at the bottom of the screen."""
    st.markdown(
        """
        <div class="footer-text">
            <p style="margin: 0; padding: 16px 0;">
                © 2026 SmartCampusAI • AI-Powered Campus Management System • Powered by Google Gemini API
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
