import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Kelola Soal - Admin",
    page_icon="📝",
    layout="wide",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

# CSS untuk sidebar dan main content
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
    .question-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
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
st.title("📝 Kelola Soal Polling")
st.markdown("Buat, edit, dan atur status soal polling untuk warga Kota Magelang")

github = GitHubAPI()

# Tab untuk list dan tambah soal
tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])

with tab1:
    questions = github.get_all_questions()
    
    if not questions:
        st.info("Belum ada soal. Silakan tambah soal baru di tab 'Tambah Soal Baru'")
    else:
        for q in questions:
            with st.container():
                col1, col2, col3 = st.columns([6, 1, 1])
                
                with col1:
                    status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
                    st.markdown(f"""
                    <div class="question-card">
                        <strong>❓ {q['question']}</strong><br>
                        📊 Opsi: {q['option_left']} vs {q['option_right']}<br>
                        🏷️ Status: {status}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    new_status = not q.get('is_active', True)
                    status_text = "Aktifkan" if new_status else "Nonaktifkan"
                    if st.button(f"{status_text}", key=f"toggle_{q['id']}"):
                        github.update_question_status(q['id'], new_status)
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Hapus", key=f"delete_{q['id']}"):
                        if github.delete_question(q['id']):
                            st.success("Soal berhasil dihapus!")
                            st.rerun()

with tab2:
    with st.form("add_question_form"):
        st.subheader("Form Tambah Soal Baru")
        
        question_text = st.text_area("Soal / Pertanyaan", placeholder="Contoh: Apakah Anda setuju dengan pembangunan taman kota?")
        
        col1, col2 = st.columns(2)
        with col1:
            option_left = st.text_input("Opsi Kiri (Setuju)", placeholder="Setuju")
        with col2:
            option_right = st.text_input("Opsi Kanan (Tidak Setuju)", placeholder="Tidak Setuju")
        
        is_active = st.checkbox("Aktifkan soal ini sekarang", value=True)
        
        if st.form_submit_button("Simpan Soal", use_container_width=True, type="primary"):
            if not question_text:
                st.error("Soal harus diisi!")
            elif not option_left or not option_right:
                st.error("Kedua opsi harus diisi!")
            else:
                success = github.add_question(question_text, option_left, option_right, is_active)
                if success:
                    st.success("Soal berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal menambahkan soal!")