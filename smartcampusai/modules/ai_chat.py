import streamlit as st
import os
import requests
import json
import time
from datetime import datetime
from helpers.json_handler import load_json, save_json
from modules.utils import load_css, styled_header

def _call_gemini_api(messages: list[dict], api_key: str) -> str:
    """Calls the Gemini 1.5 Flash model API via REST requests with history context."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Map messages to Gemini API contents format (roles: 'user' and 'model')
    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
        
    payload = {"contents": contents}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"**Gemini API Error (HTTP {response.status_code}):** {response.text}"
    except requests.exceptions.Timeout:
        return "**Timeout Error:** The request to Gemini API timed out. Please try again."
    except Exception as e:
        return f"**Connection Error:** Failed to contact Gemini API. Details: {str(e)}"

def _get_mock_response(prompt: str) -> str:
    """Generates an intelligent simulated campus response if API key is not configured."""
    time.sleep(1.2) # Mock computation latency
    p = prompt.lower()
    
    if "hello" in p or "hi" in p:
        return "Hello! I am the SmartCampusAI Assistant. How can I help you today with your campus activities, class schedules, or placement cell information?"
    elif "placement" in p or "job" in p:
        return "You can check the **Placement Cell** page to view active hiring drives from companies like Google, Microsoft, and Infosys. There you can apply or see placement results."
    elif "attendance" in p:
        return "To view your attendance statistics or log new records, head over to the **Attendance Hub**. Faculty can mark attendance, and students can monitor their daily margins."
    elif "student" in p or "crud" in p:
        return "The **Student Management** page supports full registration, profile updates, and branch-wise directories. Administrative users have permissions to add, edit, or delete listings."
    else:
        return (
            f"Thank you for asking: '{prompt}'.\n\n"
            "*(System Notice: Gemini API Key was not detected in the environment config. Running in offline mock mode. "
            "To unlock complete intelligent answering, set the `GOOGLE_API_KEY` parameter in your `.env` file.)*"
        )

def show_ai_chat():
    """Renders the AI Assistant conversational UI with full history and export capabilities."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    user = st.session_state.user
    username = user.get("username")
    
    styled_header("Campus AI Assistant", "Instant Q&A regarding classes, placements, syllabus, and college FAQs", "chat")
    
    # Check for API Key in dotenv or system environment
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    
    if not api_key:
        st.warning("No `GOOGLE_API_KEY` was found in environment. The AI assistant is running in Offline Simulation Mode.", icon=":material/wifi_off:")
        
    # Initialize session state for this user's current session conversation
    if "chat_messages" not in st.session_state:
        # Try loading past history for this user from chat_history.json
        all_histories = load_json("chat_history.json")
        user_history = next((h for h in all_histories if h["username"] == username), None)
        
        if user_history:
            st.session_state.chat_messages = user_history.get("messages", [])
        else:
            # Default intro message
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": f"Hi {user.get('name')}! I am your SmartCampusAI assistant. Ask me anything about class schedules, upcoming events, placement drives, or campus databases!"
                }
            ]
            
    # Controls layout
    col_clear, col_dl, _ = st.columns([1, 1, 3])
    
    with col_clear:
        if st.button("Clear Chat", icon=":material/delete_sweep:", key="clear_chat_btn"):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Conversation cleared. How can I help you today?"
                }
            ]
            # Save empty log
            _save_history_to_db(username, st.session_state.chat_messages)
            st.rerun()
            
    with col_dl:
        # Prepare text file for download
        conversation_txt = ""
        for msg in st.session_state.chat_messages:
            role_lbl = "User" if msg["role"] == "user" else "Assistant"
            conversation_txt += f"[{role_lbl}]: {msg['content']}\n\n"
            
        st.download_button(
            label="Download Log",
            data=conversation_txt,
            file_name=f"smartcampusai_chat_{username}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            icon=":material/download:"
        )
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Display chat logs
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat prompt box
    if prompt := st.chat_input("Ask about syllabus, schedules, attendance criteria..."):
        # Display user input
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Append to state
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Call API / Simulation
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Generating answer..."):
                if api_key:
                    # Provide system instructions prefix to keep response campus-oriented
                    system_prompt = (
                        "You are an intelligent campus assistant for the SmartCampusAI platform. "
                        "You help students and faculty with scheduling, assignments, placements, and general college queries. "
                        "Keep your responses concise, professional, and formatted in clean Markdown. "
                        "Here is the user's question:\n"
                    )
                    
                    # Package context from history
                    history_context = st.session_state.chat_messages[:-1]
                    # Append prompt with system context
                    api_messages = history_context + [{"role": "user", "content": system_prompt + prompt}]
                    
                    response = _call_gemini_api(api_messages, api_key)
                else:
                    response = _get_mock_response(prompt)
                    
            response_placeholder.markdown(response)
            
        # Append response to state
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Save updated history back to database
        _save_history_to_db(username, st.session_state.chat_messages)

def _save_history_to_db(username: str, messages: list):
    """Saves user conversation transcripts into chat_history.json database."""
    all_histories = load_json("chat_history.json")
    
    # Filter out current user's old record if exists
    filtered_histories = [h for h in all_histories if h["username"] != username]
    
    # Append updated history record
    filtered_histories.append({
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages
    })
    
    save_json("chat_history.json", filtered_histories)
