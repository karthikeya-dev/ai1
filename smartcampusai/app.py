import streamlit as st
import os
from dotenv import load_dotenv

# Set page configurations as the first Streamlit command to prevent visual blinking
st.set_page_config(
    page_title="SmartCampusAI",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment configurations
load_dotenv()

# Initialize database JSON files if they do not exist
from helpers.json_handler import init_db
init_db()

# Import page modules and layout components
from modules.utils import load_css
from modules.authentication import show_auth
from modules.dashboard import show_dashboard
from modules.students import show_students
from modules.attendance import show_attendance
from modules.announcements import show_announcements
from modules.placements import show_placements
from modules.events import show_events
from modules.ai_chat import show_ai_chat
from modules.analytics import show_analytics
from modules.settings import show_settings

from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.footer import render_footer

def main():
    # Load stylesheet rules globally
    load_css()
    
    # Initialize authentication session variables
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
        
    # Router: Show login/registration if not authenticated
    if not st.session_state.authenticated or not st.session_state.user:
        show_auth()
    else:
        # User is authenticated: Render layout headers and build dynamic routes
        render_navbar()
        render_sidebar()
        
        user_role = st.session_state.user.get("role", "Student")
        
        # Build pages list based on roles dynamically
        pages = [
            st.Page(show_dashboard, title="Dashboard", icon=":material/dashboard:")
        ]
        
        # Admin / Faculty access features
        if user_role in ["Admin", "Faculty"]:
            pages.append(st.Page(show_students, title="Student Directory", icon=":material/group:"))
            pages.append(st.Page(show_attendance, title="Attendance Marker", icon=":material/checklist:"))
        else:
            # Student view only features
            pages.append(st.Page(show_attendance, title="My Attendance", icon=":material/checklist:"))
            
        # Common feature pages
        pages.extend([
            st.Page(show_placements, title="Placement Portal", icon=":material/work:"),
            st.Page(show_announcements, title="Announcements", icon=":material/campaign:"),
            st.Page(show_events, title="Events Timeline", icon=":material/calendar_today:"),
            st.Page(show_ai_chat, title="Campus AI Assistant", icon=":material/chat:"),
            st.Page(show_analytics, title="Campus Analytics", icon=":material/analytics:"),
            st.Page(show_settings, title="System Settings", icon=":material/settings:")
        ])
        
        # Run navigation router
        pg = st.navigation(pages, position="sidebar")
        
        # Execute active page logic
        pg.run()
        
        # Render system footer
        render_footer()

if __name__ == "__main__":
    main()
