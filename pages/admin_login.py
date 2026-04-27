import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth_simple import init_session_state, login

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin Login - Kota Magelang",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# Hilangkan semua elemen termasuk sidebar (halaman login tidak butuh sidebar)
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# Custom CSS untuk login form
st.markdown("""
<style>
    .login-box {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-top: 3rem;
    }
    .login-title {
        text-align: center;
        color: #1a1a2e;
        margin-bottom: 2rem;
    }
    .login-icon {
        text-align: center;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

init_session_state()

# Login form
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-icon">🔐</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="login-title">Admin Login<br>Kota Magelang</h2>', unsafe_allow_html=True)
    
    username = st.text_input("Username", key="admin_user", placeholder="admin")
    password = st.text_input("Password", type="password", key="admin_pass", placeholder="••••••")
    
    if st.button("Login", use_container_width=True, type="primary"):
        if login(username, password):
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("❌ Username atau password salah!")
    
    st.markdown('<p style="text-align: center; margin-top: 1rem; color: #666; font-size: 0.8rem;">Demo: admin / admin123</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)