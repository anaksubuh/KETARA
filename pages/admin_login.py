import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth_simple import init_session_state, login

st.set_page_config(
    page_title="Admin Login - Kota Magelang",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

init_session_state()

# CSS khusus login
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 2rem; }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .login-title {
        text-align: center;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<h1 class="login-title">🏙️ Admin Login</h1>', unsafe_allow_html=True)
st.markdown('<p class="login-subtitle">Sistem Aspirasi & Polling Kota Magelang</p>', unsafe_allow_html=True)

username = st.text_input("Username", placeholder="admin")
password = st.text_input("Password", type="password", placeholder="••••••")

if st.button("Login", use_container_width=True, type="primary"):
    if login(username, password):
        st.switch_page("pages/admin_dashboard.py")
    else:
        st.error("❌ Username atau password salah!")

st.markdown('<p style="text-align:center; margin-top:1rem;">🔐 Demo: admin / admin123</p>', unsafe_allow_html=True)

if st.button("← Kembali ke Halaman User", use_container_width=True):
    st.switch_page("pages/user.py")

st.markdown('</div>', unsafe_allow_html=True)