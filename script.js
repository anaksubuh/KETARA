// ========== SISTEM ASPIRASI & POLLING KOTA MAGELANG ==========
// Database: Google Sheets (via Webhook)
// Hosting: GitHub Pages

let currentNik = '';
let currentSisaKuota = 0;
let currentSudahPakai = 0;

// ========== CEK NIK KE GOOGLE SHEETS ==========
async function cekNik() {
    const nik = document.getElementById('nik').value.trim();
    
    // Validasi input
    if (!nik) {
        showMessage('❌ Masukkan NIK!', 'error');
        return;
    }
    
    if (nik.length !== 16) {
        showMessage('❌ NIK harus 16 digit!', 'error');
        return;
    }
    
    if (!/^\d+$/.test(nik)) {
        showMessage('❌ NIK hanya boleh angka!', 'error');
        return;
    }
    
    // Disable tombol selama proses
    const btnCek = document.querySelector('#stepNik button');
    btnCek.disabled = true;
    btnCek.textContent = '⏳ Memeriksa...';
    
    showMessage('⏳ Menghubungi server...', 'info');
    
    try {
        // Panggil API dengan timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 detik timeout
        
        // CEK NIK
        const response = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                action: 'cek_nik',
                nik: nik
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Response cek_nik:', result);
        
        // Cek apakah response valid
        if (!result || result.success === false) {
            throw new Error(result?.error || 'Response tidak valid');
        }
        
        if (!result.valid) {
            showMessage(`❌ NIK ${nik} tidak terdaftar! Hubungi admin kelurahan.`, 'error');
            btnCek.disabled = false;
            btnCek.textContent = '✔️ Cek NIK';
            return;
        }
        
        // AMBIL KUOTA
        showMessage('⏳ Mengecek kuota...', 'info');
        
        const kuotaController = new AbortController();
        const kuotaTimeout = setTimeout(() => kuotaController.abort(), 15000);
        
        const kuotaResponse = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                action: 'get_kuota',
                nik: nik
            }),
            signal: kuotaController.signal
        });
        
        clearTimeout(kuotaTimeout);
        
        if (!kuotaResponse.ok) {
            throw new Error(`HTTP ${kuotaResponse.status}`);
        }
        
        const kuota = await kuotaResponse.json();
        console.log('Response kuota:', kuota);
        
        if (!kuota || kuota.success === false) {
            throw new Error(kuota?.error || 'Gagal mengambil kuota');
        }
        
        // SIMPAN DATA KE VARIABLE GLOBAL
        currentNik = nik;
        currentSisaKuota = kuota.sisa;
        currentSudahPakai = kuota.total;
        
        // UPDATE UI
        document.getElementById('displayNik').innerText = nik;
        document.getElementById('sisaKuota').innerText = kuota.sisa;
        document.getElementById('sudahDigunakan').innerText = kuota.total;
        document.getElementById('infoPanel').classList.remove('hidden');
        
        // CEK KUOTA
        if (kuota.sisa <= 0) {
            document.getElementById('btnPolling').disabled = true;
            document.getElementById('btnAspirasi').disabled = true;
            showMessage(`⚠️ Maaf, kuota Anda sudah habis! Sudah menggunakan ${kuota.total} dari 10 kali.`, 'error');
        } else {
            document.getElementById('btnPolling').disabled = false;
            document.getElementById('btnAspirasi').disabled = false;
            showMessage(`✅ Verifikasi berhasil! Selamat datang, warga dengan NIK ${nik}. Sisa kuota: ${kuota.sisa} dari 10.`, 'success');
        }
        
    } catch (error) {
        console.error('Error detail:', error);
        
        // Handle berbagai jenis error
        if (error.name === 'AbortError') {
            showMessage('❌ Koneksi timeout! Server tidak merespon. Coba lagi nanti.', 'error');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            showMessage('❌ Gagal terhubung ke server! Periksa koneksi internet Anda.', 'error');
        } else if (error.message.includes('HTTP')) {
            showMessage('❌ Server error! Coba lagi nanti.', 'error');
        } else {
            showMessage(`❌ ${error.message || 'Gagal koneksi ke server! Coba lagi.'}`, 'error');
        }
        
        // Reset UI
        document.getElementById('infoPanel').classList.add('hidden');
        
    } finally {
        // Enable tombol kembali
        btnCek.disabled = false;
        btnCek.textContent = '✔️ Cek NIK';
    }
}

// ========== FUNGSI KIRIM POLLING (REVISI) ==========
async function kirimPolling() {
    const p1 = document.querySelector('input[name="polling1"]:checked');
    const p2 = document.querySelector('input[name="polling2"]:checked');
    const p3 = document.querySelector('input[name="polling3"]:checked');
    const p4 = document.querySelector('input[name="polling4"]:checked');
    const p5 = document.querySelector('input[name="polling5"]:checked');
    
    if (!p1 || !p2 || !p3 || !p4 || !p5) {
        showMessage('❌ Silakan isi semua pendapat untuk 5 kebijakan!', 'error');
        return;
    }
    
    // Disable tombol submit
    const btnSubmit = document.querySelector('#pollingPanel .btn-submit');
    const originalText = btnSubmit.textContent;
    btnSubmit.disabled = true;
    btnSubmit.textContent = '⏳ Menyimpan...';
    
    showMessage('⏳ Menyimpan polling ke server...', 'info');
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000);
        
        const response = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                action: 'simpan_polling',
                nik: currentNik,
                kebijakan1: p1.value,
                kebijakan2: p2.value,
                kebijakan3: p3.value,
                kebijakan4: p4.value,
                kebijakan5: p5.value
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Response simpan:', result);
        
        if (result.success) {
            currentSisaKuota = result.sisa_kuota;
            currentSudahPakai = 10 - result.sisa_kuota;
            
            document.getElementById('sisaKuota').innerText = currentSisaKuota;
            document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
            
            showMessage(`✅ Polling berhasil disimpan! Terima kasih atas partisipasinya. Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
            batal();
            
            if (currentSisaKuota <= 0) {
                document.getElementById('btnPolling').disabled = true;
                document.getElementById('btnAspirasi').disabled = true;
            }
        } else {
            throw new Error(result.message || 'Gagal menyimpan');
        }
        
    } catch (error) {
        console.error('Error:', error);
        
        if (error.name === 'AbortError') {
            showMessage('❌ Koneksi timeout! Coba lagi nanti.', 'error');
        } else {
            showMessage(`❌ ${error.message || 'Gagal menyimpan polling! Coba lagi.'}`, 'error');
        }
        
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
    }
}

// ========== FUNGSI KIRIM ASPIRASI (REVISI) ==========
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
    
    if (teks.length > 2000) {
        showMessage('❌ Aspirasi maksimal 2000 karakter!', 'error');
        return;
    }
    
    // Disable tombol submit
    const btnSubmit = document.querySelector('#aspirasiPanel .btn-submit');
    const originalText = btnSubmit.textContent;
    btnSubmit.disabled = true;
    btnSubmit.textContent = '⏳ Menyimpan...';
    
    showMessage('⏳ Menyimpan aspirasi ke server...', 'info');
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000);
        
        const response = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                action: 'simpan_aspirasi',
                nik: currentNik,
                aspirasi: teks
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Response simpan aspirasi:', result);
        
        if (result.success) {
            currentSisaKuota = result.sisa_kuota;
            currentSudahPakai = 10 - result.sisa_kuota;
            
            document.getElementById('sisaKuota').innerText = currentSisaKuota;
            document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
            
            showMessage(`✅ Aspirasi berhasil disimpan! Terima kasih atas masukannya. Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
            batal();
            
            if (currentSisaKuota <= 0) {
                document.getElementById('btnPolling').disabled = true;
                document.getElementById('btnAspirasi').disabled = true;
            }
        } else {
            throw new Error(result.message || 'Gagal menyimpan');
        }
        
    } catch (error) {
        console.error('Error:', error);
        
        if (error.name === 'AbortError') {
            showMessage('❌ Koneksi timeout! Coba lagi nanti.', 'error');
        } else {
            showMessage(`❌ ${error.message || 'Gagal menyimpan aspirasi! Coba lagi.'}`, 'error');
        }
        
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
    }
}

// ========== TAMPIL FORM ==========
function tampilFormPolling() {
    if (currentSisaKuota <= 0) {
        showMessage('❌ Kuota habis!', 'error');
        return;
    }
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.getElementById('pollingPanel').classList.remove('hidden');
    document.getElementById('aspirasiPanel').classList.add('hidden');
}

function tampilFormAspirasi() {
    if (currentSisaKuota <= 0) {
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
    
    showMessage('⏳ Menyimpan polling...', 'info');
    
    try {
        const response = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'simpan_polling',
                nik: currentNik,
                kebijakan1: p1.value,
                kebijakan2: p2.value,
                kebijakan3: p3.value,
                kebijakan4: p4.value,
                kebijakan5: p5.value
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentSisaKuota = result.sisa_kuota;
            currentSudahPakai = 10 - result.sisa_kuota;
            
            document.getElementById('sisaKuota').innerText = currentSisaKuota;
            document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
            
            showMessage(`✅ Polling berhasil disimpan! Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
            batal();
            
            if (currentSisaKuota <= 0) {
                document.getElementById('btnPolling').disabled = true;
                document.getElementById('btnAspirasi').disabled = true;
            }
        } else {
            showMessage('❌ Gagal menyimpan polling!', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('❌ Gagal koneksi ke server!', 'error');
    }
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
    
    showMessage('⏳ Menyimpan aspirasi...', 'info');
    
    try {
        const response = await fetch(GOOGLE_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'simpan_aspirasi',
                nik: currentNik,
                aspirasi: teks
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentSisaKuota = result.sisa_kuota;
            currentSudahPakai = 10 - result.sisa_kuota;
            
            document.getElementById('sisaKuota').innerText = currentSisaKuota;
            document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
            
            showMessage(`✅ Aspirasi berhasil disimpan! Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
            batal();
            
            if (currentSisaKuota <= 0) {
                document.getElementById('btnPolling').disabled = true;
                document.getElementById('btnAspirasi').disabled = true;
            }
        } else {
            showMessage('❌ Gagal menyimpan aspirasi!', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showMessage('❌ Gagal koneksi ke server!', 'error');
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

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
    console.log('🚀 Website Aspirasi Kota Magelang siap!');
});