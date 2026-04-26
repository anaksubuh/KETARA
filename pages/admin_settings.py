import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time, SESSION_DURATION_MINUTES

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin - Pengaturan",
    page_icon="⚙️",
    layout="wide"
)

# Inisialisasi session - SETELAH page_config
init_session_state()
check_token_from_url()
require_auth()

# Custom CSS
st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .settings-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .settings-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="font-size: 3rem;">⚙️</div>
        <h3>{st.session_state.username}</h3>
        <p style="color: #667eea; font-weight: bold;">Administrator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
    
    st.markdown("---")
    st.caption("📌 Gunakan menu di sidebar kiri untuk navigasi")

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>⚙️ Pengaturan Sistem</h1>
            <p>Kelola konfigurasi sistem, NIK valid, dan pengaturan lainnya</p>
        </div>
        <div style="font-size: 3rem;">🔧</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Inisialisasi
github = GitHubAPI()
settings = github.get_settings()

# ========== PENGATURAN UMUM ==========
st.markdown('<div class="settings-card">', unsafe_allow_html=True)
st.markdown('<div class="settings-title">📋 Pengaturan Umum</div>', unsafe_allow_html=True)

with st.form("general_settings_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        max_quota = st.number_input(
            "Maksimal Kuota per Tahun", 
            min_value=1, 
            max_value=50, 
            value=settings.get('max_quota_per_year', 10)
        )
    
    submitted = st.form_submit_button("💾 Simpan Pengaturan", use_container_width=True, type="primary")
    
    if submitted:
        settings['max_quota_per_year'] = max_quota
        if github.save_settings(settings):
            st.success("✅ Pengaturan berhasil disimpan!")
            st.rerun()
        else:
            st.error("❌ Gagal menyimpan pengaturan")

st.markdown('</div>', unsafe_allow_html=True)

# ========== MANAJEMEN NIK VALID ==========
st.markdown('<div class="settings-card">', unsafe_allow_html=True)
st.markdown('<div class="settings-title">👥 Manajemen NIK Valid</div>', unsafe_allow_html=True)

valid_niks = github.get_valid_niks()

col1, col2 = st.columns([3, 1])
with col1:
    new_nik = st.text_input(
        "Tambah NIK Baru", 
        max_chars=16, 
        placeholder="Masukkan 16 digit NIK",
        key="new_nik_input",
        label_visibility="collapsed"
    )
with col2:
    if st.button("➕ Tambah", use_container_width=True):
        if len(new_nik) == 16 and new_nik.isdigit():
            if new_nik not in valid_niks:
                if github.add_valid_nik(new_nik):
                    st.success(f"✅ NIK {new_nik} berhasil ditambahkan")
                    st.rerun()
            else:
                st.warning("⚠️ NIK sudah terdaftar")
        else:
            st.error("❌ NIK harus 16 digit angka!")

st.markdown("---")

if valid_niks:
    st.write(f"**Total NIK terdaftar: {len(valid_niks)}**")
    
    for nik in valid_niks:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"📌 `{nik}`")
        with col2:
            responses = github.get_user_responses(nik)
            current_year = datetime.now().year
            used = len([r for r in responses if r.get('year') == current_year])
            max_q = settings.get('max_quota_per_year', 10)
            st.caption(f"Kuota: {used}/{max_q}")
        with col3:
            if st.button("🗑️ Hapus", key=f"del_nik_{nik}"):
                if github.remove_valid_nik(nik):
                    st.success(f"✅ NIK {nik} dihapus")
                    st.rerun()
else:
    st.info("Belum ada NIK terdaftar")

st.markdown('</div>', unsafe_allow_html=True)

# ========== INFORMASI SISTEM ==========
st.markdown('<div class="settings-card">', unsafe_allow_html=True)
st.markdown('<div class="settings-title">ℹ️ Informasi Sistem</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

responses = github.get_all_responses()
questions = github.get_all_questions()

with col1:
    st.metric("Total Partisipasi", len(responses))
with col2:
    st.metric("Total Warga", len(set([r['nik'] for r in responses])))
with col3:
    st.metric("Total Soal", len(questions))

st.markdown('</div>', unsafe_allow_html=True)