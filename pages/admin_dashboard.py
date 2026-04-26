import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time, SESSION_DURATION_MINUTES

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin Dashboard - Kota Magelang",
    page_icon="👨‍💼",
    layout="wide"
)

# Inisialisasi session - SETELAH page_config
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
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        cursor: pointer;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
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
    .welcome-text {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="font-size: 3rem;">👨‍💼</div>
        <h3>{st.session_state.username}</h3>
        <p style="color: #667eea; font-weight: bold;">Administrator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tampilkan sisa waktu session
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        total_seconds = SESSION_DURATION_MINUTES * 60
        remaining_seconds = minutes * 60 + seconds
        progress = remaining_seconds / total_seconds if total_seconds > 0 else 1
        st.info(f"⏰ Session: **{minutes}m {seconds}s** lagi")
        st.progress(1 - progress)
    else:
        st.warning("⚠️ Session akan berakhir segera!")
    
    st.markdown("---")
    
    # Tombol Logout
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
    
    st.markdown("---")
    st.caption("📌 **Navigasi:** Gunakan menu di sidebar kiri untuk pindah halaman")

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🏙️ Dashboard Admin</h1>
            <p class="welcome-text">Selamat datang di panel administrasi Sistem Aspirasi & Polling Kota Magelang</p>
        </div>
        <div style="font-size: 3rem;">📊</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Inisialisasi GitHub API
github = GitHubAPI()

# Ambil data
questions = github.get_all_questions()
responses = github.get_all_responses()
valid_niks = github.get_valid_niks()

# ========== STATISTIK ==========
st.subheader("📊 Statistik Sistem")

col1, col2, col3, col4, col5 = st.columns(5)

total_responses = len(responses)
total_questions = len(questions)
active_questions = len([q for q in questions if q.get('is_active', True)])
unique_users = len(set([r.get('nik') for r in responses]))
total_niks = len(valid_niks)

with col1:
    st.metric("Total Partisipasi", total_responses)
with col2:
    st.metric("Total Soal", total_questions)
with col3:
    st.metric("Soal Aktif", active_questions)
with col4:
    st.metric("Warga Aktif", unique_users)
with col5:
    st.metric("NIK Terdaftar", total_niks)

# ========== GRAFIK PARTISIPASI ==========
st.markdown("---")
st.subheader("📈 Tren Partisipasi")

if responses:
    df = pd.DataFrame(responses)
    df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
    monthly_counts = df.groupby('bulan').size().reset_index(name='count')
    
    fig = px.bar(monthly_counts, x='bulan', y='count', 
                 title="Jumlah Partisipasi per Bulan",
                 labels={'bulan': 'Bulan', 'count': 'Jumlah Partisipasi'},
                 color='count', color_continuous_scale='Blues')
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Belum ada data partisipasi untuk ditampilkan")

# ========== AKTIVITAS TERBARU ==========
st.markdown("---")
st.subheader("📋 Aktivitas Partisipasi Terbaru")

if responses:
    recent = sorted(responses, key=lambda x: x.get('submitted_at', ''), reverse=True)[:10]
    
    for r in recent:
        submit_time = r.get('submitted_at', '')
        nik = r.get('nik', 'Unknown')
        tanggal = submit_time[:10] if submit_time else 'Unknown'
        jam = submit_time[11:19] if len(submit_time) > 10 else 'Unknown'
        
        with st.expander(f"📅 {tanggal} {jam} - 👤 NIK: {nik}"):
            for ans in r.get('responses', []):
                if ans.get('answer'):
                    st.write(f"**{ans.get('question', '')}**")
                    st.write(f"Jawaban: {ans.get('answer', '')}")
                    st.write("---")
else:
    st.info("Belum ada aktivitas partisipasi")

# ========== TOMBOL AKSI CEPAT ==========
st.markdown("---")
st.subheader("🚀 Aksi Cepat")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Kelola Soal", use_container_width=True, type="primary"):
        st.switch_page("pages/admin_questions.py")

with col2:
    if st.button("📊 Lihat Jawaban", use_container_width=True, type="primary"):
        st.switch_page("pages/admin_responses.py")

with col3:
    if st.button("⚙️ Pengaturan", use_container_width=True, type="primary"):
        st.switch_page("pages/admin_settings.py")

# Footer
st.markdown("---")
st.caption(f"© 2024 Sistem Aspirasi & Polling - Kota Magelang | Terakhir update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")