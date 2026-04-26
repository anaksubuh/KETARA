import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth import init_session_state, check_token_from_url, require_auth, logout
from modules.github_api import GitHubAPI

# Konfigurasi
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="👨‍💼",
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

# Header
st.markdown("""
<div class="admin-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>👨‍💼 Dashboard Admin</h1>
            <p>Kelola sistem polling dan aspirasi masyarakat</p>
        </div>
        <div style="font-size: 3rem;">🏙️</div>
    </div>
</div>
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
        index=0
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout()

# Inisialisasi
github = GitHubAPI()
questions = github.get_all_questions()
responses = github.get_all_responses()

if menu == "🏠 Dashboard":
    st.title("📊 Statistik Sistem")
    
    # Statistik cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Hitung statistik
    total_responses = len(responses)
    total_questions = len(questions)
    active_questions = len([q for q in questions if q.get('is_active', True)])
    unique_users = len(set([r.get('nik') for r in responses]))
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_responses}</div>
            <div class="stat-label">Total Partisipasi</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_questions}</div>
            <div class="stat-label">Total Soal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{active_questions}</div>
            <div class="stat-label">Soal Aktif</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{unique_users}</div>
            <div class="stat-label">Warga Berpartisipasi</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grafik partisipasi per bulan
    if responses:
        st.subheader("📈 Tren Partisipasi")
        
        # Parse dates
        df = pd.DataFrame(responses)
        df['tanggal'] = pd.to_datetime(df['submitted_at']).dt.date
        df['bulan'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m')
        
        monthly_counts = df.groupby('bulan').size().reset_index(name='count')
        
        fig = px.bar(monthly_counts, x='bulan', y='count', 
                     title="Jumlah Partisipasi per Bulan",
                     color='count', color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Grafik distribusi jawaban per soal
        st.subheader("📊 Distribusi Jawaban per Soal")
        
        # Kumpulkan semua jawaban
        all_answers = []
        for r in responses:
            for ans in r.get('responses', []):
                if ans.get('answer'):
                    all_answers.append({
                        'question': ans['question'][:50],
                        'answer': ans['answer']
                    })
        
        if all_answers:
            df_ans = pd.DataFrame(all_answers)
            questions_list = df_ans['question'].unique()
            
            selected_q = st.selectbox("Pilih Soal", questions_list)
            if selected_q:
                q_data = df_ans[df_ans['question'] == selected_q]
                counts = q_data['answer'].value_counts()
                
                fig2 = px.pie(values=counts.values, names=counts.index, 
                              title=f"Distribusi Jawaban: {selected_q}",
                              color_discrete_sequence=['#4caf50', '#f44336'])
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Belum ada data partisipasi")
    
    # Tabel recent responses
    st.markdown("---")
    st.subheader("📋 Partisipasi Terbaru")
    
    if responses:
        recent = sorted(responses, key=lambda x: x['submitted_at'], reverse=True)[:10]
        
        for r in recent:
            with st.expander(f"📅 {r['submitted_at'][:10]} - NIK: {r['nik']}"):
                for ans in r.get('responses', []):
                    if ans.get('answer'):
                        st.write(f"**{ans['question']}**")
                        st.write(f"Jawaban: {ans['answer']}")
                        st.write("---")
                st.caption(f"Submit: {r['submitted_at']}")
    else:
        st.info("Belum ada partisipasi")

elif menu == "📝 Kelola Soal":
    st.title("📝 Kelola Soal Polling")
    
    # Tombol tambah soal
    if st.button("➕ Tambah Soal Baru", use_container_width=True):
        st.session_state.show_add_form = True
    
    # Form tambah soal
    if st.session_state.get('show_add_form', False):
        with st.form("add_question_form"):
            st.subheader("Tambah Soal Baru")
            question_text = st.text_area("Soal", height=80, 
                                         placeholder="Contoh: 2 + 2 = 4")
            col1, col2 = st.columns(2)
            with col1:
                option_left = st.text_input("Pilihan Kiri (Setuju)", value="✅ Setuju")
            with col2:
                option_right = st.text_input("Pilihan Kanan (Tidak Setuju)", value="❌ Tidak Setuju")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("💾 Simpan", use_container_width=True)
            with col_b:
                if st.form_submit_button("❌ Batal", use_container_width=True):
                    st.session_state.show_add_form = False
                    st.rerun()
            
            if submitted and question_text.strip():
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
                    st.error("❌ Gagal menambahkan soal")
            elif submitted:
                st.warning("⚠️ Soal tidak boleh kosong!")
    
    # Daftar soal
    st.markdown("---")
    st.subheader("📋 Daftar Soal")
    
    for q in questions:
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            status = "🟢 Aktif" if q.get('is_active', True) else "🔴 Nonaktif"
            st.markdown(f"**{q['order']}. {q['question']}**")
            st.caption(f"{q['option_left']} | {q['option_right']} | Status: {status}")
        
        with col2:
            if q.get('is_active', True):
                if st.button("🔴 Nonaktifkan", key=f"deact_{q['id']}"):
                    github.toggle_question_active(q['id'])
                    st.rerun()
            else:
                if st.button("🟢 Aktifkan", key=f"act_{q['id']}"):
                    github.toggle_question_active(q['id'])
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Hapus", key=f"del_{q['id']}"):
                if github.delete_question(q['id']):
                    st.success("✅ Soal dihapus")
                    st.rerun()
        
        st.markdown("---")

elif menu == "📊 Lihat Jawaban":
    st.title("📊 Laporan Jawaban Masyarakat")
    
    if not responses:
        st.info("Belum ada data jawaban")
    else:
        # Export ke Excel
        if st.button("📥 Download Excel", use_container_width=True):
            # Buat dataframe
            rows = []
            for r in responses:
                for ans in r.get('responses', []):
                    if ans.get('answer'):
                        rows.append({
                            'Tanggal': r['submitted_at'][:10],
                            'NIK': r['nik'],
                            'Soal': ans['question'],
                            'Jawaban': ans['answer']
                        })
            
            if rows:
                df_export = pd.DataFrame(rows)
                excel_data = df_export.to_excel(index=False, engine='openpyxl')
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="data_partisipasi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.markdown("---")
        
        # Filter
        col1, col2 = st.columns(2)
        with col1:
            questions_list = ['Semua'] + [q['question'] for q in questions]
            filter_question = st.selectbox("Filter Berdasarkan Soal", questions_list)
        with col2:
            niks = list(set([r['nik'] for r in responses]))
            filter_nik = st.selectbox("Filter Berdasarkan NIK", ['Semua'] + niks)
        
        # Tampilkan data
        filtered = responses
        if filter_question != 'Semua':
            filtered = [r for r in filtered if any(a['question'] == filter_question for a in r.get('responses', []))]
        if filter_nik != 'Semua':
            filtered = [r for r in filtered if r['nik'] == filter_nik]
        
        st.write(f"Menampilkan {len(filtered)} data")
        
        for r in filtered:
            with st.expander(f"📅 {r['submitted_at'][:10]} - NIK: {r['nik']}"):
                for ans in r.get('responses', []):
                    if ans.get('answer'):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**{ans['question']}**")
                        with col_b:
                            color = "#4caf50" if "setuju" in ans['answer'].lower() else "#f44336"
                            st.markdown(f"<span style='background:{color}; padding:4px 12px; border-radius:20px; color:white'>{ans['answer']}</span>", unsafe_allow_html=True)
                        st.write("---")
                st.caption(f"Submit: {r['submitted_at']}")

elif menu == "⚙️ Pengaturan":
    st.title("⚙️ Pengaturan Sistem")
    
    settings = github.get_settings()
    
    with st.form("settings_form"):
        st.subheader("Pengaturan Umum")
        
        max_quota = st.number_input("Maksimal Kuota per Tahun", 
                                      min_value=1, max_value=50, 
                                      value=settings.get('max_quota_per_year', 10))
        
        allow_polling = st.checkbox("Aktifkan Polling", value=settings.get('allow_polling', True))
        allow_aspirasi = st.checkbox("Aktifkan Aspirasi", value=settings.get('allow_aspirasi', True))
        
        submitted = st.form_submit_button("💾 Simpan Pengaturan", use_container_width=True)
        
        if submitted:
            settings['max_quota_per_year'] = max_quota
            settings['allow_polling'] = allow_polling
            settings['allow_aspirasi'] = allow_aspirasi
            
            if github.save_settings(settings):
                st.success("✅ Pengaturan berhasil disimpan!")
                st.rerun()
            else:
                st.error("❌ Gagal menyimpan pengaturan")
    
    st.markdown("---")
    
    # Manajemen NIK
    st.subheader("👥 Manajemen NIK Valid")
    
    valid_niks = github.get_valid_niks()
    
    with st.form("add_nik_form"):
        new_nik = st.text_input("Tambah NIK Baru", max_chars=16, placeholder="1111111111111111")
        if st.form_submit_button("➕ Tambah NIK", use_container_width=True):
            if len(new_nik) == 16 and new_nik.isdigit():
                if github.add_valid_nik(new_nik):
                    st.success(f"✅ NIK {new_nik} berhasil ditambahkan")
                    st.rerun()
                else:
                    st.error("❌ Gagal menambahkan NIK")
            else:
                st.error("❌ NIK harus 16 digit angka!")
    
    st.write("**Daftar NIK Valid:**")
    for nik in valid_niks:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📌 {nik}")
        with col2:
            if st.button("🗑️ Hapus", key=f"del_nik_{nik}"):
                if github.remove_valid_nik(nik):
                    st.success(f"✅ NIK {nik} dihapus")
                    st.rerun()