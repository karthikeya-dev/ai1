import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
from helpers.json_handler import load_json, append_json, save_json, delete_json
from modules.utils import load_css, styled_header

def show_events():
    """Renders the event scheduler (create, edit, delete tabs)."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    role = user.get("role", "Student")
    is_write_allowed = role in ["Admin", "Faculty"]
    
    styled_header("Campus Events Scheduler", "Coordinate, schedule, and view campus events", "calendar_today")
    
    tabs_list = ["Calendar Agenda"]
    if is_write_allowed:
        tabs_list.extend(["Schedule Event", "Manage Events"])
        
    tabs = st.tabs(tabs_list)
    
    # ------------------ Tab 1: Agenda ------------------
    with tabs[0]:
        st.markdown("### Scheduled Events Agenda")
        events = load_json("events.json")
        
        if not events:
            st.info("No campus events scheduled on the calendar currently.", icon=":material/event:")
        else:
            # Sort by date
            sorted_events = sorted(events, key=lambda x: x.get("date", ""))
            
            for evt in sorted_events:
                with st.container(border=True):
                    st.markdown(f"#### {evt.get('title')}")
                    
                    # Columns details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f":material/calendar_today: **Date:** {evt.get('date')}")
                    with col2:
                        st.markdown(f":material/schedule: **Time:** {evt.get('time')}")
                    with col3:
                        st.markdown(f":material/location_on: **Venue:** {evt.get('venue')}")
                        
                    st.space("small")
                    st.write(evt.get("description"))
                    
    # ------------------ Tab 2: Schedule Event ------------------
    if is_write_allowed:
        with tabs[1]:
            st.markdown("### Create New Event Listing")
            
            with st.form("new_event_form", clear_on_submit=True):
                title = st.text_input("Event Title", placeholder="e.g. Annual Technical Fest")
                
                col_d, col_t = st.columns(2)
                with col_d:
                    evt_date = st.date_input("Event Date")
                with col_t:
                    evt_time = st.text_input("Event Time", placeholder="e.g. 10:00 AM")
                    
                venue = st.text_input("Venue / Location", placeholder="e.g. Seminar Hall A")
                description = st.text_area("Event Description", placeholder="Outline details of the event schedule...")
                
                submit_evt = st.form_submit_button("Publish Event", icon=":material/publish:")
                
                if submit_evt:
                    if not title.strip() or not venue.strip() or not description.strip():
                        st.error("Title, Venue, and Description are required.")
                    else:
                        new_evt = {
                            "id": str(uuid.uuid4())[:8],
                            "title": title.strip(),
                            "date": evt_date.strftime("%Y-%m-%d"),
                            "time": evt_time.strip(),
                            "venue": venue.strip(),
                            "description": description.strip()
                        }
                        
                        if append_json("events.json", new_evt):
                            st.success("Event scheduled and published successfully!")
                            st.toast("Event published!", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            st.error("Failed to save event.")
                            
        # ------------------ Tab 3: Manage / Delete Events ------------------
        with tabs[2]:
            st.markdown("### Update or Cancel Events")
            events = load_json("events.json")
            
            if not events:
                st.info("No events registered to manage.")
            else:
                event_options = {f"{e['title']} ({e['date']})": idx for idx, e in enumerate(events)}
                sel_evt_label = st.selectbox("Select Event", list(event_options.keys()))
                sel_idx = event_options[sel_evt_label]
                
                selected_event = events[sel_idx]
                
                with st.form("edit_event_form"):
                    st.write(f"Modifying Event ID: **{selected_event['id']}**")
                    
                    e_title = st.text_input("Event Title", value=selected_event.get("title", ""))
                    
                    col_ed, col_et = st.columns(2)
                    with col_ed:
                        prev_date = datetime.strptime(selected_event.get("date"), "%Y-%m-%d")
                        e_date = st.date_input("Event Date", value=prev_date)
                    with col_et:
                        e_time = st.text_input("Event Time", value=selected_event.get("time", ""))
                        
                    e_venue = st.text_input("Venue / Location", value=selected_event.get("venue", ""))
                    e_desc = st.text_area("Event Description", value=selected_event.get("description", ""))
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        save_edits = st.form_submit_button("Update Event Details", icon=":material/save:")
                    with col_btn2:
                        cancel_evt = st.form_submit_button("Cancel / Delete Event", icon=":material/delete:", type="primary")
                        
                    if save_edits:
                        if not e_title.strip() or not e_venue.strip():
                            st.error("Title and Venue cannot be empty.")
                        else:
                            updated_evt = {
                                "title": e_title.strip(),
                                "date": e_date.strftime("%Y-%m-%d"),
                                "time": e_time.strip(),
                                "venue": e_venue.strip(),
                                "description": e_desc.strip()
                            }
                            
                            from helpers.json_handler import update_json
                            if update_json("events.json", "id", selected_event["id"], updated_evt):
                                st.success("Event details updated successfully!")
                                st.toast("Event updated!", icon=":material/check_circle:")
                                st.rerun()
                            else:
                                st.error("Failed to update event.")
                                
                    if cancel_evt:
                        if delete_json("events.json", "id", selected_event["id"]):
                            st.success("Event cancelled and removed.")
                            st.toast("Event deleted", icon=":material/delete:")
                            st.rerun()
                        else:
                            st.error("Failed to delete event.")
