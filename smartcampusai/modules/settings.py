import streamlit as st
from helpers.json_handler import load_json, save_json, init_db
from helpers.security import hash_password, verify_password
from helpers.validators import validate_password_strength
from modules.utils import load_css, styled_header

def show_settings():
    """Renders user profile settings, secure password changer, and system database diagnostics."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    username = user.get("username")
    
    styled_header("System Settings", "Configure account security, profile, and check database states", "settings")
    
    col_p, col_pwd = st.columns([1, 1])
    
    # ------------------ Profile Details Card ------------------
    with col_p:
        with st.container(border=True):
            st.markdown("### Profile Summary")
            st.markdown(f"**👤 Full Name:** {user.get('name')}")
            st.markdown(f"**📧 Email:** {user.get('email')}")
            st.markdown(f"**📱 Mobile Phone:** {user.get('mobile')}")
            st.markdown(f"**🆔 Username:** `{username}`")
            st.markdown(f"**🛡 User Authorization Role:** `{user.get('role')}`")
            st.caption("Profile edits are locked by academic administration. Contact registrations to update details.")
            
    # ------------------ Password Updater Form ------------------
    with col_pwd:
        with st.container(border=True):
            st.markdown("### Change Password")
            
            with st.form("change_password_form", clear_on_submit=True):
                old_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                confirm_new_pwd = st.text_input("Confirm New Password", type="password")
                
                submit_pwd = st.form_submit_button("Update Password", icon=":material/lock:")
                
                if submit_pwd:
                    if not all([old_pwd, new_pwd, confirm_new_pwd]):
                        st.error("Please fill in all password fields.")
                    elif new_pwd != confirm_new_pwd:
                        st.error("New passwords do not match.")
                    else:
                        # Verify old password
                        users = load_json("users.json")
                        db_user = next((u for u in users if u["username"] == username), None)
                        
                        if db_user and verify_password(old_pwd, db_user["password"]):
                            # Validate strength
                            pwd_ok, pwd_msg = validate_password_strength(new_pwd)
                            if not pwd_ok:
                                st.error(pwd_msg)
                            else:
                                # Update password hash
                                hashed = hash_password(new_pwd)
                                for u in users:
                                    if u["username"] == username:
                                        u["password"] = hashed
                                        
                                if save_json("users.json", users):
                                    st.success("Password updated successfully!")
                                    st.toast("Password updated", icon=":material/check_circle:")
                                    # Update current session dictionary to match
                                    st.session_state.user["password"] = hashed
                                else:
                                    st.error("Failed to save changes in database.")
                        else:
                            st.error("Incorrect current password value.")
                            
    # ------------------ System Diagnostics ------------------
    st.space("medium")
    st.subheader("System Database Diagnostics", anchor=False)
    
    col_d1, col_d2 = st.columns([2, 1])
    
    with col_d1:
        with st.container(border=True):
            st.markdown("**Local Databases Health Check:**")
            
            db_stats = []
            files_to_check = ["users.json", "students.json", "attendance.json", "announcements.json", "events.json", "placements.json", "chat_history.json"]
            
            for f in files_to_check:
                records = load_json(f)
                db_stats.append({
                    "Database": f,
                    "Total Records": len(records),
                    "Status": "Healthy" if isinstance(records, list) else "Corrupted"
                })
                
            import pandas as pd
            st.dataframe(pd.DataFrame(db_stats), width="stretch", hide_index=True)
            
    with col_d2:
        with st.container(border=True):
            st.markdown("**Database Reset**")
            st.warning("Resetting will wipe all adjustments and re-populate the standard mock database records.", icon=":material/warning:")
            
            if st.button("Reset Databases to Defaults", key="reset_db_btn", type="primary"):
                # Simple re-init by deleting file and calling init_db
                import os
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(base_dir, "data")
                
                try:
                    for f in files_to_check:
                        f_path = os.path.join(data_dir, f)
                        if os.path.exists(f_path):
                            os.remove(f_path)
                    init_db()
                    st.success("All databases re-initialized successfully!")
                    st.toast("Reset done!", icon=":material/refresh:")
                    st.rerun()
                except Exception as e:
                    st.error(f"Reset failed: {str(e)}")
