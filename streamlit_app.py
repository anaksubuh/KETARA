import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Aspirasi & Polling - Kota Magelang",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Sembunyikan semua elemen bawaan Streamlit
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    button[kind="header"] { display: none !important; }
    .main > div { padding-top: 0rem; }
    .stStatusWidget { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Redirect ke halaman user
st.switch_page("pages/user.py")