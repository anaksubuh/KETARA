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

# Sembunyikan semua elemen bawaan
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    button[kind="header"] { display: none !important; }
    .main > div { padding-top: 0rem; }
    .stStatusWidget { display: none !important; }
    .admin-login-btn {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .admin-login-btn:hover { opacity: 0.9; transform: translateY(-2px); }
    .hero-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .polling-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .polling-question {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<a href="/admin_login" target="_self" class="admin-login-btn">🔐 Admin Login</a>', unsafe_allow_html=True)

st.markdown("""
<div class="hero-user">
    <h1>🏙️ Sugeng Rawuh Warga Kota Magelang</h1>
    <p>Sampaikan pendapat dan aspirasi Anda untuk kemajuan bersama</p>
</div>
""", unsafe_allow_html=True)

# Inisialisasi session
if 'nik' not in st.session_state:
    st.session_state.nik = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

github = GitHubAPI()

# Verifikasi NIK
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if not st.session_state.nik:
        st.subheader("🔑 Verifikasi NIK")
        nik_input = st.text_input("Masukkan NIK (16 digit)", max_chars=16, placeholder="16 digit angka")
        if st.button("Verifikasi", use_container_width=True):
            if len(nik_input) == 16 and nik_input.isdigit():
                valid_niks = github.get_valid_niks()
                if nik_input in valid_niks:
                    st.session_state.nik = nik_input
                    st.success(f"✅ NIK {nik_input} terverifikasi!")
                    st.rerun()
                else:
                    st.error("❌ NIK tidak terdaftar. Hubungi admin.")
            else:
                st.error("❌ NIK harus 16 digit angka")
    else:
        quota = github.get_user_quota(st.session_state.nik)
        st.info(f"👤 NIK: {st.session_state.nik}")
        if quota['can_submit']:
            st.success(f"📊 Sisa kuota: {quota['remaining']} dari {quota['max']} kali/tahun")
        else:
            st.error(f"⚠️ Kuota habis! Sudah {quota['used']} dari {quota['max']} kali.")
        if st.button("🔄 Ganti NIK", use_container_width=True):
            st.session_state.nik = None
            st.rerun()

# Form polling
if st.session_state.nik and not st.session_state.submitted:
    quota = github.get_user_quota(st.session_state.nik)
    if quota['can_submit']:
        questions = github.get_all_questions()
        active_questions = [q for q in questions if q.get('is_active', True)]
        if not active_questions:
            st.warning("Belum ada polling aktif.")
        else:
            with st.form("polling_form"):
                responses = []
                for q in active_questions:
                    st.markdown(f'<div class="polling-card"><div class="polling-question">{q["question"]}</div></div>', unsafe_allow_html=True)
                    # Radio button dengan opsi kiri dan kanan
                    answer = st.radio(
                        label="Pilih jawaban",
                        options=[q['option_left'], q['option_right']],
                        key=f"q_{q['id']}",
                        index=None,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    responses.append({
                        'question_id': q['id'],
                        'question': q['question'],
                        'answer': answer,
                        'value': 'setuju' if answer == q['option_left'] else ('tidak_setuju' if answer == q['option_right'] else None)
                    })
                
                st.markdown("---")
                aspirasi = st.text_area("💬 Aspirasi / Saran / Masukan", height=120, placeholder="Contoh: Mohon perbaikan jalan ...")
                
                submitted = st.form_submit_button("📤 Kirim Partisipasi", type="primary", use_container_width=True)
                if submitted:
                    all_answered = all(r['answer'] is not None for r in responses)
                    if not all_answered:
                        st.error("❌ Harap jawab semua polling terlebih dahulu.")
                    elif len(aspirasi.strip()) < 5:
                        st.error("❌ Aspirasi minimal 5 karakter.")
                    else:
                        # Simpan dengan aspirasi
                        success = github.save_response(st.session_state.nik, responses, aspirasi)
                        if success:
                            st.session_state.submitted = True
                            st.balloons()
                            st.success("✅ Terima kasih! Partisipasi Anda tersimpan.")
                            st.rerun()
                        else:
                            st.error("❌ Gagal menyimpan, coba lagi.")
    else:
        st.error("⚠️ Kuota partisipasi Anda sudah habis untuk tahun ini.")

elif st.session_state.submitted:
    st.markdown("---")
    st.success("🎉 Terima kasih telah berpartisipasi!")
    if st.button("🏠 Kembali ke Beranda", use_container_width=True):
        st.session_state.nik = None
        st.session_state.submitted = False
        st.rerun()

st.markdown("---")
st.caption("© 2025 Sistem Aspirasi & Polling - Kota Magelang")