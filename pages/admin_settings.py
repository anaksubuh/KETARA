import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin - Pengaturan",
    page_icon="⚙️",
    layout="wide",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time

# Inisialisasi session
init_session_state()
check_token_from_url()
require_auth()

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

# Sidebar untuk admin
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
    if st.button("📝 Kelola Soal", use_container_width=True):
        st.switch_page("pages/admin_questions.py")
    if st.button("📊 Lihat Jawaban", use_container_width=True):
        st.switch_page("pages/admin_responses.py")
    if st.button("⚙️ Pengaturan", use_container_width=True):
        st.switch_page("pages/admin_settings.py")
    
    st.markdown("---")
    
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

st.title("⚙️ Pengaturan Sistem")

github = GitHubAPI()
settings = github.get_settings()

# Pengaturan Umum
with st.expander("📋 Pengaturan Umum", expanded=True):
    with st.form("settings_form"):
        max_quota = st.number_input(
            "Maksimal Kuota per Tahun", 
            min_value=1, 
            max_value=50, 
            value=settings.get('max_quota_per_year', 10)
        )
        
        submitted = st.form_submit_button("💾 Simpan Pengaturan", use_container_width=True)
        
        if submitted:
            settings['max_quota_per_year'] = max_quota
            if github.save_settings(settings):
                st.success("✅ Pengaturan berhasil disimpan!")
                st.rerun()
            else:
                st.error("❌ Gagal menyimpan pengaturan")

# Manajemen NIK
with st.expander("👥 Manajemen NIK Valid", expanded=True):
    valid_niks = github.get_valid_niks()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_nik = st.text_input("Tambah NIK Baru", max_chars=16, placeholder="16 digit NIK", key="new_nik")
    with col2:
        if st.button("➕ Tambah", use_container_width=True):
            if len(new_nik) == 16 and new_nik.isdigit():
                if new_nik not in valid_niks:
                    if github.add_valid_nik(new_nik):
                        st.success(f"✅ NIK {new_nik} ditambahkan")
                        st.rerun()
                else:
                    st.warning("⚠️ NIK sudah terdaftar")
            else:
                st.error("❌ NIK harus 16 digit!")
    
    st.markdown("---")
    st.write(f"**Total NIK terdaftar: {len(valid_niks)}**")
    
    for nik in valid_niks:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"📌 `{nik}`")
        with col2:
            responses = github.get_user_responses(nik)
            current_year = datetime.now().year
            used = len([r for r in responses if r.get('year') == current_year])
            st.caption(f"Kuota: {used}/{settings.get('max_quota_per_year', 10)}")
        with col3:
            if st.button("🗑️", key=f"del_{nik}"):
                if github.remove_valid_nik(nik):
                    st.success(f"NIK {nik} dihapus")
                    st.rerun()

# Informasi Sistem
with st.expander("ℹ️ Informasi Sistem"):
    all_responses = github.get_all_responses()
    all_questions = github.get_all_questions()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Partisipasi", len(all_responses))
    with col2:
        st.metric("Total Warga", len(set([r['nik'] for r in all_responses])))
    with col3:
        st.metric("Total Soal", len(all_questions))

st.markdown("---")
st.caption("© 2024 Sistem Aspirasi & Polling - Kota Magelang")