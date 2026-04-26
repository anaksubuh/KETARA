import streamlit as st
import uuid
from datetime import datetime, timedelta

# ========== KONFIGURASI SESSION ==========
# GAMPANG DIUBAH - Tinggal ganti angka menitnya!
SESSION_DURATION_MINUTES = 10  # <-- GANTI ANGKA INI untuk mengubah durasi login

# CREDENTIALS (GAMPANG DIUBAH)
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
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'expiry_time' not in st.session_state:
        st.session_state.expiry_time = None

def check_token_from_url():
    """Cek token dari URL parameter - TIDAK LOGOUT SAAT REFRESH"""
    query_params = st.query_params
    
    # Cek dari URL parameter
    if 'token' in query_params:
        token = query_params['token']
        try:
            # Token format: username|session_id|expiry_time
            parts = token.split('|')
            if len(parts) >= 3:
                username = parts[0]
                session_id = parts[1]
                expiry_time_str = parts[2]
                
                # Cek apakah session masih valid (belum expired)
                expiry_time = datetime.fromisoformat(expiry_time_str)
                if datetime.now() < expiry_time:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "admin"
                    st.session_state.token = token
                    st.session_state.session_id = session_id
                    st.session_state.login_time = datetime.now()
                    st.session_state.expiry_time = expiry_time
                    
                    # Tampilkan sisa waktu di sidebar nanti
                    return True
                else:
                    # Token expired, hapus dari URL
                    st.query_params.clear()
                    st.warning(f"⏰ Session telah berakhir ({SESSION_DURATION_MINUTES} menit). Silakan login kembali.")
                    return False
        except Exception as e:
            pass
    
    return False

def login(username, password):
    """Proses login - session berlaku SESSION_DURATION_MINUTES menit"""
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_id = str(uuid.uuid4())
        login_time = datetime.now()
        expiry_time = login_time + timedelta(minutes=SESSION_DURATION_MINUTES)
        
        # Format token: username|session_id|expiry_time
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
    """Proses logout"""
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
    """Middleware untuk halaman admin"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Silakan login terlebih dahulu")
        st.stop()
    
    if st.session_state.get('role') != 'admin':
        st.error("❌ Anda tidak memiliki akses ke halaman ini")
        st.stop()
    
    # Cek apakah session masih valid (belum expired)
    if st.session_state.expiry_time:
        remaining = (st.session_state.expiry_time - datetime.now()).total_seconds()
        if remaining <= 0:
            logout()
            st.warning(f"⏰ Session telah berakhir ({SESSION_DURATION_MINUTES} menit). Silakan login kembali.")
            st.rerun()
        elif remaining < 60:  # Kurang dari 1 menit
            st.warning(f"⚠️ Session akan berakhir dalam {int(remaining)} detik!")

def get_remaining_time():
    """Mendapatkan sisa waktu session dalam menit dan detik"""
    if st.session_state.expiry_time:
        remaining = (st.session_state.expiry_time - datetime.now()).total_seconds()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return minutes, seconds
    return 0, 0