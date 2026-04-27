import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.auth_simple import init_session_state, login, check_token_from_url

st.set_page_config(
    page_title="Admin Login",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

init_session_state()
check_token_from_url()

if st.session_state.get('authenticated', False):
    st.switch_page("pages/admin_dashboard.py")

st.markdown("""
<style>
    .login-box {
        max-width: 400px; margin: 2rem auto; padding: 2rem;
        background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-box">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center'>🏙️ Admin Login</h1>", unsafe_allow_html=True)
with st.form("login_form"):
    username = st.text_input("Username", placeholder="admin")
    password = st.text_input("Password", type="password", placeholder="••••••")
    if st.form_submit_button("Login", use_container_width=True, type="primary"):
        if login(username, password):
            st.success("Login berhasil!")
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("Username atau password salah")
st.caption("Demo: admin / admin123")
if st.button("← Kembali ke User", use_container_width=True):
    st.switch_page("pages/user.py")
st.markdown('</div>', unsafe_allow_html=True)