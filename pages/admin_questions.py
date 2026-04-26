import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time

st.set_page_config(
    page_title="Admin - Kelola Soal",
    page_icon="📝",
    layout="wide"
)

# Tambahkan di setiap halaman admin setelah st.set_page_config
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    button[kind="header"] { display: none !important; }
    .main > div { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# Tambahkan tombol logout di sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        from modules.auth_simple import logout
        logout()
    st.markdown("---")
    st.caption("📌 Gunakan menu di sidebar kiri untuk navigasi")

init_session_state()
check_token_from_url()
require_auth()

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

st.title("📝 Kelola Soal Polling")

github = GitHubAPI()

# Tombol tambah
if st.button("➕ Tambah Soal Baru", use_container_width=True):
    st.session_state.show_add = not st.session_state.get('show_add', False)

# Form tambah
if st.session_state.get('show_add', False):
    with st.form("add_form"):
        soal = st.text_area("Soal", height=80, placeholder="Contoh: 2 + 2 = 4")
        col1, col2 = st.columns(2)
        with col1:
            kiri = st.text_input("Pilihan Kiri", value="✅ Setuju")
        with col2:
            kanan = st.text_input("Pilihan Kanan", value="❌ Tidak Setuju")
        
        if st.form_submit_button("💾 Simpan"):
            if soal.strip():
                new = {'question': soal.strip(), 'option_left': kiri, 'option_right': kanan, 'is_active': True}
                if github.add_question(new):
                    st.success("Berhasil!")
                    st.session_state.show_add = False
                    st.rerun()

st.markdown("---")
st.subheader("📋 Daftar Soal")

for q in github.get_all_questions():
    with st.container():
        st.markdown(f"**{q.get('order', q['id'])}. {q['question']}**")
        st.caption(f"{q['option_left']} | {q['option_right']}")
        
        status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
        st.caption(f"Status: {status}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Toggle Status", key=f"toggle_{q['id']}"):
                github.toggle_question_active(q['id'])
                st.rerun()
        with col2:
            if st.button("Edit", key=f"edit_{q['id']}"):
                st.session_state[f"edit_{q['id']}"] = True
        with col3:
            if st.button("Hapus", key=f"del_{q['id']}"):
                if github.delete_question(q['id']):
                    st.rerun()
        
        if st.session_state.get(f"edit_{q['id']}", False):
            with st.form(key=f"edit_{q['id']}"):
                edit_soal = st.text_area("Soal", value=q['question'])
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_kiri = st.text_input("Pilihan Kiri", value=q['option_left'])
                with col_e2:
                    edit_kanan = st.text_input("Pilihan Kanan", value=q['option_right'])
                
                if st.form_submit_button("Update"):
                    updated = {
                        'question': edit_soal,
                        'option_left': edit_kiri,
                        'option_right': edit_kanan,
                        'is_active': q.get('is_active', True)
                    }
                    if github.update_question(q['id'], updated):
                        st.session_state[f"edit_{q['id']}"] = False
                        st.rerun()
        
        st.markdown("---")