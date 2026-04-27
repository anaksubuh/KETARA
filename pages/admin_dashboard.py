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

# Sidebar
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
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
        st.rerun()

# Main content
st.title("📝 Kelola Soal Polling")
st.markdown("Buat, edit, hapus, dan atur status soal polling.")

github = GitHubAPI()
tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])

with tab1:
    questions = github.get_all_questions()
    if not questions:
        st.info("Belum ada soal. Silakan tambah di tab sebelah.")
    else:
        for q in questions:
            col1, col2, col3, col4 = st.columns([5,1,1,1])
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
                        st.success(f"Soal {status_text.lower()}!")
                        st.rerun()
            with col4:
                if st.button("🗑️ Hapus", key=f"del_{q['id']}"):
                    if github.delete_question(q['id']):
                        st.success("Soal dihapus!")
                        st.rerun()
            st.markdown("---")
        
        # Form edit
        if 'edit_qid' in st.session_state:
            qid = st.session_state.edit_qid
            all_q = github.get_all_questions()
            q_edit = next((q for q in all_q if q['id'] == qid), None)
            if q_edit:
                st.markdown("---")
                st.subheader(f"✏️ Edit Soal ID {qid}")
                with st.form("edit_form"):
                    new_q = st.text_area("Pertanyaan", value=q_edit['question'])
                    colL, colR = st.columns(2)
                    with colL:
                        new_left = st.text_input("Opsi Kiri (Setuju)", value=q_edit['option_left'])
                    with colR:
                        new_right = st.text_input("Opsi Kanan (Tidak Setuju)", value=q_edit['option_right'])
                    new_active = st.checkbox("Aktif", value=q_edit.get('is_active', True))
                    if st.form_submit_button("💾 Simpan", type="primary"):
                        if new_q and new_left and new_right:
                            if github.update_question(qid, new_q, new_left, new_right, new_active):
                                st.success("Soal diupdate!")
                                del st.session_state.edit_qid
                                st.rerun()
                            else:
                                st.error("Gagal update")
                        else:
                            st.error("Semua field wajib diisi")
                if st.button("❌ Batal Edit"):
                    del st.session_state.edit_qid
                    st.rerun()

with tab2:
    with st.form("add_form"):
        q_text = st.text_area("Pertanyaan", placeholder="Contoh: Apakah Anda setuju dengan ...")
        col1, col2 = st.columns(2)
        with col1:
            opt_left = st.text_input("Opsi Kiri (Setuju)", value="✅ Setuju")
        with col2:
            opt_right = st.text_input("Opsi Kanan (Tidak Setuju)", value="❌ Tidak Setuju")
        is_active = st.checkbox("Aktifkan sekarang", value=True)
        if st.form_submit_button("➕ Tambah Soal", type="primary"):
            if q_text and opt_left and opt_right:
                if github.add_question(q_text, opt_left, opt_right, is_active):
                    st.success("Soal ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal tambah soal")
            else:
                st.error("Harap isi semua field")