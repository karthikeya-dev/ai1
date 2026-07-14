import streamlit as st
import pandas as pd
from helpers.json_handler import load_json
from components.cards import render_kpi_card
from components.charts import render_pie_chart, render_line_chart, render_bar_chart
from modules.utils import load_css, styled_header

def show_dashboard():
    """Renders the central KPI metrics panel, charts, notices, and upcoming events."""
    load_css()
    
    # Check session
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required! Please log in first.")
        return
        
    user = st.session_state.user
    styled_header(f"Welcome, {user.get('name', 'User')}", "Campus Operational Dashboard Overview", "dashboard")
    
    # 1. Fetch data for calculations
    students = load_json("students.json")
    users = load_json("users.json")
    placements = load_json("placements.json")
    attendance = load_json("attendance.json")
    events = load_json("events.json")
    announcements = load_json("announcements.json")
    
    total_students = len(students)
    total_faculty = len([u for u in users if u.get("role") == "Faculty"])
    total_placements = len(placements)
    
    # Calculate Attendance Rate
    if attendance:
        p_or_l = len([a for a in attendance if a.get("status") in ["Present", "Late"]])
        attendance_rate = (p_or_l / len(attendance)) * 100
        attendance_str = f"{attendance_rate:.1f}%"
    else:
        attendance_str = "0.0%"
        
    # 2. Render KPI cards in a row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Students", str(total_students), "+1", "group", "#00f0ff")
    with col2:
        render_kpi_card("Total Faculty", str(total_faculty), "0", "badge_doctor", "#8b5cf6")
    with col3:
        render_kpi_card("Active Placements", str(total_placements), "+1", "work", "#10b981")
    with col4:
        render_kpi_card("Avg Attendance", attendance_str, "+1.2%", "check_circle", "#f59e0b")
        
    st.space("medium")
    
    # 3. Main Dashboard Charts
    st.subheader("Key Operations Analytics", anchor=False)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        with st.container(border=True):
            if students:
                df_stu = pd.DataFrame(students)
                df_counts = df_stu["branch"].value_counts().reset_index()
                df_counts.columns = ["Branch", "Count"]
                fig1 = render_pie_chart(df_counts, "Branch", "Count", "Students by Branch")
                st.plotly_chart(fig1, width="stretch")
            else:
                st.info("No student data available to chart.", icon=":material/info:")
                
    with col_chart2:
        with st.container(border=True):
            if attendance:
                df_att = pd.DataFrame(attendance)
                # Count status occurrences
                df_counts_att = df_att["status"].value_counts().reset_index()
                df_counts_att.columns = ["Status", "Count"]
                fig2 = render_bar_chart(df_counts_att, "Status", "Count", "Attendance Status Distribution")
                st.plotly_chart(fig2, width="stretch")
            else:
                st.info("No attendance data available to chart.", icon=":material/info:")
                
    st.space("medium")
    
    # 4. Bulletins and Updates row
    col_bulletin1, col_bulletin2 = st.columns(2)
    
    with col_bulletin1:
        st.subheader("Announcements Board", anchor=False)
        if announcements:
            # Sort by date descending (assuming format YYYY-MM-DD)
            sorted_ann = sorted(announcements, key=lambda x: x.get("date", ""), reverse=True)[:3]
            for ann in sorted_ann:
                with st.container(border=True):
                    st.markdown(f"**{ann.get('title')}**")
                    st.caption(f"Posted by {ann.get('author')} on {ann.get('date')}")
                    st.write(ann.get('content'))
        else:
            st.info("No announcements posted yet.", icon=":material/campaign:")
            
    with col_bulletin2:
        st.subheader("Upcoming Events", anchor=False)
        if events:
            sorted_evt = sorted(events, key=lambda x: x.get("date", ""))[:3]
            for evt in sorted_evt:
                with st.container(border=True):
                    st.markdown(f"**{evt.get('title')}**")
                    st.caption(f":material/calendar_today: {evt.get('date')} | :material/schedule: {evt.get('time')} | :material/location_on: {evt.get('venue')}")
                    st.write(evt.get('description'))
        else:
            st.info("No events scheduled.", icon=":material/event:")
