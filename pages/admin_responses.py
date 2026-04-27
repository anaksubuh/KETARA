import streamlit as st
import sys
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Lihat Jawaban", page_icon="📊", layout="wide", menu_items={'Get Help': None, 'Report a bug': None, 'About': None})
sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
    [data-testid="stSidebar"] { display: block !important; background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stButton button { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:1rem;"><div style="font-size:3rem;">🏙️</div><h3>Kota Magelang</h3></div>', unsafe_allow_html=True)
    st.markdown(f"### 👤 {st.session_state.get('username', 'Admin')}")
    st.markdown("---")
    if st.button("🏠 Dashboard", use_container_width=True): st.switch_page("pages/admin_dashboard.py")
    if st.button("📝 Kelola Soal", use_container_width=True): st.switch_page("pages/admin_questions.py")
    if st.button("📊 Lihat Jawaban", use_container_width=True): st.switch_page("pages/admin_responses.py")
    if st.button("⚙️ Pengaturan", use_container_width=True): st.switch_page("pages/admin_settings.py")
    st.markdown("---")
    mins, secs = get_remaining_time()
    if mins>0 or secs>0: st.info(f"⏰ Session: {mins}m {secs}s")
    if st.button("🚪 Logout", use_container_width=True, type="primary"): logout(); st.rerun()

st.title("📊 Data Jawaban & Aspirasi")
st.markdown("Lihat, filter, dan export data partisipasi warga.")

github = GitHubAPI()
responses = github.get_all_responses()

if not responses:
    st.info("📭 Belum ada data partisipasi.")
else:
    niks = ['Semua'] + sorted(list(set(r.get('nik') for r in responses)))
    filter_nik = st.selectbox("Filter NIK", niks)
    
    filtered = responses
    if filter_nik != 'Semua':
        filtered = [r for r in filtered if r.get('nik') == filter_nik]
    
    st.markdown(f"**Menampilkan {len(filtered)} dari {len(responses)} data**")
    for r in filtered:
        with st.expander(f"📅 {r.get('submitted_at')} - NIK: {r.get('nik')}"):
            aspirasi = r.get('aspirasi', '')
            if aspirasi:
                st.markdown("**💬 Aspirasi:**")
                st.write(aspirasi)
            st.markdown("**📋 Jawaban Polling:**")
            for ans in r.get('responses', []):
                if ans.get('answer'):
                    st.write(f"- {ans.get('question')}: **{ans.get('answer')}**")