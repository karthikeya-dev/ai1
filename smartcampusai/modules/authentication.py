import streamlit as st
import time
from helpers.json_handler import load_json, append_json
from helpers.validators import is_valid_email, is_valid_mobile, validate_password_strength
from helpers.security import hash_password, verify_password
from modules.utils import load_css

def show_auth():
    """Renders the authentication interface (Login / Registration) with Glassmorphism styles."""
    load_css()
    
    # Initialize auth state if not set
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
        
    # Standard page config centering
    col_left, col_main, col_right = st.columns([1, 2, 1])
    
    with col_main:
        # App logo header
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 24px; padding-top: 30px;'>
                <div style='font-size: 3.5rem; color: #00f0ff;'>:material/school:</div>
                <h1 style='margin: 0; font-size: 2.5rem; font-weight: 800;'>
                    Smart<span class="gradient-text">CampusAI</span>
                </h1>
                <p style='margin: 6px 0 0 0; font-size: 1rem; opacity: 0.7;'>
                    Integrative AI-Powered Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display Forms
        if st.session_state.auth_mode == "login":
            render_login_form()
        else:
            render_register_form()

def render_login_form():
    """Renders the glassmorphic login screen."""
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0; text-align: center;'>Account Sign In</h3>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        
        role = st.selectbox("Select Your Role", ["Admin", "Faculty", "Student"], key="login_role")
        
        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember session", value=True)
        with col2:
            forgot_pwd = st.button("Forgot password?", key="forgot_pwd_btn", type="secondary")
            if forgot_pwd:
                st.info("Please contact the campus system administrator to reset your password.", icon=":material/info:")
                
        st.space("small")
        
        if st.button("Log In", key="login_submit_btn", width="stretch"):
            if not username or not password:
                st.error("Please fill in all fields.", icon=":material/warning:")
                return
                
            with st.spinner("Authenticating..."):
                time.sleep(1) # Loading animation simulation
                
                users = load_json("users.json")
                user = next((u for u in users if u["username"].lower() == username.strip().lower()), None)
                
                if user and verify_password(password, user["password"]):
                    if user["role"] != role:
                        st.error(f"Invalid role specified for account '{username}'.", icon=":material/gpp_bad:")
                        return
                        
                    # Successful login
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.toast("Success! Access granted.", icon=":material/check_circle:")
                    st.success("Login Successful! Redirecting...")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.", icon=":material/error:")
                    
        st.markdown("<div style='margin: 16px 0; text-align: center; opacity: 0.5;'>or</div>", unsafe_allow_html=True)
        if st.button("Create Account", key="goto_register_btn", width="stretch", type="secondary"):
            st.session_state.auth_mode = "register"
            st.rerun()

def render_register_form():
    """Renders the registration screen with fields and validations."""
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0; text-align: center;'>Account Registration</h3>", unsafe_allow_html=True)
        
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email Address", placeholder="Enter email (e.g. name@domain.com)")
        mobile = st.text_input("Mobile Number", placeholder="10-digit number")
        username = st.text_input("Username", placeholder="Enter unique username")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            password = st.text_input("Password", type="password", placeholder="Enter strong password")
        with col_p2:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Verify password")
            
        role = st.selectbox("Role", ["Student", "Faculty", "Admin"])
        
        st.space("small")
        
        if st.button("Sign Up", key="register_submit_btn", width="stretch"):
            # Core inputs check
            if not all([name, email, mobile, username, password, confirm_password]):
                st.error("All registration fields are required.", icon=":material/warning:")
                return
                
            # Validations
            if not is_valid_email(email):
                st.error("Invalid email address format.", icon=":material/error:")
                return
                
            if not is_valid_mobile(mobile):
                st.error("Invalid mobile phone number. Must be exactly 10 digits.", icon=":material/error:")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match.", icon=":material/error:")
                return
                
            # Strength Check
            pwd_ok, pwd_msg = validate_password_strength(password)
            if not pwd_ok:
                st.error(pwd_msg, icon=":material/lock_open:")
                return
                
            # Check duplicate username/email
            users = load_json("users.json")
            if any(u["username"].lower() == username.strip().lower() for u in users):
                st.error("Username is already taken. Please choose another one.", icon=":material/error:")
                return
                
            if any(u["email"].lower() == email.strip().lower() for u in users):
                st.error("Email is already registered. Please login or use another email.", icon=":material/error:")
                return
                
            # Perform registration write
            new_user = {
                "name": name.strip(),
                "email": email.strip(),
                "mobile": mobile.strip(),
                "username": username.strip(),
                "password": hash_password(password),
                "role": role
            }
            
            if append_json("users.json", new_user):
                st.success("Registration successful! Proceeding to log in...")
                time.sleep(1.5)
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.error("Database save failed. Please contact support.", icon=":material/database:")
                
        st.markdown("<div style='margin: 16px 0; text-align: center; opacity: 0.5;'>or</div>", unsafe_allow_html=True)
        if st.button("Back to Login", key="goto_login_btn", width="stretch", type="secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()
