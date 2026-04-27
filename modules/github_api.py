import streamlit as st
import requests
import json
import base64
from datetime import datetime
from typing import List, Dict

class GitHubAPI:
    def __init__(self, show_success=False):
        """
        show_success: jika True, tampilkan notifikasi sukses koneksi (default False)
        """
        try:
            self.token = st.secrets.get("GITHUB_TOKEN", "")
            owner = st.secrets.get("REPO_OWNER", "")
            repo_name = st.secrets.get("REPO_NAME", "")
        except Exception as e:
            st.error(f"Gagal baca secrets: {e}")
            self.valid = False
            return

        if not self.token or not owner or not repo_name:
            st.error("❌ Secrets tidak lengkap. Periksa GITHUB_TOKEN, REPO_OWNER, REPO_NAME")
            self.valid = False
            return

        self.repo = f"{owner}/{repo_name}"
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Test koneksi ke repository
        test_url = f"https://api.github.com/repos/{self.repo}"
        try:
            r = requests.get(test_url, headers=self.headers)
            if r.status_code == 200:
                self.valid = True
                if show_success:
                    st.success(f"✅ Terhubung ke {self.repo}")
            elif r.status_code == 401:
                st.error("❌ Token GitHub tidak valid atau sudah kadaluarsa. Buat token baru.")
                self.valid = False
                return
            elif r.status_code == 404:
                st.error(f"❌ Repository {self.repo} tidak ditemukan. Periksa nama repo dan token.")
                self.valid = False
                return
            else:
                st.error(f"❌ Gagal akses repo: {r.status_code} - {r.reason}")
                self.valid = False
                return
        except Exception as e:
            st.error(f"❌ Error koneksi: {e}")
            self.valid = False
            return

        # Inisialisasi database.json (hanya jika valid)
        if self.valid:
            self._init_database()

    def _init_database(self):
        path = "data/database.json"
        url = f"{self.base_url}/{path}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 404:
                default_data = {
                    "questions": [],
                    "responses": [],
                    "valid_niks": [],
                    "quota_config": {"max_per_year": 10, "updated_at": datetime.now().isoformat()},
                    "user_quotas": {}
                }
                content = base64.b64encode(json.dumps(default_data, indent=2).encode()).decode()
                put_resp = requests.put(url, headers=self.headers, json={
                    'message': 'Init database.json',
                    'content': content
                })
                if put_resp.status_code in [200, 201]:
                    st.info("📁 Database.json berhasil dibuat")
                else:
                    st.error(f"❌ Gagal buat database.json: {put_resp.status_code} - {put_resp.text[:100]}")
            elif resp.status_code != 200:
                st.warning(f"⚠️ Status database: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            st.warning(f"⚠️ Error inisialisasi database: {e}")

    def _get_database(self):
        if not self.valid:
            return None
        url = f"{self.base_url}/data/database.json"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                content = base64.b64decode(data['content']).decode()
                return {'data': json.loads(content), 'sha': data.get('sha')}
            else:
                # Jangan tampilkan error setiap kali, karena bisa dipanggil berulang
                # Tapi untuk debugging bisa diaktifkan
                # st.error(f"Gagal baca database: {resp.status_code}")
                return None
        except Exception as e:
            st.error(f"Error membaca database: {e}")
            return None

    def _save_database(self, data, sha):
        if not self.valid:
            return False
        url = f"{self.base_url}/data/database.json"
        try:
            content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
            payload = {'message': 'Update database', 'content': content, 'sha': sha}
            resp = requests.put(url, headers=self.headers, json=payload)
            return resp.status_code in [200, 201]
        except Exception as e:
            st.error(f"Error menyimpan database: {e}")
            return False

    # ... sisanya (get_all_questions, add_question, dll) tetap sama seperti kode Anda ...
    # (Saya tidak menulis ulang semuanya karena panjang, tapi Anda bisa salin dari kode asli dan tambahkan method di bawah ini)