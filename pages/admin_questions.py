import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="Kelola Soal", page_icon="📝", layout="wide", menu_items={'Get Help': None, 'Report a bug': None, 'About': None})
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
    [data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,0.2); }
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

st.title("📝 Kelola Soal Polling")
st.markdown("Buat, edit, hapus, dan atur status soal polling.")

github = GitHubAPI()
tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])

with tab1:
    questions = github.get_all_questions()
    if not questions:
        st.info("Belum ada soal. Silakan tambah soal baru.")
    else:
        for q in questions:
            col1, col2, col3, col4 = st.columns([5,1,1,1])
            with col1:
                status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
                st.markdown(f"**❓ {q['question']}**  \n📊 {q['option_left']} vs {q['option_right']}  \n🏷️ {status}")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{q['id']}"):
                    st.session_state.edit_qid = q['id']
                    st.rerun()
            with col3:
                new_status = not q.get('is_active', True)
                label = "Aktifkan" if new_status else "Nonaktifkan"
                if st.button(label, key=f"toggle_{q['id']}"):
                    github.update_question_status(q['id'], new_status)
                    st.rerun()
            with col4:
                if st.button("🗑️ Hapus", key=f"del_{q['id']}"):
                    github.delete_question(q['id'])
                    st.rerun()
            st.markdown("---")

    if 'edit_qid' in st.session_state:
        qid = st.session_state.edit_qid
        q_to_edit = next((q for q in github.get_all_questions() if q['id'] == qid), None)
        if q_to_edit:
            st.markdown("---")
            st.subheader(f"✏️ Edit Soal ID {qid}")
            with st.form("edit_form"):
                new_question = st.text_area("Pertanyaan", value=q_to_edit['question'])
                colL, colR = st.columns(2)
                with colL: new_left = st.text_input("Opsi Kiri (Setuju)", value=q_to_edit['option_left'])
                with colR: new_right = st.text_input("Opsi Kanan (Tidak Setuju)", value=q_to_edit['option_right'])
                new_active = st.checkbox("Aktif", value=q_to_edit.get('is_active', True))
                if st.form_submit_button("💾 Simpan Perubahan"):
                    if new_question and new_left and new_right:
                        if github.update_question(qid, new_question, new_left, new_right, new_active):
                            st.success("Soal berhasil diupdate!")
                            del st.session_state.edit_qid
                            st.rerun()
                        else:
                            st.error("Gagal update")
                    else:
                        st.error("Semua field harus diisi")
            if st.button("❌ Batal Edit"):
                del st.session_state.edit_qid
                st.rerun()

with tab2:
    with st.form("add_form"):
        q_text = st.text_area("Pertanyaan", placeholder="Contoh: Apakah Anda setuju dengan pembangunan taman kota?")
        col1, col2 = st.columns(2)
        with col1: opt_left = st.text_input("Opsi Kiri (Setuju)", value="✅ Setuju")
        with col2: opt_right = st.text_input("Opsi Kanan (Tidak Setuju)", value="❌ Tidak Setuju")
        aktif = st.checkbox("Aktifkan sekarang", value=True)
        if st.form_submit_button("➕ Tambah Soal", type="primary"):
            if q_text and opt_left and opt_right:
                if github.add_question(q_text, opt_left, opt_right, aktif):
                    st.success("Soal ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal tambah soal")
            else:
                st.error("Harap isi semua field")