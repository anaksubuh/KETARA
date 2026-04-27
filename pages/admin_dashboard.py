import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin Dashboard - Kota Magelang",
    page_icon="📊",
    layout="wide",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

# Inisialisasi session
init_session_state()
require_auth()

# CSS untuk memastikan sidebar muncul
st.markdown("""
<style>
    /* Sembunyikan elemen bawaan */
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
    
    /* PASTIKAN SIDEBAR MUNCUL */
    [data-testid="stSidebar"] { 
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        min-width: 300px !important;
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2);
        width: 100%;
        text-align: left;
        justify-content: flex-start;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2);
        color: white !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Styling tambahan */
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo/Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">🏙️</div>
        <h3>Kota Magelang</h3>
        <p style="font-size: 0.8rem; opacity: 0.8;">Sistem Aspirasi & Polling</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Info User
    st.markdown(f"""
    <div style="padding: 0.5rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">👤</span>
            <div>
                <strong>{st.session_state.get('username', 'Admin')}</strong><br>
                <span style="font-size: 0.7rem; opacity: 0.7;">Administrator</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu Navigasi - MENGGUNAKAN SESSION STATE, BUKAN SWITCH_PAGE
    st.markdown("### 📋 Menu Admin")
    
    # Simpan menu aktif di session state
    if 'admin_menu' not in st.session_state:
        st.session_state.admin_menu = 'dashboard'
    
    # Button menu dengan callback
    col1, col2 = st.columns([1, 3])
    
    if st.button("🏠 Dashboard", use_container_width=True, key="menu_dashboard"):
        st.session_state.admin_menu = 'dashboard'
        st.rerun()
    
    if st.button("📝 Kelola Soal", use_container_width=True, key="menu_questions"):
        st.session_state.admin_menu = 'questions'
        st.rerun()
    
    if st.button("📊 Lihat Jawaban", use_container_width=True, key="menu_responses"):
        st.session_state.admin_menu = 'responses'
        st.rerun()
    
    if st.button("⚙️ Pengaturan", use_container_width=True, key="menu_settings"):
        st.session_state.admin_menu = 'settings'
        st.rerun()
    
    st.markdown("---")
    
    # Session info
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2024 Kota Magelang")

# ==================== MAIN CONTENT ====================
# Routing berdasarkan menu yang dipilih
if st.session_state.admin_menu == 'dashboard':
    # TAMPILKAN DASHBOARD
    st.markdown("""
    <div class="admin-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>📊 Dashboard Admin</h1>
                <p>Selamat datang, Administrator! Kelola sistem aspirasi & polling Kota Magelang</p>
            </div>
            <div style="font-size: 3rem;">🏙️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    github = GitHubAPI()
    questions = github.get_all_questions()
    responses = github.get_all_responses()
    valid_niks = github.get_valid_niks()
    
    # Statistik
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Partisipasi", len(responses))
    with col2:
        st.metric("Total Soal", len(questions))
    with col3:
        active = len([q for q in questions if q.get('is_active', True)])
        st.metric("Soal Aktif", active)
    with col4:
        unique_users = len(set([r.get('nik') for r in responses]))
        st.metric("Warga Aktif", unique_users)
    with col5:
        st.metric("NIK Terdaftar", len(valid_niks))
    
    # Grafik
    st.markdown("---")
    st.subheader("📈 Tren Partisipasi per Bulan")
    
    if responses:
        df = pd.DataFrame(responses)
        df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
        monthly_counts = df.groupby('bulan').size().reset_index(name='count')
        
        fig = px.bar(monthly_counts, x='bulan', y='count',
                     title="Jumlah Partisipasi per Bulan",
                     labels={'bulan': 'Bulan', 'count': 'Jumlah'},
                     color='count', color_continuous_scale='Blues')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Belum ada data partisipasi")
    
    # Aktivitas terbaru
    st.markdown("---")
    st.subheader("📋 Aktivitas Partisipasi Terbaru")
    
    if responses:
        recent = sorted(responses, key=lambda x: x.get('submitted_at', ''), reverse=True)[:5]
        for r in recent:
            with st.expander(f"📅 {r.get('submitted_at', '')[:10]} - NIK: {r.get('nik', 'Unknown')}"):
                for ans in r.get('responses', []):
                    if ans.get('answer'):
                        st.write(f"**{ans.get('question', '')}**")
                        st.write(f"Jawaban: {ans.get('answer', '')}")
                        st.write("---")
    else:
        st.info("📭 Belum ada aktivitas")

elif st.session_state.admin_menu == 'questions':
    # TAMPILKAN HALAMAN KELOLA SOAL
    st.title("📝 Kelola Soal Polling")
    st.markdown("Buat, edit, dan atur status soal polling untuk warga Kota Magelang")
    
    github = GitHubAPI()
    
    tab1, tab2 = st.tabs(["📋 Daftar Soal", "➕ Tambah Soal Baru"])
    
    with tab1:
        questions = github.get_all_questions()
        
        if not questions:
            st.info("Belum ada soal. Silakan tambah soal baru di tab 'Tambah Soal Baru'")
        else:
            for q in questions:
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                    status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
                    st.markdown(f"""
                    **❓ {q['question']}**  
                    📊 Opsi: {q['option_left']} vs {q['option_right']}  
                    🏷️ Status: {status}
                    """)
                with col2:
                    new_status = not q.get('is_active', True)
                    status_text = "Aktifkan" if new_status else "Nonaktifkan"
                    if st.button(f"{status_text}", key=f"toggle_{q['id']}"):
                        github.update_question_status(q['id'], new_status)
                        st.rerun()
                with col3:
                    if st.button(f"🗑️ Hapus", key=f"delete_{q['id']}"):
                        if github.delete_question(q['id']):
                            st.success("Soal berhasil dihapus!")
                            st.rerun()
                st.markdown("---")
    
    with tab2:
        with st.form("add_question_form"):
            st.subheader("Form Tambah Soal Baru")
            
            question_text = st.text_area("Soal / Pertanyaan", placeholder="Contoh: Apakah Anda setuju dengan pembangunan taman kota?")
            
            col1, col2 = st.columns(2)
            with col1:
                option_left = st.text_input("Opsi Kiri (Setuju)", placeholder="Setuju")
            with col2:
                option_right = st.text_input("Opsi Kanan (Tidak Setuju)", placeholder="Tidak Setuju")
            
            is_active = st.checkbox("Aktifkan soal ini sekarang", value=True)
            
            if st.form_submit_button("Simpan Soal", use_container_width=True, type="primary"):
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
                        st.error("Gagal menambahkan soal!")

elif st.session_state.admin_menu == 'responses':
    # TAMPILKAN HALAMAN LIHAT JAWABAN
    st.title("📊 Data Jawaban & Aspirasi")
    st.markdown("Lihat, filter, dan export data partisipasi warga")
    
    github = GitHubAPI()
    responses = github.get_all_responses()
    
    if not responses:
        st.info("📭 Belum ada data partisipasi")
    else:
        col1, col2 = st.columns(2)
        with col1:
            niks = ['Semua'] + sorted(list(set([r.get('nik') for r in responses])))
            filter_nik = st.selectbox("Filter NIK", niks)
        
        with col2:
            dates = ['Semua'] + sorted(list(set([r.get('submitted_at', '')[:10] for r in responses])), reverse=True)
            filter_date = st.selectbox("Filter Tanggal", dates)
        
        filtered = responses
        if filter_nik != 'Semua':
            filtered = [r for r in filtered if r.get('nik') == filter_nik]
        if filter_date != 'Semua':
            filtered = [r for r in filtered if r.get('submitted_at', '')[:10] == filter_date]
        
        st.markdown(f"**Menampilkan {len(filtered)} dari {len(responses)} data**")
        
        for r in filtered:
            with st.expander(f"📅 {r.get('submitted_at')} - NIK: {r.get('nik')}"):
                st.markdown("**💬 Aspirasi:**")
                st.write(r.get('aspirasi', '-'))
                st.markdown("**📋 Jawaban Polling:**")
                for ans in r.get('responses', []):
                    if ans.get('answer'):
                        st.write(f"- {ans.get('question')}: **{ans.get('answer')}**")

elif st.session_state.admin_menu == 'settings':
    # TAMPILKAN HALAMAN PENGATURAN
    st.title("⚙️ Pengaturan Sistem")
    st.markdown("Kelola konfigurasi sistem, NIK terdaftar, dan kuota partisipasi")
    
    github = GitHubAPI()
    
    tab1, tab2 = st.tabs(["👥 Kelola NIK", "🎫 Kuota Partisipasi"])
    
    with tab1:
        st.subheader("Daftar NIK Terdaftar")
        valid_niks = github.get_valid_niks()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Total NIK terdaftar: {len(valid_niks)}**")
            if valid_niks:
                df_niks = pd.DataFrame(valid_niks, columns=['NIK'])
                st.dataframe(df_niks, use_container_width=True, height=300)
        
        with col2:
            st.markdown("### Tambah NIK")
            new_nik = st.text_input("Masukkan NIK (16 digit)", max_chars=16, key="new_nik")
            if st.button("➕ Tambah NIK", use_container_width=True):
                if len(new_nik) == 16 and new_nik.isdigit():
                    if github.add_valid_nik(new_nik):
                        st.success(f"NIK {new_nik} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.error("Gagal menambahkan NIK!")
                else:
                    st.error("NIK harus 16 digit angka!")
            
            st.markdown("### Hapus NIK")
            if valid_niks:
                nik_to_delete = st.selectbox("Pilih NIK", valid_niks)
                if st.button("🗑️ Hapus NIK", use_container_width=True):
                    if github.delete_valid_nik(nik_to_delete):
                        st.success(f"NIK {nik_to_delete} berhasil dihapus!")
                        st.rerun()
                    else:
                        st.error("Gagal menghapus NIK!")
    
    with tab2:
        st.subheader("Pengaturan Kuota Partisipasi")
        current_quota = github.get_quota_config()
        
        max_quota = st.number_input("Maksimal partisipasi per tahun", 
                                     min_value=1, max_value=100, 
                                     value=current_quota.get('max_per_year', 3))
        
        if st.button("💾 Simpan Kuota", use_container_width=True):
            if github.update_quota_config(max_quota):
                st.success("Pengaturan kuota berhasil disimpan!")
        
        if st.button("🔄 Reset Semua Kuota", use_container_width=True):
            if github.reset_all_quotas():
                st.success("Semua kuota berhasil direset!")

# Footer
st.markdown("---")
st.caption(f"© 2024 Sistem Aspirasi & Polling - Kota Magelang | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")