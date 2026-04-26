import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import base64

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth import init_session_state, check_token_from_url, require_auth, logout
from modules.github_api import GitHubAPI

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
    .response-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
    .filter-bar {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
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
        index=2
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

# Redirect berdasarkan menu
if menu == "🏠 Dashboard":
    st.switch_page("pages/admin_dashboard.py")
elif menu == "📝 Kelola Soal":
    st.switch_page("pages/admin_questions.py")
elif menu == "⚙️ Pengaturan":
    st.switch_page("pages/admin_settings.py")

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

# Buat mapping question id ke question text
question_map = {q['id']: q for q in questions}

if not responses:
    st.info("📭 Belum ada data partisipasi dari warga")
    st.stop()

# ========== FILTER ==========
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
st.subheader("🔍 Filter Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Filter tanggal
    dates = sorted(set([r['submitted_at'][:10] for r in responses]), reverse=True)
    filter_date = st.selectbox("📅 Filter Tanggal", ["Semua"] + dates)

with col2:
    # Filter NIK
    niks = sorted(set([r['nik'] for r in responses]))
    filter_nik = st.selectbox("👤 Filter NIK", ["Semua"] + niks)

with col3:
    # Filter soal
    question_options = ["Semua"] + [f"{q['order']}. {q['question'][:40]}..." for q in questions]
    filter_question_idx = st.selectbox("📋 Filter Soal", range(len(question_options)), format_func=lambda x: question_options[x])
    filter_question = None if filter_question_idx == 0 else questions[filter_question_idx - 1]['id']

with col4:
    # Filter jawaban
    filter_answer = st.selectbox("🎯 Filter Jawaban", ["Semua", "Setuju", "Tidak Setuju"])

st.markdown('</div>', unsafe_allow_html=True)

# ========== TERAPKAN FILTER ==========
filtered_responses = responses.copy()

if filter_date != "Semua":
    filtered_responses = [r for r in filtered_responses if r['submitted_at'][:10] == filter_date]

if filter_nik != "Semua":
    filtered_responses = [r for r in filtered_responses if r['nik'] == filter_nik]

if filter_question:
    filtered_responses = [
        r for r in filtered_responses 
        if any(ans.get('question_id') == filter_question for ans in r.get('responses', []))
    ]

if filter_answer != "Semua":
    filtered_responses = [
        r for r in filtered_responses
        if any(
            (filter_answer == "Setuju" and ans.get('answer') and "setuju" in ans['answer'].lower()) or
            (filter_answer == "Tidak Setuju" and ans.get('answer') and "tidak" in ans['answer'].lower())
            for ans in r.get('responses', [])
        )
    ]

# ========== STATISTIK CARD ==========
st.markdown("---")
st.subheader("📈 Statistik")

col1, col2, col3, col4 = st.columns(4)

total_responses = len(filtered_responses)
total_participants = len(set([r['nik'] for r in filtered_responses]))
total_answers = sum(len(r.get('responses', [])) for r in filtered_responses)

# Hitung setuju vs tidak setuju
setuju_count = 0
tidak_count = 0
for r in filtered_responses:
    for ans in r.get('responses', []):
        if ans.get('answer'):
            if "setuju" in ans['answer'].lower():
                setuju_count += 1
            elif "tidak" in ans['answer'].lower():
                tidak_count += 1

with col1:
    st.metric("📊 Total Partisipasi", total_responses)
with col2:
    st.metric("👥 Warga Berpartisipasi", total_participants)
with col3:
    st.metric("✅ Total Setuju", setuju_count)
with col4:
    st.metric("❌ Total Tidak Setuju", tidak_count)

if total_answers > 0:
    st.progress(setuju_count/total_answers, text=f"Persentase Setuju: {int(setuju_count/total_answers*100)}%")

# ========== GRAFIK ==========
st.markdown("---")
st.subheader("📊 Visualisasi Data")

# Pie chart distribusi jawaban
if setuju_count > 0 or tidak_count > 0:
    fig_pie = px.pie(
        values=[setuju_count, tidak_count],
        names=['Setuju', 'Tidak Setuju'],
        title="Distribusi Jawaban Keseluruhan",
        color_discrete_sequence=['#4caf50', '#f44336']
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# Bar chart per soal
st.subheader("📊 Jawaban per Soal")
soal_stats = []

for q in questions:
    q_setuju = 0
    q_tidak = 0
    for r in filtered_responses:
        for ans in r.get('responses', []):
            if ans.get('question_id') == q['id']:
                if ans.get('answer') == q['option_left']:
                    q_setuju += 1
                elif ans.get('answer') == q['option_right']:
                    q_tidak += 1
    if q_setuju > 0 or q_tidak > 0:
        soal_stats.append({
            'Soal': q['question'][:50],
            'Setuju': q_setuju,
            'Tidak Setuju': q_tidak
        })

if soal_stats:
    df_stats = pd.DataFrame(soal_stats)
    fig_bar = px.bar(
        df_stats.melt(id_vars=['Soal'], value_vars=['Setuju', 'Tidak Setuju'], 
                      var_name='Jawaban', value_name='Jumlah'),
        x='Soal', y='Jumlah', color='Jawaban', barmode='group',
        title="Perbandingan Jawaban per Soal",
        color_discrete_map={'Setuju': '#4caf50', 'Tidak Setuju': '#f44336'}
    )
    fig_bar.update_layout(height=450, xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# ========== EKSPOR EXCEL ==========
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
                'ID Soal': ans.get('question_id', ''),
                'Soal': ans.get('question', ''),
                'Jawaban': ans.get('answer', ''),
                'Nilai': 'Setuju' if 'setuju' in ans.get('answer', '').lower() else 'Tidak Setuju'
            })

if export_data:
    df_export = pd.DataFrame(export_data)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.write(f"**📊 Data siap diekspor:** {len(df_export)} baris")
    
    with col2:
        # Download as CSV
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"data_partisipasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Download as Excel
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

# Tampilkan toggle untuk mode tampilan
view_mode = st.radio("Mode Tampilan", ["Ringkas", "Detail"], horizontal=True)

if view_mode == "Ringkas":
    # Tampilan ringkas dalam tabel
    table_data = []
    for r in filtered_responses[:100]:  # Batasi 100 untuk performa
        for ans in r.get('responses', []):
            if ans.get('answer'):
                table_data.append({
                    'Tanggal': r['submitted_at'][:10],
                    'NIK': r['nik'],
                    'Soal': ans.get('question', '')[:50],
                    'Jawaban': ans.get('answer', '')
                })
    
    if table_data:
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, height=400)
    else:
        st.info("Tidak ada data untuk ditampilkan")
else:
    # Tampilan detail per partisipasi
    for r in filtered_responses[:50]:  # Batasi 50 untuk performa
        with st.expander(f"📅 {r['submitted_at'][:10]} - NIK: {r['nik']}"):
            for ans in r.get('responses', []):
                if ans.get('answer'):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**{ans.get('question', '')}**")
                    with col_b:
                        answer_class = "answer-setuju" if "setuju" in ans['answer'].lower() else "answer-tidak"
                        st.markdown(f'<span class="{answer_class}">{ans["answer"]}</span>', unsafe_allow_html=True)
                    st.write("---")
            st.caption(f"🕐 Submit: {r['submitted_at']}")

# Informasi footer
st.markdown("---")
st.caption(f"📊 Menampilkan {len(filtered_responses)} dari {len(responses)} total partisipasi")