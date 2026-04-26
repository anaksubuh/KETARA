import requests
import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st
import pandas as pd

class GitHubAPI:
    """Handler untuk menyimpan data ke GitHub"""
    
    def __init__(self):
        self.token = st.secrets["GITHUB_TOKEN"]
        self.owner = st.secrets["REPO_OWNER"]
        self.repo = st.secrets["REPO_NAME"]
        self.base_url = "https://api.github.com/repos"
        
        # File paths
        self.questions_file = "data/questions.json"
        self.responses_file = "data/responses.json"
        self.users_file = "data/users.json"
        self.settings_file = "data/settings.json"
        
    def _get_headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _get_file(self, path: str) -> Optional[Dict]:
        """Mendapatkan file dari GitHub"""
        url = f"{self.base_url}/{self.owner}/{self.repo}/contents/{path}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                content = response.json()
                decoded = base64.b64decode(content['content']).decode('utf-8')
                return {
                    'data': json.loads(decoded),
                    'sha': content['sha']
                }
            elif response.status_code == 404:
                return None
            else:
                return None
        except Exception as e:
            return None
    
    def _save_file(self, path: str, data: Any, sha: Optional[str] = None) -> bool:
        """Menyimpan file ke GitHub"""
        url = f"{self.base_url}/{self.owner}/{self.repo}/contents/{path}"
        content = json.dumps(data, indent=2, ensure_ascii=False)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": f"Update {path}",
            "content": encoded,
            "branch": "main"
        }
        
        if sha:
            payload["sha"] = sha
        
        try:
            response = requests.put(url, headers=self._get_headers(), json=payload)
            return response.status_code in [200, 201]
        except:
            return False
    
    # ========== MANAJEMEN PERTANYAAN (CRUD) ==========
    
    def get_all_questions(self) -> List[Dict]:
        """Mendapatkan semua pertanyaan polling"""
        file_data = self._get_file(self.questions_file)
        
        if not file_data:
            # Data default
            default_questions = [
                {
                    "id": "1",
                    "question": "2 + 2 = 4",
                    "option_left": "✅ Setuju",
                    "option_right": "❌ Tidak Setuju",
                    "is_active": True,
                    "order": 1,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "2",
                    "question": "Kebijakan Bantuan Sosial Daerah sudah tepat sasaran",
                    "option_left": "✅ Setuju",
                    "option_right": "❌ Tidak Setuju",
                    "is_active": True,
                    "order": 2,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "3",
                    "question": "Penyesuaian tarif air minum perlu dilakukan",
                    "option_left": "✅ Setuju",
                    "option_right": "❌ Tidak Setuju",
                    "is_active": True,
                    "order": 3,
                    "created_at": datetime.now().isoformat()
                }
            ]
            self.save_questions(default_questions)
            return default_questions
        
        return file_data['data'].get('questions', [])
    
    def save_questions(self, questions: List[Dict]) -> bool:
        """Menyimpan semua pertanyaan"""
        file_data = self._get_file(self.questions_file)
        sha = file_data['sha'] if file_data else None
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_questions': len(questions),
            'questions': questions
        }
        
        return self._save_file(self.questions_file, data, sha)
    
    def add_question(self, question: Dict) -> bool:
        """Menambah pertanyaan baru"""
        questions = self.get_all_questions()
        
        # Generate new ID
        max_id = max([int(q['id']) for q in questions], default=0)
        question['id'] = str(max_id + 1)
        question['created_at'] = datetime.now().isoformat()
        question['order'] = len(questions) + 1
        
        questions.append(question)
        return self.save_questions(questions)
    
    def update_question(self, question_id: str, updated_question: Dict) -> bool:
        """Update pertanyaan"""
        questions = self.get_all_questions()
        
        for i, q in enumerate(questions):
            if q['id'] == question_id:
                updated_question['id'] = question_id
                updated_question['created_at'] = q.get('created_at', datetime.now().isoformat())
                updated_question['updated_at'] = datetime.now().isoformat()
                questions[i] = updated_question
                return self.save_questions(questions)
        
        return False
    
    def delete_question(self, question_id: str) -> bool:
        """Menghapus pertanyaan"""
        questions = self.get_all_questions()
        questions = [q for q in questions if q['id'] != question_id]
        
        # Reorder
        for i, q in enumerate(questions):
            q['order'] = i + 1
        
        return self.save_questions(questions)
    
    def toggle_question_active(self, question_id: str) -> bool:
        """Aktif/nonaktifkan pertanyaan"""
        questions = self.get_all_questions()
        
        for q in questions:
            if q['id'] == question_id:
                q['is_active'] = not q.get('is_active', True)
                return self.save_questions(questions)
        
        return False
    
    # ========== MANAJEMEN RESPONS ==========
    
    def save_response(self, nik: str, responses: List[Dict]) -> bool:
        """Menyimpan respons user"""
        file_data = self._get_file(self.responses_file)
        
        if not file_data:
            data = {'responses': []}
            sha = None
        else:
            data = file_data['data']
            sha = file_data['sha']
        
        # Hitung kuota
        nik_responses = [r for r in data['responses'] if r['nik'] == nik]
        current_year = datetime.now().year
        used_this_year = len([r for r in nik_responses if datetime.fromisoformat(r['submitted_at']).year == current_year])
        
        response_record = {
            'id': f"{nik}_{datetime.now().timestamp()}",
            'nik': nik,
            'responses': responses,
            'submitted_at': datetime.now().isoformat(),
            'year': current_year,
            'used_count': used_this_year + 1
        }
        
        data['responses'].append(response_record)
        data['last_updated'] = datetime.now().isoformat()
        data['total_responses'] = len(data['responses'])
        
        return self._save_file(self.responses_file, data, sha)
    
    def get_all_responses(self) -> List[Dict]:
        """Mendapatkan semua respons"""
        file_data = self._get_file(self.responses_file)
        
        if not file_data:
            return []
        
        return file_data['data'].get('responses', [])
    
    def get_user_responses(self, nik: str) -> List[Dict]:
        """Mendapatkan respons user berdasarkan NIK"""
        responses = self.get_all_responses()
        return [r for r in responses if r['nik'] == nik]
    
    def get_user_quota(self, nik: str) -> Dict:
        """Mendapatkan kuota user untuk tahun ini"""
        responses = self.get_all_responses()
        current_year = datetime.now().year
        max_quota = st.secrets.get("MAX_QUOTA_PER_YEAR", 10)
        
        user_responses = [r for r in responses if r['nik'] == nik]
        used_this_year = len([r for r in user_responses if r.get('year') == current_year])
        
        return {
            'used': used_this_year,
            'remaining': max_quota - used_this_year,
            'max': max_quota,
            'can_submit': used_this_year < max_quota
        }
    
    # ========== MANAJEMEN SETTINGS ==========
    
    def get_settings(self) -> Dict:
        """Mendapatkan pengaturan sistem"""
        file_data = self._get_file(self.settings_file)
        
        if not file_data:
            default_settings = {
                'system_name': 'Sistem Aspirasi & Polling',
                'max_quota_per_year': 10,
                'allow_polling': True,
                'allow_aspirasi': True,
                'last_updated': datetime.now().isoformat()
            }
            self.save_settings(default_settings)
            return default_settings
        
        return file_data['data']
    
    def save_settings(self, settings: Dict) -> bool:
        """Menyimpan pengaturan sistem"""
        file_data = self._get_file(self.settings_file)
        sha = file_data['sha'] if file_data else None
        
        settings['last_updated'] = datetime.now().isoformat()
        
        return self._save_file(self.settings_file, settings, sha)
    
    # ========== MANAJEMEN USER (untuk verifikasi NIK) ==========
    
    def get_valid_niks(self) -> List[str]:
        """Mendapatkan daftar NIK valid"""
        file_data = self._get_file(self.users_file)
        
        if not file_data:
            default_users = {
                'valid_niks': ['1111111111111111', '2222222222222222', '3333333333333333'],
                'last_updated': datetime.now().isoformat()
            }
            self._save_file(self.users_file, default_users, None)
            return default_users['valid_niks']
        
        return file_data['data'].get('valid_niks', [])
    
    def add_valid_nik(self, nik: str) -> bool:
        """Menambah NIK valid"""
        file_data = self._get_file(self.users_file)
        
        if not file_data:
            niks = []
            sha = None
        else:
            niks = file_data['data'].get('valid_niks', [])
            sha = file_data['sha']
        
        if nik not in niks:
            niks.append(nik)
        
        data = {
            'valid_niks': niks,
            'last_updated': datetime.now().isoformat()
        }
        
        return self._save_file(self.users_file, data, sha)
    
    def remove_valid_nik(self, nik: str) -> bool:
        """Menghapus NIK valid"""
        file_data = self._get_file(self.users_file)
        
        if not file_data:
            return False
        
        niks = file_data['data'].get('valid_niks', [])
        if nik in niks:
            niks.remove(nik)
        
        data = {
            'valid_niks': niks,
            'last_updated': datetime.now().isoformat()
        }
        
        return self._save_file(self.users_file, data, file_data['sha'])