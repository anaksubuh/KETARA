import streamlit as st
import sys
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Pengaturan - Admin",
    page_icon="⚙️",
    layout="wide",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

# CSS
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
    
    [data-testid="stSidebar"] { 
        display: block !important;
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .settings-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/white?text=Kota+Magelang", use_container_width=True)
    st.markdown(f"### 👤 {st.session_state.get('username', 'Admin')}")
    st.markdown("---")
    
    if st.button("🏠 Dashboard", use_container_width=True):
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
        st.rerun()

# Main content
st.title("⚙️ Pengaturan Sistem")
st.markdown("Kelola konfigurasi sistem, NIK terdaftar, dan kuota partisipasi")

github = GitHubAPI()

# Tab pengaturan
tab1, tab2, tab3 = st.tabs(["👥 Kelola NIK", "🎫 Kuota Partisipasi", "🔐 Admin Password"])

with tab1:
    st.subheader("Daftar NIK Terdaftar")
    
    valid_niks = github.get_valid_niks()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Total NIK terdaftar: {len(valid_niks)}**")
        
        if valid_niks:
            df_niks = pd.DataFrame(valid_niks, columns=['NIK'])
            st.dataframe(df_niks, use_container_width=True, height=300)
    
    with col2:
        st.markdown("### Tambah NIK")
        new_nik = st.text_input("Masukkan NIK (16 digit)", max_chars=16, key="new_nik")
        
        if st.button("➕ Tambah NIK", use_container_width=True):
            if len(new_nik) == 16 and new_nik.isdigit():
                if github.add_valid_nik(new_nik):
                    st.success(f"NIK {new_nik} berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal menambahkan NIK!")
            else:
                st.error("NIK harus 16 digit angka!")
        
        st.markdown("### Hapus NIK")
        nik_to_delete = st.selectbox("Pilih NIK", valid_niks if valid_niks else ['Tidak ada data'])
        
        if st.button("🗑️ Hapus NIK", use_container_width=True):
            if nik_to_delete != 'Tidak ada data':
                if github.delete_valid_nik(nik_to_delete):
                    st.success(f"NIK {nik_to_delete} berhasil dihapus!")
                    st.rerun()
                else:
                    st.error("Gagal menghapus NIK!")

with tab2:
    st.subheader("Pengaturan Kuota Partisipasi")
    
    current_quota = github.get_quota_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="settings-card">
            <h3>📊 Kuota Tahunan</h3>
            <p>Setiap NIK maksimal dapat berpartisipasi dalam periode tertentu</p>
        </div>
        """, unsafe_allow_html=True)
        
        max_quota = st.number_input("Maksimal partisipasi per tahun", 
                                     min_value=1, max_value=100, 
                                     value=current_quota.get('max_per_year', 3))
        
        if st.button("💾 Simpan Kuota", use_container_width=True):
            if github.update_quota_config(max_quota):
                st.success("Pengaturan kuota berhasil disimpan!")
    
    with col2:
        st.markdown("""
        <div class="settings-card">
            <h3>ℹ️ Informasi</h3>
            <p>• Kuota dihitung per tahun kalender</p>
            <p>• Reset otomatis setiap tahun</p>
            <p>• Admin dapat reset manual jika diperlukan</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Reset Semua Kuota", use_container_width=True, type="secondary"):
            if github.reset_all_quotas():
                st.success("Semua kuota berhasil direset!")

with tab3:
    st.subheader("Keamanan Admin")
    
    with st.form("change_password_form"):
        old_pass = st.text_input("Password Lama", type="password")
        new_pass = st.text_input("Password Baru", type="password")
        confirm_pass = st.text_input("Konfirmasi Password Baru", type="password")
        
        if st.form_submit_button("Ganti Password", use_container_width=True, type="primary"):
            if not old_pass or not new_pass:
                st.error("Semua field harus diisi!")
            elif new_pass != confirm_pass:
                st.error("Password baru tidak cocok!")
            elif len(new_pass) < 6:
                st.error("Password minimal 6 karakter!")
            else:
                if github.change_admin_password(old_pass, new_pass):
                    st.success("Password berhasil diubah! Silakan login ulang.")
                    logout()
                    st.rerun()
                else:
                    st.error("Password lama salah!")

st.markdown("---")
st.caption(f"© 2024 Sistem Aspirasi & Polling - Kota Magelang")