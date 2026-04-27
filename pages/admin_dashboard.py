import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide", menu_items={'Get Help': None, 'Report a bug': None, 'About': None})
sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

# CSS sidebar
st.markdown("""
<style>
    header { display: none !important; }
    .stApp header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    .main > div { padding-top: 0rem; }
    [data-testid="stSidebar"] { display: block !important; background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stButton button { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
    [data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,0.2); }
    .admin-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 16px; color: white; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:1rem;"><div style="font-size:3rem;">🏙️</div><h3>Kota Magelang</h3></div>', unsafe_allow_html=True)
    st.markdown(f"### 👤 {st.session_state.get('username', 'Admin')}")
    st.markdown("---")
    if st.button("🏠 Dashboard", use_container_width=True): st.switch_page("pages/admin_dashboard.py")
    if st.button("📝 Kelola Soal", use_container_width=True): st.switch_page("pages/admin_questions.py")
    if st.button("📊 Lihat Jawaban", use_container_width=True): st.switch_page("pages/admin_responses.py")
    if st.button("⚙️ Pengaturan", use_container_width=True): st.switch_page("pages/admin_settings.py")
    st.markdown("---")
    mins, secs = get_remaining_time()
    if mins>0 or secs>0: st.info(f"⏰ Session: {mins}m {secs}s")
    if st.button("🚪 Logout", use_container_width=True, type="primary"): logout(); st.rerun()

st.markdown('<div class="admin-header"><h1>📊 Dashboard Admin</h1><p>Selamat datang, Administrator! Kelola sistem aspirasi & polling Kota Magelang</p></div>', unsafe_allow_html=True)

github = GitHubAPI()
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
    fig = px.bar(monthly, x='bulan', y='count', title="Partisipasi per Bulan", color='count', color_continuous_scale='Blues')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"© 2025 Sistem Aspirasi & Polling - Kota Magelang | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")