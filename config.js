// ========== KONFIGURASI GITHUB ==========
// GANTI DENGAN DATA REPOSITORY ANDA!
const GITHUB_CONFIG = {
    owner: 'anaksubuh',           // Ganti dengan username GitHub Anda
    repo: 'KETARA.github.io',     // Ganti dengan nama repository Anda
    path: 'database.json',        // Nama file database
    branch: 'main'                // Branch yang digunakan
};

// Token disimpan di sessionStorage (hanya untuk sementara)
// Wajib diisi melalui prompt saat pertama kali load
let GITHUB_TOKEN = '';

// Fungsi untuk meminta token dari user
function promptToken() {
    if (!GITHUB_TOKEN) {
        GITHUB_TOKEN = prompt('🔐 Masukkan GitHub Token Anda:\n(Simpan token di file terpisah, jangan di-hardcode!)');
        if (GITHUB_TOKEN) {
            sessionStorage.setItem('github_token', GITHUB_TOKEN);
            showMessage('✅ Token tersimpan untuk sesi ini', 'success');
        } else {
            showMessage('❌ Token wajib diisi untuk menggunakan website!', 'error');
        }
    }
    return GITHUB_TOKEN;
}

// Ambil token dari sessionStorage saat load
const savedToken = sessionStorage.getItem('github_token');
if (savedToken) {
    GITHUB_TOKEN = savedToken;
}

// URL API GitHub
function getGitHubApiUrl() {
    return `https://api.github.com/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${GITHUB_CONFIG.path}`;
}