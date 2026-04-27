import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.auth_simple import init_session_state, login, check_token_from_url

st.set_page_config(
    page_title="Admin Login - Kota Magelang",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

init_session_state()
check_token_from_url()  # Auto login dari token

# Jika sudah login, langsung ke dashboard
if st.session_state.get('authenticated', False):
    st.switch_page("pages/admin_dashboard.py")

# CSS untuk tampilan login
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    .login-title {
        text-align: center;
        color: #667eea;
        margin-bottom: 1rem;
    }
    .login-icon {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-icon">🏙️</div>', unsafe_allow_html=True)
st.markdown('<h1 class="login-title">Admin Login</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center">Sistem Aspirasi & Polling Kota Magelang</p>', unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Username", placeholder="admin")
    password = st.text_input("Password", type="password", placeholder="••••••")
    submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
    if submitted:
        if login(username, password):
            st.success("Login berhasil! Mengalihkan...")
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("Username atau password salah!")

st.caption("Demo: admin / admin123")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("← Kembali ke Halaman User", use_container_width=True):
        st.switch_page("pages/user.py")