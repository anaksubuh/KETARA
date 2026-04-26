import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Aspirasi & Polling",
    page_icon="🏙️",
    layout="wide"
)

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI

st.set_page_config(
    page_title="User - Polling & Aspirasi",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
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
        transition: transform 0.3s;
    }
    .polling-card:hover {
        transform: translateY(-3px);
    }
    .polling-question {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
    }
    .option-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    .option-left, .option-right {
        flex: 1;
        padding: 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    .quota-info {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session
if 'nik' not in st.session_state:
    st.session_state.nik = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.markdown("""
<div class="hero-user">
    <h1>🏙️ Partisipasi Warga Kota Magelang</h1>
    <p>Sampaikan pendapat dan aspirasi Anda untuk kemajuan bersama</p>
</div>
""", unsafe_allow_html=True)

# Verifikasi NIK
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.nik:
        st.subheader("🔑 Verifikasi NIK")
        nik_input = st.text_input("Masukkan NIK (16 digit)", max_chars=16, 
                                   placeholder="Contoh: 1111111111111111")
        
        if st.button("Verifikasi", use_container_width=True):
            if len(nik_input) == 16 and nik_input.isdigit():
                github = GitHubAPI()
                valid_niks = github.get_valid_niks()
                
                if nik_input in valid_niks:
                    st.session_state.nik = nik_input
                    st.success(f"✅ NIK {nik_input} terverifikasi!")
                    st.rerun()
                else:
                    st.error("❌ NIK tidak terdaftar. Hubungi admin untuk pendaftaran.")
            else:
                st.error("❌ NIK harus 16 digit angka!")
    else:
        # Tampilkan info user
        github = GitHubAPI()
        quota = github.get_user_quota(st.session_state.nik)
        
        st.info(f"👤 **NIK:** {st.session_state.nik}")
        
        if quota['can_submit']:
            st.success(f"📊 **Sisa kuota tahun ini:** {quota['remaining']} dari {quota['max']}")
        else:
            st.error(f"⚠️ **Kuota habis!** Anda sudah menggunakan {quota['used']} dari {quota['max']} kali tahun ini.")
        
        if st.button("🔄 Ganti NIK", use_container_width=True):
            st.session_state.nik = None
            st.rerun()

# Tampilkan form polling jika NIK sudah terverifikasi dan belum submit
if st.session_state.nik and not st.session_state.submitted:
    github = GitHubAPI()
    quota = github.get_user_quota(st.session_state.nik)
    
    if quota['can_submit']:
        st.markdown("---")
        st.subheader("🗳️ Polling Pendapat")
        
        questions = github.get_all_questions()
        active_questions = [q for q in questions if q.get('is_active', True)]
        
        if not active_questions:
            st.warning("Belum ada polling yang tersedia saat ini.")
        else:
            with st.form("polling_form"):
                responses = []
                
                for q in active_questions:
                    st.markdown(f"""
                    <div class="polling-card">
                        <div class="polling-question">{q['question']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_left, col_right = st.columns(2)
                    with col_left:
                        left = st.radio(
                            f"Pilih untuk: {q['question']}",
                            [q['option_left']],
                            key=f"left_{q['id']}",
                            index=None,
                            label_visibility="collapsed"
                        )
                    with col_right:
                        right = st.radio(
                            f"Pilih untuk: {q['question']}",
                            [q['option_right']],
                            key=f"right_{q['id']}",
                            index=None,
                            label_visibility="collapsed"
                        )
                    
                    # Tentukan pilihan
                    selected = None
                    if left == q['option_left']:
                        selected = q['option_left']
                    elif right == q['option_right']:
                        selected = q['option_right']
                    
                    responses.append({
                        'question_id': q['id'],
                        'question': q['question'],
                        'answer': selected,
                        'value': 'setuju' if selected == q['option_left'] else ('tidak_setuju' if selected == q['option_right'] else None)
                    })
                
                st.markdown("---")
                st.subheader("💬 Aspirasi Umum")
                aspirasi = st.text_area(
                    "Sampaikan aspirasi, saran, atau masukan Anda untuk Kota Magelang",
                    height=120,
                    placeholder="Contoh: Mohon perbaikan infrastruktur jalan di Desa Sukamakmur..."
                )
                
                submitted = st.form_submit_button("📤 Kirim Partisipasi", use_container_width=True, type="primary")
                
                if submitted:
                    # Validasi semua polling terisi
                    all_answered = all(r['answer'] is not None for r in responses)
                    
                    if not all_answered:
                        st.error("❌ Silakan isi semua polling terlebih dahulu!")
                    elif len(aspirasi.strip()) < 5:
                        st.error("❌ Aspirasi minimal 5 karakter!")
                    else:
                        # Simpan ke GitHub
                        success = github.save_response(st.session_state.nik, responses)
                        
                        if success:
                            st.session_state.submitted = True
                            st.balloons()
                            st.success("✅ Terima kasih! Partisipasi Anda telah tersimpan.")
                            st.rerun()
                        else:
                            st.error("❌ Gagal menyimpan data. Silakan coba lagi.")
    else:
        st.error(f"⚠️ Maaf, kuota Anda sudah habis untuk tahun ini. Terima kasih atas partisipasinya!")

elif st.session_state.submitted:
    st.markdown("---")
    st.success("🎉 **Terima kasih telah berpartisipasi!**")
    st.info("Partisipasi Anda sangat berharga untuk kemajuan Kota Magelang.")
    
    if st.button("🏠 Kembali ke Beranda", use_container_width=True):
        st.session_state.nik = None
        st.session_state.submitted = False
        st.rerun()

# Footer
st.markdown("---")
st.caption(f"© 2024 Sistem Aspirasi & Polling - Kota Magelang | Partisipasi Masyarakat untuk Kemajuan Bersama")