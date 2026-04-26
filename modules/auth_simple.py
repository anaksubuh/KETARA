import hashlib
from datetime import datetime, timedelta
import uuid
import streamlit as st
from pathlib import Path

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'token' not in st.session_state:
        st.session_state.token = None

def check_token_from_url():
    """Cek token dari URL parameter"""
    query_params = st.query_params
    
    if 'token' in query_params:
        token = query_params['token']
        try:
            # Validasi token sederhana
            parts = token.split('|')
            if len(parts) >= 2:
                username = parts[0]
                # Cek apakah username adalah admin
                admin_user = st.secrets.get("ADMIN_USERNAME", "admin")
                if username == admin_user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "admin"
                    st.session_state.token = token
                    return True
        except:
            pass
    
    return False

def login(username: str, password: str):
    """Proses login admin"""
    admin_user = st.secrets.get("ADMIN_USERNAME", "admin")
    admin_hash = st.secrets.get("ADMIN_PASSWORD_HASH")
    
    if username == admin_user and hash_password(password) == admin_hash:
        session_id = str(uuid.uuid4())
        token = f"{username}|{session_id}"
        
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.session_id = session_id
        st.session_state.role = "admin"
        st.session_state.token = token
        
        st.query_params["token"] = token
        
        return True, "Login berhasil!"
    
    return False, "Username atau password salah!"

def logout():
    """Proses logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.session_id = None
    st.session_state.role = None
    st.session_state.token = None
    
    st.query_params.clear()
    st.rerun()

def require_auth():
    """Middleware untuk halaman admin"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Silakan login terlebih dahulu")
        st.stop()
    
    if st.session_state.get('role') != 'admin':
        st.error("❌ Anda tidak memiliki akses ke halaman ini")
        st.stop()