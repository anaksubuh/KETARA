import streamlit as st
import requests
import json
import base64
from datetime import datetime
from typing import List, Dict

class GitHubAPI:
    def __init__(self):
        try:
            self.token = st.secrets.get("GITHUB_TOKEN", "")
            owner = st.secrets.get("REPO_OWNER", "")
            repo_name = st.secrets.get("REPO_NAME", "")
        except:
            self.token = ""
            owner = ""
            repo_name = ""

        if not self.token or not owner or not repo_name:
            st.error("❌ Secrets tidak lengkap. Periksa GITHUB_TOKEN, REPO_OWNER, REPO_NAME.")
            self.valid = False
            return

        self.repo = f"{owner}/{repo_name}"
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Test koneksi
        test_url = f"https://api.github.com/repos/{self.repo}"
        try:
            r = requests.get(test_url, headers=self.headers)
            if r.status_code == 200:
                self.valid = True
            else:
                st.error(f"❌ Gagal akses repo: {r.status_code} - {r.text[:100]}")
                self.valid = False
                return
        except Exception as e:
            st.error(f"❌ Error: {e}")
            self.valid = False
            return

        # Inisialisasi database.json jika perlu
        self._init_database()

    def _init_database(self):
        """Cek dan buat file database.json jika belum ada"""
        path = "data/database.json"
        url = f"{self.base_url}/{path}"
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
            put_resp = requests.put(url, headers=self.headers, json={'message': 'Init database', 'content': content})
            if put_resp.status_code in [200, 201]:
                st.success("✅ Database.json berhasil dibuat")
            else:
                st.error(f"❌ Gagal buat database.json: {put_resp.status_code}")
        elif resp.status_code != 200:
            st.warning(f"⚠️ Status tidak dikenal: {resp.status_code}")

    def _get_database(self):
        """Ambil seluruh data dari database.json"""
        if not self.valid:
            return None
        url = f"{self.base_url}/data/database.json"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data['content']).decode()
            return {'data': json.loads(content), 'sha': data.get('sha')}
        else:
            st.error(f"Gagal baca database: {resp.status_code}")
            return None

    def _save_database(self, data, sha):
        """Simpan seluruh data ke database.json"""
        if not self.valid:
            return False
        url = f"{self.base_url}/data/database.json"
        content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
        payload = {'message': 'Update database', 'content': content, 'sha': sha}
        resp = requests.put(url, headers=self.headers, json=payload)
        return resp.status_code in [200, 201]

    # -------- Metode untuk questions --------
    def get_all_questions(self) -> List[Dict]:
        db = self._get_database()
        if db:
            return db['data'].get('questions', [])
        return []

    def add_question(self, question, option_left, option_right, is_active=True):
        db = self._get_database()
        if not db:
            return False
        questions = db['data'].get('questions', [])
        new_id = max([q.get('id', 0) for q in questions], default=0) + 1
        new_q = {
            'id': new_id,
            'question': question,
            'option_left': option_left,
            'option_right': option_right,
            'is_active': is_active,
            'created_at': datetime.now().isoformat()
        }
        questions.append(new_q)
        db['data']['questions'] = questions
        return self._save_database(db['data'], db['sha'])

    def update_question(self, qid, question, option_left, option_right, is_active):
        db = self._get_database()
        if not db:
            return False
        for q in db['data']['questions']:
            if q['id'] == qid:
                q.update({
                    'question': question,
                    'option_left': option_left,
                    'option_right': option_right,
                    'is_active': is_active
                })
                break
        return self._save_database(db['data'], db['sha'])

    def update_question_status(self, qid, is_active):
        db = self._get_database()
        if not db:
            return False
        for q in db['data']['questions']:
            if q['id'] == qid:
                q['is_active'] = is_active
                break
        return self._save_database(db['data'], db['sha'])

    def delete_question(self, qid):
        db = self._get_database()
        if not db:
            return False
        db['data']['questions'] = [q for q in db['data']['questions'] if q['id'] != qid]
        return self._save_database(db['data'], db['sha'])

    # -------- Responses --------
    def get_all_responses(self):
        db = self._get_database()
        return db['data'].get('responses', []) if db else []

    def save_response(self, nik, responses_list, aspirasi=""):
        db = self._get_database()
        if not db:
            return False
        new_response = {
            'nik': nik,
            'submitted_at': datetime.now().isoformat(),
            'responses': responses_list,
            'aspirasi': aspirasi
        }
        db['data']['responses'].append(new_response)
        saved = self._save_database(db['data'], db['sha'])
        if saved:
            self._update_user_quota(nik)
        return saved

    # -------- NIK --------
    def get_valid_niks(self):
        db = self._get_database()
        return db['data'].get('valid_niks', []) if db else []

    def add_valid_nik(self, nik):
        db = self._get_database()
        if not db:
            return False
        if nik not in db['data']['valid_niks']:
            db['data']['valid_niks'].append(nik)
            return self._save_database(db['data'], db['sha'])
        return True

    def delete_valid_nik(self, nik):
        db = self._get_database()
        if not db:
            return False
        db['data']['valid_niks'] = [n for n in db['data']['valid_niks'] if n != nik]
        return self._save_database(db['data'], db['sha'])

    # -------- Kuota --------
    def get_quota_config(self):
        db = self._get_database()
        return db['data'].get('quota_config', {'max_per_year': 10}) if db else {'max_per_year': 10}

    def update_quota_config(self, max_per_year):
        db = self._get_database()
        if not db:
            return False
        db['data']['quota_config'] = {'max_per_year': max_per_year, 'updated_at': datetime.now().isoformat()}
        return self._save_database(db['data'], db['sha'])

    def get_user_quota(self, nik):
        db = self._get_database()
        if not db:
            return {'max': 10, 'used': 0, 'remaining': 10, 'can_submit': True}
        quotas = db['data'].get('user_quotas', {})
        current_year = datetime.now().year
        user = quotas.get(nik, {})
        if user.get('last_reset') != current_year:
            user = {'used': 0, 'last_reset': current_year}
        max_q = self.get_quota_config().get('max_per_year', 10)
        used = user.get('used', 0)
        return {
            'max': max_q,
            'used': used,
            'remaining': max_q - used,
            'can_submit': used < max_q
        }

    def _update_user_quota(self, nik):
        db = self._get_database()
        if not db:
            return False
        quotas = db['data'].get('user_quotas', {})
        current_year = datetime.now().year
        if nik not in quotas or quotas[nik].get('last_reset') != current_year:
            quotas[nik] = {'used': 0, 'last_reset': current_year}
        quotas[nik]['used'] += 1
        db['data']['user_quotas'] = quotas
        return self._save_database(db['data'], db['sha'])

    def reset_all_quotas(self):
        db = self._get_database()
        if not db:
            return False
        db['data']['user_quotas'] = {}
        return self._save_database(db['data'], db['sha'])