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
                st.success(f"✅ Terhubung ke {self.repo}")
            else:
                st.error(f"❌ Gagal akses repo: {r.status_code}. Periksa nama repo dan token.")
                self.valid = False
                return
        except Exception as e:
            st.error(f"❌ Error: {e}")
            self.valid = False
            return

        # Inisialisasi database.json
        self._init_database()

    def _init_database(self):
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
            put_resp = requests.put(url, headers=self.headers, json={
                'message': 'Init database.json',
                'content': content
            })
            if put_resp.status_code in [200, 201]:
                st.info("📁 Database.json berhasil dibuat")
            else:
                st.error(f"❌ Gagal buat database.json: {put_resp.status_code}")
        elif resp.status_code != 200:
            st.warning(f"⚠️ Status database: {resp.status_code}")

    def _get_database(self):
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
        if not self.valid:
            return False
        url = f"{self.base_url}/data/database.json"
        content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
        payload = {'message': 'Update database', 'content': content, 'sha': sha}
        resp = requests.put(url, headers=self.headers, json=payload)
        return resp.status_code in [200, 201]

    # ==================== QUESTIONS ====================
    def get_all_questions(self) -> List[Dict]:
        db = self._get_database()
        return db['data'].get('questions', []) if db else []

    def add_question(self, question: str, option_left: str, option_right: str, is_active: bool = True) -> bool:
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
        success = self._save_database(db['data'], db['sha'])
        if success:
            st.success(f"Soal ditambahkan (ID {new_id})")
        else:
            st.error("Gagal simpan soal")
        return success

    def update_question(self, qid: int, question: str, option_left: str, option_right: str, is_active: bool) -> bool:
        db = self._get_database()
        if not db:
            return False
        for q in db['data']['questions']:
            if q['id'] == qid:
                q['question'] = question
                q['option_left'] = option_left
                q['option_right'] = option_right
                q['is_active'] = is_active
                break
        return self._save_database(db['data'], db['sha'])

    def update_question_status(self, qid: int, is_active: bool) -> bool:
        db = self._get_database()
        if not db:
            return False
        for q in db['data']['questions']:
            if q['id'] == qid:
                q['is_active'] = is_active
                break
        return self._save_database(db['data'], db['sha'])

    def delete_question(self, qid: int) -> bool:
        db = self._get_database()
        if not db:
            return False
        db['data']['questions'] = [q for q in db['data']['questions'] if q['id'] != qid]
        return self._save_database(db['data'], db['sha'])

    # ==================== RESPONSES ====================
    def get_all_responses(self) -> List[Dict]:
        db = self._get_database()
        return db['data'].get('responses', []) if db else []

    def save_response(self, nik: str, responses_list: List[Dict], aspirasi: str = "") -> bool:
        db = self._get_database()
        if not db:
            return False
        new_entry = {
            'nik': nik,
            'submitted_at': datetime.now().isoformat(),
            'responses': responses_list,
            'aspirasi': aspirasi
        }
        db['data']['responses'].append(new_entry)
        saved = self._save_database(db['data'], db['sha'])
        if saved:
            self._update_user_quota(nik)
        return saved

    # ==================== NIK ====================
    def get_valid_niks(self) -> List[str]:
        db = self._get_database()
        return db['data'].get('valid_niks', []) if db else []

    def add_valid_nik(self, nik: str) -> bool:
        db = self._get_database()
        if not db:
            return False
        if nik not in db['data']['valid_niks']:
            db['data']['valid_niks'].append(nik)
            return self._save_database(db['data'], db['sha'])
        return True

    def delete_valid_nik(self, nik: str) -> bool:
        db = self._get_database()
        if not db:
            return False
        db['data']['valid_niks'] = [n for n in db['data']['valid_niks'] if n != nik]
        return self._save_database(db['data'], db['sha'])

    # ==================== KUOTA ====================
    def get_quota_config(self) -> Dict:
        db = self._get_database()
        return db['data'].get('quota_config', {'max_per_year': 10}) if db else {'max_per_year': 10}

    def update_quota_config(self, max_per_year: int) -> bool:
        db = self._get_database()
        if not db:
            return False
        db['data']['quota_config'] = {'max_per_year': max_per_year, 'updated_at': datetime.now().isoformat()}
        return self._save_database(db['data'], db['sha'])

    def get_user_quota(self, nik: str) -> Dict:
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

    def _update_user_quota(self, nik: str) -> bool:
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

    def reset_all_quotas(self) -> bool:
        db = self._get_database()
        if not db:
            return False
        db['data']['user_quotas'] = {}
        return self._save_database(db['data'], db['sha'])