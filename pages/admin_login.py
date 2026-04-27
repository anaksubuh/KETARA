import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth_simple import init_session_state, login

# Konfigurasi halaman
st.set_page_config(
    page_title="Admin Login - Kota Magelang",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",  # Sembunyikan sidebar di halaman login
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

init_session_state()

# Icon
st.markdown("""
<div class="login-icon">
    🏙️
</div>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<h1 class="login-title">Admin Login</h1>
<div class="decorative-line"></div>
<p class="login-subtitle">Sistem Aspirasi & Polling<br>Kota Magelang</p>
""", unsafe_allow_html=True)

# Form login
username = st.text_input("Username", placeholder="admin", key="admin_user")
password = st.text_input("Password", type="password", placeholder="••••••", key="admin_pass")

# Tombol Login
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Login", use_container_width=True, type="primary"):
        if login(username, password):
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("❌ Username atau password salah!")

# Demo info
st.markdown("""
<div class="demo-info">
    🔐 Demo: <strong>admin</strong> / <strong>admin123</strong>
</div>
""", unsafe_allow_html=True)

# Tombol kembali
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Kembali ke Halaman User", use_container_width=True):
    st.switch_page("app.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)