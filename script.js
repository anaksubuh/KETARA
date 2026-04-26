// ========== FUNGSI JSONP UNTUK MELEWATI CORS ==========

function jsonpRequest(url, callbackName, onSuccess, onError) {
  const script = document.createElement('script');
  const callbackFunction = `jsonp_callback_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
  
  window[callbackFunction] = function(data) {
    delete window[callbackFunction];
    document.body.removeChild(script);
    onSuccess(data);
  };
  
  const separator = url.includes('?') ? '&' : '?';
  script.src = `${url}${separator}callback=${callbackFunction}`;
  
  script.onerror = function() {
    delete window[callbackFunction];
    document.body.removeChild(script);
    onError('JSONP request failed');
  };
  
  document.body.appendChild(script);
}

// ========== CEK NIK (pakai JSONP) ==========
async function cekNik() {
  const nik = document.getElementById('nik').value.trim();
  
  if (!nik) {
    showMessage('❌ Masukkan NIK!', 'error');
    return;
  }
  
  if (nik.length !== 16 || !/^\d+$/.test(nik)) {
    showMessage('❌ NIK harus 16 digit angka!', 'error');
    return;
  }
  
  const btnCek = document.querySelector('#stepNik button');
  const originalText = btnCek.textContent;
  btnCek.disabled = true;
  btnCek.textContent = '⏳ Memeriksa...';
  
  showMessage('⏳ Memverifikasi NIK...', 'info');
  
  const url = `${GOOGLE_WEBHOOK_URL}?action=cek_nik&nik=${encodeURIComponent(nik)}`;
  
  jsonpRequest(url, 'callback', function(result) {
    console.log('Hasil cek NIK:', result);
    
    if (result.success && result.valid) {
      // Ambil kuota
      const kuotaUrl = `${GOOGLE_WEBHOOK_URL}?action=get_kuota&nik=${encodeURIComponent(nik)}`;
      
      jsonpRequest(kuotaUrl, 'callback', function(kuota) {
        console.log('Hasil kuota:', kuota);
        
        if (kuota.success) {
          currentNik = nik;
          currentSisaKuota = kuota.sisa;
          currentSudahPakai = kuota.total;
          
          document.getElementById('displayNik').innerText = nik;
          document.getElementById('sisaKuota').innerText = kuota.sisa;
          document.getElementById('sudahDigunakan').innerText = kuota.total;
          document.getElementById('infoPanel').classList.remove('hidden');
          
          if (kuota.sisa <= 0) {
            document.getElementById('btnPolling').disabled = true;
            document.getElementById('btnAspirasi').disabled = true;
            showMessage(`⚠️ Kuota habis! Sudah ${kuota.total} kali.`, 'error');
          } else {
            document.getElementById('btnPolling').disabled = false;
            document.getElementById('btnAspirasi').disabled = false;
            showMessage(`✅ Selamat datang! Sisa kuota: ${kuota.sisa} dari 10`, 'success');
          }
        } else {
          showMessage('❌ Gagal mengambil kuota', 'error');
        }
        
        btnCek.disabled = false;
        btnCek.textContent = originalText;
      }, function(err) {
        showMessage('❌ Gagal mengambil kuota', 'error');
        btnCek.disabled = false;
        btnCek.textContent = originalText;
      });
      
    } else {
      showMessage(`❌ NIK ${nik} tidak terdaftar!`, 'error');
      btnCek.disabled = false;
      btnCek.textContent = originalText;
    }
  }, function(err) {
    showMessage('❌ Gagal koneksi ke server!', 'error');
    btnCek.disabled = false;
    btnCek.textContent = originalText;
  });
}

// ========== KIRIM POLLING (pakai JSONP) ==========
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
  
  const btnSubmit = document.querySelector('#pollingPanel .btn-submit');
  const originalText = btnSubmit.textContent;
  btnSubmit.disabled = true;
  btnSubmit.textContent = '⏳ Menyimpan...';
  
  showMessage('⏳ Menyimpan polling...', 'info');
  
  const url = `${GOOGLE_WEBHOOK_URL}?action=simpan_polling&nik=${encodeURIComponent(currentNik)}&kebijakan1=${encodeURIComponent(p1.value)}&kebijakan2=${encodeURIComponent(p2.value)}&kebijakan3=${encodeURIComponent(p3.value)}&kebijakan4=${encodeURIComponent(p4.value)}&kebijakan5=${encodeURIComponent(p5.value)}`;
  
  jsonpRequest(url, 'callback', function(result) {
    if (result.success) {
      // Update kuota
      const kuotaUrl = `${GOOGLE_WEBHOOK_URL}?action=get_kuota&nik=${encodeURIComponent(currentNik)}`;
      
      jsonpRequest(kuotaUrl, 'callback', function(kuota) {
        if (kuota.success) {
          currentSisaKuota = kuota.sisa;
          currentSudahPakai = kuota.total;
          document.getElementById('sisaKuota').innerText = kuota.sisa;
          document.getElementById('sudahDigunakan').innerText = kuota.total;
          showMessage(`✅ Polling berhasil! Sisa kuota: ${kuota.sisa} dari 10`, 'success');
          
          if (kuota.sisa <= 0) {
            document.getElementById('btnPolling').disabled = true;
            document.getElementById('btnAspirasi').disabled = true;
          }
        } else {
          showMessage('✅ Polling tersimpan, tapi gagal update kuota', 'success');
        }
        
        batal();
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
      }, function(err) {
        showMessage('✅ Polling tersimpan', 'success');
        batal();
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
      });
      
    } else {
      showMessage('❌ Gagal menyimpan polling!', 'error');
      btnSubmit.disabled = false;
      btnSubmit.textContent = originalText;
    }
  }, function(err) {
    showMessage('❌ Gagal koneksi ke server!', 'error');
    btnSubmit.disabled = false;
    btnSubmit.textContent = originalText;
  });
}

// ========== KIRIM ASPIRASI (pakai JSONP) ==========
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
  
  const btnSubmit = document.querySelector('#aspirasiPanel .btn-submit');
  const originalText = btnSubmit.textContent;
  btnSubmit.disabled = true;
  btnSubmit.textContent = '⏳ Menyimpan...';
  
  showMessage('⏳ Menyimpan aspirasi...', 'info');
  
  const url = `${GOOGLE_WEBHOOK_URL}?action=simpan_aspirasi&nik=${encodeURIComponent(currentNik)}&aspirasi=${encodeURIComponent(teks)}`;
  
  jsonpRequest(url, 'callback', function(result) {
    if (result.success) {
      // Update kuota
      const kuotaUrl = `${GOOGLE_WEBHOOK_URL}?action=get_kuota&nik=${encodeURIComponent(currentNik)}`;
      
      jsonpRequest(kuotaUrl, 'callback', function(kuota) {
        if (kuota.success) {
          currentSisaKuota = kuota.sisa;
          currentSudahPakai = kuota.total;
          document.getElementById('sisaKuota').innerText = kuota.sisa;
          document.getElementById('sudahDigunakan').innerText = kuota.total;
          showMessage(`✅ Aspirasi berhasil! Sisa kuota: ${kuota.sisa} dari 10`, 'success');
          
          if (kuota.sisa <= 0) {
            document.getElementById('btnPolling').disabled = true;
            document.getElementById('btnAspirasi').disabled = true;
          }
        } else {
          showMessage('✅ Aspirasi tersimpan!', 'success');
        }
        
        batal();
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
      }, function(err) {
        showMessage('✅ Aspirasi tersimpan!', 'success');
        batal();
        btnSubmit.disabled = false;
        btnSubmit.textContent = originalText;
      });
      
    } else {
      showMessage('❌ Gagal menyimpan aspirasi!', 'error');
      btnSubmit.disabled = false;
      btnSubmit.textContent = originalText;
    }
  }, function(err) {
    showMessage('❌ Gagal koneksi ke server!', 'error');
    btnSubmit.disabled = false;
    btnSubmit.textContent = originalText;
  });
}

// Fungsi lainnya (tampilFormPolling, tampilFormAspirasi, batal, showMessage) tetap sama
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

// Init
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
  console.log('🚀 Website siap! Webhook:', GOOGLE_WEBHOOK_URL);
});