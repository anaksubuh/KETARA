import streamlit as st
import sys
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Pengaturan", page_icon="⚙️", layout="wide", menu_items={'Get Help': None, 'Report a bug': None, 'About': None})
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

st.title("⚙️ Pengaturan Sistem")
st.markdown("Kelola konfigurasi sistem, NIK terdaftar, dan kuota partisipasi.")

github = GitHubAPI()
tab1, tab2 = st.tabs(["👥 Kelola NIK", "🎫 Kuota Partisipasi"])

with tab1:
    st.subheader("Daftar NIK Terdaftar")
    valid_niks = github.get_valid_niks()
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f"**Total NIK: {len(valid_niks)}**")
        if valid_niks:
            df_niks = pd.DataFrame(valid_niks, columns=['NIK'])
            st.dataframe(df_niks, use_container_width=True, height=300)
        else:
            st.info("Belum ada NIK terdaftar")
    with col2:
        st.markdown("### Tambah NIK")
        new_nik = st.text_input("NIK (16 digit)", max_chars=16)
        if st.button("➕ Tambah", use_container_width=True):
            if len(new_nik)==16 and new_nik.isdigit():
                if github.add_valid_nik(new_nik):
                    st.success(f"NIK {new_nik} ditambahkan")
                    st.rerun()
                else:
                    st.error("Gagal menambah")
            else:
                st.error("NIK harus 16 digit angka")
        st.markdown("### Hapus NIK")
        if valid_niks:
            nik_to_delete = st.selectbox("Pilih NIK", valid_niks)
            if st.button("🗑️ Hapus", use_container_width=True):
                github.delete_valid_nik(nik_to_delete)
                st.rerun()

with tab2:
    st.subheader("Pengaturan Kuota Partisipasi")
    current_quota = github.get_quota_config()
    max_quota = current_quota.get('max_per_year', 3)
    new_max = st.number_input("Maksimal partisipasi per tahun", min_value=1, max_value=100, value=max_quota)
    if st.button("💾 Simpan Kuota", use_container_width=True):
        github.update_quota_config(new_max)
        st.success("Kuota disimpan")
    if st.button("🔄 Reset Semua Kuota", use_container_width=True):
        github.reset_all_quotas()
        st.success("Semua kuota direset")