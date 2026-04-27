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
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

init_session_state()

# CSS untuk sidebar dan login form
st.markdown("""
<style>
    /* Sembunyikan elemen bawaan, TAPI SIDEBAR TETAP MUNCUL */
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
    
    /* Pastikan sidebar tetap terlihat dan cantik */
    [data-testid="stSidebar"] { 
        display: block !important;
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2);
    }
    
    /* Styling login box */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-box {
        max-width: 450px;
        width: 100%;
        padding: 2.5rem;
        background: white;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    .login-icon {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .login-title {
        text-align: center;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        font-size: 1.8rem;
    }
    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR - Tetap muncul di halaman login
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/white?text=Kota+Magelang", use_container_width=True)
    st.markdown("### 🔐 Admin Area")
    st.markdown("Sistem Aspirasi & Polling")
    st.markdown("---")
    st.markdown("**Informasi:**")
    st.markdown("- Login untuk mengakses panel admin")
    st.markdown("- Kelola soal polling")
    st.markdown("- Lihat data partisipasi")
    st.markdown("- Kelola NIK terdaftar")
    st.markdown("---")
    st.caption("© 2024 Kota Magelang")

# Main content - Login Form
st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.markdown('<div class="login-icon">🔐</div>', unsafe_allow_html=True)
st.markdown('<h2 class="login-title">Admin Login</h2>', unsafe_allow_html=True)
st.markdown('<p class="login-subtitle">Masukkan kredensial Anda untuk mengakses panel admin</p>', unsafe_allow_html=True)

username = st.text_input("Username", key="admin_user", placeholder="admin")
password = st.text_input("Password", type="password", key="admin_pass", placeholder="••••••")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("Login", use_container_width=True, type="primary"):
        if login(username, password):
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("❌ Username atau password salah!")

st.markdown("---")
st.markdown('<p style="text-align: center; color: #999; font-size: 0.8rem;">Demo: admin / admin123</p>', unsafe_allow_html=True)

# Tombol kembali ke halaman user
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("← Kembali ke Halaman User", use_container_width=True):
        st.switch_page("app.py")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)