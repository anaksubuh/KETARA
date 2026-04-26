// ========== KONFIGURASI ==========
const GITHUB_USERNAME = 'anaksubuh';
const GITHUB_REPO = 'KETARA.github.io';
const FILE_PATH = 'database.json';

// ========== VARIABEL GLOBAL ==========
let currentNik = '';
let currentDataUser = null;

// ========== FUNGSI BACA DATABASE (SEMUA DATA DARI SINI) ==========
async function fetchDatabase() {
    const url = `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${GITHUB_REPO}/main/${FILE_PATH}`;
    
    try {
        console.log('📡 Membaca database dari:', url);
        const response = await fetch(url);
        
        if (response.status === 404) {
            console.warn('⚠️ Database belum ada, buat file database.json di GitHub');
            showMessage('⚠️ Database belum tersedia. Hubungi admin.', 'error');
            return {
                daftar_nik_valid: [],
                riwayat_penggunaan: {}
            };
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Validasi struktur
        if (!data.daftar_nik_valid) data.daftar_nik_valid = [];
        if (!data.riwayat_penggunaan) data.riwayat_penggunaan = {};
        
        console.log(`✅ Database berhasil dibaca. ${data.daftar_nik_valid.length} NIK terdaftar`);
        return data;
        
    } catch (err) {
        console.error('❌ Error baca database:', err);
        showMessage('❌ Gagal membaca database. Hubungi admin.', 'error');
        return {
            daftar_nik_valid: [],
            riwayat_penggunaan: {}
        };
    }
}

// ========== CEK NIK (BACA DARI DATABASE, BUKAN HARDCODE) ==========
async function cekNik() {
    const nikInput = document.getElementById('nik');
    const nik = nikInput.value.trim();
    
    if (!nik) {
        showMessage('❌ Masukkan NIK!', 'error');
        return;
    }
    
    if (nik.length !== 16) {
        showMessage('❌ NIK harus 16 digit!', 'error');
        return;
    }
    
    if (!/^\d+$/.test(nik)) {
        showMessage('❌ NIK hanya boleh berisi angka!', 'error');
        return;
    }
    
    showMessage('⏳ Memeriksa NIK...', 'info');
    
    try {
        const db = await fetchDatabase();
        
        // CEK DARI DATABASE.JSON (BUKAN HARDCODE!)
        if (!db.daftar_nik_valid.includes(nik)) {
            showMessage(`❌ NIK ${nik} tidak terdaftar! Hubungi admin untuk pendaftaran.`, 'error');
            return;
        }
        
        const tahunIni = new Date().getFullYear();
        
        // Inisialisasi jika belum ada riwayat
        if (!db.riwayat_penggunaan[nik]) {
            db.riwayat_penggunaan[nik] = {
                total: 0,
                lastReset: tahunIni,
                history: []
            };
        }
        
        // Reset jika tahun berganti
        if (db.riwayat_penggunaan[nik].lastReset !== tahunIni) {
            db.riwayat_penggunaan[nik].total = 0;
            db.riwayat_penggunaan[nik].lastReset = tahunIni;
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
            showMessage(`⚠️ Kuota habis! Sudah ${sudahPakai} kali digunakan tahun ini.`, 'error');
        } else {
            document.getElementById('btnPolling').disabled = false;
            document.getElementById('btnAspirasi').disabled = false;
            showMessage(`✅ Selamat datang, ${nik}! Sisa kuota: ${sisaKuota} dari 10`, 'success');
        }
        
        document.getElementById('infoPanel').classList.remove('hidden');
        
    } catch (err) {
        console.error('Error cekNik:', err);
        showMessage(`❌ Error: ${err.message}`, 'error');
    }
}

// ========== FUNGSI TAMPIL FORM POLLING ==========
function tampilFormPolling() {
    if (currentDataUser && currentDataUser.total >= 10) {
        showMessage('❌ Kuota sudah habis!', 'error');
        return;
    }
    
    // Reset semua pilihan radio
    const radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => radio.checked = false);
    
    document.getElementById('pollingPanel').classList.remove('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
}

// ========== FUNGSI TAMPIL FORM ASPIRASI ==========
function tampilFormAspirasi() {
    if (currentDataUser && currentDataUser.total >= 10) {
        showMessage('❌ Kuota sudah habis!', 'error');
        return;
    }
    
    document.getElementById('aspirasiText').value = '';
    document.getElementById('aspirasiPanel').classList.remove('hidden');
    document.getElementById('pollingPanel').classList.add('hidden');
}

// ========== FUNGSI KIRIM POLLING ==========
async function kirimPolling() {
    const pilihan1 = document.querySelector('input[name="polling1"]:checked');
    const pilihan2 = document.querySelector('input[name="polling2"]:checked');
    const pilihan3 = document.querySelector('input[name="polling3"]:checked');
    const pilihan4 = document.querySelector('input[name="polling4"]:checked');
    const pilihan5 = document.querySelector('input[name="polling5"]:checked');
    
    if (!pilihan1 || !pilihan2 || !pilihan3 || !pilihan4 || !pilihan5) {
        showMessage('❌ Silakan isi semua pendapat untuk 5 kebijakan!', 'error');
        return;
    }
    
    const jawaban = `📊 HASIL POLLING WARGA KOTA MAGELANG

1️⃣ Bantuan Sosial Daerah: ${pilihan1.value}
2️⃣ Penyesuaian Tarif Air Minum: ${pilihan2.value}
3️⃣ Penataan & Relokasi PKL: ${pilihan3.value}
4️⃣ Kelurahan Cantik (Satu Data): ${pilihan4.value}
5️⃣ Perubahan APBD 2026: ${pilihan5.value}

🕐 Waktu: ${new Date().toLocaleString('id-ID')}
🆔 NIK: ${currentNik}`;
    
    await simpanTransaksi(jawaban);
}

// ========== FUNGSI KIRIM ASPIRASI ==========
async function kirimAspirasi() {
    const teks = document.getElementById('aspirasiText').value.trim();
    
    if (!teks) {
        showMessage('❌ Aspirasi tidak boleh kosong!', 'error');
        return;
    }
    
    if (teks.length < 5) {
        showMessage('❌ Aspirasi minimal 5 karakter!', 'error');
        return;
    }
    
    const jawaban = `💬 ASPIRASI WARGA KOTA MAGELANG

📝 Isi Aspirasi:
${teks}

🕐 Waktu: ${new Date().toLocaleString('id-ID')}
🆔 NIK: ${currentNik}`;
    
    await simpanTransaksi(jawaban);
}

// ========== SIMPAN TRANSAKSI (KE LOCALSTORAGE SEMENTARA) ==========
async function simpanTransaksi(keterangan) {
    showMessage('⏳ Menyimpan data...', 'info');
    
    try {
        const db = await fetchDatabase();
        const tahunIni = new Date().getFullYear();
        
        if (!db.riwayat_penggunaan[currentNik]) {
            db.riwayat_penggunaan[currentNik] = {
                total: 0,
                lastReset: tahunIni,
                history: []
            };
        }
        
        if (db.riwayat_penggunaan[currentNik].lastReset !== tahunIni) {
            db.riwayat_penggunaan[currentNik].total = 0;
            db.riwayat_penggunaan[currentNik].lastReset = tahunIni;
        }
        
        if (db.riwayat_penggunaan[currentNik].total >= 10) {
            showMessage('❌ Kuota sudah habis!', 'error');
            batal();
            return;
        }
        
        // Tambah transaksi
        db.riwayat_penggunaan[currentNik].total += 1;
        db.riwayat_penggunaan[currentNik].history.push({
            tanggal: new Date().toISOString(),
            keterangan: keterangan,
            timestamp: Date.now()
        });
        
        // SIMPAN KE LOCALSTORAGE SEMENTARA
        // Karena tidak ada token, data disimpan di browser dulu
        const semuaData = {
            daftar_nik_valid: db.daftar_nik_valid,
            riwayat_penggunaan: db.riwayat_penggunaan
        };
        localStorage.setItem('polling_data_backup', JSON.stringify(semuaData));
        
        // Tampilkan data di console untuk admin
        console.log('📦 DATA YANG HARUS DISIMPAN KE database.json:');
        console.log(JSON.stringify(semuaData, null, 2));
        
        const sudahPakai = db.riwayat_penggunaan[currentNik].total;
        const sisaKuota = 10 - sudahPakai;
        
        showMessage(`✅ Berhasil! Sisa kuota: ${sisaKuota} dari 10\n\n📌 Data tersimpan di browser. Admin akan memproses.`, 'success');
        
        document.getElementById('sisaKuota').innerText = sisaKuota;
        document.getElementById('sudahDigunakan').innerText = sudahPakai;
        
        currentDataUser = db.riwayat_penggunaan[currentNik];
        
        batal();
        
        if (sisaKuota <= 0) {
            document.getElementById('btnPolling').disabled = true;
            document.getElementById('btnAspirasi').disabled = true;
        }
        
        // Tawarkan untuk cek NIK lain
        setTimeout(() => {
            if (confirm('✅ Data tersimpan! Ingin cek NIK lain?')) {
                document.getElementById('nik').value = '';
                document.getElementById('infoPanel').classList.add('hidden');
                currentNik = '';
                currentDataUser = null;
            }
        }, 500);
        
    } catch (err) {
        console.error('Error simpan:', err);
        showMessage(`❌ Gagal menyimpan: ${err.message}`, 'error');
    }
}

// ========== FUNGSI EXPORT DATA UNTUK ADMIN ==========
function exportData() {
    const data = localStorage.getItem('polling_data_backup');
    if (!data) {
        showMessage('❌ Tidak ada data tersimpan', 'error');
        return;
    }
    
    // Buat file download
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `database_export_${new Date().toISOString().slice(0,19)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showMessage('✅ Data diekspor! File JSON sudah di-download.', 'success');
}

// ========== FUNGSI BATAL ==========
function batal() {
    document.getElementById('pollingPanel').classList.add('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
    
    // Reset semua radio button
    const radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => radio.checked = false);
    
    document.getElementById('aspirasiText').value = '';
}

// ========== FUNGSI TAMPIL PESAN ==========
function showMessage(msg, type) {
    const msgDiv = document.getElementById('message');
    const bgColors = {
        success: '#d4edda',
        error: '#f8d7da',
        info: '#d1ecf1'
    };
    
    msgDiv.innerHTML = `<div style="background: ${bgColors[type]}; padding: 12px; border-radius: 8px; margin-top: 10px; white-space: pre-line;">${msg}</div>`;
    
    if (type !== 'info') {
        setTimeout(() => {
            if (msgDiv.innerHTML.includes(msg)) {
                msgDiv.innerHTML = '';
            }
        }, 8000);
    }
}

// ========== TAMBAHKAN TOMBOL EXPORT UNTUK ADMIN ==========
function tambahTombolExport() {
    const container = document.querySelector('.container');
    if (container && !document.getElementById('exportBtn')) {
        const btnExport = document.createElement('button');
        btnExport.id = 'exportBtn';
        btnExport.innerHTML = '📤 Export Data (Admin)';
        btnExport.onclick = exportData;
        btnExport.style.cssText = 'background: #6c757d; color: white; margin-top: 20px; width: 100%;';
        container.appendChild(btnExport);
    }
}

// ========== ENTER KEY UNTUK NIK ==========
document.addEventListener('DOMContentLoaded', () => {
    const nikInput = document.getElementById('nik');
    if (nikInput) {
        nikInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') cekNik();
        });
    }
    
    tambahTombolExport();
    
    console.log('🚀 Website Polling Warga Kota Magelang siap digunakan!');
    console.log('📌 Data NIK valid diambil dari database.json di GitHub');
    console.log('📌 Data polling tersimpan di browser Anda (LocalStorage)');
    console.log('📌 Admin bisa klik tombol "Export Data" untuk mengambil data');
});

// ========== FUNGSI DEBUG ==========
window.lihatDatabase = async function() {
    try {
        const db = await fetchDatabase();
        console.log('📊 DATABASE DARI GITHUB:', db);
        
        const localData = localStorage.getItem('polling_data_backup');
        if (localData) {
            console.log('💾 DATA TERSIMPAN DI BROWSER:', JSON.parse(localData));
        }
        
        showMessage('✅ Cek console (F12) untuk lihat database', 'success');
    } catch(err) {
        console.error('Debug error:', err);
        showMessage('❌ Error saat debug: ' + err.message, 'error');
    }
};

window.exportData = exportData;