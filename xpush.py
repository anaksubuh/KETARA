import os
import subprocess
import shutil
from pathlib import Path

# Konfigurasi
REPO_URL = "https://github.com/anaksubuh/KETARA"
REPO_NAME = "KETARA"
BRANCH = "main"

# Warna untuk output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_color(text, color=Colors.GREEN):
    print(f"{color}{text}{Colors.END}")

def run_command(command, cwd=None):
    """Jalankan perintah terminal"""
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print_color(f"⚠️ Error: {result.stderr}", Colors.RED)
        return False
    print_color(result.stdout, Colors.BLUE)
    return True

def upload_to_github():
    """Upload semua file ke GitHub dengan force push"""
    
    print_color("\n" + "="*60, Colors.HEADER)
    print_color("🚀 UPLOAD PAKSA KE GITHUB", Colors.HEADER)
    print_color("="*60 + "\n", Colors.HEADER)
    
    # 1. Cek apakah folder sudah ada
    current_dir = Path.cwd()
    repo_path = current_dir / REPO_NAME
    
    # 2. Clone repository jika belum ada
    if not repo_path.exists():
        print_color(f"📥 Cloning repository {REPO_URL}...", Colors.YELLOW)
        if run_command(f"git clone {REPO_URL}"):
            print_color("✅ Clone berhasil!", Colors.GREEN)
        else:
            print_color("❌ Gagal clone repository!", Colors.RED)
            return
    else:
        print_color(f"📁 Repository sudah ada di {repo_path}", Colors.BLUE)
    
    # 3. Copy semua file dari current directory ke repo (kecuali folder .git)
    print_color("\n📋 Menyalin file ke repository...", Colors.YELLOW)
    
    # File dan folder yang akan di-exclude
    exclude = {'.git', '__pycache__', 'venv', 'env', '.venv', 'database', '.streamlit/secrets.toml'}
    
    files_copied = []
    for item in current_dir.iterdir():
        if item.name not in exclude and item.name != REPO_NAME:
            dest = repo_path / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                files_copied.append(item.name)
                print_color(f"   📄 {item.name}", Colors.GREEN)
            elif item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
                files_copied.append(f"{item.name}/")
                print_color(f"   📁 {item.name}/", Colors.GREEN)
    
    print_color(f"\n✅ {len(files_copied)} file/folder disalin", Colors.GREEN)
    
    # 4. Masuk ke direktori repository
    os.chdir(repo_path)
    print_color(f"\n📂 Masuk ke: {repo_path}", Colors.BLUE)
    
    # 5. Git add semua file
    print_color("\n📦 Git add...", Colors.YELLOW)
    run_command("git add .")
    
    # 6. Git commit
    print_color("\n💾 Git commit...", Colors.YELLOW)
    commit_message = f"Force upload: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(f'git commit -m "{commit_message}"')
    
    # 7. Git push force
    print_color("\n🚀 Git push force ke GitHub...", Colors.YELLOW)
    if run_command(f"git push -u origin {BRANCH} --force"):
        print_color("\n" + "="*60, Colors.HEADER)
        print_color("✅ UPLOAD BERHASIL!", Colors.GREEN)
        print_color("="*60, Colors.HEADER)
        print_color(f"\n🔗 Repository: {REPO_URL}", Colors.BLUE)
        print_color(f"📁 Branch: {BRANCH}", Colors.BLUE)
        print_color(f"📅 Waktu: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
    else:
        print_color("\n❌ Gagal push ke GitHub!", Colors.RED)

def upload_file_only():
    """Upload hanya dengan force push tanpa clone ulang"""
    
    print_color("\n" + "="*60, Colors.HEADER)
    print_color("🚀 FORCE PUSH KE GITHUB (TANPA CLONE ULANG)", Colors.HEADER)
    print_color("="*60 + "\n", Colors.HEADER)
    
    current_dir = Path.cwd()
    
    # Cek apakah ini git repository
    if not (current_dir / ".git").exists():
        print_color("⚠️ Bukan git repository! Inisialisasi dulu...", Colors.YELLOW)
        run_command("git init")
        run_command(f"git remote add origin {REPO_URL}")
    
    # Git add semua
    print_color("📦 Git add semua file...", Colors.YELLOW)
    run_command("git add .")
    
    # Git commit
    print_color("💾 Git commit...", Colors.YELLOW)
    commit_message = f"Force upload: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(f'git commit -m "{commit_message}"')
    
    # Git push force
    print_color("🚀 Git push force...", Colors.YELLOW)
    if run_command(f"git push -u origin main --force"):
        print_color("\n✅ UPLOAD BERHASIL!", Colors.GREEN)
    else:
        print_color("\n❌ Gagal push! Coba metode clone...", Colors.RED)
        # Coba pull dulu
        run_command("git pull origin main --allow-unrelated-histories")
        run_command("git push -u origin main --force")

def create_gitignore():
    """Buat file .gitignore"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Streamlit
.streamlit/secrets.toml

# Database
database/
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets
secrets.toml
*.pem
*.key
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    print_color("✅ File .gitignore dibuat", Colors.GREEN)

if __name__ == "__main__":
    print_color("\n🔧 SCRIPT UPLOAD KE GITHUB", Colors.HEADER)
    print_color("="*40, Colors.HEADER)
    print("1. Upload paksa (clone ulang)")
    print("2. Force push (tanpa clone ulang)")
    print("3. Buat .gitignore lalu upload")
    print("4. Upload semua file termasuk database")
    
    
    upload_to_github()

    '''
    if choice == "1":
        upload_to_github()
    elif choice == "2":
        upload_file_only()
    elif choice == "3":
        create_gitignore()
        upload_to_github()
    elif choice == "4":
        # Upload termasuk database
        print_color("\n⚠️ PERINGATAN: Database akan diupload!", Colors.YELLOW)
        confirm = input("Lanjutkan? (y/n): ")
        if confirm.lower() == 'y':
            upload_to_github()
    else:
        print_color("Pilihan tidak valid!", Colors.RED)
    '''