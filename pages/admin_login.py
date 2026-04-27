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

# CSS Premium untuk halaman login
st.markdown("""
<style>
    /* Hapus semua margin dan padding */
    .main > div {
        padding: 0 !important;
    }
    
    /* Sembunyikan semua elemen bawaan */
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    
    /* Background gradient yang cantik */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Container utama */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 1rem;
    }
    
    /* Card login */
    .login-card {
        background: white;
        border-radius: 32px;
        padding: 2.5rem;
        max-width: 450px;
        width: 100%;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Icon */
    .login-icon {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Title */
    .login-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle */
    .login-subtitle {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    
    /* Decorative line */
    .decorative-line {
        width: 60px;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 1rem auto;
        border-radius: 2px;
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Custom button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(102, 126, 234, 0.5);
    }
    
    /* Back button */
    .back-button {
        text-align: center;
        margin-top: 1.5rem;
    }
    
    .back-button button {
        background: transparent !important;
        color: #667eea !important;
        box-shadow: none !important;
    }
    
    .back-button button:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        transform: none !important;
    }
    
    /* Demo info */
    .demo-info {
        text-align: center;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
        font-size: 0.8rem;
        color: #999;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 12px !important;
        margin-top: 1rem !important;
    }
    
    /* Hide default Streamlit elements */
    div[data-testid="stDecoration"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Container utama
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="login-card">', unsafe_allow_html=True)

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