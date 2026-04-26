import streamlit as st
import uuid
from datetime import datetime, timedelta

# ========== KONFIGURASI SESSION ==========
SESSION_DURATION_MINUTES = 10

# CREDENTIALS
ADMIN_USERNAME = "hahahihi"
ADMIN_PASSWORD = "mungedan123#"

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'expiry_time' not in st.session_state:
        st.session_state.expiry_time = None

def check_token_from_url():
    query_params = st.query_params
    
    if st.session_state.get('logged_in', False):
        if st.session_state.expiry_time:
            if datetime.now() < st.session_state.expiry_time:
                return True
            else:
                logout()
                return False
        return True
    
    if 'token' in query_params:
        token = query_params['token']
        try:
            parts = token.split('|')
            if len(parts) >= 3:
                username = parts[0]
                session_id = parts[1]
                expiry_time_str = parts[2]
                
                expiry_time = datetime.fromisoformat(expiry_time_str)
                if datetime.now() < expiry_time:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "admin"
                    st.session_state.token = token
                    st.session_state.session_id = session_id
                    st.session_state.login_time = datetime.now()
                    st.session_state.expiry_time = expiry_time
                    return True
                else:
                    st.query_params.clear()
                    return False
        except Exception as e:
            pass
    
    return False

def login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_id = str(uuid.uuid4())
        login_time = datetime.now()
        expiry_time = login_time + timedelta(minutes=SESSION_DURATION_MINUTES)
        
        token = f"{username}|{session_id}|{expiry_time.isoformat()}"
        
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "admin"
        st.session_state.token = token
        st.session_state.session_id = session_id
        st.session_state.login_time = login_time
        st.session_state.expiry_time = expiry_time
        
        st.query_params["token"] = token
        
        return True, f"Login berhasil! Session berlaku {SESSION_DURATION_MINUTES} menit"
    
    return False, "Username atau password salah!"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.token = None
    st.session_state.session_id = None
    st.session_state.login_time = None
    st.session_state.expiry_time = None
    
    st.query_params.clear()
    st.rerun()

def require_auth():
    if st.session_state.get('logged_in', False):
        if st.session_state.expiry_time:
            if datetime.now() < st.session_state.expiry_time:
                return
            else:
                logout()
                st.warning("⏰ Session telah berakhir. Silakan login kembali.")
                st.stop()
    
    if not check_token_from_url():
        st.warning("⚠️ Silakan login terlebih dahulu")
        st.stop()
    
    if st.session_state.get('role') != 'admin':
        st.error("❌ Anda tidak memiliki akses ke halaman ini")
        st.stop()

def get_remaining_time():
    if st.session_state.expiry_time:
        remaining = (st.session_state.expiry_time - datetime.now()).total_seconds()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return minutes, seconds
    return 0, 0