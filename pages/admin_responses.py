import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import io
import base64

sys.path.append(str(Path(__file__).parent.parent))

from modules.github_api import GitHubAPI
from modules.auth_simple import init_session_state, check_token_from_url, require_auth, logout, get_remaining_time, ensure_token_in_url

# Inisialisasi
init_session_state()

# Pastikan token di URL sebelum cek auth
ensure_token_in_url()

# Cek autentikasi
check_token_from_url()
require_auth()

# Konfigurasi halaman
st.set_page_config(
    page_title="Admin - Lihat Jawaban",
    page_icon="📊",
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
    .filter-bar {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .answer-setuju {
        background: #4caf50;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .answer-tidak {
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
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="font-size: 3rem;">📊</div>
        <h3>{st.session_state.username}</h3>
        <p style="color: #667eea; font-weight: bold;">Administrator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    minutes, seconds = get_remaining_time()
    if minutes > 0 or seconds > 0:
        st.info(f"⏰ Session: {minutes}m {seconds}s")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()
    
    st.markdown("---")
    st.caption("📌 Gunakan menu di sidebar kiri untuk navigasi")

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>📊 Laporan Jawaban Masyarakat</h1>
            <p>Lihat, filter, dan download data partisipasi warga</p>
        </div>
        <div style="font-size: 3rem;">📈</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Inisialisasi
github = GitHubAPI()
responses = github.get_all_responses()
questions = github.get_all_questions()

if not responses:
    st.info("📭 Belum ada data partisipasi dari warga")
    st.stop()

# ========== FILTER ==========
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
st.subheader("🔍 Filter Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    dates = sorted(set([r['submitted_at'][:10] for r in responses]), reverse=True)
    filter_date = st.selectbox("📅 Filter Tanggal", ["Semua"] + dates)

with col2:
    niks = sorted(set([r['nik'] for r in responses]))
    filter_nik = st.selectbox("👤 Filter NIK", ["Semua"] + niks)

with col3:
    question_options = ["Semua"] + [q['question'][:40] for q in questions]
    filter_question = st.selectbox("📋 Filter Soal", question_options)

with col4:
    filter_answer = st.selectbox("🎯 Filter Jawaban", ["Semua", "Setuju", "Tidak Setuju"])

st.markdown('</div>', unsafe_allow_html=True)

# ========== TERAPKAN FILTER ==========
filtered_responses = responses.copy()

if filter_date != "Semua":
    filtered_responses = [r for r in filtered_responses if r['submitted_at'][:10] == filter_date]

if filter_nik != "Semua":
    filtered_responses = [r for r in filtered_responses if r['nik'] == filter_nik]

if filter_question != "Semua":
    filtered_responses = [
        r for r in filtered_responses 
        if any(filter_question in ans.get('question', '') for ans in r.get('responses', []))
    ]

if filter_answer != "Semua":
    keyword = "setuju" if filter_answer == "Setuju" else "tidak"
    filtered_responses = [
        r for r in filtered_responses
        if any(keyword in ans.get('answer', '').lower() for ans in r.get('responses', []))
    ]

# ========== STATISTIK ==========
st.markdown("---")
st.subheader("📈 Statistik")

col1, col2, col3, col4 = st.columns(4)

total = len(filtered_responses)
unique_nik = len(set([r['nik'] for r in filtered_responses]))

# Hitung setuju/tidak
setuju = 0
tidak = 0
for r in filtered_responses:
    for ans in r.get('responses', []):
        if 'setuju' in ans.get('answer', '').lower():
            setuju += 1
        elif 'tidak' in ans.get('answer', '').lower():
            tidak += 1

with col1:
    st.metric("📊 Total Partisipasi", total)
with col2:
    st.metric("👥 Warga", unique_nik)
with col3:
    st.metric("✅ Setuju", setuju)
with col4:
    st.metric("❌ Tidak Setuju", tidak)

# ========== EKSPOR DATA ==========
st.markdown("---")
st.subheader("📥 Ekspor Data")

# Siapkan data untuk export
export_data = []
for r in filtered_responses:
    for ans in r.get('responses', []):
        if ans.get('answer'):
            export_data.append({
                'Tanggal': r['submitted_at'][:10],
                'Waktu': r['submitted_at'][11:19],
                'NIK': r['nik'],
                'Soal': ans.get('question', ''),
                'Jawaban': ans.get('answer', '')
            })

if export_data:
    df_export = pd.DataFrame(export_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"data_partisipasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='Partisipasi', index=False)
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"data_partisipasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ========== TABEL DATA ==========
st.markdown("---")
st.subheader("📋 Detail Partisipasi")

# Tampilkan data dalam tabel
table_data = []
for r in filtered_responses[:100]:
    for ans in r.get('responses', []):
        if ans.get('answer'):
            table_data.append({
                'Tanggal': r['submitted_at'][:10],
                'NIK': r['nik'],
                'Soal': ans.get('question', '')[:60],
                'Jawaban': ans.get('answer', '')
            })

if table_data:
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, height=400)
else:
    st.info("Tidak ada data untuk ditampilkan")

# Footer
st.markdown("---")
st.caption(f"Menampilkan {len(filtered_responses)} dari {len(responses)} total partisipasi")