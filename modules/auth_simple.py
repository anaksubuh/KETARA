import streamlit as st
import uuid

# CREDENTIALS - GANTI SESUAI KEHENDAK ANDA
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'token' not in st.session_state:
        st.session_state.token = None

def check_token_from_url():
    query_params = st.query_params
    if 'token' in query_params:
        token = query_params['token']
        try:
            username = token.split('|')[0]
            if username == ADMIN_USERNAME:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "admin"
                st.session_state.token = token
                return True
        except:
            pass
    return False

def login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_id = str(uuid.uuid4())
        token = f"{username}|{session_id}"
        
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "admin"
        st.session_state.token = token
        
        st.query_params["token"] = token
        return True, "Login berhasil!"
    
    return False, "Username atau password salah!"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.token = None
    st.query_params.clear()
    st.rerun()

def require_auth():
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Silakan login terlebih dahulu")
        st.stop()