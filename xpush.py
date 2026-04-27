import subprocess
from pathlib import Path
from datetime import datetime

REPO_URL = "https://github.com/anaksubuh/KETARA"
BRANCH = "main"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode == 0

def is_git_repo():
    return (Path.cwd() / ".git").exists()

def setup_repo():
    print("🔧 Setup repository...")
    run("git init")
    run(f"git remote add origin {REPO_URL}")

def commit_and_push(force=False):
    print("📦 Adding files...")
    run("git add -A")

    print("📊 Checking status...")
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)

    if not status.stdout.strip():
        print("⚠️ Tidak ada perubahan (nothing to commit)")
        return

    msg = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print("💾 Committing...")
    run(f'git commit -m "{msg}"')

    print("🚀 Pushing...")
    if force:
        run(f"git push -u origin {BRANCH} --force")
    else:
        run(f"git push -u origin {BRANCH}")

def main():
    print("🚀 AUTO PUSH LOCAL → GITHUB\n")

    if not is_git_repo():
        print("⚠️ Belum git repo")
        setup_repo()

    # set branch (biar aman)
    run(f"git branch -M {BRANCH}")

    # push
    commit_and_push(force=False)

if __name__ == "__main__":
    main()