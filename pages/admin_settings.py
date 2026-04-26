import streamlit as st
import sys
from pathlib import Path
import re

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth import init_session_state, check_token_from_url, require_auth, logout
from modules.github_api import GitHubAPI

# Konfigurasi halaman
st.set_page_config(
    page_title="Admin - Pengaturan",
    page_icon="⚙️",
    layout="wide"
)

# Cek autentikasi
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
    .nik-item {
        background: #f5f5f5;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .info-text {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.caption(f"Role: **{st.session_state.role.upper()}**")
    st.markdown("---")
    
    menu = st.radio(
        "📋 **Menu Admin**",
        [
            "🏠 Dashboard",
            "📝 Kelola Soal",
            "📊 Lihat Jawaban",
            "⚙️ Pengaturan"
        ],
        index=3
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

# Redirect berdasarkan menu
if menu == "🏠 Dashboard":
    st.switch_page("pages/admin_dashboard.py")
elif menu == "📝 Kelola Soal":
    st.switch_page("pages/admin_questions.py")
elif menu == "📊 Lihat Jawaban":
    st.switch_page("pages/admin_responses.py")

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
            value=settings.get('max_quota_per_year', 10),
            help="Jumlah maksimal partisipasi per NIK dalam satu tahun"
        )
    
    with col2:
        system_name = st.text_input(
            "Nama Sistem",
            value=settings.get('system_name', 'Sistem Aspirasi & Polling'),
            help="Nama yang tampil di header aplikasi"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        allow_polling = st.checkbox(
            "Aktifkan Fitur Polling",
            value=settings.get('allow_polling', True),
            help="Jika nonaktif, halaman polling tidak akan muncul"
        )
    
    with col4:
        allow_aspirasi = st.checkbox(
            "Aktifkan Fitur Aspirasi",
            value=settings.get('allow_aspirasi', True),
            help="Jika nonaktif, form aspirasi tidak akan muncul"
        )
    
    submitted = st.form_submit_button("💾 Simpan Pengaturan", use_container_width=True, type="primary")
    
    if submitted:
        settings['max_quota_per_year'] = max_quota
        settings['system_name'] = system_name
        settings['allow_polling'] = allow_polling
        settings['allow_aspirasi'] = allow_aspirasi
        
        if github.save_settings(settings):
            st.success("✅ Pengaturan berhasil disimpan!")
            st.rerun()
        else:
            st.error("❌ Gagal menyimpan pengaturan")

st.markdown('</div>', unsafe_allow_html=True)

# ========== MANAJEMEN NIK VALID ==========
st.markdown('<div class="settings-card">', unsafe_allow_html=True)
st.markdown('<div class="settings-title">👥 Manajemen NIK Valid</div>', unsafe_allow_html=True)

st.write("Daftar NIK yang diizinkan untuk berpartisipasi:")

valid_niks = github.get_valid_niks()

# Form tambah NIK
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
                    st.error("❌ Gagal menambahkan NIK")
            else:
                st.warning("⚠️ NIK sudah terdaftar")
        else:
            st.error("❌ NIK harus 16 digit angka!")

st.markdown("---")

# Daftar NIK
if valid_niks:
    st.write(f"**Total NIK terdaftar: {len(valid_niks)}**")
    
    # Search NIK
    search_nik = st.text_input("🔍 Cari NIK", placeholder="Ketik NIK untuk mencari...")
    
    niks_to_show = [nik for nik in valid_niks if search_nik in nik] if search_nik else valid_niks
    
    for nik in niks_to_show:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"📌 `{nik}`")
        with col2:
            # Hitung kuota NIK ini
            responses = github.get_user_responses(nik)
            current_year = __import__('datetime').datetime.now().year
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

# ========== STATISTIK SISTEM ==========
st.markdown('<div class="settings-card">', unsafe_allow_html=True)
st.markdown('<div class="settings-title">📊 Statistik Sistem</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

responses = github.get_all_responses()
questions = github.get_all_questions()

with col1:
    st.metric("Total Partisipasi", len(responses))
with col2:
    st.metric("Total Warga", len(set([r['nik'] for r in responses])))
with col3:
    st.metric("Total Soal", len(questions))

# Partisipasi per bulan
if responses:
    import pandas as pd
    df = pd.DataFrame(responses)
    df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
    monthly = df.groupby('bulan').size()
    
    st.write("**Partisipasi per Bulan:**")
    for bulan, count in monthly.items():
        st.write(f"- {bulan}: {count} partisipasi")

st.markdown('</div>', unsafe_allow_html=True)

# ========== PANDUAN ==========
with st.expander("ℹ️ Panduan Pengaturan Sistem"):
    st.markdown("""
    **Panduan Pengaturan:**
    
    1. **Pengaturan Umum**
       - Kuota per Tahun: Batasi jumlah partisipasi per NIK
       - Nama Sistem: Ubah nama yang tampil di aplikasi
       - Aktif/Nonaktifkan fitur polling dan aspirasi
    
    2. **Manajemen NIK**
       - Tambah NIK baru untuk warga yang diizinkan
       - Hapus NIK jika diperlukan
       - Pantau kuota penggunaan per NIK
    
    3. **Tips Keamanan**
       - Jangan bagikan token admin kepada siapapun
       - Backup data secara berkala dengan download Excel
       - Gunakan NIK yang valid untuk mencegah spam
    
    4. **Penyimpanan Data**
       - Semua data tersimpan di GitHub repository
       - Bisa diakses kapan saja via GitHub API
       - Data aman dan tidak mudah hilang
    """)

# ========== RESET DATA (Opsional) ==========
with st.expander("⚠️ Zona Bahaya - Hapus Data"):
    st.warning("⚠️ **Perhatian!** Tindakan berikut tidak dapat dibatalkan.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Hapus Semua Jawaban", use_container_width=True):
            st.error("🚨 **KONFIRMASI!** Ketik 'DELETE' untuk menghapus semua data jawaban")
            confirm = st.text_input("Ketik DELETE untuk konfirmasi")
            if confirm == "DELETE":
                # Implementasi hapus data
                st.error("Fitur ini belum diimplementasikan untuk keamanan")
    
    with col2:
        if st.button("🔄 Reset Semua Pengaturan", use_container_width=True):
            st.error("🚨 Reset pengaturan ke default?")
            reset_confirm = st.text_input("Ketik RESET untuk konfirmasi")
            if reset_confirm == "RESET":
                default_settings = {
                    'system_name': 'Sistem Aspirasi & Polling',
                    'max_quota_per_year': 10,
                    'allow_polling': True,
                    'allow_aspirasi': True
                }
                github.save_settings(default_settings)
                st.success("Pengaturan direset ke default")
                st.rerun()