import streamlit as st
import pandas as pd
from helpers.json_handler import load_json, save_json, append_json, delete_json
from modules.utils import load_css, check_access, styled_header

def show_students():
    """Renders the student management dashboard (CRUD interface)."""
    load_css()
    
    # Check access for viewing
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    role = user.get("role", "Student")
    is_write_allowed = role in ["Admin", "Faculty"]
    
    styled_header("Student Management", "View and coordinate campus student profiles", "group")
    
    # Create tabs
    tabs_list = ["Search & View Profiles"]
    if is_write_allowed:
        tabs_list.extend(["Add Student", "Update Student", "Delete Student"])
        
    tabs = st.tabs(tabs_list)
    
    # ------------------ Tab 1: Search & View ------------------
    with tabs[0]:
        st.markdown("### Campus Student Directory")
        students = load_json("students.json")
        
        if not students:
            st.info("No student profiles registered in the system database.", icon=":material/database:")
        else:
            df = pd.DataFrame(students)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                search_query = st.text_input("Search student", placeholder="Type Name or Student ID...", key="student_search")
            with col2:
                branches = ["All"] + sorted(list(df["branch"].unique()))
                filter_branch = st.selectbox("Filter by branch", branches, key="student_filter_branch")
            with col3:
                years = ["All"] + sorted(list(df["year"].unique()))
                filter_year = st.selectbox("Filter by year", years, key="student_filter_year")
                
            # Filter Logic
            filtered_df = df.copy()
            if search_query:
                q = search_query.strip().lower()
                filtered_df = filtered_df[
                    filtered_df["name"].str.lower().str.contains(q) | 
                    filtered_df["student_id"].str.lower().str.contains(q)
                ]
                
            if filter_branch != "All":
                filtered_df = filtered_df[filtered_df["branch"] == filter_branch]
                
            if filter_year != "All":
                filtered_df = filtered_df[filtered_df["year"] == filter_year]
                
            st.markdown(f"**Found {len(filtered_df)} student records:**")
            if not filtered_df.empty:
                # Format dataframe display columns
                display_cols = {
                    "student_id": "Student ID",
                    "name": "Full Name",
                    "branch": "Branch",
                    "year": "Year",
                    "section": "Section",
                    "phone": "Phone",
                    "email": "Email",
                    "skills": "Key Skills"
                }
                st.dataframe(
                    filtered_df[list(display_cols.keys())].rename(columns=display_cols),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.warning("No students match your query criteria.")
                
    # ------------------ Tab 2: Add Student ------------------
    if is_write_allowed:
        with tabs[1]:
            st.markdown("### Add New Student Profile")
            with st.form("add_student_form", clear_on_submit=True):
                stu_id = st.text_input("Student ID (Unique)", placeholder="e.g. STU104")
                name = st.text_input("Full Name", placeholder="e.g. Sarah Connor")
                
                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    branch = st.selectbox("Branch", ["CSE", "ECE", "Civil", "Mechanical", "EE", "AIE", "BioTech"])
                with col_b2:
                    year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
                with col_b3:
                    section = st.selectbox("Section", ["A", "B", "C", "D"])
                    
                phone = st.text_input("Phone Number", placeholder="10-digit number")
                email = st.text_input("Email Address", placeholder="name@smartcampus.edu")
                address = st.text_area("Home Address", placeholder="Street, City, State, ZIP")
                skills = st.text_input("Skills (Comma separated)", placeholder="e.g. Python, SQL, Communication")
                
                submit_add = st.form_submit_button("Save Student Profile")
                
                if submit_add:
                    if not all([stu_id, name, phone, email]):
                        st.error("Student ID, Name, Phone and Email are mandatory fields.")
                    elif not phone.isdigit() or len(phone) != 10:
                        st.error("Phone number must be exactly 10 digits.")
                    else:
                        # Check duplicate student ID
                        students = load_json("students.json")
                        if any(s["student_id"].lower() == stu_id.strip().lower() for s in students):
                            st.error(f"Student ID '{stu_id}' is already registered.")
                        else:
                            new_student = {
                                "student_id": stu_id.strip().upper(),
                                "name": name.strip(),
                                "branch": branch,
                                "year": year,
                                "section": section,
                                "phone": phone.strip(),
                                "email": email.strip(),
                                "address": address.strip(),
                                "skills": skills.strip()
                            }
                            if append_json("students.json", new_student):
                                st.success(f"Successfully saved profile for {name} ({stu_id.upper()}).")
                                st.toast("Student added!", icon=":material/check_circle:")
                            else:
                                st.error("Database save failed.")
                                
        # ------------------ Tab 3: Update Student ------------------
        with tabs[2]:
            st.markdown("### Modify Student Profile")
            students = load_json("students.json")
            
            if not students:
                st.info("No students registered to update.")
            else:
                student_options = {f"{s['name']} ({s['student_id']})": s for s in students}
                selected_label = st.selectbox("Select Student to Update", list(student_options.keys()))
                
                student_data = student_options[selected_label]
                
                with st.form("update_student_form"):
                    st.write(f"Editing Student ID: **{student_data['student_id']}**")
                    
                    up_name = st.text_input("Full Name", value=student_data.get("name", ""))
                    
                    col_ub1, col_ub2, col_ub3 = st.columns(3)
                    with col_ub1:
                        # Find index of branch in standard options to preselect
                        branches_list = ["CSE", "ECE", "Civil", "Mechanical", "EE", "AIE", "BioTech"]
                        branch_val = student_data.get("branch", "CSE")
                        b_idx = branches_list.index(branch_val) if branch_val in branches_list else 0
                        up_branch = st.selectbox("Branch", branches_list, index=b_idx)
                    with col_ub2:
                        years_list = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                        year_val = student_data.get("year", "1st Year")
                        y_idx = years_list.index(year_val) if year_val in years_list else 0
                        up_year = st.selectbox("Year", years_list, index=y_idx)
                    with col_ub3:
                        sections_list = ["A", "B", "C", "D"]
                        sec_val = student_data.get("section", "A")
                        s_idx = sections_list.index(sec_val) if sec_val in sections_list else 0
                        up_section = st.selectbox("Section", sections_list, index=s_idx)
                        
                    up_phone = st.text_input("Phone Number", value=student_data.get("phone", ""))
                    up_email = st.text_input("Email Address", value=student_data.get("email", ""))
                    up_address = st.text_area("Home Address", value=student_data.get("address", ""))
                    up_skills = st.text_input("Skills", value=student_data.get("skills", ""))
                    
                    submit_update = st.form_submit_button("Update Student Profile")
                    
                    if submit_update:
                        if not all([up_name, up_phone, up_email]):
                            st.error("Name, Phone, and Email cannot be empty.")
                        elif not up_phone.isdigit() or len(up_phone) != 10:
                            st.error("Phone number must be exactly 10 digits.")
                        else:
                            updated_fields = {
                                "name": up_name.strip(),
                                "branch": up_branch,
                                "year": up_year,
                                "section": up_section,
                                "phone": up_phone.strip(),
                                "email": up_email.strip(),
                                "address": up_address.strip(),
                                "skills": up_skills.strip()
                            }
                            
                            # Update JSON handler
                            from helpers.json_handler import update_json
                            if update_json("students.json", "student_id", student_data["student_id"], updated_fields):
                                st.success("Student profile updated successfully!")
                                st.toast("Profile updated!", icon=":material/check_circle:")
                                st.rerun()
                            else:
                                st.error("Failed to update student profile.")
                                
        # ------------------ Tab 4: Delete Student ------------------
        with tabs[3]:
            st.markdown("### Delete Student Record")
            students = load_json("students.json")
            
            if not students:
                st.info("No students registered to delete.")
            else:
                student_options = {f"{s['name']} ({s['student_id']})": s for s in students}
                selected_label = st.selectbox("Select Student to Delete", list(student_options.keys()), key="student_delete_select")
                student_data = student_options[selected_label]
                
                st.warning(f"Are you absolutely sure you want to delete the student profile of {student_data['name']} ({student_data['student_id']})?")
                st.write("This action cannot be undone and will delete the record from the database.")
                
                if st.button("Delete Record Permanently", key="student_delete_btn", type="primary"):
                    if delete_json("students.json", "student_id", student_data["student_id"]):
                        st.success(f"Record for {student_data['name']} deleted successfully!")
                        st.toast("Record deleted", icon=":material/delete:")
                        st.rerun()
                    else:
                        st.error("Deletion failed.")
