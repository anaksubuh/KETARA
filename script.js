// ========== DAFTAR NIK VALID (EDIT DI SINI) ==========
const DAFTAR_NIK_VALID = [
    "1111111111111111",
    "2222222222222222",
    "3333333333333333"
];

// ========== DATA RIWAYAT (Tersimpan di Browser) ==========
let currentNik = '';
let currentDataUser = null;
let riwayatPenggunaan = {};

// ========== LOAD DATA DARI BROWSER ==========
function loadData() {
    const saved = localStorage.getItem('polling_data');
    if (saved) {
        riwayatPenggunaan = JSON.parse(saved);
        console.log('✅ Data dimuat dari browser');
    }
}

// ========== SAVE DATA KE BROWSER ==========
function saveData() {
    localStorage.setItem('polling_data', JSON.stringify(riwayatPenggunaan));
    console.log('✅ Data disimpan ke browser');
    
    // Tampilkan data untuk admin (copy ke database.json)
    console.log('📦 COPY INI KE database.json:');
    console.log(JSON.stringify({
        daftar_nik_valid: DAFTAR_NIK_VALID,
        riwayat_penggunaan: riwayatPenggunaan
    }, null, 2));
}

// ========== CEK NIK ==========
async function cekNik() {
    const nik = document.getElementById('nik').value.trim();
    
    if (!nik) {
        showMessage('❌ Masukkan NIK!', 'error');
        return;
    }
    
    if (nik.length !== 16) {
        showMessage('❌ NIK harus 16 digit!', 'error');
        return;
    }
    
    if (!/^\d+$/.test(nik)) {
        showMessage('❌ NIK hanya angka!', 'error');
        return;
    }
    
    // CEK APAKAH NIK VALID
    if (!DAFTAR_NIK_VALID.includes(nik)) {
        showMessage(`❌ NIK ${nik} tidak terdaftar!`, 'error');
        return;
    }
    
    const tahunIni = new Date().getFullYear();
    
    // Inisialisasi jika belum ada
    if (!riwayatPenggunaan[nik]) {
        riwayatPenggunaan[nik] = {
            total: 0,
            lastReset: tahunIni,
            history: []
        };
        saveData();
    }
    
    // Reset jika tahun berganti
    if (riwayatPenggunaan[nik].lastReset !== tahunIni) {
        riwayatPenggunaan[nik].total = 0;
        riwayatPenggunaan[nik].lastReset = tahunIni;
        saveData();
    }
    
    const sudahPakai = riwayatPenggunaan[nik].total;
    const sisaKuota = 10 - sudahPakai;
    
    currentNik = nik;
    currentDataUser = riwayatPenggunaan[nik];
    
    document.getElementById('displayNik').innerText = nik;
    document.getElementById('sisaKuota').innerText = sisaKuota;
    document.getElementById('sudahDigunakan').innerText = sudahPakai;
    
    if (sisaKuota <= 0) {
        document.getElementById('btnPolling').disabled = true;
        document.getElementById('btnAspirasi').disabled = true;
        showMessage(`⚠️ Kuota habis! Sudah ${sudahPakai} kali.`, 'error');
    } else {
        document.getElementById('btnPolling').disabled = false;
        document.getElementById('btnAspirasi').disabled = false;
        showMessage(`✅ Selamat datang! Sisa kuota: ${sisaKuota} dari 10`, 'success');
    }
    
    document.getElementById('infoPanel').classList.remove('hidden');
}

// ========== TAMPIL FORM ==========
function tampilFormPolling() {
    if (currentDataUser && currentDataUser.total >= 10) {
        showMessage('❌ Kuota habis!', 'error');
        return;
    }
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.getElementById('pollingPanel').classList.remove('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
}

function tampilFormAspirasi() {
    if (currentDataUser && currentDataUser.total >= 10) {
        showMessage('❌ Kuota habis!', 'error');
        return;
    }
    document.getElementById('aspirasiText').value = '';
    document.getElementById('aspirasiPanel').classList.remove('hidden');
    document.getElementById('pollingPanel').classList.add('hidden');
}

// ========== KIRIM POLLING ==========
async function kirimPolling() {
    const p1 = document.querySelector('input[name="polling1"]:checked');
    const p2 = document.querySelector('input[name="polling2"]:checked');
    const p3 = document.querySelector('input[name="polling3"]:checked');
    const p4 = document.querySelector('input[name="polling4"]:checked');
    const p5 = document.querySelector('input[name="polling5"]:checked');
    
    if (!p1 || !p2 || !p3 || !p4 || !p5) {
        showMessage('❌ Isi semua pendapat!', 'error');
        return;
    }
    
    const jawaban = `📊 HASIL POLLING

1. Bantuan Sosial: ${p1.value}
2. Tarif Air: ${p2.value}
3. PKL: ${p3.value}
4. Kelurahan Cantik: ${p4.value}
5. APBD 2026: ${p5.value}

Waktu: ${new Date().toLocaleString('id-ID')}
NIK: ${currentNik}`;
    
    await simpanTransaksi(jawaban);
}

// ========== KIRIM ASPIRASI ==========
async function kirimAspirasi() {
    const teks = document.getElementById('aspirasiText').value.trim();
    
    if (!teks) {
        showMessage('❌ Aspirasi tidak boleh kosong!', 'error');
        return;
    }
    
    if (teks.length < 5) {
        showMessage('❌ Minimal 5 karakter!', 'error');
        return;
    }
    
    const jawaban = `💬 ASPIRASI

${teks}

Waktu: ${new Date().toLocaleString('id-ID')}
NIK: ${currentNik}`;
    
    await simpanTransaksi(jawaban);
}

// ========== SIMPAN TRANSAKSI ==========
async function simpanTransaksi(keterangan) {
    showMessage('⏳ Menyimpan data...', 'info');
    
    const tahunIni = new Date().getFullYear();
    
    if (!riwayatPenggunaan[currentNik]) {
        riwayatPenggunaan[currentNik] = { total: 0, lastReset: tahunIni, history: [] };
    }
    
    if (riwayatPenggunaan[currentNik].total >= 10) {
        showMessage('❌ Kuota habis!', 'error');
        batal();
        return;
    }
    
    riwayatPenggunaan[currentNik].total += 1;
    riwayatPenggunaan[currentNik].history.push({
        tanggal: new Date().toISOString(),
        keterangan: keterangan
    });
    
    saveData();
    
    const sisa = 10 - riwayatPenggunaan[currentNik].total;
    showMessage(`✅ Berhasil! Sisa kuota: ${sisa} dari 10`, 'success');
    
    document.getElementById('sisaKuota').innerText = sisa;
    document.getElementById('sudahDigunakan').innerText = riwayatPenggunaan[currentNik].total;
    
    batal();
    
    if (sisa <= 0) {
        document.getElementById('btnPolling').disabled = true;
        document.getElementById('btnAspirasi').disabled = true;
    }
    
    setTimeout(() => {
        if (confirm('✅ Data tersimpan! Ingin cek NIK lain?')) {
            document.getElementById('nik').value = '';
            document.getElementById('infoPanel').classList.add('hidden');
            currentNik = '';
            currentDataUser = null;
        }
    }, 500);
}

function batal() {
    document.getElementById('pollingPanel').classList.add('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.getElementById('aspirasiText').value = '';
}

function showMessage(msg, type) {
    const colors = { success: '#d4edda', error: '#f8d7da', info: '#d1ecf1' };
    const msgDiv = document.getElementById('message');
    msgDiv.innerHTML = `<div style="background:${colors[type]}; padding:12px; border-radius:8px; white-space:pre-line;">${msg}</div>`;
    if (type !== 'info') setTimeout(() => msgDiv.innerHTML = '', 5000);
}

// ========== EXPORT DATA (UNTUK ADMIN) ==========
function exportData() {
    const data = {
        daftar_nik_valid: DAFTAR_NIK_VALID,
        riwayat_penggunaan: riwayatPenggunaan
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `database_${new Date().toISOString().slice(0,19)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showMessage('✅ Data diekspor! File JSON sudah di-download.', 'success');
}

function tambahTombolExport() {
    const container = document.querySelector('.container');
    if (container && !document.getElementById('exportBtn')) {
        const btn = document.createElement('button');
        btn.id = 'exportBtn';
        btn.innerHTML = '📤 Export Data (Admin)';
        btn.onclick = exportData;
        btn.style.cssText = 'background: #6c757d; color: white; margin-top: 20px; width: 100%;';
        container.appendChild(btn);
    }
}

// ========== INIT ==========
loadData();
tambahTombolExport();

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
    console.log('🚀 Website siap!');
    console.log('📋 Daftar NIK:', DAFTAR_NIK_VALID);
});

window.lihatData = function() {
    console.log('📊 NIK:', DAFTAR_NIK_VALID);
    console.log('📝 Riwayat:', riwayatPenggunaan);
};