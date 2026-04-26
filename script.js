// ========== KONFIGURASI ==========
const REPO_OWNER = 'anaksubuh';  // Ganti dengan username GitHub Anda
const REPO_NAME = 'KETARA.github.io';  // Ganti dengan nama repository Anda

// Data akan disimpan via membuat Issue (tidak perlu token user!)
let currentNik = '';
let currentDataUser = null;
let daftarNIKValid = [];

// ========== LOAD DAFTAR NIK (dari file raw GitHub) ==========
async function loadDaftarNIK() {
    try {
        // Baca database.json dari raw GitHub (public, tanpa token)
        const response = await fetch(`https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/database.json`);
        
        if (!response.ok) {
            throw new Error('Database belum tersedia');
        }
        
        const data = await response.json();
        daftarNIKValid = data.daftar_nik_valid || [];
        
        // Load juga riwayat penggunaan untuk cek kuota
        const riwayat = data.riwayat_penggunaan || {};
        
        // Simpan ke localStorage untuk sementara
        localStorage.setItem('riwayat_penggunaan', JSON.stringify(riwayat));
        
        console.log('✅ Daftar NIK dimuat:', daftarNIKValid);
        return true;
    } catch (error) {
        console.error('Gagal load database:', error);
        // Fallback ke default
        daftarNIKValid = ["1111111111111111", "2222222222222222", "3333333333333333"];
        return false;
    }
}

// ========== CEK KUOTA DARI LOCALSTORAGE ==========
function cekKuota(nik) {
    const riwayat = JSON.parse(localStorage.getItem('riwayat_penggunaan') || '{}');
    const tahunIni = new Date().getFullYear();
    
    if (!riwayat[nik]) {
        return { sisa: 10, sudah: 0, perluReset: false };
    }
    
    // Reset jika tahun berganti
    if (riwayat[nik].lastReset !== tahunIni) {
        return { sisa: 10, sudah: 0, perluReset: true };
    }
    
    const sudah = riwayat[nik].total || 0;
    return { sisa: 10 - sudah, sudah: sudah, perluReset: false };
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
    
    // Pastikan daftar NIK sudah dimuat
    if (daftarNIKValid.length === 0) {
        await loadDaftarNIK();
    }
    
    // CEK APAKAH NIK VALID
    if (!daftarNIKValid.includes(nik)) {
        showMessage(`❌ NIK ${nik} tidak terdaftar! Silakan hubungi admin.`, 'error');
        return;
    }
    
    const kuota = cekKuota(nik);
    
    currentNik = nik;
    
    document.getElementById('displayNik').innerText = nik;
    document.getElementById('sisaKuota').innerText = kuota.sisa;
    document.getElementById('sudahDigunakan').innerText = kuota.sudah;
    
    if (kuota.sisa <= 0) {
        document.getElementById('btnPolling').disabled = true;
        document.getElementById('btnAspirasi').disabled = true;
        showMessage(`⚠️ Kuota habis! Sudah ${kuota.sudah} kali.`, 'error');
    } else {
        document.getElementById('btnPolling').disabled = false;
        document.getElementById('btnAspirasi').disabled = false;
        showMessage(`✅ Selamat datang! Sisa kuota: ${kuota.sisa} dari 10`, 'success');
    }
    
    document.getElementById('infoPanel').classList.remove('hidden');
}

// ========== KIRIM DATA VIA GITHUB ISSUES ==========
async function kirimKeGitHub(title, body) {
    showMessage('⏳ Mengirim data...', 'info');
    
    // Buat issue baru di repository
    const issueData = {
        title: title,
        body: body,
        labels: ['save-data']  // Label ini akan trigger GitHub Actions
    };
    
    try {
        // Gunakan API tanpa auth untuk create issue? TIDAK BISA.
        // Kita perlu cara lain: redirect ke form issue GitHub?
        
        // === SOLUSI: Buka halaman new issue di GitHub ===
        const issueUrl = `https://github.com/${REPO_OWNER}/${REPO_NAME}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}&labels=save-data`;
        
        // Buka di tab baru
        window.open(issueUrl, '_blank');
        
        showMessage(
            '📝 Akan terbuka halaman GitHub. Silakan klik "Submit new issue" untuk menyimpan data.\n\n' +
            '⚠️ Anda perlu login GitHub untuk mengirim aspirasi.\n\n' +
            'Atau hubungi admin jika tidak punya akun GitHub.',
            'info'
        );
        
        // Simpan ke localStorage dulu sebagai cache
        simpanKeLocalCache(currentNik, body);
        
        return true;
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('❌ Gagal membuka halaman GitHub', 'error');
        return false;
    }
}

// ========== SIMPAN KE LOCAL CACHE ==========
function simpanKeLocalCache(nik, data) {
    const cache = JSON.parse(localStorage.getItem('pending_submissions') || '[]');
    cache.push({
        nik: nik,
        data: data,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('pending_submissions', JSON.stringify(cache));
    console.log('📦 Data disimpan di cache lokal');
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
    
    const title = `POLLING: NIK ${currentNik}`;
    const body = `📊 **HASIL POLLING**

| Kebijakan | Pendapat |
|-----------|----------|
| Bantuan Sosial | ${p1.value} |
| Tarif Air | ${p2.value} |
| PKL | ${p3.value} |
| Kelurahan Cantik | ${p4.value} |
| APBD 2026 | ${p5.value} |

---
**NIK:** ${currentNik}  
**Waktu:** ${new Date().toLocaleString('id-ID')}  
**User Agent:** ${navigator.userAgent.substring(0, 100)}`;
    
    await kirimKeGitHub(title, body);
    
    // Update kuota lokal
    updateKuotaLokal();
    
    batal();
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
    
    const title = `ASPIRASI: NIK ${currentNik}`;
    const body = `💬 **ASPIRASI MASYARAKAT**

${teks}

---
**NIK:** ${currentNik}  
**Waktu:** ${new Date().toLocaleString('id-ID')}`;
    
    await kirimKeGitHub(title, body);
    
    // Update kuota lokal
    updateKuotaLokal();
    
    batal();
}

// ========== UPDATE KUOTA LOKAL ==========
function updateKuotaLokal() {
    const riwayat = JSON.parse(localStorage.getItem('riwayat_penggunaan') || '{}');
    const tahunIni = new Date().getFullYear();
    
    if (!riwayat[currentNik]) {
        riwayat[currentNik] = { total: 0, lastReset: tahunIni };
    }
    
    riwayat[currentNik].total += 1;
    localStorage.setItem('riwayat_penggunaan', JSON.stringify(riwayat));
    
    const sisa = 10 - riwayat[currentNik].total;
    document.getElementById('sisaKuota').innerText = sisa;
    document.getElementById('sudahDigunakan').innerText = riwayat[currentNik].total;
    
    if (sisa <= 0) {
        document.getElementById('btnPolling').disabled = true;
        document.getElementById('btnAspirasi').disabled = true;
    }
}

// ========== FUNGSI LAINNYA ==========
function tampilFormPolling() {
    const kuota = cekKuota(currentNik);
    if (kuota.sisa <= 0) {
        showMessage('❌ Kuota habis!', 'error');
        return;
    }
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.getElementById('pollingPanel').classList.remove('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
}

function tampilFormAspirasi() {
    const kuota = cekKuota(currentNik);
    if (kuota.sisa <= 0) {
        showMessage('❌ Kuota habis!', 'error');
        return;
    }
    document.getElementById('aspirasiText').value = '';
    document.getElementById('aspirasiPanel').classList.remove('hidden');
    document.getElementById('pollingPanel').classList.add('hidden');
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
    if (type !== 'info') setTimeout(() => msgDiv.innerHTML = '', 8000);
}

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', async () => {
    await loadDaftarNIK();
    
    document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
    console.log('🚀 Website siap!');
    console.log('📋 Jumlah NIK terdaftar:', daftarNIKValid.length);
});

// Debug
window.lihatData = function() {
    console.log('Daftar NIK:', daftarNIKValid);
    console.log('Riwayat:', JSON.parse(localStorage.getItem('riwayat_penggunaan') || '{}'));
};