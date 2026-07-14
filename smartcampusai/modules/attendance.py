import streamlit as st
import pandas as pd
from datetime import datetime
from helpers.json_handler import load_json, save_json
from modules.utils import load_css, styled_header

def show_attendance():
    """Renders the attendance logging and percentage calculation screen."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    role = user.get("role", "Student")
    is_faculty_or_admin = role in ["Faculty", "Admin"]
    
    styled_header("Attendance Hub", "Record daily attendance logs and analyze statistics", "checklist")
    
    # Define tabs based on role
    tabs_list = ["My Attendance Report"]
    if is_faculty_or_admin:
        tabs_list.insert(0, "Mark Attendance")
        
    tabs = st.tabs(tabs_list)
    
    # Tab indexing helpers
    mark_tab_idx = 0 if is_faculty_or_admin else None
    report_tab_idx = 1 if is_faculty_or_admin else 0
    
    # ------------------ Tab: Mark Attendance ------------------
    if is_faculty_or_admin:
        with tabs[mark_tab_idx]:
            st.markdown("### Record Daily Attendance")
            
            # Select filters
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                branch = st.selectbox("Branch", ["CSE", "ECE", "Civil", "Mechanical", "EE", "AIE", "BioTech"], key="att_branch")
            with col2:
                year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"], key="att_year")
            with col3:
                section = st.selectbox("Section", ["A", "B", "C", "D"], key="att_section")
            with col4:
                att_date = st.date_input("Date", datetime.now(), key="att_date")
                
            # Convert date to string format YYYY-MM-DD
            date_str = att_date.strftime("%Y-%m-%d")
            
            # Fetch matching students
            all_students = load_json("students.json")
            matching_students = [
                s for s in all_students 
                if s.get("branch") == branch and s.get("year") == year and s.get("section") == section
            ]
            
            if not matching_students:
                st.info(f"No students found in: {branch} - {year} - Section {section}", icon=":material/info:")
            else:
                st.write(f"Found {len(matching_students)} students. Set attendance status below:")
                
                # Fetch existing logs for this date to preselect status if already marked
                existing_logs = load_json("attendance.json")
                date_logs = {log["student_id"]: log["status"] for log in existing_logs if log["date"] == date_str}
                
                # Create form for marking attendance
                with st.form("mark_attendance_form"):
                    student_statuses = {}
                    
                    # Columns header
                    c_header1, c_header2, c_header3 = st.columns([1, 2, 2])
                    with c_header1:
                        st.markdown("**Student ID**")
                    with c_header2:
                        st.markdown("**Full Name**")
                    with c_header3:
                        st.markdown("**Status**")
                        
                    st.markdown("<hr style='margin: 4px 0;' />", unsafe_allow_html=True)
                    
                    # Render student rows
                    for student in matching_students:
                        col_id, col_name, col_status = st.columns([1, 2, 2])
                        sid = student["student_id"]
                        sname = student["name"]
                        
                        # Pre-select status: existing in logs, or default to "Present"
                        current_status = date_logs.get(sid, "Present")
                        status_options = ["Present", "Absent", "Late"]
                        sel_idx = status_options.index(current_status)
                        
                        with col_id:
                            st.write(sid)
                        with col_name:
                            st.write(sname)
                        with col_status:
                            # Unique key for widget
                            choice = st.segmented_control(
                                label=f"Status for {sid}",
                                options=status_options,
                                default=current_status,
                                key=f"status_select_{sid}",
                                label_visibility="collapsed"
                            )
                            student_statuses[sid] = choice if choice else "Present"
                            
                    st.space("medium")
                    save_submit = st.form_submit_button("Save Attendance Records", icon=":material/save:")
                    
                    if save_submit:
                        # Update database records
                        # Remove existing logs for these students on this date first
                        filtered_logs = [
                            log for log in existing_logs 
                            if not (log["date"] == date_str and log["student_id"] in student_statuses)
                        ]
                        
                        # Append new marked logs
                        for student in matching_students:
                            sid = student["student_id"]
                            filtered_logs.append({
                                "date": date_str,
                                "student_id": sid,
                                "name": student["name"],
                                "branch": branch,
                                "year": year,
                                "section": section,
                                "status": student_statuses[sid]
                            })
                            
                        if save_json("attendance.json", filtered_logs):
                            st.success(f"Attendance recorded successfully for {date_str}!")
                            st.toast("Attendance updated!", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            st.error("Failed to save attendance logs.")
                            
    # ------------------ Tab: Report View ------------------
    with tabs[report_tab_idx]:
        st.markdown("### Attendance Metrics Analytics")
        attendance_logs = load_json("attendance.json")
        
        if not attendance_logs:
            st.info("No attendance database records found.", icon=":material/database:")
        else:
            df = pd.DataFrame(attendance_logs)
            
            # Determine which view to render: Student view vs Faculty/Admin view
            if role == "Student":
                student_id = user.get("username").upper() # assuming student username corresponds to student ID or name
                # Let's map student user by checking name matches
                student_obj = next((s for s in load_json("students.json") if s["name"].lower() == user["name"].lower()), None)
                
                if not student_obj:
                    st.warning(f"Could not map user account '{user['name']}' to any registered Student ID.")
                else:
                    sid = student_obj["student_id"]
                    stu_df = df[df["student_id"] == sid]
                    
                    if stu_df.empty:
                        st.info(f"No attendance logs recorded yet for {user['name']} ({sid}).")
                    else:
                        render_student_report(stu_df, student_obj)
            else:
                # Faculty / Admin view: can see overall report or select a student to see report
                st.write("Overview of all students' attendance statistics:")
                
                # Metrics grouping
                stats = []
                for sid, group in df.groupby("student_id"):
                    total = len(group)
                    present_late = len(group[group["status"].isin(["Present", "Late"])])
                    rate = (present_late / total) * 100 if total > 0 else 0
                    
                    student_name = group.iloc[0]["name"]
                    branch_val = group.iloc[0]["branch"]
                    year_val = group.iloc[0]["year"]
                    
                    stats.append({
                        "Student ID": sid,
                        "Name": student_name,
                        "Branch": branch_val,
                        "Year": year_val,
                        "Total Lectures": total,
                        "Attendance %": f"{rate:.1f}%",
                        "Raw Rate": rate
                    })
                    
                stats_df = pd.DataFrame(stats)
                
                # Filters for statistics
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    br_opt = ["All"] + list(stats_df["Branch"].unique())
                    sel_br = st.selectbox("Department Filter", br_opt, key="stat_br_filter")
                with col_f2:
                    yr_opt = ["All"] + list(stats_df["Year"].unique())
                    sel_yr = st.selectbox("Year Filter", yr_opt, key="stat_yr_filter")
                    
                filtered_stats = stats_df.copy()
                if sel_br != "All":
                    filtered_stats = filtered_stats[filtered_stats["Branch"] == sel_br]
                if sel_yr != "All":
                    filtered_stats = filtered_stats[filtered_stats["Year"] == sel_yr]
                    
                # Format color highlight for low attendance
                def color_low_attendance(val):
                    try:
                        num = float(val.replace("%", ""))
                        if num < 75.0:
                            return "color: #f43f5e; font-weight: bold;"
                        return "color: #10b981;"
                    except Exception:
                        return ""
                
                st.dataframe(
                    filtered_stats[["Student ID", "Name", "Branch", "Year", "Total Lectures", "Attendance %"]],
                    width="stretch",
                    hide_index=True
                )
                
                # Detailed view of a single student's logs
                st.markdown("---")
                st.markdown("#### View Detailed Student Log")
                all_students_db = load_json("students.json")
                student_options = {f"{s['name']} ({s['student_id']})": s for s in all_students_db}
                
                if student_options:
                    sel_stu_label = st.selectbox("Select student to view log details", list(student_options.keys()))
                    sel_student_obj = student_options[sel_stu_label]
                    sel_sid = sel_student_obj["student_id"]
                    
                    sel_stu_df = df[df["student_id"] == sel_sid]
                    if sel_stu_df.empty:
                        st.info(f"No logs recorded yet for {sel_student_obj['name']}.")
                    else:
                        render_student_report(sel_stu_df, sel_student_obj)

def render_student_report(stu_df: pd.DataFrame, student_obj: dict):
    """Utility helper to render detailed attendance summary for a single student."""
    total = len(stu_df)
    present = len(stu_df[stu_df["status"] == "Present"])
    absent = len(stu_df[stu_df["status"] == "Absent"])
    late = len(stu_df[stu_df["status"] == "Late"])
    
    rate = ((present + late) / total) * 100 if total > 0 else 0
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.metric("Total Lectures", str(total), border=True)
    with col_c2:
        st.metric("Present Count", str(present), border=True)
    with col_c3:
        st.metric("Absent Count", str(absent), border=True)
    with col_c4:
        st.metric("Attendance %", f"{rate:.1f}%", border=True, delta="Passes Criteria" if rate >= 75 else "Low Attendance", delta_color="normal" if rate >= 75 else "inverse")
        
    st.markdown("#### Logs Timeline")
    # Sort logs by date descending
    stu_df_sorted = stu_df.sort_values(by="date", ascending=False)
    
    # Rename display columns
    display_df = stu_df_sorted[["date", "status"]].rename(columns={"date": "Date", "status": "Attendance Status"})
    st.dataframe(display_df, width="stretch", hide_index=True)
