import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth_simple import init_session_state, check_token_from_url, login

# Konfigurasi halaman
st.set_page_config(
    page_title="Admin Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Tambahkan di setiap halaman admin setelah st.set_page_config
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    button[kind="header"] { display: none !important; }
    .main > div { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# Tambahkan tombol logout di sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        from modules.auth_simple import logout
        logout()
    st.markdown("---")
    st.caption("📌 Gunakan menu di sidebar kiri untuk navigasi")

# Sembunyikan elemen bawaan
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# Inisialisasi
init_session_state()
check_token_from_url()

# Jika sudah login, redirect ke dashboard
if st.session_state.get('logged_in', False):
    st.success(f"✅ Anda sudah login sebagai {st.session_state.username}")
    if st.button("🚀 Buka Dashboard Admin", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
    st.stop()

st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 20px; max-width: 450px; width: 100%;">
        <div style="background: white; padding: 35px; border-radius: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 60px; margin-bottom: 20px;">🔐</div>
                <h1 style="color: #667eea; margin-bottom: 10px;">Admin Login</h1>
                <p style="color: #666; margin-bottom: 30px;">Masukkan username dan password</p>
            </div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Username", placeholder="admin")
    password = st.text_input("Password", type="password", placeholder="admin123")
    
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
    with col2:
        if st.form_submit_button("Kembali ke User", use_container_width=True):
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
        st.warning("Harap isi username dan password")

st.markdown("""
            <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;">
                <strong>🔑 Credentials Default</strong><br>
                Username: <code style="background:#e0e0e0; padding:2px 6px; border-radius:4px;">admin</code><br>
                Password: <code style="background:#e0e0e0; padding:2px 6px; border-radius:4px;">admin123</code>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)