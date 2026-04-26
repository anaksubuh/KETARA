import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import io

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time

st.set_page_config(
    page_title="Admin - Lihat Jawaban",
    page_icon="📊",
    layout="wide"
)

init_session_state()
check_token_from_url()
require_auth()

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

st.title("📊 Laporan Jawaban Masyarakat")

github = GitHubAPI()
responses = github.get_all_responses()
questions = github.get_all_questions()

if not responses:
    st.info("📭 Belum ada data partisipasi")
    st.stop()

# Filter
st.subheader("🔍 Filter Data")
col1, col2 = st.columns(2)

with col1:
    niks = sorted(set([r['nik'] for r in responses]))
    filter_nik = st.selectbox("Filter NIK", ["Semua"] + niks)

with col2:
    question_options = ["Semua"] + [q['question'][:50] for q in questions]
    filter_question = st.selectbox("Filter Soal", question_options)

# Apply filter
filtered = responses.copy()
if filter_nik != "Semua":
    filtered = [r for r in filtered if r['nik'] == filter_nik]
if filter_question != "Semua":
    filtered = [r for r in filtered if any(filter_question in ans.get('question', '') for ans in r.get('responses', []))]

# Statistik
st.markdown("---")
st.subheader("📈 Statistik")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Partisipasi", len(filtered))
with col2:
    st.metric("Warga", len(set([r['nik'] for r in filtered])))
with col3:
    total_answers = sum(len(r.get('responses', [])) for r in filtered)
    st.metric("Total Jawaban", total_answers)

# Export
st.markdown("---")
st.subheader("📥 Ekspor Data")

export_data = []
for r in filtered:
    for ans in r.get('responses', []):
        if ans.get('answer'):
            export_data.append({
                'Tanggal': r['submitted_at'][:10],
                'NIK': r['nik'],
                'Soal': ans.get('question', ''),
                'Jawaban': ans.get('answer', '')
            })

if export_data:
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, f"data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

# Tabel data
st.markdown("---")
st.subheader("📋 Detail Partisipasi")

table_data = []
for r in filtered[:100]:
    for ans in r.get('responses', []):
        if ans.get('answer'):
            table_data.append({
                'Tanggal': r['submitted_at'][:10],
                'NIK': r['nik'],
                'Soal': ans.get('question', '')[:60],
                'Jawaban': ans.get('answer', '')
            })

if table_data:
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

st.caption(f"Menampilkan {len(filtered)} dari {len(responses)} total")