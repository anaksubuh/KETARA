import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth import init_session_state, check_token_from_url, login, logout

# Konfigurasi halaman
st.set_page_config(
    page_title="Login - Sistem Polling",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS untuk halaman login yang cantik
st.markdown("""
<style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 450px;
        width: 100%;
    }
    .login-box {
        background: white;
        padding: 35px;
        border-radius: 15px;
    }
    .login-title {
        text-align: center;
        margin-bottom: 30px;
    }
    .login-title h1 {
        color: #667eea;
        margin-bottom: 10px;
    }
    .login-title p {
        color: #666;
        font-size: 14px;
    }
    .login-icon {
        font-size: 60px;
        text-align: center;
        margin-bottom: 20px;
    }
    .info-login {
        background: #f0f0f0;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session
init_session_state()
check_token_from_url()

# Jika sudah login, redirect ke dashboard
if st.session_state.get('logged_in', False):
    st.success(f"✅ Anda sudah login sebagai {st.session_state.username}")
    if st.button("🚀 Buka Dashboard Admin", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
    st.stop()

# Tampilkan halaman login
st.markdown("""
<div class="login-container">
    <div class="login-card">
        <div class="login-box">
            <div class="login-icon">🔐</div>
            <div class="login-title">
                <h1>Login Admin</h1>
                <p>Masukkan credentials untuk mengakses panel admin</p>
            </div>
""", unsafe_allow_html=True)

# Form Login
with st.form("login_form"):
    username = st.text_input("👤 Username", placeholder="admin", key="login_user")
    password = st.text_input("🔑 Password", type="password", placeholder="••••••", key="login_pass")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submitted = st.form_submit_button("🔐 Login", use_container_width=True, type="primary")
    with col2:
        if st.form_submit_button("🏠 Kembali ke User", use_container_width=True):
            st.switch_page("pages/user.py")

if submitted:
    if username and password:
        success, message = login(username, password)
        if success:
            st.success(message)
            st.balloons()
            st.rerun()
        else:
            st.error(message)
    else:
        st.warning("⚠️ Harap isi username dan password")

# Info default login
st.markdown("""
<div class="info-login">
    <strong>ℹ️ Informasi Login Default</strong><br>
    Username: <code>admin</code><br>
    Password: <code>admin123</code>
</div>
""", unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
</div>
""", unsafe_allow_html=True)