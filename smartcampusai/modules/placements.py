import streamlit as st
import pandas as pd
from helpers.json_handler import load_json, save_json
from modules.utils import load_css, styled_header

def show_placements():
    """Renders the placement dashboard including drives timeline, job applications, and selection lists."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    role = user.get("role", "Student")
    is_write_allowed = role in ["Admin", "Faculty"]
    
    styled_header("Placement Cell", "Organize recruitment drives and monitor selections", "work")
    
    # Map student object if role is Student
    student_obj = None
    if role == "Student":
        all_students = load_json("students.json")
        student_obj = next((s for s in all_students if s["name"].lower() == user["name"].lower()), None)
        
    tabs_list = ["Hiring Drives Portal"]
    if is_write_allowed:
        tabs_list.extend(["Schedule Drive", "Recruitment Selection"])
        
    tabs = st.tabs(tabs_list)
    
    # ------------------ Tab 1: Portal View ------------------
    with tabs[0]:
        st.markdown("### Active Recruitment Drives")
        drives = load_json("placements.json")
        
        if not drives:
            st.info("No active corporate drives listed currently.", icon=":material/info:")
        else:
            for idx, drive in enumerate(drives):
                with st.container(border=True):
                    col_det, col_act = st.columns([5, 2])
                    
                    with col_det:
                        st.markdown(f"#### {drive.get('company_name')}")
                        st.markdown(f"💼 **Annual CTC Package:** {drive.get('package')}")
                        st.markdown(f"📅 **Drive Date:** {drive.get('drive_date')}")
                        
                        branches = drive.get("eligible_branches", [])
                        branches_str = ", ".join(branches) if isinstance(branches, list) else branches
                        st.markdown(f"🎓 **Eligible Streams:** `{branches_str}`")
                        
                    with col_act:
                        applied = drive.get("applied_students", [])
                        selected = drive.get("selected_students", [])
                        
                        st.metric("Applicants", str(len(applied)), border=True)
                        
                        # Student Action: Apply
                        if role == "Student":
                            if not student_obj:
                                st.warning("Register a student profile with your account name to apply.")
                            else:
                                sid = student_obj["student_id"]
                                is_eligible = student_obj["branch"] in branches or "All" in branches
                                
                                if not is_eligible:
                                    st.error("Branch not eligible.")
                                elif sid in selected:
                                    st.success("🎉 You are Selected!", icon=":material/celebration:")
                                elif sid in applied:
                                    st.info("Applied ✔")
                                else:
                                    if st.button("Apply Now", key=f"apply_{idx}", type="primary"):
                                        applied.append(sid)
                                        # Update DB
                                        drives[idx]["applied_students"] = applied
                                        if save_json("placements.json", drives):
                                            st.toast("Application sent successfully!", icon=":material/check_circle:")
                                            st.rerun()
                        # Admin/Faculty view statistics
                        else:
                            st.markdown("**Placement Status:**")
                            if selected:
                                st.success(f"{len(selected)} Hired ✅")
                            else:
                                st.info("Selections Pending ⏳")
                                
                    # Selection results board
                    if selected:
                        st.markdown("---")
                        st.markdown(f"🏆 **Selected Students from this drive:**")
                        stu_list = load_json("students.json")
                        selected_names = [s["name"] for s in stu_list if s["student_id"] in selected]
                        if selected_names:
                            st.write(", ".join(selected_names))
                            
    # ------------------ Tab 2: Schedule Drive (Write allowed) ------------------
    if is_write_allowed:
        with tabs[1]:
            st.markdown("### Create New Recruitment Drive")
            
            with st.form("schedule_drive_form", clear_on_submit=True):
                company_name = st.text_input("Company Name", placeholder="e.g. Google Cloud")
                package = st.text_input("CTC Package Offered", placeholder="e.g. 15 LPA")
                
                # Checkbox selection for branches
                st.write("Eligible Departments:")
                all_branches = ["CSE", "ECE", "Civil", "Mechanical", "EE", "AIE", "BioTech"]
                selected_br = []
                col_br1, col_br2, col_br3 = st.columns(3)
                
                for b_idx, br in enumerate(all_branches):
                    # Distribute checkboxes across columns
                    c_col = col_br1 if b_idx % 3 == 0 else (col_br2 if b_idx % 3 == 1 else col_br3)
                    with c_col:
                        if st.checkbox(br, key=f"br_chk_{br}"):
                            selected_br.append(br)
                            
                drive_date = st.date_input("Drive Event Date")
                
                submit_drive = st.form_submit_button("Publish Recruitment Drive", icon=":material/publish:")
                
                if submit_drive:
                    if not company_name.strip() or not package.strip():
                        st.error("Company Name and Package are required.")
                    elif not selected_br:
                        st.error("Select at least one eligible department.")
                    else:
                        new_drive = {
                            "company_name": company_name.strip(),
                            "package": package.strip(),
                            "eligible_branches": selected_br,
                            "drive_date": drive_date.strftime("%Y-%m-%d"),
                            "applied_students": [],
                            "selected_students": []
                        }
                        
                        d_db = load_json("placements.json")
                        d_db.append(new_drive)
                        
                        if save_json("placements.json", d_db):
                            st.success(f"Recruitment drive for {company_name} published successfully!")
                            st.toast("Drive published!", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            st.error("Failed to save drive details.")
                            
        # ------------------ Tab 3: Recruitment Selection (Write allowed) ------------------
        with tabs[2]:
            st.markdown("### Select Hired Candidates")
            drives = load_json("placements.json")
            
            if not drives:
                st.info("No corporate drives created to manage selections.")
            else:
                drive_options = {f"{d['company_name']} ({d['drive_date']})": idx for idx, d in enumerate(drives)}
                sel_drive_label = st.selectbox("Select Placement Drive", list(drive_options.keys()))
                sel_idx = drive_options[sel_drive_label]
                
                selected_drive = drives[sel_idx]
                applicants = selected_drive.get("applied_students", [])
                
                if not applicants:
                    st.info(f"No students have applied to the {selected_drive['company_name']} recruitment drive yet.")
                else:
                    st.write(f"Following students applied. Select candidates who cleared the evaluation process:")
                    
                    student_list_db = load_json("students.json")
                    applicants_details = [s for s in student_list_db if s["student_id"] in applicants]
                    
                    with st.form("selection_management_form"):
                        selections = []
                        prev_selected = selected_drive.get("selected_students", [])
                        
                        for student in applicants_details:
                            sid = student["student_id"]
                            sname = student["name"]
                            sbranch = student["branch"]
                            
                            is_checked = sid in prev_selected
                            
                            col_chk, col_det = st.columns([1, 6])
                            with col_chk:
                                if st.checkbox(f"Select {sname}", value=is_checked, label_visibility="collapsed", key=f"sel_chk_{sid}"):
                                    selections.append(sid)
                            with col_det:
                                st.write(f"**{sname}** ({sid}) | Branch: {sbranch} | Skills: {student.get('skills', 'N/A')}")
                                
                        st.space("small")
                        save_selection = st.form_submit_button("Confirm Selection List", icon=":material/check_circle:")
                        
                        if save_selection:
                            drives[sel_idx]["selected_students"] = selections
                            
                            if save_json("placements.json", drives):
                                st.success("Candidate selection status updated successfully!")
                                st.toast("Selections saved!", icon=":material/check_circle:")
                                st.rerun()
                            else:
                                st.error("Failed to update selections in database.")
