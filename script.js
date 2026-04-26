// ========== VARIABEL GLOBAL ==========
let currentNik = '';
let currentDataUser = null;
let databaseData = null;

// ========== FUNGSI BACA DATABASE DARI GITHUB ==========
async function loadDatabaseFromGitHub() {
    try {
        if (!GITHUB_TOKEN) {
            promptToken();
            if (!GITHUB_TOKEN) return null;
        }

        showMessage('📥 Memuat data dari server...', 'info');
        
        const response = await fetch(getGitHubApiUrl(), {
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                showMessage('❌ Token tidak valid! Masukkan token yang benar.', 'error');
                sessionStorage.removeItem('github_token');
                GITHUB_TOKEN = '';
                promptToken();
                return loadDatabaseFromGitHub();
            }
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        // Decode content dari base64
        const content = atob(data.content);
        databaseData = JSON.parse(content);
        
        console.log('✅ Database loaded:', databaseData);
        showMessage('✅ Data berhasil dimuat', 'success');
        return databaseData;
        
    } catch (error) {
        console.error('Error loading database:', error);
        showMessage(`❌ Gagal memuat data: ${error.message}`, 'error');
        
        // Fallback ke default jika file tidak ada
        if (!databaseData) {
            databaseData = {
                daftar_nik_valid: ["1111111111111111", "2222222222222222", "3333333333333333"],
                riwayat_penggunaan: {}
            };
        }
        return databaseData;
    }
}

// ========== FUNGSI SIMPAN DATABASE KE GITHUB ==========
async function saveDatabaseToGitHub() {
    try {
        if (!GITHUB_TOKEN) {
            promptToken();
            if (!GITHUB_TOKEN) return false;
        }

        showMessage('💾 Menyimpan data ke server...', 'info');
        
        // Dapatkan SHA file terbaru
        const getResponse = await fetch(getGitHubApiUrl(), {
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });

        let sha = null;
        if (getResponse.ok) {
            const data = await getResponse.json();
            sha = data.sha;
        }

        // Encode content ke base64
        const content = btoa(unescape(encodeURIComponent(JSON.stringify(databaseData, null, 2))));
        
        // Upload file
        const uploadResponse = await fetch(getGitHubApiUrl(), {
            method: 'PUT',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: `Update database - ${new Date().toLocaleString('id-ID')}`,
                content: content,
                sha: sha,
                branch: GITHUB_CONFIG.branch
            })
        });

        if (!uploadResponse.ok) {
            throw new Error(`HTTP ${uploadResponse.status}`);
        }

        console.log('✅ Database saved to GitHub');
        showMessage('✅ Data berhasil disimpan ke server!', 'success');
        return true;
        
    } catch (error) {
        console.error('Error saving database:', error);
        showMessage(`❌ Gagal menyimpan data: ${error.message}`, 'error');
        return false;
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
    
    // Load database dulu
    if (!databaseData) {
        await loadDatabaseFromGitHub();
    }
    
    // CEK APAKAH NIK VALID
    if (!databaseData.daftar_nik_valid.includes(nik)) {
        showMessage(`❌ NIK ${nik} tidak terdaftar!`, 'error');
        return;
    }
    
    const tahunIni = new Date().getFullYear();
    
    // Inisialisasi jika belum ada
    if (!databaseData.riwayat_penggunaan[nik]) {
        databaseData.riwayat_penggunaan[nik] = {
            total: 0,
            lastReset: tahunIni,
            history: []
        };
        await saveDatabaseToGitHub();
    }
    
    // Reset jika tahun berganti
    if (databaseData.riwayat_penggunaan[nik].lastReset !== tahunIni) {
        databaseData.riwayat_penggunaan[nik].total = 0;
        databaseData.riwayat_penggunaan[nik].lastReset = tahunIni;
        await saveDatabaseToGitHub();
    }
    
    const sudahPakai = databaseData.riwayat_penggunaan[nik].total;
    const sisaKuota = 10 - sudahPakai;
    
    currentNik = nik;
    currentDataUser = databaseData.riwayat_penggunaan[nik];
    
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
    
    const jawaban = {
        type: 'polling',
        data: {
            kebijakan1: p1.value,
            kebijakan2: p2.value,
            kebijakan3: p3.value,
            kebijakan4: p4.value,
            kebijakan5: p5.value
        },
        timestamp: new Date().toISOString(),
        nik: currentNik
    };
    
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
    
    const jawaban = {
        type: 'aspirasi',
        data: teks,
        timestamp: new Date().toISOString(),
        nik: currentNik
    };
    
    await simpanTransaksi(jawaban);
}

// ========== SIMPAN TRANSAKSI ==========
async function simpanTransaksi(data) {
    const tahunIni = new Date().getFullYear();
    
    if (!databaseData.riwayat_penggunaan[currentNik]) {
        databaseData.riwayat_penggunaan[currentNik] = { total: 0, lastReset: tahunIni, history: [] };
    }
    
    if (databaseData.riwayat_penggunaan[currentNik].total >= 10) {
        showMessage('❌ Kuota habis!', 'error');
        batal();
        return;
    }
    
    // Tambah ke history
    databaseData.riwayat_penggunaan[currentNik].total += 1;
    databaseData.riwayat_penggunaan[currentNik].history.push(data);
    
    // Simpan ke GitHub
    const saved = await saveDatabaseToGitHub();
    
    if (saved) {
        const sisa = 10 - databaseData.riwayat_penggunaan[currentNik].total;
        showMessage(`✅ Berhasil! Sisa kuota: ${sisa} dari 10`, 'success');
        
        document.getElementById('sisaKuota').innerText = sisa;
        document.getElementById('sudahDigunakan').innerText = databaseData.riwayat_penggunaan[currentNik].total;
        
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

// ========== TAMPILKAN DATA UNTUK ADMIN ==========
function lihatDataAdmin() {
    console.log('📊 DATABASE:', databaseData);
    alert('Cek console (F12) untuk melihat data lengkap');
}

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', async () => {
    // Load database saat pertama kali
    await loadDatabaseFromGitHub();
    
    document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
    console.log('🚀 Website siap!');
    console.log('📋 Daftar NIK:', databaseData?.daftar_nik_valid);
});

// Export ke window untuk debugging
window.lihatData = lihatDataAdmin;
window.cekNik = cekNik;
window.tampilFormPolling = tampilFormPolling;
window.tampilFormAspirasi = tampilFormAspirasi;
window.kirimPolling = kirimPolling;
window.kirimAspirasi = kirimAspirasi;
window.batal = batal;