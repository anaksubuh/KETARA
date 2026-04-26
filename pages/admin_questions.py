import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI

from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout


# Konfigurasi halaman
st.set_page_config(
    page_title="Admin - Kelola Soal",
    page_icon="📝",
    layout="wide"
)

# Cek autentikasi
init_session_state()
check_token_from_url()
require_auth()

# Custom CSS
st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .question-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .question-number {
        font-size: 0.8rem;
        color: #667eea;
        font-weight: 600;
    }
    .question-text {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
        color: #333;
    }
    .question-options {
        display: flex;
        gap: 1rem;
        margin: 0.5rem 0;
    }
    .option-badge {
        background: #f0f0f0;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .status-active {
        background: #4caf50;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-inactive {
        background: #f44336;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.caption(f"Role: **{st.session_state.role.upper()}**")
    st.markdown("---")
    
    menu = st.radio(
        "📋 **Menu Admin**",
        [
            "🏠 Dashboard",
            "📝 Kelola Soal",
            "📊 Lihat Jawaban",
            "⚙️ Pengaturan"
        ],
        index=1
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

# Redirect berdasarkan menu
if menu == "🏠 Dashboard":
    st.switch_page("pages/admin_dashboard.py")
elif menu == "📊 Lihat Jawaban":
    st.switch_page("pages/admin_responses.py")
elif menu == "⚙️ Pengaturan":
    st.switch_page("pages/admin_settings.py")

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>📝 Kelola Soal Polling</h1>
            <p>Tambah, edit, atau hapus soal polling yang akan ditampilkan kepada warga</p>
        </div>
        <div style="font-size: 3rem;">📋</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Inisialisasi
github = GitHubAPI()

# Tombol tambah soal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("➕ Tambah Soal Baru", use_container_width=True, type="primary"):
        st.session_state.show_add_form = True

# Form tambah soal
if st.session_state.get('show_add_form', False):
    with st.expander("📝 Form Tambah Soal Baru", expanded=True):
        with st.form("add_question_form"):
            st.subheader("Detail Soal")
            
            question_text = st.text_area(
                "📌 Soal/Pertanyaan", 
                height=80, 
                placeholder="Contoh: 2 + 2 = 4",
                help="Tuliskan pertanyaan atau pernyataan yang akan dipolling"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                option_left = st.text_input(
                    "⬅️ Pilihan Kiri (Setuju)", 
                    value="✅ Setuju",
                    help="Teks yang muncul di tombol kiri (biasanya setuju)"
                )
            with col2:
                option_right = st.text_input(
                    "➡️ Pilihan Kanan (Tidak Setuju)", 
                    value="❌ Tidak Setuju",
                    help="Teks yang muncul di tombol kanan (biasanya tidak setuju)"
                )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                submitted = st.form_submit_button("💾 Simpan Soal", use_container_width=True, type="primary")
            with col_c:
                if st.form_submit_button("❌ Batal", use_container_width=True):
                    st.session_state.show_add_form = False
                    st.rerun()
            
            if submitted:
                if question_text.strip():
                    new_question = {
                        'question': question_text.strip(),
                        'option_left': option_left,
                        'option_right': option_right,
                        'is_active': True
                    }
                    if github.add_question(new_question):
                        st.success("✅ Soal berhasil ditambahkan!")
                        st.session_state.show_add_form = False
                        st.rerun()
                    else:
                        st.error("❌ Gagal menambahkan soal. Cek koneksi GitHub.")
                else:
                    st.warning("⚠️ Soal tidak boleh kosong!")

# Daftar Soal
st.markdown("---")
st.subheader("📋 Daftar Semua Soal")

questions = github.get_all_questions()

if not questions:
    st.info("Belum ada soal. Klik 'Tambah Soal Baru' untuk memulai.")
else:
    # Urutkan berdasarkan order
    questions_sorted = sorted(questions, key=lambda x: x.get('order', 0))
    
    for q in questions_sorted:
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <div class="question-number">Soal #{q.get('order', q['id'])} | ID: {q['id']}</div>
                <div class="question-text">{q['question']}</div>
                <div class="question-options">
                    <span class="option-badge">{q['option_left']}</span>
                    <span>↔️</span>
                    <span class="option-badge">{q['option_right']}</span>
                </div>
                <div style="margin-top: 10px;">
                    {'<span class="status-active">🟢 Aktif</span>' if q.get('is_active', True) else '<span class="status-inactive">🔴 Nonaktif</span>'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tombol aksi
            # Tombol aksi - PERBAIKAN UNTUK HAPUS SOAL
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                if st.button(f"✏️ Edit", key=f"edit_{q['id']}", use_container_width=True):
                    st.session_state[f"editing_{q['id']}"] = True

            with col2:
                if q.get('is_active', True):
                    if st.button(f"🔴 Nonaktifkan", key=f"deact_{q['id']}", use_container_width=True):
                        if github.toggle_question_active(q['id']):
                            st.success(f"Soal dinonaktifkan")
                            st.rerun()
                        else:
                            st.error("Gagal menonaktifkan soal")
                else:
                    if st.button(f"🟢 Aktifkan", key=f"act_{q['id']}", use_container_width=True):
                        if github.toggle_question_active(q['id']):
                            st.success(f"Soal diaktifkan")
                            st.rerun()
                        else:
                            st.error("Gagal mengaktifkan soal")

            with col3:
                if st.button(f"📊 Statistik", key=f"stats_{q['id']}", use_container_width=True):
                    st.session_state[f"stats_{q['id']}"] = True

            with col4:
                if st.button(f"🗑️ Hapus", key=f"del_{q['id']}", use_container_width=True):
                    st.session_state[f"confirm_del_{q['id']}"] = True

            # Konfirmasi Hapus - DIPISAH AGAR TIDAK BENTROK
            if st.session_state.get(f"confirm_del_{q['id']}", False):
                st.warning(f"⚠️ **Yakin ingin menghapus soal ini?**")
                st.write(f"**Soal:** {q['question'][:100]}")
                st.write("⚠️ Tindakan ini tidak dapat dibatalkan!")
                
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Ya, Hapus Permanen", key=f"confirm_yes_{q['id']}", use_container_width=True):
                        if github.delete_question(q['id']):
                            st.success("✅ Soal berhasil dihapus!")
                            # Hapus state konfirmasi
                            del st.session_state[f"confirm_del_{q['id']}"]
                            st.rerun()
                        else:
                            st.error("❌ Gagal menghapus soal")
                with col_no:
                    if st.button("❌ Batal", key=f"confirm_no_{q['id']}", use_container_width=True):
                        del st.session_state[f"confirm_del_{q['id']}"]
                        st.rerun()
            
            # Form Edit
            if st.session_state.get(f"editing_{q['id']}", False):
                st.markdown("---")
                st.subheader(f"✏️ Edit Soal #{q.get('order', q['id'])}")
                
                with st.form(key=f"edit_form_{q['id']}"):
                    new_question_text = st.text_area("Soal", value=q['question'], height=80)
                    
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        new_option_left = st.text_input("Pilihan Kiri", value=q['option_left'])
                    with col_e2:
                        new_option_right = st.text_input("Pilihan Kanan", value=q['option_right'])
                    
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if st.form_submit_button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
                            updated_question = {
                                'question': new_question_text,
                                'option_left': new_option_left,
                                'option_right': new_option_right,
                                'is_active': q.get('is_active', True),
                                'order': q.get('order', 0)
                            }
                            if github.update_question(q['id'], updated_question):
                                st.success("✅ Soal berhasil diupdate!")
                                st.session_state[f"editing_{q['id']}"] = False
                                st.rerun()
                            else:
                                st.error("❌ Gagal update soal")
                    with col_s2:
                        if st.form_submit_button("❌ Batal Edit", use_container_width=True):
                            st.session_state[f"editing_{q['id']}"] = False
                            st.rerun()
            
            # Statistik per soal
            if st.session_state.get(f"stats_{q['id']}", False):
                st.markdown("---")
                st.subheader(f"📊 Statistik Jawaban: {q['question'][:50]}...")
                
                responses = github.get_all_responses()
                
                # Hitung jawaban untuk soal ini
                setuju = 0
                tidak_setuju = 0
                total = 0
                
                for r in responses:
                    for ans in r.get('responses', []):
                        if ans.get('question_id') == q['id']:
                            total += 1
                            if ans.get('answer') == q['option_left']:
                                setuju += 1
                            elif ans.get('answer') == q['option_right']:
                                tidak_setuju += 1
                
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Total Jawaban", total)
                with col_s2:
                    st.metric(q['option_left'], setuju, delta=f"{int(setuju/total*100) if total>0 else 0}%")
                with col_s3:
                    st.metric(q['option_right'], tidak_setuju, delta=f"{int(tidak_setuju/total*100) if total>0 else 0}%")
                
                if total > 0:
                    st.progress(setuju/total, text=f"Persentase {q['option_left']}")
                
                if st.button("Tutup Statistik", key=f"close_stats_{q['id']}"):
                    st.session_state[f"stats_{q['id']}"] = False
                    st.rerun()
            
            st.markdown("---")

# Informasi tambahan
with st.expander("ℹ️ Panduan Kelola Soal"):
    st.markdown("""
    **Cara menggunakan halaman ini:**
    
    1. **Tambah Soal Baru**: Klik tombol "Tambah Soal Baru" lalu isi form yang muncul
    2. **Edit Soal**: Klik tombol "Edit" pada soal yang ingin diubah
    3. **Aktif/Nonaktifkan**: Gunakan tombol untuk menonaktifkan soal sementara tanpa menghapus
    4. **Lihat Statistik**: Klik "Statistik" untuk melihat jumlah jawaban per soal
    5. **Hapus Soal**: Klik "Hapus" dan konfirmasi untuk menghapus soal permanen
    
    **Tips:**
    - Soal yang dinonaktifkan tidak akan muncul di halaman user
    - Urutan soal akan diatur otomatis berdasarkan ID
    - Pastikan teks soal jelas dan mudah dipahami
    """)