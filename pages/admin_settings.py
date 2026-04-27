import streamlit as st
import sys
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Pengaturan", page_icon="⚙️", layout="wide")
sys.path.append(str(Path(__file__).parent.parent))
from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

with st.sidebar:
    # Sama seperti sebelumnya
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

st.title("⚙️ Pengaturan Sistem")
github = GitHubAPI()
tab1, tab2 = st.tabs(["👥 Kelola NIK", "🎫 Kuota Partisipasi"])

with tab1:
    niks = github.get_valid_niks()
    col1, col2 = st.columns([2,1])
    with col1:
        st.dataframe(pd.DataFrame(niks, columns=["NIK"]), use_container_width=True) if niks else st.info("Belum ada NIK")
    with col2:
        new_nik = st.text_input("Tambah NIK (16 digit)", max_chars=16)
        if st.button("➕ Tambah"):
            if len(new_nik)==16 and new_nik.isdigit():
                github.add_valid_nik(new_nik)
                st.rerun()
        if niks:
            del_nik = st.selectbox("Hapus NIK", niks)
            if st.button("🗑️ Hapus"):
                github.delete_valid_nik(del_nik)
                st.rerun()

with tab2:
    config = github.get_quota_config()
    max_q = config.get('max_per_year', 3)
    new_max = st.number_input("Maksimal partisipasi per tahun", min_value=1, value=max_q)
    if st.button("💾 Simpan Kuota"):
        github.update_quota_config(new_max)
        st.success("Tersimpan")
    if st.button("🔄 Reset Semua Kuota"):
        github.reset_all_quotas()
        st.success("Reset berhasil")