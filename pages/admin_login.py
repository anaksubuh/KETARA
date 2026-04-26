import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth_simple import init_session_state, check_token_from_url, login

# Konfigurasi halaman - HARUS PERTAMA
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

with st.form("login_form"):
    username = st.text_input("Username", placeholder="hahahihi", key="login_user")
    password = st.text_input("Password", type="password", placeholder="********", key="login_pass")
    
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
    with col2:
        if st.form_submit_button("Kembali", use_container_width=True):
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
