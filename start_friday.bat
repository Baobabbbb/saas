@echo off
echo 🚀 Démarrage FRIDAY Backend...
cd saas
start "FRIDAY Backend" cmd /k "uvicorn main_new:app --host 0.0.0.0 --port 8000 --reload"

echo 🌐 Démarrage Frontend...
cd ..\frontend
start "FRIDAY Frontend" cmd /k "npm run dev"

echo ✅ Services démarrés!
echo 📱 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo 📚 Docs: http://localhost:8000/docs
pause
