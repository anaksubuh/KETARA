import streamlit as st
from datetime import datetime, timedelta
import hashlib
import time

# Dummy admin credentials (bisa diganti dengan database nanti)
ADMIN_CREDENTIALS = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest()
}

SESSION_DURATION = timedelta(hours=8)

def init_session_state():
    """Inisialisasi session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'expiry_time' not in st.session_state:
        st.session_state.expiry_time = None

def verify_password(username, password):
    """Verifikasi username dan password"""
    if username in ADMIN_CREDENTIALS:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return hashed == ADMIN_CREDENTIALS[username]
    return False

def login(username, password):
    """Proses login"""
    if verify_password(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.login_time = datetime.now()
        st.session_state.expiry_time = datetime.now() + SESSION_DURATION
        return True
    return False

def logout():
    """Proses logout"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None
    st.session_state.expiry_time = None

def is_session_valid():
    """Cek apakah session masih valid"""
    if not st.session_state.authenticated:
        return False
    if st.session_state.expiry_time and datetime.now() > st.session_state.expiry_time:
        logout()
        return False
    return True

def require_auth():
    """Decorator untuk require authentication"""
    if not is_session_valid():
        st.warning("⚠️ Silakan login terlebih dahulu!")
        st.switch_page("pages/admin_login.py")
        st.stop()
    return True

def get_remaining_time():
    """Dapatkan sisa waktu session"""
    if st.session_state.expiry_time:
        remaining = st.session_state.expiry_time - datetime.now()
        if remaining.total_seconds() > 0:
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            return minutes, seconds
    return 0, 0

def check_token_from_url():
    """Cek token dari URL (untuk auto-login via link)"""
    query_params = st.query_params
    if 'token' in query_params and query_params['token'] == 'admin_secret_2024':
        if not st.session_state.authenticated:
            login('admin', 'admin123')
            st.rerun()