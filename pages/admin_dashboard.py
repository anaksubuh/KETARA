import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime

# Konfigurasi halaman - HARUS PERTAMA
st.set_page_config(
    page_title="Admin Dashboard - Kota Magelang",
    page_icon="👨‍💼",
    layout="wide",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time

# Inisialisasi session
init_session_state()
check_token_from_url()
require_auth()

# Sembunyikan elemen bawaan
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar untuk admin
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
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
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

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

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🏙️ Dashboard Admin</h1>
            <p>Selamat datang di panel administrasi Sistem Aspirasi & Polling Kota Magelang</p>
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
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Belum ada data partisipasi")

# ========== AKTIVITAS TERBARU ==========
st.markdown("---")
st.subheader("📋 Aktivitas Partisipasi Terbaru")

if responses:
    recent = sorted(responses, key=lambda x: x.get('submitted_at', ''), reverse=True)[:10]
    for r in recent:
        with st.expander(f"📅 {r.get('submitted_at', '')[:10]} - NIK: {r.get('nik', 'Unknown')}"):
            for ans in r.get('responses', []):
                if ans.get('answer'):
                    st.write(f"**{ans.get('question', '')}**")
                    st.write(f"Jawaban: {ans.get('answer', '')}")
                    st.write("---")
else:
    st.info("Belum ada aktivitas")

# Footer
st.markdown("---")
st.caption(f"© 2024 Sistem Aspirasi & Polling - Kota Magelang")