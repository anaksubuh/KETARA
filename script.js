// ========== SISTEM ASPIRASI & POLLING DENGAN GITHUB ISSUES ==========
// User akan diarahkan ke GitHub (perlu login GitHub, TIDAK PERLU TOKEN!)

let currentNik = '';
let currentSisaKuota = 0;
let currentSudahPakai = 0;

// Konfigurasi repository
const REPO_OWNER = 'anaksubuh';
const REPO_NAME = 'KETARA.github.io';

// Load daftar NIK dari database.json (public, tanpa token)
async function loadDaftarNIK() {
  try {
    const response = await fetch(`https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/database.json`);
    const data = await response.json();
    return data.daftar_nik_valid || [];
  } catch (error) {
    console.error('Gagal load NIK:', error);
    return ["1111111111111111", "2222222222222222", "3333333333333333"];
  }
}

// Cek kuota dari localStorage
function getKuota(nik) {
  const riwayat = JSON.parse(localStorage.getItem(`kuota_${nik}`) || '{}');
  const tahunIni = new Date().getFullYear();
  
  if (!riwayat.tahun || riwayat.tahun !== tahunIni) {
    return { sisa: 10, sudah: 0 };
  }
  return { sisa: 10 - (riwayat.total || 0), sudah: riwayat.total || 0 };
}

function updateKuota(nik) {
  const riwayat = JSON.parse(localStorage.getItem(`kuota_${nik}`) || '{}');
  const tahunIni = new Date().getFullYear();
  
  riwayat.tahun = tahunIni;
  riwayat.total = (riwayat.total || 0) + 1;
  
  localStorage.setItem(`kuota_${nik}`, JSON.stringify(riwayat));
  return riwayat.total;
}

// Buka halaman Create Issue di GitHub
function buatIssueGitHub(title, body) {
  const url = `https://github.com/${REPO_OWNER}/${REPO_NAME}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}&labels=save-data`;
  window.open(url, '_blank');
}

// ========== CEK NIK ==========
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
  btnCek.disabled = true;
  btnCek.textContent = '⏳ Memeriksa...';
  
  showMessage('⏳ Memeriksa NIK...', 'info');
  
  // Load daftar NIK
  const daftarNIK = await loadDaftarNIK();
  
  if (!daftarNIK.includes(nik)) {
    showMessage(`❌ NIK ${nik} tidak terdaftar! Hubungi admin.`, 'error');
    btnCek.disabled = false;
    btnCek.textContent = '✔️ Cek NIK';
    return;
  }
  
  const kuota = getKuota(nik);
  
  currentNik = nik;
  currentSisaKuota = kuota.sisa;
  currentSudahPakai = kuota.sudah;
  
  document.getElementById('displayNik').innerText = nik;
  document.getElementById('sisaKuota').innerText = kuota.sisa;
  document.getElementById('sudahDigunakan').innerText = kuota.sudah;
  document.getElementById('infoPanel').classList.remove('hidden');
  
  if (kuota.sisa <= 0) {
    document.getElementById('btnPolling').disabled = true;
    document.getElementById('btnAspirasi').disabled = true;
    showMessage(`⚠️ Kuota habis! Sudah ${kuota.sudah} kali.`, 'error');
  } else {
    document.getElementById('btnPolling').disabled = false;
    document.getElementById('btnAspirasi').disabled = false;
    showMessage(`✅ Selamat datang! Sisa kuota: ${kuota.sisa} dari 10`, 'success');
  }
  
  btnCek.disabled = false;
  btnCek.textContent = '✔️ Cek NIK';
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
function kirimPolling() {
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
  const body = `📊 **HASIL POLLING WARGA**

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
  
  buatIssueGitHub(title, body);
  
  // Update kuota lokal
  updateKuota(currentNik);
  const kuota = getKuota(currentNik);
  currentSisaKuota = kuota.sisa;
  currentSudahPakai = kuota.sudah;
  
  document.getElementById('sisaKuota').innerText = currentSisaKuota;
  document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
  
  showMessage(`✅ Buka halaman GitHub yang muncul, lalu klik "Submit new issue". Data akan otomatis tersimpan! Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
  
  batal();
  
  if (currentSisaKuota <= 0) {
    document.getElementById('btnPolling').disabled = true;
    document.getElementById('btnAspirasi').disabled = true;
  }
}

// ========== KIRIM ASPIRASI ==========
function kirimAspirasi() {
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
  
  buatIssueGitHub(title, body);
  
  // Update kuota lokal
  updateKuota(currentNik);
  const kuota = getKuota(currentNik);
  currentSisaKuota = kuota.sisa;
  currentSudahPakai = kuota.sudah;
  
  document.getElementById('sisaKuota').innerText = currentSisaKuota;
  document.getElementById('sudahDigunakan').innerText = currentSudahPakai;
  
  showMessage(`✅ Buka halaman GitHub yang muncul, lalu klik "Submit new issue". Data akan otomatis tersimpan! Sisa kuota: ${currentSisaKuota} dari 10`, 'success');
  
  batal();
  
  if (currentSisaKuota <= 0) {
    document.getElementById('btnPolling').disabled = true;
    document.getElementById('btnAspirasi').disabled = true;
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
  if (type !== 'info') setTimeout(() => msgDiv.innerHTML = '', 8000);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('nik')?.addEventListener('keypress', e => e.key === 'Enter' && cekNik());
  console.log('🚀 Website Aspirasi Kota Magelang siap!');
  console.log('Menggunakan sistem GitHub Issues');
  console.log('Repository:', `${REPO_OWNER}/${REPO_NAME}`);
});