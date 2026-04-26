@echo off
cd /d "D:\sinau html\KETARA"
git add .
git commit -m "Auto Update"
git push -u origin main --force
echo ✅ Selesai!
pause