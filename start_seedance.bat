@echo off
echo 🚀 Demarrage du serveur SEEDANCE...
cd /d "c:\Users\Admin\Documents\saas\saas"
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
pause
