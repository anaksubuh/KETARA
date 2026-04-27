import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="Kelola Soal", page_icon="📝", layout="wide")
sys.path.append(str(Path(__file__).parent.parent))
from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

# SIDEBAR SAMA (tanpa CSS)
with st.sidebar:
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

st.title("📝 Kelola Soal Polling")
github = GitHubAPI()
tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal"])

with tab1:
    questions = github.get_all_questions()
    if not questions:
        st.info("Belum ada soal.")
    else:
        for q in questions:
            col1, col2, col3, col4 = st.columns([5,1,1,1])
            with col1:
                status = "🟢 Aktif" if q.get('is_active') else "🔴 Nonaktif"
                st.markdown(f"**{q['question']}**  \n{q['option_left']} vs {q['option_right']}  \nStatus: {status}")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{q['id']}"):
                    st.session_state.edit_qid = q['id']
                    st.rerun()
            with col3:
                new = not q.get('is_active', True)
                label = "Aktifkan" if new else "Nonaktifkan"
                if st.button(label, key=f"toggle_{q['id']}"):
                    if github.update_question_status(q['id'], new):
                        st.rerun()
            with col4:
                if st.button("🗑️ Hapus", key=f"del_{q['id']}"):
                    if github.delete_question(q['id']):
                        st.rerun()
            st.markdown("---")
        
        if 'edit_qid' in st.session_state:
            qid = st.session_state.edit_qid
            q = next((q for q in github.get_all_questions() if q['id'] == qid), None)
            if q:
                st.subheader(f"Edit Soal ID {qid}")
                with st.form("edit_form"):
                    new_q = st.text_area("Pertanyaan", value=q['question'])
                    colL, colR = st.columns(2)
                    with colL:
                        new_left = st.text_input("Opsi Kiri", value=q['option_left'])
                    with colR:
                        new_right = st.text_input("Opsi Kanan", value=q['option_right'])
                    new_active = st.checkbox("Aktif", value=q.get('is_active', True))
                    if st.form_submit_button("💾 Simpan"):
                        if new_q and new_left and new_right:
                            if github.update_question(qid, new_q, new_left, new_right, new_active):
                                del st.session_state.edit_qid
                                st.rerun()
                            else:
                                st.error("Gagal update")
                if st.button("❌ Batal"):
                    del st.session_state.edit_qid
                    st.rerun()

with tab2:
    with st.form("add_form"):
        q_text = st.text_area("Pertanyaan")
        col1, col2 = st.columns(2)
        with col1:
            opt_left = st.text_input("Opsi Kiri (Setuju)", value="✅ Setuju")
        with col2:
            opt_right = st.text_input("Opsi Kanan (Tidak Setuju)", value="❌ Tidak Setuju")
        aktif = st.checkbox("Aktifkan", value=True)
        if st.form_submit_button("➕ Tambah"):
            if q_text and opt_left and opt_right:
                if github.add_question(q_text, opt_left, opt_right, aktif):
                    st.success("Soal ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal tambah soal. Cek koneksi GitHub.")
            else:
                st.error("Harap isi semua field")