import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import base64
import streamlit as st

class GitHubAPI:
    def __init__(self):
        # Gunakan st.secrets untuk keamanan (di Streamlit Cloud)
        # Atau hardcode sementara untuk testing
        try:
            self.token = st.secrets.get("GITHUB_TOKEN", "")
            self.repo = st.secrets.get("GITHUB_REPO", "")
        except:
            # Fallback untuk testing local - GANTI DENGAN DATA GITHUB ANDA
            self.token = "YOUR_GITHUB_TOKEN_HERE"
            self.repo = "YOUR_USERNAME/YOUR_REPO_NAME"
        
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Inisialisasi file data jika belum ada
        self._init_data_files()
    
    def _init_data_files(self):
        """Inisialisasi file-file JSON jika belum ada"""
        files = {
            "data/questions.json": {"questions": []},
            "data/responses.json": {"responses": []},
            "data/valid_niks.json": {"niks": []},
            "data/quota_config.json": {"max_per_year": 3, "updated_at": datetime.now().isoformat()},
            "data/user_quotas.json": {"quotas": {}}
        }
        
        for file_path, default_data in files.items():
            url = f"{self.base_url}/{file_path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                # File tidak ada, buat baru
                content = base64.b64encode(json.dumps(default_data, indent=2).encode()).decode()
                data = {
                    'message': f'Initialize {file_path}',
                    'content': content
                }
                requests.put(url, headers=self.headers, json=data)
    
    def _make_request(self, method, url, **kwargs):
        """Helper untuk membuat request dengan error handling"""
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            return response
        except Exception as e:
            st.error(f"Error connecting to GitHub: {str(e)}")
            return None
    
    def _get_file_content(self, file_path: str) -> dict:
        """Ambil konten file dari GitHub"""
        try:
            url = f"{self.base_url}/{file_path}"
            response = self._make_request("GET", url)
            
            if response and response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data['content']).decode()
                return {
                    'data': json.loads(content),
                    'sha': data.get('sha')
                }
            return {'data': None, 'sha': None}
        except Exception as e:
            print(f"Error get file content: {e}")
            return {'data': None, 'sha': None}
    
    def _save_file_content(self, file_path: str, data: dict, sha: str = None) -> bool:
        """Simpan konten file ke GitHub"""
        try:
            url = f"{self.base_url}/{file_path}"
            
            content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
            
            payload = {
                'message': f'Update {file_path} at {datetime.now().isoformat()}',
                'content': content
            }
            
            if sha:
                payload['sha'] = sha
            
            response = self._make_request("PUT", url, json=payload)
            return response and response.status_code in [200, 201]
        except Exception as e:
            print(f"Error save file content: {e}")
            return False
    
    # ========== MANAJEMEN SOAL ==========
    def get_all_questions(self) -> List[Dict]:
        """Ambil semua soal dari GitHub"""
        try:
            result = self._get_file_content("data/questions.json")
            if result['data']:
                return result['data'].get('questions', [])
            return []
        except Exception as e:
            print(f"Error get questions: {e}")
            return []
    
    def add_question(self, question: str, option_left: str, option_right: str, is_active: bool = True) -> bool:
        """Tambah soal baru"""
        try:
            # Ambil data existing
            result = self._get_file_content("data/questions.json")
            questions_data = result['data'] if result['data'] else {"questions": []}
            questions = questions_data.get('questions', [])
            
            # Buat ID baru
            new_id = 1
            if questions:
                new_id = max([q.get('id', 0) for q in questions]) + 1
            
            # Buat soal baru
            new_question = {
                'id': new_id,
                'question': question,
                'option_left': option_left,
                'option_right': option_right,
                'is_active': is_active,
                'created_at': datetime.now().isoformat()
            }
            
            questions.append(new_question)
            
            # Simpan kembali
            success = self._save_file_content(
                "data/questions.json",
                {"questions": questions},
                result['sha']
            )
            
            if success:
                print(f"Success adding question: {new_question}")
            else:
                print("Failed to add question")
            
            return success
        except Exception as e:
            print(f"Error add question: {e}")
            return False
    
    def update_question_status(self, question_id: int, is_active: bool) -> bool:
        """Update status soal"""
        try:
            result = self._get_file_content("data/questions.json")
            if not result['data']:
                return False
            
            questions = result['data'].get('questions', [])
            for q in questions:
                if q.get('id') == question_id:
                    q['is_active'] = is_active
                    break
            
            return self._save_file_content(
                "data/questions.json",
                {"questions": questions},
                result['sha']
            )
        except Exception as e:
            print(f"Error update status: {e}")
            return False
    
    def delete_question(self, question_id: int) -> bool:
        """Hapus soal"""
        try:
            result = self._get_file_content("data/questions.json")
            if not result['data']:
                return False
            
            questions = result['data'].get('questions', [])
            questions = [q for q in questions if q.get('id') != question_id]
            
            return self._save_file_content(
                "data/questions.json",
                {"questions": questions},
                result['sha']
            )
        except Exception as e:
            print(f"Error delete question: {e}")
            return False
    
    # ========== MANAJEMEN RESPONSES ==========
    def get_all_responses(self) -> List[Dict]:
        """Ambil semua response"""
        try:
            result = self._get_file_content("data/responses.json")
            if result['data']:
                return result['data'].get('responses', [])
            return []
        except Exception as e:
            print(f"Error get responses: {e}")
            return []
    
    def save_response(self, nik: str, responses_list: List[Dict], aspirasi: str = "") -> bool:
        """Simpan response baru"""
        try:
            result = self._get_file_content("data/responses.json")
            responses_data = result['data'] if result['data'] else {"responses": []}
            all_responses = responses_data.get('responses', [])
            
            new_response = {
                'nik': nik,
                'submitted_at': datetime.now().isoformat(),
                'responses': responses_list,
                'aspirasi': aspirasi
            }
            
            all_responses.append(new_response)
            
            # Update kuota user
            self._update_user_quota(nik)
            
            return self._save_file_content(
                "data/responses.json",
                {"responses": all_responses},
                result['sha']
            )
        except Exception as e:
            print(f"Error save response: {e}")
            return False
    
    # ========== MANAJEMEN NIK ==========
    def get_valid_niks(self) -> List[str]:
        """Ambil daftar NIK terdaftar"""
        try:
            result = self._get_file_content("data/valid_niks.json")
            if result['data']:
                return result['data'].get('niks', [])
            return []
        except Exception as e:
            print(f"Error get valid niks: {e}")
            return []
    
    def add_valid_nik(self, nik: str) -> bool:
        """Tambah NIK baru"""
        try:
            result = self._get_file_content("data/valid_niks.json")
            niks_data = result['data'] if result['data'] else {"niks": []}
            niks = niks_data.get('niks', [])
            
            if nik not in niks:
                niks.append(nik)
            
            return self._save_file_content(
                "data/valid_niks.json",
                {"niks": niks},
                result['sha']
            )
        except Exception as e:
            print(f"Error add nik: {e}")
            return False
    
    def delete_valid_nik(self, nik: str) -> bool:
        """Hapus NIK"""
        try:
            result = self._get_file_content("data/valid_niks.json")
            if not result['data']:
                return False
            
            niks = result['data'].get('niks', [])
            niks = [n for n in niks if n != nik]
            
            return self._save_file_content(
                "data/valid_niks.json",
                {"niks": niks},
                result['sha']
            )
        except Exception as e:
            print(f"Error delete nik: {e}")
            return False
    
    # ========== MANAJEMEN KUOTA ==========
    def get_quota_config(self) -> Dict:
        """Ambil konfigurasi kuota"""
        try:
            result = self._get_file_content("data/quota_config.json")
            if result['data']:
                return result['data']
            return {'max_per_year': 3}
        except Exception as e:
            print(f"Error get quota config: {e}")
            return {'max_per_year': 3}
    
    def update_quota_config(self, max_per_year: int) -> bool:
        """Update konfigurasi kuota"""
        try:
            result = self._get_file_content("data/quota_config.json")
            config = {
                'max_per_year': max_per_year,
                'updated_at': datetime.now().isoformat()
            }
            
            return self._save_file_content(
                "data/quota_config.json",
                config,
                result['sha']
            )
        except Exception as e:
            print(f"Error update quota config: {e}")
            return False
    
    def get_user_quota(self, nik: str) -> Dict:
        """Dapatkan kuota user"""
        try:
            result = self._get_file_content("data/user_quotas.json")
            quotas = result['data'] if result['data'] else {"quotas": {}}
            quotas_dict = quotas.get('quotas', {})
            
            current_year = datetime.now().year
            user_data = quotas_dict.get(nik, {})
            
            # Reset tahunan
            if user_data.get('last_reset') != current_year:
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
            result = self._get_file_content("data/user_quotas.json")
            quotas_data = result['data'] if result['data'] else {"quotas": {}}
            quotas = quotas_data.get('quotas', {})
            
            current_year = datetime.now().year
            
            if nik not in quotas:
                quotas[nik] = {'used': 0, 'last_reset': current_year}
            
            if quotas[nik].get('last_reset') != current_year:
                quotas[nik] = {'used': 0, 'last_reset': current_year}
            
            quotas[nik]['used'] = quotas[nik].get('used', 0) + 1
            
            return self._save_file_content(
                "data/user_quotas.json",
                {"quotas": quotas},
                result['sha']
            )
        except Exception as e:
            print(f"Error update user quota: {e}")
            return False
    
    def reset_all_quotas(self) -> bool:
        """Reset semua kuota"""
        try:
            result = self._get_file_content("data/user_quotas.json")
            return self._save_file_content(
                "data/user_quotas.json",
                {"quotas": {}},
                result['sha']
            )
        except Exception as e:
            print(f"Error reset quotas: {e}")
            return False