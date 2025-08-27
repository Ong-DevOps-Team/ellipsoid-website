#!/usr/bin/env python3
"""
Streamlit Test Application for ChatGIS Endpoint

This application provides a test interface for the chat/gis endpoint with:
1. Login page for authentication
2. Chat interface with the GIS AI
3. Raw text display of chat history to inspect geo-XML tags
4. Areas of interest disabled for this initial version

Requirements:
- streamlit
- requests
- python-dotenv (optional, for environment variables)
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BACKEND_URL}/auth/login"
CHAT_GIS_ENDPOINT = f"{BACKEND_URL}/chat/gis"
SYSTEM_PROMPTS_ENDPOINT = f"{BACKEND_URL}/system-prompts"

# Page configuration
st.set_page_config(
    page_title="ChatGIS Test Application",
    page_icon="🌍",
    layout="wide",  # Use wide layout for maximum screen real estate
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = None

def login_user(username: str, password: str) -> bool:
    """
    Authenticate user with the backend
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(LOGIN_ENDPOINT, json=login_data)
        
        if response.status_code == 200:
            auth_data = response.json()
            st.session_state.authenticated = True
            st.session_state.access_token = auth_data['access_token']
            st.session_state.username = auth_data['username']
            st.session_state.user_id = auth_data['user_id']
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
            
    except requests.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers for API requests"""
    return {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }

def load_system_prompt() -> Optional[str]:
    """Load system prompt from backend"""
    try:
        response = requests.get(SYSTEM_PROMPTS_ENDPOINT)
        if response.status_code == 200:
            prompts = response.json()
            return prompts.get('gis_expert')
        return None
    except Exception as e:
        st.warning(f"Could not load system prompt: {str(e)}")
        return None

def send_chat_message(message: str) -> bool:
    """
    Send message to chat/gis endpoint
    
    Args:
        message: User's message
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare chat request
        chat_request = {
            "message": message,
            "chat_history": st.session_state.chat_history,
            "session_id": st.session_state.session_id,
            "areas_of_interest": None  # Disabled for this version
        }
        
        response = requests.post(
            CHAT_GIS_ENDPOINT,
            json=chat_request,
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            chat_response = response.json()
            
            # Update session state with response
            st.session_state.chat_history = chat_response['chat_history']
            st.session_state.session_id = chat_response.get('session_id')
            
            return True
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"Chat request failed: {error_detail}")
            return False
            
    except requests.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Chat error: {str(e)}")
        return False

def logout():
    """Clear session state and logout user"""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.chat_history = []
    st.session_state.session_id = None
    st.session_state.system_prompt = None

def render_login_page():
    """Render the login page"""
    st.title("🌍 ChatGIS Test Application")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    with st.spinner("Logging in..."):
                        if login_user(username, password):
                            st.success("Login successful!")
                            st.rerun()
                else:
                    st.error("Please enter both username and password")
    
    # Backend connection status
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backend Status")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend is running")
            else:
                st.error("❌ Backend is not responding properly")
        except:
            st.error("❌ Cannot connect to backend")
    
    with col2:
        st.subheader("Configuration")
        st.info(f"Backend URL: `{BACKEND_URL}`")

def render_chat_page():
    """Render the main chat interface"""
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🌍 ChatGIS Test Application")
        st.caption(f"Logged in as: **{st.session_state.username}** (ID: {st.session_state.user_id})")
    
    with col2:
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar with configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Session info
        st.subheader("Session Info")
        st.write(f"**Session ID:** {st.session_state.session_id or 'None'}")
        st.write(f"**Messages:** {len(st.session_state.chat_history)}")
        
        # Areas of interest (disabled for this version)
        st.subheader("Areas of Interest")
        st.info("🚫 Areas of Interest are disabled in this test version")
        
        # Clear chat button
        st.markdown("---")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.session_id = None
            st.rerun()
        
        # Load system prompt
        if st.button("Load System Prompt", use_container_width=True):
            with st.spinner("Loading system prompt..."):
                prompt = load_system_prompt()
                if prompt:
                    st.session_state.system_prompt = prompt
                    st.success("System prompt loaded!")
                else:
                    st.error("Failed to load system prompt")
    
    # Main chat interface - Use full width for chat, sidebar for controls
    st.subheader("Chat Interface")
    
    # Chat input form - full width
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_area(
            "Your message:",
            height=100,
            placeholder="Ask something about GIS... (e.g., 'Tell me about mapping in San Francisco')"
        )
        submit_chat = st.form_submit_button("Send Message", use_container_width=True)
        
        if submit_chat and user_message.strip():
            with st.spinner("Sending message..."):
                if send_chat_message(user_message.strip()):
                    st.rerun()
    
    # Chat history display - full width with very wide text areas
    st.subheader("Chat History (Raw Text - Full Width Display)")
    
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            # Color coding for different roles with expanded display
            if role == 'user':
                st.markdown(f"**🧑 User (Message {i+1}):**")
                # Use text_area with very wide display for better readability
                st.text_area(
                    f"User Message {i+1}",
                    value=content,
                    height=max(100, min(400, len(content) // 5)),  # Dynamic height based on content
                    disabled=True,
                    label_visibility="collapsed"
                )
            elif role == 'assistant':
                st.markdown(f"**🤖 Assistant (Message {i+1}):**")
                # Use text_area with very wide display for better readability
                st.text_area(
                    f"Assistant Message {i+1}",
                    value=content,
                    height=max(150, min(500, len(content) // 4)),  # Dynamic height based on content
                    disabled=True,
                    label_visibility="collapsed"
                )
            elif role == 'system':
                st.markdown(f"**⚙️ System (Message {i+1}):**")
                # Use text_area with very wide display for better readability
                st.text_area(
                    f"System Message {i+1}",
                    value=content,
                    height=max(100, min(300, len(content) // 6)),  # Dynamic height based on content
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            st.markdown("---")
    else:
        st.info("No chat history yet. Send a message to start the conversation!")
    
    # System prompt in an expander for full width when needed
    with st.expander("🔧 System Prompt", expanded=False):
        if st.session_state.system_prompt:
            st.text_area(
                "Current system prompt:",
                value=st.session_state.system_prompt,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
        else:
            st.info("No system prompt loaded. Click 'Load System Prompt' in the sidebar to retrieve it from the backend.")
    
    # Backend status at bottom
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Disconnected")
    
    with col2:
        st.info(f"📊 Messages: {len(st.session_state.chat_history)}")
    
    with col3:
        st.info(f"🆔 Session: {st.session_state.session_id or 'None'}")

def main():
    """Main application function"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        render_login_page()
    else:
        render_chat_page()

if __name__ == "__main__":
    main()
