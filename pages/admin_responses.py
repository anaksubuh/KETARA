import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="Lihat Jawaban", page_icon="📊", layout="wide")
sys.path.append(str(Path(__file__).parent.parent))
from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

with st.sidebar:
    # Sama seperti di admin_questions.py
    st.markdown('<div style="text-align:center"><h2>🏙️ Kota Magelang</h2></div>', unsafe_allow_html=True)
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown("---")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
    if st.button("📝 Kelola Soal", use_container_width=True):
        st.switch_page("pages/admin_questions.py")
    if st.button("📋 Lihat Jawaban", use_container_width=True):
        st.switch_page("pages/admin_responses.py")
    if st.button("⚙️ Pengaturan", use_container_width=True):
        st.switch_page("pages/admin_settings.py")
    st.markdown("---")
    mins, secs = get_remaining_time()
    if mins or secs:
        st.info(f"⏰ {mins}m {secs}s")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
        st.rerun()

st.title("📋 Data Jawaban & Aspirasi")
github = GitHubAPI()
responses = github.get_all_responses()
if not responses:
    st.info("Belum ada data")
else:
    filter_nik = st.selectbox("Filter NIK", ["Semua"] + sorted(set(r['nik'] for r in responses)))
    filtered = responses if filter_nik == "Semua" else [r for r in responses if r['nik'] == filter_nik]
    for r in filtered:
        with st.expander(f"📅 {r['submitted_at']} - NIK: {r['nik']}"):
            if r.get('aspirasi'):
                st.markdown(f"**Aspirasi:** {r['aspirasi']}")
            for ans in r['responses']:
                if ans.get('answer'):
                    st.write(f"- {ans['question']}: **{ans['answer']}**")