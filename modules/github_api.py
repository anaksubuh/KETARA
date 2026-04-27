import requests
import json
from datetime import datetime
from typing import List, Dict
import base64
import streamlit as st

class GitHubAPI:
    def __init__(self):
        try:
            self.token = st.secrets.get("GITHUB_TOKEN", "")
            self.repo = st.secrets.get("GITHUB_REPO", "")
        except:
            # Fallback untuk local testing - GANTI DENGAN DATA ANDA
            self.token = "YOUR_GITHUB_TOKEN_HERE"
            self.repo = "YOUR_USERNAME/YOUR_REPO_NAME"
        
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self._init_data_files()
    
    def _init_data_files(self):
        files = {
            "data/questions.json": {"questions": []},
            "data/responses.json": {"responses": []},
            "data/valid_niks.json": {"niks": []},
            "data/quota_config.json": {"max_per_year": 3, "updated_at": datetime.now().isoformat()},
            "data/user_quotas.json": {"quotas": {}}
        }
        for file_path, default_data in files.items():
            url = f"{self.base_url}/{file_path}"
            try:
                resp = requests.get(url, headers=self.headers)
                if resp.status_code == 404:
                    content = base64.b64encode(json.dumps(default_data, indent=2).encode()).decode()
                    requests.put(url, headers=self.headers, json={'message': 'Init', 'content': content})
            except:
                pass
    
    def _get_file(self, path):
        url = f"{self.base_url}/{path}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                content = base64.b64decode(data['content']).decode()
                return {'data': json.loads(content), 'sha': data.get('sha')}
        except:
            pass
        return {'data': None, 'sha': None}
    
    def _save_file(self, path, data, sha=None):
        url = f"{self.base_url}/{path}"
        content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
        payload = {'message': f'Update {path}', 'content': content}
        if sha:
            payload['sha'] = sha
        try:
            resp = requests.put(url, headers=self.headers, json=payload)
            return resp.status_code in [200, 201]
        except:
            return False
    
    # ========== SOAL ==========
    def get_all_questions(self) -> List[Dict]:
        res = self._get_file("data/questions.json")
        return res['data'].get('questions', []) if res['data'] else []
    
    def add_question(self, question: str, option_left: str, option_right: str, is_active: bool = True) -> bool:
        res = self._get_file("data/questions.json")
        questions = res['data'].get('questions', []) if res['data'] else []
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
        return self._save_file("data/questions.json", {"questions": questions}, res['sha'])
    
    def update_question(self, qid: int, question: str, option_left: str, option_right: str, is_active: bool) -> bool:
        res = self._get_file("data/questions.json")
        if not res['data']:
            return False
        questions = res['data']['questions']
        found = False
        for q in questions:
            if q['id'] == qid:
                q['question'] = question
                q['option_left'] = option_left
                q['option_right'] = option_right
                q['is_active'] = is_active
                found = True
                break
        if not found:
            return False
        return self._save_file("data/questions.json", {"questions": questions}, res['sha'])
    
    def update_question_status(self, qid: int, is_active: bool) -> bool:
        res = self._get_file("data/questions.json")
        if not res['data']:
            return False
        questions = res['data']['questions']
        for q in questions:
            if q['id'] == qid:
                q['is_active'] = is_active
                break
        return self._save_file("data/questions.json", {"questions": questions}, res['sha'])
    
    def delete_question(self, qid: int) -> bool:
        res = self._get_file("data/questions.json")
        if not res['data']:
            return False
        questions = [q for q in res['data']['questions'] if q['id'] != qid]
        return self._save_file("data/questions.json", {"questions": questions}, res['sha'])
    
    # ========== RESPONSES ==========
    def get_all_responses(self) -> List[Dict]:
        res = self._get_file("data/responses.json")
        return res['data'].get('responses', []) if res['data'] else []
    
    def save_response(self, nik: str, responses_list: List[Dict], aspirasi: str = "") -> bool:
        res = self._get_file("data/responses.json")
        all_resp = res['data'].get('responses', []) if res['data'] else []
        new_entry = {
            'nik': nik,
            'submitted_at': datetime.now().isoformat(),
            'responses': responses_list,
            'aspirasi': aspirasi
        }
        all_resp.append(new_entry)
        saved = self._save_file("data/responses.json", {"responses": all_resp}, res['sha'])
        if saved:
            self._update_user_quota(nik)
        return saved
    
    # ========== NIK ==========
    def get_valid_niks(self) -> List[str]:
        res = self._get_file("data/valid_niks.json")
        return res['data'].get('niks', []) if res['data'] else []
    
    def add_valid_nik(self, nik: str) -> bool:
        res = self._get_file("data/valid_niks.json")
        niks = res['data'].get('niks', []) if res['data'] else []
        if nik not in niks:
            niks.append(nik)
        return self._save_file("data/valid_niks.json", {"niks": niks}, res['sha'])
    
    def delete_valid_nik(self, nik: str) -> bool:
        res = self._get_file("data/valid_niks.json")
        if not res['data']:
            return False
        niks = [n for n in res['data']['niks'] if n != nik]
        return self._save_file("data/valid_niks.json", {"niks": niks}, res['sha'])
    
    # ========== KUOTA ==========
    def get_quota_config(self) -> Dict:
        res = self._get_file("data/quota_config.json")
        return res['data'] if res['data'] else {'max_per_year': 3}
    
    def update_quota_config(self, max_per_year: int) -> bool:
        res = self._get_file("data/quota_config.json")
        config = {'max_per_year': max_per_year, 'updated_at': datetime.now().isoformat()}
        return self._save_file("data/quota_config.json", config, res['sha'])
    
    def get_user_quota(self, nik: str) -> Dict:
        res = self._get_file("data/user_quotas.json")
        quotas = res['data'].get('quotas', {}) if res['data'] else {}
        current_year = datetime.now().year
        user = quotas.get(nik, {})
        if user.get('last_reset') != current_year:
            user = {'used': 0, 'last_reset': current_year}
        max_q = self.get_quota_config().get('max_per_year', 3)
        used = user.get('used', 0)
        return {
            'max': max_q,
            'used': used,
            'remaining': max_q - used,
            'can_submit': used < max_q
        }
    
    def _update_user_quota(self, nik: str) -> bool:
        res = self._get_file("data/user_quotas.json")
        quotas = res['data'].get('quotas', {}) if res['data'] else {}
        current_year = datetime.now().year
        if nik not in quotas or quotas[nik].get('last_reset') != current_year:
            quotas[nik] = {'used': 0, 'last_reset': current_year}
        quotas[nik]['used'] = quotas[nik].get('used', 0) + 1
        return self._save_file("data/user_quotas.json", {"quotas": quotas}, res['sha'])
    
    def reset_all_quotas(self) -> bool:
        res = self._get_file("data/user_quotas.json")
        return self._save_file("data/user_quotas.json", {"quotas": {}}, res['sha'])