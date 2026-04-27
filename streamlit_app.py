import streamlit as st

st.set_page_config(
    page_title="Sistem Aspirasi & Polling - Kota Magelang",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# Redirect langsung ke halaman user
st.switch_page("pages/user.py")