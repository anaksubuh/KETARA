import streamlit as st
import sys
from pathlib import Path

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

# CSS untuk sidebar dan tampilan admin
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
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2);
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem;">🏙️</div>
        <h3>Kota Magelang</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### 👤 {st.session_state.get('username', 'Admin')}")
    st.markdown("---")
    st.markdown("### 📋 Menu Admin")
    
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

# ==================== MAIN CONTENT ====================
st.title("📝 Kelola Soal Polling")
st.markdown("Buat, edit, hapus, dan atur status soal polling untuk warga Kota Magelang.")

github = GitHubAPI()

tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])

# ========== TAB 1: DAFTAR SOAL ==========
with tab1:
    questions = github.get_all_questions()
    
    if not questions:
        st.info("Belum ada soal. Silakan tambah soal baru di tab 'Tambah Soal Baru'")
    else:
        for q in questions:
            col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
            with col1:
                status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
                st.markdown(f"""
                **❓ {q['question']}**  
                📊 Opsi: {q['option_left']} vs {q['option_right']}  
                🏷️ Status: {status}
                """)
            with col2:
                if st.button("✏️ Edit", key=f"edit_{q['id']}"):
                    st.session_state.edit_qid = q['id']
                    st.rerun()
            with col3:
                new_status = not q.get('is_active', True)
                status_text = "Aktifkan" if new_status else "Nonaktifkan"
                if st.button(status_text, key=f"toggle_{q['id']}"):
                    if github.update_question_status(q['id'], new_status):
                        st.success(f"Soal berhasil {status_text.lower()}!")
                        st.rerun()
                    else:
                        st.error("Gagal mengubah status.")
            with col4:
                if st.button("🗑️ Hapus", key=f"delete_{q['id']}"):
                    if github.delete_question(q['id']):
                        st.success("Soal berhasil dihapus!")
                        st.rerun()
                    else:
                        st.error("Gagal menghapus soal.")
            st.markdown("---")
        
        # Form Edit Soal (muncul jika tombol Edit ditekan)
        if 'edit_qid' in st.session_state:
            qid = st.session_state.edit_qid
            # Ambil data soal yang akan diedit
            all_q = github.get_all_questions()
            q_to_edit = next((q for q in all_q if q['id'] == qid), None)
            
            if q_to_edit:
                st.markdown("---")
                st.subheader(f"✏️ Edit Soal ID: {qid}")
                with st.form("edit_question_form"):
                    edited_question = st.text_area("Pertanyaan", value=q_to_edit['question'])
                    col_left, col_right = st.columns(2)
                    with col_left:
                        edited_option_left = st.text_input("Opsi Kiri (Setuju)", value=q_to_edit['option_left'])
                    with col_right:
                        edited_option_right = st.text_input("Opsi Kanan (Tidak Setuju)", value=q_to_edit['option_right'])
                    edited_is_active = st.checkbox("Aktif", value=q_to_edit.get('is_active', True))
                    
                    if st.form_submit_button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
                        if not edited_question:
                            st.error("Pertanyaan harus diisi!")
                        elif not edited_option_left or not edited_option_right:
                            st.error("Kedua opsi harus diisi!")
                        else:
                            success = github.update_question(
                                qid, edited_question, edited_option_left, 
                                edited_option_right, edited_is_active
                            )
                            if success:
                                st.success("Soal berhasil diperbarui!")
                                del st.session_state.edit_qid
                                st.rerun()
                            else:
                                st.error("Gagal memperbarui soal. Coba lagi.")
                
                if st.button("❌ Batal Edit", use_container_width=True):
                    del st.session_state.edit_qid
                    st.rerun()

# ========== TAB 2: TAMBAH SOAL BARU ==========
with tab2:
    with st.form("add_question_form"):
        st.subheader("Form Tambah Soal Baru")
        
        question_text = st.text_area(
            "Soal / Pertanyaan", 
            placeholder="Contoh: Apakah Anda setuju dengan pembangunan taman kota baru?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            option_left = st.text_input("Opsi Kiri (Setuju)", value="✅ Setuju", placeholder="Setuju")
        with col2:
            option_right = st.text_input("Opsi Kanan (Tidak Setuju)", value="❌ Tidak Setuju", placeholder="Tidak Setuju")
        
        is_active = st.checkbox("Aktifkan soal ini sekarang", value=True)
        
        if st.form_submit_button("➕ Simpan Soal", use_container_width=True, type="primary"):
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
                    st.error("Gagal menambahkan soal. Periksa koneksi atau konfigurasi GitHub.")