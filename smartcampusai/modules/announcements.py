import streamlit as st
import uuid
from datetime import datetime
from helpers.json_handler import load_json, append_json, delete_json
from modules.utils import load_css, styled_header

def show_announcements():
    """Renders the announcements creation (Admin/Faculty) and viewing (All) panels."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    role = user.get("role", "Student")
    is_write_allowed = role in ["Admin", "Faculty"]
    
    styled_header("Campus Announcements", "View official circulars and campus notices", "campaign")
    
    tabs_list = ["Bulletin Board"]
    if is_write_allowed:
        tabs_list.append("Post Announcement")
        
    tabs = st.tabs(tabs_list)
    
    # ------------------ Tab 1: View Announcements ------------------
    with tabs[0]:
        announcements = load_json("announcements.json")
        
        if not announcements:
            st.info("No notices currently posted on the bulletin board.", icon=":material/campaign:")
        else:
            # Sort by date descending
            sorted_ann = sorted(announcements, key=lambda x: x.get("date", ""), reverse=True)
            
            for ann in sorted_ann:
                with st.container(border=True):
                    col_t, col_btn = st.columns([6, 1])
                    with col_t:
                        st.markdown(f"#### {ann.get('title')}")
                        st.caption(f":material/person: Posted by **{ann.get('author')}** on **{ann.get('date')}**")
                    with col_btn:
                        # Faculty/Admin can delete notices
                        if is_write_allowed:
                            ann_id = ann.get("id")
                            if st.button("Delete", key=f"del_ann_{ann_id}", icon=":material/delete:", type="secondary"):
                                if delete_json("announcements.json", "id", ann_id):
                                    st.toast("Notice deleted!", icon=":material/delete:")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete announcement.")
                    
                    st.write(ann.get("content"))
                    
    # ------------------ Tab 2: Post Announcement ------------------
    if is_write_allowed:
        with tabs[1]:
            st.markdown("### Draft New Announcement")
            
            with st.form("new_announcement_form", clear_on_submit=True):
                title = st.text_input("Announcement Title", placeholder="e.g. Semester Exams Timetable")
                content = st.text_area("Notice Content", placeholder="Write announcement details here...")
                
                submit_ann = st.form_submit_button("Publish Announcement", icon=":material/publish:")
                
                if submit_ann:
                    if not title.strip() or not content.strip():
                        st.error("Title and Content are required fields.")
                    else:
                        new_ann = {
                            "id": str(uuid.uuid4())[:8],
                            "title": title.strip(),
                            "content": content.strip(),
                            "author": user.get("name", "Faculty Member"),
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        if append_json("announcements.json", new_ann):
                            st.success("Announcement published successfully!")
                            st.toast("Published!", icon=":material/campaign:")
                            st.rerun()
                        else:
                            st.error("Save operation failed.")
