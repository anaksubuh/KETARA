import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import streamlit as st

class GitHubAPI:
    def __init__(self):
        # Ganti dengan config GitHub Anda
        self.token = st.secrets.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
        self.repo = st.secrets.get("GITHUB_REPO", "YOUR_USERNAME/YOUR_REPO")
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    # ========== MANAJEMEN SOAL ==========
    def get_all_questions(self) -> List[Dict]:
        """Ambil semua soal dari GitHub"""
        try:
            url = f"{self.base_url}/data/questions.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                return data.get('questions', [])
            return []
        except Exception as e:
            print(f"Error get questions: {e}")
            return []
    
    def add_question(self, question: str, option_left: str, option_right: str, is_active: bool = True) -> bool:
        """Tambah soal baru"""
        try:
            questions = self.get_all_questions()
            new_id = max([q.get('id', 0) for q in questions]) + 1 if questions else 1
            
            new_question = {
                'id': new_id,
                'question': question,
                'option_left': option_left,
                'option_right': option_right,
                'is_active': is_active,
                'created_at': datetime.now().isoformat()
            }
            
            questions.append(new_question)
            return self._save_questions(questions)
        except Exception as e:
            print(f"Error add question: {e}")
            return False
    
    def update_question_status(self, question_id: int, is_active: bool) -> bool:
        """Update status soal (aktif/nonaktif)"""
        try:
            questions = self.get_all_questions()
            for q in questions:
                if q.get('id') == question_id:
                    q['is_active'] = is_active
                    break
            return self._save_questions(questions)
        except Exception as e:
            print(f"Error update status: {e}")
            return False
    
    def delete_question(self, question_id: int) -> bool:
        """Hapus soal"""
        try:
            questions = self.get_all_questions()
            questions = [q for q in questions if q.get('id') != question_id]
            return self._save_questions(questions)
        except Exception as e:
            print(f"Error delete question: {e}")
            return False
    
    def _save_questions(self, questions: List[Dict]) -> bool:
        """Simpan soal ke GitHub"""
        try:
            url = f"{self.base_url}/data/questions.json"
            
            # Get current file SHA
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            # Prepare new content
            import base64
            content = base64.b64encode(json.dumps({'questions': questions}, indent=2).encode()).decode()
            
            data = {
                'message': f'Update questions {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error save questions: {e}")
            return False
    
    # ========== MANAJEMEN RESPONSES ==========
    def get_all_responses(self) -> List[Dict]:
        """Ambil semua response dari GitHub"""
        try:
            url = f"{self.base_url}/data/responses.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                return data.get('responses', [])
            return []
        except Exception as e:
            print(f"Error get responses: {e}")
            return []
    
    def save_response(self, nik: str, responses_list: List[Dict], aspirasi: str = "") -> bool:
        """Simpan response baru"""
        try:
            all_responses = self.get_all_responses()
            
            new_response = {
                'nik': nik,
                'submitted_at': datetime.now().isoformat(),
                'responses': responses_list,
                'aspirasi': aspirasi
            }
            
            all_responses.append(new_response)
            
            # Update kuota user
            self._update_user_quota(nik)
            
            return self._save_responses(all_responses)
        except Exception as e:
            print(f"Error save response: {e}")
            return False
    
    def _save_responses(self, responses: List[Dict]) -> bool:
        """Simpan responses ke GitHub"""
        try:
            url = f"{self.base_url}/data/responses.json"
            
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            import base64
            content = base64.b64encode(json.dumps({'responses': responses}, indent=2).encode()).decode()
            
            data = {
                'message': f'Update responses {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error save responses: {e}")
            return False
    
    # ========== MANAJEMEN NIK ==========
    def get_valid_niks(self) -> List[str]:
        """Ambil daftar NIK terdaftar"""
        try:
            url = f"{self.base_url}/data/valid_niks.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                return data.get('niks', [])
            return []
        except Exception as e:
            print(f"Error get valid niks: {e}")
            return []
    
    def add_valid_nik(self, nik: str) -> bool:
        """Tambah NIK baru"""
        try:
            niks = self.get_valid_niks()
            if nik not in niks:
                niks.append(nik)
            return self._save_valid_niks(niks)
        except Exception as e:
            print(f"Error add nik: {e}")
            return False
    
    def delete_valid_nik(self, nik: str) -> bool:
        """Hapus NIK"""
        try:
            niks = self.get_valid_niks()
            niks = [n for n in niks if n != nik]
            return self._save_valid_niks(niks)
        except Exception as e:
            print(f"Error delete nik: {e}")
            return False
    
    def _save_valid_niks(self, niks: List[str]) -> bool:
        """Simpan daftar NIK ke GitHub"""
        try:
            url = f"{self.base_url}/data/valid_niks.json"
            
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            import base64
            content = base64.b64encode(json.dumps({'niks': niks}, indent=2).encode()).decode()
            
            data = {
                'message': f'Update valid niks {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error save niks: {e}")
            return False
    
    # ========== MANAJEMEN KUOTA ==========
    def get_quota_config(self) -> Dict:
        """Ambil konfigurasi kuota"""
        try:
            url = f"{self.base_url}/data/quota_config.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                return data
            return {'max_per_year': 3}
        except Exception as e:
            print(f"Error get quota config: {e}")
            return {'max_per_year': 3}
    
    def update_quota_config(self, max_per_year: int) -> bool:
        """Update konfigurasi kuota"""
        try:
            url = f"{self.base_url}/data/quota_config.json"
            
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            config = {'max_per_year': max_per_year, 'updated_at': datetime.now().isoformat()}
            
            import base64
            content = base64.b64encode(json.dumps(config, indent=2).encode()).decode()
            
            data = {
                'message': f'Update quota config {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error update quota config: {e}")
            return False
    
    def get_user_quota(self, nik: str) -> Dict:
        """Dapatkan kuota user"""
        try:
            url = f"{self.base_url}/data/user_quotas.json"
            response = requests.get(url, headers=self.headers)
            
            quotas = {}
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                quotas = data.get('quotas', {})
            
            current_year = datetime.now().year
            user_data = quotas.get(nik, {})
            last_reset = user_data.get('last_reset', 0)
            
            # Reset tahunan
            if last_reset != current_year:
                user_data = {'used': 0, 'last_reset': current_year}
            
            max_quota = self.get_quota_config().get('max_per_year', 3)
            used = user_data.get('used', 0)
            
            return {
                'max': max_quota,
                'used': used,
                'remaining': max_quota - used,
                'can_submit': used < max_quota
            }
        except Exception as e:
            print(f"Error get user quota: {e}")
            return {'max': 3, 'used': 0, 'remaining': 3, 'can_submit': True}
    
    def _update_user_quota(self, nik: str) -> bool:
        """Update kuota user setelah submit"""
        try:
            url = f"{self.base_url}/data/user_quotas.json"
            
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            quotas = {}
            if response.status_code == 200:
                content = response.json()
                import base64
                data = json.loads(base64.b64decode(content['content']).decode())
                quotas = data.get('quotas', {})
            
            current_year = datetime.now().year
            if nik not in quotas:
                quotas[nik] = {'used': 0, 'last_reset': current_year}
            
            if quotas[nik].get('last_reset') != current_year:
                quotas[nik] = {'used': 0, 'last_reset': current_year}
            
            quotas[nik]['used'] += 1
            
            import base64
            content = base64.b64encode(json.dumps({'quotas': quotas}, indent=2).encode()).decode()
            
            data = {
                'message': f'Update user quota {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error update user quota: {e}")
            return False
    
    def reset_all_quotas(self) -> bool:
        """Reset semua kuota"""
        try:
            url = f"{self.base_url}/data/user_quotas.json"
            
            response = requests.get(url, headers=self.headers)
            sha = response.json().get('sha') if response.status_code == 200 else None
            
            import base64
            content = base64.b64encode(json.dumps({'quotas': {}}, indent=2).encode()).decode()
            
            data = {
                'message': f'Reset all quotas {datetime.now().isoformat()}',
                'content': content,
                'sha': sha
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error reset quotas: {e}")
            return False
    
    def change_admin_password(self, old_pass: str, new_pass: str) -> bool:
        """Ganti password admin (simulasi)"""
        # Implementasi sesuai kebutuhan
        return True