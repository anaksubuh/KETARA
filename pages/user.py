import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from modules.github_api import GitHubAPI

st.set_page_config(
    page_title="Polling & Aspirasi - Kota Magelang",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

st.markdown("""
<style>
    header, footer, .stApp header, [data-testid="stToolbar"], .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0; }
    .admin-login-btn {
        position: fixed; top: 10px; right: 10px; z-index: 999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 8px 16px; border-radius: 20px;
        text-decoration: none; font-weight: 600;
    }
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 20px; color: white; text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<a href="/admin_login" target="_self" class="admin-login-btn">🔐 Admin Login</a>', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏙️ Sugeng Rawuh Warga Kota Magelang</h1><p>Sampaikan pendapat dan aspirasi Anda</p></div>', unsafe_allow_html=True)

if 'nik' not in st.session_state:
    st.session_state.nik = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

github = GitHubAPI()

if not st.session_state.nik:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("🔑 Verifikasi NIK")
        nik_input = st.text_input("Masukkan NIK (16 digit)", max_chars=16)
        if st.button("Verifikasi", use_container_width=True):
            if len(nik_input)==16 and nik_input.isdigit():
                valid = github.get_valid_niks()
                if nik_input in valid:
                    st.session_state.nik = nik_input
                    st.rerun()
                else:
                    st.error("NIK tidak terdaftar")
            else:
                st.error("NIK harus 16 digit angka")
else:
    quota = github.get_user_quota(st.session_state.nik)
    st.info(f"👤 NIK: {st.session_state.nik} | Sisa kuota: {quota['remaining']}/{quota['max']}")
    if st.button("🔄 Ganti NIK"):
        st.session_state.nik = None
        st.rerun()
    
    if not st.session_state.submitted and quota['can_submit']:
        questions = github.get_all_questions()
        active_q = [q for q in questions if q.get('is_active', True)]
        if active_q:
            with st.form("polling_form"):
                responses = []
                for q in active_q:
                    st.markdown(f"**{q['question']}**")
                    ans = st.radio(
                        "Pilih jawaban",
                        options=[q['option_left'], q['option_right']],
                        key=f"q_{q['id']}",
                        index=None,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    responses.append({
                        'question_id': q['id'],
                        'question': q['question'],
                        'answer': ans,
                        'value': 'setuju' if ans == q['option_left'] else ('tidak_setuju' if ans == q['option_right'] else None)
                    })
                aspirasi = st.text_area("💬 Aspirasi", height=100)
                if st.form_submit_button("📤 Kirim", type="primary", use_container_width=True):
                    if any(r['answer'] is None for r in responses):
                        st.error("Jawab semua polling")
                    elif len(aspirasi.strip()) < 5:
                        st.error("Aspirasi minimal 5 karakter")
                    else:
                        if github.save_response(st.session_state.nik, responses, aspirasi):
                            st.session_state.submitted = True
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Gagal menyimpan")
        else:
            st.warning("Belum ada polling aktif")
    elif not quota['can_submit']:
        st.error("⚠️ Kuota tahun ini habis")
    elif st.session_state.submitted:
        st.success("✅ Terima kasih telah berpartisipasi!")
        if st.button("Kembali ke Beranda"):
            st.session_state.nik = None
            st.session_state.submitted = False
            st.rerun()

st.markdown("---")
st.caption("© 2025 Sistem Aspirasi & Polling - Kota Magelang")