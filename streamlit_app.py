import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
from modules.github_api import GitHubAPI

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Sistem Aspirasi & Polling - Kota Magelang",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",  # Sidebar selalu terbuka
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# ==================== INISIALISASI SESSION STATE ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'admin_menu' not in st.session_state:
    st.session_state.admin_menu = "Dashboard"  # Default menu admin
if 'nik' not in st.session_state:
    st.session_state.nik = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# ==================== FUNGSI AUTH ====================
def verify_password(username, password):
    if username == "admin" and hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256("admin123".encode()).hexdigest():
        return True
    return False

def login(username, password):
    if verify_password(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.admin_menu = "Dashboard"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem;">🏙️</div>
        <h3>Kota Magelang</h3>
        <p>Sistem Aspirasi & Polling</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu untuk semua pengguna (User)
    st.markdown("### 🗳️ Polling Warga")
    if st.button("📝 Beranda (Polling)", use_container_width=True):
        st.session_state.admin_menu = None  # Kembali ke mode user
        st.rerun()
    
    # Jika sudah login sebagai admin, tampilkan menu admin
    if st.session_state.authenticated:
        st.markdown("---")
        st.markdown(f"### 👤 Admin: {st.session_state.username}")
        st.markdown("### ⚙️ Menu Admin")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.admin_menu = "Dashboard"
            st.rerun()
        if st.button("📝 Kelola Soal", use_container_width=True):
            st.session_state.admin_menu = "Kelola Soal"
            st.rerun()
        if st.button("📊 Lihat Jawaban", use_container_width=True):
            st.session_state.admin_menu = "Lihat Jawaban"
            st.rerun()
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.session_state.admin_menu = "Pengaturan"
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
            st.rerun()
    else:
        st.markdown("---")
        st.markdown("### 🔐 Admin Login")
        with st.form("login_form"):
            admin_user = st.text_input("Username", placeholder="admin")
            admin_pass = st.text_input("Password", type="password", placeholder="••••••")
            if st.form_submit_button("Login", use_container_width=True):
                if login(admin_user, admin_pass):
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah")
        st.caption("Demo: admin / admin123")

# ==================== MAIN CONTENT ====================
github = GitHubAPI()

# CSS tambahan untuk tampilan
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .polling-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOGIKA MENU ====================
# Jika admin sudah login dan memilih menu admin
if st.session_state.authenticated and st.session_state.admin_menu:
    
    # ---------- DASHBOARD ADMIN ----------
    if st.session_state.admin_menu == "Dashboard":
        st.markdown('<div class="main-header"><h1>📊 Dashboard Admin</h1><p>Selamat datang, Administrator!</p></div>', unsafe_allow_html=True)
        
        questions = github.get_all_questions()
        responses = github.get_all_responses()
        valid_niks = github.get_valid_niks()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Partisipasi", len(responses))
        col2.metric("Total Soal", len(questions))
        col3.metric("Soal Aktif", len([q for q in questions if q.get('is_active', True)]))
        col4.metric("Warga Aktif", len(set(r.get('nik') for r in responses)))
        col5.metric("NIK Terdaftar", len(valid_niks))
        
        if responses:
            df = pd.DataFrame(responses)
            df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
            monthly = df.groupby('bulan').size().reset_index(name='count')
            fig = px.bar(monthly, x='bulan', y='count', title="Partisipasi per Bulan")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data partisipasi")
    
    # ---------- KELOLA SOAL ----------
    elif st.session_state.admin_menu == "Kelola Soal":
        st.markdown('<div class="main-header"><h1>📝 Kelola Soal Polling</h1></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])
        
        with tab1:
            questions = github.get_all_questions()
            if not questions:
                st.info("Belum ada soal.")
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
                            if github.delete_question(q['id']):
                                st.success("Soal dihapus")
                                st.rerun()
                    st.markdown("---")
                
                # Form Edit
                if 'edit_qid' in st.session_state:
                    qid = st.session_state.edit_qid
                    q_edit = next((q for q in github.get_all_questions() if q['id'] == qid), None)
                    if q_edit:
                        st.subheader(f"✏️ Edit Soal ID {qid}")
                        with st.form("edit_form"):
                            new_q = st.text_area("Pertanyaan", value=q_edit['question'])
                            colL, colR = st.columns(2)
                            with colL:
                                new_left = st.text_input("Opsi Kiri (Setuju)", value=q_edit['option_left'])
                            with colR:
                                new_right = st.text_input("Opsi Kanan (Tidak Setuju)", value=q_edit['option_right'])
                            new_active = st.checkbox("Aktif", value=q_edit.get('is_active', True))
                            if st.form_submit_button("💾 Simpan"):
                                if new_q and new_left and new_right:
                                    if github.update_question(qid, new_q, new_left, new_right, new_active):
                                        st.success("Soal diupdate!")
                                        del st.session_state.edit_qid
                                        st.rerun()
                        if st.button("❌ Batal Edit"):
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
    
    # ---------- LIHAT JAWABAN ----------
    elif st.session_state.admin_menu == "Lihat Jawaban":
        st.markdown('<div class="main-header"><h1>📊 Data Jawaban & Aspirasi</h1></div>', unsafe_allow_html=True)
        responses = github.get_all_responses()
        if not responses:
            st.info("Belum ada partisipasi")
        else:
            col1, col2 = st.columns(2)
            with col1:
                niks = ['Semua'] + sorted(set(r['nik'] for r in responses))
                filter_nik = st.selectbox("Filter NIK", niks)
            with col2:
                dates = ['Semua'] + sorted(set(r['submitted_at'][:10] for r in responses), reverse=True)
                filter_date = st.selectbox("Filter Tanggal", dates)
            filtered = responses
            if filter_nik != 'Semua':
                filtered = [r for r in filtered if r['nik'] == filter_nik]
            if filter_date != 'Semua':
                filtered = [r for r in filtered if r['submitted_at'][:10] == filter_date]
            st.markdown(f"**Menampilkan {len(filtered)} dari {len(responses)} data**")
            for r in filtered:
                with st.expander(f"📅 {r['submitted_at']} - NIK: {r['nik']}"):
                    if r.get('aspirasi'):
                        st.markdown("**💬 Aspirasi:**")
                        st.write(r['aspirasi'])
                    st.markdown("**📋 Jawaban:**")
                    for ans in r['responses']:
                        if ans.get('answer'):
                            st.write(f"- {ans['question']}: **{ans['answer']}**")
    
    # ---------- PENGATURAN ----------
    elif st.session_state.admin_menu == "Pengaturan":
        st.markdown('<div class="main-header"><h1>⚙️ Pengaturan Sistem</h1></div>', unsafe_allow_html=True)
        tabA, tabB = st.tabs(["👥 Kelola NIK", "🎫 Kuota Partisipasi"])
        
        with tabA:
            st.subheader("Daftar NIK Terdaftar")
            valid_niks = github.get_valid_niks()
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Total: {len(valid_niks)} NIK**")
                if valid_niks:
                    st.dataframe(pd.DataFrame(valid_niks, columns=['NIK']), use_container_width=True)
            with col2:
                new_nik = st.text_input("Tambah NIK (16 digit)", max_chars=16)
                if st.button("➕ Tambah"):
                    if len(new_nik)==16 and new_nik.isdigit():
                        github.add_valid_nik(new_nik)
                        st.rerun()
                if valid_niks:
                    nik_del = st.selectbox("Hapus NIK", valid_niks)
                    if st.button("🗑️ Hapus"):
                        github.delete_valid_nik(nik_del)
                        st.rerun()
        
        with tabB:
            config = github.get_quota_config()
            max_q = config.get('max_per_year', 3)
            new_max = st.number_input("Maksimal partisipasi per tahun", min_value=1, value=max_q)
            if st.button("💾 Simpan Kuota"):
                github.update_quota_config(new_max)
                st.success("Tersimpan")
            if st.button("🔄 Reset Semua Kuota"):
                github.reset_all_quotas()
                st.success("Reset berhasil")

# ==================== HALAMAN USER (POLLING) ====================
else:
    # Tampilan user (polling)
    st.markdown('<div class="main-header"><h1>🏙️ Sugeng Rawuh Warga Kota Magelang</h1><p>Sampaikan pendapat dan aspirasi Anda</p></div>', unsafe_allow_html=True)
    
    # Verifikasi NIK
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
        st.info(f"👤 NIK: {st.session_state.nik} | Sisa kuota tahun ini: {quota['remaining']} dari {quota['max']}")
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
                        st.markdown(f"<div class='polling-card'><b>{q['question']}</b></div>", unsafe_allow_html=True)
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
                    aspirasi = st.text_area("💬 Aspirasi / Saran / Masukan", height=100)
                    if st.form_submit_button("📤 Kirim Partisipasi", type="primary", use_container_width=True):
                        if any(r['answer'] is None for r in responses):
                            st.error("Jawab semua polling terlebih dahulu")
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
                st.warning("Belum ada polling aktif saat ini.")
        elif not quota['can_submit']:
            st.error("⚠️ Maaf, kuota partisipasi Anda sudah habis untuk tahun ini.")
        elif st.session_state.submitted:
            st.success("✅ Terima kasih telah berpartisipasi!")
            if st.button("Kembali ke Beranda"):
                st.session_state.nik = None
                st.session_state.submitted = False
                st.rerun()
    
    st.markdown("---")
    st.caption(f"© 2025 Sistem Aspirasi & Polling - Kota Magelang")