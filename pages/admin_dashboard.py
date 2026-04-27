import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
sys.path.append(str(Path(__file__).parent.parent))
from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, require_auth, logout, get_remaining_time

init_session_state()
require_auth()

# SIDEBAR CUSTOM (TIDAK ADA CSS YANG MENGHILANGKAN)
with st.sidebar:
    st.markdown('<div style="text-align:center"><h2>🏙️ Kota Magelang</h2></div>', unsafe_allow_html=True)
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown("---")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
    if st.button("📝 Kelola Soal", use_container_width=True):
        st.switch_page("pages/admin_questions.py")
    if st.button("📋 Lihat Jawaban", use_container_width=True):
        st.switch_page("pages/admin_responses.py")
    if st.button("⚙️ Pengaturan", use_container_width=True):
        st.switch_page("pages/admin_settings.py")
    st.markdown("---")
    mins, secs = get_remaining_time()
    if mins or secs:
        st.info(f"⏰ {mins}m {secs}s")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
        st.rerun()

st.title("📊 Dashboard Admin")
github = GitHubAPI()
questions = github.get_all_questions()
responses = github.get_all_responses()
valid = github.get_valid_niks()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Partisipasi", len(responses))
col2.metric("Total Soal", len(questions))
col3.metric("Soal Aktif", len([q for q in questions if q.get('is_active')]))
col4.metric("NIK Terdaftar", len(valid))

if responses:
    df = pd.DataFrame(responses)
    df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
    fig = px.bar(df.groupby('bulan').size().reset_index(name='count'), x='bulan', y='count')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Belum ada data")

st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")