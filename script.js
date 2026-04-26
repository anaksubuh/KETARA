// ========== KONFIGURASI ==========
const GITHUB_USERNAME = 'anaksubuh';
const GITHUB_REPO = 'KETARA.github.io';
const FILE_PATH = 'database.json';

let currentNik = '';
let currentDataUser = null;

// ========== BACA DATABASE ==========
async function fetchDatabase() {
    try {
        const url = `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${GITHUB_REPO}/main/${FILE_PATH}`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const text = await response.text();
        const cleanText = text.replace(/^\uFEFF/, '').trim();
        const data = JSON.parse(cleanText);
        
        if (!data.daftar_nik_valid) throw new Error('daftar_nik_valid tidak ditemukan');
        if (!data.riwayat_penggunaan) throw new Error('riwayat_penggunaan tidak ditemukan');
        
        return data;
    } catch (err) {
        console.error('Error baca database:', err);
        throw err;
    }
}

// ========== SIMPAN DATABASE via GitHub Actions ==========
async function saveToDatabase(data) {
    try {
        // Kirim data ke GitHub Actions via Issue
        const response = await fetch(`https://api.github.com/repos/${GITHUB_USERNAME}/${GITHUB_REPO}/issues`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: `📝 Data Baru - ${currentNik} - ${new Date().toLocaleString('id-ID')}`,
                body: JSON.stringify(data, null, 2),
                labels: ['save-data']
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        console.log('✅ Data dikirim ke GitHub Actions');
        return true;
    } catch (err) {
        console.error('Error simpan:', err);
        throw err;
    }
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
    
    showMessage('⏳ Memeriksa NIK...', 'info');
    
    try {
        const db = await fetchDatabase();
        
        if (!db.daftar_nik_valid.includes(nik)) {
            showMessage(`❌ NIK ${nik} tidak terdaftar!`, 'error');
            return;
        }
        
        const tahunIni = new Date().getFullYear();
        
        if (!db.riwayat_penggunaan[nik]) {
            db.riwayat_penggunaan[nik] = {
                total: 0,
                lastReset: tahunIni,
                history: []
            };
            await saveToDatabase(db);
        }
        
        if (db.riwayat_penggunaan[nik].lastReset !== tahunIni) {
            db.riwayat_penggunaan[nik].total = 0;
            db.riwayat_penggunaan[nik].lastReset = tahunIni;
            await saveToDatabase(db);
        }
        
        const sudahPakai = db.riwayat_penggunaan[nik].total;
        const sisaKuota = 10 - sudahPakai;
        
        currentNik = nik;
        currentDataUser = db.riwayat_penggunaan[nik];
        
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
        
    } catch (err) {
        console.error(err);
        showMessage(`❌ Error: ${err.message}`, 'error');
    }
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
    
    try {
        const db = await fetchDatabase();
        const tahunIni = new Date().getFullYear();
        
        if (!db.riwayat_penggunaan[currentNik]) {
            db.riwayat_penggunaan[currentNik] = { total: 0, lastReset: tahunIni, history: [] };
        }
        
        if (db.riwayat_penggunaan[currentNik].lastReset !== tahunIni) {
            db.riwayat_penggunaan[currentNik].total = 0;
            db.riwayat_penggunaan[currentNik].lastReset = tahunIni;
        }
        
        if (db.riwayat_penggunaan[currentNik].total >= 10) {
            showMessage('❌ Kuota habis!', 'error');
            batal();
            return;
        }
        
        db.riwayat_penggunaan[currentNik].total += 1;
        db.riwayat_penggunaan[currentNik].history.push({
            tanggal: new Date().toISOString(),
            keterangan: keterangan
        });
        
        await saveToDatabase(db);
        
        const sisa = 10 - db.riwayat_penggunaan[currentNik].total;
        showMessage(`✅ Berhasil! Sisa kuota: ${sisa} dari 10`, 'success');
        
        document.getElementById('sisaKuota').innerText = sisa;
        document.getElementById('sudahDigunakan').innerText = db.riwayat_penggunaan[currentNik].total;
        
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
        
    } catch (err) {
        showMessage(`❌ Gagal: ${err.message}`, 'error');
    }
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
    msgDiv.innerHTML = `<div style="background:${colors[type]}; padding:12px; border-radius:8px;">${msg}</div>`;
    if (type !== 'info') setTimeout(() => msgDiv.innerHTML = '', 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
    console.log('🚀 Website siap!');
});